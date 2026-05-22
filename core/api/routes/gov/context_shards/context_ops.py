# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Context & System Diagnosis Ops
职责：承载系统上下文、诊断日志读取与健康状态监控的底层原子实现。
"""

import os
from typing import Optional, List
from core.runtime.engine_singleton import get_global_engine
from core.config.config import CONFIG_NAME, CONFIG_LOCAL_NAME, IMPRINT_DIR, CONFIG_DIR, CONFIG_IMPRINT_NAME

def get_system_context_impl():
    """
    承载系统上下文及运行元数据构建的原子逻辑实现。
    """
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}

    from core.governance.imprint_manager import im
    from core import __version__
    from core.ui.delegate import DisplayDelegate

    ai_cfg = engine.config.translation
    active_node = ai_cfg.primary_node
    active_provider = "Unknown"
    active_model = ai_cfg.primary_model or "Unknown"

    if active_node in ai_cfg.compute_nodes:
        node_cfg = ai_cfg.compute_nodes[active_node]
        active_provider = (getattr(node_cfg, "type", "") or "Unknown").upper()

    active_imprint = im.get_active_imprint()

    theme_map = {
        "default": "Sovereign (default)",
        "starlight": "Starlight (official)",
        "docusaurus": "Docusaurus (classic)",
        "vitepress": "VitePress (next)",
        "nextra": "Nextra (docs)"
    }
    raw_theme = engine.active_theme
    display_theme = theme_map.get(raw_theme, f"Custom ({raw_theme})")

    needs_install = False
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    if os.path.exists(os.path.join(theme_dir, "package.json")):
        if not os.path.exists(os.path.join(theme_dir, "node_modules")):
            needs_install = True

    from core.ingress.registry import ingress_registry
    ingress_cfg = engine.config.ingress_settings
    active_dialects = ingress_cfg.active_dialects or ["auto"]
    
    if "auto" in active_dialects:
        dialect_display = "自动感应 (Auto-Sensing)"
    else:
        active_dialect_id = active_dialects[0] if active_dialects else "generic"
        dialect_cls = ingress_registry.get_dialect(active_dialect_id)
        dialect_display = getattr(dialect_cls, "DISPLAY_NAME", active_dialect_id.upper()) if dialect_cls else active_dialect_id.upper()

    # 🛡️ 优雅解耦：直接从底层的 plugin_mapper 加载插件矩阵，避免循环引用 Hub 文件
    from core.api.routes.gov.plugin_mapper import assemble_plugin_matrix
    plugins = assemble_plugin_matrix()

    return {
        "version": DisplayDelegate.get_system_version(engine.config),
        "imprint": active_imprint,
        "imprint_name": engine.config.imprint_name,
        "theme": display_theme,
        "onboarding_required": engine.onboarding_required,
        "vault": {
            "root": engine.vault_root,
            "dialect": dialect_display
        },
        "ai": {
            "provider": active_provider,
            "model": active_model,
            "status": "degraded" if getattr(engine.translator, 'node_name', '') == 'fallback_mock' else "online",
            "warning": "当前版图的主力算力节点配置缺失，系统已自动切换至模拟/离线模式。" if getattr(engine.translator, 'node_name', '') == 'fallback_mock' else None
        },
        "i18n": {
            "source": getattr(engine.config.i18n_settings.source, 'prompt_lang', "Chinese"),
            "targets": [
                t.prompt_lang if hasattr(t, 'prompt_lang') else str(t)
                for t in engine.config.i18n_settings.targets
            ]
        },
        "plugins": plugins # 🚀 [V74.88] 物理补全插件指纹，驱动前端联动逻辑
    }

def get_lessons_impl():
    """
    承载 lessons-learned 诊断记录加载的原子逻辑实现。
    """
    engine = get_global_engine()
    if not engine: return []
    path = engine._resolve_path(engine.config.get_lessons_learned_path())
    if os.path.exists(path):
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return []

def get_sync_stats_impl():
    """
    承载同步状态流量看板的原子逻辑实现。
    """
    engine = get_global_engine()
    if not engine: return {}
    path = engine._resolve_path(engine.config.get_sync_stats_path())
    if os.path.exists(path):
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {}

def get_health_report_impl():
    """
    承载系统健康自愈与异常诊断报告的原子逻辑实现。
    """
    engine = get_global_engine()
    if not engine: return {}
    path = engine._resolve_path(engine.config.get_health_report_path())
    if os.path.exists(path):
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {}
