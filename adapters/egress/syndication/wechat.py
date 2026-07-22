#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - WeChat Official Account Syndicator
模块职责：负责将稿件作为草稿同步分发至微信公众号平台。
"""

import requests
import threading
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


# 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
_last_wechat_time = 0.0
_wechat_lock = threading.Lock()

class WeChatSyndicator(BaseSyndicator):
    PLUGIN_ID = "wechat"
    DISPLAY_NAME = "微信公众号"
    VERSION = "V1.0"
    DESCRIPTION = "将文章作为草稿同步至微信公众号素材库，支持自动授权与原文链接回溯。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        # 提取摘要
        digest = metadata.get("description") or metadata.get("digest") or (content[:120] + "...")
        author = metadata.get("author") or "Plenipes Bot"

        # 微信公众号要求图片封面 thumb_media_id 字段。此处测试时提供占位符，若有需要用户可在微信后台替换
        thumb_media_id = metadata.get("wechat_thumb_media_id") or "media_id_placeholder"

        return {
            "articles": [
                {
                    "title": title,
                    "author": author,
                    "digest": digest,
                    "content": content,  # 支持富文本 HTML 排版
                    "content_source_url": canonical_url,
                    "thumb_media_id": thumb_media_id,
                    "need_open_comment": 1,
                    "only_fans_can_comment": 0
                }
            ]
        }

    def push(self, payload: dict):
        import time
        import random

        app_id = getattr(self.config, 'app_id', None) or self.config.get('app_id')
        app_secret = getattr(self.config, 'app_secret', None) or self.config.get('app_secret')

        if not app_id or not app_secret:
            tlog.warning("⚠️ [微信公众号] 缺少 app_id 或 app_secret 配置，分发跳过。")
            return

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

        # 🛡️ 2. 指数退避重试循环 (对冲微信 API 的频控限制)
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # ── 2.1 获取全局 Access Token ──────────────────
                token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
                token_resp = requests.get(token_url, timeout=self.timeout)
                _last_wechat_time = time.time()

                if token_resp.status_code == 429:
                    if attempt < max_attempts - 1:
                        sleep_time = 3.0 * (2 ** attempt) + random.uniform(0.1, 0.5)
                        time.sleep(sleep_time)
                        continue
                    else:
                        raise RuntimeError("微信接口频控超限 (429 Too Many Requests)，请稍后重试。")

                if token_resp.status_code != 200:
                    raise RuntimeError(f"获取微信 Access Token 失败，HTTP 状态码: {token_resp.status_code}")

                token_data = token_resp.json()
                errcode = token_data.get("errcode")
                if errcode:
                    if errcode in (40013, 40001):
                        raise RuntimeError("微信授权认证失败：AppID 或 AppSecret 错误，请在插件配置中核对。")
                    elif errcode == 45009:
                        if attempt < max_attempts - 1:
                            sleep_time = 3.0 * (2 ** attempt) + random.uniform(0.1, 0.5)
                            time.sleep(sleep_time)
                            continue
                        raise RuntimeError("微信公众号接口调用频控限制 (45009 api freq out of limit)。")
                    else:
                        raise RuntimeError(f"微信接口获取 Token 报错 (errcode {errcode}): {token_data.get('errmsg')}")

                access_token = token_data.get("access_token")
                if not access_token:
                    raise RuntimeError("无法提取微信 Access Token。")

                # ── 2.2 将图文推送至草稿箱 ────────────────────
                draft_url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
                resp = requests.post(draft_url, json=payload, headers={"Content-Type": "application/json"}, timeout=self.timeout)
                _last_wechat_time = time.time()

                if resp.status_code == 200:
                    resp_data = resp.json()
                    draft_errcode = resp_data.get("errcode", 0)
                    if draft_errcode == 0 and "media_id" in resp_data:
                        media_id = resp_data.get("media_id")
                        tlog.info(f"🚀 [微信公众号分发成功] 草稿 Media ID: {media_id}")
                        return {"media_id": media_id}
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
