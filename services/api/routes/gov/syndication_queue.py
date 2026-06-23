# -*- coding: utf-8 -*-
"""
🛡️ [V105.0] Gov Syndication Queue Administration Routes
职责：承载多渠道异步分发队列状态查询、死信任务重试与一键清空治理路由。
符合 SOP-02 物理拆分协议与 300 行复杂度红线。
"""

import os
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from core.runtime.engine_singleton import get_global_engine
from ..system import verify_token

router = APIRouter()

class QueueItemAction(BaseModel):
    """队列项操作荷载"""
    rel_path: Optional[str] = None
    target_id: Optional[str] = None

@router.get("/api/governance/syndication/queue", dependencies=[Depends(verify_token)])
async def list_syndication_queue() -> dict:
    """📡 获取分发队列里的所有任务 (包含 PENDING, FAILED)"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")
    tasks = engine.meta.list_all_syndication_tasks()
    return {"tasks": tasks}

@router.post("/api/governance/syndication/queue/retry", dependencies=[Depends(verify_token)])
async def retry_syndication_queue_task(payload: QueueItemAction) -> dict:
    """🔄 重试特定分发任务或一键重试所有失败的任务"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")
    
    # 1. 更新数据库状态
    engine.meta.retry_syndication_task(payload.rel_path, payload.target_id)
    
    # 2. 动态加载并执行立即重试，以提供极佳的响应反馈
    try:
        from core.syndication.hub import ContentSyndicator
        syndication_cfg = getattr(engine.config, "syndication", {})
        site_url = getattr(engine.config, "site_url", "")
        sys_tuning = {"vault_root": getattr(engine, "vault_root", os.getcwd())}
        
        syndicator = ContentSyndicator(
            syndication_cfg=syndication_cfg,
            site_url=site_url,
            sys_tuning_cfg=sys_tuning,
            meta=engine.meta
        )
        # 调用 process_pending_retries 立即在后台线程池中拉起重试
        syndicator.process_pending_retries()
    except Exception:
        # 降级：仅作为后台排队重试，不阻断 API 成功返回
        pass
        
    return {"success": True}

@router.post("/api/governance/syndication/queue/delete", dependencies=[Depends(verify_token)])
async def delete_syndication_queue_task(payload: QueueItemAction) -> dict:
    """🗑️ 删除特定分发任务或一键清空所有失败的任务"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")
    
    engine.meta.delete_syndication_task(payload.rel_path, payload.target_id)
    return {"success": True}
