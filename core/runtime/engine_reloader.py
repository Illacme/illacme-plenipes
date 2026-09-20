#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Engine Reloader
模块职责：同步引擎运行时配置热重载与参数对齐分片。
"""

import os
from core.utils.tracing import tlog


def reload_engine_config(engine, config=None, **kwargs):
    """⚡ [V55.12] 深度主权对齐：响应配置变更，同步全量运行时参数"""
    tlog.info("⚡ [Engine] 接收到配置变更信号，正在执行全量参数对齐...")
    
    if config is None:
        try:
            from core.config.config import load_config
            config = load_config()
        except Exception as cfg_err:
            tlog.error(f"❌ [Engine] 加载物理配置失败: {cfg_err}")
            config = None
    if not config:
        tlog.error("❌ [Engine] 热重载配置失败，新的配置为空！物理拒绝覆盖当前有效配置。")
        return
    was_onboarding = engine.onboarding_required
    
    # 🛡️ [SOP-13 物理隔离防护] 锁定品牌领地，防止重载时 data_root 退化回根目录
    imprint_id = getattr(engine, 'imprint_id', 'default') or 'default'
    imprint_path = os.path.join("imprints", imprint_id) if imprint_id != "root" else "."
    if hasattr(config, 'system') and config.system:
        config.system.data_root = imprint_path
        
    engine.config = config
    engine.active_theme = config.active_theme
    engine.vault_root = os.path.abspath(os.path.expanduser(config.vault_root)) if config.vault_root else ""
    
    # 同步更新收稿渠道的数据源路径，确保热重载生效
    if hasattr(engine, 'manuscript_source') and hasattr(engine.manuscript_source, 'root_path'):
        engine.manuscript_source.root_path = engine.vault_root
        
    engine.route_matrix = config.route_matrix
    engine.fm_defaults = config.frontmatter_defaults
    engine.fm_order = config.frontmatter_order
    engine.max_workers = config.system.max_workers
    engine.auto_save_interval = config.system.auto_save_interval
    engine.max_depth = config.system.max_depth
    
    # 3. 🛡️ 治理配置实时热挂载
    engine.i18n = config.i18n_settings
    engine.seo_cfg = config.seo_settings
    engine.img_cfg = config.image_settings
    engine.pub_cfg = config.publish_control
    
    # 3b. 📂 重新装配全渠道发布编排器 (Reassemble DeploymentManager)
    if hasattr(engine, 'deployment_manager'):
        from core.bindery.deployment_manager import DeploymentManager
        try:
            engine.deployment_manager = DeploymentManager(config)
        except Exception as e:
            tlog.error(f"❌ [Engine] 重新装配发布编排器失败: {e}")
    
    # 3c. 🪝 重新装配主题钩子管理器，对齐当前 active_theme
    from core.logic.hooks import ThemeHookManager
    engine.theme_hooks = ThemeHookManager(engine)

    # 4. 🗺️ 物理路径矩阵重新锚定
    # 如果 active_theme 发生变更，必须重新计算 engine.paths 以防 IO 错误
    if hasattr(engine, 'paths'):
        from core.runtime.infrastructure.path_resolver import resolve_engine_paths
        from core.config.config import THEMES_DIR
        engine.paths = resolve_engine_paths(engine, engine.config, THEMES_DIR)

    # 4b. 🎨 重新装配 SSG 渲染适配器与分发器，对齐当前 active_theme
    from core.adapters.egress.ssg import SSGAdapter
    from core.config.models.theme import ThemeSettings
    theme_settings = engine.config.theme_options.get(engine.active_theme, ThemeSettings())
    theme_settings.name = engine.active_theme
    engine.ssg_adapter = SSGAdapter(theme_settings, custom_adapters=engine.config.framework_adapters, engine=engine)
    engine.ssg_adapter.default_lang = engine.config.i18n_settings.source.lang_code or "zh"

    if hasattr(engine, 'dispatcher') and engine.dispatcher:
        engine.dispatcher.ssg_adapter = engine.ssg_adapter
        engine.dispatcher.paths = engine.paths

    # 5. 🧠 算力池与业务中枢重校
    from core.logic.orchestration.task_orchestrator import global_executor, ai_executor
    global_executor.update_concurrency(config.system.concurrency.global_workers)
    ai_executor.update_concurrency(config.system.concurrency.ai_workers)

    from core.logic.ai.ai_factory import TranslatorFactory
    enable_ai_val = getattr(config.translation, 'enable_ai', True)
    
    if enable_ai_val:
        if not getattr(engine, 'no_ai', False):
            tlog.info("📡 [算力热加载] 检测到 AI 算力总控已启用，正在热加载/更新翻译官组件...")
            engine.translator = TranslatorFactory.create(config.translation)
            if engine.translator:
                engine.translator.api_timeout = config.translation.api_timeout
        else:
            engine.translator = None
    else:
        tlog.info("🔌 [算力热卸载] 检测到 AI 算力总控已关闭，正在热卸载翻译官组件...")
        engine.translator = None

    if hasattr(engine, 'route_manager') and engine.route_manager:
        engine.route_manager.translator = engine.translator
        
    # 6. 记录主权对齐日志
    tlog.info(f"✅ [Engine] 物理参数已全量对齐: Theme={engine.active_theme} | Vault={engine.vault_root}")
    engine.ledger.log("CONFIG_RELOADED", "主权参数全量原子对齐完成", imprint_id=engine.imprint_id)

    # ⚡ [V74.96] 主题选项配置变动实时热编译对正
    if hasattr(engine, 'ssg_adapter') and engine.ssg_adapter:
        try:
            engine.ssg_adapter.compile_theme_options()
        except Exception as compile_err:
            tlog.warning(f"⚠️ [Engine] 实时对正主题 CSS 变量失败: {compile_err}")

    # 🚀 [V74.9] 零重启热自愈：若状态从 Onboarding 状态复苏至就绪状态
    if was_onboarding and not engine.onboarding_required:
        tlog.info("🚀 [Onboarding 自愈] 检测到文库路径配置已生效！正在启动物理金库首次全量索引扫描...")
        try:
            # 重新执行首次全量索引重构，充填内存
            from core.editorial.vault_indexer import VaultIndexer
            VaultIndexer.build_indexes(engine.manuscript_source, config=engine.config, ledger=engine.ledger)
            tlog.info("✅ [Onboarding 自愈] 物理索引热扫描已完成！")
        except Exception as e:
            tlog.error(f"❌ [Onboarding 自愈] 物理索引扫描失败: {e}")
        
        # 若启动参数包含 --watch，则实时唤醒/点火守护进程
        if getattr(engine, 'args', None) and getattr(engine.args, 'watch', False):
            tlog.info("🐕 [Onboarding 自愈] 正在实时点火 Watchdog 本地热更监听线程...")
            try:
                from core.runtime.daemon import start_watchdog
                from core.runtime.engine_singleton import get_global_observer, set_global_observer
                # 确保没有旧的监听在运行
                if not get_global_observer():
                    # 获取当前索引的所有源文件相对路径
                    current_source_files = list(engine.manuscript_source.list_files())
                    new_observer, _ = start_watchdog(engine, engine.args, current_source_files)
                    set_global_observer(new_observer)
                    tlog.info("✅ [Onboarding 自愈] Watchdog 实时热更新探针启动成功！")
            except Exception as e:
                tlog.error(f"❌ [Onboarding 自愈] 实时热更点火失败: {e}")
