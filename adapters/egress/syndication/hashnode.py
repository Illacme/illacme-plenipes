#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Hashnode Syndicator Plugin
🚀 [V75.1]：对齐 BaseSyndicator 物理契约。
"""

from typing import Dict, Any
from core.adapters.syndication.base import BaseSyndicator

class HashnodeSyndicator(BaseSyndicator):
    PLUGIN_ID = "hashnode"
    DISPLAY_NAME = "Hashnode"
    VERSION = "V1.1"
    DESCRIPTION = "同步至 Hashnode 全球博客社区，支持 GraphQL 协议分发。"

    def format_payload(self, title: str, slug: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "input": {
                "title": title,
                "markdown": content,
                "tags": []
            }
        }

    def push(self, payload: Dict[str, Any]):
        # 预留给未来真实 API 开发，当前安全空过
        pass
