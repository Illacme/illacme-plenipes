# -*- coding: utf-8 -*-
"""
⚡ [V125.2] Hosting Diagnostics & Connectivity Ping Routes
职责：为 11 大全站托管平台提供轻量探测、静态网站发布包态势与部署控制台流水。
🛡️ 规范：单文件物理行数严格控制在 300 行以内 (SOP-02)。
"""

import os
import re
import time
import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.runtime.engine_singleton import get_global_engine
from ..system import verify_token
from ..gov.context_shards.plugin_dry_run_hosting import run_hosting_plugin_dry_run


router = APIRouter(tags=["Hosting Diagnostics"])


class HostingPingPayload(BaseModel):
    channel: str
    settings_override: Optional[Dict[str, Any]] = None


def extract_direct_upload(engine: Any) -> Dict[str, Any]:
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


def resolve_hosting_site_url(pid: str, cfg: Dict[str, Any], target_info: Dict[str, Any]) -> str:
    """智能推导或提取各大全站托管平台的对外可访问 URL (支持 11 大平台)"""
    url = cfg.get("site_url") or cfg.get("custom_domain") or cfg.get("domain") or target_info.get("url") or ""
    if url:
        return url if url.startswith("http") else f"https://{url}"
    p_name = cfg.get("project_name") or cfg.get("site_name") or cfg.get("app_name") or cfg.get("name") or ""
    if pid == "vercel" and p_name: return f"https://{p_name}.vercel.app"
    if pid == "cloudflare_pages" and p_name: return f"https://{p_name}.pages.dev"
    if pid == "netlify" and p_name: return f"https://{p_name}.netlify.app"
    if pid == "render" and p_name: return f"https://{p_name}.onrender.com"
    if pid == "github_pages":
        if cfg.get("cname"): return f"https://{cfg.get('cname')}"
        m = re.search(r"github\.com[:/]([^/]+)/([^/\.]+)", cfg.get("repo_url") or cfg.get("repo") or "")
        if m: return f"https://{m.group(1)}.github.io/{m.group(2)}/"
    if pid == "gitlab_pages":
        if cfg.get("cname"): return f"https://{cfg.get('cname')}"
        m = re.search(r"gitlab\.com[:/]([^/]+)/([^/\.]+)", cfg.get("repo_url") or cfg.get("project_path") or "")
        if m: return f"https://{m.group(1)}.gitlab.io/{m.group(2)}/"
    if pid == "gitee_pages":
        m = re.search(r"gitee\.com[:/]([^/]+)/([^/\.]+)", cfg.get("repo_url") or cfg.get("repo") or "")
        if m: return f"https://{m.group(1)}.gitee.io/{m.group(2)}/"
    return ""


def get_bundle_stats(engine: Any) -> Dict[str, Any]:
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
        os.path.abspath(resolved_site_dir), os.path.abspath("dist")
    ]
    bundle_path = next((p for p in candidates if os.path.exists(p)), candidates[0])
    exists = os.path.exists(bundle_path) and os.path.isdir(bundle_path)

    total_files, total_bytes, last_modified, html_pages = 0, 0, 0, 0
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


@router.post("/api/dispatch/hosting/ping")
async def ping_hosting_channel(
    payload: HostingPingPayload,
    token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """⚡ 执行指定全站托管平台渠道的凭证鉴权与网络连通性轻量健康探测"""
    channel = (payload.channel or "").strip().lower()
    if not channel:
        raise HTTPException(status_code=400, detail="缺少目标托管平台标识 (channel)")

    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="出版发行引擎正在初始化")

    direct_upload = extract_direct_upload(engine)
    saved_cfg = direct_upload.get(channel, {}) if isinstance(direct_upload, dict) else {}
    if hasattr(saved_cfg, "dict") and callable(saved_cfg.dict):
        saved_cfg = saved_cfg.dict()
    elif hasattr(saved_cfg, "__dict__"):
        saved_cfg = saved_cfg.__dict__
    elif not isinstance(saved_cfg, dict):
        saved_cfg = {}

    settings = dict(saved_cfg)
    if payload.settings_override and isinstance(payload.settings_override, dict):
        settings.update(payload.settings_override)

    logs = []
    def log_fn(level: str, msg: str) -> Dict[str, str]:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        entry = {"time": now, "level": level, "message": msg}
        logs.append(entry)
        return entry

    t0 = time.time()
    healthy = False
    try:
        if channel == "sftp":
            from ..gov.context_shards.plugin_dry_run_media import run_media_plugin_dry_run
            healthy = run_media_plugin_dry_run("sftp", settings, logs, log_fn)
        else:
            healthy = run_hosting_plugin_dry_run(channel, settings, logs, log_fn)
    except Exception as exc:
        log_fn("ERROR", f"❌ [探测异常] 底层链路发生未预期异常: {str(exc)}")
        healthy = False

    latency_ms = max(1, int((time.time() - t0) * 1000))
    summary = ""
    identity = ""
    for entry in reversed(logs):
        msg = entry.get("message", "")
        if "识别当前用户身份" in msg or "Cloudflare 账号" in msg:
            identity = msg.split(":")[-1].replace("'", "").strip()
        if not summary and entry.get("level") in ("SUCCESS", "ERROR", "WARN"):
            summary = msg

    if not summary:
        summary = "连通性测试通过" if healthy else "测试未通过，请检查配置"

    return {
        "status": "success", "channel": channel, "healthy": healthy,
        "latency_ms": latency_ms, "identity": identity, "summary": summary, "logs": logs
    }


