# -*- coding: utf-8 -*-
"""
⚡ [V126.0] Bindery Public Tunnel Manager (Facade)
职责：作为移动端扫码下载业务与底层网络穿透驱动插件之间的门面中枢 (Facade)，
以及管理单点出版物 30 分钟限时防越权安全令牌。
规范：遵循工业主权架构，单文件行数严格 ≤ 300 行。
"""

import time
import secrets
import threading
from typing import Dict, Any, Optional

from core.adapters.tunnel import TunnelRegistry, BaseTunnelAdapter
from core.utils.tracing import tlog


class TunnelHub:
    """⚡ 零配置临时公网隧道与临时安全凭证单例门面中枢"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TunnelHub, cls).__new__(cls)
                cls._instance._init_hub()
            return cls._instance

    def _init_hub(self):
        self._active_adapter: Optional[BaseTunnelAdapter] = None
        self._process = None
        self._public_url: Optional[str] = None
        self._provider: Optional[str] = None
        self._start_time: float = 0
        self._tokens: Dict[str, Dict[str, Any]] = {}  # {token: {filename, expires_at}}

    def issue_token(self, filename: str, ttl_seconds: int = 1800) -> str:
        """为特定出版物签发一个安全的 30 分钟限时一次性/临时访问令牌"""
        self.cleanup_expired_tokens()
        token = secrets.token_urlsafe(24)
        self._tokens[token] = {
            "filename": filename,
            "expires_at": time.time() + ttl_seconds,
        }
        return token

    def verify_token(self, filename: str, token: Optional[str]) -> bool:
        """校验凭证有效性与目标文件契约"""
        if not token or token not in self._tokens:
            return False
        entry = self._tokens[token]
        if time.time() > entry["expires_at"]:
            self._tokens.pop(token, None)
            return False
        return entry["filename"] == filename

    def cleanup_expired_tokens(self):
        """清理已失效的历史临时凭证"""
        now = time.time()
        expired = [k for k, v in self._tokens.items() if now > v["expires_at"]]
        for k in expired:
            self._tokens.pop(k, None)

    def get_status(self) -> Dict[str, Any]:
        """获取当前公网隧道状态"""
        # 兼容旧版及单测直接注入 _process / _public_url
        if self._process and getattr(self._process, "poll", lambda: None)() is None and self._public_url:
            uptime = int(time.time() - self._start_time)
            return {
                "is_running": True,
                "public_url": self._public_url,
                "provider": self._provider or "tunnel",
                "uptime_seconds": uptime,
            }
        if not self._active_adapter:
            return {
                "is_running": False,
                "public_url": None,
                "provider": None,
                "uptime_seconds": 0,
            }
        status = self._active_adapter.get_status()
        is_alive = status.get("is_running", False)
        uptime = int(time.time() - self._start_time) if is_alive else 0
        return {
            "is_running": is_alive,
            "public_url": status.get("public_url") if is_alive else None,
            "provider": status.get("provider") if is_alive else None,
            "uptime_seconds": uptime,
        }

    def start_tunnel(self, port: int = 43212, timeout_seconds: int = 15) -> Dict[str, Any]:
        """唤醒临时公网隧道 (委托给当前已注册的首选穿透驱动)"""
        cur = self.get_status()
        if cur.get("is_running") and cur.get("public_url"):
            return cur

        self.stop_tunnel()
        last_error = ""

        # 1. 尝试 Cloudflare Argo Tunnel
        cf_cls = TunnelRegistry.get("cloudflare")
        if cf_cls:
            cf_adapter = cf_cls()
            probe_res = cf_adapter.probe()
            # 若本地已存在 cloudflared 组件，优先使用
            if probe_res.get("healthy"):
                res = cf_adapter.start_tunnel(local_port=port, timeout_seconds=timeout_seconds)
                if res.get("is_running"):
                    self._active_adapter = cf_adapter
                    self._start_time = time.time()
                    return self.get_status()
                last_error = res.get("error", "")

        # 2. 备选方案：尝试 Pinggy 原生 OpenSSH 反向代理
        pinggy_cls = TunnelRegistry.get("pinggy")
        if pinggy_cls:
            pinggy_adapter = pinggy_cls()
            res = pinggy_adapter.start_tunnel(local_port=port, timeout_seconds=timeout_seconds)
            if res.get("is_running"):
                self._active_adapter = pinggy_adapter
                self._start_time = time.time()
                return self.get_status()
            last_error = res.get("error", "") or last_error

        err_msg = last_error or "未能在本机找到可用的公网穿透组件 (可安装 cloudflared 获取最佳体验)"
        return {
            "is_running": False,
            "error": err_msg,
        }

    def stop_tunnel(self) -> Dict[str, Any]:
        """关闭并注销当前公网隧道，收缩回局域网隔离状态"""
        if self._active_adapter:
            try:
                self._active_adapter.stop_tunnel()
            except Exception as e:
                tlog.warning(f"⚠️ [公网隧道] 关闭适配器异常: {e}")
            self._active_adapter = None
        self._start_time = 0
        tlog.info("🔒 [公网隧道] 已安全关闭临时公网通道，收缩至局域网保护模式。")
        return {"is_running": False, "success": True}


def get_tunnel_hub() -> TunnelHub:
    """获取隧道管理器单例"""
    return TunnelHub()
