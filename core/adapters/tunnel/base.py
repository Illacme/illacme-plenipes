# -*- coding: utf-8 -*-
"""
🛰️ [V126.0] Illacme Plenipes - Tunnel Adapter Base Contracts
模块职责：定义公网与局域网网络穿透驱动的最高抽象基类与动态注册中枢。
🛡️ [SOP-01 规范]：单文件代码行数严格 ≤ 300 行。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type


class BaseTunnelAdapter(ABC):
    """💎 网络穿透适配器抽象基座契约"""

    # 插件唯一标识符 (小写蛇形，如 "pinggy", "cloudflare")
    PLUGIN_ID: str = ""
    # 界面友好展示名
    DISPLAY_NAME: str = ""
    # 插件描述信息
    DESCRIPTION: str = ""
    # 所属插件大类
    CATEGORY: str = "tunnel"
    # 版本标识
    VERSION: str = "V1.0"
    # 是否支持通过表单或抽屉进行配置 (若为 False 则为免配置开箱即用型)
    HAS_CONFIG: bool = False

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._process = None
        self._public_url: Optional[str] = None
        self._start_time: float = 0

    @abstractmethod
    def start_tunnel(self, local_port: int, timeout_seconds: int = 15) -> Dict[str, Any]:
        """
        🚀 建立公网穿透通道
        :param local_port: 本地待反代服务端口 (如 43212)
        :param timeout_seconds: 最大握手超时秒数
        :return: {"is_running": bool, "public_url": Optional[str], "provider": str, "error": Optional[str]}
        """
        pass

    @abstractmethod
    def stop_tunnel(self) -> Dict[str, Any]:
        """🔒 关闭并注销当前公网穿透通道"""
        pass

    @abstractmethod
    def probe(self) -> Dict[str, Any]:
        """
        ⚡ 物理连通性与底层组件探测
        :return: {"success": bool, "healthy": bool, "message": str, "details": Optional[dict]}
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        """获取当前适配器穿透状态"""
        is_alive = bool(self._process and getattr(self._process, "poll", lambda: None)() is None and self._public_url)
        return {
            "is_running": is_alive,
            "public_url": self._public_url if is_alive else None,
            "provider": self.PLUGIN_ID,
        }


class TunnelRegistry:
    """🛰️ 网络穿透驱动容器中枢"""

    _registry: Dict[str, Type[BaseTunnelAdapter]] = {}

    @classmethod
    def register(cls, plugin_cls: Type[BaseTunnelAdapter]) -> None:
        """注册一个穿透驱动类"""
        if not plugin_cls or not getattr(plugin_cls, "PLUGIN_ID", None):
            return
        cls._registry[plugin_cls.PLUGIN_ID.lower()] = plugin_cls

    @classmethod
    def get(cls, plugin_id: str) -> Optional[Type[BaseTunnelAdapter]]:
        """获取指定驱动类"""
        return cls._registry.get(plugin_id.lower() if plugin_id else "")

    @classmethod
    def list_all(cls) -> Dict[str, Type[BaseTunnelAdapter]]:
        """获取所有已注册的穿透驱动映射"""
        return dict(cls._registry)

    @classmethod
    def get_default_driver_id(cls) -> str:
        """获取系统首选穿透驱动 ID (优先 cloudflare，备选 pinggy)"""
        if "cloudflare" in cls._registry:
            import shutil, os
            if shutil.which("cloudflared") or os.path.exists(os.path.expanduser("~/.plenipes/bin/cloudflared")):
                return "cloudflare"
        if "pinggy" in cls._registry:
            return "pinggy"
        return next(iter(cls._registry.keys()), "")
