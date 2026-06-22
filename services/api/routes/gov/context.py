# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Context & System Discovery Routes
职责：承载系统上下文、插件发现、配置审计及健康报告的 API 接口。
架构：已从 governance.py 物理降解，实现业务逻辑的原子化隔离。
"""

from fastapi import APIRouter, Depends
from typing import Optional
from ..system import verify_token
from .context_shards.context_ops import (
    get_system_context_impl,
    get_lessons_impl,
    get_sync_stats_impl,
    get_health_report_impl,
    get_pulse_impl
)
from .context_shards.config_ops import get_full_config_impl
from .context_shards.plugin_ops import (
    list_active_plugins_impl,
    probe_plugin_impl,
    toggle_plugin_impl,
    dry_run_plugin_impl,
    install_plugin_deps_impl
)

router = APIRouter()

@router.get("/api/system/context", dependencies=[Depends(verify_token)])
def get_system_context():
    """获取系统上下文"""
    return get_system_context_impl()

@router.get("/api/governance/lessons", dependencies=[Depends(verify_token)])
def get_lessons():
    """获取治理经验库"""
    return get_lessons_impl()

@router.get("/api/governance/sync-stats", dependencies=[Depends(verify_token)])
def get_sync_stats():
    """获取分发同步统计数据"""
    return get_sync_stats_impl()

@router.get("/api/governance/health-report", dependencies=[Depends(verify_token)])
def get_health_report():
    """获取治理健康度报告"""
    return get_health_report_impl()

@router.get("/api/system/config", dependencies=[Depends(verify_token)])
def get_full_config(level: str = "merged", imprint_id: Optional[str] = None):
    """获取全量系统配置信息"""
    return get_full_config_impl(level, imprint_id)

@router.get("/api/plugins/list", dependencies=[Depends(verify_token)])
def list_active_plugins():
    """列出全域活动状态的插件"""
    return list_active_plugins_impl()

@router.post("/api/plugins/probe", dependencies=[Depends(verify_token)])
async def probe_plugin(payload: dict):
    """探测指定插件的健康度"""
    return await probe_plugin_impl(payload)

@router.post("/api/plugins/toggle", dependencies=[Depends(verify_token)])
async def toggle_plugin(payload: dict):
    """切换插件的物理驱动加载状态"""
    return await toggle_plugin_impl(payload)

@router.post("/api/plugins/dry-run", dependencies=[Depends(verify_token)])
async def dry_run_plugin(payload: dict):
    """测试自检校验仿真测试接口"""
    return await dry_run_plugin_impl(payload)

@router.post("/api/plugins/install-deps", dependencies=[Depends(verify_token)])
async def install_plugin_deps(payload: dict):
    """一键安装缺失的外部库物理依赖"""
    return await install_plugin_deps_impl(payload)

@router.get("/api/governance/pulse", dependencies=[Depends(verify_token)])
def get_pulse():
    """获取治理中枢的心跳状态脉冲"""
    return get_pulse_impl()

