#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Markup Plugin Registry
职责：负责内容处理插件的动态注册与发现。
"""
from typing import Dict, List, Type
from .base import ISyntaxBlockPlugin, IContentTransformer, ISecurityMasker

class MarkupRegistry:
    """🚀 [V16.0] 插件注册中心：支持热插拔的解析管线"""
    
    def __init__(self):
        self._block_plugins: List[ISyntaxBlockPlugin] = []
        self._transformers: List[IContentTransformer] = []
        self._maskers: Dict[str, ISecurityMasker] = {}

    def register_block(self, plugin: ISyntaxBlockPlugin):
        """注册语法块识别插件"""
        self._block_plugins.append(plugin)
        # 按照优先级排序 (如果有优先级字段的话)
        
    def register_transformer(self, transformer: IContentTransformer):
        """注册内容转换插件"""
        self._transformers.append(transformer)

    def register_masker(self, name: str, masker: ISecurityMasker):
        """注册安全屏蔽插件"""
        self._maskers[name] = masker

    def get_blocks(self) -> List[ISyntaxBlockPlugin]:
        return self._block_plugins

    def get_transformers(self) -> List[IContentTransformer]:
        return self._transformers

    def get_masker(self, name: str) -> ISecurityMasker:
        return self._maskers.get(name)

# 全局单例注册表
markup_registry = MarkupRegistry()
