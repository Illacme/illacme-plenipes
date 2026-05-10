"""
🛡️ 治理路由 — RESTful API 治理与审计端点。
提供主权契约校验、许可证状态查询与审计报告的 API 接口。
"""
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from typing import Optional, List
import os
from core.runtime.cli_bootstrap import get_global_engine
from .system import verify_token
from core.config.config import CONFIG_NAME, CONFIG_LOCAL_NAME, IMPRINT_DIR, CONFIG_DIR, CONFIG_IMPRINT_NAME

from core.utils.tracing import tlog
from core.utils.event_bus import bus

router = APIRouter()

@router.get("/api/system/context", dependencies=[Depends(verify_token)])
def get_system_context():
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    # 🚀 [V50.3] 提取全量治理上下文
    from core.governance.imprint_manager import im
    from core import __version__
    from core.ui.delegate import DisplayDelegate
    
    # 获取 AI 信息 (安全脱敏)
    ai_cfg = engine.config.translation
    active_node = ai_cfg.primary_node
    active_provider = "Unknown"
    active_model = ai_cfg.primary_model or "Unknown"
    
    if active_node in ai_cfg.compute_nodes:
        node_cfg = ai_cfg.compute_nodes[active_node]
        active_provider = (getattr(node_cfg, "type", "") or "Unknown").upper()

    # 🚀 [V52.5] 主权解耦：明确区分品牌身份与装帧主题
    from core.governance.imprint_manager import im
    active_imprint = im.get_active_imprint()
    
    # 主题友好名映射
    theme_map = {
        "default": "Sovereign (default)",
        "starlight": "Starlight (official)",
        "docusaurus": "Docusaurus (classic)",
        "vitepress": "VitePress (next)",
        "nextra": "Nextra (docs)"
    }
    raw_theme = engine.active_theme
    display_theme = theme_map.get(raw_theme, f"Custom ({raw_theme})")

    # 🚀 [V52.11] 依赖环境审计：检测是否需要 npm install
    needs_install = False
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    if os.path.exists(os.path.join(theme_dir, "package.json")):
        if not os.path.exists(os.path.join(theme_dir, "node_modules")):
            needs_install = True

    context = {
        "version": __version__,
        "active_imprint": active_imprint,
        "active_theme": display_theme,
        "raw_theme": raw_theme,
        "engine_status": "Optimal",
        "imprint_count": len(im.list_imprints()),
        "needs_install": needs_install
    }

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
    import os
    path = CONFIG_NAME
    if level == "local":
        path = CONFIG_LOCAL_NAME
    elif level == "imprint":
        # 🚀 [V52.22] 跨主权访问：支持获取指定 Imprint 的配置
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
    
    # 🚀 [V52.18] 全量治理感知：聚合所有物理与逻辑层级的插件化能力
    from core.adapters.egress.ssg.registry import SSGRegistry
    from core.adapters.egress.publishers.base import PublisherRegistry
    from core.adapters.ai.registry import AIProviderRegistry
    from core.markup.manager import MarkupManager
    
    SYSTEM_TRACK = "V24.0"
    p_cfg = engine.config.plugins
    disabled = p_cfg.disabled_plugins
    active_theme = engine.config.active_theme
    
    plugins = []
    
    # 0. 🏗️ Imprint 设施 (Imprint Infrastructure)
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
    
    # 1. 🎨 装帧主题治理 (Theme Governance)
    from core.config.config import THEMES_DIR
    local_theme_root = os.path.join(engine.config.system.data_root, THEMES_DIR)
    global_theme_root = os.path.join(os.getcwd(), THEMES_DIR)
    
    theme_ids = set()
    
    # 1.1 探测版图本地主题 (Local Themes)
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

    # 1.2 探测全局主题中心 (Global Theme Center)
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

    # 1.3 内核原生适配器兜底
    for adapter in ["docusaurus", "starlight", "sovereign", "vitepress", "nextra"]:
        if adapter in theme_ids: continue
        is_active = (active_theme == adapter)
        plugins.append({
            "id": adapter, "category": "theme", "category_name": "🎨 装帧主题",
            "status": "In-Use" if is_active else "Native",
            "is_in_use": is_active, "is_enabled": (adapter not in disabled),
            "origin": "core", "location": "native", "version": SYSTEM_TRACK,
            "description": f"内核原生适配器：驱动 {adapter.upper()} 工业级排版引擎。"
        })
        
    # 2. 🚀 发布与托管能力治理 (Egress & Hosting Governance)
    
    # 2.1 🌐 全站托管基础设施 (Hosting Infrastructure)
    # 专门处理 GitHub Pages, S3, Vercel 等全站托管渠道
    hosting_ids = ["github_pages", "cloudflare_pages", "s3", "ftp", "vercel", "netlify"]
    for p_id in hosting_ids:
        # 探测配置状态
        p_cfg_obj = getattr(engine.config.publish_control, "direct_upload", {})
        is_in_use = False
        if isinstance(p_cfg_obj, dict) and p_id in p_cfg_obj:
            is_in_use = p_cfg_obj[p_id].get("enabled", False)
        
        is_enabled = (p_id not in disabled)
        plugins.append({
            "id": p_id, "category": "hosting", "category_name": "🌐 全站托管基础设施",
            "status": "In-Use" if is_in_use else ("Active" if is_enabled else "Disabled"),
            "is_in_use": is_in_use, "is_enabled": is_enabled,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"全站静态托管：将装帧主题生成的产物发布至 {p_id.upper()}。"
        })

    # 2.2 内核原生分发渠道
    for name in PublisherRegistry.list_active_targets():
        if name in hosting_ids: continue # 已由托管分类处理
        if any(p["id"] == name for p in plugins): continue
        is_enabled = (name not in disabled)
        plugins.append({
            "id": name, "category": "publisher", "category_name": "🚀 多维分发矩阵",
            "status": "In-Use" if is_enabled else "Disabled",
            "is_in_use": is_enabled, "is_enabled": is_enabled,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"内核发布网关：同步资产至 {name.upper()} 节点。"
        })

    # 2.3 外部扩展插件 (External Plugins)
    from core.utils.plugin_loader import PluginLoader
    from plugins.publishers.base import BasePublisher
    plugin_pub_dir = os.path.join(os.getcwd(), "plugins", "publishers")
    if os.path.exists(plugin_pub_dir):
        discovered = PluginLoader.load_plugins(plugin_pub_dir, BasePublisher)
        for p_cls in discovered:
            p_id = getattr(p_cls, "PLUGIN_ID", p_cls.__name__.lower())
            
            # 🛑 [物理拦截] Webhook 已升级为聚合网关，不再以原子形式展示
            if p_id == "webhook": continue
            
            if any(p["id"] == p_id for p in plugins): continue
            
            # 探测配置状态
            p_cfg_obj = getattr(engine.config.publish_control, "direct_upload", {})
            is_in_use = False
            if isinstance(p_cfg_obj, dict) and p_id in p_cfg_obj:
                is_in_use = p_cfg_obj[p_id].get("enabled", False)
            
            is_enabled = (p_id not in disabled)
            plugins.append({
                "id": p_id, "category": "publisher", "category_name": "🚀 分发渠道",
                "status": "In-Use" if is_in_use else ("Active" if is_enabled else "Disabled"),
                "is_in_use": is_in_use, "is_enabled": is_enabled,
                "origin": "user", "version": SYSTEM_TRACK,
                "description": f"外部发布插件：驱动 {p_id.upper()} 渠道的内容分发。"
            })

    # 2.3 🚀 聚合能力容器 (Aggregated Capability Containers)
    # A. Webhook 网关
    webhook_gateway = {
        "id": "webhook_gateway", "type": "container", "category": "publisher", "category_name": "🚀 分发渠道",
        "status": "Ready", "is_in_use": False, "is_enabled": True, "origin": "core", "version": "V2.0",
        "description": "多通道 Webhook 发布网关：聚合管理所有物理分发端点。",
        "sub_items": []
    }
    for w_id, w_def in engine.config.publish_control.webhook_registry.items():
        endpoint = engine.config.publish_control.webhook_endpoints.get(w_id)
        is_ready = endpoint is not None and endpoint.enabled
        is_in_use = (w_id in engine.config.publish_control.active_webhook_ids) and is_ready
        from urllib.parse import urlparse
        domain = urlparse(endpoint.url).netloc if is_ready else "待授权"
        webhook_gateway["sub_items"].append({
            "id": w_id, "name": w_def.name, "target": domain, "is_in_use": is_in_use,
            "status": "In-Use" if is_in_use else ("Ready" if is_ready else "Blueprint")
        })
    if webhook_gateway["sub_items"]:
        in_use_count = sum(1 for s in webhook_gateway["sub_items"] if s["is_in_use"])
        webhook_gateway["status"] = f"{in_use_count} 通道服役"
        webhook_gateway["is_in_use"] = in_use_count > 0
        plugins.append(webhook_gateway)

    # 2.3 🚀 [Identity Multiplexing] 多维主权治理
    # 将所有分发节点按物理类型归类，实现“单实例原子化，多实例容器化”
    syndication_groups = {} # platform_type -> list of (id, cfg)
    known_platforms = ["devto", "medium", "ghost", "wordpress", "hashnode", "linkedin"]
    
    for s_id, s_cfg in engine.config.syndication.items():
        if not isinstance(s_cfg, dict): continue
        p_type = s_cfg.get("platform")
        if not p_type:
            for kp in known_platforms:
                if kp in s_id.lower():
                    p_type = kp
                    break
        p_type = p_type or s_id
        if p_type not in syndication_groups: syndication_groups[p_type] = []
        syndication_groups[p_type].append((s_id, s_cfg))

    for p_type, instances in syndication_groups.items():
        # 判定逻辑：WordPress 强制容器化，其他平台仅在多实例时容器化
        should_be_container = (p_type == "wordpress" or p_type == "ghost" or len(instances) > 1)
        
        if should_be_container:
            gateway = {
                "id": f"{p_type}_gateway", "type": "container", "category": "publisher", "category_name": "🚀 多维分发矩阵",
                "status": "Ready", "is_in_use": False, "is_enabled": True, "origin": "core", "version": "V2.0",
                "description": f"{p_type.upper()} 矩阵网关：聚合管理多个物理分发节点。",
                "sub_items": []
            }
            for inst_id, inst_cfg in instances:
                is_active = inst_cfg.get("enabled", False)
                target = inst_cfg.get("url", inst_cfg.get("username", "Account Node"))
                gateway["sub_items"].append({
                    "id": inst_id, "name": inst_id.upper(), "target": target, "is_in_use": is_active,
                    "status": "In-Use" if is_active else "Ready"
                })
            in_use_count = sum(1 for s in gateway["sub_items"] if s["is_in_use"])
            gateway["status"] = f"{in_use_count} 节点活跃"
            gateway["is_in_use"] = in_use_count > 0
            plugins.append(gateway)
        else:
            # 保持原子卡片的极致简洁
            inst_id, inst_cfg = instances[0]
            is_active = inst_cfg.get("enabled", False)
            plugins.append({
                "id": inst_id, "type": "atomic", "category": "publisher", "category_name": "🚀 多维分发矩阵",
                "status": "In-Use" if is_active else "Ready",
                "is_in_use": is_active, "is_enabled": True, "origin": "core", "version": SYSTEM_TRACK,
                "description": f"{p_type.upper()} 直连节点：同步资产至该平台内容生态。",
                "platform": p_type
            })
    
    # 3. 🛰️ 算力驱动 (AI Protocols)
    seen_providers = set()
    for p_id in AIProviderRegistry.get_all_protocols():
        p_cls = AIProviderRegistry.get_provider(p_id)
        if not p_cls or p_cls in seen_providers:
            continue
        seen_providers.add(p_cls)
        
        # 🚀 [V67.5] 权威对正：优先使用插件声明的 ID，而非注册别名
        canonical_id = getattr(p_cls, "PLUGIN_ID", p_id)
        
        is_enabled = (canonical_id not in disabled)
        # 探测当前是否有节点正在使用此协议
        is_in_use = any(getattr(n, 'type', '').lower() == canonical_id.lower() for n in engine.config.translation.compute_nodes.values())
        
        display_name = getattr(p_cls, "DISPLAY_NAME", canonical_id.title())
        proto_family = getattr(p_cls, "PROTOCOL_FAMILY", "native")
        default_url = getattr(p_cls, "DEFAULT_URL", "")
        
        plugins.append({
            "id": canonical_id,
            "name": display_name,
            "protocol_family": proto_family,
            "default_url": default_url,
            "category": "protocol", "category_name": "🛰️ 算力驱动",
            "status": "In-Use" if is_in_use else ("Active" if is_enabled else "Disabled"),
            "is_in_use": is_in_use, "is_enabled": is_enabled,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"AI 算力协议驱动：内核原生支持通过 {display_name} 协议调度远程或本地算力资源。"
        })

    # 4. 📥 输入感应 (Ingress Dialects & Sources)
    from core.ingress.registry import ingress_registry
    # 4.1 语法方言
    for d in ingress_registry.list_dialects():
        is_in_use = (d in p_cfg.ingress_dialects)
        is_enabled = (d not in disabled)
        plugins.append({
            "id": d, "category": "ingress", "category_name": "📥 输入感应",
            "status": "In-Use" if is_in_use else ("Active" if is_enabled else "Disabled"),
            "is_in_use": is_in_use, "is_enabled": is_enabled,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"语法方言适配器：内核原生支持感应并解析 {d.upper()} 格式的原始笔记。"
        })
    
    # 4.2 物理数据源
    active_source = getattr(engine.config.ingress_settings, "source_type", "local")
    for s in ingress_registry.list_sources():
        is_in_use = (s == active_source)
        is_enabled = (s not in disabled)
        plugins.append({
            "id": s, "category": "ingress", "category_name": "📥 输入感应",
            "status": "In-Use" if is_in_use else ("Active" if is_enabled else "Disabled"),
            "is_in_use": is_in_use, "is_enabled": is_enabled,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"物理数据源适配器：驱动 {s.upper()} 节点的原始资产采集。"
        })

    # 5. 🛠️ 资产加工 (Transformers)
    for t_name in MarkupManager._TRANSFORMER_MAP.keys():
        is_in_use = (t_name in p_cfg.markup_transformers)
        is_enabled = (t_name not in disabled)
        plugins.append({
            "id": t_name, "category": "transformer", "category_name": "🛠️ 资产加工",
            "status": "In-Use" if is_in_use else ("Active" if is_enabled else "Disabled"),
            "is_in_use": is_in_use, "is_enabled": is_enabled,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"标记转换网关：内核原生执行 {t_name.replace('_', ' ').upper()} 逻辑的语义变换。"
        })

    # 6. 🛡️ 安全防护 (Maskers)
    for m_name in MarkupManager._MASKER_MAP.keys():
        is_in_use = (m_name in p_cfg.security_maskers)
        is_enabled = (m_name not in disabled)
        plugins.append({
            "id": m_name, "category": "masker", "category_name": "🛡️ 安全防护",
            "status": "In-Use" if is_in_use else ("Active" if is_enabled else "Disabled"),
            "is_in_use": is_in_use, "is_enabled": is_enabled,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"内容脱敏卫士：对敏感信息进行 {m_name.upper()} 级别的物理屏蔽。"
        })

    # 7. 🧬 流程审计 (Pipeline Steps)
    from core.editorial.registry import StepRegistry
    for s_name in StepRegistry.get_all_names():
        is_in_use = True
        is_enabled = (s_name not in disabled)
        plugins.append({
            "id": s_name, "category": "editorial", "category_name": "🧬 流程审计",
            "status": "In-Use" if is_in_use else ("Active" if is_enabled else "Disabled"),
            "is_in_use": is_in_use, "is_enabled": is_enabled,
            "origin": "core", "version": SYSTEM_TRACK,
            "description": f"主权管线插件：执行 {s_name.replace('_', ' ').upper()} 逻辑的合规性审计。"
        })
    
    # 🚀 [排序算法]：In-Use 优先 > Enabled 优先 > ID 字母序
    plugins.sort(key=lambda p: (not p["is_in_use"], not p["is_enabled"], p["id"]))
    
    return {"plugins": plugins}
    
