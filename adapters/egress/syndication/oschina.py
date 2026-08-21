#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - OSChina (开源中国) Syndicator
模块职责：负责将稿件同步分发至开源中国博客平台。
"""

import requests
import threading
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

_last_oschina_time = 0.0
_oschina_lock = threading.Lock()

class OSChinaSyndicator(BaseSyndicator):
    PLUGIN_ID = "oschina"
    DISPLAY_NAME = "开源中国"
    VERSION = "V1.0"
    DESCRIPTION = "将文章同步发表至开源中国 (OSChina) 博客，触达国内最大开源软件社区与开发者资讯阵地。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        tags = metadata.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        return {
            "title": title,
            "content": content,
            "content_type": 3,  # 3: Markdown 格式
            "classification": metadata.get("oschina_classification") or 428612,  # 默认技术分类
            "type": 1 if metadata.get("is_original", True) else 4,  # 1: 原创, 4: 转载
            "origin_url": canonical_url,
            "save_as_draft": 1 if getattr(self.config, 'save_as_draft', True) else 0,
            "catalog": metadata.get("catalog") or "",
            "tags": ",".join(tags[:5])
        }

    def push(self, payload: dict):
        import time
        import random

        access_token = getattr(self.config, 'access_token', None) or self.config.get('access_token') or getattr(self.config, 'token', None) or self.config.get('token')

        if not access_token:
            tlog.warning("⚠️ [开源中国] 缺少 access_token 凭据配置，分发跳过。")
            return

        api_url = getattr(self.config, 'api_url', None) or self.config.get('api_url') or "https://www.oschina.net/action/openapi/blog_pub"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Illacme-Plenipes-OSChina-Client/1.0"
        }
        
        # 注入 access_token
        req_data = dict(payload)
        req_data["access_token"] = access_token
        req_data["dataType"] = "json"

        max_attempts = 3
        global _last_oschina_time
        for attempt in range(max_attempts):
            with _oschina_lock:
                while True:
                    elapsed = time.time() - _last_oschina_time
                    if elapsed < 2.0:
                        time.sleep(2.0 - elapsed)
                    else:
                        break

                _last_oschina_time = time.time()
                try:
                    resp = requests.post(api_url, data=req_data, headers=headers, timeout=self.timeout)
                    _last_oschina_time = time.time()
                except requests.RequestException as req_err:
                    _last_oschina_time = time.time()
                    if attempt < max_attempts - 1:
                        sleep_time = 2.0 + random.uniform(0.1, 0.5)
                        tlog.warning(f"⚠️ [开源中国网络重试] 正在休眠 {sleep_time:.2f} 秒后重试...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        tlog.error(f"🛑 [开源中国分发] 请求异常: {req_err}")
                        return

            if resp.status_code in [200, 201]:
                tlog.info(f"✅ [开源中国] 文章《{payload.get('title')}》成功同步分发！")
                return
            else:
                tlog.warning(f"⚠️ [开源中国] 服务端返回状态码 {resp.status_code}: {resp.text}")
                return
