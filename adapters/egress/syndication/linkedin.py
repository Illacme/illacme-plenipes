#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — LinkedIn Syndicator Plugin
🚀 [V75.1]：对齐 BaseSyndicator 物理契约。
"""

from typing import Dict, Any
from core.adapters.syndication.base import BaseSyndicator

class LinkedInSyndicator(BaseSyndicator):
    PLUGIN_ID = "linkedin"
    DISPLAY_NAME = "LinkedIn"
    VERSION = "V1.1"
    DESCRIPTION = "同步至 LinkedIn 职场社交平台，支持分享文章至个人动态与组织页面。"

    def format_payload(self, title: str, slug: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "commentary": title,
            "content": content
        }

    def push(self, payload: Dict[str, Any]):
        # 预留给未来真实 API 开发，当前安全空过
        pass
