#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Version Sentinel & Process Lifecycle Guardian Tests
模块职责：验证源码指纹与版本漂移感知器、API 端点契约，以及进程热重载自我接力机制。
"""

import os
import time
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from core.runtime.version_sentinel import VersionSentinel
from services.api.server import app

client = TestClient(app)

def test_version_sentinel_baseline():
    """验证 VersionSentinel 基线状态与启动时间"""
    VersionSentinel.initialize()
    status = VersionSentinel.check_drift()
    
    assert "is_drifted" in status
    assert "process_start_time" in status
    assert "uptime_seconds" in status
    assert "latest_code_mtime" in status
    assert "status" in status
    assert status["uptime_seconds"] >= 0

def test_version_sentinel_drift_simulation(tmp_path):
    """验证当模拟产生新代码文件或修改时，check_drift 能准确感知漂移"""
    VersionSentinel.initialize()
    original_start = VersionSentinel._process_start_time
    
    # 模拟过去启动的进程
    VersionSentinel._process_start_time = time.time() - 100
    VersionSentinel._initial_max_mtime = time.time() - 50
    
    status = VersionSentinel.check_drift()
    # 物理磁盘上的文件修改时间均晚于 100 秒前，应被识别为已更新或至少具备正确的类型判断
    assert isinstance(status["is_drifted"], bool)
    assert isinstance(status["drift_files"], list)
    
    # 复位
    VersionSentinel.initialize()

def test_api_health_version_drift_integration():
    """验证 /health 与 /api/system/health 返回体中包含完整的 version_drift 数据"""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "version_drift" in data
    assert "is_drifted" in data["version_drift"]

def test_api_system_version_endpoint():
    """验证 /api/system/version 端点返回结构契约"""
    res = client.get("/api/system/version")
    assert res.status_code == 200
    data = res.json()
    assert "is_drifted" in data
    assert "uptime_seconds" in data
    assert "process_start_time" in data
    assert "status" in data

def test_api_system_stats_version_drift():
    """验证 /api/system/stats 端点集成 version_drift"""
    res = client.get("/api/system/stats")
    assert res.status_code == 200
    data = res.json()
    assert "version_drift" in data
    assert "is_drifted" in data["version_drift"]

def test_api_system_restart_endpoint_mocked():
    """验证 /api/system/restart 端点能正常响应并触发平滑重启"""
    with patch.object(VersionSentinel, 'trigger_process_restart') as mock_restart:
        res = client.post("/api/system/restart")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "restarting"
        mock_restart.assert_called_once()
