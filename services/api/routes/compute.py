# -*- coding: utf-8 -*-
"""
🚀 [V66.5] 算力治理路由 - Sovereign Compute Management (Dispatch Hub)
职责：负责算力节点的物理配置更新、连通性探测与热重载调度中枢。
🛡️ [SOP-01 & SOP-02]：已原子化物理拆分至 compute_shards/ 分片，彻底消除大单体红线。
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, Request

from core.runtime.engine_singleton import get_global_engine
from core.utils.event_bus import bus
from .system import verify_token
from .compute_shards import (
    list_compute_nodes_logic,
    update_compute_node_logic,
    delete_node_logic,
    switch_primary_node_logic,
    switch_fallback_node_logic,
    probe_compute_logic,
    test_node_connectivity_logic,
    get_node_models_logic,
)

router = APIRouter(prefix="/api/compute", tags=["Compute"])


@router.get("/probe", dependencies=[Depends(verify_token)])
def probe_compute() -> Dict[str, Any]:
    """🚀 [V76.0] 实时嗅探本地算力（LM Studio / Ollama）与本地凭据环境"""
    return probe_compute_logic()


@router.get("/nodes", dependencies=[Depends(verify_token)])
def list_compute_nodes() -> Dict[str, Any]:
    """🚀 [V66.5] 枚举物理底座中的算力节点"""
    return list_compute_nodes_logic()


@router.post("/nodes/update", dependencies=[Depends(verify_token)])
async def update_compute_node(req: dict) -> Dict[str, Any]:
    """🚀 [V66.5] 新增或更新物理算力底座配置"""
    return await update_compute_node_logic(req)


@router.post("/nodes/delete", dependencies=[Depends(verify_token)])
async def delete_node(request: Request) -> Dict[str, Any]:
    """🪓 [算力移除] 从物理底座中永久抹除算力节点"""
    return await delete_node_logic(request)


@router.post("/nodes/test", dependencies=[Depends(verify_token)])
async def test_node_connectivity(req: dict) -> Dict[str, Any]:
    """执行算力节点连通性物理探针"""
    return await test_node_connectivity_logic(req)


@router.get("/models", dependencies=[Depends(verify_token)])
async def get_node_models(node_id: str, provider: str = None, api_key: str = None, base_url: str = None, proxy: str = None) -> Dict[str, Any]:
    """🚀 [V66.5] 动态模型发现：实时从算力节点获取可用模型列表"""
    return await get_node_models_logic(node_id, provider=provider, api_key=api_key, base_url=base_url, proxy=proxy)


@router.post("/primary/switch", dependencies=[Depends(verify_token)])
async def switch_primary_node(req: dict) -> Dict[str, Any]:
    """热切换主算力节点"""
    return await switch_primary_node_logic(req)


@router.post("/fallback/switch", dependencies=[Depends(verify_token)])
async def switch_fallback_node(req: dict) -> Dict[str, Any]:
    """热切换备用算力节点"""
    return await switch_fallback_node_logic(req)


__all__ = [
    "router",
    "probe_compute",
    "list_compute_nodes",
    "update_compute_node",
    "delete_node",
    "test_node_connectivity",
    "get_node_models",
    "switch_primary_node",
    "switch_fallback_node",
    "get_global_engine",
    "bus",
]
