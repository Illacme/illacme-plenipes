#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Dev.to Syndicator
模块职责：负责将内容分发至 Dev.to 平台。
🛡️ [AEL-Iter-v5.3]：全自治插件实现。
"""
import requests
from core.adapters.syndication.base import BaseSyndicator

from core.utils.tracing import tlog

class DevToSyndicator(BaseSyndicator):
    PLUGIN_ID = "devto"
    
    # 🚀 [V11.3] 声明运行时依赖契约
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict) -> dict:
        tags = metadata.get('tags', [])
        # Canonical URL 推导
        canonical_url = f"{self.site_url}/{slug}".replace('//', '/')
        
        return {
            "article": {
                "title": title,
                "body_markdown": content,
                "published": getattr(self.config, 'published', False),
                "tags": tags[:4],
                "canonical_url": canonical_url
            }
        }

    def push(self, payload: dict):
        api_key = getattr(self.config, 'api_key', None)
        if not api_key:
            tlog.warning("⚠️ [Dev.to] 缺少 API Key，分发跳过。")
            return
            
        url = "https://dev.to/api/articles"
        headers = {"api-key": api_key, "Content-Type": "application/json"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code == 201:
                tlog.info(f"🚀 [Dev.to 分发成功] 预览: {resp.json().get('url')}")
            else:
                tlog.warning(f"⚠️ [Dev.to 异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e:
            tlog.error(f"🛑 [Dev.to 失败]: {e}")
