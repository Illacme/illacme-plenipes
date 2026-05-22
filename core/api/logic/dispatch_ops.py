#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V68.0] Illacme Plenipes - Dispatch Operations Hub Facade
职责：中枢代理层，对外暴露 100% 兼容的接口。
"""

from .dispatch_ops_shards.telemetry_ops import get_dispatch_status_logic
from .dispatch_ops_shards.daemon_ops import toggle_lab_logic
from .dispatch_ops_shards.pipeline_ops import trigger_re_dispatch_logic, destroy_artifact_logic

def get_dispatch_status_facade(engine, doc_id: str) -> dict:
    """物理感应与多语种遥测分析门面中介"""
    return get_dispatch_status_logic(engine, doc_id)

def toggle_lab_facade(engine) -> dict:
    """本地 DevServer 预览引擎调度门面中介"""
    return toggle_lab_logic(engine)

def trigger_re_dispatch_facade(engine, doc_id: str, req: dict) -> dict:
    """管线异步重分发编译分发门面中介"""
    return trigger_re_dispatch_logic(engine, doc_id, req)

def destroy_artifact_facade(engine, doc_id: str) -> dict:
    """出版产物彻底物理销毁与目录自愈门面中介"""
    return destroy_artifact_logic(engine, doc_id)
