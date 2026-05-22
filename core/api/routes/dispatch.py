#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V68.0] Illacme Plenipes - Dispatch Hub API (Router Hub)
职责：仅定义资产分发状态控制路由契约，实体业务逻辑均委派至门面 dispatch_ops.py。
"""

from fastapi import APIRouter, Depends, HTTPException
from .system import verify_token
from core.runtime.engine_singleton import get_global_engine

# 引入中枢逻辑代理层
from core.api.logic.dispatch_ops import (
    get_dispatch_status_facade,
    toggle_lab_facade,
    trigger_re_dispatch_facade,
    destroy_artifact_facade
)

router = APIRouter()

@router.get("/api/vault/dispatch-status/{doc_id:path}", dependencies=[Depends(verify_token)])
async def get_dispatch_status(doc_id: str):
    """
    🛰️ 物理感应探针 (Sovereign Sensing)
    委派给 telemetry_ops 分片完成，扫描真实产物分布并还原算力、费用与节点状态。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return get_dispatch_status_facade(engine, doc_id)

@router.post("/api/vault/toggle-lab", dependencies=[Depends(verify_token)])
async def toggle_lab():
    """
    🧪 实时预览引擎物理调度 (Physical Daemon Scheduling)
    委派给 daemon_ops 分片完成，在后台线程中拉起/关闭 DevServer。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return toggle_lab_facade(engine)

@router.post("/api/vault/re-dispatch/{doc_id:path}", dependencies=[Depends(verify_token)])
async def trigger_re_dispatch(doc_id: str, req: dict):
    """
    ♻️ 主权调度中心：强制推入出版管线
    委派给 pipeline_ops 分片完成，提交任务至异步线程池。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return trigger_re_dispatch_facade(engine, doc_id, req)

@router.delete("/api/vault/destroy/{doc_id:path}", dependencies=[Depends(verify_token)])
async def destroy_artifact(doc_id: str):
    """
    🗑️ 物理销毁逻辑：抹除磁盘资产及其所有出版产物，并在账本中彻底注销
    委派给 pipeline_ops 分片完成，自愈清理多级空目录。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return destroy_artifact_facade(engine, doc_id)
