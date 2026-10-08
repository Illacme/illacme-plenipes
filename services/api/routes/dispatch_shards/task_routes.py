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
from core.syndication.syndication_diagnostic import diagnose_syndication_error
from core.utils.language_data import SUPPORTED_MATRIX
from ..system import verify_token


router = APIRouter(tags=["Dispatch Tasks"])


class TaskActionPayload(BaseModel):
    rel_path: Optional[str] = None
    target_id: Optional[str] = None
    lang_code: Optional[str] = None


_HOSTING_ICON_MAP = {
    "cloudflare_pages": "☁️",
    "github_pages": "🐱",
    "gitee_pages": "🚩",
    "gitlab_pages": "🦊",
    "vercel": "▲",
    "netlify": "💠",
    "zeabur": "⛵",
    "render": "🟣",
    "railway": "🚂",
    "firebase": "🔥",
    "sftp": "🖥️",
}


def _get_channel_registry_map() -> Dict[str, Dict[str, str]]:
    """🛰️ 统一从底层插件驱动注册中心动态检索全量渠道官方名称与图标 (SSOT)"""
    cmap = {}
    try:
        from core.adapters.egress.publishers.base import PublisherRegistry
        for pid, cls in PublisherRegistry.get_all_publishers().items():
            if pid not in {"webhook_dispatch", "aliyun_oss", "tencent_cos", "s3", "upyun_uss"}:
                icon = getattr(cls, "ICON", None) or _HOSTING_ICON_MAP.get(pid, "🌐")
                cmap[pid] = {
                    "id": pid,
                    "name": getattr(cls, "DISPLAY_NAME", None) or pid.upper(),
                    "icon": icon,
                    "type": "hosting"
                }
    except Exception:
        pass
    try:
        from core.adapters.syndication.targets import TARGET_REGISTRY
        for tid, tcls in TARGET_REGISTRY.items():
            cmap[tid] = {
                "id": tid,
                "name": getattr(tcls, "DISPLAY_NAME", None) or tid.upper(),
                "icon": getattr(tcls, "ICON", None) or "📡",
                "type": "social"
            }
    except Exception:
        pass
    return cmap


def _resolve_lang_meta(code: str) -> Dict[str, str]:
    """解析语种标准母语名称与图标"""
    if not code: return {"name": "简体中文", "icon": "🇨🇳"}
    clean = str(code).strip().lower()
    if clean in ("zh-hans", "zh-cn", "zh"): return {"name": "简体中文", "icon": "🇨🇳"}
    if clean in ("zh-hant", "zh-tw", "zh-hk"): return {"name": "繁體中文", "icon": "🇭🇰"}
    base = clean.split("-")[0].split("_")[0]
    for item in SUPPORTED_MATRIX:
        if item["code"].lower() in (clean, base): return {"name": item["name"], "icon": item["icon"]}
    return {"name": code.upper(), "icon": "🌐"}


