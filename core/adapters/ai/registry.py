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
    def register(cls, provider_class: Type):
        """🚀 [V53.8] 智能注册：支持插件 ID 与 别名矩阵"""
        ptype = getattr(provider_class, "PLUGIN_ID", provider_class.__name__.lower())
        cls._providers[ptype] = provider_class
        
        # 注册别名 (例如 openai-compatible -> openai)
        aliases = getattr(provider_class, "ALIASES", [])
        for alias in aliases:
            cls._providers[alias] = provider_class
            
        tlog.debug(f"🤖 [算力插件] 已注册协议: {ptype} (别名: {', '.join(aliases)})")

    @classmethod
    def get_provider(cls, ptype: str) -> Type:
        return cls._providers.get(ptype)

    @classmethod
    def get_all_protocols(cls) -> list:
        return list(cls._providers.keys())