def format_deploy_process_logs(
    batch_id: str,
    theme: str,
    pages_count: int,
    bundle_size_formatted: str,
    channels: list,
    targets_result: dict,
    overall_status: str,
    duration: float,
    start_time_str: str = "",
    doc_id: Optional[str] = None
) -> str:
    """🛠️ 构建专业 CI/CD 分步部署控制台终端流水日志"""
    now_f = lambda: time.strftime("%H:%M:%S")
    t0 = start_time_str or now_f()
    clean_channels = [c for c in channels if not c.startswith("_")]
    short_b = batch_id.split('_')[-1] if '_' in batch_id else batch_id[-6:]

    if doc_id:
        pg_desc = f"{pages_count} 个网页 (含多语言版本)" if pages_count > 1 else f"{pages_count} 个网页"
        lines = [
            f"[{t0}] [INIT] 启动单篇文档托管同步任务 (批次: #{short_b})",
            f"[{t0}] [SOURCE] 触发原稿: [{doc_id}] (联动整站静态包推流以同步全站索引与导航)",
            f"[{t0}] [BUNDLE] 校验静态产物: 装帧主题={theme}, 对应网页={pg_desc}, 构建体积={bundle_size_formatted}",
            f"[{t0}] [ROUTING] 目标发布渠道队列: {', '.join(clean_channels) if clean_channels else '无就绪渠道'}"
        ]
    else:
        lines = [
            f"[{t0}] [INIT] 启动全站托管部署任务 (批次: #{short_b})",
            f"[{t0}] [BUNDLE] 校验静态网站产物: 装帧主题={theme}, 页面数={pages_count}, 构建体积={bundle_size_formatted}",
            f"[{t0}] [ROUTING] 目标发布渠道队列: {', '.join(clean_channels) if clean_channels else '无就绪渠道'}"
        ]

    for ch in clean_channels:
        t_info = targets_result.get(ch, {}) if isinstance(targets_result, dict) else {}
        st = t_info.get("status", "UNKNOWN")
        dep_t = (t_info.get("deployed_at") or "").split(" ")[-1] or now_f()
        dur = t_info.get("duration_sec")
        dur_str = f" (耗时 {dur}s)" if dur else ""
        if st == "SUCCESS":
            lines.append(f"[{dep_t}] [SUCCESS] 平台 [{ch}] 发布成功 -> 线上公网: {t_info.get('url', '--')}{dur_str}")
        elif st == "RUNNING":
            lines.append(f"[{now_f()}] [PUSH] 正在向平台 [{ch}] 推送静态网站产物...")
        elif st == "PENDING":
            lines.append(f"[{t0}] [QUEUE] 平台 [{ch}] 队列就绪，等待推流...")
        elif st == "FAILED":
            lines.append(f"[{dep_t}] [ERROR] 平台 [{ch}] 推送失败: {t_info.get('error', '未知异常')}{dur_str}")

    finish_label = "文档托管同步" if doc_id else "全站托管部署"
    if overall_status not in ("RUNNING", "PENDING"):
        lines.append(f"[{now_f()}] [FINISH] {finish_label}执行完毕，总状态: {overall_status}，总耗时: {duration}s")
    else:
        lines.append(f"[{now_f()}] [PROGRESS] 正在部署推流中，实时状态: {overall_status}...")
    return "\n".join(lines)


@router.get("/api/dispatch/hosting/batch/{batch_id}")
async def get_hosting_batch_detail(
    batch_id: str,
    token: str = Depends(verify_token)
):
    """📋 查询整站托管部署批次详情与控制台日志流水"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="出版发行引擎正在初始化")

    batch = None
    if hasattr(engine, "meta") and hasattr(engine.meta, "get_hosting_deploy_batch"):
        try:
            batch = engine.meta.get_hosting_deploy_batch(batch_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"查询批次失败: {str(e)}")

    if not batch:
        raise HTTPException(status_code=404, detail=f"未找到批次 {batch_id}")

    targets = batch.get("targets") or {}
    trig_src = batch.get("trigger_source") or ""
    doc_id = None
    if trig_src.startswith("vault_drawer:"):
        doc_id = trig_src.split("vault_drawer:", 1)[1]
    elif "_trigger_doc" in targets:
        doc_id = targets.get("_trigger_doc")
    if doc_id:
        batch["doc_id"] = doc_id

    logs = batch.get("logs_excerpt") or ""
    needs_rf = (not logs or logs.startswith("已部署至") or len(logs.strip()) < 15)
    if doc_id and not needs_rf:
        needs_rf = any(isinstance(t, dict) and t.get("url", "").endswith((".html", ".htm")) and t["url"] not in logs for k, t in targets.items() if not k.startswith("_"))
    if needs_rf:
        ch_list = [k for k in targets.keys() if not k.startswith("_")]
        kb = batch.get("bundle_size_kb", 0) or 0
        sz_fmt = f"{round(kb, 2)} KB" if kb < 1024 else f"{round(kb / 1024, 2)} MB"
        fresh_logs = format_deploy_process_logs(
            batch_id=batch_id,
            theme=batch.get("theme", "default"),
            pages_count=batch.get("pages_count", 0),
            bundle_size_formatted=sz_fmt,
            channels=ch_list,
            targets_result=targets,
            overall_status=batch.get("overall_status", "UNKNOWN"),
            duration=batch.get("duration_sec", 0),
            start_time_str=(batch.get("started_at") or "").split(" ")[-1],
            doc_id=doc_id
        )
        batch["logs_excerpt"] = fresh_logs
        if hasattr(engine, "meta") and hasattr(engine.meta, "update_hosting_deploy_batch"):
            try: engine.meta.update_hosting_deploy_batch(batch_id=batch_id, logs_excerpt=fresh_logs)
            except Exception: pass

    return {
        "status": "success",
        "batch": batch
    }
