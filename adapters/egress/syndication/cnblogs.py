#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - CNBlogs (博客园) Syndicator
模块职责：负责将稿件通过 MetaWeblog / REST API 同步分发至博客园。
"""

import requests
import threading
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

_last_cnblogs_time = 0.0
_cnblogs_lock = threading.Lock()

class CNBlogsSyndicator(BaseSyndicator):
    PLUGIN_ID = "cnblogs"
    DISPLAY_NAME = "博客园"
    VERSION = "V1.0"
    DESCRIPTION = "将文章同步发表至博客园 (CNBlogs)，支持原生 Markdown 格式与 MetaWeblog / REST API 规范。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        tags = metadata.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        return {
            "title": title,
            "postType": 1,  # 1: 博客文章
            "categoryIds": metadata.get("cnblogs_categories") or [],
            "tags": tags,
            "body": content,
            "isPublished": False if getattr(self.config, 'save_as_draft', True) else True,
            "canonicalUrl": canonical_url
        }

    def push(self, payload: dict):
        import time
        import random

        token = getattr(self.config, 'token', None) or self.config.get('token') or getattr(self.config, 'bearer_token', None) or self.config.get('bearer_token')
        blog_app = getattr(self.config, 'blog_app', None) or self.config.get('blog_app')

        if not token:
            tlog.warning("⚠️ [博客园] 缺少 token / bearer_token 配置，分发跳过。")
            return

        api_url = getattr(self.config, 'api_url', None) or self.config.get('api_url')
        if not api_url:
            if blog_app:
                api_url = "https://api.cnblogs.com/api/blogposts"
            else:
                api_url = "https://api.cnblogs.com/api/blogposts"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Illacme-Plenipes-CNBlogs-Client/1.0"
        }

        max_attempts = 3
        global _last_cnblogs_time
        for attempt in range(max_attempts):
            with _cnblogs_lock:
                while True:
                    elapsed = time.time() - _last_cnblogs_time
                    if elapsed < 2.0:
                        time.sleep(2.0 - elapsed)
                    else:
                        break

                _last_cnblogs_time = time.time()
                try:
                    resp = requests.post(api_url, json=payload, headers=headers, timeout=self.timeout)
                    _last_cnblogs_time = time.time()
                except requests.RequestException as req_err:
                    _last_cnblogs_time = time.time()
                    if attempt < max_attempts - 1:
                        sleep_time = 2.0 + random.uniform(0.1, 0.5)
                        tlog.warning(f"⚠️ [博客园网络重试] 正在休眠 {sleep_time:.2f} 秒后重试...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        tlog.error(f"🛑 [博客园分发] 请求异常: {req_err}")
                        return

            if resp.status_code in [200, 201]:
                tlog.info(f"✅ [博客园] 文章《{payload.get('title')}》成功同步分发！")
                return
            else:
                tlog.warning(f"⚠️ [博客园] 服务端返回状态码 {resp.status_code}: {resp.text}")
                return
