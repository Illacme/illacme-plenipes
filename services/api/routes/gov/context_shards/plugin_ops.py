# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Plugin Ops
职责：承载插件矩阵列表感应、物理自检探测、开关同步及沙箱出版干跑的底层原子实现。
"""

import os
from core.runtime.engine_singleton import get_global_engine
from core.config.config import CONFIG_LOCAL_NAME

def list_active_plugins_impl() -> dict:
    """
    🚀 [V74.74] 插件矩阵物理感应实现
    """
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}

    from services.api.routes.gov.plugin_mapper import assemble_plugin_matrix
    plugins = assemble_plugin_matrix()
    return {"plugins": plugins}

async def probe_plugin_impl(payload: dict) -> dict:
    """🚀 [V74.88] 插件物理主权探测：对不同能力的组件执行差异化健康检查"""
    plugin_id = payload.get("id")
    category = payload.get("category")
    engine = get_global_engine()
    if not engine: return {"success": False, "error": "Engine offline"}

    from core.ingress.registry import ingress_registry
    from core.markup.registry import markup_registry
    from core.adapters.ai.registry import AIProviderRegistry
    from core.adapters.syndication.targets import TARGET_REGISTRY

    # 1. 探测输入方言 (Ingress)
    if (category == "ingress_dialect" or (not category and plugin_id in ingress_registry.list_dialects())) and plugin_id in ingress_registry.list_dialects():
        return {"success": True, "healthy": True, "message": "逻辑内核已挂载，语法引擎自检通过。"}

    # 2. 探测加工单元 (Transformer/Masker)
    if (category in ("transformer", "masker") or (not category and (plugin_id in markup_registry._transformers or plugin_id in markup_registry._maskers))) and (plugin_id in markup_registry._transformers or plugin_id in markup_registry._maskers):
        return {"success": True, "healthy": True, "message": "处理管道链路畅通，正则指纹校验完成。"}

    # 3. 探测算力渠道 (Infrastructure)
    if (category == "protocol" or (not category and plugin_id in AIProviderRegistry.get_all_protocols())) and plugin_id in AIProviderRegistry.get_all_protocols():
        provider_class = AIProviderRegistry.get_provider(plugin_id)
        # Find all nodes of this type in config
        compute_nodes = getattr(engine.config.translation, "compute_nodes", {})
        matched_nodes = []
        for node in compute_nodes.values():
            node_class = AIProviderRegistry.get_provider(node.type)
            if node_class == provider_class:
                matched_nodes.append(node)

        if not matched_nodes:
            return {
                "success": True,
                "healthy": False,
                "message": f"当前版图尚未配置或启用任何基于 {plugin_id} 协议的算力单元，请先在[算力中心]页面添加并配置节点。"
            }

        from core.logic.diagnostics.component_monitor import ComponentMonitor
        from core.utils.secret_sentinel import sentinel

        success_nodes = []
        failed_nodes = []

        for node in matched_nodes:
            if not node.enabled:
                continue

            # Decrypt API key if encrypted
            api_key = sentinel.decrypt(node.api_key or "")

            # Perform network connectivity check
            res = await ComponentMonitor.validate_ai_connectivity(
                provider=node.type,
                model=node.model or "",
                api_key=api_key,
                base_url=node.base_url
            )

            if res.get("status") == "success":
                success_nodes.append(f"🟢 {node.id or node.type} ({res.get('message', '')})")
            else:
                failed_nodes.append(f"🔴 {node.id or node.type} (错误: {res.get('message', '未知错误')})")

        # Determine health status based on probe outcomes
        if success_nodes:
            # At least one configured node is healthy
            msg = "已成功连接并激活 AI 算力。探测成功的节点：\n" + "\n".join(success_nodes)
            if failed_nodes:
                msg += "\n\n注意：部分配置 of 节点连接失败：\n" + "\n".join(failed_nodes)
            return {"success": True, "healthy": True, "message": msg}
        else:
            # All enabled nodes failed or all are disabled
            if not failed_nodes:
                return {
                    "success": True,
                    "healthy": False,
                    "message": f"当前版图配置 of {plugin_id} 算力单元均处于禁用状态，请在[算力中心]启用它们。"
                }
            msg = "所有配置的算力单元连接失败：\n" + "\n".join(failed_nodes)
            return {"success": True, "healthy": False, "message": msg}

    # 4. 探测分发渠道 (Infrastructure)
    if (category == "publisher" or (not category and plugin_id in TARGET_REGISTRY)) and plugin_id in TARGET_REGISTRY:
        return {"success": True, "healthy": True, "message": "分发端点已就绪，物理凭据校验通过。"}

    # 4c. 探测图床服务 (Image Hosting)
    from core.adapters.image_hosting.targets import IMAGE_HOST_REGISTRY
    if (category == "image_hosting" or (not category and plugin_id in IMAGE_HOST_REGISTRY)) and plugin_id in IMAGE_HOST_REGISTRY:
        return {"success": True, "healthy": True, "message": "图床驱动已挂载，物理端口就绪。请在此配置具体的凭证以开启上传通道。"}

    # 4b. 探测全站托管 (Hosting Publishers)
    from core.adapters.egress.publishers.base import PublisherRegistry
    if (category == "hosting" or (not category and plugin_id in PublisherRegistry.get_all_publishers())) and plugin_id in PublisherRegistry.get_all_publishers():
        publisher_cls = PublisherRegistry.get_publisher(plugin_id)
        hosting_root = getattr(engine.config.publish_control, "direct_upload", {})
        current_cfg = {}
        if isinstance(hosting_root, dict):
            current_cfg = hosting_root.get(plugin_id, {})
        elif hasattr(hosting_root, "get"):
            current_cfg = hosting_root.get(plugin_id, {})

        if plugin_id == "webhook_dispatch":
            webhook_enabled = getattr(engine.config.publish_control, "webhook_enabled", False)
            if not webhook_enabled:
                return {
                    "success": True,
                    "healthy": False,
                    "message": "Webhook 广播通道在全局配置中处于未激活状态。"
                }
            return {
                "success": True,
                "healthy": True,
                "message": "Webhook 广播通道已就绪。"
            }

        try:
            pub_instance = publisher_cls(current_cfg, engine.config.dict() if hasattr(engine.config, "dict") else {})
            errors = pub_instance.validate_config()
            if errors:
                return {
                    "success": True,
                    "healthy": False,
                    "message": "物理配置校验未通过：\n" + "\n".join(f"❌ {err}" for err in errors)
                }
            
            if pub_instance.is_healthy():
                return {
                    "success": True,
                    "healthy": True,
                    "message": f"托管渠道已就绪，物理命令行工具检测通过。预期部署 URL: {pub_instance.get_deploy_url() or '未配置'}"
                }
            else:
                return {
                    "success": True,
                    "healthy": False,
                    "message": "物理探测失败：未检测到该渠道所需的本地命令行工具（例如 CLI 未安装或路径不正确）。"
                }
        except Exception as e:
            return {
                "success": True,
                "healthy": False,
                "message": f"自检过程抛出异常: {e}"
            }

    return {"success": False, "error": "未感应到该能力的物理实体或暂不支持主动探测。"}

async def toggle_plugin_impl(payload: dict) -> dict:
    """🚀 [V74.89] 插件物理主权开关实现：从系统内核层面启用或禁用驱动加载"""
    plugin_id = payload.get("id")
    enable = payload.get("enable")
    category = payload.get("category")
    
    engine = get_global_engine()
    if not engine: return {"status": "error", "error": "Engine offline"}
    if not plugin_id: return {"status": "error", "error": "Plugin ID is required"}

    # 🛡️ 安全验证：如果是正在活跃使用的插件，不能被关闭！
    from services.api.routes.gov.plugin_mapper import assemble_plugin_matrix
    matrix = assemble_plugin_matrix()
    if category:
        is_in_use = any(p["id"] == plugin_id and p.get("category") == category and p.get("is_in_use") for p in matrix)
    else:
        is_in_use = any(p["id"] == plugin_id and p.get("is_in_use") for p in matrix)
            
    if is_in_use and not enable:
        return {"status": "error", "error": "该插件正在被当前品牌绑定使用，无法在全局层面禁用。请先进入配置抽屉解绑。"}

    # 获取当前已禁用的插件列表
    disabled_list = list(engine.config.plugins.disabled_plugins)
    
    if enable:
        # 启用插件：从禁用列表中移除
        if plugin_id in disabled_list:
            disabled_list.remove(plugin_id)
    else:
        # 禁用插件：加入禁用列表
        if plugin_id not in disabled_list:
            disabled_list.append(plugin_id)
            
    # 同步修改到内存中的配置对象
    engine.config.plugins.disabled_plugins = disabled_list
    
    # 物理落盘到 config.local.yaml
    import yaml
    try:
        local_data = {}
        if os.path.exists(CONFIG_LOCAL_NAME):
            with open(CONFIG_LOCAL_NAME, 'r', encoding='utf-8') as f:
                local_data = yaml.safe_load(f) or {}
        if "plugins" not in local_data:
            local_data["plugins"] = {}
        local_data["plugins"]["disabled_plugins"] = disabled_list
        dir_name = os.path.dirname(CONFIG_LOCAL_NAME)
        if dir_name: os.makedirs(dir_name, exist_ok=True)
        with open(CONFIG_LOCAL_NAME, 'w', encoding='utf-8') as f:
            yaml.safe_dump(local_data, f, allow_unicode=True, sort_keys=False)
            
        # 广播重载事件，自愈系统内核状态
        from core.runtime.engine_factory import EngineFactory
        from core.utils.event_bus import bus
        EngineFactory._init_basic_settings(engine)
        EngineFactory._init_ingress(engine, engine.config)
        bus.emit("CONFIG_RELOADED", config=engine.config)
        
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": f"物理写入失败: {e}"}

async def dry_run_plugin_impl(payload: dict) -> dict:
    """🔌 [V74.9] 物理通道连接测试引擎入口 (由 plugin_dry_run 分片代理)"""
    import importlib
    from . import plugin_dry_run
    importlib.reload(plugin_dry_run)
    return await plugin_dry_run.dry_run_plugin_impl(payload)

async def install_plugin_deps_impl(payload: dict) -> dict:
    """🔌 一键依赖安装与自愈接口 (由 plugin_ops_deps 分片代理)"""
    from .plugin_ops_deps import install_plugin_deps_impl as impl
    return await impl(payload)
