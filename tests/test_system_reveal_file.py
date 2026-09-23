# -*- coding: utf-8 -*-
"""
Illacme Plenipes - System Reveal File Unit Tests
模块职责：验证原生文件定位 (Show in Finder / Explorer) 接口逻辑、跨平台调用与越权白名单防护。
🛡️ [SOP-01 规范]：单文件行数严格 ≤ 300 行。
"""

import os
import sys
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from services.api.server import app
from services.api.routes.system_shards.system_health_ops import reveal_file_logic


@pytest.fixture
def client():
    return TestClient(app)


def test_reveal_file_logic_invalid_param():
    """测试空参数或非字符串参数拦截"""
    res = reveal_file_logic("")
    assert res["success"] is False
    assert "无效" in res["error"]

    res_none = reveal_file_logic(None)
    assert res_none["success"] is False


def test_reveal_file_logic_not_exist():
    """测试文件不存在时的友好提示"""
    res = reveal_file_logic("dist/books/not_exist_file_9999.epub")
    assert res["success"] is False
    assert "不存在" in res["error"]


def test_reveal_file_logic_security_boundary(tmp_path):
    """测试越权或系统敏感路径白名单安全拦截 (SOP-04 & Rule #10)"""
    # 模拟一个位于系统外部的敏感文件
    outside_file = tmp_path / "sensitive.txt"
    outside_file.write_text("secret")

    # 尝试访问系统外部目录
    res = reveal_file_logic(str(outside_file))
    assert res["success"] is False
    assert "安全边界" in res["error"]


def test_reveal_file_logic_darwin_success(tmp_path):
    """测试 macOS 下调用 open -R 定位合法文件"""
    # 在当前合法的 dist 目录下创建测试文件
    dist_dir = os.path.abspath("dist/books")
    os.makedirs(dist_dir, exist_ok=True)
    test_book = os.path.join(dist_dir, "test_darwin.epub")
    with open(test_book, "w") as f:
        f.write("content")

    try:
        with patch("sys.platform", "darwin"), patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            res = reveal_file_logic("dist/books/test_darwin.epub")
            assert res["success"] is True
            assert "访达" in res["message"]
            mock_run.assert_called_once_with(["open", "-R", test_book], check=True)
    finally:
        if os.path.exists(test_book):
            os.remove(test_book)


def test_reveal_file_logic_windows_success():
    """测试 Windows 下调用 explorer /select 定位合法文件"""
    dist_dir = os.path.abspath("dist/books")
    os.makedirs(dist_dir, exist_ok=True)
    test_book = os.path.join(dist_dir, "test_win.pdf")
    with open(test_book, "w") as f:
        f.write("content")

    try:
        with patch("sys.platform", "win32"), patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            res = reveal_file_logic("dist/books/test_win.pdf")
            assert res["success"] is True
            assert "资源管理器" in res["message"]
            mock_run.assert_called_once_with(["explorer", f"/select,{test_book}"], check=True)
    finally:
        if os.path.exists(test_book):
            os.remove(test_book)


def test_reveal_file_api_endpoint(client):
    """测试 /api/system/reveal-file HTTP API 路由连通性"""
    dist_dir = os.path.abspath("dist/books")
    os.makedirs(dist_dir, exist_ok=True)
    test_book = os.path.join(dist_dir, "test_api.epub")
    with open(test_book, "w") as f:
        f.write("content")

    try:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            response = client.post("/api/system/reveal-file", json={"path": "dist/books/test_api.epub"})
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    finally:
        if os.path.exists(test_book):
            os.remove(test_book)
