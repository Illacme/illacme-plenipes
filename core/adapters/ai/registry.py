#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Provider Registry
模块职责：管理所有 AI 算力协议的注册与发现。
🛡️ [AEL-Iter-v5.3]：全链路透明化的算力注册机。
"""

import logging
from typing import Dict, Type, List, Optional

from core.utils.tracing import tlog

class AIProviderRegistry:
    """🚀 AI 算力协议注册中心"""
    _protocols: Dict[str, Type] = {}

    @classmethod
    def register(cls, provider_class: Type):
        """
        🚀 [V53.8] 智能注册：支持插件 ID 与 别名矩阵。
        
        别名系统 (ALIASES) 的设计初衷：
        1. 物理兼容性：支持用户在 config.yaml 中使用不同的称呼习惯 (如 v1, openai, openai-compatible)。
        2. 降低迁移成本：兼容来自其他生态系统 (如 LocalAI, One-API) 的默认命名规范。
        3. 鲁棒性：防止因微小的配置名称差异导致驱动加载失败。
        """
        ptype = getattr(provider_class, "PLUGIN_ID", provider_class.__name__.lower())
        cls._protocols[ptype] = provider_class
        
        # 注册别名：建立多对一的映射关系，确保无论用户写哪一个 ID 都能命中同一物理驱动
        aliases = getattr(provider_class, "ALIASES", [])
        for alias in aliases:
            cls._protocols[alias] = provider_class
            
        tlog.debug(f"🤖 [算力插件] 已注册协议: {ptype} (别名: {', '.join(aliases)})")

    @classmethod
    def get_provider(cls, ptype: str) -> Optional[Type]:
        return cls._protocols.get(ptype)

    @classmethod
    def get_all_protocols(cls) -> List[str]:
        return list(cls._protocols.keys())

    @classmethod
    def list_active(cls) -> List[str]:
        return cls.get_all_protocols()
