#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SegmentFault (思否) Syndicator
模块职责：负责将稿件同步分发至 SegmentFault 思否专栏。
"""

import requests
import threading
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

_last_sf_time = 0.0
_sf_lock = threading.Lock()

class SegmentFaultSyndicator(BaseSyndicator):
    PLUGIN_ID = "segmentfault"
    DISPLAY_NAME = "SegmentFault 思否"
    VERSION = "V1.0"
    DESCRIPTION = "将文章同步发表至 SegmentFault 思否开发者专栏或草稿箱，触达一线现代技术圈层。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        tags = metadata.get("tags") or ["javascript", "python"]
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        return {
            "title": title,
            "text": content,
            "tags": tags[:5],
            "blog_id": getattr(self.config, 'blog_id', None) or self.config.get('blog_id'),
            "is_draft": 1 if getattr(self.config, 'save_as_draft', True) else 0,
            "original_url": canonical_url
        }

    def push(self, payload: dict):
        import time
        import random

        token = getattr(self.config, 'token', None) or self.config.get('token')
        cookie = getattr(self.config, 'cookie', None) or self.config.get('cookie')

        if not token and not cookie:
            tlog.warning("⚠️ [SegmentFault] 缺少 token 或 cookie 配置，分发跳过。")
            return

        api_url = getattr(self.config, 'api_url', None) or self.config.get('api_url') or "https://segmentfault.com/api/article/draft/save"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
            headers["X-SF-Token"] = token
        if cookie:
            headers["Cookie"] = cookie

        max_attempts = 3
        global _last_sf_time
        for attempt in range(max_attempts):
            with _sf_lock:
                while True:
                    elapsed = time.time() - _last_sf_time
                    if elapsed < 2.0:
                        time.sleep(2.0 - elapsed)
                    else:
                        break

                _last_sf_time = time.time()
                try:
                    resp = requests.post(api_url, json=payload, headers=headers, timeout=self.timeout)
                    _last_sf_time = time.time()
                except requests.RequestException as req_err:
                    _last_sf_time = time.time()
                    if attempt < max_attempts - 1:
                        sleep_time = 2.0 + random.uniform(0.1, 0.5)
                        tlog.warning(f"⚠️ [SegmentFault 网络重试] 正在休眠 {sleep_time:.2f} 秒后重试...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        tlog.error(f"🛑 [SegmentFault 分发] 请求异常: {req_err}")
                        return

            if resp.status_code in [200, 201]:
                tlog.info(f"✅ [SegmentFault] 文章《{payload.get('title')}》成功同步分发！")
                return
            else:
                tlog.warning(f"⚠️ [SegmentFault] 服务端返回状态码 {resp.status_code}: {resp.text}")
                return
