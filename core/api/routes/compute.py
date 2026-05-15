# -*- coding: utf-8 -*-
"""
🚀 [V66.5] 算力治理路由 - Sovereign Compute Management
职责：负责算力节点的物理配置更新、连通性探测与热重载调度。
🛡️ [Sovereignty]：已完全移除 providers 兼容逻辑，强制对正物理节点架构。
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from core.runtime.engine_singleton import get_global_engine
from .system import verify_token
from core.config.models.ai import ComputeNode
from core.utils.tracing import tlog
from core.utils.event_bus import bus
import time
import asyncio
import os

router = APIRouter(prefix="/api/compute", tags=["Compute"])

@router.get("/nodes", dependencies=[Depends(verify_token)])
def list_compute_nodes():
    """🚀 [V66.5] 枚举物理底座中的算力节点"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
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
                "avg_latency": round(metrics.avg_latency * 1000, 0), # 转换为 ms
                "success_rate": round(metrics.success_count / (metrics.success_count + metrics.failure_count + 1e-6) * 100, 1),
                "total_calls": metrics.success_count + metrics.failure_count
            }
        })
    
    # 🚀 [V74.9] 排序平权：按编辑时间倒序排列
    nodes.sort(key=lambda x: x.get("last_updated_raw", 0), reverse=True)
    
    return {"nodes": nodes, "primary": config.primary_node, "fallback": config.fallback_node}

@router.post("/nodes/update", dependencies=[Depends(verify_token)])
async def update_compute_node(req: dict):
    """🚀 [V66.5] 新增或更新物理算力底座配置"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    node_id = req.get("id")
    if not node_id: raise HTTPException(status_code=400, detail="Missing node id")
    
    try:
        # 物理注入：使用新版 ComputeNode 模型
        new_node = ComputeNode(**req)
        engine.config.translation.compute_nodes[node_id] = new_node
        
        # 物理固化 (仅保存到 local_config，品牌 config 会在 dump 时自动剥离)
        from core.config.config import CONFIG_LOCAL_NAME
        engine.config.dump_to_disk(CONFIG_LOCAL_NAME)
        
        tlog.info(f"🛰️ [物理算力更新] 节点 '{node_id}' 已同步至本地环境。")
        return {"success": True, "node": req}
    except Exception as e:
        tlog.error(f"🛑 [算力更新失败] 数据格式错误: {e}")
        return {"success": False, "error": str(e)}

@router.post("/nodes/delete", dependencies=[Depends(verify_token)])
async def delete_node(request: Request):
    """🪓 [算力移除] 从物理底座中永久抹除算力节点"""
    data = await request.json()
    node_id = data.get("id")
    
    if not node_id:
        return {"success": False, "error": "Missing node_id"}
        
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
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
    return {"success": True}

@router.post("/nodes/test", dependencies=[Depends(verify_token)])
async def test_node_connectivity(req: dict):
    """执行算力节点连通性物理探针"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    node_id = req.get("id")
    if not node_id: return {"error": "Missing node id"}
    
    # 🚀 [V66.5] 支持实时配置覆盖测试
    from core.config.models.ai import TranslationSettings
    config_override = req.get("config")
    if config_override:
        try:
            # 这里的 TranslationSettings 会包含 compute_nodes
            trans_cfg = TranslationSettings(**config_override)
            tlog.info(f"⚡ [算力探测] 正在对节点 '{node_id}' 发起 [实时动态] 连通性测试...")
        except Exception as e:
            tlog.error(f"🛑 [探测预检失败] 动态配置格式错误: {e}")
            return {"status": "error", "error": f"Invalid config: {e}"}
    else:
        trans_cfg = engine.config.translation
        tlog.info(f"⚡ [算力探测] 正在对节点 '{node_id}' 发起 [持久化] 连通性测试...")
    
    start_time = time.time()
    try:
        from core.logic.ai.ai_factory import TranslatorFactory
        translator = TranslatorFactory._build_node(node_id, trans_cfg)
        
        success, message = await translator.test_connection()
        latency = int((time.time() - start_time) * 1000)
        
        if success:
            tlog.success(f"✅ [探测成功] 节点 '{node_id}' 正常，延迟: {latency}ms")
            return {"status": "success", "latency": latency, "message": message}
        else:
            return {"status": "failed", "error": message}
            
    except Exception as e:
        tlog.error(f"🛑 [探测异常] 节点 '{node_id}' 响应异常: {e}")
        return {"status": "error", "error": str(e)}

