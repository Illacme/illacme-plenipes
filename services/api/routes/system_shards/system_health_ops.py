# -*- coding: utf-8 -*-
"""
⚙️ [V74.8] System Health & Info Operations Shard
职责：提供系统全息健康检查、状态诊断、物理资源采样与基础控制。
"""

import os
import time
import signal
import subprocess
import sys
from typing import Dict, Any, List

from core.logic.orchestration.task_orchestrator import global_executor
from core.utils.tracing import tlog
from core.logic.diagnostics.component_monitor import ComponentMonitor
from core.runtime.version_sentinel import VersionSentinel
from services.api.schemas import SystemHealthResponse, HealthMatrixResponse


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


def health_check_logic() -> SystemHealthResponse:
    """🚀 [P1 规范统一] 系统全息健康检查端点 (含版本漂移感知)"""
    engine = _get_engine()
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


def get_system_status_logic() -> Dict[str, Any]:
    """🚀 [V48.3] 全息状态诊断：返回服务状态、AI 排行榜与系统负载"""
    engine = _get_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    services = getattr(engine, "services", {}) or {}
    for name, s in services.items():
        if isinstance(s, dict) and s.get("start_time"):
            s["uptime"] = round(time.time() - s.get("start_time"), 1)

    from core.governance.health_registry import health_registry
    return {
        "services": services,
        "ai_nodes": health_registry.get_rankings(),
        "tasks": {
            "queued": global_executor._work_queue.qsize() if hasattr(global_executor, "_work_queue") else 0,
            "active": len([t for t in global_executor.workers if t.is_alive()]) if hasattr(global_executor, "workers") else 0
        },
        "timestamp": time.time()
    }


def get_stats_logic() -> Dict[str, Any]:
    """🚀 [V74.8] 物理资源采样：返回真实的 CPU、内存与计费数据"""
    engine = _get_engine()
    if not engine:
        return {"error": "Engine not initialized", "version_drift": VersionSentinel.check_drift()}
    cpu, mem = 0.0, 0.0
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
    except ImportError:
        pass
    workers = len([t for t in global_executor.workers if t.is_alive()]) if hasattr(global_executor, "workers") else 0
    return {
        "usage": engine.meter.get_summary_report(),
        "load": {"cpu": cpu, "memory": mem, "workers": workers},
        "version_drift": VersionSentinel.check_drift(),
        "timestamp": time.time()
    }


def shutdown_logic() -> Dict[str, str]:
    """安全关闭系统"""
    os.kill(os.getpid(), signal.SIGINT)
    return {"status": "accepted"}


def get_version_info_logic() -> Dict[str, Any]:
    """🚀 [V85.0] 运行时源码指纹与版本漂移查询接口"""
    return VersionSentinel.check_drift()


def restart_kernel_logic() -> Dict[str, str]:
    """🚀 [V85.0] 平滑热重启 API 核心引擎：释放端口并自我 execv 接力"""
    tlog.warning("🔄 [API] 收到平滑热重启指令，即将唤醒全新内核进程...")
    VersionSentinel.trigger_process_restart(delay_seconds=0.3)
    return {"status": "restarting", "message": "Kernel is gracefully restarting..."}


def get_health_matrix_logic() -> HealthMatrixResponse:
    """🚀 [P1 规范统一] 获取系统组件全息健康矩阵"""
    matrix = ComponentMonitor.get_matrix()
    return HealthMatrixResponse(
        engine=matrix.get("engine", {"status": "offline", "label": "核心引擎", "health": 0}),
        onboarding=matrix.get("onboarding", {"status": "offline", "label": "品牌向导", "health": 0}),
        preview=matrix.get("preview", {"status": "offline", "label": "预览服务", "health": 0})
    )


def get_supported_languages_logic() -> Dict[str, List[Any]]:
    """🌍 [V55.3] 动态获取系统支持的全球语种矩阵"""
    from core.utils.language_hub import LanguageHub
    return {"languages": LanguageHub.get_supported_matrix()}


async def pick_directory_logic() -> Dict[str, Any]:
    """📂 [V75.6] 唤起操作系统原生文件夹拾取器，返回绝对路径"""
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
