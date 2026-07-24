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
            "id": imp_id,
            "name": imp.get("name", imp_id.upper()),
            "category": "imprint",
            "category_name": "🏷️ 出版印记",
            "status": "Active" if is_active else "Standby",
            "is_in_use": is_active,
            "is_enabled": True,
            "origin": "sovereign",
            "version": SYSTEM_TRACK,
            "description": imp.get("description", "主权出版印记配额指纹。"),
            "is_manageable": False
        })

    # 1. SSG Themes (Local & Remote)
    vault_themes = os.path.join(engine.vault_root, THEMES_DIR)
    local_themes = []
    if os.path.exists(vault_themes):
        local_themes = [d for d in os.listdir(vault_themes) if os.path.isdir(os.path.join(vault_themes, d)) and not d.startswith('.')]

    for t_id in local_themes:
        is_active = (t_id == active_theme)
        schema = _load_schema(vault_themes, t_id)
        plugins.append({
            "id": t_id,
            "name": f"{t_id.upper()} (本地)",
            "category": "theme",
            "category_name": "🎨 视觉装帧",
            "status": "In-Use" if is_active else "Ready",
            "is_in_use": is_active,
            "is_enabled": t_id not in disabled,
            "origin": "local",
            "location": "local",
            "version": schema.get("version", SYSTEM_TRACK),
            "description": schema.get("description", f"存储于本地文库中的装帧主题 ({t_id})"),
            "schema": schema,
            "has_config": bool(schema.get("properties")),
            "is_manageable": True
        })

    for ssg in SSGRegistry.list_renderers():
        if ssg not in local_themes:
            renderer_cls = SSGRegistry.get_renderer(ssg)
            name = getattr(renderer_cls, "DISPLAY_NAME", ssg.upper()) if renderer_cls else ssg.upper()
            plugins.append({
                "id": ssg,
                "name": name,
                "category": "theme",
                "category_name": "🎨 视觉装帧",
                "status": "Available",
                "is_in_use": False,
                "is_enabled": ssg not in disabled,
                "origin": "core",
                "location": "remote",
                "version": getattr(renderer_cls, "VERSION", SYSTEM_TRACK) if renderer_cls else SYSTEM_TRACK,
                "description": getattr(renderer_cls, "DESCRIPTION", f"官方内置的物理静态站点渲染引擎 ({ssg})。") if renderer_cls else f"内置引擎 ({ssg})",
                "has_config": False,
                "is_manageable": False
            })

    # 2. Direct Upload Platforms (Publish Control)
    for p_id in PublisherRegistry.list_active_targets():
        pub_cls = PublisherRegistry.get_publisher(p_id)
        is_en = p_id not in disabled
        name = getattr(pub_cls, "DISPLAY_NAME", p_id.upper()) if pub_cls else p_id.upper()
        plugins.append({
            "id": p_id,
            "name": name,
            "category": "hosting",
            "category_name": "🌐 全站托管",
            "status": "Enabled" if is_en else "Disabled",
            "is_in_use": is_en,
            "is_enabled": is_en,
            "origin": "official",
            "version": getattr(pub_cls, "VERSION", SYSTEM_TRACK) if pub_cls else SYSTEM_TRACK,
            "description": getattr(pub_cls, "DESCRIPTION", f"官方直连部署管道，支持物理产物全量推送到 {name}。") if pub_cls else f"部署管道 ({p_id})",
            "has_config": True,
            "is_manageable": True
        })

    # 2.5 Image Hosting Adapters
    try:
        from adapters.egress.image_hosting.registry import ImageHostingRegistry
        for img_id in ImageHostingRegistry.list_adapters():
            adapter_cls = ImageHostingRegistry.get_adapter(img_id)
            is_en = img_id not in disabled
            name = getattr(adapter_cls, "DISPLAY_NAME", img_id.upper()) if adapter_cls else img_id.upper()
            plugins.append({
                "id": img_id,
                "name": name,
                "category": "image_hosting",
                "category_name": "📷 图床存储",
                "status": "Enabled" if is_en else "Disabled",
                "is_in_use": is_en,
                "is_enabled": is_en,
                "origin": "official",
                "version": getattr(adapter_cls, "VERSION", SYSTEM_TRACK) if adapter_cls else SYSTEM_TRACK,
                "description": getattr(adapter_cls, "DESCRIPTION", f"图床对象存储服务，支持物理资源自动上云与外链转换。") if adapter_cls else f"图床服务 ({img_id})",
                "has_config": True,
                "is_manageable": True
            })
    except Exception:
        pass

    # 2.6 Notification Adapters
    try:
        from adapters.notifications.webhook.registry import NotificationRegistry
        for notif_id in NotificationRegistry.list_adapters():
            adapter_cls = NotificationRegistry.get_adapter(notif_id)
            is_en = notif_id not in disabled
            name = getattr(adapter_cls, "DISPLAY_NAME", notif_id.upper()) if adapter_cls else notif_id.upper()
            plugins.append({
                "id": notif_id,
                "name": name,
                "category": "notification",
                "category_name": "📢 消息通知",
                "status": "Enabled" if is_en else "Disabled",
                "is_in_use": is_en,
                "is_enabled": is_en,
                "origin": "official",
                "version": getattr(adapter_cls, "VERSION", SYSTEM_TRACK) if adapter_cls else SYSTEM_TRACK,
                "description": getattr(adapter_cls, "DESCRIPTION", f"即时消息广播与告警 Hook 通道。") if adapter_cls else f"消息通知 ({notif_id})",
                "has_config": True, "is_manageable": True
            })
    except Exception:
        pass

    # 3. Syndication Platforms
    for target_id, target in TARGET_REGISTRY.items():
        is_en = target_id not in disabled
        t_name = getattr(target, "name", getattr(target, "DISPLAY_NAME", target_id.upper()))
        t_desc = getattr(target, "description", getattr(target, "DESCRIPTION", f"分发渠道适配器 ({target_id})"))
        plugins.append({
            "id": target_id,
            "name": t_name,
            "category": "publisher",
            "category_name": "🚀 分发渠道",
            "status": "Enabled" if is_en else "Disabled",
            "is_in_use": is_en,
            "is_enabled": is_en,
            "origin": "official",
            "version": getattr(target, "VERSION", SYSTEM_TRACK),
            "description": t_desc,
            "has_config": True,
            "is_manageable": True
        })

    # 4. AI Provider Network
    for prov_id in AIProviderRegistry.list_active():
        prov_cls = AIProviderRegistry.get_provider(prov_id)
        is_en = prov_id not in disabled
        name = getattr(prov_cls, "DISPLAY_NAME", prov_id.upper()) if prov_cls else prov_id.upper()
        plugins.append({
            "id": prov_id,
            "name": name,
            "category": "protocol",
            "category_name": "🧠 AI 协议",
            "status": "Active" if is_en else "Disabled",
            "is_in_use": is_en,
            "is_enabled": is_en,
            "origin": "core",
            "version": getattr(prov_cls, "VERSION", SYSTEM_TRACK) if prov_cls else SYSTEM_TRACK,
            "description": getattr(prov_cls, "DESCRIPTION", f"AI 大模型能力网络节点 ({name})。") if prov_cls else f"AI 模型 ({prov_id})",
            "is_manageable": False
        })

    # 5. Dialects & Processors
    active_dialects = engine.config.ingress_settings.active_dialects
    for dialect in ingress_registry.list_dialects():
        dialect_cls = ingress_registry.get_dialect(dialect)
        is_pinned = (dialect in active_dialects)
        is_auto = ("auto" in active_dialects)
        display_name = getattr(dialect_cls, "DISPLAY_NAME", dialect.upper()) if dialect_cls else dialect.upper()
        plugins.append({
            "id": dialect,
            "name": display_name,
            "category": "ingress_dialect",
            "category_name": "🌀 逻辑解析层",
            "status": "In-Use" if is_pinned else ("Auto-Sensing" if is_auto else "Standby"),
            "is_in_use": is_pinned or is_auto,
            "is_enabled": True,
            "origin": "core",
            "version": getattr(dialect_cls, "VERSION", SYSTEM_TRACK) if dialect_cls else SYSTEM_TRACK,
            "description": getattr(dialect_cls, "DESCRIPTION", f"稿件输入方言适配：支持解析 {display_name} 格式文档。") if dialect_cls else f"解析器 ({dialect})",
            "is_manageable": False
        })

    for trans in markup_registry.get_transformers():
        t_id = getattr(trans, "PLUGIN_ID", trans.__class__.__name__.lower().replace("transformer", ""))
        name = getattr(trans, "DISPLAY_NAME", t_id.upper())
        plugins.append({
            "id": t_id,
            "name": name,
            "category": "transformer",
            "category_name": "🛠️ 资产加工",
            "status": "Active",
            "is_in_use": True,
            "is_enabled": True,
            "origin": "core",
            "version": getattr(trans, "VERSION", SYSTEM_TRACK),
            "description": getattr(trans, "DESCRIPTION", f"物理加工单元 ({name})。"),
            "is_manageable": False
        })

    for m_id in markup_registry._maskers.keys():
        masker = markup_registry.get_masker(m_id)
        name = getattr(masker, "DISPLAY_NAME", m_id.upper())
        plugins.append({
            "id": m_id,
            "name": name,
            "category": "masker",
            "category_name": "🛡️ 安全防护",
            "status": "Shielded",
            "is_in_use": True,
            "is_enabled": True,
            "origin": "core",
            "version": getattr(masker, "VERSION", SYSTEM_TRACK),
            "description": getattr(masker, "DESCRIPTION", f"隐私脱敏引擎 ({name})。"),
            "is_manageable": False
        })

    for step in StepRegistry.get_all_names():
        step_cls = StepRegistry.get_step(step)
        is_active = (step == "staticizer" and engine.config.ingress_settings.staticize_components) or (step == "seo" and engine.config.seo_settings.enabled) or True
        display_name = getattr(step_cls, "DISPLAY_NAME", step.upper())
        plugins.append({
            "id": step,
            "name": display_name,
            "category": "editorial",
            "category_name": "🧬 流程审计",
            "status": "In-Use" if is_active else "Standby",
            "is_in_use": is_active,
            "is_enabled": True,
            "origin": "core",
            "version": getattr(step_cls, "VERSION", SYSTEM_TRACK),
            "description": getattr(step_cls, "DESCRIPTION", f"主权出版流水线 '{display_name}' 核心步骤。"),
            "is_manageable": False
        })

    for p in plugins:
        renderer_cls = SSGRegistry.get_renderer("sovereign" if p["id"] == "default" else ("generic" if p["id"] == "universal" else p["id"])) if p["category"] == "theme" else None
        if renderer_cls:
            p["name"] = getattr(renderer_cls, "DISPLAY_NAME", p["id"].upper())
            p["description"] = getattr(renderer_cls, "DESCRIPTION", p["description"])
        if "name" not in p: p["name"] = p["id"].upper()
    return plugins
