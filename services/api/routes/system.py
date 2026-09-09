# -*- coding: utf-8 -*-
"""
⚙️ 系统路由 — RESTful API 系统健康与运维端点。
职责：提供引擎状态、版本信息与运行时诊断的 API 接口。
🛡️ [V74.8]：物理瘦身版，逻辑已委托至 diagnostics 与 sys_ops 模块。
"""

import os
import time
import signal
import threading
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from core.runtime.engine_singleton import get_global_engine
from core.logic.orchestration.task_orchestrator import global_executor
from core.utils.tracing import tlog
from core.utils.event_bus import bus
from core.logic.diagnostics.component_monitor import ComponentMonitor
from services.api.logic import sys_ops

router = APIRouter()

def verify_token(x_token: Optional[str] = Header(None, alias="X-Token")) -> None:
    """验证 API 访问令牌"""
    engine = get_global_engine()
    if not engine or not getattr(engine, 'config', None) or not getattr(engine.config, 'system', None) or not getattr(engine.config.system, 'api_token', None):
        return
    if x_token != engine.config.system.api_token:
        from core.utils.event_bus import bus
        bus.emit("SECURITY_ALERT", category="API_TOKEN_EXPIRED", message="接口访问认证失败：检测到未授权或非法的令牌（API Token）尝试跨站越权访问控制台。")
        raise HTTPException(status_code=403, detail="Unauthorized")

from services.api.schemas import SystemHealthResponse, HealthMatrixResponse
from core.runtime.version_sentinel import VersionSentinel

@router.get("/api/system/health", response_model=SystemHealthResponse)
def health_check() -> SystemHealthResponse:
    """🚀 [P1 规范统一] 系统全息健康检查端点 (含版本漂移感知)"""
    engine = get_global_engine()
    drift_data = VersionSentinel.check_drift()
    if not engine:
        return SystemHealthResponse(
            status="starting",
            engine="Illacme-plenipes",
            imprint=None,
            services={},
            version_drift=drift_data
        )
    services_dict = engine.services if isinstance(engine.services, dict) else {}
    return SystemHealthResponse(
        status="online",
        engine="Illacme-plenipes",
        imprint=getattr(engine, "imprint_id", None),
        services=services_dict,
        version_drift=drift_data
    )

@router.get("/api/system/status", dependencies=[Depends(verify_token)])
def get_system_status() -> Dict[str, Any]:
    """🚀 [V48.3] 全息状态诊断：返回服务状态、AI 排行榜与系统负载"""
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    # 计算服务运行时间
    services = getattr(engine, "services", {}) or {}
    for name, s in services.items():
        if isinstance(s, dict) and s.get("start_time"):
            s["uptime"] = round(time.time() - s.get("start_time"), 1)

    from core.governance.health_registry import health_registry
    return {
        "services": services,
        "ai_nodes": health_registry.get_rankings(),
        "tasks": {
            "queued": global_executor._work_queue.qsize() if hasattr(global_executor, '_work_queue') else 0,
            "active": len([t for t in global_executor.workers if t.is_alive()]) if hasattr(global_executor, 'workers') else 0
        },
        "timestamp": time.time()
    }

@router.get("/api/system/stats", dependencies=[Depends(verify_token)])
def get_stats() -> Dict[str, Any]:
    """🚀 [V74.8] 物理资源采样：返回真实的 CPU、内存与计费数据"""
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized", "version_drift": VersionSentinel.check_drift()}
    cpu, mem = 0.0, 0.0
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
    except ImportError:
        pass
    workers = len([t for t in global_executor.workers if t.is_alive()]) if hasattr(global_executor, 'workers') else 0
    return {
        "usage": engine.meter.get_summary_report(),
        "load": {"cpu": cpu, "memory": mem, "workers": workers},
        "version_drift": VersionSentinel.check_drift(),
        "timestamp": time.time()
    }

@router.post("/api/system/shutdown", dependencies=[Depends(verify_token)])
def shutdown() -> Dict[str, str]:
    """安全关闭系统"""
    os.kill(os.getpid(), signal.SIGINT)
    return {"status": "accepted"}

