#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Event Signal Registry
模块职责：全域信号主权中心。
通过强类型枚举彻底杜绝“静默失效”风险。
"""
from enum import Enum

class EngineEvent(Enum):
    # 核心管线事件
    SYNC_STARTED = "sync_started"
    SYNC_COMPLETED = "sync_completed"

    # 算力事件
    AI_CALL_STARTED = "ai_call_started"
    AI_CALL_COMPLETED = "ai_call_completed"
    AI_CALL_FAILED = "ai_call_failed"

    # 缓存事件
    BLOCK_CACHE_HIT = "block_cache_hit"
    BLOCK_CACHE_MISS = "block_cache_miss"

    # 发布与分发事件
    ASSET_PUBLISHED = "asset_published"
    SYNDICATION_SUCCESS = "syndication_success"
    SYNDICATION_FAILED = "syndication_failed"

    # 治理事件
    HEALTH_CHECK_COMPLETED = "health_check_completed"
    DOCTOR_REPORT_READY = "doctor_report_ready"

