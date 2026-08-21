#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - CSDN Blog Syndicator
模块职责：负责将稿件同步分发至 CSDN 博客平台。
"""

import requests
import threading
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

_last_csdn_time = 0.0
_csdn_lock = threading.Lock()

class CSDNSyndicator(BaseSyndicator):
    PLUGIN_ID = "csdn"
    DISPLAY_NAME = "CSDN 博客"
    VERSION = "V1.0"
    DESCRIPTION = "将 Markdown 文章同步发表至 CSDN 博客或草稿箱，具备极高搜索引擎收录权重与长尾曝光。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        tags = metadata.get("tags") or ["技术手记"]
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        
        digest = metadata.get("description") or metadata.get("summary") or (content[:150] + "...")

        return {
            "title": title,
            "markdowncontent": content,
            "content": content,
            "tags": ",".join(tags[:5]),
            "categories": metadata.get("category") or "技术分享",
            "type": "original" if metadata.get("is_original", True) else "repost",
            "original_url": canonical_url,
            "status": getattr(self.config, 'status', 2) or 2,  # 2: 草稿, 0: 直接发布
            "description": digest
        }

    def push(self, payload: dict):
        import time
        import random

        token = getattr(self.config, 'token', None) or self.config.get('token')
        cookie = getattr(self.config, 'cookie', None) or self.config.get('cookie')

        if not token and not cookie:
            tlog.warning("⚠️ [CSDN 博客] 缺少 token 或 cookie 凭据配置，分发跳过。")
            return

        api_url = getattr(self.config, 'api_url', None) or self.config.get('api_url') or "https://bizapi.csdn.net/blog-console-api/v3/article/saveArticle"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if token:
            headers["X-CSDN-Token"] = token
            headers["Authorization"] = f"Bearer {token}"
        if cookie:
            headers["Cookie"] = cookie

        max_attempts = 3
        global _last_csdn_time
        for attempt in range(max_attempts):
            with _csdn_lock:
                while True:
                    elapsed = time.time() - _last_csdn_time
                    if elapsed < 2.0:
                        time.sleep(2.0 - elapsed)
                    else:
                        break

                _last_csdn_time = time.time()
                try:
                    resp = requests.post(api_url, json=payload, headers=headers, timeout=self.timeout)
                    _last_csdn_time = time.time()
                except requests.RequestException as req_err:
                    _last_csdn_time = time.time()
                    if attempt < max_attempts - 1:
                        sleep_time = 2.0 + random.uniform(0.1, 0.5)
                        tlog.warning(f"⚠️ [CSDN 网络重试] 正在休眠 {sleep_time:.2f} 秒后重试...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        tlog.error(f"🛑 [CSDN 分发] 请求异常: {req_err}")
                        return

            if resp.status_code in [200, 201]:
                tlog.info(f"✅ [CSDN 博客] 文章《{payload.get('title')}》成功同步分发！")
                return
            else:
                tlog.warning(f"⚠️ [CSDN 博客] 服务端返回状态码 {resp.status_code}: {resp.text}")
                return
