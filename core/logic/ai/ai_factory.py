#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Provider Universal Gateway
模块职责：基于注册机制的算力分发枢纽。
🚀 [V33 终极透明版]：实现 Zero-Touch 算力自发现。
"""

import logging
from core.adapters.ai.registry import AIProviderRegistry
# 🚀 导入 ai 包将触发其 __init__.py 中的自发现逻辑

from core.utils.tracing import tlog

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
        # 🚀 [V24.6] 工业级指令重载：从外部 YAML 加载全量提示词指令矩阵
        try:
            import os
            import yaml
            prompt_file = os.path.join(os.getcwd(), "configs/prompts.yaml")
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    p_data = yaml.safe_load(f)
                    if p_data:
                        tlog.info(f"🧠 [指令矩阵激活] 已从 {prompt_file} 加载全量提示词策略")
                        # 动态同步至配置模型
                        if 'translation' in p_data:
                            trans_cfg.prompts.translate_system = p_data['translation'].get('system', trans_cfg.prompts.translate_system)
                            trans_cfg.prompts.translate_user = p_data['translation'].get('user', trans_cfg.prompts.translate_user)
                        if 'seo' in p_data:
                            trans_cfg.prompts.seo_system = p_data['seo'].get('system', trans_cfg.prompts.seo_system)
                            trans_cfg.prompts.seo_user = p_data['seo'].get('user', trans_cfg.prompts.seo_user)
                        if 'slug' in p_data:
                            trans_cfg.prompts.slug_system = p_data['slug'].get('system', trans_cfg.prompts.slug_system)
                            trans_cfg.prompts.slug_user = p_data['slug'].get('user', trans_cfg.prompts.slug_user)
                        if 'title' in p_data:
                            # 动态注入标题润色策略 (如果模型支持)
                            trans_cfg.prompts.title_system = p_data['title'].get('system', getattr(trans_cfg.prompts, 'title_system', ""))
                            trans_cfg.prompts.title_user = p_data['title'].get('user', getattr(trans_cfg.prompts, 'title_user', ""))
                        if 'metadata' in p_data:
                            # 动态注入全量元数据翻译策略
                            trans_cfg.prompts.metadata_system = p_data['metadata'].get('system', getattr(trans_cfg.prompts, 'metadata_system', ""))
                            trans_cfg.prompts.metadata_user = p_data['metadata'].get('user', getattr(trans_cfg.prompts, 'metadata_user', ""))

            # 🛡️ [V24.6] 应用本地 custom_prompts 覆盖 (最高优先级)
            if hasattr(trans_cfg, 'custom_prompts') and trans_cfg.custom_prompts:
                for k, v in trans_cfg.custom_prompts.items():
                    if hasattr(trans_cfg.prompts, k):
                        setattr(trans_cfg.prompts, k, v)
                        tlog.debug(f"⚙️ [指令覆盖] 应用本地自定义策略: {k}")

        except Exception as e:
            tlog.warning(f"⚠️ [指令矩阵加载失败]: {e}，将回退至硬编码默认值")

        strategy = trans_cfg.strategy
        try:
            primary = trans_cfg.primary_node
            fallback = trans_cfg.fallback_node

            if strategy == 'single':
                return TranslatorFactory._build_node(primary, trans_cfg)

            if strategy == 'fallback':
                from core.adapters.ai.strategies import FallbackStrategy
                return FallbackStrategy(
                    TranslatorFactory._build_node(primary, trans_cfg),
                    TranslatorFactory._build_node(fallback, trans_cfg)
                )

            if strategy == 'smart_routing':
                from core.adapters.ai.strategies import SmartRoutingStrategy
                return SmartRoutingStrategy(
                    TranslatorFactory._build_node(primary, trans_cfg),
                    TranslatorFactory._build_node(fallback, trans_cfg),
                    trans_cfg.routing_threshold
                )

            raise ValueError(f"❌ 不支持的分流策略: {strategy}")

        except Exception as e:
            tlog.error(f"🛑 算力网关初始化失败: {e}")
            raise
