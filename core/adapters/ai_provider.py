#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Provider Universal Gateway
模块职责：基于注册机制的算力分发枢纽。
🚀 [V33 终极透明版]：实现 Zero-Touch 算力自发现。
"""

import logging
from .ai.registry import AIProviderRegistry
# 🚀 导入 ai 包将触发其 __init__.py 中的自发现逻辑
from .ai import strategies 

logger = logging.getLogger("Illacme.plenipes")

class TranslatorFactory:
    """🚀 算力工厂：负责根据配置实例化对应的 AI 转换器"""
    
    @classmethod
    def _build_node(cls, node_name, trans_cfg):
        node_cfg = trans_cfg.providers.get(node_name)
        if not node_cfg:
            raise ValueError(f"❌ [算力网关] 未找到节点配置: {node_name}")
            
        ptype = node_cfg.type
        provider_cls = AIProviderRegistry.get_provider(ptype)
        
        if provider_cls:
            return provider_cls(node_name, trans_cfg)
            
        raise ValueError(f"❌ [算力网关] 不支持的协议类型: {ptype} (可用: {AIProviderRegistry.get_all_protocols()})")

    @staticmethod
    def create(trans_cfg):
        strategy = trans_cfg.strategy
        try:
            primary = trans_cfg.primary_node
            fallback = trans_cfg.fallback_node
            
            if strategy == 'single':
                return TranslatorFactory._build_node(primary, trans_cfg)
                
            if strategy == 'fallback':
                from .ai.strategies import FallbackStrategy
                return FallbackStrategy(
                    TranslatorFactory._build_node(primary, trans_cfg), 
                    TranslatorFactory._build_node(fallback, trans_cfg)
                )
                
            if strategy == 'smart_routing':
                from .ai.strategies import SmartRoutingStrategy
                return SmartRoutingStrategy(
                    TranslatorFactory._build_node(primary, trans_cfg), 
                    TranslatorFactory._build_node(fallback, trans_cfg), 
                    trans_cfg.routing_threshold
                )
                
            raise ValueError(f"❌ 不支持的分流策略: {strategy}")
            
        except Exception as e:
            logger.error(f"🛑 算力网关初始化失败: {e}")
            raise
