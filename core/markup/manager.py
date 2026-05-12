#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Markup Manager
职责：负责内容处理层的初始化、插件自动载入与解析调度。
"""
from .registry import markup_registry

class MarkupManager:
    """🚀 [V24.0] 内容处理层总控中心 (Zero-Touch 版)"""
    
    @staticmethod
    def initialize(settings=None):
        """
        [Bootstrap] 根据配置初始化并注册插件
        """
        # 1. 🚀 [Zero-Touch] 触发全域发现
        markup_registry.discover_all()
        
        if not settings:
            return

        # 0. [V53.1] 双重主权过滤：汇总本地禁用与品牌禁用清单
        disabled_all = set(getattr(settings, 'disabled_plugins', [])) | \
                       set(getattr(settings, 'imprint_disabled_plugins', []))
        
        def is_active(name):
            return name not in disabled_all

        # 2. [V75.0] 根据配置过滤已加载的插件
        # 注意：在 Zero-Touch 架构下，插件已物理加载，此处仅做逻辑开关过滤
        if hasattr(settings, 'security_maskers'):
            for name in settings.security_maskers:
                if not is_active(name):
                    from core.utils.tracing import tlog
                    tlog.info(f"🚫 [插件治理] 安全插件 '{name}' 已被主权层禁用。")
                    if name in markup_registry._maskers:
                        del markup_registry._maskers[name]

    @staticmethod
    def get_processor(processor_type: str = "markdown"):
        from core.logic.block_parser import MarkdownBlockParser
        return MarkdownBlockParser()

# 初始化全局标记语言环境 (默认加载)
MarkupManager.initialize()