def _extract_doc_title(engine: Any, rel_path: str, docs_snapshot: Optional[Dict[str, Any]] = None) -> str:
    """提取原稿文档人类可读的真实标题，带 SEO 属性与文件名回退"""
    if not rel_path:
        return ""
    info = (docs_snapshot.get(rel_path) if isinstance(docs_snapshot, dict) else None)
    if not info and hasattr(engine, "meta") and hasattr(engine.meta, "get_doc_info"):
        info = engine.meta.get_doc_info(rel_path)
    base_name = os.path.splitext(os.path.basename(rel_path))[0]
    if isinstance(info, dict):
        title = info.get("title")
        seo_data = info.get("seo_data") or {}
        if (not title or title == base_name) and isinstance(seo_data, dict) and seo_data.get("title"):
            title = seo_data.get("title")
        if title:
            return str(title)
    return base_name


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

    docs_snapshot = engine.meta.get_documents_snapshot() if hasattr(engine.meta, "get_documents_snapshot") else {}
    channel_map = _get_channel_registry_map()

    # 1. 查询死信与待重试任务
    raw_tasks = engine.meta.list_all_syndication_tasks() if hasattr(engine.meta, "list_all_syndication_tasks") else []
    dead_letter_tasks = []
    if isinstance(raw_tasks, list):
        for item in raw_tasks:
            if isinstance(item, dict):
                tid = item.get("target_id", "")
                rel_p = item.get("rel_path", "")
                l_code = item.get("lang_code", "zh-CN")
                lerr = item.get("last_error", "未知网络或认证异常")
                diag = diagnose_syndication_error(tid, lerr) if tid else {}
                real_title = item.get("title") or _extract_doc_title(engine, rel_p, docs_snapshot)
                ch_info = channel_map.get(tid, {})
                l_info = _resolve_lang_meta(l_code)
                dead_letter_tasks.append({
                    "id": item.get("id"), "rel_path": rel_p, "target_id": tid,
                    "target_type": ch_info.get("type", "social"), "target_name": ch_info.get("name", tid), "target_icon": ch_info.get("icon", "🏷️"),
                    "title": real_title, "slug": item.get("slug", ""), "lang_code": l_code,
                    "lang_name": l_info.get("name", l_code), "lang_icon": l_info.get("icon", "🌐"),
                    "status": item.get("status", "FAILED"), "last_error": lerr,
                    "retry_count": item.get("retry_count", 0), "next_retry_time": item.get("next_retry_time", 0), "diagnostic": diag
                })

    # 2. 查询历史成功分发物权记录
    raw_records = engine.meta.list_all_syndication_records(limit=100) if hasattr(engine.meta, "list_all_syndication_records") else []
    recent_records = []
    if isinstance(raw_records, list):
        for rec in raw_records:
            if isinstance(rec, dict):
                r_path, tid, l_code = rec.get("rel_path", ""), rec.get("target_id", ""), rec.get("lang_code", "zh-CN")
                rec_title = _extract_doc_title(engine, r_path, docs_snapshot)
                ch_info, l_info = channel_map.get(tid, {}), _resolve_lang_meta(l_code)
                recent_records.append({
                    "id": rec.get("id"), "rel_path": r_path, "title": rec_title or r_path,
                    "lang_code": l_code, "lang_name": l_info.get("name", l_code), "lang_icon": l_info.get("icon", "🌐"),
                    "target_id": tid, "target_type": ch_info.get("type", "social"), "target_name": ch_info.get("name", tid), "target_icon": ch_info.get("icon", "🏷️"),
                    "remote_article_id": rec.get("remote_article_id", ""), "remote_url": rec.get("remote_url", ""), "updated_at": rec.get("updated_at", "")
                })

    # 3. 统计全渠道连通性健康矩阵
    syndication_cfg = getattr(engine.config, "syndication", None) or {}
    if hasattr(syndication_cfg, "dict"): syndication_cfg = syndication_cfg.dict()
    if not isinstance(syndication_cfg, dict): syndication_cfg = {}

    pub_ctrl = getattr(engine.config, "publish_control", None)
    direct_upload = getattr(pub_ctrl, "direct_upload", {}) if pub_ctrl else {}
    if hasattr(direct_upload, "dict"): direct_upload = direct_upload.dict()
    if not isinstance(direct_upload, dict): direct_upload = {}

    known_channels = list(channel_map.values())
    failed_target_ids = {t["target_id"] for t in dead_letter_tasks if t.get("status") == "FAILED"}

    channel_health = []
    for ch in known_channels:
        cid = ch["id"]
        ctype = ch.get("type", "social")
        if ctype == "hosting":
            ch_sub_cfg = direct_upload.get(cid, {}) if isinstance(direct_upload, dict) else {}
            enabled = bool(ch_sub_cfg.get("enabled", False)) if isinstance(ch_sub_cfg, dict) else False
            has_token = bool(ch_sub_cfg.get("token") or ch_sub_cfg.get("access_token") or ch_sub_cfg.get("api_token") or ch_sub_cfg.get("host") or ch_sub_cfg.get("repo_url")) if isinstance(ch_sub_cfg, dict) else False
        else:
            ch_sub_cfg = syndication_cfg.get(cid, {}) if isinstance(syndication_cfg, dict) else {}
            enabled = bool(ch_sub_cfg.get("enabled", False)) if isinstance(ch_sub_cfg, dict) else False
            has_token = bool(ch_sub_cfg.get("api_token") or ch_sub_cfg.get("token") or ch_sub_cfg.get("cookie")) if isinstance(ch_sub_cfg, dict) else False
        
        if cid in failed_target_ids: status, msg = "error", "存在推送失败任务待自愈"
        elif enabled and has_token: status, msg = "healthy", "凭证就绪 · 待命状态"
        elif enabled and not has_token: status, msg = "warning", "已启用但缺少密钥或授权"
        else: status, msg = "disabled", "未配置启用"
        channel_health.append({**ch, "status": status, "status_msg": msg, "enabled": enabled})

    active_count = (1 if _is_publishing else 0) + len(_pending_sync_queue)

    return {
        "status": "success", "is_publishing": _is_publishing,
        "summary": {
            "total_syndicated": len(recent_records), "total_failed": len(dead_letter_tasks), "active_count": active_count,
            "success_rate": f"{round((len(recent_records) / max(len(recent_records) + len(dead_letter_tasks), 1)) * 100, 1)}%"
        },
        "channel_health": channel_health, "dead_letter_tasks": dead_letter_tasks, "recent_records": recent_records
    }