@router.get("/models", dependencies=[Depends(verify_token)])
async def get_node_models(node_id: str, provider: str = None, api_key: str = None, base_url: str = None):
    """🚀 [V66.5] 动态模型发现：实时从算力节点获取可用模型列表"""
    from core.adapters.ai.registry import AIProviderRegistry
    
    engine = get_global_engine()
    target_provider = provider
    target_key = api_key
    target_url = base_url
    
    if engine and node_id in engine.config.translation.compute_nodes:
        node_cfg = engine.config.translation.compute_nodes[node_id]
        target_provider = target_provider or node_cfg.type
        target_key = target_key or node_cfg.api_key
        target_url = target_url or node_cfg.base_url
        
    if not target_provider: return {"models": []}
    p_cls = AIProviderRegistry.get_provider(target_provider)
    if not p_cls: return {"models": []}
    
    try:
        target_url = target_url or getattr(p_cls, "DEFAULT_URL", "")
        from types import SimpleNamespace
        
        mock_limits = SimpleNamespace(max_concurrency=1, timeout=10)
        mock_node = SimpleNamespace(
            base_url=target_url,
            api_key=target_key,
            type=target_provider,
            limits=mock_limits
        )
        
        mock_config = SimpleNamespace(
            base_url=target_url,
            api_key=target_key,
            model='discovery',
            api_timeout=10,
            max_retries=1,
            compute_nodes={node_id: mock_node}
        )
        
        translator = p_cls(node_id, mock_config)
        models = await translator.list_models()
        return {"models": models}
    except Exception as e:
        tlog.warning(f"⚠️ [模型发现失败] 节点 '{node_id}' ({target_provider}): {e}")
        return {"models": [], "error": str(e)}

@router.post("/primary/switch", dependencies=[Depends(verify_token)])
async def switch_primary_node(req: dict):
    """热切换主算力节点"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    node_id = req.get("node_id")
    if node_id not in engine.config.translation.compute_nodes:
        return {"error": "Target node not found in compute nodes matrix"}
        
    old_primary = engine.config.translation.primary_node
    engine.config.translation.primary_node = node_id
    
    # 持久化品牌策略
    from core.governance.imprint_manager import im
    active_imprint = im.get_active_imprint()
    from core.config.config import CONFIG_IMPRINT_NAME, CONFIG_DIR, IMPRINT_DIR
    path = os.path.join(IMPRINT_DIR, active_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME)
    engine.config.dump_to_disk(path)
    
    bus.emit("CONFIG_RELOADED", config=engine.config)
    tlog.success(f"🔄 [算力对正] 主算力节点已切换至 '{node_id}'")
    return {"success": True, "new_primary": node_id}

@router.post("/fallback/switch", dependencies=[Depends(verify_token)])
async def switch_fallback_node(req: dict):
    """热切换备用算力节点"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    node_id = req.get("node_id")
    if node_id and node_id not in engine.config.translation.compute_nodes:
        return {"error": "Target node not found in compute nodes matrix"}
        
    old_fallback = engine.config.translation.fallback_node
    engine.config.translation.fallback_node = node_id
    
    # 持久化品牌策略
    from core.governance.imprint_manager import im
    active_imprint = im.get_active_imprint()
    from core.config.config import CONFIG_IMPRINT_NAME, CONFIG_DIR, IMPRINT_DIR
    path = os.path.join(IMPRINT_DIR, active_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME)
    engine.config.dump_to_disk(path)
    
    bus.emit("CONFIG_RELOADED", config=engine.config)
    tlog.info(f"🛰️ [容灾对正] 备用算力节点调整为 '{node_id or 'NONE'}'")
    return {"success": True, "new_fallback": node_id}
