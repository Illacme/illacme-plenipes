#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Toutiao (今日头条) Syndicator
模块职责：负责将稿件同步分发至今日头条（头条号）平台。
"""

import markdown
import requests
import threading
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

_last_toutiao_time = 0.0
_toutiao_lock = threading.Lock()

class ToutiaoSyndicator(BaseSyndicator):
    PLUGIN_ID = "toutiao"
    DISPLAY_NAME = "今日头条"
    VERSION = "V1.0"
    DESCRIPTION = "将文章同步发表至今日头条（头条号），支持字节算法大盘分发与草稿/公开发布。"
    
    REQUIRED_PACKAGES = ["requests", "markdown"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        # 将 Markdown 转换为头条号兼容的 HTML 富文本内容
        html_body = markdown.markdown(content, extensions=['extra', 'codehilite', 'tables'])
        
        abstract = metadata.get("description") or metadata.get("abstract") or (content[:150] + "...")
        cover_image = metadata.get("cover") or metadata.get("image") or ""

        return {
            "title": title,
            "content": html_body,
            "abstract": abstract,
            "cover_url": cover_image,
            "source_url": canonical_url,
            "is_original": 1 if metadata.get("is_original", True) else 0,
            "save_as_draft": 1 if getattr(self.config, 'save_as_draft', True) else 0
        }

    def push(self, payload: dict):
        import time
        import random

        access_token = getattr(self.config, 'access_token', None) or self.config.get('access_token') or getattr(self.config, 'token', None) or self.config.get('token')
        cookie = getattr(self.config, 'cookie', None) or self.config.get('cookie')

        if not access_token and not cookie:
            tlog.warning("⚠️ [今日头条] 缺少 access_token 或 cookie 凭据配置，分发跳过。")
            return

        api_url = getattr(self.config, 'api_url', None) or self.config.get('api_url') or "https://open.toutiao.com/data/article/post/"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Illacme-Plenipes-Toutiao-Syndicator/1.0"
        }
        if access_token:
            headers["Access-Token"] = access_token
        if cookie:
            headers["Cookie"] = cookie

        max_attempts = 3
        global _last_toutiao_time
        for attempt in range(max_attempts):
            with _toutiao_lock:
                while True:
                    elapsed = time.time() - _last_toutiao_time
                    if elapsed < 2.0:
                        time.sleep(2.0 - elapsed)
                    else:
                        break

                _last_toutiao_time = time.time()
                try:
                    resp = requests.post(api_url, json=payload, headers=headers, timeout=self.timeout)
                    _last_toutiao_time = time.time()
                except requests.RequestException as req_err:
                    _last_toutiao_time = time.time()
                    if attempt < max_attempts - 1:
                        sleep_time = 2.0 + random.uniform(0.1, 0.5)
                        tlog.warning(f"⚠️ [今日头条网络重试] 正在休眠 {sleep_time:.2f} 秒后重试...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        tlog.error(f"🛑 [今日头条分发] 请求异常: {req_err}")
                        return

            if resp.status_code in [200, 201]:
                tlog.info(f"✅ [今日头条] 文章《{payload.get('title')}》成功同步分发！")
                return
            else:
                tlog.warning(f"⚠️ [今日头条] 服务端返回状态码 {resp.status_code}: {resp.text}")
                return
