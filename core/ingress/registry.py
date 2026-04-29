#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ingress Registry
职责：负责语法方言 (Dialect) 与数据源 (Source) 的插件注册。
"""
from typing import Dict, Type, List, Optional
from .base import BaseDialect, BaseSource

class IngressRegistry:
    """🚀 [V16.0] 输入层注册中心"""
    
    _dialects: Dict[str, Type[BaseDialect]] = {}
    _sources: Dict[str, Type[BaseSource]] = {}

    @classmethod
    def register_dialect(cls, name: str, dialect_class: Type[BaseDialect]):
        """注册语法方言插件"""
        cls._dialects[name.lower()] = dialect_class

    @classmethod
    def get_dialect(cls, name: str) -> Optional[Type[BaseDialect]]:
        """获取方言处理器类"""
        return cls._dialects.get(name.lower())

    @classmethod
    def list_dialects(cls) -> List[str]:
        """列出所有已注册方言"""
        return list(cls._dialects.keys())

    @classmethod
    def register_source(cls, name: str, source_class: Type[BaseSource]):
        """🚀 [V25.0] 注册物理数据源插件 (收稿渠道)"""
        cls._sources[name.lower()] = source_class

    @classmethod
    def get_source(cls, name: str) -> Optional[Type[BaseSource]]:
        """获取物理数据源类"""
        return cls._sources.get(name.lower())

    @classmethod
    def list_sources(cls) -> List[str]:
        """列出所有已注册数据源"""
        return list(cls._sources.keys())

# 全局单例注册表
ingress_registry = IngressRegistry()

