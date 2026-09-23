# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Desktop Application Bootstrap & Packaging Test Suite
模块职责：全面验证桌面客户端路径自愈解析 (FrozenPathResolver)、单例锁生命周期、
双模态窗口调度以及 PyInstaller 打包构建参数规范。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import sys
import socket
import tempfile
from unittest.mock import patch, MagicMock
import pytest

from core.utils.frozen_paths import FrozenPathResolver
from desktop.app import (
    acquire_singleton_lock,
    release_singleton_lock,
    wait_for_api_ready,
    _launch_native_window,
    SINGLETON_PORT,
    API_PORT
)
from desktop.packager import DesktopPackager


def test_frozen_path_resolver_dev_mode():
    """验证在源码开发态下，正确回退解析项目根目录与核心资源"""
    with patch.object(sys, "frozen", False, create=True):
        assert not FrozenPathResolver.is_frozen()
        root = FrozenPathResolver.get_bundle_root()
        assert os.path.exists(root)
        dash_dir = FrozenPathResolver.get_dashboard_dir()
        assert os.path.exists(dash_dir)
        assert os.path.basename(dash_dir) == "dashboard"


def test_frozen_path_resolver_frozen_mock():
    """验证在 PyInstaller 冻结打包态下 (_MEIPASS)，优先锚定临时 Bundle 资源"""
    with tempfile.TemporaryDirectory() as fake_meipass:
        mock_web = os.path.join(fake_meipass, "web", "dashboard")
        mock_themes = os.path.join(fake_meipass, "themes")
        os.makedirs(mock_web, exist_ok=True)
        os.makedirs(mock_themes, exist_ok=True)

        with patch.object(sys, "frozen", True, create=True), \
             patch.object(sys, "_MEIPASS", fake_meipass, create=True):
            assert FrozenPathResolver.is_frozen()
            assert FrozenPathResolver.get_bundle_root() == fake_meipass
            assert FrozenPathResolver.get_dashboard_dir() == os.path.abspath(mock_web)
            assert FrozenPathResolver.get_themes_dir() == os.path.abspath(mock_themes)


def test_desktop_singleton_lock_lifecycle():
    """验证单例锁能够成功绑定，并在重复获取时被安全拦截"""
    test_port = 43219  # 使用独立测试端口防冲突
    try:
        # 第一次获取成功
        assert acquire_singleton_lock(port=test_port) is True
        # 第二次获取被拦截 (已有实例在运行)
        assert acquire_singleton_lock(port=test_port) is False
    finally:
        release_singleton_lock()

    # 释放后可再次获取
    try:
        assert acquire_singleton_lock(port=test_port) is True
    finally:
        release_singleton_lock()


def test_wait_for_api_ready():
    """验证 API 端口就绪探测逻辑"""
    # 模拟端口未开放时超时返回 False
    fake_port = 43218
    with patch("desktop.app.API_PORT", fake_port):
        assert wait_for_api_ready(timeout_sec=0.4) is False

    # 模拟本地起一个测试监听端口
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", fake_port))
    srv.listen(1)
    try:
        with patch("desktop.app.API_PORT", fake_port):
            assert wait_for_api_ready(timeout_sec=1.0) is True
    finally:
        srv.close()


def test_launch_native_window_fallback():
    """验证未安装 pywebview 时能优雅降级返回 False，而不是崩溃"""
    with patch.dict("sys.modules", {"webview": None}):
        res = _launch_native_window("http://127.0.0.1:43212/")
        assert res is False


def test_desktop_packager_assemble_args():
    """验证 PyInstaller 打包参数组装规范与关键隐藏依赖"""
    args = DesktopPackager.assemble_build_args(output_dir="dist/test_app")
    assert "pyinstaller" in args[0]
    assert "--windowed" in args
    assert "--name=Illacme-Plenipes" in args
    assert any("--distpath=dist/test_app" in a for a in args)

    # 断言关键数据包与动态隐藏依赖
    arg_str = " ".join(args)
    assert "web/dashboard" in arg_str
    assert "themes" in arg_str
    assert "fastapi" in arg_str
    assert "uvicorn.logging" in arg_str
    assert "cryptography" in arg_str
    assert "desktop/app.py" in arg_str or "desktop\\app.py" in arg_str


def test_desktop_packager_dry_run():
    """验证打包工坊 Dry-Run 校验流水线顺利通过"""
    res = DesktopPackager.execute_build(dry_run=True, output_dir="dist/desktop_test")
    assert res is True
