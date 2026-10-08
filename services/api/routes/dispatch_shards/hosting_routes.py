#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 [V125.0] Illacme Plenipes - Hosting Deploy Management Routes
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
from ..system import verify_token


router = APIRouter(tags=["Hosting Deployments"])


class HostingDeployPayload(BaseModel):
    target_channel: Optional[str] = None
    trigger_source: str = "workbench"


_HOSTING_ICON_MAP = {
    "cloudflare_pages": "☁️", "github_pages": "🐱", "gitee_pages": "🚩", "gitlab_pages": "🦊",
    "vercel": "▲", "netlify": "💠", "zeabur": "⛵", "render": "🟣", "railway": "🚂", "firebase": "🔥", "sftp": "🖥️"
}


def _get_bundle_stats(engine: Any) -> Dict[str, Any]:
    """探测当前装帧主题静态发布包物理态势"""
    imprint_id = getattr(engine.config, "active_imprint", "default") or "default" if hasattr(engine, "config") else "default"
    theme = getattr(engine.config, "active_theme", "default") or "default" if hasattr(engine, "config") else "default"
    ssg_site_dir = engine.ssg_adapter.get_site_dir() if (hasattr(engine, "ssg_adapter") and engine.ssg_adapter and hasattr(engine.ssg_adapter, "get_site_dir")) else "dist"
    paths_cfg = getattr(engine.config, "output_paths", {}) or {} if hasattr(engine, "config") else {}
    site_dir_cfg = (paths_cfg.get("site_dir") if isinstance(paths_cfg, dict) else getattr(paths_cfg, "site_dir", ssg_site_dir)) or ssg_site_dir
    resolved_site_dir = site_dir_cfg.replace("{theme}", theme)

    candidates = [
        os.path.abspath(os.path.join("imprints", imprint_id, "themes", theme, resolved_site_dir)),
        os.path.abspath(os.path.join("themes", theme, resolved_site_dir)),
        os.path.abspath(os.path.join("imprints", imprint_id, resolved_site_dir)),
        os.path.abspath(resolved_site_dir),
        os.path.abspath("dist")
    ]
    bundle_path = next((p for p in candidates if os.path.exists(p)), candidates[0])
    exists = os.path.exists(bundle_path) and os.path.isdir(bundle_path)

    total_files, total_bytes, last_modified = 0, 0, 0
    html_pages = 0
    if exists:
        try:
            for root, _, files in os.walk(bundle_path):
                total_files += len(files)
                for f in files:
                    try:
                        st = os.stat(os.path.join(root, f))
                        total_bytes += st.st_size
                        if st.st_mtime > last_modified: last_modified = st.st_mtime
                        if f.lower().endswith(".html"): html_pages += 1
                    except Exception: pass
        except Exception: pass

    size_kb = round(total_bytes / 1024, 2)
    size_formatted = f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb / 1024, 2)} MB"
    last_built_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_modified)) if last_modified > 0 else "--"
    effective_pages = html_pages if html_pages > 0 else total_files

    return {
        "imprint_id": imprint_id, "theme": theme, "bundle_path": bundle_path, "bundle_exists": exists,
        "pages_count": effective_pages, "html_pages": html_pages, "total_files": total_files,
        "bundle_size_kb": size_kb, "bundle_size_formatted": size_formatted, "last_built_at": last_built_str
    }


def _extract_direct_upload(engine: Any) -> Dict[str, Any]:
    """🛡️ 防御性提取当前品牌已配置的独立站直传与全站托管平台字典"""
    if not engine or not hasattr(engine, "config"):
        return {}
    cfg = engine.config
    pub_ctrl = getattr(cfg, "publish_control", None)
    if pub_ctrl is None and isinstance(cfg, dict):
        pub_ctrl = cfg.get("publish_control")
    direct_upload = None
    if pub_ctrl:
        direct_upload = pub_ctrl.get("direct_upload") if isinstance(pub_ctrl, dict) else getattr(pub_ctrl, "direct_upload", None)
    if direct_upload is None:
        direct_upload = cfg.get("direct_upload") if isinstance(cfg, dict) else getattr(cfg, "direct_upload", None)
    if hasattr(direct_upload, "dict") and callable(direct_upload.dict):
        direct_upload = direct_upload.dict()
    elif hasattr(direct_upload, "__dict__"):
        direct_upload = direct_upload.__dict__
    return direct_upload if isinstance(direct_upload, dict) else {}


