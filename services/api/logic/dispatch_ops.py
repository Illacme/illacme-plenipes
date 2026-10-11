#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V68.0] Illacme Plenipes - Dispatch Operations Hub Facade
职责：中枢代理层，对外暴露 100% 兼容的接口。
"""

from .dispatch_ops_shards.telemetry_ops import get_dispatch_status_logic
from .dispatch_ops_shards.daemon_ops import toggle_lab_logic
from .dispatch_ops_shards.pipeline_ops import (
    trigger_re_dispatch_logic,
    destroy_artifact_logic,
    get_pending_syndication_logic,
    check_and_acquire_rate_limit,
    get_channel_rate_limit_status
)

def get_dispatch_status_facade(engine, doc_id: str, lang_code: str = None) -> dict:
    """物理感应与多语种遥测分析门面中介"""
    return get_dispatch_status_logic(engine, doc_id, lang_code=lang_code)

def toggle_lab_facade(engine) -> dict:
    """本地 DevServer 预览引擎调度门面中介"""
    return toggle_lab_logic(engine)

def trigger_re_dispatch_facade(engine, doc_id: str, req: dict) -> dict:
    """管线异步重分发编译分发门面中介"""
    return trigger_re_dispatch_logic(engine, doc_id, req)

def destroy_artifact_facade(engine, doc_id: str) -> dict:
    """出版产物彻底物理销毁与目录自愈门面中介"""
    return destroy_artifact_logic(engine, doc_id)

def get_pending_syndication_facade(engine) -> dict:
    """获取待同步至分发渠道的稿件信息门面中介"""
    return get_pending_syndication_logic(engine)

def check_channel_rate_limit_facade(doc_id: str, target_channel: str) -> tuple:
    """平台级社交渠道频控门禁中介"""
    return check_and_acquire_rate_limit(doc_id, target_channel)

def get_channel_rate_limit_status_facade(doc_id: str, target_channel: str) -> dict:
    """社交渠道频控状态查询中介"""
    return get_channel_rate_limit_status(doc_id, target_channel)

