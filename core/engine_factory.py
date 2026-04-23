#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Engine Assembly Factory
模块职责：负责主引擎的所有核心组件装配、服务挂载与依赖注入。
🛡️ [AEL-Iter-v5.3]：彻底消灭上帝函数的架构分层枢纽。
"""
import os
import logging
import threading
from .config.config import load_config, Configuration, ThemeSettings
from .storage.ledger import MetadataManager
from .storage.timeline import TimelineManager
from .storage.sentinel import SentinelManager
from .services.staticizer import StaticizerService
from .adapters.ai_provider import TranslatorFactory
from .pipeline.runner import Pipeline
from .pipeline.registry import StepRegistry
from .asset_pipeline import AssetPipeline
from .router import RouteManager
from .adapters.ingress import InputAdapter
from .adapters.egress.ssg import SSGAdapter
from .adapters.ast_resolver import TransclusionResolver, MDXResolver
from .adapters.egress.webhook import WebhookBroadcaster
from .adapters.syndication.syndication import ContentSyndicator
from .egress_dispatcher import EgressDispatcher
from .services.janitor import JanitorService
from .vault_indexer import VaultIndexer

logger = logging.getLogger("Illacme.plenipes")

class EngineFactory:
    """🚀 [TDR-Iter-021] 引擎工厂：负责复杂的组件装配与初始化工作"""
    
    @staticmethod
    def assemble_components(engine, config_path, no_ai=False):
        """物理装配引擎的所有核心组件"""
        engine.no_ai = no_ai
        engine.config = load_config(config_path)
        
        # 1. 基础配置映射
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
        engine.max_depth = engine.config.system.max_depth
        
        log_level_str = engine.config.system.log_level.upper()
        logger.setLevel(getattr(logging, log_level_str, logging.INFO))
        
        engine.vault_root = os.path.abspath(os.path.expanduser(engine.config.vault_root))
        engine.route_matrix = engine.config.route_matrix
        engine.active_theme = engine.config.active_theme
        
        paths_cfg = engine.config.output_paths
        target_base_dir = paths_cfg.get('markdown_dir')
        target_assets_dir = paths_cfg.get('assets_dir')
        target_graph_dir = paths_cfg.get('graph_json_dir')
        
        theme_settings = engine.config.theme_options.get(engine.active_theme, ThemeSettings())
        engine.ssg_adapter = SSGAdapter(theme_settings, custom_adapters=engine.config.framework_adapters)
        
        # 2. 适配器与路径初始化
        ingress_cfg = engine.config.ingress_settings
        engine.input_adapter = InputAdapter(
            active_dialects=ingress_cfg.active_dialects, 
            custom_rules=ingress_cfg.custom_sanitizers,
            hard_line_break=ingress_cfg.hard_line_break
        )
        
        engine.paths = {
            "vault": engine.vault_root,
            "target_base": os.path.abspath(os.path.expanduser(target_base_dir)) if target_base_dir else None,
            "assets": os.path.abspath(os.path.expanduser(target_assets_dir)) if target_assets_dir else None,
            "graph_json_dir": os.path.abspath(os.path.expanduser(target_graph_dir)) if target_graph_dir else None,
            "db": os.path.abspath(os.path.expanduser(engine.config.metadata_db)),
            "shadow": os.path.join(engine.vault_root, '.illacme-shadow')
        }
        
        engine.i18n = engine.config.i18n_settings
        engine.seo_cfg = engine.config.seo_settings
        engine.img_cfg = engine.config.image_settings
        engine.pub_cfg = engine.config.publish_control
        engine.asset_base_url = engine.img_cfg.base_url.rstrip('/') + '/'
        
        # 3. 服务与索引挂载
        engine.meta = MetadataManager(engine.paths["db"], engine.auto_save_interval)
        engine.timeline = TimelineManager(engine.config)
        engine.sentinel = SentinelManager(engine.config)
        engine.staticizer = StaticizerService()
        engine.translator = TranslatorFactory.create(engine.config.translation)
        engine.asset_pipeline = AssetPipeline(engine.paths['assets'], engine.img_cfg)
        
        engine.route_manager = RouteManager(
            engine.meta, engine.translator, 
            lang_mapping=engine.config.lang_mapping,
            default_lang=engine.i18n.source.lang_code,
            active_theme=engine.active_theme
        )
        
        engine.md_index, engine.asset_index = VaultIndexer.build_indexes(engine.paths['vault'])
        engine.transclusion_resolver = TransclusionResolver(engine.md_index, engine.asset_index, engine.max_depth)
        engine.mdx_resolver = MDXResolver(engine.paths["vault"], engine.paths["target_base"])
        
        engine.janitor = JanitorService(
            engine._global_engine_lock, engine._processing_locks, 
            engine.paths, engine.meta, engine.route_manager, engine.i18n, 
            sys_cfg=engine.config.system, 
            active_theme=engine.active_theme
        )
        
        engine.broadcaster = WebhookBroadcaster(engine.pub_cfg, sys_tuning_cfg=engine.config.system)
        engine.syndicator = ContentSyndicator(engine.config.syndication, engine.config.site_url, sys_tuning_cfg=engine.config.system)
        
        engine.dispatcher = EgressDispatcher(
            paths=engine.paths, meta=engine.meta, route_manager=engine.route_manager,
            asset_pipeline=engine.asset_pipeline, ssg_adapter=engine.ssg_adapter,
            mdx_resolver=engine.mdx_resolver, syndicator=engine.syndicator,
            broadcaster=engine.broadcaster,
            pub_cfg=engine.pub_cfg, 
            fm_order=engine.fm_order,
            asset_base_url=engine.asset_base_url,
            i18n_cfg=engine.i18n,
            janitor=engine.janitor
        )
        
        # 🚀 [V33] 动态组装处理流水线
        # 未来可根据 config.pipeline_steps 动态过滤
        default_steps = [
            "read_normalize", "staticize", "purify", 
            "metadata_hash", "ai_slug_seo", "image_alt", "masking_routing"
        ]
        engine.pipeline = Pipeline.build(default_steps, StepRegistry)
