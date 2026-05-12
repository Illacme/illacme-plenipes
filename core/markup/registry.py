#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Markup Plugin Registry
职责：负责内容处理插件的动态注册与发现。
"""
import os
import sys
from typing import Dict, List, Type
from .base import ISyntaxBlockPlugin, IContentTransformer, ISecurityMasker
from core.utils.plugin_loader import discover_and_register

class MarkupRegistry:
    """🚀 [V24.0] 插件注册中心：支持热插拔的解析管线 (Zero-Touch 版)"""
    
    def __init__(self):
        self._block_plugins: List[ISyntaxBlockPlugin] = []
        self._transformers: List[IContentTransformer] = []
        self._maskers: Dict[str, ISecurityMasker] = {}

    def register_block(self, plugin: ISyntaxBlockPlugin):
        """注册语法块识别插件"""
        plugin_type = type(plugin)
        if not any(isinstance(p, plugin_type) for p in self._block_plugins):
            self._block_plugins.append(plugin)
        
    def register_transformer(self, transformer: IContentTransformer):
        """注册内容转换插件"""
        transformer_type = type(transformer)
        if not any(isinstance(t, transformer_type) for t in self._transformers):
            self._transformers.append(transformer)

    def register_masker(self, name: str, masker: ISecurityMasker):
        """注册安全屏蔽插件"""
        self._maskers[name] = masker

    def discover_all(self):
        """🚀 [Zero-Touch] 全域发现并挂载标记处理插件"""
        # 1. 扫描 Blocks
        block_path = os.path.abspath("adapters/markup/blocks")
        if os.path.exists(block_path):
            discover_and_register([block_path], "adapters.markup.blocks", ISyntaxBlockPlugin, lambda cls: self.register_block(cls()))

        # 2. 扫描 Transformers
        trans_path = os.path.abspath("adapters/markup/transformers")
        if os.path.exists(trans_path):
            discover_and_register([trans_path], "adapters.markup.transformers", IContentTransformer, lambda cls: self.register_transformer(cls()))

        # 3. 扫描 Maskers
        masker_path = os.path.abspath("adapters/markup/maskers")
        if os.path.exists(masker_path):
            discover_and_register([masker_path], "adapters.markup.maskers", ISecurityMasker, lambda cls: self.register_masker(getattr(cls, "PLUGIN_ID", cls.__name__.lower()), cls()))

    def get_blocks(self) -> List[ISyntaxBlockPlugin]:
        return self._block_plugins

    def get_transformers(self) -> List[IContentTransformer]:
        return self._transformers

    def get_masker(self, name: str) -> ISecurityMasker:
        return self._maskers.get(name)

# 全局单例注册表
markup_registry = MarkupRegistry()