@router.get("/api/vault/list", dependencies=[Depends(verify_token)])
async def list_vault_manuscripts():
    """🚀 [V52.12] 资产审计接口：获取物理仓库内所有稿件的全量生命周期快照"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    # 1. 从账本获取全量快照
    docs = engine.meta.get_documents_snapshot()
    
    # 2. 物理目录补全与归一化
    vault_list = []
    for rel_path, info in docs.items():
        if not info: continue
        
        # 计算总体发布状态
        status_map = info.get("publish_status") or {}
        live_channels = [ch for ch, s in status_map.items() if s and s.get("status") == "success"]
        
        # 🛡️ [V52.13] 鲁棒性增强：防御性解析元数据
        seo_data = info.get("seo_data") or {}
        translations = info.get("translations") or {}
        zh_trans = translations.get("zh") or {}
        
        vault_list.append({
            "id": rel_path,
            "path": rel_path,
            "title": info.get("title") or os.path.basename(rel_path),
            "slug": info.get("slug") or "pending",
            "lang": info.get("source_lang") or zh_trans.get("lang") or "zh",
            "word_count": seo_data.get("word_count") or 0,
            "status": "Live" if live_channels else "Draft",
            "channels": list(status_map.keys()),
            "last_updated": max([s.get("timestamp", 0) for s in status_map.values() if s] + [0])
        })
        
    # 🚀 [排序逻辑]：按更新时间降序排列
    vault_list.sort(key=lambda x: x["last_updated"], reverse=True)
    
    return {"manuscripts": vault_list}

@router.post("/api/plugins/toggle", dependencies=[Depends(verify_token)])
async def toggle_plugin_status(req: dict):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    plugin_id = req.get("id")
    enable = req.get("enable", True)
    
    if not plugin_id: return {"error": "Missing plugin ID"}
    
    # 更新禁用名单
    current_disabled = set(engine.config.plugins.disabled_plugins)
    if enable:
        current_disabled.discard(plugin_id)
    else:
        current_disabled.add(plugin_id)
    
    engine.config.plugins.disabled_plugins = list(current_disabled)
    
    # 持久化变更
    from core.config.governance_map import get_local_config_path
    local_path = get_local_config_path()
    engine.config.dump_to_disk(local_path)
    
    return {"status": "success", "message": f"Plugin {plugin_id} {'enabled' if enable else 'disabled'}"}

@router.post("/api/intelligence/test", dependencies=[Depends(verify_token)])
async def test_llm_connectivity(req: dict):
    provider = req.get("provider")
    model = req.get("model")
    if not provider or not model: return {"error": "Missing provider or model"}
    
    # 🚀 [V52.2] 仿真连通性测试：实际调用 LLM 探针
    # 这里简单演示，实际应调用核心逻辑中的探针
    import time
    time.sleep(1) # 模拟网络延迟
    return {"status": "success", "latency": "842ms", "message": f"Successfully connected to {provider} ({model})"}

from core.config.governance_map import resolve_governance_level

@router.post("/api/config/update", dependencies=[Depends(verify_token)])
async def update_config(req: dict, imprint_id: Optional[str] = None):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    from core.config.config import CONFIG_NAME, CONFIG_LOCAL_NAME, CONFIG_IMPRINT_NAME, IMPRINT_DIR, CONFIG_DIR
    from core.config.governance_map import resolve_governance_level
    routing_groups = {
        "local": {},
        "imprint": {},
        "global": {}
    }
    
    # 1. 字段映射、注入与分流
    for key, value in req.items():
        if key == "_level": continue # 忽略过时的显式层级指令
        
        # A. 判定层级
        level = resolve_governance_level(key)
        # 如果指定了 imprint_id，则强制将所有项视为品牌级
        if imprint_id:
            level = "imprint"
            
        routing_groups[level][key] = value
        
        # B. 同步更新内存状态 (仅当更新的是当前活跃身份或全局/本地时)
        if not imprint_id or imprint_id == engine.im.get_active_imprint():
            parts = key.split('.')
            target = engine.config
            for part in parts[:-1]:
                if hasattr(target, part):
                    target = getattr(target, part)
                else:
                    target = None
                    break
            
            if target and hasattr(target, parts[-1]):
                # 特殊处理列表类型
                # 🚀 [修复] 移除过于激进的逗号自动分割逻辑，防止提示词句子被误判为列表
                # if isinstance(value, str) and ',' in value:
                #     value = [v.strip() for v in value.split(',')]

                
                # 🚀 [V55.4] 强制安全转换为 I18n 结构，并执行授权分层校验
                if key == "i18n_settings.targets" and isinstance(value, list):
                    from core.governance.license_guard import LicenseGuard
                    if not LicenseGuard.is_licensed() and len(value) > 1:
                        return {"status": "error", "error": "🛡️ [主权拦截] 社区版仅支持 1 个目标语种。开启全球矩阵分发请升级至授权版。"}
                    
                    from core.config.config_models import I18nTarget
                    from core.utils.language_hub import LanguageHub
                    new_targets = []
                    for code in value:
                        if isinstance(code, str):
                            name = LanguageHub.resolve_to_name(code)
                            iso = LanguageHub.resolve_to_iso(code)
                            new_targets.append(I18nTarget(lang_code=iso, name=name, prompt_lang=name))
                        else:
                            new_targets.append(code)
                    value = new_targets
                    # 🚀 [V55.8] 物理序列化对正：在存入持久化队列前，必须将 Pydantic 模型转换为纯 dict，防止 yaml.safe_dump 崩溃
                    routing_groups[level][key] = [t.model_dump() if hasattr(t, 'model_dump') else t for t in value]
                elif key == "i18n_settings.source.lang_code" and isinstance(value, str):
                    from core.utils.language_hub import LanguageHub
                    name = LanguageHub.resolve_to_name(value)
                    # 🚀 [V55.7] 双向同步：不仅更新内存，也同步到物理持久化堆栈
                    if hasattr(target, 'name'):
                        target.name = name
                        routing_groups[level]["i18n_settings.source.name"] = name
                    if hasattr(target, 'prompt_lang'):
                        target.prompt_lang = name
                        routing_groups[level]["i18n_settings.source.prompt_lang"] = name
                
                # 🚀 [V53.0] 强制安全转换为 Enum，防止 Pydantic 序列化警告
                if parts[-1] == "publishing_mode":
                    from core.config.models.governance import PublishingMode
                    try: value = PublishingMode(value)
                    except ValueError: pass
                elif parts[-1] == "seo_strategy":
                    from core.config.models.governance import SeoStrategy
                    try: value = SeoStrategy(value)
                    except ValueError: pass
                    
                setattr(target, parts[-1], value)

    # 2. 物理持久化分流
    import yaml
    import os
    
    # 🚀 [V55.10] 增加深度递归安全转换，彻底拦截 Pydantic 模型进入 yaml.safe_dump
    def make_yaml_safe(data):
        if hasattr(data, 'model_dump'):
            return data.model_dump()
        if isinstance(data, dict):
            return {k: make_yaml_safe(v) for k, v in data.items()}
        if isinstance(data, list):
            return [make_yaml_safe(v) for v in data]
        return data

    # 🚀 [V52.22] 物理路径确定
    target_imprint = imprint_id or engine.im.get_active_imprint()
    paths = {
        "local": CONFIG_LOCAL_NAME,
        "imprint": os.path.join(IMPRINT_DIR, target_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME) if target_imprint else None,
        "global": CONFIG_NAME
    }
    
    file_data = {}
    for level, path in paths.items():
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    file_data[level] = yaml.safe_load(f) or {}
            except:
                file_data[level] = {}
        else:
            file_data[level] = {}

    # 3. 执行分流合并与“高层清理”
    dirty_levels = set()
    for level, fields in routing_groups.items():
        if not fields: continue
        
        # A. 将更新写入目标层级
        dest_data = file_data[level]
        for k, v in fields.items():
            k_parts = k.split('.')
            d = dest_data
            for p in k_parts[:-1]:
                if p not in d: d[p] = {}
                d = d[p]
            d[k_parts[-1]] = make_yaml_safe(v) # 🛡️ 安全转换
            dirty_levels.add(level)
            
            # B. 🛡️ 主权清理：如果更新的是低层级 (imprint)，且没有指定特定 id (即更新当前)，则从高层级 (local) 中删除该项
            if level == "imprint" and not imprint_id:
                local_data = file_data["local"]
                ld = local_data
                for p in k_parts[:-1]:
                    if p in ld and isinstance(ld[p], dict):
                        ld = ld[p]
                    else:
                        ld = None
                        break
                if ld and k_parts[-1] in ld:
                    del ld[k_parts[-1]]
                    dirty_levels.add("local")
                    tlog.info(f"🛡️ [主权清理] 已从 local 层移除覆盖项: {k}")

    # 4. 物理落盘
    for level, path in paths.items():
        if not path or level not in dirty_levels: continue
        try:
            dir_path = os.path.dirname(path)
            if dir_path: os.makedirs(dir_path, exist_ok=True)
            
            # 🚀 [V55.12] 最终全量扫描转换，防止残留模型
            safe_to_save = make_yaml_safe(file_data[level])
            
            with open(path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(safe_to_save, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            tlog.error(f"❌ 物理落盘失败: {path} - {str(e)}")
            
    # 🚀 [V52.22] 如果更新的是当前激活配置，确保属性同步、路径重新锚定并广播信号
    if not imprint_id or imprint_id == engine.im.get_active_imprint():
        # 🚀 [V55.12] 物理对正补丁：在执行 Factory 逻辑前，必须先同步投影属性
        engine.active_theme = engine.config.active_theme
        engine.vault_root = engine.config.vault_root
        
        # 🚀 [V55.13] 主题物理同步逻辑：如果目标主题仅存在于全局中心，则自动复制到版图本地
        if "active_theme" in req:
            theme_id = req["active_theme"]
            from core.config.config import THEMES_DIR
            local_theme_path = os.path.join(engine.config.system.data_root, THEMES_DIR, theme_id)
            global_theme_path = os.path.join(os.getcwd(), THEMES_DIR, theme_id)
            
            if not os.path.exists(local_theme_path) and os.path.exists(global_theme_path):
                tlog.info(f"🏗️ [主题安装] 正在将主题 '{theme_id}' 从全局中心物理同步至当前版图...")
                try:
                    import shutil
                    os.makedirs(os.path.dirname(local_theme_path), exist_ok=True)
                    shutil.copytree(
                        global_theme_path,
                        local_theme_path,
                        dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('node_modules', '.git', '.DS_Store', '__pycache__', 'dist', 'build', '.astro', '.docusaurus', '.next')
                    )
                    tlog.success(f"✅ [同步完成] 主题 '{theme_id}' 已成功固化至版图本地。")
                except Exception as e:
                    tlog.error(f"❌ [同步失败] 无法复制主题资产: {str(e)}")
            
            # 🚀 [V56.0] 意图感知对正：通过适配器协议获取目标主题的最佳物理布局
            from core.adapters.egress.ssg import SSGAdapter
            from core.config.config import ThemeSettings
            
            # 临时实例化目标适配器以嗅探其物理契约
            temp_settings = ThemeSettings(name=theme_id)
            temp_adapter = SSGAdapter(temp_settings, engine=engine)
            slots = temp_adapter.get_feature_slots()
            
            is_i18n = engine.config.i18n_settings.enable_multilingual and len(engine.config.i18n_settings.targets) > 0
            
            # 自动对齐输出矩阵中的关键出口
            from core.config.config import THEMES_DIR
            if hasattr(engine.config, "output_paths"):
                for slot_id, slot_cfg in slots.items():
                    rel_path = slot_cfg["multi" if is_i18n else "single"]
                    # 物理对正：主题相关路径必须锚定在 themes/{theme_id} 之下
                    abs_target = os.path.join(THEMES_DIR, theme_id, rel_path)
                    
                    # 🚀 [V56.7] 命名美学对正：docs -> docs_dir (正式废弃 markdown_dir)
                    field_name = f"{slot_id}_dir"
                    engine.config.output_paths[field_name] = abs_target
                    tlog.debug(f"🛰️ [意图感知] 已对齐出口 '{slot_id}' -> {abs_target}")

            tlog.info(f"🛰️ [路径对正] 引擎主题切换: {theme_id} (保持既有金库主权: {engine.config.vault_root})")
        
        from core.runtime.engine_factory import EngineFactory
        EngineFactory._init_paths_and_adapters(engine)
        
        from core.config.config import CONFIG_NAME, CONFIG_LOCAL_NAME, CONFIG_IMPRINT_NAME, IMPRINT_DIR, CONFIG_DIR
        
        # 🚀 [V55.22] 物理持久化：主权路径智能解析
        if engine.imprint_id and engine.imprint_id != "default":
            # 品牌主权层：imprints/[id]/configs/config.imprint.yaml
            config_path = os.path.join(IMPRINT_DIR, engine.imprint_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
        else:
            # 环境物理层：config.local.yaml (遵循原则：不篡改 config.yaml 基座)
            config_path = CONFIG_LOCAL_NAME
            
        try:
            import yaml
            # 1. 尝试读取原始物理文件以执行“外科手术式”更新
            current_raw = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    current_raw = yaml.safe_load(f) or {}
            
            # 2. 仅同步更新受治理的主权路径字段，避免全局配置膨胀
            current_raw["active_theme"] = engine.config.active_theme
            current_raw["vault_root"] = engine.config.vault_root
            
            if "output_paths" not in current_raw: current_raw["output_paths"] = {}
            
            # 🚀 [V56.7] 精准治理：仅同步标准命名槽位
            governed_fields = ["docs_dir", "blog_dir", "pages_dir", "static_dir"]
            for field in governed_fields:
                if field in engine.config.output_paths:
                    val = engine.config.output_paths[field]
                    # 解析占位符
                    if isinstance(val, str) and "{theme}" in val:
                        val = val.replace("{theme}", theme_id)
                    
                    current_raw["output_paths"][field] = val
                    tlog.debug(f"💾 [精准存档] 同步出口: {field} -> {val}")

            # 3. 物理回写：保持物理文件的精简与主权纯粹
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(current_raw, f, allow_unicode=True, sort_keys=False)
                
            tlog.success(f"💾 [主权存档] 路径对正信息已精准同步至 {config_path}")
        except Exception as e:
            tlog.error(f"❌ [存档失败] 无法更新 config.imprint.yaml: {str(e)}")
        
        # 🚀 [V55.12] 全量广播：通知所有治理守卫、AI 调度器及前端感知组件
        from core.utils.event_bus import bus
        bus.emit("CONFIG_RELOADED", config=engine.config)
        tlog.info(f"🛰️ [主权同步] 已完成 '{engine.active_theme}' 主题的运行时全量对齐与广播。")
            
    return {"status": "success", "active_config": engine.config.model_dump()}

@router.post("/api/themes/bootstrap", dependencies=[Depends(verify_token)])
async def bootstrap_theme(req: dict):
    """🚀 [V55.14] 主题物理自愈：从官方通道自动初始化缺失的主题资产"""
    theme_id = req.get("id")
    if not theme_id: return {"status": "error", "message": "Missing theme ID"}
    
    import subprocess
    import os
    import shutil
    
    from core.config.config import THEMES_DIR
    global_theme_root = os.path.join(os.getcwd(), THEMES_DIR)
    target_path = os.path.join(global_theme_root, theme_id)
    
    if os.path.exists(target_path):
        return {"status": "error", "message": f"物理资产已存在: {theme_id}"}

    # 🚀 [V55.15] 针对不同引擎的官方引导指令 (增强非交互模式支持)
    bootstrap_cmds = {
        "starlight": f"npx -y create-astro@latest {theme_id} --template starlight --no-install --no-git --yes",
        "docusaurus": f"npx -y create-docusaurus@latest {theme_id} classic --skip-install",
        "vitepress": f"mkdir -p {theme_id} && cd {theme_id} && npm init -y && npm install -D vitepress",
        "nextra": f"npx -y create-nextra-app@latest {theme_id} --example docs"
    }
    
    cmd = bootstrap_cmds.get(theme_id)
    if not cmd:
        return {"status": "error", "message": f"引擎 '{theme_id}' 尚不支持自动物理引导，请手动放置资产。"}

    tlog.info(f"🏗️ [物理自愈] 正在启动主题 '{theme_id}' 的官方引导程序...")
    bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"📡 [系统感知] 正在从官方通道拉取 {theme_id.upper()} 物理资产...")

    try:
        os.makedirs(global_theme_root, exist_ok=True)
        
        # 🛡️ 增加环境变量以强制非交互模式
        env = os.environ.copy()
        env["CI"] = "true"
        
        process = subprocess.Popen(
            cmd, shell=True, cwd=global_theme_root,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            env=env
        )
        
        full_output = []
        for line in process.stdout:
            clean_line = line.strip()
            if clean_line:
                full_output.append(clean_line)
                bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"  [CLI] {clean_line}")
        
        process.wait()
        
        if process.returncode == 0:
            # 🚀 [V55.20] Docusaurus 特殊物理补全：防止 i18n 导致的 docs 缺失报错
            if theme_id == "docusaurus":
                docs_path = os.path.join(target_path, "docs")
                if not os.path.exists(docs_path):
                    os.makedirs(docs_path, exist_ok=True)
                    with open(os.path.join(docs_path, "intro.md"), "w", encoding="utf-8") as f:
                        f.write("# Welcome\n\nThis is your sovereign documentation site.")
            
            tlog.success(f"✅ [引导成功] 主题 '{theme_id}' 物理资产已就绪。")
            return {"status": "success", "message": f"主题 {theme_id} 初始化完成。"}
        else:
            err_msg = "\n".join(full_output[-3:]) # 抓取最后三行错误
            return {"status": "error", "message": f"引导程序失败 (Code: {process.returncode}): {err_msg}"}
            
    except Exception as e:
        tlog.error(f"❌ [自愈失败] 无法执行初始化: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.post("/api/publish/trigger", dependencies=[Depends(verify_token)])
async def trigger_publish(req: dict):
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    try:
        mode = req.get("mode", "static")
        theme = req.get("theme", engine.config.active_theme)
        
        # 🚀 [V51.0] 异步出版流水线：调用 Orchestrator 助手
        from core.runtime.orchestrator import start_asynchronous_sync
        is_dry_run = mode == "dry-run"
        is_sandbox = mode == "sandbox"
        
        tlog.info(f"📡 [API] 收到全量出版指令 (Mode: {mode})")
        task_id = start_asynchronous_sync(engine, dry_run=is_dry_run, sandbox=is_sandbox)
        
        if task_id is None:
            return {"status": "error", "message": "出版任务已在运行中，请勿重复点火。"}
            
        return {"status": "task_queued", "task_id": task_id}
    except Exception as e:
        import traceback
        err_detail = traceback.format_exc()
        tlog.error(f"🚨 [API] 全量出版点火失败: {str(e)}\n{err_detail}")
        return {"status": "error", "message": f"引擎点火失败: {str(e)}"}

@router.get("/api/imprints/stats", dependencies=[Depends(verify_token)])
def get_imprints_stats():
    """🚀 [V52.22] 跨品牌资产大盘与环境健康统计"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    from core.governance.imprint_manager import im
    from core.governance.env_sentry import sentry
    imprints = im.list_imprints()
    
    stats = {}
    for imp in imprints:
        imp_id = imp["id"]
        # 🚀 [V65.4] 物理路径对正：imp["path"] 是金库(Vault)路径，资产账本位于版图(Imprint)根目录
        from core.config.config import IMPRINT_DIR
        actual_imp_path = os.path.join(os.getcwd(), IMPRINT_DIR, imp_id) if imp_id != "default" else os.getcwd()
        
        # 1. 探测活跃主题 (用于资产统计与审计豁免)
        active_theme = "default"
        config_path = os.path.join(actual_imp_path, CONFIG_DIR, CONFIG_IMPRINT_NAME)
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    c = yaml.safe_load(f) or {}
                    active_theme = c.get("active_theme", "default")
            except: pass

        # 2. 资产统计 (Metadata DB)
        # 🚀 [V65.4] 锚定物理根目录进行查找
        from core.config.config import METADATA_DIR
        meta_db = os.path.join(actual_imp_path, METADATA_DIR, "themes", active_theme, "ledger.db")
        doc_count = 0
        if os.path.exists(meta_db):
            import sqlite3
            try:
                conn = sqlite3.connect(meta_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM documents")
                doc_count = cursor.fetchone()[0]
                conn.close()
            except: pass
            
        health = sentry.check_isolation_health(actual_imp_path, theme=active_theme)
        
        stats[imp_id] = {
            "doc_count": doc_count,
            "isolation": health["isolation_level"],
            "healthy": health["has_local_toolchain"]
        }
    return stats

@router.get("/api/imprints", dependencies=[Depends(verify_token)])
def list_imprints():
    from core.governance.imprint_manager import im
    return {"imprints": im.list_imprints(), "active": im.get_active_imprint()}

@router.post("/api/imprints/add", dependencies=[Depends(verify_token)])
async def add_imprint(req: dict):
    from core.governance.imprint_manager import im
    name = req.get("name")
    path = req.get("path")
    press_name = req.get("press_name")
    if not name or not path: return {"error": "Missing name or path"}
    
    success = im.init_sovereign_imprint(name, path, press_name)
    return {"success": success}

@router.post("/api/imprints/switch", dependencies=[Depends(verify_token)])
async def switch_imprint(req: dict):
    from core.governance.imprint_manager import im
    from core.runtime.cli_bootstrap import deep_reload_imprint
    
    imprint_id = req.get("imprint_id")
    if not imprint_id: return {"error": "Missing imprint_id"}
    
    # 🚀 [V52.6] 执行深度主权迁移 (热重载引擎与监控器)
    success = deep_reload_imprint(imprint_id)
    if success:
        im.switch(imprint_id)
        return {"success": True, "active": imprint_id}
    else:
        return {"success": False, "error": "引擎深度重载失败，请检查终端日志。"}

@router.post("/api/imprints/delete", dependencies=[Depends(verify_token)])
async def delete_imprint(req: dict):
    from core.governance.imprint_manager import im
    name = req.get("name")
    if not name: return {"error": "Missing name"}
    
    success = im.delete_imprint(name)
    return {"success": success}

@router.post("/api/plugins/probe", dependencies=[Depends(verify_token)])
async def probe_plugin(req: dict):
    engine = get_global_engine()
    plugin_id = req.get("id")
    if not plugin_id: return {"success": False, "error": "Missing plugin id"}
    
    tlog.info(f"📡 [治理探测] 正在对组件 [{plugin_id}] 执行物理链路审计...")
    
    # 1. 🌐 探测全站托管与分发渠道 (Hosting & Publishers)
    if hasattr(engine, 'deployment_manager'):
        # 先在活跃实例中查找
        for pub in engine.deployment_manager.publishers:
            p_id = getattr(pub, "PLUGIN_ID", pub.__class__.__name__.lower().replace("publisher", "").replace("plugin", ""))
            if p_id == plugin_id:
                is_ok = pub.is_healthy()
                return {"success": True, "healthy": is_ok, "id": plugin_id}
        
        # 如果未在活跃实例中，检查是否属于已知分发渠道
        known_publishers = ["github_pages", "cloudflare_pages", "s3", "ftp", "vercel", "netlify", "devto", "medium", "ghost", "wordpress", "hashnode", "linkedin", "webhook"]
        if plugin_id in known_publishers:
            return {"success": True, "healthy": False, "error": "组件未激活：请在配置中启用该分发节点以执行物理联通性探测。"}

    # 2. 🎨 探测装帧主题 (Themes)
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(os.getcwd(), THEMES_DIR, plugin_id)
    if os.path.exists(theme_dir) or plugin_id in ["default", "docusaurus", "starlight", "sovereign", "vitepress", "nextra"]:
        return {"success": True, "healthy": True, "id": plugin_id}
        
    # 3. 🧠 探测智能算力 (Processor / AI)
    from core.adapters.ai.registry import AIProviderRegistry
    ai_nodes = engine.config.translation.compute_nodes if hasattr(engine.config, 'translation') else {}
    
    # 逻辑：如果是协议名 (如 openai)，则探测当前正在使用该协议的节点
    target_node = ai_nodes.get(plugin_id)
    if not target_node:
        # 尝试协议反向搜索 (如通过 'openai' 找使用 openai 协议的第一个节点)
        for n_id, n_cfg in ai_nodes.items():
            if n_cfg.type == plugin_id:
                target_node = n_cfg
                break
    
    if target_node or plugin_id in AIProviderRegistry.get_all_protocols():
        if target_node:
            has_key = target_node.api_key and len(target_node.api_key) > 10 and "your" not in target_node.api_key.lower()
            if target_node.type in ["ollama", "lmstudio", "local"]: has_key = True
            if not has_key:
                return {"success": True, "healthy": False, "error": "算力凭据缺失或仍处于占位符状态。"}
            return {"success": True, "healthy": True, "id": plugin_id}
        else:
            return {"success": True, "healthy": False, "error": "协议未绑定：未在物理底座中发现任何节点使用该 AI 协议。"}

    # 4. 📥 输入、加工与审计 (Ingress / Transformer / Masker / Editorial)
    # 动态查询内核注册中心，确保所有内部组件均可探测
    from core.ingress.registry import ingress_registry
    from core.markup.manager import MarkupManager
    from core.editorial.registry import StepRegistry
    
    if plugin_id in ingress_registry.list_dialects() or plugin_id in ingress_registry.list_sources():
        return {"success": True, "healthy": True, "id": plugin_id}
        
    if plugin_id in MarkupManager._TRANSFORMER_MAP or plugin_id in MarkupManager._MASKER_MAP:
        return {"success": True, "healthy": True, "id": plugin_id}
        
    if plugin_id in StepRegistry.get_all_names():
        return {"success": True, "healthy": True, "id": plugin_id}
        
    # 兜底硬编码匹配 (针对一些特殊的虚拟 ID)
    if plugin_id in ["mdx", "local", "obsidian", "standard_md", "editorial", "audit"]:
        return {"success": True, "healthy": True, "id": plugin_id}
    
    return {"success": False, "error": f"该组件 [{plugin_id}] 尚未实装物理自检协议。"}


from pydantic import BaseModel
from fastapi import Request
class StyleRequest(BaseModel):
    style: str

@router.post("/api/config/style")
async def apply_translation_style(req: StyleRequest, request: Request):
    from core.governance.imprint_manager import im
    import shutil
    
    imprint_id = request.headers.get("Imprint-Id")
    target_imprint = imprint_id or im.get_active_imprint()
    if not target_imprint:
        return {"status": "error", "message": "No active imprint"}
        
    from core.config.config import PROMPTS_NAME, DIALECTS_DIR, DEFAULT_DIALECT_NAME, CONFIG_DIR, PROMPTS_TEMPLATES_DIR
    source_template = os.path.join(os.getcwd(), CONFIG_DIR, PROMPTS_TEMPLATES_DIR, f"{req.style}.yaml")
    if not os.path.exists(source_template):
        return {"status": "error", "message": f"Template {req.style} not found"}
        
    from core.config.config import PROMPTS_NAME, DIALECTS_DIR, DEFAULT_DIALECT_NAME, CONFIG_DIR, CONFIG_IMPRINT_NAME, IMPRINT_DIR
    target_dir = os.path.join(im.imprint_root, target_imprint, CONFIG_DIR, DIALECTS_DIR)
    os.makedirs(target_dir, exist_ok=True)
    
    # 🚀 [V55.25] 物理资产同步：根据风格 ID 生成方言文件
    style_filename = f"{req.style}.yaml"
    target_file = os.path.join(target_dir, style_filename)
    shutil.copy2(source_template, target_file)
    
    # 同时也保持 default.yaml 为最新，作为保底
    shutil.copy2(source_template, os.path.join(target_dir, DEFAULT_DIALECT_NAME))
    
    # 🚀 [V55.25] 逻辑标识对正
    engine = get_global_engine()
    if engine:
        engine.config.translation.active_style = req.style
        
        # 持久化变更至品牌配置
        imprint_cfg_path = os.path.join(IMPRINT_DIR, target_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME)
        engine.config.dump_to_disk(imprint_cfg_path)
    
    # Also update the mother prompts in root
    mother_file = os.path.join(os.getcwd(), CONFIG_DIR, PROMPTS_NAME)
    shutil.copy2(source_template, mother_file)
    
    return {"status": "success", "style": req.style}
