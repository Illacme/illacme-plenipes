# -*- coding: utf-8 -*-
"""
📡 Dispatch Hub API Shard - Vault Routes (稿件感知与出版管线调度分片)
职责：承载稿件状态扫描、离线预览调起、强制重出版、物理销毁及待同步感知路由。
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
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
async def get_dispatch_status(doc_id: str, lang_code: Optional[str] = Query(None)):
    """
    🛰️ 物理感应探针 (Sovereign Sensing)
    委派给 telemetry_ops 分片完成，扫描真实产物分布并还原算力、费用与节点状态。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return get_dispatch_status_facade(engine, doc_id, lang_code=lang_code)

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

class RemoteActionReq(BaseModel):
    rel_path: str
    lang_code: str = 'zh'
    target_id: str
    action: str  # 'delete' or 'unlink'

@router.get("/api/syndication/records/{doc_id:path}", dependencies=[Depends(verify_token)])
async def get_syndication_records(doc_id: str, lang_code: str = None):
    """
    🛰️ 全渠道分发物权账本查询接口：获取文档的远程文章 ID 与公网 URL
    """
    engine = get_global_engine()
    if not engine: raise HTTPException(status_code=503, detail="Engine not initialized")
    if hasattr(engine, 'meta') and engine.meta:
        records = engine.meta.list_syndication_records_for_doc(doc_id, lang_code)
        return {"ok": True, "records": records}
    return {"ok": True, "records": []}

@router.post("/api/syndication/remote-action", dependencies=[Depends(verify_token)])
async def handle_remote_syndication_action(req: RemoteActionReq):
    """
    🗑️ 全渠道文章生命周期物权控制：远程下架 (delete) 或本地解绑 (unlink)
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    syndicator = getattr(engine, 'syndication', None)
    if not syndicator:
        from core.syndication.hub import ContentSyndicator
        syndication_cfg = getattr(engine.config, 'syndication', None) or {}
        if hasattr(syndication_cfg, 'dict'):
            syndication_cfg = syndication_cfg.dict()

        site_url = getattr(getattr(engine.config, 'publishing', None), 'site_url', '') or ''
        sys_tuning = getattr(engine.config, 'system_tuning', None) or {}
        if hasattr(sys_tuning, 'dict'):
            sys_tuning = sys_tuning.dict()

        syndicator = ContentSyndicator(
            syndication_cfg=syndication_cfg,
            site_url=site_url,
            sys_tuning_cfg=sys_tuning,
            meta=getattr(engine, 'meta', None)
        )

    if req.action == "delete":
        res = syndicator.delete_remote_article(req.rel_path, req.lang_code, req.target_id)
        return res
    elif req.action == "unlink":
        res = syndicator.unlink_remote_article(req.rel_path, req.lang_code, req.target_id)
        return res
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported action: {req.action}")

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
            if exists:
                subprocess.Popen(['open', '-R', target_path])
            else:
                subprocess.Popen(['open', os.path.dirname(target_path)])
        elif sys.platform == 'win32':
            if exists:
                subprocess.Popen(['explorer', '/select,', target_path])
            else:
                subprocess.Popen(['explorer', os.path.dirname(target_path)])
        else:
            subprocess.Popen(['xdg-open', os.path.dirname(target_path)])
        return {"ok": True, "path": target_path}
    except Exception as e:
        return {"ok": False, "error": str(e)}
