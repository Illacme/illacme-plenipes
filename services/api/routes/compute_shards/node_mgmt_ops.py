# -*- coding: utf-8 -*-
"""
🚀 [V66.5] Compute Node Management Operations Shard
职责：负责算力节点的物理配置更新、枚举、删除与主备容灾切换。
"""

import os
from typing import Dict, Any
from fastapi import HTTPException, Request
from core.config.models.ai import ComputeNode
from core.utils.tracing import tlog


def _get_engine():
    """获取全局引擎实例，优先兼容外部对主模块的动态 patch / mock"""
    try:
        import services.api.routes.compute as parent_mod
        if hasattr(parent_mod, "get_global_engine"):
            return parent_mod.get_global_engine()
    except Exception:
        pass
    from core.runtime.engine_singleton import get_global_engine
    return get_global_engine()


def _get_bus():
    """获取事件总线实例，优先兼容外部对主模块的动态 patch / mock"""
    try:
        import services.api.routes.compute as parent_mod
        if hasattr(parent_mod, "bus"):
            return parent_mod.bus
    except Exception:
        pass
    from core.utils.event_bus import bus
    return bus


def list_compute_nodes_logic() -> Dict[str, Any]:
    """🚀 [V66.5] 枚举物理底座中的算力节点"""
    engine = _get_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    config = engine.config.translation
    nodes = []
    for node_id, node in config.compute_nodes.items():
        # 🚀 [V74.9] 物理模型感知：优先读取节点自身配置，再根据角色进行策略对齐
        display_model = getattr(node, "model", "-")
        if node_id == config.primary_node:
            display_model = config.primary_model
        elif node_id == config.fallback_node:
            display_model = config.fallback_model

        from core.adapters.ai.registry import AIProviderRegistry
        p_cls = AIProviderRegistry.get_provider(node.type)
        p_name = getattr(p_cls, "DISPLAY_NAME", node.type.title())
        proto_family = getattr(p_cls, "PROTOCOL_FAMILY", "native")

        from core.governance.health_registry import health_registry
        metrics = health_registry.get_node(node_id)
        
        nodes.append({
            "id": node_id,
            "type": node.type,
            "protocol_family": proto_family,
            "provider": node.type,
            "provider_name": p_name,
            "model": display_model,
            "base_url": node.base_url,
            "enabled": node.enabled,
            "is_primary": node_id == config.primary_node,
            "is_fallback": node_id == config.fallback_node,
            "last_updated_raw": getattr(node, "last_updated", 0),
            "health": {
                "score": round(metrics.get_score(), 1),
                "avg_latency": round(metrics.avg_latency * 1000, 0),  # 转换为 ms
                "success_rate": round(metrics.success_count / (metrics.success_count + metrics.failure_count + 1e-6) * 100, 1),
                "total_calls": metrics.success_count + metrics.failure_count
            }
        })
    
    # 🚀 [V74.9] 排序平权：按编辑时间倒序排列
    nodes.sort(key=lambda x: x.get("last_updated_raw", 0), reverse=True)
    
    return {"nodes": nodes, "primary": config.primary_node, "fallback": config.fallback_node}


async def update_compute_node_logic(req: dict) -> Dict[str, Any]:
    """🚀 [V66.5] 新增或更新物理算力底座配置"""
    engine = _get_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    node_id = req.get("id")
    if not node_id:
        raise HTTPException(status_code=400, detail="Missing node id")
    
    try:
        # 物理注入：使用新版 ComputeNode 模型
        new_node = ComputeNode(**req)
        engine.config.translation.compute_nodes[node_id] = new_node
        
        # 物理固化 (仅保存到 local_config，品牌 config 会在 dump 时自动剥离)
        from core.config.config import CONFIG_LOCAL_NAME
        engine.config.dump_to_disk(CONFIG_LOCAL_NAME)
        
        tlog.info(f"🛰️ [物理算力更新] 节点 '{node_id}' 已同步至本地环境。")
        if engine and hasattr(engine, "ledger") and engine.ledger:
            engine.ledger.log(
                event_type="PUBLISH_LAYOUT_CHANGED",
                details=f"更新或创建了算力节点 '{node_id}'，类型: {req.get('type') or '-'}",
                severity="INFO",
                actor="APIAdmin",
                metadata={"node_id": node_id, "type": req.get("type"), "model": req.get("model")}
            )
        return {"success": True, "node": req}
    except Exception as e:
        tlog.error(f"🛑 [算力更新失败] 数据格式错误: {e}")
        return {"success": False, "error": str(e)}


