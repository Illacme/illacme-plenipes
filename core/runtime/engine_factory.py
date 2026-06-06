# -*- coding: utf-8 -*-
"""
⚙️ Illacme-plenipes Core - Engine Assembly Factory
模块职责：作为主引擎的流水线枢纽，负责调用各分片装配器。
🛡️ [V74.8 Decoupled]：逻辑分片架构，装配逻辑已委托至 .assemblers 与 .infrastructure。
"""

import os
import time
import logging
from typing import Any, Optional

from core.config.config import ThemeSettings, THEMES_DIR
from core.runtime.engine import IllacmeEngine
from core.adapters.egress.ssg import SSGAdapter
from core.utils.tracing import tlog
from core.runtime.engine_preflight import EnginePreflight

# 🚀 导入分片后的基础设施与组装器
from .infrastructure.path_resolver import resolve_engine_paths
from .assemblers.component_assembler import assemble_core_components

class EngineFactory:
    """🚀 [V74.8] 主权治理引擎工厂：流水线式组装枢纽"""

    @staticmethod
    def create_engine(config: Any, no_ai: bool = False, args: Any = None, imprint_id: str = "default") -> Optional[IllacmeEngine]:
        """🚀 [V50.3] 工业级引擎工厂：组装全功能主权治理中枢"""

        # 1. 执行起飞前预检 (环境审计、路径锚定等)
        config = EnginePreflight.perform_preflight(config, imprint_id, args)
        if config is None:
            return None

        # 2. 实例化引擎主体
        engine = IllacmeEngine(config, no_ai=no_ai, config=config, imprint_id=imprint_id)
        engine.config = config
        engine.vault_root = os.path.abspath(os.path.expanduser(config.vault_root)) if config.vault_root else ""
        engine.route_matrix = config.route_matrix
        engine.active_theme = config.active_theme

        if no_ai:
            engine.config.translation.enable_ai = False
            tlog.info("🚫 [AI 熔断] 检测到 --no-ai 标志，已强制关闭全局推理网关。")

        # 3. 🔗 流水线装配
        EngineFactory._init_basic_settings(engine)
        
        # 委托路径解析
        engine.paths = resolve_engine_paths(engine, config, THEMES_DIR)
        engine.asset_base_url = config.image_settings.base_url.rstrip('/') + '/'
        
        # 委托收稿渠道初始化
        EngineFactory._init_ingress(engine, config)
        
        # 委托核心组件装配 (语义、治理、业务)
        assemble_core_components(engine, config)
        
        # 生命周期服务与策略
        EngineFactory._init_lifecycle_and_strategies(engine, config, args)
        
        return EngineFactory._finalize_assembly(engine, args)

    @staticmethod
    def _init_basic_settings(engine: IllacmeEngine) -> None:
        """基础参数同步"""
        engine.sys_cfg = engine.config.system
        engine.fm_defaults = engine.config.frontmatter_defaults
        engine.fm_order = engine.config.frontmatter_order or ['title', 'description', 'keywords', 'author', 'date', 'tags', 'categories']
        engine.max_workers = engine.config.system.max_workers
        engine.auto_save_interval = engine.config.system.auto_save_interval
        
        log_level_str = engine.config.system.log_level.upper()
        tlog.setLevel(getattr(logging, log_level_str, logging.INFO))

        theme_settings = engine.config.theme_options.get(engine.active_theme, ThemeSettings())
        theme_settings.name = engine.active_theme
        engine.ssg_adapter = SSGAdapter(theme_settings, custom_adapters=engine.config.framework_adapters, engine=engine)
        engine.ssg_adapter.default_lang = engine.config.i18n_settings.source.lang_code or "zh"

    @staticmethod
    def _init_ingress(engine: IllacmeEngine, config: Any) -> None:
        """收稿渠道与输入适配器装配"""
        from core.ingress.registry import ingress_registry
        from core.ingress.adapter import InputAdapter
        
        ingress_cfg = config.ingress_settings
        source_type = ingress_cfg.source_type or "local"
        source_cls = ingress_registry.get_source(source_type)
        
        if not source_cls:
            from core.ingress.source.local import LocalFileSource
            source_cls = LocalFileSource
            
        if source_type == "local":
            engine.manuscript_source = source_cls(engine.vault_root)
        else:
            engine.manuscript_source = source_cls(**ingress_cfg.source_options)

        engine.input_adapter = InputAdapter(
            active_dialects=ingress_cfg.active_dialects,
            custom_rules=ingress_cfg.custom_sanitizers,
            hard_line_break=ingress_cfg.hard_line_break
        )

    @staticmethod
    def _init_lifecycle_and_strategies(engine: IllacmeEngine, config: Any, args: Any) -> None:
        """生命周期与弹性策略组装"""
        from core.governance.heartbeat import HeartbeatService
        from core.syndication.publisher import PublisherService
        from core.logic.ai.ai_batcher import AIBatcher
        from core.governance.brain import KnowledgeService
        from core.logic.strategies.sandbox import SandboxSyncStrategy
        from core.logic.strategies.fingerprint import FingerprintSyncStrategy
        
        # 🚀 [V15.1] 挂载治理组件别名 (满足同步策略调用需求)
        engine.heartbeat = engine.governance.heartbeat
        engine.qa_guard = engine.governance.qa_guard
        engine.vector_index = engine.governance.vector_index
        engine.sentinel = engine.governance.health_sentinel
        
        engine.publisher = PublisherService(config.model_dump(), sys_tuning=config.system)
        engine.ai_batcher = AIBatcher(engine)
        engine.brain = KnowledgeService(engine)
        engine.publisher.bind_to_bus(engine.bus)
        
        engine.sync_strategy = SandboxSyncStrategy(engine) if getattr(args, 'sandbox', False) else FingerprintSyncStrategy(engine)

    @staticmethod
    def _finalize_assembly(engine: IllacmeEngine, args: Any) -> IllacmeEngine:
        """最终审计与 UI 挂载"""
        from core.governance.isolator import DependencyIsolator
        from core.logic.hooks import ThemeHookManager
        
        for adapter in [engine.input_adapter, engine.ssg_adapter]:
            if adapter: DependencyIsolator.check_adapter(adapter)
            
        # 🚀 [SSG 物理对齐] 在引擎组装的最终阶段，必须强制物理热编译一次主题选项，确保桥接常数和视觉 CSS 安全对齐！
        if hasattr(engine, 'ssg_adapter') and engine.ssg_adapter:
            try:
                engine.ssg_adapter.compile_theme_options()
            except Exception as e:
                tlog.warning(f"⚠️ [EngineFactory] 初始化热编译主题选项失败: {e}")
            
        engine.args = args
        engine.theme_hooks = ThemeHookManager(engine)
        engine.theme_hooks.trigger("init")
        return engine
