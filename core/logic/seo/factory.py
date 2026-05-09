#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SEO Processor Factory
职责：根据出版模式与 SEO 策略，实例化对应的处理器。
🚀 [V53.0] 出版模式矩阵的策略分发枢纽。
"""

from core.config.models.governance import (
    PublishingMode,
    SeoStrategy,
    validate_mode_strategy,
    get_default_strategy,
)
from .base import BaseSeoProcessor
from core.utils.tracing import tlog


class SeoProcessorFactory:
    """🚀 SEO 处理器工厂
    
    根据当前出版模式和 SEO 策略，创建并返回对应的处理器实例。
    如果模式-策略组合非法，自动回退至该模式的默认策略。
    """

    # 延迟导入映射表，避免循环依赖
    _REGISTRY = None

    @classmethod
    def _ensure_registry(cls):
        """延迟初始化策略注册表"""
        if cls._REGISTRY is not None:
            return
        
        from .heuristic import HeuristicSeoProcessor
        from .protocol import ProtocolSeoProcessor
        from .ai_alignment import AIAlignmentProcessor
        from .ai_authority import AIAuthorityProcessor
        from .ai_sync import AISyncProcessor
        from .ai_localized import AILocalizedProcessor

        cls._REGISTRY = {
            # 基础模式
            SeoStrategy.HEURISTIC: HeuristicSeoProcessor,
            SeoStrategy.PROTOCOL: ProtocolSeoProcessor,
            # 智能模式
            SeoStrategy.AI_ALIGNMENT: AIAlignmentProcessor,
            SeoStrategy.AI_AUTHORITY: AIAuthorityProcessor,
            # 全球模式
            SeoStrategy.AI_SYNC: AISyncProcessor,
            SeoStrategy.AI_LOCALIZED: AILocalizedProcessor,
        }


    @classmethod
    def create(cls, mode: PublishingMode, strategy: SeoStrategy) -> BaseSeoProcessor:
        """创建 SEO 处理器实例。
        
        Args:
            mode: 当前出版模式
            strategy: 用户选择的 SEO 策略
        
        Returns:
            BaseSeoProcessor: 对应的处理器实例
        
        Raises:
            ValueError: 如果策略尚未实装
        """
        cls._ensure_registry()

        # 校验组合合法性
        if not validate_mode_strategy(mode, strategy):
            default = get_default_strategy(mode)
            tlog.warning(
                f"⚠️ [SEO 工厂] 模式-策略组合非法: {mode.value}/{strategy.value}，"
                f"已回退至默认策略: {default.value}"
            )
            strategy = default

        processor_cls = cls._REGISTRY.get(strategy)
        
        if processor_cls is None:
            # 策略尚未实装，回退至 Heuristic
            tlog.warning(
                f"⚠️ [SEO 工厂] 策略 '{strategy.value}' 尚未实装，回退至 heuristic"
            )
            from .heuristic import HeuristicSeoProcessor
            processor_cls = HeuristicSeoProcessor

        tlog.info(f"🧬 [SEO 工厂] 已装载处理器: {processor_cls.__name__} (模式={mode.value})")
        return processor_cls()

    @classmethod
    def register(cls, strategy: SeoStrategy, processor_cls: type):
        """动态注册新的 SEO 处理器（供插件扩展使用）"""
        cls._ensure_registry()
        cls._REGISTRY[strategy] = processor_cls
        tlog.info(f"🧩 [SEO 工厂] 已注册扩展处理器: {strategy.value} -> {processor_cls.__name__}")
