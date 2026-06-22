#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Zhihu Syndicator
模块职责：负责将稿件同步分发至知乎专栏。
"""

import requests
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


class ZhihuSyndicator(BaseSyndicator):
    PLUGIN_ID = "zhihu"
    DISPLAY_NAME = "知乎"
    VERSION = "V1.0"
    DESCRIPTION = "将文章同步发表至指定的知乎专栏，支持 Markdown 内容排版。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        # 知乎官方及常见扩展通常接受 HTML 或 Markdown 格式的内容
        return {
            "title": title,
            "content": content,
            "column_id": getattr(self.config, 'column_id', None) or self.config.get('column_id'),
            "source_url": canonical_url,
            "state": "draft"  # 默认发布为草稿以保防误触
        }

    def push(self, payload: dict):
        token = getattr(self.config, 'token', None) or self.config.get('token')
        column_id = payload.get("column_id")

        if not token:
            tlog.warning("⚠️ [知乎专栏] 缺少 token 配置，分发跳过。")
            return
        if not column_id:
            tlog.warning("⚠️ [知乎专栏] 缺少 column_id 配置，分发跳过。")
            return

        url = f"https://api.zhihu.com/columns/{column_id}/articles"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Illacme-Plenipes-Client"
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code in [200, 201]:
                tlog.info(f"🚀 [知乎分发成功] 文章已成功同步至专栏 '{column_id}'。")
            else:
                tlog.warning(f"⚠️ [知乎异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e:
            tlog.error(f"🛑 [知乎失败]: {e}")
