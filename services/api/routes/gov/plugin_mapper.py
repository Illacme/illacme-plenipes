#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Plugin Matrix Mapper & Assembler
模块职责：全域插件指纹提取、矩阵组装与 1:1 逻辑对正。
🛡️ [SOP-01 & SOP-02]：自底向上物理拆分重构版本，单文件物理行数严格 ≤300 行。
"""

import os
from typing import List, Dict, Any
from core.runtime.engine_singleton import get_global_engine
from core.adapters.egress.ssg.registry import SSGRegistry
from core.config.config import THEMES_DIR
from core.governance.imprint_manager import im

from .plugin_collector_channels import (
    collect_hosting_plugins,
    collect_notification_plugins,
    collect_syndication_plugins,
    collect_image_hosting_plugins,
)
from .plugin_collector_pipeline import (
    collect_compute_and_protocol_plugins,
    collect_ingress_and_editorial_plugins,
)


def _load_schema(theme_root: str, entry: str) -> dict:
    """🚀 物理探测并加载主题自描述配置，优先对齐全局母本契约，防卫品牌旧假数据"""
    import json
    global_root = os.path.join(os.getcwd(), THEMES_DIR)
    path = os.path.join(global_root, entry, "theme.schema.json")
    if not os.path.exists(path):
        path = os.path.join(theme_root, entry, "theme.schema.json")

    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as sf:
                return json.load(sf)
        except Exception:
            pass
    return {}


def _collect_imprint_plugins() -> List[Dict[str, Any]]:
    """0. Imprint Infrastructure"""
    plugins = []
    active_imprint = im.get_active_imprint()
    for imp in im.list_imprints():
        imp_id = imp["id"]
        is_active = (imp_id == active_imprint)
        plugins.append({
            "id": imp_id, "category": "imprint", "category_name": "🏗️ Imprint 设施",
            "status": "In-Use" if is_active else "Ready",
            "is_in_use": is_active, "is_enabled": True,
            "origin": "user", "version": "V1.0",
            "description": f"主权 Imprint 设施：承载 '{imp_id}' 旗下的全量出版资产与政务规则。",
            "is_manageable": False
        })
    return plugins


def _collect_theme_plugins(engine, disabled: set, system_track: str) -> List[Dict[str, Any]]:
    """1. Theme Governance (Local & Central) & Native Renderers"""
    plugins = []
    active_theme = engine.config.active_theme
    local_theme_root = os.path.join(engine.config.system.data_root, THEMES_DIR)
    global_theme_root = os.path.join(os.getcwd(), THEMES_DIR)
    theme_ids = set()

    norm_active = "sovereign" if (active_theme in ("default", "sovereign", None, "")) else active_theme

    for root, loc, status, orig, ver, desc in [
        (local_theme_root, "local", "Local", "user", "V1.0", "品牌专属主题：位于当前品牌目录下的物理资产。"),
        (global_theme_root, "global", "Central", "core", system_track, "全局主题中心：位于系统根目录的主题资产库，随时可同步至品牌。")
    ]:
        if os.path.exists(root):
            for entry in os.listdir(root):
                if entry in theme_ids or entry in ["shared", "__pycache__", ".DS_Store"] or entry.startswith("."):
                    continue
                # 🛡️ 过滤历史旧别名 default，统一归一化为 sovereign
                if entry == "default":
                    continue
                if os.path.isdir(os.path.join(root, entry)):
                    is_active = (norm_active == entry)
                    plugins.append({
                        "id": entry, "category": "theme", "category_name": "🎨 装帧主题",
                        "status": "In-Use" if is_active else status,
                        "is_in_use": is_active, "is_enabled": True,
                        "origin": orig, "location": loc, "version": ver,
                        "description": desc, "is_manageable": True,
                        "schema": _load_schema(root, entry)
                    })
                    theme_ids.add(entry)

    # 1b. Native Renderers
    for r_id in SSGRegistry.get_all_names():
        if r_id in ("generic", *theme_ids) or (r_id in ("sovereign", "default") and "sovereign" in theme_ids):
            continue
        is_active = (norm_active == r_id)
        r_cls = SSGRegistry.get_renderer(r_id)
        name = getattr(r_cls, "DISPLAY_NAME", r_id.upper())
        plugins.append({
            "id": r_id, "name": name, "category": "theme", "category_name": "🎨 装帧主题适配器",
            "status": "In-Use" if is_active else "Native", "is_in_use": is_active, "is_enabled": (r_id not in disabled),
            "origin": "core", "location": "native", "version": getattr(r_cls, "VERSION", system_track),
            "description": getattr(r_cls, "DESCRIPTION", f"内核原生适配器：驱动 {name} 工业级排版引擎。"),
            "is_manageable": True, "schema": _load_schema(global_theme_root, r_id)
        })
    return plugins


def _normalize_plugin_names(plugins: List[Dict[str, Any]]) -> None:
    """🚀 [V74.56] 统一对齐：同步核心 SSG 驱动的 DISPLAY_NAME 与 DESCRIPTION 并兜底 name"""
    theme_display_names = {
        "sovereign": "Sovereign",
        "default": "Sovereign",
        "docusaurus": "Docusaurus",
        "starlight": "Starlight",
        "vitepress": "VitePress",
        "nextra": "Nextra",
        "universal": "Universal",
        "hexo": "Hexo",
        "hugo": "Hugo",
    }
    for p in plugins:
        if p.get("category") == "theme":
            p["name"] = theme_display_names.get(p["id"].lower(), p["id"].capitalize())
            renderer_cls = SSGRegistry.get_renderer(
                "sovereign" if p["id"] == "default" else ("generic" if p["id"] == "universal" else p["id"])
            )
            if renderer_cls:
                p["description"] = getattr(renderer_cls, "DESCRIPTION", p.get("description", ""))
        elif "name" not in p:
            p["name"] = p["id"].upper()


def _collect_ebook_plugins(engine, disabled: set, system_track: str) -> List[Dict[str, Any]]:
    """🚀 [V125.0] EBook Bindery Plugins (电子书装订驱动)"""
    from core.adapters.egress.ebook import EBookRegistry
    plugins = []
    for plugin_id in EBookRegistry.get_all_names():
        adapter_cls = EBookRegistry.get_adapter(plugin_id)
        if not adapter_cls:
            continue
        display_name = getattr(adapter_cls, "DISPLAY_NAME", plugin_id.upper())
        ext = getattr(adapter_cls, "OUTPUT_EXTENSION", "")
        desc = getattr(adapter_cls, "DESCRIPTION", f"数字装订驱动：将文库原稿整卷编排导出为 {ext} 便携数字出版物。")
        ver = getattr(adapter_cls, "VERSION", system_track)
        plugins.append({
            "id": plugin_id,
            "name": display_name,
            "category": "ebook",
            "category_name": "📚 数字装订",
            "status": "Ready",
            "is_in_use": True,
            "is_enabled": (plugin_id not in disabled),
            "origin": "core",
            "location": "native",
            "version": ver,
            "description": desc,
            "output_extension": ext,
            "is_manageable": True
        })
    return plugins


def assemble_plugin_matrix() -> List[Dict[str, Any]]:
    """
    🧠 [V74.72] 物理插件矩阵组装器
    职责：从引擎配置与注册表中提取全域插件指纹，执行 1:1 逻辑对正。
    """
    engine = get_global_engine()
    if not engine:
        return []

    system_track = "V24.0"
    p_cfg = engine.config.plugins
    disabled = p_cfg.disabled_plugins

    plugins: List[Dict[str, Any]] = []

    # 0. Imprint Infrastructure
    plugins.extend(_collect_imprint_plugins())

    # 1. Theme Governance & Native Renderers
    plugins.extend(_collect_theme_plugins(engine, disabled, system_track))

    # 2 & 5. Compute Nodes & AI Protocols
    plugins.extend(collect_compute_and_protocol_plugins(engine, system_track))

    # 3. Hosting (全站托管)
    plugins.extend(collect_hosting_plugins(engine, disabled, system_track))

    # 3b. Notifications & Event Dispatchers (消息通知)
    plugins.extend(collect_notification_plugins(engine, disabled))

    # 4. Syndication (分发渠道)
    plugins.extend(collect_syndication_plugins(engine, disabled, system_track))

    # 4b. EBook Bindery (数字装订)
    plugins.extend(_collect_ebook_plugins(engine, disabled, system_track))

    # 4c. Image Hosting (图床服务)
    plugins.extend(collect_image_hosting_plugins(engine, disabled, system_track))

    # 6-9. Ingress, Transformers, Maskers, Pipeline Steps (流水线)
    plugins.extend(collect_ingress_and_editorial_plugins(engine, system_track))

    # 对齐与兜底
    _normalize_plugin_names(plugins)

    return plugins

