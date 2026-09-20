#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Plugin Matrix Pipeline Collector Shard
模块职责：收集算力节点 (Compute)、AI协议 (Protocols)、接入层 (Ingress)、资产加工 (Transformers)、安全防护 (Maskers) 与流程审计 (Steps)。
🛡️ [SOP-01 & SOP-02]：从 plugin_mapper.py 物理拆解出的流水线层装配器。
"""

from typing import List, Dict, Any


def collect_compute_and_protocol_plugins(engine, system_track: str) -> List[Dict[str, Any]]:
    """收集算力节点 (Compute Nodes) 与 AI 协议 (Protocols)"""
    from core.adapters.ai.registry import AIProviderRegistry

    plugins = []
    # 2. 🧱 算力节点 (Compute Nodes)
    for node_id, node_cfg in engine.config.translation.compute_nodes.items():
        is_active = (engine.config.translation.primary_node == node_id)
        node_type = getattr(node_cfg, "type", "")
        name = getattr(AIProviderRegistry.get_provider(node_type), "DISPLAY_NAME", node_id.upper())
        plugins.append({
            "id": node_id, "name": name, "category": "compute", "category_name": "⚙️ 算力节点",
            "status": "In-Use" if is_active else "Standby", "is_in_use": is_active,
            "is_enabled": getattr(node_cfg, "enabled", True), "origin": "user", "version": "V1.0",
            "base_url": getattr(node_cfg, "base_url", ""), "model": getattr(node_cfg, "model", ""), "node_type": node_type,
            "description": f"已划定的算力基座：类型为 {name}，负责承担 AI 推理任务。", "is_manageable": True
        })

    # 5. 🧠 AI 协议 (Protocols)
    seen_proto_classes = set()
    for proto in AIProviderRegistry.get_all_protocols():
        if proto == "generic":
            continue
        proto_cls = AIProviderRegistry.get_provider(proto)
        if not proto_cls:
            continue
        # 别名过滤：若当前键名与对应类定义的主 PLUGIN_ID 不一致，说明它是别名，直接跳过以防重复
        main_plugin_id = getattr(proto_cls, "PLUGIN_ID", None)
        if main_plugin_id and proto != main_plugin_id:
            continue
        if proto_cls in seen_proto_classes:
            continue
        seen_proto_classes.add(proto_cls)
        display_name = getattr(proto_cls, "DISPLAY_NAME", proto.upper())
        protocol_family = getattr(proto_cls, "PROTOCOL_FAMILY", "native")
        default_url = getattr(proto_cls, "DEFAULT_URL", "")
        aliases = getattr(proto_cls, "ALIASES", [])
        fallback_desc = f"内核级 AI 通讯协议：支持对接任何符合 {proto.upper()} 标准的算力终端。"
        plugins.append({
            "id": proto, "name": display_name, "protocol_family": protocol_family, "default_url": default_url,
            "aliases": aliases,
            "category": "protocol", "category_name": "🧠 算力渠道",
            "status": protocol_family.capitalize(), "is_in_use": True, "is_enabled": True,
            "origin": "core", "version": getattr(proto_cls, "VERSION", system_track),
            "description": getattr(proto_cls, "DESCRIPTION", fallback_desc), "is_manageable": True
        })
    return plugins


def collect_ingress_and_editorial_plugins(engine, system_track: str) -> List[Dict[str, Any]]:
    """收集接入源、方言、转换器、脱敏器与流程步骤"""
    from core.ingress.registry import ingress_registry
    from core.markup.registry import markup_registry
    from core.editorial.registry import StepRegistry

    plugins = []

    # Ingress Sources
    for source in ingress_registry.list_sources():
        source_cls = ingress_registry.get_source(source)
        is_active = (engine.config.ingress_settings.source_type == source)
        display_name = getattr(source_cls, "DISPLAY_NAME", source.upper())
        fallback_desc = f"物理数据源适配器：支持从 {display_name} 物理同步原始资产。"
        plugins.append({
            "id": source, "name": display_name, "category": "ingress_source", "category_name": "📥 物理接入层",
            "status": "In-Use" if is_active else "Ready",
            "is_in_use": is_active, "is_enabled": True,
            "origin": "core", "version": getattr(source_cls, "VERSION", system_track),
            "description": getattr(source_cls, "DESCRIPTION", fallback_desc),
            "is_manageable": False
        })

    # Ingress Dialects
    active_dialects = engine.config.ingress_settings.active_dialects
    for dialect in ingress_registry.list_dialects():
        dialect_cls = ingress_registry.get_dialect(dialect)
        is_pinned = (dialect in active_dialects)
        is_auto = ("auto" in active_dialects)
        
        display_name = getattr(dialect_cls, "DISPLAY_NAME", dialect.upper()) if dialect_cls else dialect.upper()
        fallback_desc = f"稿件输入方言适配：支持物理识别并解析 {display_name} 格式的原始文档。"
        
        if is_pinned:
            status = "In-Use"
        elif is_auto:
            status = "Auto-Sensing"
        else:
            status = "Standby"
            
        plugins.append({
            "id": dialect, "name": display_name, "category": "ingress_dialect", "category_name": "🌀 逻辑解析层",
            "status": status,
            "is_in_use": is_pinned or is_auto,
            "is_enabled": True,
            "origin": "core", "version": getattr(dialect_cls, "VERSION", system_track) if dialect_cls else system_track,
            "description": getattr(dialect_cls, "DESCRIPTION", fallback_desc) if dialect_cls else fallback_desc,
            "is_manageable": False
        })

    # Transformers
    for trans in markup_registry.get_transformers():
        t_id = getattr(trans, "PLUGIN_ID", trans.__class__.__name__.lower().replace("transformer", ""))
        name = getattr(trans, "DISPLAY_NAME", t_id.upper())
        plugins.append({
            "id": t_id, "name": name, "category": "transformer", "category_name": "🛠️ 资产加工",
            "status": "Active", "is_in_use": True, "is_enabled": True, "origin": "core", "version": getattr(trans, "VERSION", system_track),
            "description": getattr(trans, "DESCRIPTION", f"物理加工单元：负责对稿件进行 {name} 维度的结构化治理与转换。"), "is_manageable": False
        })

    # Maskers
    for m_id in markup_registry._maskers.keys():
        masker = markup_registry.get_masker(m_id)
        name = getattr(masker, "DISPLAY_NAME", m_id.upper())
        plugins.append({
            "id": m_id, "name": name, "category": "masker", "category_name": "🛡️ 安全防护",
            "status": "Shielded", "is_in_use": True, "is_enabled": True, "origin": "core", "version": getattr(masker, "VERSION", system_track),
            "description": getattr(masker, "DESCRIPTION", f"隐私脱敏引擎：在出版分发前自动对稿件执行 {name} 级安全屏蔽。"), "is_manageable": False
        })

    # Editorial Steps
    for step in StepRegistry.get_all_names():
        step_cls = StepRegistry.get_step(step)
        is_active = True
        
        if step == "staticizer":
            is_active = engine.config.ingress_settings.staticize_components
        elif step == "seo":
            is_active = engine.config.seo_settings.enabled
            
        display_name = getattr(step_cls, "DISPLAY_NAME", step.upper())
        fallback_desc = f"出版工序环节：构成主权出版流水线的 '{display_name}' 核心原子步骤。"
        plugins.append({
            "id": step, "name": display_name, "category": "editorial", "category_name": "🧬 流程审计",
            "status": "In-Use" if is_active else "Standby",
            "is_in_use": is_active, "is_enabled": True,
            "origin": "core", "version": getattr(step_cls, "VERSION", system_track),
            "description": getattr(step_cls, "DESCRIPTION", fallback_desc),
            "is_manageable": False
        })

    return plugins