@router.get("/api/system/version", dependencies=[Depends(verify_token)])
def get_version_info() -> Dict[str, Any]:
    """🚀 [V85.0] 运行时源码指纹与版本漂移查询接口"""
    return VersionSentinel.check_drift()

class SwitchAndLaunchPreviewRequest(BaseModel):
    theme_id: str
    imprint_id: Optional[str] = "default"
    port: Optional[int] = None
    allow_fallback: Optional[bool] = True
    sync_vault: Optional[bool] = True

@router.post("/api/system/preview/switch-and-launch", dependencies=[Depends(verify_token)])
def switch_and_launch_preview(req: SwitchAndLaunchPreviewRequest) -> Dict[str, Any]:
    """⚡ [工业级编排] 切换主题并一键点火 DevServer 预览"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    from core.runtime.infrastructure.theme_orchestrator import theme_orchestrator

    imprint_id = req.imprint_id or getattr(engine.config, "active_imprint", "default") or "default"

    # 1. 物理持久化与全链路在线热重构 (彻底对齐当前出版品牌的 active_theme、engine.paths 与 ssg_adapter)
    try:
        from services.api.routes.gov.config_shards.config_sync_ops import process_config_sync
        from services.api.routes.gov.config_shards.config_persistence_ops import persist_config_to_disk
        from services.api.routes.gov.config_shards.config_reload_ops import live_reload_engine_config

        update_payload = {"active_theme": req.theme_id}
        routing_groups, err_response = process_config_sync(engine, update_payload, imprint_id=imprint_id)
        if err_response:
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=400, content=err_response)
        if routing_groups:
            persist_config_to_disk(engine, routing_groups, imprint_id=imprint_id)
        live_reload_engine_config(engine, update_payload, imprint_id=imprint_id)
    except Exception as e:
        tlog.warning(f"⚠️ [Switch & Launch] 配置持久化或热重构容错降级: {e}")
        engine.active_theme = req.theme_id
        if hasattr(engine, "config"):
            engine.config.active_theme = req.theme_id

    result = theme_orchestrator.launch_dev_server(
        theme_id=req.theme_id,
        imprint_id=imprint_id,
        requested_port=req.port,
        engine=engine
    )

    if result.get("status") == "error":
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content=result)

    port = result.get("port", 43213)
    if "preview" in engine.services:
        engine.services["preview"].update({
            "status": "running",
            "port": port,
            "start_time": time.time(),
            "mode": result.get("mode", "framework")
        })

    # 2. 🚀 [极致简化] 强制全量编译落盘文库文档至当前主题目录 (HMR 实时呈现)
    if req.sync_vault:
        try:
            from core.runtime.orchestrator import start_asynchronous_sync
            task_id = start_asynchronous_sync(engine, force=True, local_only=True)
            result["sync_triggered"] = True
            result["sync_task_id"] = task_id
        except Exception as e:
            tlog.error(f"Failed to trigger auto sync during preview switch: {e}")
            result["sync_triggered"] = False
            result["sync_error"] = str(e)
    else:
        result["sync_triggered"] = False

    return result

@router.post("/api/system/preview/restart", dependencies=[Depends(verify_token)])
def restart_preview() -> Dict[str, Any]:
    """🚀 [Orchestrator 桥接] 工业级增强型重启预览"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    from core.runtime.infrastructure.theme_orchestrator import theme_orchestrator

    imprint_id = getattr(engine.config, "active_imprint", "default") or "default"
    theme_id = getattr(engine, "active_theme", "default") or "default"
    result = theme_orchestrator.launch_dev_server(
        theme_id=theme_id,
        imprint_id=imprint_id,
        engine=engine
    )
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Restart failed"))

    port = result.get("port", 43213)
    if "preview" in engine.services:
        engine.services["preview"].update({
            "status": "running",
            "port": port,
            "start_time": time.time(),
            "mode": result.get("mode", "framework")
        })
    return {"status": "success", "message": "Preview server started.", "port": port, "url": result.get("url", f"http://localhost:{port}")}

