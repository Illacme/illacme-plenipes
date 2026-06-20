#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Medium Syndicator Plugin
🚀 [V75.1]：全面对齐 BaseSyndicator 物理契约，彻底清扫零散碎片。
"""

import requests
from typing import Dict, Any
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

class MediumSyndicator(BaseSyndicator):
    PLUGIN_ID = "medium"
    DISPLAY_NAME = "Medium"
    VERSION = "V1.1"
    DESCRIPTION = "同步至 Medium 全球创作平台，支持 Markdown 格式化与 Canonical URL 溯源。"

    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: Dict[str, Any], canonical_url: str = None) -> Dict[str, Any]:
        """对齐 BaseSyndicator 抽象接口契约"""
        tags = metadata.get('tags', [])
        # Canonical URL 优先使用传入值，否则 Fallback 推导
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        return {
            "title": title,
            "contentFormat": "markdown",
            "content": content,
            "canonicalUrl": canonical_url,
            "tags": tags[:5],
            "publishStatus": getattr(self.config, 'publish_status', 'draft') # 默认为草稿模式，安全防呆
        }

    def push(self, payload: Dict[str, Any]):
        """执行物理推流到 Medium"""
        token = getattr(self.config, 'integration_token', None)
        if not token:
            tlog.warning("⚠️ [Medium] 缺少 integration_token，分发跳过。")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            # 1. 物理获取当前授权的 Author ID
            user_url = "https://api.medium.com/v1/me"
            user_resp = requests.get(user_url, headers=headers, timeout=self.timeout)
            if user_resp.status_code != 200:
                raise RuntimeError(f"Medium 账户认证失败 ({user_resp.status_code}): {user_resp.text}")

            author_id = user_resp.json().get("data", {}).get("id")
            if not author_id:
                raise RuntimeError("无法提取 Medium Author ID。")

            # 2. 推送文章
            post_url = f"https://api.medium.com/v1/users/{author_id}/posts"
            resp = requests.post(post_url, json=payload, headers=headers, timeout=self.timeout)

            if resp.status_code in [200, 201]:
                post_link = resp.json().get("data", {}).get("url")
                tlog.info(f"✨ [Medium 同步成功] 链接: {post_link}")
            else:
                raise RuntimeError(f"Medium API 报错 ({resp.status_code}): {resp.text}")

        except Exception as e:
            tlog.error(f"🛑 [Medium 失败]: {e}")
            raise e