def _collect_fleet_status(engine: Any, last_batches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """扫描 11 大全站托管平台渠道舰队网格状态"""
    fleet = []
    known_publishers = PublisherRegistry.get_all_publishers()
    direct_upload = _extract_direct_upload(engine)

    # 聚合各渠道历史最近一次的部署结果（避免因单渠道定向发布冲掉其他渠道状态）
    latest_targets: Dict[str, Any] = {}
    for b in (last_batches or []):
        for ch_id, t_info in (b.get("targets") or {}).items():
            if ch_id not in latest_targets and isinstance(t_info, dict):
                latest_targets[ch_id] = t_info

    for pid, icon in _HOSTING_ICON_MAP.items():
        cls = known_publishers.get(pid)
        name = getattr(cls, "DISPLAY_NAME", None) or pid.replace("_", " ").title()
        icon = getattr(cls, "ICON", None) or icon

        cfg = direct_upload.get(pid, {}) if isinstance(direct_upload, dict) else (getattr(direct_upload, pid, {}) or {})
        cfg = cfg.__dict__ if hasattr(cfg, "__dict__") else (cfg.dict() if hasattr(cfg, "dict") else (cfg if isinstance(cfg, dict) else {}))

        enabled = bool(cfg.get("enabled", False))
        target_info = latest_targets.get(pid, {})
        site_url = cfg.get("site_url") or cfg.get("custom_domain") or cfg.get("domain") or target_info.get("url") or ""
        if not site_url and pid == "vercel" and cfg.get("project_name"):
            site_url = f"https://{cfg.get('project_name')}.vercel.app"
        elif not site_url and pid == "github_pages" and cfg.get("cname"):
            site_url = f"https://{cfg.get('cname')}"

        status = "ready" if enabled else "not_configured"
        last_status = target_info.get("status") or ("SUCCESS" if enabled else "IDLE")
        last_deployed_at = target_info.get("deployed_at") or "--"

        fleet.append({
            "id": pid, "name": name, "icon": icon, "enabled": enabled, "status": status,
            "site_url": site_url, "last_status": last_status, "last_deployed_at": last_deployed_at,
            "error": target_info.get("error")
        })
    return fleet


@router.get("/api/dispatch/hosting/overview")
async def get_hosting_overview(token: str = Depends(verify_token)) -> Dict[str, Any]:
    """🌐 获取全站托管大盘概览态势、11 大托管舰队网格与整站部署批次流水"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="出版发行引擎正在初始化")

    imprint_id = getattr(engine.config, "active_imprint", "default") or "default" if hasattr(engine, "config") else "default"
    bundle_stats = _get_bundle_stats(engine)

    # 读取部署流水
    batches = []
    if hasattr(engine, "meta") and hasattr(engine.meta, "list_hosting_deploy_batches"):
        try:
            batches = engine.meta.list_hosting_deploy_batches(imprint_id=imprint_id, limit=30)
        except Exception:
            batches = []

    fleet = _collect_fleet_status(engine, batches)

    return {
        "status": "success",
        "bundle": bundle_stats,
        "fleet": fleet,
        "batches": batches,
        "total_channels": len(_HOSTING_ICON_MAP),
        "ready_channels": sum(1 for c in fleet if c["enabled"])
    }


def _execute_hosting_deploy_sync(engine: Any, batch_id: str, target_channel: Optional[str] = None):
    """后台执行整站托管部署任务并更新批次账本"""
    start_time = time.time()
    bundle_stats = _get_bundle_stats(engine)
    bundle_path = bundle_stats["bundle_path"]

    targets_result = {}
    direct_upload = _extract_direct_upload(engine)

    channels_to_push = [target_channel] if target_channel else [
        pid for pid in _HOSTING_ICON_MAP.keys()
        if (direct_upload.get(pid, {}) if isinstance(direct_upload, dict) else (getattr(direct_upload, pid, {}) or {})).get("enabled")
    ]
    all_success = True
    any_success = False

    for ch in channels_to_push:
        pub_cls = PublisherRegistry.get_publisher(ch)
        if not pub_cls:
            targets_result[ch] = {"status": "FAILED", "error": f"未找到渠道驱动 {ch}"}
            all_success = False
            continue

        chan_cfg = direct_upload.get(ch, {}) if isinstance(direct_upload, dict) else (getattr(direct_upload, ch, {}) or {})
        if hasattr(chan_cfg, "__dict__"): chan_cfg = chan_cfg.__dict__
        elif hasattr(chan_cfg, "dict"): chan_cfg = chan_cfg.dict()
        elif not isinstance(chan_cfg, dict): chan_cfg = {}

        sys_tuning = {"vault_root": getattr(engine, "vault_root", os.getcwd())}
        try:
            pub = pub_cls(chan_cfg, sys_tuning)
            metadata = {"batch_id": batch_id, "title": f"Full Site Deploy - {bundle_stats['theme']}", "imprint": bundle_stats["imprint_id"]}
            res = pub.push(bundle_path, metadata)
            if isinstance(res, dict) and res.get("status") != "success":
                raise RuntimeError(res.get("message") or "对端部署返回异常")
            
            deploy_url = res.get("url") if isinstance(res, dict) else chan_cfg.get("site_url")
            targets_result[ch] = {"status": "SUCCESS", "url": deploy_url, "deployed_at": time.strftime("%Y-%m-%d %H:%M:%S")}
            any_success = True
        except Exception as pe:
            all_success = False
            targets_result[ch] = {"status": "FAILED", "error": str(pe), "deployed_at": time.strftime("%Y-%m-%d %H:%M:%S")}

    duration = round(time.time() - start_time, 2)
    overall = "SUCCESS" if (all_success and channels_to_push) else ("PARTIAL_SUCCESS" if any_success else "FAILED")
    if not channels_to_push:
        overall = "FAILED"
        targets_result["error"] = "未选择或未配置任何可推送的全站托管渠道"

    if hasattr(engine, "meta") and hasattr(engine.meta, "update_hosting_deploy_batch"):
        try:
            engine.meta.update_hosting_deploy_batch(
                batch_id=batch_id,
                overall_status=overall,
                duration_sec=duration,
                targets_json=targets_result,
                logs_excerpt=f"已部署至 {len(channels_to_push)} 个渠道，耗时 {duration}s"
            )
        except Exception:
            pass


@router.post("/api/dispatch/hosting/deploy")
async def trigger_hosting_deploy(
    payload: HostingDeployPayload,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """🚀 触发全站托管部署（支持一键全量并发推流或定向单渠道部署）"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="出版发行引擎正在初始化")

    bundle_stats = _get_bundle_stats(engine)
    if not bundle_stats["bundle_exists"]:
        raise HTTPException(
            status_code=400,
            detail=f"静态发布产物包不存在或未构建（路径：{bundle_stats['bundle_path']}），请先执行装帧构建。"
        )

    batch_id = f"deploy_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    imprint_id = bundle_stats["imprint_id"]
    theme = bundle_stats["theme"]

    # 预建批次记录
    if hasattr(engine, "meta") and hasattr(engine.meta, "create_hosting_deploy_batch"):
        try:
            engine.meta.create_hosting_deploy_batch(
                batch_id=batch_id,
                trigger_source=payload.trigger_source,
                imprint_id=imprint_id,
                theme=theme,
                pages_count=bundle_stats["pages_count"],
                bundle_size_kb=bundle_stats["bundle_size_kb"],
                targets_json={},
                overall_status="RUNNING"
            )
        except Exception:
            pass

    # 注入后台任务执行
    background_tasks.add_task(
        _execute_hosting_deploy_sync,
        engine,
        batch_id,
        payload.target_channel
    )

    return {
        "status": "success",
        "batch_id": batch_id,
        "message": "整站托管部署任务已进入执行队列",
        "bundle": bundle_stats
    }
