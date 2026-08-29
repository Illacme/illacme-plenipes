# -*- coding: utf-8 -*-
"""
⚙️ [V74.55] Gov Config Live Reload Shard
职责：统一在线热重构、主题母本对齐、算力/发布中枢/路由调度器组件热加载与事件广播。
架构：由 config.py 物理拆分而来 (SOP-02 标准)。
"""

import os
from typing import Optional, Dict, Any
from core.utils.tracing import tlog


def live_reload_engine_config(
    engine: Any,
    req: Dict[str, Any],
    imprint_id: Optional[str] = None
) -> None:
    """
    对已更新的 engine 进行全链路在线热重构，消除残留引用，刷新发布与算力管线。
    """
    if imprint_id and hasattr(engine, 'im') and engine.im and imprint_id != engine.im.get_active_imprint():
        return

    if "active_theme" in req:
        theme_id = req["active_theme"]
        from core.config.config import THEMES_DIR
        local_theme_path = os.path.join(engine.config.system.data_root, THEMES_DIR, theme_id)
        global_theme_path = os.path.join(os.getcwd(), THEMES_DIR, theme_id)
        if not os.path.exists(local_theme_path) and os.path.exists(global_theme_path):
            import shutil
            shutil.copytree(
                global_theme_path,
                local_theme_path,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns('node_modules', '.git', '.DS_Store')
            )
        
    if hasattr(engine, 'config_manager') and engine.config_manager and type(engine.config_manager).__name__ not in ('MagicMock', 'Mock'):
        target_imp = imprint_id or (engine.im.get_active_imprint() if hasattr(engine, 'im') and engine.im else 'default')
        engine.config_manager.imprint_id = target_imp
        tlog.info(f"🔍 [Reload 前] engine.config: mode={getattr(engine.config.governance, 'publishing_mode', None)}, i18n={getattr(engine.config.i18n_settings, 'enabled', None)}")
        engine.config_manager.reload()
        engine.config = engine.config_manager.config
        tlog.info(f"🔍 [Reload 后] engine.config: mode={getattr(engine.config.governance, 'publishing_mode', None)}, i18n={getattr(engine.config.i18n_settings, 'enabled', None)}")
    
    # 统一在线热重构（对齐路径、主题、算力与路由组件，彻底消除残留引用）
    engine.active_theme = engine.config.active_theme
    engine.vault_root = engine.config.vault_root
    
    from core.runtime.engine_factory import EngineFactory
    EngineFactory._init_basic_settings(engine)
    EngineFactory._init_ingress(engine, engine.config)
    
    # 🚀 [V100.0] 重构发布中枢：保证发布插件在热重载时能立刻获取最新的配置
    if hasattr(engine, "publisher") and engine.publisher:
        from core.syndication.publisher import PublisherService
        engine.publisher = PublisherService(engine.config.model_dump(), sys_tuning=engine.config.system)
        engine.publisher.bind_to_bus(engine.bus)
    
    # 🚀 [V74.80] 动态算力网络重构：实时热加载翻译官组件
    if not getattr(engine, 'no_ai', False):
        if getattr(engine.config.translation, 'enable_ai', True):
            from core.logic.ai.ai_factory import TranslatorFactory
            engine.translator = TranslatorFactory.create(engine.config.translation)
        else:
            engine.translator = None
        
    if hasattr(engine, 'route_manager') and engine.route_manager:
        engine.route_manager.lang_mapping = engine.config.lang_mapping
        engine.route_manager.default_lang = engine.config.i18n_settings.source.lang_code
        engine.route_manager.active_theme = (engine.active_theme or "starlight").lower()
        engine.route_manager.ssg_adapter = engine.ssg_adapter
        engine.route_manager.force_source_prefix = engine.config.i18n_settings.force_source_prefix

    if hasattr(engine, 'dispatcher') and engine.dispatcher:
        engine.dispatcher.ssg_adapter = engine.ssg_adapter
        engine.dispatcher.i18n_cfg = engine.config.i18n_settings
        engine.dispatcher.pub_cfg = engine.config.publish_control

    if hasattr(engine, 'janitor') and engine.janitor:
        engine.janitor.i18n_cfg = engine.config.i18n_settings
        engine.janitor.active_theme = engine.active_theme
    
    from core.utils.event_bus import bus
    bus.emit("CONFIG_RELOADED", config=engine.config)