@router.post("/api/system/preview/stop", dependencies=[Depends(verify_token)])
async def stop_preview() -> Dict[str, str]:
    """🛑 [Orchestrator 桥接] 停止预览服务"""
    engine = get_global_engine()
    if not engine: raise HTTPException(status_code=400, detail="Engine not initialized")
    from core.runtime.infrastructure.theme_orchestrator import theme_orchestrator
    theme_orchestrator.shutdown_all()
    if "preview" in engine.services:
        engine.services["preview"].update({"status": "offline", "port": theme_orchestrator.active_port, "start_time": 0.0})
    bus.emit("UI_TERMINAL_DATA", type="LOG", data="⏹️ [系统感知] 预览服务器已物理停机，端口已安全释放。")
    return {"status": "success", "message": "Preview server stopped."}

@router.get("/api/system/preview/logs", dependencies=[Depends(verify_token)])
def get_preview_logs() -> Dict[str, Any]:
    """📋 [Orchestrator 桥接] 获取预览服务最新采样日志"""
    from core.runtime.infrastructure.theme_orchestrator import theme_orchestrator
    return {
        "status": "success",
        "logs": list(theme_orchestrator.log_ring_buffer),
        "theme": theme_orchestrator.active_theme,
        "port": theme_orchestrator.active_port,
        "is_alive": bool(theme_orchestrator.active_process and theme_orchestrator.active_process.poll() is None)
    }

@router.post("/api/system/restart", dependencies=[Depends(verify_token)])
def restart_kernel() -> Dict[str, str]:
    """🚀 [V85.0] 平滑热重启 API 核心引擎：释放端口并自我 execv 接力"""
    tlog.warning("🔄 [API] 收到平滑热重启指令，即将唤醒全新内核进程...")
    VersionSentinel.trigger_process_restart(delay_seconds=0.3)
    return {"status": "restarting", "message": "Kernel is gracefully restarting..."}


@router.get("/api/system/preview/status", dependencies=[Depends(verify_token)])
def get_preview_status() -> Dict[str, Any]:
    """🔍 [Orchestrator 桥接] 查询本地预览服务实时运行状态与拓扑元数据"""
    from core.runtime.infrastructure.theme_orchestrator import theme_orchestrator
    is_alive = bool(theme_orchestrator.active_process and theme_orchestrator.active_process.poll() is None)
    port = theme_orchestrator.active_port or 43213
    theme_id = theme_orchestrator.active_theme or "default"
    return {
        "status": "online" if is_alive else "offline",
        "theme": theme_id,
        "port": port,
        "is_alive": is_alive,
        "pid": theme_orchestrator.active_process.pid if (is_alive and theme_orchestrator.active_process) else None,
        "url": f"http://localhost:{port}" if is_alive else None
    }


@router.get("/api/system/health/matrix", dependencies=[Depends(verify_token)], response_model=HealthMatrixResponse)
def get_health_matrix() -> HealthMatrixResponse:
    """🚀 [P1 规范统一] 获取系统组件全息健康矩阵"""
    matrix = ComponentMonitor.get_matrix()
    return HealthMatrixResponse(
        engine=matrix.get("engine", {"status": "offline", "label": "核心引擎", "health": 0}),
        onboarding=matrix.get("onboarding", {"status": "offline", "label": "品牌向导", "health": 0}),
        preview=matrix.get("preview", {"status": "offline", "label": "预览服务", "health": 0})
    )

@router.get("/api/system/languages")
def get_supported_languages() -> Dict[str, List[Any]]:
    """🌍 [V55.3] 动态获取系统支持的全球语种矩阵"""
    from core.utils.language_hub import LanguageHub
    return {"languages": LanguageHub.get_supported_matrix()}

