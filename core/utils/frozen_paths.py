# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Frozen Path Resolver & Asset Anchor
模块职责：统一解决源码运行态与桌面单体打包态 (PyInstaller _MEIPASS) 下的资源定位差异。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import sys
from typing import Optional


class FrozenPathResolver:
    """🏛️ 运行时与打包态多态路径锚定中枢"""

    _cached_root: Optional[str] = None

    @classmethod
    def is_frozen(cls) -> bool:
        """判定当前是否运行在 PyInstaller / 二进制冻结打包环境中"""
        return bool(getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"))

    @classmethod
    def get_bundle_root(cls) -> str:
        """获取应用程序包自身所在的只读物理根目录"""
        if cls.is_frozen():
            return getattr(sys, "_MEIPASS", os.getcwd())
        if cls._cached_root:
            return cls._cached_root
        # 源码开发态：从 core/utils/ 回退两级至项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cls._cached_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
        return cls._cached_root

    @classmethod
    def get_dashboard_dir(cls) -> str:
        """获取仪表盘前端静态资源目录 (web/dashboard)"""
        bundle_root = cls.get_bundle_root()
        path = os.path.join(bundle_root, "web", "dashboard")
        if os.path.exists(path):
            return os.path.abspath(path)
        # 兜底源码相对路径
        fallback = os.path.abspath(os.path.join(os.getcwd(), "web", "dashboard"))
        return fallback if os.path.exists(fallback) else path

    @classmethod
    def get_themes_dir(cls) -> str:
        """获取只读官方主题母本目录 (themes)"""
        bundle_root = cls.get_bundle_root()
        path = os.path.join(bundle_root, "themes")
        if os.path.exists(path):
            return os.path.abspath(path)
        fallback = os.path.abspath(os.path.join(os.getcwd(), "themes"))
        return fallback if os.path.exists(fallback) else path

    @classmethod
    def get_user_workspace_dir(cls) -> str:
        """
        获取用户工作区持久化目录。
        在打包独立应用运行时，优先将用户数据保留在用户启动目录或当前工作区，
        杜绝应用升级导致用户文库与配置被覆盖清除。
        """
        # 环境变量显式指定优先
        custom_ws = os.environ.get("ILLACME_WORKSPACE")
        if custom_ws and os.path.exists(custom_ws):
            return os.path.abspath(custom_ws)
        return os.path.abspath(os.getcwd())

    @classmethod
    def resolve_asset_path(cls, relative_path: str) -> str:
        """解析打包资源文件的绝对物理路径"""
        bundle_root = cls.get_bundle_root()
        return os.path.abspath(os.path.join(bundle_root, relative_path))
