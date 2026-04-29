#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Engine Assembly Factory
模块职责：负责主引擎的所有核心组件装配、服务挂载与依赖注入。
🛡️ [AEL-Iter-v5.3]：彻底消灭上帝函数的架构分层枢纽。
"""
import os
import logging
from dataclasses import asdict
from core.config.config import load_config, ThemeSettings
from core.archives.ledger import MetadataManager
from core.archives.timeline import TimelineManager
from core.governance.sentinel import SentinelManager
from core.services.staticizer import StaticizerService
from core.logic.ai.ai_factory import TranslatorFactory
from core.runtime.engine import IllacmeEngine
from core.editorial.runner import Pipeline
from core.editorial.registry import StepRegistry
from core.editorial.asset_pipeline import AssetPipeline
from core.editorial.router import RouteManager
from core.ingress.adapter import InputAdapter
from core.adapters.egress.ssg import SSGAdapter
from core.logic.notification_hub import WebhookBroadcaster
from core.syndication.hub import ContentSyndicator
from core.bindery.bindery_dispatcher import BinderyDispatcher
from core.governance.auditor import SovereignAuditor
from core.governance.brain import KnowledgeService
from core.governance.janitor import JanitorService
from core.governance.doctor import DoctorService
from core.services.link_resolver import LinkResolver
from core.editorial.vault_indexer import VaultIndexer
from core.logic.block_parser import MarkdownBlockParser
from core.markup.manager import MarkupManager
from core.ingress.manager import IngressManager
from core.logic.ast_resolver import ASTResolver
from core.archives.block_cache import BlockCache
from core.governance.meter import UsageMeter
from core.syndication.publisher import PublisherService
from core.governance.contract_guard import ContractGuard
from core.governance.heartbeat import HeartbeatService
from core.governance.qa_guard import QAGuard
from core.logic.ai.ai_batcher import AIBatcher

from core.utils.event_bus import bus
from core.utils.tracing import tlog

class EngineFactory:
    # 🛡️ [V35.2] 主权物理布局协议 (唯一真理源)
    SOVEREIGN_LAYOUT = {
        "logs": "logs",
        "metadata": "metadata",
        "cache": "cache",
        "themes": "themes"
    }
    """🚀 [V35.2] 主权治理引擎工厂：负责全功能治理中枢的装配与依赖注入"""

    @staticmethod
    def create_engine(config, no_ai=False, args=None, territory_id: str = "default"):

        """🚀 [V35.2] 工业级引擎工厂：组装全功能主权治理中枢"""

        # 1. 🧬 [补救逻辑] 如果传入的是路径字符串，先加载为配置对象
        if isinstance(config, str):
            from core.config.config import load_config
            config = load_config(config)


        # 🚀 [V8.0] 激活物理安全底座
        from core.governance.secret_manager import secrets
        secrets.initialize()
        
        # 🛡️ [V35.2] 审计账本主权对正 (引用协议)
        from core.governance.audit_ledger import initialize_ledger
        audit_path = os.path.join("territories", territory_id, EngineFactory.SOVEREIGN_LAYOUT["metadata"], "audit.db") if territory_id != "default" else ".plenipes/ledger_audit.db"
        initialize_ledger(audit_path)

        
        # 🛡️ [V35.2] 主权路径强制对正：确保所有相对路径都锁定在疆域内部
        if territory_id and territory_id != "default":
            # 如果是具体疆域，强制将 data_root 指向疆域物理根部
            territory_path = os.path.join("territories", territory_id)
            if not config.system:
                config.system = type('SystemConfig', (), {'data_root': territory_path})()
            else:
                config.system.data_root = territory_path
            tlog.debug(f"🛰️ [主权对正] 引擎数据根部已强制锚定至: {territory_path}")


        # 2. 🚀 [审计逻辑] 此时 config 已经是对象，可以安全审计
        violations = ContractGuard.verify_config(config)
        if violations and any("❌" in v for v in violations):
            import sys
            sys.stderr.write("\n🚨 [CONTRACT VIOLATION] 引擎启动契约校验失败：\n")
            for v in violations:
                sys.stderr.write(f"  {v}\n")
            sys.stderr.flush()
            return None


        # 🚀 [V24.6] 视觉主权：Banner 抢占式渲染 (必须在所有初始化日志前)
        from core.ui.delegate import DisplayDelegate
        sys_version = DisplayDelegate.get_system_version(config)
        ael_iter_id = SentinelManager._detect_current_iter()
        
        # 🚀 [V24.6] 动态获取最新 Iter-ID
        # 🚀 [V24.6] 使用协议常量定位历史存档
        history_dir = os.path.join("territories", territory_id, EngineFactory.SOVEREIGN_LAYOUT["metadata"], "history") if territory_id != "default" else ".plenipes/history"

        current_iter_id = "V24.0_Default"
        if os.path.exists(history_dir):
            iters = [d for d in os.listdir(history_dir) if os.path.isdir(os.path.join(history_dir, d))]
            if iters:
                # 获取按名称排序或时间排序最新的迭代文件夹
                current_iter_id = sorted(iters)[-1]
        
        # 🛡️ [V24.6] 探测 Sentinel 状态 (双向监听)
        config_path = getattr(config, 'config_path', 'config.yaml')
        config_name = os.path.basename(config_path)
        base, ext = os.path.splitext(config_name)
        local_name = f"{base}.local{ext}"
        
        local_path = os.path.join(os.path.dirname(os.path.abspath(config_path)), local_name)
        sentinel_info = f"双向热监听 ({config_name} + {local_name})" if os.path.exists(local_path) else f"标准热监听 ({config_name})"
        
        bus.emit("UI_BANNER",
                 version=sys_version,
                 ael_iter_id=current_iter_id,
                 mode=DisplayDelegate.get_banner_mode(config, args),
                 sentinel_status=sentinel_info)

        # 🚀 [V16.0] 插件化基座点火
        plugin_settings = getattr(config, 'plugins', None)
        MarkupManager.initialize(plugin_settings)
        IngressManager.initialize(plugin_settings)

        # 3. 🔧 [挂载逻辑] 实例化并立即挂载核心属性
        engine = IllacmeEngine(config, no_ai=no_ai, config=config, territory_id=territory_id)

        engine.config = config
        engine.vault_root = os.path.abspath(os.path.expanduser(config.vault_root))
        engine.route_matrix = config.route_matrix
        engine.active_theme = config.active_theme

        if no_ai:
            engine.config.translation.enable_ai = False
            tlog.info("🚫 [AI 熔断] 检测到 --no-ai 标志，已强制关闭全局推理网关。")

        # 4. 🔗 分层组装
        EngineFactory._init_basic_settings(engine)
        EngineFactory._init_paths_and_adapters(engine)
        EngineFactory._init_semantic_and_governance(engine)
        EngineFactory._init_business_hubs(engine)
        EngineFactory._init_lifecycle_services(engine)
        EngineFactory._init_strategies_and_resilience(engine, args)
        
        return EngineFactory._finalize_assembly(engine, args)

    @staticmethod
    def _init_basic_settings(engine):
        """基础配置与 SSG 适配器映射"""
        engine.sys_cfg = engine.config.system
        engine.sys_tuning = {
            "ai_translation": {
                "temperature": engine.config.translation.temperature,
                "max_tokens": engine.config.translation.max_tokens
            }
        }
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
        
        # 🚀 [V24.6] 补全系统参数
        engine.max_depth = engine.config.system.max_depth
        engine.i18n = engine.config.i18n_settings
        engine.seo_cfg = engine.config.seo_settings
        engine.img_cfg = engine.config.image_settings
        engine.pub_cfg = engine.config.publish_control

    @staticmethod
    def _init_paths_and_adapters(engine):
        """🚀 [V35.0] 动态收稿渠道与物理路径矩阵"""
        from core.ingress.registry import ingress_registry
        paths_cfg = engine.config.output_paths
        ingress_cfg = engine.config.ingress_settings
        
        # 1. 动态实例化收稿渠道 (Source)
        source_type = ingress_cfg.source_type or "local"
        source_cls = ingress_registry.get_source(source_type)
        if not source_cls:
            tlog.error(f"🚨 [Ingress] 无法找到收稿渠道插件: {source_type}，回退至 local")
            from core.ingress.source.local import LocalFileSource
            source_cls = LocalFileSource
            
        # 根据不同渠道传入参数 (本地渠道需要 vault_root)
        if source_type == "local":
            engine.manuscript_source = source_cls(engine.vault_root)
        else:
            # 远程渠道使用 source_options
            engine.manuscript_source = source_cls(**ingress_cfg.source_options)

        # 2. 初始化方言适配器 (Dialect)
        engine.input_adapter = InputAdapter(
            active_dialects=ingress_cfg.active_dialects,
            custom_rules=ingress_cfg.custom_sanitizers,
            hard_line_break=ingress_cfg.hard_line_break
        )
        
        # 🚀 [V35.1] 主权路径锚定器：确保所有相对路径都锁定在 data_root 之下
        data_root = os.path.abspath(os.path.expanduser(engine.config.system.data_root))
        def anchor(p):
            if not p: return None
            p = os.path.expanduser(p)
            if not os.path.isabs(p):
                return os.path.join(data_root, p)
            return os.path.abspath(p)

        source_dir = paths_cfg.get('source_dir') or paths_cfg.get('markdown_dir')
        static_dir = paths_cfg.get('static_dir')
        
        engine.paths = {
            "vault": engine.vault_root,
            "source_dir": anchor(source_dir.replace("{theme}", engine.active_theme) if source_dir else ""),
            "static_dir": anchor(static_dir.replace("{theme}", engine.active_theme) if static_dir else ""),
            "assets": anchor(paths_cfg.get('assets_dir', '').replace("{theme}", engine.active_theme)),
            "graph_json_dir": anchor(paths_cfg.get('graph_json_dir', '').replace("{theme}", engine.active_theme)),
            "target_base": anchor((paths_cfg.get('target_base') or "").replace("{theme}", engine.active_theme)),
            "db": anchor(engine.config.metadata_db.format(theme=engine.active_theme) if "{theme}" in engine.config.metadata_db else engine.config.metadata_db.replace(".db", f"_{engine.active_theme}.db")),
            "cache": os.path.join(data_root, EngineFactory.SOVEREIGN_LAYOUT["cache"]),
            "logs": os.path.join(data_root, EngineFactory.SOVEREIGN_LAYOUT["logs"]),
            "metadata": os.path.join(data_root, EngineFactory.SOVEREIGN_LAYOUT["metadata"]),
            "themes": os.path.join(data_root, EngineFactory.SOVEREIGN_LAYOUT["themes"])
        }


        engine.asset_base_url = engine.config.image_settings.base_url.rstrip('/') + '/'


    @staticmethod
    def _init_semantic_and_governance(engine):
        """语义大脑与治理组件初始化"""
        from core.adapters.ai.embedding import EmbeddingFactory
        from core.governance.vector_index import VectorIndex
        from core.logic.knowledge.knowledge_graph import KnowledgeGraph
        from core.governance.health_registry import HealthRegistry
        from core.logic.smart_router import SmartRouter
        from core.governance.sentinel import SentinelManager
        from core.logic.knowledge.conversational_brain import ConversationalBrain

        data_paths = engine.config.system.data_paths
        v_raw = data_paths.get("vectors_json", "vectors_{theme}.json")
        v_path = os.path.join(engine.paths["metadata"], v_raw.format(theme=engine.active_theme) if "{theme}" in v_raw else v_raw.replace(".json", f"_{engine.active_theme}.json"))
        
        g_raw = data_paths.get("link_graph", "link_graph_{theme}.json")
        g_path = os.path.join(engine.paths["metadata"], g_raw.format(theme=engine.active_theme) if "{theme}" in g_raw else g_raw.replace(".json", f"_{engine.active_theme}.json"))
        
        p_raw = data_paths.get("pulse_json", "pulse_{theme}.json")
        engine.paths["pulse"] = os.path.join(engine.paths["metadata"], p_raw.format(theme=engine.active_theme) if "{theme}" in p_raw else p_raw.replace(".json", f"_{engine.active_theme}.json"))
        
        engine.embedding_adapter = EmbeddingFactory.create(engine)
        engine.vector_index = engine.governance.vector_index
        engine.knowledge_graph = KnowledgeGraph(g_path)
        engine.health_registry = HealthRegistry()
        engine.smart_router = SmartRouter(engine)
        engine.meta = MetadataManager(engine.paths["db"], engine.auto_save_interval, engine=engine)
        engine.timeline = TimelineManager(engine)
        engine.doctor = DoctorService(engine)
        engine.health_sentinel = engine.governance.health_sentinel
        engine.staticizer = StaticizerService()
        engine.conversational_brain = ConversationalBrain(engine)

    @staticmethod
    def _init_business_hubs(engine):
        """业务调度中枢 (Router, Translator, Dispatcher)"""
        # 🚀 [V10.5] 算力网关点火 (仅在启用 AI 时实例化重型模型)
        if not engine.no_ai:
            from core.logic.ai.ai_factory import TranslatorFactory
            engine.translator = TranslatorFactory.create(engine.config.translation)
        else:
            engine.translator = None
            tlog.info("🔌 [算力网关] AI 模式已关闭，跳过翻译官初始化。")

        engine.meter = engine.governance.meter
        engine.asset_pipeline = AssetPipeline(engine.paths['assets'], engine.config.image_settings)
        engine.route_manager = RouteManager(
            engine.meta, engine.translator,
            lang_mapping=engine.config.lang_mapping,
            default_lang=engine.config.i18n_settings.source.lang_code,
            active_theme=engine.active_theme,
            ssg_adapter=engine.ssg_adapter
        )
        engine.link_resolver = LinkResolver(engine.meta, engine.route_manager, engine.active_theme)
        # 🚀 [V35.0] 索引器适配：使用抽象 Source 适配器并注入主权配置
        engine.md_index, engine.asset_index, engine.link_graph = VaultIndexer.build_indexes(
            engine.manuscript_source, config=engine.config, ledger=engine.meta
        )

        engine.ast_resolver = ASTResolver(engine.md_index, engine.asset_index, source=engine.manuscript_source)

        from core.bindery.deployment_manager import DeploymentManager
        engine.deployment_manager = DeploymentManager(engine.config)

        engine.janitor = JanitorService(
            engine._global_engine_lock, engine._processing_locks,
            engine.paths, engine.meta, engine.route_manager, engine.config.i18n_settings,
            sys_cfg=engine.config.system, active_theme=engine.active_theme
        )
        
        engine.dispatcher = BinderyDispatcher(
            paths=engine.paths, meta=engine.meta, route_manager=engine.route_manager,
            asset_pipeline=engine.asset_pipeline, ssg_adapter=engine.ssg_adapter,
            ast_resolver=engine.ast_resolver,
            deployment_manager=engine.deployment_manager,
            pub_cfg=engine.config.publish_control, fm_order=engine.fm_order,
            asset_base_url=engine.asset_base_url, i18n_cfg=engine.config.i18n_settings, janitor=engine.janitor
        )



    @staticmethod
    def _init_lifecycle_services(engine):
        """生命周期服务 (Cache, Auditor, Guards)"""
        engine.block_cache = BlockCache(engine.paths['cache'])
        engine.auditor = SovereignAuditor(engine)
        engine.qa_guard = engine.governance.qa_guard
        engine.resource_guard = engine.governance.resource_guard
        engine.heartbeat = engine.governance.heartbeat
        engine.sentinel = engine.governance.health_sentinel # 🛡️ [V24.6] 映射主权健康哨兵
        engine.publisher = PublisherService(engine.config.model_dump(), sys_tuning=engine.config.system)
        engine.ai_batcher = AIBatcher(engine)
        engine.brain = KnowledgeService(engine)
        
        # 🚀 [V24.6] 启动总线绑定 (后台服务已在 GovernanceManager 中启动)
        engine.publisher.bind_to_bus(engine.bus)

    @staticmethod
    def _init_strategies_and_resilience(engine, args):
        """同步策略与熔断韧性"""
        from core.logic.strategies.fingerprint import FingerprintSyncStrategy
        from core.logic.strategies.sandbox import SandboxSyncStrategy
        from core.governance.circuit_breaker import CircuitBreaker
        from core.logic.orchestration.task_orchestrator import global_executor, ai_executor
        
        engine.sync_strategy = SandboxSyncStrategy(engine) if getattr(args, 'sandbox', False) else FingerprintSyncStrategy(engine)
        
        res = engine.config.system.resilience
        global_executor.update_concurrency(engine.config.system.concurrency.global_workers)
        ai_executor.update_concurrency(engine.config.system.concurrency.ai_workers)
        
        engine.circuit_breakers = {
            "ai": CircuitBreaker("AI-Gateway", failure_threshold=res.cb_failure_threshold, recovery_timeout=res.cb_recovery_timeout),
            "syndication": CircuitBreaker("Syndication-Hub", failure_threshold=3, recovery_timeout=120)
        }
        engine.pipeline = Pipeline.build(engine.config.system.pipeline_steps, StepRegistry)

    @staticmethod
    def _finalize_assembly(engine, args):
        """最终装配审计与 UI 挂载"""
        from core.governance.isolator import DependencyIsolator
        from core.ui.delegate import DisplayDelegate
        
        for adapter in [engine.input_adapter, engine.ssg_adapter]:
            if adapter: DependencyIsolator.check_adapter(adapter)
            
        from core.logic.hooks import ThemeHookManager
        engine.args = args  # 🚀 [V26.5] 显式挂载运行时参数
        engine.theme_hooks = ThemeHookManager(engine)

        engine.theme_hooks.trigger("init")
        return engine