@router.post("/api/system/theme/install", dependencies=[Depends(verify_token)])
async def install_theme_dependencies() -> Dict[str, str]:
    """🚀 [V52.11] 自动化依赖安装接口"""
    engine = get_global_engine()
    if not engine: raise HTTPException(status_code=400, detail="Engine missing")
    
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    if not os.path.exists(os.path.join(theme_dir, "package.json")):
        return {"status": "skipped", "message": "No package.json"}
    
    threading.Thread(target=sys_ops.run_theme_install, args=(engine, theme_dir), daemon=True).start()
    return {"status": "started"}

@router.post("/api/system/theme/upgrade", dependencies=[Depends(verify_token)])
async def upgrade_theme_dependencies() -> Dict[str, str]:
    """🚀 [V65.0] 自动化版本升级接口"""
    engine = get_global_engine()
    if not engine: raise HTTPException(status_code=400, detail="Engine missing")
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    threading.Thread(target=sys_ops.run_theme_upgrade, args=(engine, theme_dir), daemon=True).start()
    return {"status": "started"}

@router.post("/api/system/theme/rollback", dependencies=[Depends(verify_token)])
async def rollback_theme_config() -> Dict[str, Any]:
    """🚀 [V65.3] 物理快照回滚接口"""
    engine = get_global_engine()
    if not engine: raise HTTPException(status_code=400, detail="Engine missing")
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    restored = sys_ops.rollback_config(engine, theme_dir)
    if restored:
        bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"⏪ [环境复原] 已恢复: {', '.join(restored)}")
        if "package.json" in restored:
            await install_theme_dependencies()
        return {"status": "success", "restored": restored}
    return {"status": "skipped"}

@router.post("/api/system/wizard/start", dependencies=[Depends(verify_token)])
async def start_wizard() -> Dict[str, str]:
    """🚀 [V55.0] 启动品牌向导服务"""
    if ComponentMonitor.check_port(43211):
        return {"status": "already_running"}
    from services.wizard.wizard_server import start_wizard_server
    threading.Thread(target=start_wizard_server, kwargs={"port": 43211}, daemon=True).start()
    return {"status": "started"}

@router.post("/api/system/wizard/stop", dependencies=[Depends(verify_token)])
async def stop_wizard() -> Dict[str, str]:
    """🛑 [V55.0] 停止品牌向导服务"""
    try:
        import urllib.request
        req = urllib.request.Request("http://127.0.0.1:43211/api/shutdown", method="POST")
        with urllib.request.urlopen(req, timeout=2.0): pass
        return {"status": "stopped"}
    except Exception:
        return {"status": "stopped", "note": "Service may already be down"}

