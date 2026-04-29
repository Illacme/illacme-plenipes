#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Provider Registry
模块职责：管理所有 AI 算力协议的注册与发现。
🛡️ [AEL-Iter-v5.3]：全链路透明化的算力注册机。
"""

import logging
from typing import Dict, Type

from core.utils.tracing import tlog

class AIProviderRegistry:
    """🚀 AI 算力协议注册中心"""
    _providers: Dict[str, Type] = {}

    @classmethod
    def register(cls, ptype: str, provider_class: Type):
        cls._providers[ptype] = provider_class
        tlog.debug(f"🤖 [算力插件] 已注册协议: {ptype}")

    @classmethod
    def get_provider(cls, ptype: str) -> Type:
        return cls._providers.get(ptype)

    @classmethod
    def get_all_protocols(cls) -> list:
        return list(cls._providers.keys())
