# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Desktop Application Suite
模块职责：提供跨平台独立桌面可执行客户端启动入口与原生窗口生命周期管控。
"""

from .app import run_desktop_app
from .packager import DesktopPackager

__all__ = ["run_desktop_app", "DesktopPackager"]
