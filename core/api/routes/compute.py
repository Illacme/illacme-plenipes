# -*- coding: utf-8 -*-
"""
🚀 [V52.10] 算力治理路由 - Sovereign Compute Management
职责：负责算力节点的物理配置更新、连通性探测与热重载调度。
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from core.runtime.cli_bootstrap import get_global_engine
from .system import verify_token
from core.config.models.ai import TranslationProvider
from core.utils.tracing import tlog
from core.utils.event_bus import bus
import time
import asyncio
import os

router = APIRouter(prefix="/api/compute", tags=["Compute"])

@router.get("/nodes", dependencies=[Depends(verify_token)])
def list_compute_nodes():
    """枚举所有已配置的算力节点"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    config = engine.config.translation
    nodes = []
    for node_id, provider in config.providers.items():
        nodes.append({
            "id": node_id,
            "type": provider.type,
            "provider": getattr(provider, 'provider', provider.type),
            "model": provider.model,
            "base_url": provider.base_url,
            "enabled": getattr(provider, 'enabled', True), # 🚀 [V54.1] 透传物理启用状态
            "is_primary": node_id == config.primary_node,
            "is_fallback": node_id == config.fallback_node
        })
    
    # 🚀 [V52.18] 优先级对正：主算力节点与备选节点物理置顶
    nodes.sort(key=lambda x: (not x["is_primary"], not x["is_fallback"], x["id"]))
    
    return {"nodes": nodes, "primary": config.primary_node}

@router.post("/nodes/update", dependencies=[Depends(verify_token)])
async def update_compute_node(req: dict):
    """新增或更新算力节点配置"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    node_id = req.get("id")
    if not node_id: raise HTTPException(status_code=400, detail="Missing node id")
    
    # 物理注入
    try:
        new_provider = TranslationProvider(**req)
        engine.config.translation.providers[node_id] = new_provider
        
        # 持久化对正
        from core.governance.imprint_manager import im
        from core.config.config import CONFIG_IMPRINT_NAME, CONFIG_DIR, CONFIG_LOCAL_NAME, IMPRINT_DIR
        active_imprint = im.get_active_imprint()
        path = os.path.join(IMPRINT_DIR, active_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME)
        engine.config.dump_to_disk(path)
        engine.config.dump_to_disk(CONFIG_LOCAL_NAME)
        
        tlog.info(f"🛰️ [算力更新] 节点 '{node_id}' 配置已同步至物理磁盘。")
        return {"success": True, "node": req}
    except Exception as e:
        tlog.error(f"🛑 [算力更新失败] 数据格式错误: {e}")
        return {"success": False, "error": str(e)}

@router.post("/nodes/delete", dependencies=[Depends(verify_token)])
async def delete_node(request: Request):
    """🪓 [算力移除] 从当前主权配置中物理抹除指定的算力节点"""
    data = await request.json()
    node_id = data.get("id")
    
    if not node_id:
        return {"success": False, "error": "Missing node_id"}
        
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    providers = engine.config.translation.providers
    
    if node_id not in providers:
        return {"success": False, "error": "Node not found"}
        
    if node_id == engine.config.translation.primary_node:
        return {"success": False, "error": "Cannot delete active primary node. Switch primary first."}
        
    # 物理抹除
    del providers[node_id]
    
    # 固化变更
    from core.governance.imprint_manager import im
    from core.config.config import CONFIG_IMPRINT_NAME, CONFIG_DIR, CONFIG_LOCAL_NAME, IMPRINT_DIR
    active_imprint = im.get_active_imprint()
    engine.config.dump_to_disk(os.path.join(IMPRINT_DIR, active_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME))
    engine.config.dump_to_disk(CONFIG_LOCAL_NAME)
    
    tlog.warning(f"🪓 [算力移除] 节点 '{node_id}' 已从主权矩阵中抹除。")
    return {"success": True}

@router.post("/nodes/test", dependencies=[Depends(verify_token)])
async def test_node_connectivity(req: dict):
    """执行算力节点连通性物理探针"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    node_id = req.get("id")
    if not node_id: return {"error": "Missing node id"}
    
    # 🚀 [V53.1] 支持实时配置覆盖测试
    from core.config.models.ai import TranslationSettings
    config_override = req.get("config")
    if config_override:
        try:
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
        # 1. 动态构建临时翻译器 (不影响主引擎状态)
        from core.logic.ai.ai_factory import TranslatorFactory
        translator = TranslatorFactory._build_node(node_id, trans_cfg)
        
        # 🚀 [V55.1] 使用标准化的连通性探针 (通常是模型发现)，避免浪费 Token
        success, message = await translator.test_connection()
        
        latency = int((time.time() - start_time) * 1000)
        
        if success:
            tlog.success(f"✅ [探测成功] 节点 '{node_id}' 响应正常，延迟: {latency}ms")
            return {"status": "success", "latency": latency, "message": message}
        else:
            return {"status": "failed", "error": message}

            
    except asyncio.TimeoutError:
        return {"status": "failed", "error": "Connection Timeout (15s)"}
    except Exception as e:
        tlog.error(f"🛑 [探测异常] 节点 '{node_id}' 响应异常: {e}")
        return {"status": "error", "error": str(e)}

