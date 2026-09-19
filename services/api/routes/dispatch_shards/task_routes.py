#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 [V122.0] Illacme Plenipes - Dispatch Task Management Routes
职责：全域发布任务管理与成果物权中枢 API 分片（支持总览、流水线状态、渠道健康度、死信自愈）。
🛡️ [SOP-02 模块拆分 / AEL-Iter] 单文件严格保持在 300 行以内。
"""

from typing import Dict, Any, Optional
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.runtime.engine_singleton import get_global_engine
from core.runtime.orchestrator import _is_publishing, _pending_sync_queue
from ..system import verify_token


router = APIRouter(tags=["Dispatch Tasks"])


class TaskActionPayload(BaseModel):
    rel_path: Optional[str] = None
    target_id: Optional[str] = None


@router.get("/api/dispatch/overview", dependencies=[Depends(verify_token)])
async def get_dispatch_overview() -> Dict[str, Any]:
    """🚀 [V122.0] 获取全域发布与分发任务大盘数据：统计指标、渠道健康度、死信队列与成功成果账本"""
    engine = get_global_engine()
    if not engine or not hasattr(engine, "meta"):
        return {
            "status": "warning",
            "is_publishing": False,
            "summary": {"total_syndicated": 0, "total_failed": 0, "active_count": 0},
            "channel_health": [],
            "dead_letter_tasks": [],
            "recent_records": []
        }

    # 1. 查询死信与待重试任务
    raw_tasks = engine.meta.list_all_syndication_tasks() if hasattr(engine.meta, "list_all_syndication_tasks") else []
    dead_letter_tasks = []
    if isinstance(raw_tasks, list):
        for item in raw_tasks:
            if isinstance(item, dict):
                dead_letter_tasks.append({
                    "id": item.get("id"),
                    "rel_path": item.get("rel_path", ""),
                    "target_id": item.get("target_id", ""),
                    "title": item.get("title", ""),
                    "slug": item.get("slug", ""),
                    "lang_code": item.get("lang_code", "zh-CN"),
                    "status": item.get("status", "FAILED"),
                    "last_error": item.get("last_error", "未知网络或认证异常"),
                    "retry_count": item.get("retry_count", 0),
                    "next_retry_time": item.get("next_retry_time", 0)
                })

    # 2. 查询历史成功分发物权记录
    raw_records = engine.meta.list_all_syndication_records(limit=100) if hasattr(engine.meta, "list_all_syndication_records") else []
    recent_records = []
    if isinstance(raw_records, list):
        for rec in raw_records:
            if isinstance(rec, dict):
                recent_records.append({
                    "id": rec.get("id"),
                    "rel_path": rec.get("rel_path", ""),
                    "lang_code": rec.get("lang_code", "zh-CN"),
                    "target_id": rec.get("target_id", ""),
                    "remote_article_id": rec.get("remote_article_id", ""),
                    "remote_url": rec.get("remote_url", ""),
                    "updated_at": rec.get("updated_at", "")
                })

    # 3. 统计全渠道连通性健康矩阵
    syndication_cfg = getattr(engine.config, "syndication", None) or {}
    if hasattr(syndication_cfg, "dict"):
        syndication_cfg = syndication_cfg.dict()
    elif not isinstance(syndication_cfg, dict):
        syndication_cfg = {}

    known_channels = [
        {"id": "github_pages", "name": "GitHub Pages", "icon": "🐙", "type": "hosting"},
        {"id": "cloudflare_pages", "name": "Cloudflare Pages", "icon": "⚡", "type": "hosting"},
        {"id": "vercel", "name": "Vercel", "icon": "▲", "type": "hosting"},
        {"id": "netlify", "name": "Netlify", "icon": "🌐", "type": "hosting"},
        {"id": "devto", "name": "Dev.to", "icon": "👩‍💻", "type": "social"},
        {"id": "hashnode", "name": "Hashnode", "icon": "📘", "type": "social"},
        {"id": "medium", "name": "Medium", "icon": "✍️", "type": "social"},
        {"id": "wechat", "name": "微信公众号", "icon": "🟢", "type": "social"},
        {"id": "zhihu", "name": "知乎专栏", "icon": "🔵", "type": "social"},
        {"id": "juejin", "name": "掘金社区", "icon": "💎", "type": "social"},
        {"id": "bilibili", "name": "哔哩哔哩专栏", "icon": "📺", "type": "social"},
    ]

    failed_target_ids = {t["target_id"] for t in dead_letter_tasks if t.get("status") == "FAILED"}

    channel_health = []
    for ch in known_channels:
        cid = ch["id"]
        ch_sub_cfg = syndication_cfg.get(cid, {}) if isinstance(syndication_cfg, dict) else {}
        enabled = bool(ch_sub_cfg.get("enabled", False)) if isinstance(ch_sub_cfg, dict) else False
        has_token = bool(ch_sub_cfg.get("api_token") or ch_sub_cfg.get("token") or ch_sub_cfg.get("cookie")) if isinstance(ch_sub_cfg, dict) else False
        
        if cid in failed_target_ids:
            status = "error"
            msg = "存在推送失败任务待自愈"
        elif enabled and has_token:
            status = "healthy"
            msg = "凭证就绪 · 待命状态"
        elif enabled and not has_token:
            status = "warning"
            msg = "已启用但缺少密钥或授权"
        else:
            status = "disabled"
            msg = "未配置启用"

        channel_health.append({
            **ch,
            "status": status,
            "status_msg": msg,
            "enabled": enabled
        })

    active_count = (1 if _is_publishing else 0) + len(_pending_sync_queue)

    return {
        "status": "success",
        "is_publishing": _is_publishing,
        "summary": {
            "total_syndicated": len(recent_records),
            "total_failed": len(dead_letter_tasks),
            "active_count": active_count,
            "success_rate": f"{round((len(recent_records) / max(len(recent_records) + len(dead_letter_tasks), 1)) * 100, 1)}%"
        },
        "channel_health": channel_health,
        "dead_letter_tasks": dead_letter_tasks,
        "recent_records": recent_records
    }


@router.get("/api/dispatch/tasks/active", dependencies=[Depends(verify_token)])
async def get_active_dispatch_tasks() -> Dict[str, Any]:
    """🚀 [V122.0] 查询当前正在活跃执行与排队的发布作业"""
    pending = []
    for idx, item in enumerate(_pending_sync_queue):
        if isinstance(item, dict):
            pending.append({
                "queue_index": idx + 1,
                "requested_paths": item.get("requested_paths") or ["全站所有稿件"],
                "target_langs": item.get("target_langs") or ["全部语种"],
                "dry_run": item.get("dry_run", False)
            })

    return {
        "is_publishing": _is_publishing,
        "active_pipeline": {
            "current_stage": "多渠道并发推送与成果验证" if _is_publishing else "IDLE",
            "progress_percent": 75 if _is_publishing else 100,
            "can_abort": _is_publishing
        },
        "pending_queue": pending
    }


@router.post("/api/dispatch/tasks/abort", dependencies=[Depends(verify_token)])
async def abort_dispatch_task() -> Dict[str, Any]:
    """🛑 [V122.0] 紧急中止当前正在运行的发布流水线"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=500, detail="引擎未就绪")
    
    engine.abort_sync = True
    try:
        _pending_sync_queue.clear()
    except Exception:
        pass

    try:
        from core.logic.orchestration.task_orchestrator import global_executor, ai_executor
        global_executor.cancel_all_pending()
        ai_executor.cancel_all_pending()
    except Exception:
        pass

    return {"status": "aborted", "message": "全域发布作业与排队队列已全量中止。"}


