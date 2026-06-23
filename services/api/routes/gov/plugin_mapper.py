import os
from typing import List, Dict, Any
from core.runtime.engine_singleton import get_global_engine

def _load_schema(theme_root: str, entry: str) -> dict:
    """🚀 物理探测并加载主题自描述配置，自动处理 IO 异常与缺省，支持全局 fallback"""
    import json
    path = os.path.join(theme_root, entry, "theme.schema.json")
    if not os.path.exists(path):
        from core.config.config import THEMES_DIR
        global_root = os.path.join(os.getcwd(), THEMES_DIR)
        path = os.path.join(global_root, entry, "theme.schema.json")

    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as sf:
                return json.load(sf)
        except Exception:
            pass
    return {}

def assemble_plugin_matrix() -> List[Dict[str, Any]]:
    """
    🧠 [V74.72] 物理插件矩阵组装器
    职责：从引擎配置与注册表中提取全域插件指纹，执行 1:1 逻辑对正。
    """
    engine = get_global_engine()
    if not engine:
        return []

    from core.adapters.egress.ssg.registry import SSGRegistry
    from core.adapters.egress.publishers.base import PublisherRegistry
    from core.adapters.ai.registry import AIProviderRegistry
    from core.adapters.syndication.targets import TARGET_REGISTRY
    from core.config.config import THEMES_DIR
    from core.governance.imprint_manager import im
    from core.ingress.registry import ingress_registry
    from core.markup.registry import markup_registry
    from core.editorial.registry import StepRegistry

    SYSTEM_TRACK = "V24.0"
    p_cfg = engine.config.plugins
    disabled = p_cfg.disabled_plugins
    active_theme = engine.config.active_theme
    plugins = []

    # 0. Imprint Infrastructure
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

    # 1. Theme Governance (Local & Central)
    local_theme_root = os.path.join(engine.config.system.data_root, THEMES_DIR)
    global_theme_root = os.path.join(os.getcwd(), THEMES_DIR)
    theme_ids = set()

    for root, loc, status, orig, ver, desc in [
        (local_theme_root, "local", "Local", "user", "V1.0", "版图专属主题：位于当前版图目录下的物理资产。"),
        (global_theme_root, "global", "Central", "core", SYSTEM_TRACK, "全局主题中心：位于系统根目录的主题资产库，随时可同步至版图。")
    ]:
        if os.path.exists(root):
            for entry in os.listdir(root):
                if entry in theme_ids or entry in ["shared", "__pycache__", ".DS_Store"] or entry.startswith("."):
                    continue
                if os.path.isdir(os.path.join(root, entry)):
                    is_active = (active_theme == entry)
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
        if r_id in ("generic", *theme_ids) or (r_id == "sovereign" and "default" in theme_ids): continue
        is_active = (active_theme == r_id)
        r_cls = SSGRegistry.get_renderer(r_id)
        name = getattr(r_cls, "DISPLAY_NAME", r_id.upper())
        plugins.append({
            "id": r_id, "name": name, "category": "theme", "category_name": "🎨 装帧主题适配器",
            "status": "In-Use" if is_active else "Native", "is_in_use": is_active, "is_enabled": (r_id not in disabled),
            "origin": "core", "location": "native", "version": getattr(r_cls, "VERSION", SYSTEM_TRACK),
            "description": getattr(r_cls, "DESCRIPTION", f"内核原生适配器：驱动 {name} 工业级排版引擎。"),
            "is_manageable": True, "schema": _load_schema(global_theme_root, r_id)
        })

    # 2. 🧱 算力节点 (Compute Nodes)
    for node_id, node_cfg in engine.config.translation.compute_nodes.items():
        is_active = (engine.config.translation.primary_node == node_id)
        node_type = getattr(node_cfg, "type", "")
        name = getattr(AIProviderRegistry.get_provider(node_type), "DISPLAY_NAME", node_id.upper())
        plugins.append({
            "id": node_id, "name": name, "category": "compute", "category_name": "⚙️ 算力节点",
            "status": "In-Use" if is_active else "Standby", "is_in_use": is_active, "is_enabled": getattr(node_cfg, "enabled", True), "origin": "user", "version": "V1.0",
            "base_url": getattr(node_cfg, "base_url", ""), "model": getattr(node_cfg, "model", ""), "node_type": node_type,
            "description": f"已划定的算力基座：类型为 {name}，负责承担 AI 推理任务。", "is_manageable": True
        })

    # 3. 🌐 全站托管能力 (Hosting)
    hosting_root = engine.config.publish_control.direct_upload
    for p_id, cls in PublisherRegistry.get_all_publishers().items():
        current_cfg = {}
        if isinstance(hosting_root, dict):
            current_cfg = hosting_root.get(p_id, {})
        elif hasattr(hosting_root, "get"):
            current_cfg = hosting_root.get(p_id, {})
            
        is_active = engine.config.publish_control.webhook_enabled if p_id == "webhook_dispatch" else (
            current_cfg.get("enabled", False) if isinstance(current_cfg, dict) else (
                getattr(current_cfg, "enabled", False) if hasattr(current_cfg, "enabled") else False
            )
        )
        name = getattr(cls, "DISPLAY_NAME", p_id.upper())
        plugins.append({
            "id": p_id, "name": name, "category": "hosting", "category_name": "🌐 全站托管",
            "status": "In-Use" if is_active else "Ready", "is_in_use": is_active, "is_enabled": (p_id not in disabled),
            "origin": "core", "version": getattr(cls, "VERSION", SYSTEM_TRACK),
            "description": getattr(cls, "DESCRIPTION", f"托管适配器插件：负责将出版物物理同步至 {name}。"),
            "cfg": hosting_root.get(p_id, {}) if isinstance(hosting_root, dict) else {}, "is_manageable": True
        })

    # 4. 🚀 分发渠道 (Syndication)
    synd_cfg = engine.config.syndication
    for t_id in TARGET_REGISTRY.keys():
        targets = getattr(synd_cfg, "targets", synd_cfg) if synd_cfg else {}
        curr_cfg = targets.get(t_id, {}) if isinstance(targets, dict) else getattr(targets, t_id, {})
        is_in_use = curr_cfg.get("enabled", False) if isinstance(curr_cfg, dict) else getattr(curr_cfg, "enabled", False)
        if hasattr(curr_cfg, 'dict'): curr_cfg = curr_cfg.dict()
        t_cls = TARGET_REGISTRY.get(t_id)
        name = getattr(t_cls, "DISPLAY_NAME", t_id.upper())
        plugins.append({
            "id": t_id, "name": name, "category": "publisher", "category_name": "🚀 分发渠道",
            "status": "Active" if is_in_use else "Ready", "is_in_use": is_in_use, "is_enabled": (t_id not in disabled),
            "origin": "core", "version": getattr(t_cls, "VERSION", SYSTEM_TRACK),
            "description": f"全自动分发插件：支持将出版成品推向 {name} 矩阵。", "cfg": curr_cfg, "is_manageable": True
        })

    # 4c. 🔌 图床服务 (Image Hosting)
    from core.adapters.image_hosting.targets import IMAGE_HOST_REGISTRY
    image_hosting_cfg = getattr(engine.config, "image_hosting", {}) or {}
    if hasattr(image_hosting_cfg, "dict"):
        image_hosting_cfg = image_hosting_cfg.dict()
    elif not isinstance(image_hosting_cfg, dict):
        image_hosting_cfg = {}

    for host_id, host_cls in IMAGE_HOST_REGISTRY.items():
        is_in_use = False
        current_cfg = {}
        if host_id in image_hosting_cfg and isinstance(image_hosting_cfg[host_id], dict):
            current_cfg = image_hosting_cfg[host_id]
            is_in_use = current_cfg.get("enabled", False)
        elif image_hosting_cfg.get("provider") == host_id:
            current_cfg = image_hosting_cfg
            is_in_use = True
            
        if host_id == "s3" and not is_in_use:
            s3_hosting = engine.config.publish_control.direct_upload.get("s3", {})
            if s3_hosting.get("enabled"):
                is_in_use = True
                current_cfg = s3_hosting

        display_name = getattr(host_cls, "DISPLAY_NAME", host_id.upper())
        description = getattr(host_cls, "DESCRIPTION", f"图床自发现适配器：支持将原稿相对图片上传至 {display_name} 并自动替换 CDN 链接。")
        plugins.append({
            "id": host_id, "name": display_name, "category": "image_hosting", "category_name": "🔌 图床服务",
            "status": "Active" if is_in_use else "Ready",
            "is_in_use": is_in_use,
            "is_enabled": (host_id not in disabled),
            "origin": "core" if host_id == "s3" else "extension", "version": getattr(host_cls, "VERSION", SYSTEM_TRACK),
            "description": description,
            "cfg": current_cfg,
            "is_manageable": True
        })

    # 5. 🧠 AI 协议 (Protocols)
    seen_proto_classes = set()
    for proto in AIProviderRegistry.get_all_protocols():
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
        fallback_desc = f"内核级 AI 通讯协议：支持对接任何符合 {proto.upper()} 标准的算力终端。"
        plugins.append({
            "id": proto, "name": display_name, "protocol_family": protocol_family, "default_url": default_url,
            "category": "protocol", "category_name": "🧠 AI 协议",
            "status": protocol_family.capitalize(), "is_in_use": True, "is_enabled": True,
            "origin": "core", "version": getattr(proto_cls, "VERSION", SYSTEM_TRACK),
            "description": getattr(proto_cls, "DESCRIPTION", fallback_desc), "is_manageable": True
        })
    # 6. Ingress (Sources & Dialects) / 7. Transformers / 8. Maskers / 9. Pipeline Steps
    for source in ingress_registry.list_sources():
        source_cls = ingress_registry.get_source(source)
        is_active = (engine.config.ingress_settings.source_type == source)
        display_name = getattr(source_cls, "DISPLAY_NAME", source.upper())
        fallback_desc = f"物理数据源适配器：支持从 {display_name} 物理同步原始资产。"
        plugins.append({
            "id": source, "name": display_name, "category": "ingress_source", "category_name": "📥 物理接入层",
            "status": "In-Use" if is_active else "Ready",
            "is_in_use": is_active, "is_enabled": True,
            "origin": "core", "version": getattr(source_cls, "VERSION", SYSTEM_TRACK),
            "description": getattr(source_cls, "DESCRIPTION", fallback_desc),
            "is_manageable": False
        })

    active_dialects = engine.config.ingress_settings.active_dialects
    for dialect in ingress_registry.list_dialects():
        dialect_cls = ingress_registry.get_dialect(dialect)
        is_pinned = (dialect in active_dialects)
        is_auto = ("auto" in active_dialects)
        
        display_name = getattr(dialect_cls, "DISPLAY_NAME", dialect.upper()) if dialect_cls else dialect.upper()
        fallback_desc = f"稿件输入方言适配：支持物理识别并解析 {display_name} 格式的原始文档。"
        
        # 优化状态显示
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
            "origin": "core", "version": getattr(dialect_cls, "VERSION", SYSTEM_TRACK) if dialect_cls else SYSTEM_TRACK,
            "description": getattr(dialect_cls, "DESCRIPTION", fallback_desc) if dialect_cls else fallback_desc,
            "is_manageable": False
        })

    for trans in markup_registry.get_transformers():
        t_id = getattr(trans, "PLUGIN_ID", trans.__class__.__name__.lower().replace("transformer", ""))
        name = getattr(trans, "DISPLAY_NAME", t_id.upper())
        plugins.append({
            "id": t_id, "name": name, "category": "transformer", "category_name": "🛠️ 资产加工",
            "status": "Active", "is_in_use": True, "is_enabled": True, "origin": "core", "version": getattr(trans, "VERSION", SYSTEM_TRACK),
            "description": getattr(trans, "DESCRIPTION", f"物理加工单元：负责对稿件进行 {name} 维度的结构化治理与转换。"), "is_manageable": False
        })

    for m_id in markup_registry._maskers.keys():
        masker = markup_registry.get_masker(m_id)
        name = getattr(masker, "DISPLAY_NAME", m_id.upper())
        plugins.append({
            "id": m_id, "name": name, "category": "masker", "category_name": "🛡️ 安全防护",
            "status": "Shielded", "is_in_use": True, "is_enabled": True, "origin": "core", "version": getattr(masker, "VERSION", SYSTEM_TRACK),
            "description": getattr(masker, "DESCRIPTION", f"隐私脱敏引擎：在出版分发前自动对稿件执行 {name} 级安全屏蔽。"), "is_manageable": False
        })

    for step in StepRegistry.get_all_names():
        step_cls = StepRegistry.get_step(step)
        is_active = True
        
        # 针对特定步骤检查开关
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
            "origin": "core", "version": getattr(step_cls, "VERSION", SYSTEM_TRACK),
            "description": getattr(step_cls, "DESCRIPTION", fallback_desc),
            "is_manageable": False
        })
    # 🚀 [V74.56] 统一对齐：同步核心 SSG 驱动的 DISPLAY_NAME 与 DESCRIPTION
    for p in plugins:
        renderer_cls = SSGRegistry.get_renderer("sovereign" if p["id"] == "default" else ("generic" if p["id"] == "universal" else p["id"])) if p["category"] == "theme" else None
        if renderer_cls:
            p["name"] = getattr(renderer_cls, "DISPLAY_NAME", p["id"].upper())
            p["description"] = getattr(renderer_cls, "DESCRIPTION", p["description"])
        if "name" not in p: p["name"] = p["id"].upper()
    return plugins