@router.get("/models", dependencies=[Depends(verify_token)])
async def get_node_models(node_id: str, provider: str = None, api_key: str = None, base_url: str = None):
    """🚀 [V53.2] 动态模型发现：实时从算力节点获取可用模型列表"""
    from core.adapters.ai.registry import AIProviderRegistry
    
    engine = get_global_engine()
    # 优先使用传入参数，否则从引擎配置中读取
    target_provider = provider
    target_key = api_key
    target_url = base_url
    
    if engine and node_id in engine.config.translation.providers:
        node_cfg = engine.config.translation.providers[node_id]
        target_provider = target_provider or node_cfg.type or node_cfg.provider
        target_key = target_key or node_cfg.api_key
        target_url = target_url or node_cfg.base_url
        
    if not target_provider:
        return {"models": []}
        
    p_cls = AIProviderRegistry.get_provider(target_provider)
    if not p_cls: return {"models": []}
    
    try:
        target_url = target_url or getattr(p_cls, "DEFAULT_URL", "")
        # 🚀 [V53.8] 工业级 Mock：构造具备完整生命周期的配置镜像
        from types import SimpleNamespace
        
        mock_limits = SimpleNamespace(max_concurrency=1, timeout=10)
        mock_node = SimpleNamespace(
            base_url=target_url,
            url=target_url,
            api_key=target_key,
            type=target_provider,
            limits=mock_limits,
            proxy=None
        )
        
        mock_config = SimpleNamespace(
            base_url=target_url,
            api_key=target_key,
            model='discovery',
            api_timeout=10,
            max_retries=1,
            providers={node_id: mock_node}
        )
        
        translator = p_cls(node_id, mock_config)
        models = await translator.list_models()
        return {"models": models}
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        tlog.warning(f"⚠️ [模型发现失败] 节点 '{node_id}' ({target_provider}): {e}\n{error_detail}")
        return {"models": [], "error": str(e)}

@router.post("/primary/switch", dependencies=[Depends(verify_token)])
async def switch_primary_node(req: dict):
    """热切换主算力节点"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    node_id = req.get("node_id")
    if node_id not in engine.config.translation.providers:
        return {"error": "Target node not found in providers matrix"}
        
    old_primary = engine.config.translation.primary_node
    engine.config.translation.primary_node = node_id
    
    # 持久化
    from core.governance.imprint_manager import im
    active_imprint = im.get_active_imprint()
    from core.config.config import CONFIG_IMPRINT_NAME, CONFIG_DIR, CONFIG_LOCAL_NAME, IMPRINT_DIR
    engine.config.dump_to_disk(os.path.join(IMPRINT_DIR, active_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME))
    engine.config.dump_to_disk(CONFIG_LOCAL_NAME)
    
    # 4. 热重载通知 (EventBus)
    # 🔔 修正：EventBus.emit 使用关键字参数传递 payload
    bus.emit("CONFIG_RELOADED", config=engine.config)
    
    tlog.success(f"🔄 [算力对正] 主算力节点已从 '{old_primary}' 切换至 '{node_id}'")
    return {"success": True, "new_primary": node_id}
