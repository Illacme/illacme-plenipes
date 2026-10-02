# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Test Suite for Auto-Update Sentinel & Release Checker
测试目标：
1. 验证 SemVer 解析算法与版本递增比对
2. 验证多平台专属安装包智能匹配规则 (DMG / Setup.exe / tar.gz)
3. 验证网络异常与降级兜底逻辑
4. 验证 /api/system/check_update API 端点响应结构
🛡️ [SOP-01 规范]：单文件行数严格 ≤ 300 行。
"""

import io
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from core.runtime.update_checker import UpdateChecker
from services.api.server import app


def test_semver_parsing_and_comparison():
    """验证语义化版本解析与比较"""
    assert UpdateChecker.parse_semver("v1.2.1") == (1, 2, 1)
    assert UpdateChecker.parse_semver("1.2") == (1, 2, 0)
    assert UpdateChecker.parse_semver("v2.0.0-rc1") == (2, 0, 0)

    # 比较最新版本是否更高
    assert UpdateChecker.is_newer_version("v1.2.2", "v1.2.1") is True
    assert UpdateChecker.is_newer_version("v2.0.0", "v1.9.9") is True
    assert UpdateChecker.is_newer_version("v1.2.1", "v1.2.1") is False
    assert UpdateChecker.is_newer_version("v1.1.0", "v1.2.0") is False


def test_platform_asset_detection():
    """验证根据不同宿主操作系统匹配推荐安装格式"""
    mock_assets = [
        {"name": "Illacme-Plenipes-Windows-x64.zip", "browser_download_url": "https://.../win.zip", "size": 10485760},
        {"name": "Illacme-Plenipes-Windows-x64-Setup.exe", "browser_download_url": "https://.../win-setup.exe", "size": 20971520},
        {"name": "Illacme-Plenipes-macOS-AppleSilicon-arm64.dmg", "browser_download_url": "https://.../mac.dmg", "size": 31457280},
        {"name": "Illacme-Plenipes-macOS-AppleSilicon-arm64.zip", "browser_download_url": "https://.../mac.zip", "size": 15728640},
        {"name": "Illacme-Plenipes-Linux-x64.tar.gz", "browser_download_url": "https://.../linux.tar.gz", "size": 41943040},
        {"name": "Illacme-Plenipes-Linux-x64.tar.gz.sha256", "browser_download_url": "https://.../linux.sha256", "size": 100},
    ]

    # 1. 模拟 macOS 环境
    with patch("platform.system", return_value="Darwin"):
        with patch("platform.machine", return_value="arm64"):
            asset = UpdateChecker.detect_platform_asset(mock_assets)
            assert asset is not None
            assert asset["name"] == "Illacme-Plenipes-macOS-AppleSilicon-arm64.dmg"
            assert "DMG" in asset["format_desc"]
            assert asset["size_mb"] == 30.0

    # 2. 模拟 Windows 环境
    with patch("platform.system", return_value="Windows"):
        asset = UpdateChecker.detect_platform_asset(mock_assets)
        assert asset is not None
        assert asset["name"] == "Illacme-Plenipes-Windows-x64-Setup.exe"
        assert "安装向导" in asset["format_desc"]

    # 3. 模拟 Linux 环境
    with patch("platform.system", return_value="Linux"):
        asset = UpdateChecker.detect_platform_asset(mock_assets)
        assert asset is not None
        assert asset["name"] == "Illacme-Plenipes-Linux-x64.tar.gz"


def test_update_checker_api_success():
    """验证通过 Mock 模拟 GitHub API 响应并探测新版本"""
    mock_gh_response = {
        "tag_name": "v9.9.9",
        "name": "Illacme Plenipes v9.9.9 里程碑",
        "published_at": "2026-10-02T12:00:00Z",
        "html_url": "https://github.com/Illacme/illacme-plenipes/releases/tag/v9.9.9",
        "body": "### ✨ 本次更新内容\n* 增强全平台桌面应用体验",
        "assets": [
            {
                "name": "Illacme-Plenipes-macOS-AppleSilicon-arm64.dmg",
                "browser_download_url": "https://download/v9.9.9/Illacme-Plenipes.dmg",
                "size": 52428800
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(mock_gh_response).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        with patch.object(UpdateChecker, "get_current_version", return_value="1.2.1"):
            with patch("platform.system", return_value="Darwin"):
                res = UpdateChecker.check_update(force=True)
                assert res["status"] == "success"
                assert res["current_version"] == "v1.2.1"
                assert res["latest_version"] == "v9.9.9"
                assert res["has_update"] is True
                assert res["recommended_asset"]["name"] == "Illacme-Plenipes-macOS-AppleSilicon-arm64.dmg"


def test_update_checker_offline_fallback():
    """验证网络异常时平滑降级，不抛出异常"""
    import urllib.error
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Network unreachable")):
        res = UpdateChecker.check_update(force=True)
        assert res["status"] == "offline_fallback"
        assert res["has_update"] is False
        assert "离线" in res["release_notes"]


def test_api_endpoint_check_update():
    """验证 FastAPI /api/system/check_update 端点集成测试"""
    client = TestClient(app)
    with patch.object(UpdateChecker, "check_update") as mock_chk:
        mock_chk.return_value = {
            "status": "success",
            "current_version": "v1.2.1",
            "latest_version": "v1.2.1",
            "has_update": False,
            "release_name": "Illacme Plenipes v1.2.1",
            "recommended_asset": None
        }
        resp = client.get("/api/system/check_update?force=true")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["current_version"] == "v1.2.1"
        assert data["has_update"] is False