@router.post("/api/system/pick_directory", dependencies=[Depends(verify_token)])
async def pick_directory() -> Dict[str, Any]:
    """📂 [V75.6] 唤起操作系统原生文件夹拾取器，返回绝对路径"""
    import subprocess
    import sys
    if sys.platform == "darwin":
        try:
            cmd = ['osascript', '-e', 'POSIX path of (choose folder with prompt "请选择内容文库 (Vault) 物理根目录:")']
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and res.stdout.strip():
                selected_path = res.stdout.strip().rstrip('/')
                return {"success": True, "path": selected_path}
            elif "User canceled" in res.stderr or "-128" in res.stderr:
                return {"success": False, "canceled": True}
            return {"success": False, "error": res.stderr.strip() or "未选择任何路径"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    elif sys.platform == "win32":
        try:
            ps_script = "[System.Reflection.Assembly]::LoadWithPartialName('System.windows.forms') | Out-Null; $f = New-Object System.Windows.Forms.FolderBrowserDialog; $f.Description = '请选择内容文库根目录'; if ($f.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $f.SelectedPath }"
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and res.stdout.strip():
                return {"success": True, "path": res.stdout.strip()}
            return {"success": False, "canceled": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return {"success": False, "unsupported": True, "message": "当前服务器环境暂无图形界面，请直接手动输入绝对路径"}

@router.post("/api/system/sync/precheck", dependencies=[Depends(verify_token)])
async def precheck_sync() -> Dict[str, Any]:
    """🚀 [V78.5] 毫秒级双段式预检接口：用于提供给 UI 拦截"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not ready")
    return sys_ops.run_precheck_logic(engine)

@router.post("/api/system/watchdog/suspend", dependencies=[Depends(verify_token)])
async def suspend_watchdog() -> Dict[str, str]:
    """🚀 [V78.6] 挂起监控狗：阻止自动同步触发 (UI 独占模式)"""
    engine = get_global_engine()
    if engine:
        engine.is_watchdog_suspended = True
        tlog.info("🤫 [UI] 已发出静默指令：监控狗进入休眠状态。")
    return {"status": "suspended"}

@router.post("/api/system/watchdog/resume", dependencies=[Depends(verify_token)])
async def resume_watchdog() -> Dict[str, str]:
    """🚀 [V78.6] 唤醒监控狗：恢复自动同步"""
    engine = get_global_engine()
    if engine:
        engine.is_watchdog_suspended = False
        tlog.info("🐕 [UI] 已发出唤醒指令：监控狗重新开始巡视。")
    return {"status": "resumed"}

@router.post("/api/system/sync/trigger", dependencies=[Depends(verify_token)])
async def trigger_sync(dry_run: bool = False, force: bool = False, sandbox: bool = False, local_only: bool = False, clear_cache: bool = False) -> Dict[str, Any]:
    """🚀 [V51.0] 全球同步点火接口：驱动编排中枢执行全量同步 / 发布预览"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not ready")
    
    # 🛡️ [V76.8] 翻译矩阵与算力可用性强关联校验熔断门禁 (同步拦截)
    try:
        from core.governance.checks.ai import check_ai_availability_or_raise
        check_ai_availability_or_raise(engine)
    except RuntimeError as e:
        return {"status": "error", "reason": str(e)}

    from core.runtime.orchestrator import start_asynchronous_sync
    future_id = start_asynchronous_sync(engine, dry_run=dry_run, force=force, sandbox=sandbox, local_only=local_only, clear_cache=clear_cache)

    
    if future_id is None or future_id == 0:
        return {"status": "rejected", "reason": "Already publishing"}
    
    return {
        "status": "started",
        "future_id": future_id,
        "mode": "asynchronous",
        "local_only": local_only
    }

@router.get("/api/system/sync/status", dependencies=[Depends(verify_token)])
def get_sync_status() -> Dict[str, Any]:
    """🚀 [V78.8] 查询当前出版流水线是否在运行"""
    from core.runtime.orchestrator import _is_publishing
    return {"is_publishing": _is_publishing}

@router.post("/api/system/sync/abort", dependencies=[Depends(verify_token)])
async def abort_sync() -> Dict[str, Any]:
    """🛑 [V79.0] 中止全量同步接口"""
    engine = get_global_engine()
    if not engine:
        return {"status": "error", "reason": "Engine not ready"}
    
    # 开启中止信号
    engine.abort_sync = True

    # 清空后台排队队列
    try:
        from core.runtime.orchestrator import _pending_sync_queue
        _pending_sync_queue.clear()
    except Exception:
        pass
    
    # 清空并发执行池中挂起的工作
    from core.logic.orchestration.task_orchestrator import global_executor, ai_executor, asset_executor
    global_executor.cancel_all_pending()
    ai_executor.cancel_all_pending()
    asset_executor.cancel_all_pending()
    
    tlog.warning("🛑 [UI] 已接收到停止同步指令，已向执行器广播中止信号并清空待处理队列。")
    return {"status": "aborted"}

@router.get("/api/system/theme/slots", dependencies=[Depends(verify_token)])
def get_theme_slots() -> Dict[str, Any]:
    """🚀 [V75.0] 动态探测当前主题/SSG 引擎支持的页面模板槽位"""
    engine = get_global_engine()
    if not engine or not hasattr(engine, 'ssg_adapter') or not engine.ssg_adapter:
        return {"slots": {}}
    
    try:
        return {"slots": engine.ssg_adapter.get_feature_slots()}
    except Exception:
        return {"slots": {}}
