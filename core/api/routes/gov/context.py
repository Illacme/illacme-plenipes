# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Context & System Discovery Routes
职责：承载系统上下文、插件发现、配置审计及健康报告的 API 接口。
架构：已从 governance.py 物理降解，实现业务逻辑的原子化隔离。
"""

from fastapi import APIRouter, Depends
from typing import Optional
import os
from core.runtime.engine_singleton import get_global_engine
from ..system import verify_token
from core.config.config import CONFIG_NAME, CONFIG_LOCAL_NAME, IMPRINT_DIR, CONFIG_DIR, CONFIG_IMPRINT_NAME
from .context_shards.context_ops import (
    get_system_context_impl,
    get_lessons_impl,
    get_sync_stats_impl,
    get_health_report_impl
)
from .context_shards.config_ops import get_full_config_impl
from .context_shards.plugin_ops import (
    list_active_plugins_impl,
    probe_plugin_impl,
    toggle_plugin_impl,
    dry_run_plugin_impl
)

router = APIRouter()

@router.get("/api/system/context", dependencies=[Depends(verify_token)])
def get_system_context():
    return get_system_context_impl()

@router.get("/api/governance/lessons", dependencies=[Depends(verify_token)])
def get_lessons():
    return get_lessons_impl()

@router.get("/api/governance/sync-stats", dependencies=[Depends(verify_token)])
def get_sync_stats():
    return get_sync_stats_impl()

@router.get("/api/governance/health-report", dependencies=[Depends(verify_token)])
def get_health_report():
    return get_health_report_impl()

@router.get("/api/system/config", dependencies=[Depends(verify_token)])
def get_full_config(level: str = "merged", imprint_id: Optional[str] = None):
    return get_full_config_impl(level, imprint_id)

@router.get("/api/plugins/list", dependencies=[Depends(verify_token)])
def list_active_plugins():
    return list_active_plugins_impl()

@router.post("/api/plugins/probe", dependencies=[Depends(verify_token)])
async def probe_plugin(payload: dict):
    return await probe_plugin_impl(payload)

@router.post("/api/plugins/toggle", dependencies=[Depends(verify_token)])
async def toggle_plugin(payload: dict):
    return await toggle_plugin_impl(payload)

@router.post("/api/plugins/dry-run", dependencies=[Depends(verify_token)])
async def dry_run_plugin(payload: dict):
    return await dry_run_plugin_impl(payload)

