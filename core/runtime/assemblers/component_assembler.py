# -*- coding: utf-8 -*-
"""
⚙️ Illacme Runtime Assembler - Component Factory (组件组装工厂)
职责：负责引擎语义大脑、治理逻辑与业务中枢的物理装配。
🛡️ [V74.8]：解耦 EngineFactory 的重度实例化负担。
"""

from core.utils.tracing import tlog
from core.archives.ledger import MetadataManager
from core.archives.timeline import TimelineManager
from core.services.staticizer import StaticizerService
from core.editorial.asset_pipeline import AssetPipeline
from core.editorial.router import RouteManager
from core.ingress.adapter import InputAdapter
from core.bindery.bindery_dispatcher import BinderyDispatcher
from core.governance.doctor import DoctorService
from core.services.link_resolver import LinkResolver
from core.editorial.vault_indexer import VaultIndexer
from core.logic.ast_resolver import ASTResolver
from core.governance.janitor import JanitorService
from core.bindery.deployment_manager import DeploymentManager
from core.editorial.runner import Pipeline
from core.editorial.registry import StepRegistry
from core.governance.circuit_breaker import CircuitBreaker
from core.archives.block_cache import BlockCache
from core.adapters.ai.embedding import EmbeddingFactory

def assemble_core_components(engine, config):
    """
    组装引擎的语义、治理与业务核心组件。
    """
    # 1. 初始化语义与治理
    from core.logic.knowledge.knowledge_graph import KnowledgeGraph
    from core.governance.health_registry import HealthRegistry
    from core.logic.smart_router import SmartRouter
    from core.logic.knowledge.conversational_brain import ConversationalBrain

    g_path = engine._resolve_path(config.get_sync_stats_path().replace("sync_stats", "knowledge_graph"))
    engine.paths["pulse"] = engine._resolve_path(config.get_pulse_path())
    
    # 🚀 [V50.3] 注入系统配置快照 (修复 AttributeError)
    engine.max_depth = config.system.max_depth
    engine.i18n = config.i18n_settings
    engine.seo_cfg = config.seo_settings
    engine.img_cfg = config.image_settings
    engine.pub_cfg = config.publish_control

    from core.governance.meter import UsageMeter
    engine.meter = UsageMeter(engine)
    
    engine.knowledge_graph = KnowledgeGraph(g_path)
    engine.health_registry = HealthRegistry()
    engine.smart_router = SmartRouter(engine)
    engine.meta = MetadataManager(engine.paths["db"], engine.auto_save_interval, engine=engine)
    engine.timeline = TimelineManager(engine)
    engine.doctor = DoctorService(engine)
    engine.staticizer = StaticizerService()
    engine.conversational_brain = ConversationalBrain(engine)

    # 🚀 [V15.1] 初始化治理与缓存组件 (修复 AttributeError)
    engine.circuit_breakers = {"ai": CircuitBreaker("Global-AI")}
    engine.block_cache = BlockCache(
        engine.paths["metadata"],
        custom_cache_dir=getattr(config, 'block_cache_dir', None),
        shard_levels=getattr(config, 'block_cache_shard_levels', 0)
    )
    
    if not engine.no_ai:
        engine.embedding_adapter = EmbeddingFactory.create(engine)
    else:
        engine.embedding_adapter = None

    # 2. 业务中枢组装
    if not engine.no_ai:
        from core.logic.ai.ai_factory import TranslatorFactory
        engine.translator = TranslatorFactory.create(config.translation)
    else:
        engine.translator = None
        tlog.info("🔌 [算力网关] AI 模式已关闭，跳过翻译官初始化。")

    engine.asset_pipeline = AssetPipeline(engine.paths.get('assets', ''), config.image_settings)
    
    # 🚀 [V11.0] 初始化文档出版流水线
    engine.pipeline = Pipeline.build(config.system.pipeline_steps, StepRegistry)
    engine.route_manager = RouteManager(
        engine.meta, engine.translator,
        lang_mapping=config.lang_mapping,
        default_lang=config.i18n_settings.source.lang_code,
        active_theme=engine.active_theme,
        ssg_adapter=engine.ssg_adapter,
        force_source_prefix=config.i18n_settings.force_source_prefix
    )
    engine.link_resolver = LinkResolver(engine.meta, engine.route_manager, engine.active_theme)
    engine.md_index, engine.asset_index, engine.link_graph = VaultIndexer.build_indexes(
        engine.manuscript_source, config=config, ledger=engine.meta
    )

    engine.ast_resolver = ASTResolver(engine.md_index, engine.asset_index, source=engine.manuscript_source)
    engine.deployment_manager = DeploymentManager(config)

    engine.janitor = JanitorService(
        engine._global_engine_lock, engine._processing_locks,
        engine.paths, engine.meta, engine.route_manager, config.i18n_settings,
        sys_cfg=config.system, active_theme=engine.active_theme
    )
    
    engine.dispatcher = BinderyDispatcher(
        paths=engine.paths, meta=engine.meta, route_manager=engine.route_manager,
        asset_pipeline=engine.asset_pipeline, ssg_adapter=engine.ssg_adapter,
        ast_resolver=engine.ast_resolver,
        deployment_manager=engine.deployment_manager,
        pub_cfg=config.publish_control, fm_order=engine.fm_order,
        asset_base_url=engine.asset_base_url, i18n_cfg=config.i18n_settings, janitor=engine.janitor
    )
