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
    if not engine or not engine.config.system.api_token:
        return
    if x_token != engine.config.system.api_token:
        from core.utils.event_bus import bus
        bus.emit("SECURITY_ALERT", category="API_TOKEN_EXPIRED", message="接口访问认证失败：检测到未授权或非法的令牌（API Token）尝试跨站越权访问控制台。")
        raise HTTPException(status_code=403, detail="Unauthorized")

from services.api.schemas import SystemHealthResponse, HealthMatrixResponse

@router.get("/api/system/health", response_model=SystemHealthResponse)
def health_check() -> SystemHealthResponse:
    """🚀 [P1 规范统一] 系统全息健康检查端点"""
    engine = get_global_engine()
    if not engine:
        return SystemHealthResponse(
            status="starting",
            engine="Illacme-plenipes",
            imprint=None,
            services={}
        )
    services_dict = engine.services if isinstance(engine.services, dict) else {}
    return SystemHealthResponse(
        status="online",
        engine="Illacme-plenipes",
        imprint=getattr(engine, "imprint_id", None),
        services=services_dict
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
        return {"error": "Engine not initialized"}
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
        "timestamp": time.time()
    }

@router.post("/api/system/shutdown", dependencies=[Depends(verify_token)])
def shutdown() -> Dict[str, str]:
    """安全关闭系统"""
    os.kill(os.getpid(), signal.SIGINT)
    return {"status": "accepted"}

@router.post("/api/system/preview/restart", dependencies=[Depends(verify_token)])
def restart_preview() -> Dict[str, str]:
    """🚀 [V55.8] 工业级增强型重启：支持依赖自愈与日志实时穿透"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    is_framework = os.path.exists(os.path.join(theme_dir, "package.json"))
    
    from core.utils.dev_server import DevServer, FrameworkDevServer
    srv = getattr(engine, 'preview_server', None)
    p_dir = engine.paths.get('site_dir') or engine.paths.get('target_base')
    is_diff = srv and (not isinstance(srv, FrameworkDevServer if is_framework else DevServer) or srv.directory != (theme_dir if is_framework else p_dir))
    if is_diff:
        try:
            engine.preview_server.stop()
            time.sleep(0.5)
        except: pass
        engine.preview_server = None
    if not srv or is_diff:
        port = getattr(engine.config.system, 'serve_port', 43213)
        cmd = "npm run start -- --port {port}" if os.path.exists(os.path.join(theme_dir, "docusaurus.config.js")) else "npm run dev -- --port {port}"
        engine.preview_server = FrameworkDevServer(directory=theme_dir, command=cmd, port=port) if is_framework else DevServer(directory=p_dir, port=port)
    
    try:
        if engine.preview_server:
            try:
                engine.preview_server.stop()
                time.sleep(1.0)
            except: pass
            
        def terminal_broadcaster(line: str) -> None:
            tlog.info(f"🛰️ [终端采样] {line}")
            bus.emit("UI_TERMINAL_DATA", type="LOG", data=line)

        if hasattr(engine.preview_server, 'start_with_callback'):
            success = engine.preview_server.start_with_callback(callback=terminal_broadcaster)
        else:
            success = engine.preview_server.start(blocking=False)
            if success:
                bus.emit("UI_TERMINAL_DATA", type="LOG", data="🚀 [静态预览] 零依赖静态资源容器点火中...")
                bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"📂 [静态预览] 物理映射目录: {engine.preview_server.directory}")
                bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"🟢 [静态预览] Local: http://localhost:{engine.preview_server.port}")
            
        if success:
            engine.services["preview"].update({
                "status": "running",
                "port": engine.preview_server.port,
                "start_time": time.time(),
                "mode": "framework" if is_framework else "static"
            })
            return {"status": "success", "message": "Preview server ignition started."}
        else:
            raise HTTPException(status_code=500, detail="Failed to start preview server")
    except Exception as e:
        import traceback
        f = open("/Volumes/Notebook/omni-hub/illacme-plenipes/scratch/restart_error.log", "w")
        traceback.print_exc(file=f)
        f.close()
        raise HTTPException(status_code=500, detail=f"Restart failed: {str(e)}")


@router.post("/api/system/preview/stop", dependencies=[Depends(verify_token)])
def stop_preview() -> Dict[str, str]:
    """⏹️ 安全停机"""
    engine = get_global_engine()
    if not engine: raise HTTPException(status_code=400, detail="Engine not initialized")
    try:
        if getattr(engine, 'preview_server', None):
            engine.preview_server.stop()
            engine.services["preview"].update({"status": "offline", "port": engine.preview_server.port, "start_time": 0.0})
            bus.emit("UI_TERMINAL_DATA", type="LOG", data="⏹️ [系统感知] 预览服务器已物理停机，端口已释放。")
        return {"status": "success", "message": "Preview server stopped."}
    except Exception as e: raise HTTPException(status_code=500, detail=f"Stop failed: {str(e)}")

@router.get("/api/system/health/matrix", dependencies=[Depends(verify_token)], response_model=HealthMatrixResponse)
def get_health_matrix() -> HealthMatrixResponse:
    """🚀 [P1 规范统一] 获取系统组件全息健康矩阵"""
    matrix = ComponentMonitor.get_matrix()
    return HealthMatrixResponse(
        engine=matrix.get("engine", {"status": "offline", "label": "核心引擎", "health": 0}),
        onboarding=matrix.get("onboarding", {"status": "offline", "label": "版图向导", "health": 0}),
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
    """🚀 [V55.0] 远程点火版图向导"""
    if ComponentMonitor.check_port(43211):
        return {"status": "already_running"}
    from services.wizard.wizard_server import start_wizard_server
    threading.Thread(target=start_wizard_server, kwargs={"port": 43211}, daemon=True).start()
    return {"status": "started"}

@router.post("/api/system/wizard/stop", dependencies=[Depends(verify_token)])
async def stop_wizard() -> Dict[str, str]:
    """🛑 [V55.0] 销毁版图向导"""
    try:
        import urllib.request
        req = urllib.request.Request("http://127.0.0.1:43211/api/shutdown", method="POST")
        with urllib.request.urlopen(req, timeout=2.0): pass
        return {"status": "stopped"}
    except Exception:
        return {"status": "stopped", "note": "Service may already be down"}

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
async def trigger_sync(dry_run: bool = False, force: bool = False, sandbox: bool = False) -> Dict[str, Any]:
    """🚀 [V51.0] 全球同步点火接口：驱动编排中枢执行全量同步"""
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
    future_id = start_asynchronous_sync(engine, dry_run=dry_run, force=force, sandbox=sandbox)
    
    if future_id is None or future_id == 0:
        return {"status": "rejected", "reason": "Already publishing"}
    
    return {
        "status": "started",
        "future_id": future_id,
        "mode": "asynchronous"
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
