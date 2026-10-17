# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Test Suite for Auto-Update Installer & Self-Restart Pipeline
测试目标：
1. 验证 UpdateInstaller 进度计算与状态机 (idle -> downloading -> ready -> applying)
2. 验证 UpdateInstaller 流式分块下载与 part 临时文件重命名逻辑
3. 验证 /api/system/update/download, /api/system/update/progress, /api/system/update/apply 端点逻辑
🛡️ [SOP-01 规范]：单文件行数严格 ≤ 300 行。
"""

import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from core.runtime.update_installer import UpdateInstaller
from services.api.server import app


def test_update_installer_initial_progress():
    """验证更新安装引擎初始状态"""
    with UpdateInstaller._lock:
        UpdateInstaller._status = "idle"
        UpdateInstaller._downloaded_bytes = 0
        UpdateInstaller._total_bytes = 0
        UpdateInstaller._percent = 0.0
        UpdateInstaller._speed_mb = 0.0
        UpdateInstaller._error_message = ""
        UpdateInstaller._downloaded_file_path = None

    prog = UpdateInstaller.get_progress()
    assert prog["status"] == "idle"
    assert prog["percent"] == 0.0
    assert prog["is_ready"] is False


def test_update_installer_download_worker_success():
    """验证后台下载线程流式下载与重命名机制"""
    temp_dir = tempfile.mkdtemp()
    try:
        with patch.object(UpdateInstaller, "get_cache_dir", return_value=temp_dir):
            mock_data = b"MOCK_BINARY_PAYLOAD_FOR_AUTO_UPDATE" * 1024
            mock_resp = MagicMock()
            mock_resp.headers = {"content-length": str(len(mock_data))}
            mock_resp.read.side_effect = [mock_data[:1024], mock_data[1024:], b""]
            mock_resp.__enter__.return_value = mock_resp

            with patch("urllib.request.urlopen", return_value=mock_resp):
                UpdateInstaller._download_worker(
                    url="https://github.com/test/release/download/v1.8.0/Illacme-macOS.dmg",
                    version="v1.8.0",
                    custom_filename="test_update.dmg"
                )

            prog = UpdateInstaller.get_progress()
            assert prog["status"] == "ready"
            assert prog["percent"] == 100.0
            assert prog["is_ready"] is True
            assert os.path.exists(prog["file_path"])
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_api_update_endpoints():
    """验证 FastAPI 静默升级三部曲端点契约"""
    client = TestClient(app)

    # 1. 验证下载启动
    with patch.object(UpdateInstaller, "start_download", return_value={"success": True, "message": "已在后台启动静默下载", "status": "downloading"}):
        resp = client.post("/api/system/update/download", json={"download_url": "https://example.com/asset.dmg", "version": "v1.8.0"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    # 2. 验证进度轮询
    with patch.object(UpdateInstaller, "get_progress", return_value={"status": "downloading", "percent": 45.5, "speed_mb": 2.4, "is_ready": False}):
        resp = client.get("/api/system/update/progress")
        assert resp.status_code == 200
        data = resp.json()
        assert data["percent"] == 45.5
        assert data["speed_mb"] == 2.4

    # 3. 验证应用升级并重启
    with patch.object(UpdateInstaller, "apply_and_restart", return_value={"success": True, "message": "正在执行静默替换并自动重启客户端..."}):
        resp = client.post("/api/system/update/apply")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
