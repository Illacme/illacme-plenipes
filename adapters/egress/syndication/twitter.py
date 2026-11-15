#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Twitter / X Syndicator
模块职责：负责将稿件智能转换为精炼推文并装配 16:9 / 1:1 知识卡片海报轮播 (至多 4 张)。
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

_last_twitter_time = 0.0
_twitter_lock = threading.Lock()


class TwitterSyndicator(BaseSyndicator):
    PLUGIN_ID = "twitter"
    DISPLAY_NAME = "Twitter / X"
    ICON = "𝕏"
    VERSION = "v1.8.0"
    DESCRIPTION = "将文章提炼为精炼推文与核心观点，装配 16:9 宽屏或 1:1 知识卡片海报轮播 (最多 4 张)，同步推向 Twitter / X。"
    SLA_TIER = "tier1"
    SLA_LABEL = "双模支持"
    SLA_DESC = "支持 Twitter API v2 Bearer Token / OAuth 直连，或自建 API 网关代理。"

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
        """优先嗅探由卡片工坊派生的 16:9 宽屏或 1:1 知识卡片海报 (Twitter 黄金画幅，至多 4 张)"""
        clean_slug = "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in (slug or "")])
        if not clean_slug:
            return []
        candidates = [f"{clean_slug}_16x9", f"{clean_slug}_1x1", f"{clean_slug}_3x4", clean_slug]
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
            tlog.info(f"📑 [Twitter/X] 自动装配知识卡片推文轮播 ({min(len(urls), 4)} 张): {folder_name}")
        return urls[:4]

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
                if len(image_urls) >= 4:
                    return image_urls
        return image_urls[:4]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> Dict[str, Any]:
        site_url = self.site_url.rstrip('/') if self.site_url else ""
        if not canonical_url:
            canonical_url = f"{site_url}/{slug}".replace('//', '/').replace(':/', '://') if site_url else f"/{slug}"

        metadata = metadata or {}
        deck_imgs = self._resolve_deck_images(slug, site_url)
        image_urls = deck_imgs if deck_imgs else self.extract_images(content, metadata, site_url)

        raw_tags = metadata.get("tags") or []
        if isinstance(raw_tags, str):
            raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
        clean_tags = [re.sub(r'^[#＃]+', '', str(t)).strip() for t in raw_tags if str(t).strip()]
        tags_str = " ".join([f"#{t}" for t in clean_tags[:4]])

        clean_title = title.replace("#", "").replace("*", "").strip()
        body = content.strip()
        body = re.sub(r'```[\s\S]*?```', '', body)
        body = re.sub(r'(?m)^#{1,6}\s+(.+)$', r'\1', body)
        lines = [l.strip() for l in body.split('\n') if l.strip()]
        excerpt = " ".join(lines[:2])
        if len(excerpt) > 120:
            excerpt = excerpt[:110] + "..."

        tweet_text = f"【{clean_title}】\n\n{excerpt}\n\n🔗 Read more: {canonical_url}\n{tags_str}".strip()

        return {
            "title": clean_title,
            "text": tweet_text,
            "images": image_urls,
            "canonical_url": canonical_url,
            "total_images": len(image_urls)
        }

    def push(self, payload: Dict[str, Any], remote_id: str = None) -> Dict[str, Any]:
        bearer_token = getattr(self.config, 'bearer_token', None) or (self.config.get('bearer_token') if isinstance(self.config, dict) else None)
        token = getattr(self.config, 'token', None) or (self.config.get('token') if isinstance(self.config, dict) else None)
        api_key = getattr(self.config, 'api_key', None) or (self.config.get('api_key') if isinstance(self.config, dict) else None)
        active_token = bearer_token or token or api_key

        if not active_token:
            tlog.warning("⚠️ [Twitter / X] 缺少 Bearer Token 或 API Key 凭据，分发取消。")
            return {"success": False, "error": "缺少 Twitter / X Bearer Token 凭据"}

        api_url = getattr(self.config, 'api_url', None) or (self.config.get('api_url') if isinstance(self.config, dict) else None) or "https://api.twitter.com/2/tweets"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {active_token}",
            "User-Agent": "Illacme-Plenipes-Syndication/1.0"
        }

        proxy_url = getattr(self.config, 'proxy', None) or (self.config.get('proxy') if isinstance(self.config, dict) else None)
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url and proxy_url.lower() != "direct" else {}

        post_data = {"text": payload.get("text", "")}

        global _last_twitter_time
        with _twitter_lock:
            elapsed = time.time() - _last_twitter_time
            if elapsed < 2.0:
                time.sleep(2.0 - elapsed)
            _last_twitter_time = time.time()

            try:
                resp = requests.post(api_url, json=post_data, headers=headers, proxies=proxies, timeout=self.timeout)
                _last_twitter_time = time.time()
                if resp.status_code in (200, 201):
                    res_json = resp.json() if resp.text else {}
                    tweet_data = res_json.get("data", {})
                    tweet_id = tweet_data.get("id") or res_json.get("id") or f"tw_{int(time.time())}"
                    tlog.info(f"🟢 [Twitter / X] 推文发布成功！Tweet ID: {tweet_id}")
                    return {"success": True, "remote_id": str(tweet_id), "url": f"https://x.com/i/status/{tweet_id}"}
                else:
                    msg = f"HTTP {resp.status_code}: {resp.text[:180]}"
                    tlog.error(f"❌ [Twitter / X] 响应失败: {msg}")
                    return {"success": False, "error": msg}
            except Exception as e:
                _last_twitter_time = time.time()
                tlog.error(f"❌ [Twitter / X] 请求异常: {e}")
                return {"success": False, "error": str(e)}

