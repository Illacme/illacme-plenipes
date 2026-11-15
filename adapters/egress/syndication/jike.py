#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Jike (即刻) Syndicator
模块职责：负责将稿件智能转换为即刻短动态并装配多图卡片轮播 (3:4 / 1:1)。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import re
import time
import requests
import threading
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

_last_jike_time = 0.0
_jike_lock = threading.Lock()


class JikeSyndicator(BaseSyndicator):
    PLUGIN_ID = "jike"
    DISPLAY_NAME = "即刻"
    ICON = "🟡"
    VERSION = "v1.8.0"
    DESCRIPTION = "将文章提炼为精炼动态，装配多图卡片轮播 (3:4 / 1:1)，同步至即刻圈子或个人主页。"
    SLA_TIER = "tier2"
    SLA_LABEL = "Token辅助"
    SLA_DESC = "依赖即刻 x-access-token / app-token 或 Cookie 凭据，支持 3:4/1:1 多图轮播。"

    REQUIRED_PACKAGES = ["requests"]

    def _normalize_image_url(self, raw_path: str, site_url: str) -> Optional[str]:
        if not raw_path:
            return None
        p = str(raw_path).strip().strip("'\"")
        if p.startswith("http://") or p.startswith("https://"):
            return p
        if not site_url:
            return None
        return urljoin(site_url.rstrip("/") + "/", p.lstrip("/"))

    def _resolve_deck_images(self, slug: str, site_url: str) -> List[str]:
        """优先嗅探由卡片工坊派生的 3:4 / 1:1 知识卡片图集 (即刻短动态黄金轮播)"""
        clean_slug = "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in (slug or "")])
        if not clean_slug:
            return []
        candidates = [f"{clean_slug}_3x4", f"{clean_slug}_1x1", clean_slug]
        target_dir, folder_name = None, clean_slug
        for cand in candidates:
            d = os.path.join(os.getcwd(), ".plenipes", "cache", "cards", cand)
            if os.path.isdir(d):
                target_dir, folder_name = d, cand
                break
        if not target_dir:
            return []
        files = sorted([f for f in os.listdir(target_dir) if f.startswith("card_") and f.endswith(".jpg")])
        urls = [f"{site_url.rstrip('/')}/api/design/assets/cards/{folder_name}/{fn}" if site_url else f"/api/design/assets/cards/{folder_name}/{fn}" for fn in files]
        if urls:
            tlog.info(f"📑 [即刻] 自动装配知识卡片多图轮播 ({len(urls)} 张): {folder_name}")
        return urls

    def extract_images(self, content: str, metadata: dict, site_url: str) -> List[str]:
        image_urls: List[str] = []
        cover = metadata.get("cover") or metadata.get("image") or metadata.get("banner")
        norm_cover = self._normalize_image_url(cover, site_url)
        if norm_cover:
            image_urls.append(norm_cover)

        for img in re.findall(r'!\[.*?\]\(([^)\s]+)', content):
            u = self._normalize_image_url(img, site_url)
            if u and u not in image_urls:
                image_urls.append(u)
                if len(image_urls) >= 9:
                    return image_urls
        return image_urls

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> Dict[str, Any]:
        site_url = self.site_url.rstrip('/') if self.site_url else ""
        if not canonical_url:
            canonical_url = f"{site_url}/{slug}".replace('//', '/').replace(':/', '://') if site_url else f"/{slug}"

        metadata = metadata or {}
        deck_imgs = self._resolve_deck_images(slug, site_url)
        image_urls = deck_imgs[:9] if deck_imgs else self.extract_images(content, metadata, site_url)[:9]

        raw_tags = metadata.get("tags") or []
        if isinstance(raw_tags, str):
            raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
        tags_str = " ".join([f"#{t}#" for t in raw_tags[:5]])

        clean_title = title.replace("#", "").replace("*", "").strip()
        body = content.strip()
        body = re.sub(r'```[\s\S]*?```', '[💻 代码实现请查阅全文链接]', body)
        body = re.sub(r'(?m)^#{1,6}\s+(.+)$', r'📌 \1', body)
        lines = [l.strip() for l in body.split('\n') if l.strip()]
        excerpt = "\n\n".join(lines[:4])
        if len(excerpt) > 400:
            excerpt = excerpt[:390] + "..."

        topic_id = metadata.get("jike_topic_id") or getattr(self.config, "topic_id", None) or (self.config.get("topic_id") if isinstance(self.config, dict) else "")

        full_content = f"【{clean_title}】\n\n{excerpt}\n\n📖 全文指引: {canonical_url}\n{tags_str}".strip()

        return {
            "title": clean_title,
            "content": full_content,
            "images": image_urls,
            "topic_id": str(topic_id).strip() if topic_id else "",
            "canonical_url": canonical_url,
            "total_images": len(image_urls)
        }

    def push(self, payload: Dict[str, Any], remote_id: str = None) -> Dict[str, Any]:
        token = getattr(self.config, 'token', None) or (self.config.get('token') if isinstance(self.config, dict) else None)
        app_token = getattr(self.config, 'app_token', None) or (self.config.get('app_token') if isinstance(self.config, dict) else None)
        cookie = getattr(self.config, 'cookie', None) or (self.config.get('cookie') if isinstance(self.config, dict) else None)
        active_token = token or app_token

        if not active_token and not cookie:
            tlog.warning("⚠️ [即刻] 缺少访问令牌 (Token) 或 Cookie 凭据，分发取消。")
            return {"success": False, "error": "缺少即刻 Token 或 Cookie 凭据"}

        api_url = getattr(self.config, 'api_url', None) or (self.config.get('api_url') if isinstance(self.config, dict) else None) or "https://api.ruguoapp.com/1.0/originalPosts/create"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Jike/7.0.0",
            "Referer": "https://web.okjike.com"
        }
        if active_token:
            headers["x-access-token"] = active_token
            headers["app-token"] = active_token
        if cookie:
            headers["Cookie"] = cookie

        proxy_url = getattr(self.config, 'proxy', None) or (self.config.get('proxy') if isinstance(self.config, dict) else None)
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url and proxy_url.lower() != "direct" else {}

        post_data: Dict[str, Any] = {"content": payload.get("content", "")}
        if payload.get("topic_id"):
            post_data["topic"] = payload["topic_id"]
        if payload.get("images"):
            post_data["pictureKeys"] = payload["images"]

        global _last_jike_time
        with _jike_lock:
            elapsed = time.time() - _last_jike_time
            if elapsed < 2.0:
                time.sleep(2.0 - elapsed)
            _last_jike_time = time.time()

            try:
                resp = requests.post(api_url, json=post_data, headers=headers, proxies=proxies, timeout=self.timeout)
                _last_jike_time = time.time()
                if resp.status_code in (200, 201):
                    res_json = resp.json() if resp.text else {}
                    post_id = res_json.get("id") or res_json.get("postId") or f"jike_{int(time.time())}"
                    tlog.info(f"🟢 [即刻] 动态分发成功！Post ID: {post_id}")
                    return {"success": True, "remote_id": str(post_id), "url": f"https://web.okjike.com/originalPost/{post_id}"}
                else:
                    msg = f"HTTP {resp.status_code}: {resp.text[:180]}"
                    tlog.error(f"❌ [即刻] 分发响应失败: {msg}")
                    return {"success": False, "error": msg}
            except Exception as e:
                _last_jike_time = time.time()
                tlog.error(f"❌ [即刻] 请求异常: {e}")
                return {"success": False, "error": str(e)}

