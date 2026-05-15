#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Provider Universal Gateway
模块职责：基于注册机制的算力分发枢纽。
🚀 [V33 终极透明版]：实现 Zero-Touch 算力自发现。
"""

import logging
from typing import Any
from core.adapters.ai.registry import AIProviderRegistry
# 🚀 导入 ai 包将触发其 __init__.py 中的自发现逻辑

from core.utils.tracing import tlog

class TranslatorFactory:
    """🚀 算力工厂：负责根据配置实例化对应的 AI 转换器"""
    
    # 🧠 [V55.26] 提示词模版缓存矩阵：{imprint_id: {style_id: PromptTemplates}}
    _prompt_cache = {}

    @classmethod
    def get_prompts_for_style(cls, style_id: str, imprint_id: str, base_prompts: Any) -> Any:
        """🚀 [V55.26] 动态方言获取：优先从缓存读取，否则从物理磁盘加载"""
        # 🚀 [V55.26] 授权版主权检查
        from core.governance.license_guard import LicenseGuard
        if style_id != "default" and not LicenseGuard.is_licensed():
            tlog.warning(f"🛡️ [License Guard] 社区版尝试加载非默认方言 [{style_id}]，已强制降级。")
            return base_prompts
            
        cache_key = f"{imprint_id}:{style_id}"
        if cache_key in cls._prompt_cache:
            return cls._prompt_cache[cache_key]

        # 1. 准备空模板 (基于传入的 base_prompts 深度复制)
        from copy import deepcopy
        style_prompts = deepcopy(base_prompts)
        
        # 2. 物理寻址
        import os
        import yaml
        from core.config.config import IMPRINT_DIR, CONFIG_DIR, DIALECTS_DIR, PROMPTS_NAME
        
        style_file = f"{style_id}.yaml"
        prompt_path = os.path.join(IMPRINT_DIR, imprint_id, CONFIG_DIR, DIALECTS_DIR, style_file)
        
        if not os.path.exists(prompt_path):
            # 降级寻址：如果是 default 风格且不存在，尝试读取根目录母本
            if style_id == "default":
                prompt_path = os.path.join(os.getcwd(), CONFIG_DIR, PROMPTS_NAME)
            else:
                # 非 default 风格不存在，则直接返回基础模版（不缓存，防止污染）
                return style_prompts

        # 3. 执行物理加载
        try:
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    p_data = yaml.safe_load(f)
                    if p_data:
                        # 动态注入
                        if 'translation' in p_data:
                            style_prompts.translate_system = p_data['translation'].get('system', style_prompts.translate_system)
                            style_prompts.translate_user = p_data['translation'].get('user', style_prompts.translate_user)
                        if 'seo' in p_data:
                            style_prompts.seo_system = p_data['seo'].get('system', style_prompts.seo_system)
                            style_prompts.seo_user = p_data['seo'].get('user', style_prompts.seo_user)
                        if 'slug' in p_data:
                            style_prompts.slug_system = p_data['slug'].get('system', style_prompts.slug_system)
                            style_prompts.slug_user = p_data['slug'].get('user', style_prompts.slug_user)
                        if 'title' in p_data:
                            style_prompts.title_system = p_data['title'].get('system', getattr(style_prompts, 'title_system', ""))
                            style_prompts.title_user = p_data['title'].get('user', getattr(style_prompts, 'title_user', ""))
                        if 'metadata' in p_data:
                            style_prompts.metadata_system = p_data['metadata'].get('system', getattr(style_prompts, 'metadata_system', ""))
                            style_prompts.metadata_user = p_data['metadata'].get('user', getattr(style_prompts, 'metadata_user', ""))
            
            # 写入缓存
            cls._prompt_cache[cache_key] = style_prompts
            return style_prompts
        except Exception as e:
            tlog.warning(f"⚠️ [方言加载失败] {prompt_path}: {e}")
            return style_prompts

    @classmethod
    def _build_node(cls, node_name, trans_cfg, role='primary'):
        """🚀 [V66.5] 核心对正逻辑：物理底座与版图策略的动态合成"""
        
        # 1. 强制从新版“物理底座 (compute_nodes)”中提取物理参数
        physical_node = trans_cfg.compute_nodes.get(node_name)
        
        if not physical_node:
            raise ValueError(f"❌ [算力网关] 未能对正物理节点: {node_name}。请先在‘算力底座’中配置。")
            
        tlog.info(f"🛰️ [主权对正] 正在将版图策略注入物理底座: {node_name} (Role: {role})")
        # 动态决定模型（优先使用版图层指定的模型）
        target_model = getattr(trans_cfg, f"{role}_model", "gpt-4o")
        
        # 🚀 工业级 Mock：合成符合 BaseTranslator 预期的配置镜像
        from types import SimpleNamespace
        node_cfg = SimpleNamespace(
            type=physical_node.type,
            provider=physical_node.type,
            model=target_model,
            api_key=physical_node.api_key,
            base_url=physical_node.base_url,
            enabled=physical_node.enabled,
            limits=physical_node.limits,
            iter_id="v1"
        )

        ptype = node_cfg.type.lower()
        
        # 🚀 [V52.10] 语义容错：将通用的 openai-compatible 自动对正为标准 openai 协议
        if ptype == "openai-compatible":
            ptype = "openai"
            
        provider_cls = AIProviderRegistry.get_provider(ptype)

        if provider_cls:
            return provider_cls(node_name, trans_cfg)

        raise ValueError(f"❌ [算力网关] 不支持协议类型: {ptype}")

    @staticmethod
    def create(trans_cfg):
        # 🚀 [V48.3] 工业级指令重载：从外部 YAML 加载全量提示词指令矩阵
        try:
            import os
            import yaml
            from core.governance.imprint_manager import im
            
            imprint_id = im.get_active_imprint()
            active_style = getattr(trans_cfg, 'active_style', 'default')
            from core.config.config import PROMPTS_NAME, DIALECTS_DIR, CONFIG_DIR, IMPRINT_DIR
            
            if imprint_id and imprint_id != "default":
                # 🚀 [V55.25] 动态寻址：优先使用 active_style 对应的方言文件
                style_file = f"{active_style}.yaml"
                prompt_file = os.path.join(IMPRINT_DIR, imprint_id, CONFIG_DIR, DIALECTS_DIR, style_file)
                
                if not os.path.exists(prompt_file):
                    # 如果特定风格不存在，尝试降级到 default.yaml
                    from core.config.config import DEFAULT_DIALECT_NAME
                    prompt_file = os.path.join(IMPRINT_DIR, imprint_id, CONFIG_DIR, DIALECTS_DIR, DEFAULT_DIALECT_NAME)
                    
                if not os.path.exists(prompt_file):
                    # 最终降级：读取根目录母本
                    prompt_file = os.path.join(os.getcwd(), CONFIG_DIR, PROMPTS_NAME)
            else:
                prompt_file = os.path.join(os.getcwd(), CONFIG_DIR, PROMPTS_NAME)

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

            # 🛡️ [V48.3] 应用本地 custom_prompts 覆盖 (最高优先级)
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
                return TranslatorFactory._build_node(primary, trans_cfg, role='primary')

            if strategy == 'fallback' or strategy == 'concurrent':
                from core.adapters.ai.strategies import FallbackStrategy
                return FallbackStrategy(
                    TranslatorFactory._build_node(primary, trans_cfg, role='primary'),
                    TranslatorFactory._build_node(fallback, trans_cfg, role='fallback')
                )

            if strategy == 'smart_routing':
                from core.adapters.ai.strategies import SmartRoutingStrategy
                return SmartRoutingStrategy(
                    TranslatorFactory._build_node(primary, trans_cfg, role='primary'),
                    TranslatorFactory._build_node(fallback, trans_cfg, role='fallback'),
                    trans_cfg.routing_threshold
                )

            raise ValueError(f"❌ 不支持的分流策略: {strategy}")

        except Exception as e:
            tlog.warning(f"📡 [算力对正] 检测到版图配置缺失或冲突: {e}")
            tlog.info("  └── 🛡️ [主权自愈] 系统已自动挂载“模拟算力”镜像，确保出版管线物理连续。")
            
            # 🚀 [V74.8] 极致降级：通过注册表动态获取 Mock 协议，规避物理路径依赖
            try:
                from types import SimpleNamespace
                from core.adapters.ai.registry import AIProviderRegistry
                
                # 动态获取注册过的 mock 适配器类
                MockAIProvider = AIProviderRegistry.get_provider("mock")
                if not MockAIProvider:
                    # 最后的物理防线：如果注册表也没找到，直接报错抛出
                    raise RuntimeError("无法在注册表中定位 'mock' 协议，自愈管线断裂。")
                
                # 构造符合 BaseTranslator 预期的虚拟配置镜像
                mock_node_cfg = SimpleNamespace(
                    type="mock",
                    id="fallback_mock",
                    api_key="",
                    base_url="http://localhost:0",
                    enabled=True,
                    limits=SimpleNamespace(max_concurrency=1, timeout=10)
                )
                
                # 注入一个最小化的 trans_cfg 镜像
                mock_trans_cfg = SimpleNamespace(
                    compute_nodes={"fallback_mock": mock_node_cfg},
                    api_timeout=10,
                    max_retries=0,
                    _synced_providers={"fallback_mock": mock_node_cfg}
                )
                
                return MockAIProvider("fallback_mock", mock_trans_cfg)
            except Exception as inner_e:
                tlog.critical(f"🚨 [核心故障] 算力降级管线也已物理断裂: {inner_e}")
                raise e