async def delete_node_logic(request: Request) -> Dict[str, Any]:
    """🪓 [算力移除] 从物理底座中永久抹除算力节点"""
    data = await request.json()
    node_id = data.get("id")
    
    if not node_id:
        return {"success": False, "error": "Missing node_id"}
        
    engine = _get_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    nodes = engine.config.translation.compute_nodes
    
    if node_id not in nodes:
        return {"success": False, "error": "Node not found"}
        
    if node_id == engine.config.translation.primary_node:
        return {"success": False, "error": "Cannot delete active primary node. Switch primary first."}
        
    # 物理抹除
    del nodes[node_id]
    
    from core.config.config import CONFIG_LOCAL_NAME
    engine.config.dump_to_disk(CONFIG_LOCAL_NAME)
    
    tlog.warning(f"🪓 [物理移除] 节点 '{node_id}' 已从算力底座中抹除。")
    if engine and hasattr(engine, "ledger") and engine.ledger:
        engine.ledger.log(
            event_type="PUBLISH_LAYOUT_CHANGED",
            details=f"移除了算力节点 '{node_id}'",
            severity="WARNING",
            actor="APIAdmin",
            metadata={"node_id": node_id}
        )
    return {"success": True}


async def switch_primary_node_logic(req: dict) -> Dict[str, Any]:
    """热切换主算力节点"""
    engine = _get_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    node_id = req.get("node_id")
    if node_id not in engine.config.translation.compute_nodes:
        return {"error": "Target node not found in compute nodes matrix"}
        
    engine.config.translation.primary_node = node_id
    
    # 持久化品牌策略
    from core.governance.imprint_manager import im
    active_imprint = im.get_active_imprint()
    from core.config.config import CONFIG_IMPRINT_NAME, CONFIG_DIR, IMPRINT_DIR
    engine.config.dump_to_disk(os.path.join(IMPRINT_DIR, active_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME))
    
    bus = _get_bus()
    bus.emit("CONFIG_RELOADED", config=engine.config)
    tlog.success(f"🔄 [算力对正] 主算力节点已切换至 '{node_id}'")
    if engine and getattr(engine, "ledger", None):
        engine.ledger.log(event_type="PUBLISH_LAYOUT_CHANGED", details=f"切换主算力节点至 '{node_id}'", severity="INFO", actor="APIAdmin", metadata={"node_id": node_id, "active_imprint": active_imprint})
    return {"success": True, "new_primary": node_id}


async def switch_fallback_node_logic(req: dict) -> Dict[str, Any]:
    """热切换备用算力节点"""
    engine = _get_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    node_id = req.get("node_id")
    if node_id and node_id not in engine.config.translation.compute_nodes:
        return {"error": "Target node not found in compute nodes matrix"}
        
    engine.config.translation.fallback_node = node_id
    
    # 持久化品牌策略
    from core.governance.imprint_manager import im
    active_imprint = im.get_active_imprint()
    from core.config.config import CONFIG_IMPRINT_NAME, CONFIG_DIR, IMPRINT_DIR
    engine.config.dump_to_disk(os.path.join(IMPRINT_DIR, active_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME))
    
    bus = _get_bus()
    bus.emit("CONFIG_RELOADED", config=engine.config)
    tlog.info(f"🛰️ [容灾对正] 备用算力节点调整为 '{node_id or 'NONE'}'")
    if engine and getattr(engine, "ledger", None):
        engine.ledger.log(event_type="PUBLISH_LAYOUT_CHANGED", details=f"切换备用容灾算力节点至 '{node_id or 'NONE'}'", severity="INFO", actor="APIAdmin", metadata={"node_id": node_id, "active_imprint": active_imprint})
    return {"success": True, "new_fallback": node_id}
