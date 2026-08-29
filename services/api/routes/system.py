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
    if not engine or not getattr(engine, 'config', None) or not getattr(engine.config, 'system', None) or not getattr(engine.config.system, 'api_token', None):
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
    brand_theme_dir = os.path.join(getattr(engine, 'imprint_root', ''), "themes", engine.active_theme) if getattr(engine, 'imprint_root', None) else ""
    mother_theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    theme_dir = brand_theme_dir if (brand_theme_dir and os.path.exists(brand_theme_dir)) else mother_theme_dir
    
    # 🎯 准确判别是否为真实的 SSG 前端框架 DevServer 还是原生静态编译站点
    # 真实框架判定条件：必须存在框架特有的配置文件 (Docusaurus/VitePress/Nextra/Starlight)
    is_docusaurus = os.path.exists(os.path.join(theme_dir, "docusaurus.config.js")) or os.path.exists(os.path.join(mother_theme_dir, "docusaurus.config.js"))
    is_vitepress = os.path.exists(os.path.join(theme_dir, ".vitepress")) or os.path.exists(os.path.join(mother_theme_dir, ".vitepress"))
    is_nextra = os.path.exists(os.path.join(theme_dir, "theme.config.jsx")) or os.path.exists(os.path.join(theme_dir, "theme.config.tsx")) or os.path.exists(os.path.join(mother_theme_dir, "theme.config.jsx"))
    is_starlight = "starlight" in (engine.active_theme or "").lower() and (
        os.path.exists(os.path.join(theme_dir, "astro.config.mjs")) or os.path.exists(os.path.join(mother_theme_dir, "astro.config.mjs"))
    )

    has_package_json = os.path.exists(os.path.join(theme_dir, "package.json")) or os.path.exists(os.path.join(mother_theme_dir, "package.json"))
    is_framework = bool((is_docusaurus or is_vitepress or is_nextra or is_starlight) and has_package_json)
    
    from core.utils.dev_server import DevServer, FrameworkDevServer
    srv = getattr(engine, 'preview_server', None)
    p_dir = engine.paths.get('site_dir') or engine.paths.get('target_base')
    if p_dir:
        os.makedirs(p_dir, exist_ok=True)

    is_diff = srv and (not isinstance(srv, FrameworkDevServer if is_framework else DevServer) or srv.directory != (theme_dir if is_framework else p_dir))
    if is_diff:
        try:
            engine.preview_server.stop()
            time.sleep(0.5)
        except: pass
        engine.preview_server = None
    if not srv or is_diff:
        port = getattr(engine.config.system, 'serve_port', 43213)
        cmd = "npm run start -- --port {port}" if is_docusaurus else "npm run dev -- --port {port}"
        target_dir = theme_dir if (is_framework and os.path.exists(theme_dir)) else mother_theme_dir if is_framework else p_dir
        engine.preview_server = FrameworkDevServer(directory=target_dir, command=cmd, port=port) if is_framework else DevServer(directory=p_dir, port=port)
    
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
                bus.emit("UI_TERMINAL_DATA", type="LOG", data="🚀 [静态预览] 零依赖静态资源容器启动中...")
                bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"📂 [静态预览] 物理映射目录: {engine.preview_server.directory}")
                bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"🟢 [静态预览] Local: http://localhost:{engine.preview_server.port}")
            
        if success:
            engine.services["preview"].update({
                "status": "running",
                "port": engine.preview_server.port,
                "start_time": time.time(),
                "mode": "framework" if is_framework else "static"
            })
            return {"status": "success", "message": "Preview server started."}
        else:
            raise HTTPException(status_code=500, detail="Failed to start preview server")
    except Exception as e:
        import traceback
        f = open("/Volumes/Notebook/omni-hub/illacme-plenipes/scratch/restart_error.log", "w")
        traceback.print_exc(file=f)
        f.close()
        raise HTTPException(status_code=500, detail=f"Restart failed: {str(e)}")


@router.post("/api/system/preview/stop", dependencies=[Depends(verify_token)])
async def stop_preview() -> Dict[str, str]:
    """🛑 [V55.0] 停止预览服务"""
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