@router.post("/api/dispatch/deadletter/retry", dependencies=[Depends(verify_token)])
async def retry_deadletter_tasks(payload: TaskActionPayload) -> Dict[str, Any]:
    """🔄 [V122.0] 重试指定死信任务，或重试当前所有失败任务"""
    engine = get_global_engine()
    if not engine or not hasattr(engine, "meta") or not engine.meta:
        return {"status": "warning", "message": "引擎元数据暂不可用"}

    engine.meta.retry_syndication_task(payload.rel_path, payload.target_id)

    # 触发社媒分发重试服务异步调度
    try:
        from core.syndication.hub import ContentSyndicator
        syndication_cfg = getattr(engine.config, "syndication", {})
        if hasattr(syndication_cfg, "dict"):
            syndication_cfg = syndication_cfg.dict()
        site_url = getattr(engine.config, "site_url", "")
        sys_tuning = {"vault_root": getattr(engine, "vault_root", os.getcwd())}
        syndicator = ContentSyndicator(
            syndication_cfg=syndication_cfg,
            site_url=site_url,
            sys_tuning_cfg=sys_tuning,
            meta=engine.meta
        )
        syndicator.process_pending_retries()
    except Exception as e:
        return {"status": "success", "message": f"任务已重置为待重试状态，调度器告警: {str(e)}"}

    return {"status": "success", "message": "已将任务重置并触发后台重试管线。"}


@router.delete("/api/dispatch/deadletter/clear", dependencies=[Depends(verify_token)])
async def clear_deadletter_tasks(payload: TaskActionPayload) -> Dict[str, Any]:
    """🗑️ [V122.0] 物理清理/废弃指定死信任务，或清理所有已失败任务"""
    engine = get_global_engine()
    if not engine or not hasattr(engine, "meta") or not engine.meta:
        return {"status": "warning", "message": "引擎元数据暂不可用"}

    engine.meta.delete_syndication_task(payload.rel_path, payload.target_id)
    return {"status": "success", "message": "死信任务已移出队列。"}
