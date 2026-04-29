#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Markup Manager
职责：负责内容处理层的初始化、插件自动载入与解析调度。
"""
from .registry import markup_registry
from .processors.markdown.blocks.standard import HeaderBlockPlugin, CodeBlockPlugin
from .processors.markdown.blocks.obsidian import CalloutBlockPlugin
from .processors.markdown.maskers.mdx import MDXMasker
from .processors.markdown.links.obsidian import ObsidianTransclusionTransformer
from .processors.markdown.links.mdx import MDXTransformer

class MarkupManager:
    """🚀 [V16.0] 内容处理层总控中心"""
    
    _TRANSFORMER_MAP = {
        "obsidian_transclusion": ObsidianTransclusionTransformer,
        "mdx_transformer": MDXTransformer
    }
    
    _MASKER_MAP = {
        "mdx": MDXMasker
    }

    @staticmethod
    def initialize(settings=None):
        """
        [Bootstrap] 根据配置初始化并注册插件
        """
        # 1. 注册基础语法块 (始终加载)
        markup_registry.register_block(HeaderBlockPlugin())
        markup_registry.register_block(CodeBlockPlugin())
        markup_registry.register_block(CalloutBlockPlugin())
        
        if not settings:
            # 无配置时的默认回退
            markup_registry.register_masker("mdx", MDXMasker())
            markup_registry.register_transformer(ObsidianTransclusionTransformer())
            markup_registry.register_transformer(MDXTransformer())
            return

        # 2. 动态注册安全屏蔽插件
        for name in settings.security_maskers:
            masker_cls = MarkupManager._MASKER_MAP.get(name)
            if masker_cls:
                markup_registry.register_masker(name, masker_cls())

        # 3. 动态注册内容转换插件
        for name in settings.markup_transformers:
            transformer_cls = MarkupManager._TRANSFORMER_MAP.get(name)
            if transformer_cls:
                markup_registry.register_transformer(transformer_cls())

    @staticmethod
    def get_processor(processor_type: str = "markdown"):
        from core.logic.block_parser import MarkdownBlockParser
        return MarkdownBlockParser()

# 初始化全局标记语言环境 (默认加载)
MarkupManager.initialize()
