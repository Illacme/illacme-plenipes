#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 [V125.2] Illacme Plenipes - Hosting Deploy Management Routes
职责：全站托管部署大盘、静态产物态势、渠道舰队网格与整站部署批次流水 API 分片。
🛡️ [SOP-02 模块拆分 / AEL-Iter] 单文件严格保持在 300 行以内。
"""

import os
import time
import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel

from core.runtime.engine_singleton import get_global_engine
from core.adapters.egress.publishers.base import PublisherRegistry
from core.bindery.hosting_record_bridge import inspect_doc_bundle_artifact, resolve_doc_channel_url, normalize_batch_for_doc
from ..system import verify_token
from .hosting_diagnostic_routes import (
    get_bundle_stats as _get_bundle_stats, extract_direct_upload as _extract_direct_upload,
    resolve_hosting_site_url as _resolve_hosting_site_url, format_deploy_process_logs
)


router = APIRouter(tags=["Hosting Deployments"])


class HostingDeployPayload(BaseModel):
    target_channel: Optional[str] = None
    target_channels: Optional[List[str]] = None
    doc_id: Optional[str] = None
    trigger_source: str = "workbench"


_HOSTING_ICON_MAP = {
    "cloudflare_pages": "☁️", "github_pages": "🐱", "gitee_pages": "🚩", "gitlab_pages": "🦊",
    "vercel": "▲", "netlify": "💠", "zeabur": "⛵", "render": "🟣", "railway": "🚂", "firebase": "🔥", "sftp": "🖥️"
}


def _collect_fleet_status(engine: Any, last_batches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """扫描 11 大全站托管平台渠道舰队网格状态"""
    fleet = []
    known_publishers = PublisherRegistry.get_all_publishers()
    direct_upload = _extract_direct_upload(engine)

    latest_targets: Dict[str, Any] = {}
    for b in (last_batches or []):
        for ch_id, t_info in (b.get("targets") or {}).items():
            if ch_id.startswith("_") or not isinstance(t_info, dict): continue
            if ch_id not in latest_targets:
                latest_targets[ch_id] = t_info

    for pid, icon in _HOSTING_ICON_MAP.items():
        cls = known_publishers.get(pid)
        name = getattr(cls, "DISPLAY_NAME", None) or pid.replace("_", " ").title()
        icon = getattr(cls, "ICON", None) or icon

        cfg = direct_upload.get(pid, {}) if isinstance(direct_upload, dict) else (getattr(direct_upload, pid, {}) or {})
        cfg = cfg.__dict__ if hasattr(cfg, "__dict__") else (cfg.dict() if hasattr(cfg, "dict") else (cfg if isinstance(cfg, dict) else {}))

        enabled = bool(cfg.get("enabled", False))
        target_info = latest_targets.get(pid, {})
        site_url = _resolve_hosting_site_url(pid, cfg, target_info)

        status = "ready" if enabled else "not_configured"
        last_status = target_info.get("status") or "IDLE"
        last_deployed_at = target_info.get("deployed_at") or "--"

        fleet.append({
            "id": pid, "name": name, "icon": icon, "enabled": enabled, "status": status,
            "site_url": site_url, "last_status": last_status, "last_deployed_at": last_deployed_at,
            "error": target_info.get("error")
        })
    return fleet


@router.get("/api/dispatch/hosting/overview")
async def get_hosting_overview(
    page: int = 1, page_size: int = 10,
    token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """🌐 获取全站托管大盘概览态势、11 大托管舰队网格与整站部署批次流水"""
    engine = get_global_engine()
    if not engine: raise HTTPException(status_code=503, detail="出版发行引擎正在初始化")

    imprint_id = getattr(engine.config, "active_imprint", "default") or "default" if hasattr(engine, "config") else "default"
    bundle_stats = _get_bundle_stats(engine)
    limit, offset = max(1, min(100, page_size)), max(0, (page - 1) * max(1, min(100, page_size)))
    batches, total_batches = [], 0
    if hasattr(engine, "meta"):
        if hasattr(engine.meta, "list_hosting_deploy_batches"):
            try: batches = engine.meta.list_hosting_deploy_batches(imprint_id=imprint_id, limit=limit, offset=offset)
            except Exception: batches = []
        if hasattr(engine.meta, "count_hosting_deploy_batches"):
            try: total_batches = engine.meta.count_hosting_deploy_batches(imprint_id=imprint_id)
            except Exception: total_batches = len(batches)

    batches = [normalize_batch_for_doc(engine, b, bundle_stats["bundle_path"]) for b in batches]
    fleet = _collect_fleet_status(engine, batches)
    total_pages = max(1, (total_batches + limit - 1) // limit)
    return {
        "status": "success", "bundle": bundle_stats, "fleet": fleet, "batches": batches,
        "pagination": {"page": page, "page_size": limit, "total": total_batches, "total_pages": total_pages},
        "total_channels": len(_HOSTING_ICON_MAP), "ready_channels": sum(1 for c in fleet if c["enabled"])
    }


@router.get("/api/dispatch/hosting/batches")
async def list_hosting_batches(
    page: int = 1, page_size: int = 10,
    token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """按分页快速拉取整站托管部署历史记录"""
    engine = get_global_engine()
    if not engine: raise HTTPException(status_code=503, detail="出版发行引擎正在初始化")
    imprint_id = getattr(engine.config, "active_imprint", "default") or "default" if hasattr(engine, "config") else "default"
    bundle_stats = _get_bundle_stats(engine)
    limit, offset = max(1, min(100, page_size)), max(0, (page - 1) * max(1, min(100, page_size)))
    batches, total_batches = [], 0
    if hasattr(engine, "meta"):
        if hasattr(engine.meta, "list_hosting_deploy_batches"):
            try: batches = engine.meta.list_hosting_deploy_batches(imprint_id=imprint_id, limit=limit, offset=offset)
            except Exception: batches = []
        if hasattr(engine.meta, "count_hosting_deploy_batches"):
            try: total_batches = engine.meta.count_hosting_deploy_batches(imprint_id=imprint_id)
            except Exception: total_batches = len(batches)
    batches = [normalize_batch_for_doc(engine, b, bundle_stats["bundle_path"]) for b in batches]
    total_pages = max(1, (total_batches + limit - 1) // limit)
    return {
        "status": "success", "batches": batches,
        "pagination": {"page": page, "page_size": limit, "total": total_batches, "total_pages": total_pages}
    }


def _resolve_ordered_hosting_channels(engine: Any, direct_upload: Dict[str, Any], target_channel: Optional[str] = None, target_channels: Optional[List[str]] = None) -> List[str]:
    """🛡️ 提取并按官方主站优先级稳定排序托管发布渠道（主站优先率先投递，备用镜像排后）"""
    if target_channels and isinstance(target_channels, list):
        channels = [c for c in target_channels if c]
    elif target_channel:
        channels = [target_channel]
    else:
        channels = [pid for pid in _HOSTING_ICON_MAP.keys() if (direct_upload.get(pid, {}) if isinstance(direct_upload, dict) else (getattr(direct_upload, pid, {}) or {})).get("enabled")]

    cfg = getattr(engine, "config", None)
    pub_ctrl = getattr(cfg, "publish_control", None) if cfg else None
    if isinstance(pub_ctrl, dict):
        primary_id = pub_ctrl.get("primary_hosting_id") or pub_ctrl.get("direct_upload", {}).get("primary_hosting_id") or ""
    elif pub_ctrl:
        primary_id = getattr(pub_ctrl, "primary_hosting_id", "") or (getattr(getattr(pub_ctrl, "direct_upload", None), "primary_hosting_id", "") or "")
    else:
        primary_id = ""

    if primary_id and primary_id in channels:
        return sorted(channels, key=lambda c: 0 if c == primary_id else 1)
    return channels


def _execute_hosting_deploy_sync(engine: Any, batch_id: str, target_channel: Optional[str] = None, target_channels: Optional[List[str]] = None, doc_id: Optional[str] = None):
    """后台执行整站托管部署任务并实时向批次账本与控制台流水推流"""
    start_time = time.time()
    bundle_stats = _get_bundle_stats(engine)
    bundle_path = bundle_stats["bundle_path"]
    direct_upload = _extract_direct_upload(engine)

    channels_to_push = _resolve_ordered_hosting_channels(engine, direct_upload, target_channel, target_channels)
    targets_result = {ch: {"status": "PENDING"} for ch in channels_to_push}
    if doc_id: targets_result["_trigger_doc"] = doc_id

    pages_to_rec = bundle_stats["pages_count"]
    size_to_rec = bundle_stats["bundle_size_kb"]
    size_fmt_to_rec = bundle_stats["bundle_size_formatted"]
    doc_web_rel = ""
    if doc_id:
        doc_stat = inspect_doc_bundle_artifact(bundle_path, doc_id)
        doc_web_rel = doc_stat.get("web_rel_path") or ""
        pages_to_rec = doc_stat["pages_count"]
        size_to_rec = doc_stat["size_kb"]
        size_fmt_to_rec = doc_stat["size_formatted"]

    def _save_realtime(status_str="RUNNING", dur=0.0):
        if hasattr(engine, "meta") and hasattr(engine.meta, "update_hosting_deploy_batch"):
            try:
                logs_str = format_deploy_process_logs(
                    batch_id=batch_id, theme=bundle_stats.get("theme", "default"),
                    pages_count=pages_to_rec, bundle_size_formatted=size_fmt_to_rec,
                    channels=channels_to_push, targets_result=targets_result, overall_status=status_str,
                    duration=dur, start_time_str=time.strftime("%H:%M:%S", time.localtime(start_time)),
                    doc_id=doc_id
                )
                engine.meta.update_hosting_deploy_batch(
                    batch_id=batch_id, overall_status=status_str, duration_sec=dur,
                    targets_json=targets_result, logs_excerpt=logs_str,
                    pages_count=pages_to_rec, bundle_size_kb=size_to_rec
                )
            except Exception as e:
                import logging; logging.getLogger("Main").error(f"❌ [批次更新异常] {e}")

    all_success, any_success = True, False
    for ch in channels_to_push:
        targets_result[ch] = {"status": "RUNNING"}
        _save_realtime("RUNNING", round(time.time() - start_time, 2))
        pub_cls = PublisherRegistry.get_publisher(ch)
        if not pub_cls:
            targets_result[ch] = {"status": "FAILED", "error": f"未找到渠道驱动 {ch}"}
            all_success = False
            _save_realtime("RUNNING", round(time.time() - start_time, 2))
            continue

        chan_cfg = direct_upload.get(ch, {}) if isinstance(direct_upload, dict) else (getattr(direct_upload, ch, {}) or {})
        chan_cfg = chan_cfg.__dict__ if hasattr(chan_cfg, "__dict__") else (chan_cfg.dict() if hasattr(chan_cfg, "dict") else (chan_cfg if isinstance(chan_cfg, dict) else {}))
        sys_tuning = {"vault_root": getattr(engine, "vault_root", os.getcwd())}
        t_ch_start = time.time()
        try:
            pub = pub_cls(chan_cfg, sys_tuning)
            metadata = {"batch_id": batch_id, "title": f"Deploy [{doc_id}] - {bundle_stats['theme']}" if doc_id else f"Full Site Deploy - {bundle_stats['theme']}", "imprint": bundle_stats["imprint_id"]}
            res = pub.push(bundle_path, metadata)
            if isinstance(res, dict) and res.get("status") != "success":
                raise RuntimeError(res.get("message") or "对端部署返回异常")
            base_site_url = res.get("url") if isinstance(res, dict) else chan_cfg.get("site_url")
            doc_pub_url = resolve_doc_channel_url(base_site_url, doc_web_rel) if (doc_id and doc_web_rel) else base_site_url
            targets_result[ch] = {"status": "SUCCESS", "url": doc_pub_url, "site_url": base_site_url, "duration_sec": round(time.time() - t_ch_start, 2), "deployed_at": time.strftime("%Y-%m-%d %H:%M:%S")}
            any_success = True
            if doc_id and hasattr(engine, "meta") and hasattr(engine.meta, "update_egress_status"):
                try: engine.meta.update_egress_status(doc_id, ch, "SUCCESS", url=doc_pub_url); engine.meta.save()
                except Exception: pass
        except Exception as pe:
            all_success = False
            targets_result[ch] = {"status": "FAILED", "error": str(pe), "duration_sec": round(time.time() - t_ch_start, 2), "deployed_at": time.strftime("%Y-%m-%d %H:%M:%S")}
            if doc_id and hasattr(engine, "meta") and hasattr(engine.meta, "update_egress_status"):
                try: engine.meta.update_egress_status(doc_id, ch, "FAILED", error=str(pe)); engine.meta.save()
                except Exception: pass
        _save_realtime("RUNNING", round(time.time() - start_time, 2))

    duration = round(time.time() - start_time, 2)
    overall = "SUCCESS" if (all_success and channels_to_push) else ("PARTIAL_SUCCESS" if any_success else "FAILED")
    if not channels_to_push:
        overall = "FAILED"
        targets_result["error"] = "未选择或未配置任何可推送的全站托管渠道"
    _save_realtime(overall, duration)


@router.post("/api/dispatch/hosting/deploy")
async def trigger_hosting_deploy(
    payload: HostingDeployPayload,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """🚀 触发全站托管部署（支持一键全量并发推流、勾选多平台或定向单渠道部署）"""
    engine = get_global_engine()
    if not engine: raise HTTPException(status_code=503, detail="出版发行引擎正在初始化")

    bundle_stats = _get_bundle_stats(engine)
    if not bundle_stats["bundle_exists"]:
        raise HTTPException(status_code=400, detail=f"静态发布产物包不存在或未构建（路径：{bundle_stats['bundle_path']}），请先执行装帧构建。")

    batch_id = f"deploy_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    imprint_id = bundle_stats["imprint_id"]
    theme = bundle_stats["theme"]
    direct_upload = _extract_direct_upload(engine)

    channels_to_push = _resolve_ordered_hosting_channels(engine, direct_upload, payload.target_channel, payload.target_channels)
    init_targets = {ch: {"status": "PENDING"} for ch in channels_to_push}
    if payload.doc_id:
        init_targets["_trigger_doc"] = payload.doc_id

    pages_to_rec = bundle_stats["pages_count"]
    size_to_rec = bundle_stats["bundle_size_kb"]
    size_fmt_to_rec = bundle_stats["bundle_size_formatted"]
    if payload.doc_id:
        doc_stat = inspect_doc_bundle_artifact(bundle_stats["bundle_path"], payload.doc_id)
        pages_to_rec = doc_stat["pages_count"]
        size_to_rec = doc_stat["size_kb"]
        size_fmt_to_rec = doc_stat["size_formatted"]

    init_logs = format_deploy_process_logs(
        batch_id=batch_id, theme=theme, pages_count=pages_to_rec,
        bundle_size_formatted=size_fmt_to_rec, channels=channels_to_push,
        targets_result=init_targets, overall_status="RUNNING", duration=0.0,
        start_time_str=time.strftime("%H:%M:%S"), doc_id=payload.doc_id
    )

    trigger_src = f"vault_drawer:{payload.doc_id}" if payload.doc_id else payload.trigger_source
    if hasattr(engine, "meta") and hasattr(engine.meta, "create_hosting_deploy_batch"):
        try:
            engine.meta.create_hosting_deploy_batch(
                batch_id=batch_id, trigger_source=trigger_src, imprint_id=imprint_id,
                theme=theme, pages_count=pages_to_rec, bundle_size_kb=size_to_rec,
                targets_json=init_targets, overall_status="RUNNING", started_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                logs_excerpt=init_logs
            )
        except Exception: pass

    background_tasks.add_task(_execute_hosting_deploy_sync, engine, batch_id, payload.target_channel, payload.target_channels, payload.doc_id)
    msg = f"原稿 [{payload.doc_id}] 托管同步任务已进入执行队列" if payload.doc_id else "整站托管部署任务已进入执行队列"
    return {"status": "success", "batch_id": batch_id, "message": msg, "bundle": bundle_stats}
