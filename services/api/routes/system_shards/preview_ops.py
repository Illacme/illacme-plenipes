# -*- coding: utf-8 -*-
"""
⚡ [V74.8] System Preview Operations Shard
职责：提供本地静态/框架实时预览服务的全生命周期编排与一键点火切换。
"""

import time
from typing import Optional, Dict, Any
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.utils.tracing import tlog
from core.utils.event_bus import bus


def _get_engine():
    """获取全局引擎实例，优先兼容外部对主模块的动态 patch / mock"""
    try:
        import services.api.routes.system as parent_mod
        if hasattr(parent_mod, "get_global_engine"):
            return parent_mod.get_global_engine()
    except Exception:
        pass
    from core.runtime.engine_singleton import get_global_engine
    return get_global_engine()


class SwitchAndLaunchPreviewRequest(BaseModel):
    theme_id: str
    imprint_id: Optional[str] = "default"
    port: Optional[int] = None
    allow_fallback: Optional[bool] = True
    sync_vault: Optional[bool] = True


def switch_and_launch_preview_logic(req: SwitchAndLaunchPreviewRequest) -> Any:
    """⚡ [工业级编排] 切换主题并一键点火 DevServer 预览"""
    engine = _get_engine()
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    from core.runtime.infrastructure.theme_orchestrator import theme_orchestrator

    imprint_id = req.imprint_id or getattr(engine.config, "active_imprint", "default") or "default"

    # 1. 物理持久化与全链路在线热重构
    try:
        from services.api.routes.gov.config_shards.config_sync_ops import process_config_sync
        from services.api.routes.gov.config_shards.config_persistence_ops import persist_config_to_disk
        from services.api.routes.gov.config_shards.config_reload_ops import live_reload_engine_config

        update_payload = {"active_theme": req.theme_id}
        routing_groups, err_response = process_config_sync(engine, update_payload, imprint_id=imprint_id)
        if err_response:
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


def restart_preview_logic() -> Dict[str, Any]:
    """🚀 [Orchestrator 桥接] 工业级增强型重启预览"""
    engine = _get_engine()
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


async def stop_preview_logic() -> Dict[str, str]:
    """🛑 [Orchestrator 桥接] 停止预览服务"""
    engine = _get_engine()
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    from core.runtime.infrastructure.theme_orchestrator import theme_orchestrator
    theme_orchestrator.shutdown_all()
    if "preview" in engine.services:
        engine.services["preview"].update({"status": "offline", "port": theme_orchestrator.active_port, "start_time": 0.0})
    bus.emit("UI_TERMINAL_DATA", type="LOG", data="⏹️ [系统感知] 预览服务器已物理停机，端口已安全释放。")
    return {"status": "success", "message": "Preview server stopped."}


def get_preview_logs_logic() -> Dict[str, Any]:
    """📋 [Orchestrator 桥接] 获取预览服务最新采样日志"""
    from core.runtime.infrastructure.theme_orchestrator import theme_orchestrator
    return {
        "status": "success",
        "logs": list(theme_orchestrator.log_ring_buffer),
        "theme": theme_orchestrator.active_theme,
        "port": theme_orchestrator.active_port,
        "is_alive": bool(theme_orchestrator.active_process and theme_orchestrator.active_process.poll() is None)
    }


def get_preview_status_logic() -> Dict[str, Any]:
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
