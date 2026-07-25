# -*- coding: utf-8 -*-
"""
📡 Dispatch Hub API Shard - Vault Routes (稿件感知与出版管线调度分片)
职责：承载稿件状态扫描、离线预览调起、强制重出版、物理销毁及待同步感知路由。
"""

from fastapi import APIRouter, Depends, HTTPException
from ..system import verify_token
from core.runtime.engine_singleton import get_global_engine

# 引入中枢逻辑代理层
from services.api.logic.dispatch_ops import (
    get_dispatch_status_facade,
    toggle_lab_facade,
    trigger_re_dispatch_facade,
    destroy_artifact_facade,
    get_pending_syndication_facade
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

@router.get("/api/vault/pending-syndication", dependencies=[Depends(verify_token)])
async def get_pending_syndication():
    """
    📡 获取待同步至分发渠道的稿件信息（用于前端同步自愈引导）
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return get_pending_syndication_facade(engine)

from pydantic import BaseModel
import os
import sys
import subprocess

class OpenFolderReq(BaseModel):
    rel_path: str

@router.post("/api/vault/open-local-folder", dependencies=[Depends(verify_token)])
async def open_local_folder(req: OpenFolderReq):
    """
    📂 物理一键唤醒本机 Finder / 资源管理器定位并高亮聚焦产物文件/目录
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    root_dir = engine.project_root if hasattr(engine, 'project_root') else os.getcwd()
    rel = (req.rel_path or '').strip().lstrip("/")
    
    target_path = os.path.abspath(os.path.join(root_dir, rel))
    exists = os.path.exists(target_path)
    
    try:
        if sys.platform == 'darwin':
            if exists and not os.path.isdir(target_path):
                subprocess.run(['open', '-R', target_path], check=False)
            else:
                target_dir = target_path if os.path.isdir(target_path) else os.path.dirname(target_path)
                os.makedirs(target_dir, exist_ok=True)
                subprocess.run(['open', target_dir], check=False)
        elif sys.platform == 'win32':
            if exists and not os.path.isdir(target_path):
                subprocess.run(['explorer', '/select,', target_path], check=False)
            else:
                target_dir = target_path if os.path.isdir(target_path) else os.path.dirname(target_path)
                os.makedirs(target_dir, exist_ok=True)
                os.startfile(target_dir)
        else:
            target_dir = target_path if os.path.isdir(target_path) else os.path.dirname(target_path)
            os.makedirs(target_dir, exist_ok=True)
            subprocess.run(['xdg-open', target_dir], check=False)
        return {"status": "ok", "opened_path": target_path}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
