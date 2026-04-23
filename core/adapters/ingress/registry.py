#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ingress Registry
模块职责：管理所有输入端方言解析器的注册与发现。
🛡️ [AEL-Iter-v5.3]：全链路透明化的方言注册机。
"""

import logging
from typing import Dict, Type
from .base import BaseDialect

logger = logging.getLogger("Illacme.plenipes")

class IngressRegistry:
    """🚀 Ingress 方言注册中心"""
    _dialects: Dict[str, Type[BaseDialect]] = {}

    @classmethod
    def register(cls, name: str, dialect_class: Type[BaseDialect]):
        cls._dialects[name] = dialect_class
        logger.debug(f"📜 [方言插件] 已注册解析器: {name}")

    @classmethod
    def get_dialect(cls, name: str) -> Type[BaseDialect]:
        return cls._dialects.get(name)

    @classmethod
    def get_all_names(cls) -> list:
        return list(cls._dialects.keys())
