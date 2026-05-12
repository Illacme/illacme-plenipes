# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Context & System Discovery Routes
职责：承载系统上下文、插件发现、配置审计及健康报告的 API 接口。
架构：已从 governance.py 物理降解，实现业务逻辑的原子化隔离。
"""

from fastapi import APIRouter, Depends
from typing import Optional, List
import os
from core.runtime.cli_bootstrap import get_global_engine
from ..system import verify_token
from core.config.config import CONFIG_NAME, CONFIG_LOCAL_NAME, IMPRINT_DIR, CONFIG_DIR, CONFIG_IMPRINT_NAME

router = APIRouter()

@router.get("/api/system/context", dependencies=[Depends(verify_token)])
def get_system_context():
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

    return {
        "version": DisplayDelegate.get_system_version(engine.config),
        "imprint": active_imprint,
        "imprint_name": engine.config.imprint_name,
        "theme": display_theme,
        "vault": engine.vault_root,
        "ai": {
            "provider": active_provider,
            "model": active_model
        },
        "i18n": {
            "source": getattr(engine.config.i18n_settings.source, 'prompt_lang', "Chinese"),
            "targets": [
                t.prompt_lang if hasattr(t, 'prompt_lang') else str(t)
                for t in engine.config.i18n_settings.targets
            ]
        }
    }

@router.get("/api/governance/lessons", dependencies=[Depends(verify_token)])
def get_lessons():
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

@router.get("/api/governance/sync-stats", dependencies=[Depends(verify_token)])
def get_sync_stats():
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

@router.get("/api/governance/health-report", dependencies=[Depends(verify_token)])
def get_health_report():
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

@router.get("/api/system/config", dependencies=[Depends(verify_token)])
def get_full_config(level: str = "merged", imprint_id: Optional[str] = None):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    from core.config.governance_map import GOVERNANCE_RULES
    from core.governance.license_guard import LicenseGuard
    
    if level == "merged":
        data = engine.config.model_dump()
        data["_governance_rules"] = GOVERNANCE_RULES
        data["_is_licensed"] = LicenseGuard.is_licensed()
        return data
    
    import yaml
    path = CONFIG_NAME
    if level == "local":
        path = CONFIG_LOCAL_NAME
    elif level == "imprint":
        target_id = imprint_id or engine.im.get_active_imprint()
        path = os.path.join(IMPRINT_DIR, target_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
    
    data = {}
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        except:
            data = {"error": f"Failed to parse {path}"}
    else:
        data = {"error": f"File {path} not found"}
        
    return {
        "config": data,
        "governance_rules": GOVERNANCE_RULES
    }

@router.get("/api/plugins/list", dependencies=[Depends(verify_token)])
def list_active_plugins():
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    from core.adapters.egress.ssg.registry import SSGRegistry
    from core.adapters.egress.publishers.base import PublisherRegistry
    from core.adapters.ai.registry import AIProviderRegistry
    from core.adapters.syndication.targets import TARGET_REGISTRY
    
    SYSTEM_TRACK = "V24.0"
    p_cfg = engine.config.plugins
    disabled = p_cfg.disabled_plugins
    active_theme = engine.config.active_theme
    
    plugins = []
    
    # 0. Imprint Infrastructure
    from core.governance.imprint_manager import im
    active_imprint = im.get_active_imprint()
    for imp in im.list_imprints():
        imp_id = imp["id"]
        is_active = (imp_id == active_imprint)
        plugins.append({
            "id": imp_id, "category": "imprint", "category_name": "🏗️ Imprint 设施",
            "status": "In-Use" if is_active else "Ready",
            "is_in_use": is_active, "is_enabled": True,
            "origin": "user", "version": "V1.0",
            "description": f"主权 Imprint 设施：承载 '{imp_id}' 旗下的全量出版资产与政务规则。"
        })
    
    # 1. Theme Governance
    from core.config.config import THEMES_DIR
    local_theme_root = os.path.join(engine.config.system.data_root, THEMES_DIR)
    global_theme_root = os.path.join(os.getcwd(), THEMES_DIR)
    
    theme_ids = set()
    if os.path.exists(local_theme_root):
        for entry in os.listdir(local_theme_root):
            if os.path.isdir(os.path.join(local_theme_root, entry)) and not entry.startswith("."):
                if entry == "shared": continue
                is_active = (active_theme == entry)
                plugins.append({
                    "id": entry, "category": "theme", "category_name": "🎨 装帧主题",
                    "status": "In-Use" if is_active else "Local",
                    "is_in_use": is_active, "is_enabled": True,
                    "origin": "user", "location": "local", "version": "V1.0",
                    "description": "版图专属主题：位于当前版图目录下的物理资产。"
                })
                theme_ids.add(entry)

    if os.path.exists(global_theme_root):
        for entry in os.listdir(global_theme_root):
            if os.path.isdir(os.path.join(global_theme_root, entry)) and not entry.startswith("."):
                if entry in theme_ids or entry == "shared": continue
                is_active = (active_theme == entry)
                plugins.append({
                    "id": entry, "category": "theme", "category_name": "🎨 装帧主题",
                    "status": "In-Use" if is_active else "Central",
                    "is_in_use": is_active, "is_enabled": True,
                    "origin": "core", "location": "global", "version": SYSTEM_TRACK,
                    "description": "全局主题中心：位于系统根目录的主题资产库，随时可同步至版图。"
                })
                theme_ids.add(entry)

    for adapter_id in SSGRegistry.get_all_names():
        if adapter_id in theme_ids: continue
        is_active = (active_theme == adapter_id)
        renderer_cls = SSGRegistry.get_renderer(adapter_id)
        display_name = getattr(renderer_cls, "DISPLAY_NAME", adapter_id.upper())
        description = getattr(renderer_cls, "DESCRIPTION", f"内核原生适配器：驱动 {display_name} 工业级排版引擎。")
        plugins.append({
            "id": adapter_id, "name": display_name, "category": "theme", "category_name": "🎨 装帧主题适配器",
            "status": "In-Use" if is_active else "Native",
            "is_in_use": is_active, "is_enabled": (adapter_id not in disabled),
            "origin": "core", "version": SYSTEM_TRACK, "description": description
        })

    # 2. Compute Nodes
    for node_id, node_cfg in engine.config.translation.compute_nodes.items():
        is_active = (engine.config.translation.primary_node == node_id)
        plugins.append({
            "id": node_id, "category": "compute", "category_name": "⚙️ 算力节点",
            "status": "In-Use" if is_active else "Standby",
            "is_in_use": is_active, "is_enabled": True,
            "origin": "user", "version": "V1.0",
            "description": f"已划定的算力基座：类型为 {getattr(node_cfg, 'type', 'Unknown')}，负责承担 AI 推理任务。"
        })

    # 3. Syndication Targets
    for target_id in TARGET_REGISTRY.keys():
        plugins.append({
            "id": target_id, "category": "syndication", "category_name": "🛰️ 发行渠道",
            "status": "Ready", "is_in_use": False, "is_enabled": (target_id not in disabled),
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"全自动分发插件：支持将出版成品推向 {target_id.upper()} 矩阵。"
        })

    return {"plugins": plugins}
