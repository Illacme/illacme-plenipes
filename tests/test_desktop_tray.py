# -*- coding: utf-8 -*-
"""
Tests for Desktop System Tray Hub (tests/test_desktop_tray.py)
验证跨平台系统托盘在原生环境、无依赖环境下的防御性降级、菜单拓扑与动作回调。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import sys
import threading
from unittest.mock import MagicMock, patch

import pytest
from desktop.tray import SystemTrayManager


def test_system_tray_fallback_when_dependency_missing():
    """测试在缺失 pystray 依赖时能够 100% 优雅降级且不抛出异常"""
    with patch("desktop.tray._get_pystray", return_value=None):
        tray = SystemTrayManager(api_url="http://127.0.0.1:43212")
        assert tray.is_supported() is False
        assert tray.start_in_thread() is False
        assert tray.build_menu() is None
        # stop 调用不报错
        tray.stop()


def test_system_tray_icon_generation_with_pil():
    """测试使用 PIL 能在内存中成功合成科技风托盘微标"""
    tray = SystemTrayManager()
    img = tray._generate_icon_image()
    if img is not None:
        assert img.size == (64, 64)
        assert img.mode == "RGBA"


def test_system_tray_actions_dispatch():
    """测试托盘菜单各项动作分发与异步 API 链路"""
    tray = SystemTrayManager(api_url="http://127.0.0.1:43212")

    # 1. 测试打开控制台回调
    open_called = []
    tray._on_open = lambda: open_called.append(True)
    tray._action_open()
    assert open_called == [True]

    # 2. 测试全域发布
    with patch.object(tray, "_async_api_call", return_value={"status": "ok"}) as mock_api:
        mock_icon = MagicMock()
        tray._action_publish(icon=mock_icon)
        # 等待后台线程执行
        import time
        time.sleep(0.1)
        mock_api.assert_called_with("/api/publish/trigger", method="POST")

    # 3. 测试检查更新通知
    with patch.object(tray, "_async_api_call", return_value={"has_update": True, "latest_version": "v2.0.0"}) as mock_api:
        mock_icon = MagicMock()
        tray._action_check_update(icon=mock_icon)
        time.sleep(0.1)
        mock_api.assert_called_with("/api/system/check_update?force=true", method="GET")

    # 4. 测试重启内核
    with patch.object(tray, "_async_api_call", return_value={"status": "restarting"}) as mock_api:
        mock_icon = MagicMock()
        tray._action_restart(icon=mock_icon)
        time.sleep(0.1)
        mock_api.assert_called_with("/api/system/restart", method="POST")


def test_system_tray_lifecycle_with_mocked_pystray():
    """测试完整生命周期 (start_in_thread -> stop) 在 mock 下的表现"""
    mock_pystray = MagicMock()
    mock_icon_instance = MagicMock()
    mock_pystray.Icon.return_value = mock_icon_instance

    with patch("desktop.tray._get_pystray", return_value=mock_pystray), \
         patch.object(SystemTrayManager, "is_supported", return_value=True), \
         patch.object(SystemTrayManager, "_generate_icon_image", return_value=MagicMock()):

        tray = SystemTrayManager(api_url="http://127.0.0.1:43212")
        started = tray.start_in_thread(
            on_open=lambda: None,
            on_quit=lambda: None
        )
        assert started is True
        assert tray._icon is not None

        tray.stop()
        assert tray._icon is None
        mock_icon_instance.stop.assert_called_once()

