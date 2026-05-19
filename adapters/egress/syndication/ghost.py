#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Ghost Syndicator Plugin
🚀 [V75.1]：对齐 BaseSyndicator 物理契约。
"""

from typing import Dict, Any
from core.adapters.syndication.base import BaseSyndicator

class GhostSyndicator(BaseSyndicator):
    PLUGIN_ID = "ghost"
    DISPLAY_NAME = "Ghost"
    VERSION = "V1.1"
    DESCRIPTION = "同步至 Ghost 专业出版平台，支持 Content API 物理对接。"

    def format_payload(self, title: str, slug: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "posts": [{
                "title": title,
                "markdown": content,
                "status": "draft"
            }]
        }

    def push(self, payload: Dict[str, Any]):
        # 预留给未来真实 API 开发，当前安全空过
        pass
