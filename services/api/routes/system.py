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
        raise HTTPException(status_code=403, detail="Unauthorized")

@router.get("/api/system/health")
def health_check() -> Dict[str, str]:
    """基础健康检查"""
    engine = get_global_engine()
    if not engine:
        return {"status": "starting", "engine": "Illacme-plenipes"}
    return {
        "status": "online",
        "engine": "Illacme-plenipes",
        "imprint": engine.imprint_id,
        "services": str(engine.services)
    }

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
    
    # 获取物理负载 (带防御保护)
    cpu_usage = 0.0
    memory_usage = 0.0
    try:
        import psutil
        cpu_usage = psutil.cpu_percent(interval=None)
        memory_usage = psutil.virtual_memory().percent
    except ImportError:
        pass
        
    return {
        "usage": engine.meter.get_summary_report(),
        "load": {
            "cpu": cpu_usage,
            "memory": memory_usage,
            "workers": len([t for t in global_executor.workers if t.is_alive()]) if hasattr(global_executor, 'workers') else 0
        },
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
    
    # 如果预览服务器实例不存在，尝试根据配置动态创建
    if not hasattr(engine, 'preview_server') or engine.preview_server is None:
        from core.utils.dev_server import DevServer, FrameworkDevServer
        port = getattr(engine.config.system, 'serve_port', 43213)
        if is_framework:
            cmd = "npm run dev -- --port {port}"
            if os.path.exists(os.path.join(theme_dir, "docusaurus.config.js")):
                cmd = "npm run start -- --port {port}"
            engine.preview_server = FrameworkDevServer(directory=theme_dir, command=cmd, port=port)
        else:
            preview_dir = engine.paths.get('site_dir') or engine.paths.get('target_base')
            engine.preview_server = DevServer(directory=preview_dir, port=port)
    
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
        raise HTTPException(status_code=500, detail=f"Restart failed: {str(e)}")

@router.get("/api/system/health/matrix", dependencies=[Depends(verify_token)])
def get_health_matrix() -> Dict[str, Dict[str, Any]]:
    """获取系统组件全息健康矩阵"""
    return ComponentMonitor.get_matrix()

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
    except:
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
    
    if future_id == 0:
        return {"status": "rejected", "reason": "Already publishing"}
    
    return {
        "status": "started",
        "future_id": future_id,
        "mode": "asynchronous"
    }

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