@router.get("/api/dispatch/tasks/active", dependencies=[Depends(verify_token)])
async def get_active_dispatch_tasks() -> Dict[str, Any]:
    """🚀 [V122.0] 查询当前正在活跃执行与排队的发布作业"""
    pending = []
    for idx, item in enumerate(_pending_sync_queue):
        if isinstance(item, dict):
            pending.append({
                "queue_index": idx + 1, "requested_paths": item.get("requested_paths") or ["全站所有稿件"],
                "target_langs": item.get("target_langs") or ["全部语种"], "dry_run": item.get("dry_run", False)
            })

    return {
        "is_publishing": _is_publishing,
        "active_pipeline": {
            "current_stage": "多渠道并发推送与成果验证" if _is_publishing else "IDLE",
            "progress_percent": 75 if _is_publishing else 100, "can_abort": _is_publishing
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

    # 1. 首先在元数据库中重置该任务为待重试状态
    engine.meta.retry_syndication_task(payload.rel_path, payload.target_id)

    # 2. 定向单个任务重发 (支持托管发布与社媒广播统一调度)
    if payload.rel_path and payload.target_id:
        try:
            from services.api.logic.dispatch_ops import trigger_re_dispatch_facade
            req = {
                "target_channel": payload.target_id,
                "target_slot": payload.lang_code or "zh-CN",
                "skip_syndication": False,
                "clear_cache": False
            }
            res = trigger_re_dispatch_facade(engine, payload.rel_path, req)
            if isinstance(res, dict) and res.get("success") is True:
                return {"status": "success", "message": f"已成功为 {payload.target_id.upper()} 下发重新发布任务。"}
        except Exception:
            pass

    # 3. 社媒调度服务异步重试兜底
    try:
        from core.syndication.hub import ContentSyndicator
        syndication_cfg = getattr(engine.config, "syndication", {})
        if hasattr(syndication_cfg, "dict"): syndication_cfg = syndication_cfg.dict()
        site_url = getattr(engine.config, "site_url", "")
        sys_tuning = {"vault_root": getattr(engine, "vault_root", os.getcwd())}
        syndicator = ContentSyndicator(syndication_cfg=syndication_cfg, site_url=site_url, sys_tuning_cfg=sys_tuning, meta=engine.meta)
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
