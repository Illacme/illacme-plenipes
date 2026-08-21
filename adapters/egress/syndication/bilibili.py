#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Bilibili Article (B站专栏) Syndicator
模块职责：负责将稿件同步分发至 Bilibili 专栏平台。
"""

import markdown
import requests
import threading
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

_last_bili_time = 0.0
_bili_lock = threading.Lock()

class BilibiliSyndicator(BaseSyndicator):
    PLUGIN_ID = "bilibili"
    DISPLAY_NAME = "Bilibili 专栏"
    VERSION = "V1.0"
    DESCRIPTION = "将文章同步发表至 Bilibili (B站) 专栏，触达年轻硬核极客与科技知识圈层。"
    
    REQUIRED_PACKAGES = ["requests", "markdown"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        # 将 Markdown 转换为 B 站专栏 HTML 富文本
        html_body = markdown.markdown(content, extensions=['extra', 'codehilite', 'tables'])
        
        tags = metadata.get("tags") or ["科技", "知识"]
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        summary = metadata.get("description") or metadata.get("summary") or (content[:120] + "...")
        banner_url = metadata.get("cover") or metadata.get("image") or ""

        return {
            "title": title,
            "banner_url": banner_url,
            "category": metadata.get("bili_category_id") or 17,  # 默认分类：科技/数码/泛知识
            "tags": ",".join(tags[:4]),
            "summary": summary,
            "content": html_body,
            "original": 1 if metadata.get("is_original", True) else 0,
            "original_url": canonical_url
        }

    def push(self, payload: dict):
        import time
        import random

        sessdata = getattr(self.config, 'sessdata', None) or self.config.get('sessdata')
        bili_jct = getattr(self.config, 'bili_jct', None) or self.config.get('bili_jct')
        cookie = getattr(self.config, 'cookie', None) or self.config.get('cookie')
        token = getattr(self.config, 'token', None) or self.config.get('token')

        if not (sessdata or cookie or token):
            tlog.warning("⚠️ [Bilibili 专栏] 缺少 SESSDATA / Cookie 凭据配置，分发跳过。")
            return

        api_url = getattr(self.config, 'api_url', None) or self.config.get('api_url') or "https://api.bilibili.com/x/article/creative/draft/addupdate"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://member.bilibili.com/platform/article-up"
        }
        
        if cookie:
            headers["Cookie"] = cookie
        elif sessdata:
            headers["Cookie"] = f"SESSDATA={sessdata}; bili_jct={bili_jct or ''};"
        if token:
            headers["Authorization"] = f"Bearer {token}"

        max_attempts = 3
        global _last_bili_time
        for attempt in range(max_attempts):
            with _bili_lock:
                while True:
                    elapsed = time.time() - _last_bili_time
                    if elapsed < 2.0:
                        time.sleep(2.0 - elapsed)
                    else:
                        break

                _last_bili_time = time.time()
                try:
                    resp = requests.post(api_url, json=payload, headers=headers, timeout=self.timeout)
                    _last_bili_time = time.time()
                except requests.RequestException as req_err:
                    _last_bili_time = time.time()
                    if attempt < max_attempts - 1:
                        sleep_time = 2.0 + random.uniform(0.1, 0.5)
                        tlog.warning(f"⚠️ [Bilibili 网络重试] 正在休眠 {sleep_time:.2f} 秒后重试...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        tlog.error(f"🛑 [Bilibili 分发] 请求异常: {req_err}")
                        return

            if resp.status_code in [200, 201]:
                tlog.info(f"✅ [Bilibili 专栏] 文章《{payload.get('title')}》成功同步分发！")
                return
            else:
                tlog.warning(f"⚠️ [Bilibili 专栏] 服务端返回状态码 {resp.status_code}: {resp.text}")
                return
