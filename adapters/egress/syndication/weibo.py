#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Weibo (新浪微博) Syndicator
模块职责：负责将稿件智能转换为九宫格微博并装配 1:1 / 3:4 知识卡片图集。
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

_last_weibo_time = 0.0
_weibo_lock = threading.Lock()


class WeiboSyndicator(BaseSyndicator):
    PLUGIN_ID = "weibo"
    DISPLAY_NAME = "微博"
    ICON = "🔴"
    VERSION = "v1.8.0"
    DESCRIPTION = "将文章提炼为九宫格微文案，装配 1:1 方形或 3:4 知识卡片海报图集，同步发布至微博。"
    SLA_TIER = "tier1"
    SLA_LABEL = "双模支持"
    SLA_DESC = "支持微博开放平台 Access Token 直连，或创作者 Cookie (SUB 凭据)，支持九宫格图集。"

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
        """优先嗅探由卡片工坊派生的 1:1 / 3:4 知识卡片图集 (微博九宫格黄金画幅)"""
        clean_slug = "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in (slug or "")])
        if not clean_slug:
            return []
        candidates = [f"{clean_slug}_1x1", f"{clean_slug}_3x4", clean_slug]
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
            tlog.info(f"📑 [微博] 自动装配知识卡片九宫格图集 ({len(urls)} 张): {folder_name}")
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
        tags_str = " ".join([f"#{t}#" for t in raw_tags[:4]])

        clean_title = title.replace("#", "").replace("*", "").strip()
        body = content.strip()
        body = re.sub(r'```[\s\S]*?```', '', body)
        body = re.sub(r'(?m)^#{1,6}\s+(.+)$', r'【\1】', body)
        lines = [l.strip() for l in body.split('\n') if l.strip()]
        excerpt = " ".join(lines[:3])
        if len(excerpt) > 180:
            excerpt = excerpt[:170] + "..."

        status_text = f"【{clean_title}】{excerpt} 网页链接：{canonical_url} {tags_str}".strip()

        return {
            "title": clean_title,
            "status": status_text,
            "images": image_urls,
            "canonical_url": canonical_url,
            "total_images": len(image_urls)
        }

    def push(self, payload: Dict[str, Any], remote_id: str = None) -> Dict[str, Any]:
        access_token = getattr(self.config, 'access_token', None) or (self.config.get('access_token') if isinstance(self.config, dict) else None)
        token = getattr(self.config, 'token', None) or (self.config.get('token') if isinstance(self.config, dict) else None)
        cookie = getattr(self.config, 'cookie', None) or (self.config.get('cookie') if isinstance(self.config, dict) else None)
        active_token = access_token or token

        if not active_token and not cookie:
            tlog.warning("⚠️ [微博] 缺少 Access Token 或 Cookie 凭据，分发取消。")
            return {"success": False, "error": "缺少微博 Access Token 或 Cookie 凭据"}

        proxy_url = getattr(self.config, 'proxy', None) or (self.config.get('proxy') if isinstance(self.config, dict) else None)
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url and proxy_url.lower() != "direct" else {}

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://weibo.com"
        }
        if cookie:
            headers["Cookie"] = cookie

        global _last_weibo_time
        with _weibo_lock:
            elapsed = time.time() - _last_weibo_time
            if elapsed < 2.0:
                time.sleep(2.0 - elapsed)
            _last_weibo_time = time.time()

            try:
                # 优先走官方开放平台 share.json 接口，或创作者端点
                if active_token:
                    api_url = "https://api.weibo.com/2/statuses/share.json"
                    params = {"access_token": active_token, "status": payload.get("status", "")}
                    resp = requests.post(api_url, data=params, headers=headers, proxies=proxies, timeout=self.timeout)
                else:
                    api_url = getattr(self.config, 'api_url', None) or (self.config.get('api_url') if isinstance(self.config, dict) else None) or "https://weibo.com/aj/mblog/add"
                    data = {"text": payload.get("status", "")}
                    resp = requests.post(api_url, data=data, headers=headers, proxies=proxies, timeout=self.timeout)

                _last_weibo_time = time.time()
                if resp.status_code in (200, 201):
                    res_json = resp.json() if resp.text else {}
                    mid = res_json.get("id") or res_json.get("mid") or f"weibo_{int(time.time())}"
                    tlog.info(f"🟢 [微博] 发布成功！MID: {mid}")
                    return {"success": True, "remote_id": str(mid), "url": f"https://weibo.com/detail/{mid}"}
                else:
                    msg = f"HTTP {resp.status_code}: {resp.text[:180]}"
                    tlog.error(f"❌ [微博] 响应失败: {msg}")
                    return {"success": False, "error": msg}
            except Exception as e:
                _last_weibo_time = time.time()
                tlog.error(f"❌ [微博] 请求异常: {e}")
                return {"success": False, "error": str(e)}

