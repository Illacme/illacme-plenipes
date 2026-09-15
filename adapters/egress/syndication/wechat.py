#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - WeChat Official Account Syndicator
模块职责：负责将稿件作为草稿同步分发至微信公众号平台。
"""

import requests
import json
import threading
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog
from .wechat_shards.wechat_formatter import render_wechat_html
from .wechat_shards.wechat_uploader import transmute_article_images, ensure_valid_thumb_media_id
from .wechat_shards.wechat_token_cache import wechat_token_cache


# 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
_last_wechat_time = 0.0
_wechat_lock = threading.Lock()

class WeChatSyndicator(BaseSyndicator):
    PLUGIN_ID = "wechat"
    DISPLAY_NAME = "微信公众号"
    ICON = "💬"
    VERSION = "V1.0"
    DESCRIPTION = "将文章作为草稿同步至微信公众号素材库，支持自动授权与原文链接回溯。"
    SLA_TIER = "tier1"
    SLA_LABEL = "官方直连"
    SLA_DESC = "通过微信公众平台官方 OpenAPI 草稿箱直连分发，企业级稳定性与高可用保障。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        def _sanitize_wechat_url(url: str) -> str:
            if not url or not isinstance(url, str):
                return ""
            lower_u = url.lower()
            if any(h in lower_u for h in ["localhost", "127.0.0.1", "0.0.0.0", "192.168.", "10.", "172."]):
                return ""
            if not (lower_u.startswith("http://") or lower_u.startswith("https://")):
                return ""
            return url

        if not canonical_url and self.site_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        safe_source_url = _sanitize_wechat_url(canonical_url)
        
        # 提取并清洗摘要 (剥离 Frontmatter，微信官方限制单行，上限 40 汉字/120 字节)
        clean_body = content
        if clean_body.startswith("---"):
            parts = clean_body.split("---", 2)
            if len(parts) >= 3:
                clean_body = parts[2].strip()
        raw_digest = metadata.get("description") or metadata.get("digest") or (clean_body[:80])
        digest = " ".join(str(raw_digest).split())[:40]

        # 作者字段 (微信官方限制不超过 8 个字符，超限报 45110 author size out of limit)
        default_author = getattr(self.config, 'author', None) or (self.config.get('author') if isinstance(self.config, dict) else None)
        raw_author = metadata.get("author") or default_author or "Plenipes"
        author = str(raw_author)[:8]

        # 标题清洗 (微信官方限制 32 字符以内)
        safe_title = str(title or "未命名文章").strip()[:32]

        # 微信公众号要求图片封面 thumb_media_id 字段。此处测试时提供占位符，由后续 ensure_valid_thumb_media_id 注入真实素材 ID
        thumb_media_id = metadata.get("wechat_thumb_media_id") or "media_id_placeholder"

        # 🎨 调用微信专属美化排版与外链转脚注模块
        convert_footnotes = getattr(self.config, 'convert_footnotes', True)
        if isinstance(self.config, dict) and 'convert_footnotes' in self.config:
            convert_footnotes = self.config.get('convert_footnotes')
        
        formatted_html = render_wechat_html(content, {"convert_footnotes": convert_footnotes})

        doc_dir = metadata.get("doc_dir")
        if not doc_dir and metadata.get("file_path"):
            import os
            doc_dir = os.path.dirname(metadata.get("file_path"))

        cover_src = metadata.get("cover") or metadata.get("cover_image") or metadata.get("banner") or metadata.get("image")
        article_item = {
            "title": safe_title,
            "author": author,
            "digest": digest,
            "content": formatted_html,  # 支持富文本 HTML 排版与内联样式
            "content_source_url": safe_source_url,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }
        if cover_src:
            article_item["_cover_src"] = cover_src

        payload = {"articles": [article_item]}
        if doc_dir:
            payload["_doc_dir"] = doc_dir
        return payload

    def validate_preflight(self, title: str, content: str, metadata: dict) -> dict:
        """
        [Contract] 微信公众号发布前预检防呆：
        1. 标题长度校验（微信官方上限 32 字符，超限自动截断并预警）；
        2. 作者长度校验（微信官方上限 8 字符，超限自动截断并预警）；
        3. 摘要长度校验（微信官方上限 40 汉字/120 字节，超限自动截断并预警）；
        4. 凭据完整性断言（AppID 与 AppSecret 必填）。
        """
        errors = []
        warnings = []
        meta = metadata or {}

        # 凭据预检
        app_id = getattr(self.config, 'app_id', None) or (self.config.get('app_id') if isinstance(self.config, dict) else None)
        app_secret = getattr(self.config, 'app_secret', None) or (self.config.get('app_secret') if isinstance(self.config, dict) else None)
        if not app_id or not app_secret:
            errors.append("微信公众号未配置 AppID 或 AppSecret，无法发起远程分发。")

        # 标题防呆
        clean_title = str(title or "").strip()
        if not clean_title:
            errors.append("文章标题不能为空。")
        elif len(clean_title) > 32:
            warnings.append(f"文章标题长度 ({len(clean_title)}) 超过微信官方 32 字符硬限制，系统将自动安全截断为前 32 字符。")
            clean_title = clean_title[:32]

        # 正文非空
        if not content or not str(content).strip():
            errors.append("文章正文内容不能为空。")

        # 作者防呆
        raw_author = meta.get("author") or getattr(self.config, 'author', None) or "Plenipes"
        clean_author = str(raw_author)[:8]
        if len(str(raw_author)) > 8:
            warnings.append(f"作者名称 '{raw_author}' 超过微信 8 字符上限，已自动截断为 '{clean_author}'。")

        # 摘要防呆
        raw_desc = meta.get("description") or meta.get("digest") or ""
        clean_digest = " ".join(str(raw_desc).split())[:40] if raw_desc else ""
        if len(str(raw_desc)) > 40:
            warnings.append("文章摘要超过微信 40 字符建议上限，已自动保留前 40 字符精简版。")

        sanitized_meta = dict(meta)
        sanitized_meta["author"] = clean_author
        if clean_digest:
            sanitized_meta["description"] = clean_digest

        return {
            "valid": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "sanitized": {
                "title": clean_title,
                "content": content,
                "metadata": sanitized_meta
            }
        }


    def push(self, payload: dict, remote_id: str = None, **kwargs):
        import time
        import random

        app_id = getattr(self.config, 'app_id', None) or self.config.get('app_id')
        app_secret = getattr(self.config, 'app_secret', None) or self.config.get('app_secret')

        if not app_id or not app_secret:
            raise RuntimeError("微信公众号缺少 AppID 或 AppSecret 凭据配置，请先在插件中心完善配置。")

        # 🛡️ 1. 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上 (加上线程锁防止竞态穿透)
        global _last_wechat_time
        with _wechat_lock:
            while True:
                elapsed = time.time() - _last_wechat_time
                if elapsed < 1.5:
                    time.sleep(1.5 - elapsed)
                else:
                    break

            _last_wechat_time = time.time()

        # 🛡️ 2. 指数退避重试循环 (对冲微信 API 的频控限制与凭据自愈)
        doc_dir = payload.pop("_doc_dir", None)
        max_attempts = 3
        force_refresh = False
        for attempt in range(max_attempts):
            try:
                proxy_val = getattr(self.config, 'proxy', None) or (self.config.get('proxy') if isinstance(self.config, dict) else None)
                p_str = str(proxy_val).strip() if proxy_val else ""
                proxies = {"http": None, "https": None} if p_str.lower() == "direct" else ({"http": p_str, "https": p_str} if p_str else None)

                # ── 2.1 从本地长效缓存获取 Access Token (7200s 有效期，提前 300s 静默续期) ──
                access_token = wechat_token_cache.get_token(
                    app_id, app_secret, timeout=self.timeout, force_refresh=force_refresh, proxy=proxy_val
                )
                force_refresh = False

                # ── 2.2 自动转存正文图片至微信素材 CDN ─────────────
                auto_upload_images = getattr(self.config, 'auto_upload_images', True)
                if isinstance(self.config, dict) and 'auto_upload_images' in self.config:
                    auto_upload_images = self.config.get('auto_upload_images')

                if auto_upload_images and payload.get("articles"):
                    transmute_article_images(payload["articles"], access_token, doc_dir=doc_dir, proxy=proxy_val, timeout=self.timeout)

                # ── 2.3 确保封面 thumb_media_id 为真实合法的永久素材 ID (根除 40007 报错) ───
                if payload.get("articles"):
                    ensure_valid_thumb_media_id(payload["articles"], access_token, doc_dir=doc_dir, proxy=proxy_val, timeout=self.timeout)
                    for art in payload["articles"]:
                        thumb = art.get("thumb_media_id")
                        if not thumb or thumb == "media_id_placeholder":
                            raise RuntimeError("微信公众号分发失败：未能成功生成或上传封面永久素材 (thumb_media_id 为空)。")

                # ── 2.4 将图文推送至草稿箱 (强制原生 UTF-8 编码，彻底根除微信 \\uXXXX 乱码) ─────
                draft_url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
                post_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                post_headers = {"Content-Type": "application/json; charset=utf-8"}
                resp = requests.post(draft_url, data=post_data, headers=post_headers, proxies=proxies, timeout=self.timeout)
                _last_wechat_time = time.time()

                if resp.status_code == 200:
                    resp_data = resp.json()
                    draft_errcode = resp_data.get("errcode", 0)
                    if draft_errcode == 0 and "media_id" in resp_data:
                        media_id = resp_data.get("media_id")
                        tlog.info(f"🚀 [微信公众号分发成功] 草稿 Media ID: {media_id}")
                        return {
                            "media_id": media_id,
                            "remote_id": media_id,
                            "draft": True,
                            "url": "https://mp.weixin.qq.com",
                            "dashboard_url": "https://mp.weixin.qq.com"
                        }
                    elif draft_errcode in (40001, 42001):
                        tlog.warning("⚠️ [微信公众号] 微信草稿箱接口提示 Access Token 过期失效 (40001/42001)，强制清除缓存并重试...")
                        wechat_token_cache.invalidate(app_id, app_secret)
                        force_refresh = True
                        if attempt < max_attempts - 1:
                            time.sleep(1.0)
                            continue
                        raise RuntimeError(f"微信公众号 Access Token 认证失效 (errcode {draft_errcode})。")
                    elif draft_errcode == 40164:
                        import re
                        ip_match = re.search(r"invalid ip\s+([0-9\.]+)", resp_data.get("errmsg", ""))
                        invalid_ip = ip_match.group(1) if ip_match else "未知"
                        raise RuntimeError(
                            f"微信公众号 IP 白名单拦截 (40164)：检测到出口 IP 为 [{invalid_ip}]，请在微信公众平台【设置与开发 -> 基本配置 -> IP白名单】添加此 IP。"
                        )
                    elif draft_errcode == 45009:
                        if attempt < max_attempts - 1:
                            sleep_time = 3.0 * (2 ** attempt) + random.uniform(0.1, 0.5)
                            time.sleep(sleep_time)
                            continue
                        raise RuntimeError("微信公众号接口调用频控限制 (45009)。")
                    else:
                        raise RuntimeError(f"微信草稿箱接口报错 (errcode {draft_errcode}): {resp_data.get('errmsg')}")
                else:
                    raise RuntimeError(f"微信草稿箱接口 HTTP 错误 ({resp.status_code}): {resp.text}")

            except requests.RequestException as req_err:
                if attempt < max_attempts - 1:
                    sleep_time = 2.0 + random.uniform(0.1, 0.5)
                    time.sleep(sleep_time)
                    continue
                else:
                    tlog.error(f"🛑 [微信公众号] 网络请求失败: {req_err}")
                    raise RuntimeError(f"微信网络请求失败: {req_err}") from req_err
            except Exception as e:
                tlog.error(f"🛑 [微信公众号分发失败]: {e}")
                raise e
