import os
from typing import List, Dict, Any
from core.api.routes.system import get_global_engine

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
            "description": f"主权 Imprint 设施：承载 '{imp_id}' 旗下的全量出版资产与政务规则。"
        })

    # 1. Theme Governance (Local & Central)
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

    # 1b. Native Renderers
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

    # 2. 🧱 算力节点 (Compute Nodes)
    for node_id, node_cfg in engine.config.translation.compute_nodes.items():
        is_active = (engine.config.translation.primary_node == node_id)
        plugins.append({
            "id": node_id, "category": "compute", "category_name": "⚙️ 算力节点",
            "status": "In-Use" if is_active else "Standby",
            "is_in_use": is_active, "is_enabled": True,
            "origin": "user", "version": "V1.0",
            "base_url": getattr(node_cfg, "base_url", ""),
            "model": getattr(node_cfg, "model", ""),
            "node_type": getattr(node_cfg, "type", ""),
            "description": f"已划定的算力基座：类型为 {getattr(node_cfg, 'type', 'Unknown')}，负责承担 AI 推理任务。"
        })

    # 3. 🌐 全站托管能力 (Hosting)
    hosting_root = engine.config.publish_control.direct_upload
    for p_id, cls in PublisherRegistry.get_all_publishers().items():
        is_active = False
        if hasattr(engine, 'deployment_manager'):
            is_active = any(isinstance(pub, cls) for pub in engine.deployment_manager.publishers)
        current_cfg = hosting_root.get(p_id, {}) if isinstance(hosting_root, dict) else {}
        description = getattr(cls, "DESCRIPTION", f"托管适配器插件：负责将出版物物理同步至 {p_id.upper()}。")
        plugins.append({
            "id": p_id, "category": "hosting", "category_name": "🌐 全站托管",
            "status": "In-Use" if is_active else "Ready",
            "is_in_use": is_active, "is_enabled": True,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": description,
            "cfg": current_cfg
        })

    # 4. 🚀 分发渠道 (Syndication)
    synd_cfg = engine.config.syndication
    for target_id in TARGET_REGISTRY.keys():
        is_in_use = (target_id in synd_cfg.targets) if hasattr(synd_cfg, 'targets') else False
        current_cfg = synd_cfg.targets.get(target_id, {}) if is_in_use else {}
        if hasattr(current_cfg, 'dict'): current_cfg = current_cfg.dict()
        plugins.append({
            "id": target_id, "category": "publisher", "category_name": "🚀 分发渠道",
            "status": "Active" if is_in_use else "Ready",
            "is_in_use": is_in_use,
            "is_enabled": (target_id not in disabled),
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"全自动分发插件：支持将出版成品推向 {target_id.upper()} 矩阵。",
            "cfg": current_cfg
        })

    # 5. 🧠 AI 协议 (Protocols)
    for proto in AIProviderRegistry.get_all_protocols():
        proto_cls = AIProviderRegistry.get_provider(proto)
        display_name = getattr(proto_cls, "DISPLAY_NAME", proto.upper())
        protocol_family = getattr(proto_cls, "PROTOCOL_FAMILY", "native")
        default_url = getattr(proto_cls, "DEFAULT_URL", "")
        plugins.append({
            "id": proto, "name": display_name,
            "protocol_family": protocol_family,
            "default_url": default_url,
            "category": "protocol", "category_name": "🧠 AI 协议",
            "status": "Native", "is_in_use": True, "is_enabled": True,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"内核级 AI 通讯协议：支持对接任何符合 {proto.upper()} 标准的算力终端。"
        })

    # 6. Ingress / 7. Transformers / 8. Maskers / 9. Pipeline Steps
    # (省略部分说明，逻辑与原 context.py 保持 1:1)
    for dialect in ingress_registry.list_dialects():
        plugins.append({
            "id": dialect, "name": dialect.upper(), "category": "ingress", "category_name": "📥 输入方言",
            "status": "Active", "is_in_use": True, "is_enabled": True,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"稿件输入方言适配：支持物理识别并解析 {dialect.upper()} 格式的原始文档。"
        })

    for trans in markup_registry.get_transformers():
        t_id = getattr(trans, "PLUGIN_ID", trans.__class__.__name__.lower().replace("transformer", ""))
        plugins.append({
            "id": t_id, "name": t_id.upper(), "category": "transformer", "category_name": "🛠️ 资产加工",
            "status": "Active", "is_in_use": True, "is_enabled": True,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"物理加工单元：负责对稿件进行 {t_id.upper()} 维度的结构化治理与转换。"
        })

    for masker_id in markup_registry._maskers.keys():
        plugins.append({
            "id": masker_id, "name": masker_id.upper(), "category": "masker", "category_name": "🛡️ 安全防护",
            "status": "Shielded", "is_in_use": True, "is_enabled": True,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"隐私脱敏引擎：在出版分发前自动对稿件执行 {masker_id.upper()} 级安全屏蔽。"
        })

    for step in StepRegistry.get_all_names():
        plugins.append({
            "id": step, "name": step.upper(), "category": "editorial", "category_name": "🧬 流程审计",
            "status": "Audited", "is_in_use": True, "is_enabled": True,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"出版工序环节：构成主权出版流水线的 '{step}' 核心原子步骤。"
        })

    # 🚀 [V74.56] 统一对齐：确保所有插件均具备 name 属性
    for p in plugins:
        if "name" not in p:
            p["name"] = p["id"].upper()

    return plugins
