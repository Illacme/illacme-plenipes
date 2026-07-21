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
    DISPLAY_NAME = "Dev.to"
    VERSION = "V1.0"
    DESCRIPTION = "将内容同步分发至全球开发者社区 Dev.to，支持标签映射与原文链接回溯。"
    
    # 🚀 [V11.3] 声明运行时依赖契约
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        tags = metadata.get('tags', [])
        # Canonical URL 优先使用传入值，否则 Fallback 推导
        if not canonical_url and self.site_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        payload = {
            "article": {
                "title": title,
                "body_markdown": content,
                "published": self.config.get('published', False) if isinstance(self.config, dict) else getattr(self.config, 'published', False),
                "tags": tags[:4]
            }
        }
        
        # 🛡️ [V89.3] 极其强顺的公网 Canonical URL 校验
        if canonical_url and (canonical_url.startswith("http://") or canonical_url.startswith("https://")):
            payload["article"]["canonical_url"] = canonical_url
            
        return payload

    def push(self, payload: dict):
        api_key = self.config.get('api_key') if isinstance(self.config, dict) else getattr(self.config, 'api_key', None)
        if not api_key:
            raise RuntimeError("缺少 API Key，分发自动熔断。")
            
        url = "https://dev.to/api/articles"
        headers = {"api-key": api_key, "Content-Type": "application/json"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code == 201:
                publish_url = resp.json().get('url')
                tlog.info(f"🚀 [Dev.to 分发成功] 预览: {publish_url}")
                return {"url": publish_url}
            else:
                raise RuntimeError(f"对端接口返回错误 (状态码 {resp.status_code}): {resp.text[:200]}")
        except Exception as e:
            tlog.error(f"🛑 [Dev.to 失败]: {e}")
            raise e
