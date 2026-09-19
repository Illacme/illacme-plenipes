# -*- coding: utf-8 -*-
"""
⚙️ 系统路由 — RESTful API 系统健康与运维调度中枢 (Dispatch Hub)。
职责：提供引擎状态、版本信息与运行时诊断的 API 接口调度。
🛡️ [SOP-01 & SOP-02]：已原子化拆分至 system_shards/ 物理分片，彻底消除大单体红线。
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from core.runtime.engine_singleton import get_global_engine
from services.api.schemas import SystemHealthResponse, HealthMatrixResponse

from .system_shards import (
    verify_token,
    health_check_logic,
    get_system_status_logic,
    get_stats_logic,
    shutdown_logic,
    get_version_info_logic,
    restart_kernel_logic,
    get_health_matrix_logic,
    get_supported_languages_logic,
    pick_directory_logic,
    SwitchAndLaunchPreviewRequest,
    switch_and_launch_preview_logic,
    restart_preview_logic,
    stop_preview_logic,
    get_preview_logs_logic,
    get_preview_status_logic,
    precheck_sync_logic,
    suspend_watchdog_logic,
    resume_watchdog_logic,
    trigger_sync_logic,
    get_sync_status_logic,
    abort_sync_logic,
    install_theme_dependencies_logic,
    upgrade_theme_dependencies_logic,
    rollback_theme_config_logic,
    get_theme_slots_logic,
    start_wizard_logic,
    stop_wizard_logic,
)

router = APIRouter()


# 1. 系统全息健康、状态与资源端点
@router.get("/api/system/health", response_model=SystemHealthResponse)
def health_check() -> SystemHealthResponse:
    """🚀 [P1 规范统一] 系统全息健康检查端点 (含版本漂移感知)"""
    return health_check_logic()


@router.get("/api/system/status", dependencies=[Depends(verify_token)])
def get_system_status() -> Dict[str, Any]:
    """🚀 [V48.3] 全息状态诊断：返回服务状态、AI 排行榜与系统负载"""
    return get_system_status_logic()


@router.get("/api/system/stats", dependencies=[Depends(verify_token)])
def get_stats() -> Dict[str, Any]:
    """🚀 [V74.8] 物理资源采样：返回真实的 CPU、内存与计费数据"""
    return get_stats_logic()


@router.post("/api/system/shutdown", dependencies=[Depends(verify_token)])
def shutdown() -> Dict[str, str]:
    """安全关闭系统"""
    return shutdown_logic()


@router.get("/api/system/version", dependencies=[Depends(verify_token)])
def get_version_info() -> Dict[str, Any]:
    """🚀 [V85.0] 运行时源码指纹与版本漂移查询接口"""
    return get_version_info_logic()


@router.post("/api/system/restart", dependencies=[Depends(verify_token)])
def restart_kernel() -> Dict[str, str]:
    """🚀 [V85.0] 平滑热重启 API 核心引擎：释放端口并自我 execv 接力"""
    return restart_kernel_logic()


@router.get("/api/system/health/matrix", dependencies=[Depends(verify_token)], response_model=HealthMatrixResponse)
def get_health_matrix() -> HealthMatrixResponse:
    """🚀 [P1 规范统一] 获取系统组件全息健康矩阵"""
    return get_health_matrix_logic()


@router.get("/api/system/languages")
def get_supported_languages() -> Dict[str, List[Any]]:
    """🌍 [V55.3] 动态获取系统支持的全球语种矩阵"""
    return get_supported_languages_logic()


@router.post("/api/system/pick_directory", dependencies=[Depends(verify_token)])
async def pick_directory() -> Dict[str, Any]:
    """📂 [V75.6] 唤起操作系统原生文件夹拾取器，返回绝对路径"""
    return await pick_directory_logic()


# 2. 本地实时预览全生命周期编排端点
@router.post("/api/system/preview/switch-and-launch", dependencies=[Depends(verify_token)])
def switch_and_launch_preview(req: SwitchAndLaunchPreviewRequest) -> Dict[str, Any]:
    """⚡ [工业级编排] 切换主题并一键点火 DevServer 预览"""
    return switch_and_launch_preview_logic(req)


@router.post("/api/system/preview/restart", dependencies=[Depends(verify_token)])
def restart_preview() -> Dict[str, Any]:
    """🚀 [Orchestrator 桥接] 工业级增强型重启预览"""
    return restart_preview_logic()


@router.post("/api/system/preview/stop", dependencies=[Depends(verify_token)])
async def stop_preview() -> Dict[str, str]:
    """🛑 [Orchestrator 桥接] 停止预览服务"""
    return await stop_preview_logic()


@router.get("/api/system/preview/logs", dependencies=[Depends(verify_token)])
def get_preview_logs() -> Dict[str, Any]:
    """📋 [Orchestrator 桥接] 获取预览服务最新采样日志"""
    return get_preview_logs_logic()


@router.get("/api/system/preview/status", dependencies=[Depends(verify_token)])
def get_preview_status() -> Dict[str, Any]:
    """🔍 [Orchestrator 桥接] 查询本地预览服务实时运行状态与拓扑元数据"""
    return get_preview_status_logic()


# 3. 全局同步点火与监控狗管线端点
@router.post("/api/system/sync/precheck", dependencies=[Depends(verify_token)])
async def precheck_sync() -> Dict[str, Any]:
    """🚀 [V78.5] 毫秒级双段式预检接口：用于提供给 UI 拦截"""
    return await precheck_sync_logic()


@router.post("/api/system/watchdog/suspend", dependencies=[Depends(verify_token)])
async def suspend_watchdog() -> Dict[str, str]:
    """🚀 [V78.6] 挂起监控狗：阻止自动同步触发 (UI 独占模式)"""
    return await suspend_watchdog_logic()


@router.post("/api/system/watchdog/resume", dependencies=[Depends(verify_token)])
async def resume_watchdog() -> Dict[str, str]:
    """🚀 [V78.6] 唤醒监控狗：恢复自动同步"""
    return await resume_watchdog_logic()


@router.post("/api/system/sync/trigger", dependencies=[Depends(verify_token)])
async def trigger_sync(dry_run: bool = False, force: bool = False, sandbox: bool = False, local_only: bool = False, clear_cache: bool = False) -> Dict[str, Any]:
    """🚀 [V51.0] 全球同步点火接口：驱动编排中枢执行全量同步 / 发布预览"""
    return await trigger_sync_logic(dry_run=dry_run, force=force, sandbox=sandbox, local_only=local_only, clear_cache=clear_cache)


@router.get("/api/system/sync/status", dependencies=[Depends(verify_token)])
def get_sync_status() -> Dict[str, Any]:
    """🚀 [V78.8] 查询当前出版流水线是否在运行"""
    return get_sync_status_logic()


@router.post("/api/system/sync/abort", dependencies=[Depends(verify_token)])
async def abort_sync() -> Dict[str, Any]:
    """🛑 [V79.0] 中止全量同步接口"""
    return await abort_sync_logic()


# 4. 主题与向导生命周期管理端点
@router.post("/api/system/theme/install", dependencies=[Depends(verify_token)])
async def install_theme_dependencies() -> Dict[str, str]:
    """🚀 [V52.11] 自动化依赖安装接口"""
    return await install_theme_dependencies_logic()


@router.post("/api/system/theme/upgrade", dependencies=[Depends(verify_token)])
async def upgrade_theme_dependencies() -> Dict[str, str]:
    """🚀 [V65.0] 自动化版本升级接口"""
    return await upgrade_theme_dependencies_logic()


@router.post("/api/system/theme/rollback", dependencies=[Depends(verify_token)])
async def rollback_theme_config() -> Dict[str, Any]:
    """🚀 [V65.3] 物理快照回滚接口"""
    return await rollback_theme_config_logic()


@router.get("/api/system/theme/slots", dependencies=[Depends(verify_token)])
def get_theme_slots() -> Dict[str, Any]:
    """🚀 [V75.0] 动态探测当前主题/SSG 引擎支持的页面模板槽位"""
    return get_theme_slots_logic()


@router.post("/api/system/wizard/start", dependencies=[Depends(verify_token)])
async def start_wizard() -> Dict[str, str]:
    """🚀 [V55.0] 启动品牌向导服务"""
    return await start_wizard_logic()


@router.post("/api/system/wizard/stop", dependencies=[Depends(verify_token)])
async def stop_wizard() -> Dict[str, str]:
    """🛑 [V55.0] 停止品牌向导服务"""
    return await stop_wizard_logic()


__all__ = [
    "router",
    "verify_token",
    "health_check",
    "get_system_status",
    "get_stats",
    "shutdown",
    "get_version_info",
    "switch_and_launch_preview",
    "SwitchAndLaunchPreviewRequest",
    "restart_preview",
    "stop_preview",
    "get_preview_logs",
    "restart_kernel",
    "get_preview_status",
    "get_health_matrix",
    "get_supported_languages",
    "install_theme_dependencies",
    "upgrade_theme_dependencies",
    "rollback_theme_config",
    "start_wizard",
    "stop_wizard",
    "pick_directory",
    "precheck_sync",
    "suspend_watchdog",
    "resume_watchdog",
    "trigger_sync",
    "get_sync_status",
    "abort_sync",
    "get_theme_slots",
    "get_global_engine",
]
