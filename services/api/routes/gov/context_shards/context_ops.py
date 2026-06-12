# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Context & System Diagnosis Ops
职责：承载系统上下文、诊断日志读取与健康状态监控的底层原子实现。
"""

import os
from core.runtime.engine_singleton import get_global_engine

def get_system_context_impl():
    """
    承载系统上下文及运行元数据构建的原子逻辑实现。
    """
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}

    from core.governance.imprint_manager import im
    from core.ui.delegate import DisplayDelegate

    ai_cfg = engine.config.translation
    active_node = ai_cfg.primary_node
    active_provider = "Unknown"
    active_model = ai_cfg.primary_model or "Unknown"

    if active_node in ai_cfg.compute_nodes:
        node_cfg = ai_cfg.compute_nodes[active_node]
        active_provider = (getattr(node_cfg, "type", "") or "Unknown").upper()

    # 📡 物理算力容灾拓扑对正 (V75.12)
    primary_node = ai_cfg.primary_node or "Unknown"
    fallback_node = ai_cfg.fallback_node or "Unknown"
    primary_model = ai_cfg.primary_model or "Unknown"
    fallback_model = ai_cfg.fallback_model or "Unknown"
    
    primary_provider = "UNKNOWN"
    if primary_node in ai_cfg.compute_nodes:
        primary_provider = (getattr(ai_cfg.compute_nodes[primary_node], "type", "") or "UNKNOWN").upper()
        
    fallback_provider = "UNKNOWN"
    if fallback_node in ai_cfg.compute_nodes:
        fallback_provider = (getattr(ai_cfg.compute_nodes[fallback_node], "type", "") or "UNKNOWN").upper()

    strategy_str = ai_cfg.strategy.value if hasattr(ai_cfg.strategy, "value") else str(ai_cfg.strategy)

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
    from services.api.routes.gov.plugin_mapper import assemble_plugin_matrix
    plugins = assemble_plugin_matrix()

    # 📡 算力状态检测
    enable_ai = getattr(ai_cfg, 'enable_ai', True) and not getattr(engine, 'no_ai', False)
    if not enable_ai:
        ai_status = "disabled"
        warning_msg = "AI 算力总控已关闭，系统运行于纯本地出版模式。"
    elif getattr(engine.translator, 'node_name', '') == 'fallback_mock':
        ai_status = "degraded"
        warning_msg = "当前版图的主力算力节点配置缺失，系统已自动切换至模拟/离线模式。"
    else:
        ai_status = "online"
        warning_msg = None

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
            "status": ai_status,
            "warning": warning_msg,
            "strategy": strategy_str.upper(),
            "primary": {
                "node": primary_node,
                "provider": primary_provider,
                "model": primary_model
            },
            "fallback": {
                "node": fallback_node,
                "provider": fallback_provider,
                "model": fallback_model
            }
        },
        "i18n": {
            "enabled": engine.config.i18n_settings.enabled,
            "source": getattr(engine.config.i18n_settings.source, 'lang_code', 'ZH').upper(),
            # 🛡️ [UI 一致性] 使用 lang_code 大写（如 ES、EN）而非全名（Spanish、English），
            # 与校对工作台的语种 Tab 标签风格保持一致，避免两处显示不一致造成用户困惑。
            "targets": [
                (t.lang_code if hasattr(t, 'lang_code') else str(t)).upper()
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

def get_pulse_impl():
    """
    承载系统实时脉搏与调度指标加载的原子逻辑实现。
    """
    engine = get_global_engine()
    if not engine: return {}
    path = engine._resolve_path(engine.config.get_pulse_path())
    if os.path.exists(path):
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {}
