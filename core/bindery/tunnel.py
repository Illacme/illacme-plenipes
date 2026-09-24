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

    def get_status(self, verify_alive: bool = False) -> Dict[str, Any]:
        """获取当前公网隧道状态 (支持活性校验)"""
        # 兼容旧版及单测直接注入 _process / _public_url
        if self._process and getattr(self._process, "poll", lambda: None)() is None and self._public_url:
            uptime = int(time.time() - self._start_time)
            prov = self._provider or "tunnel"
            cls = TunnelRegistry.get(prov)
            prov_name = getattr(cls, "DISPLAY_NAME", prov.upper()) if cls else prov.upper()
            return {
                "is_running": True,
                "public_url": self._public_url,
                "provider": prov,
                "provider_name": prov_name,
                "uptime_seconds": uptime,
            }
        if not self._active_adapter:
            return {
                "is_running": False,
                "public_url": None,
                "provider": None,
                "provider_name": None,
                "uptime_seconds": 0,
            }
        status = self._active_adapter.get_status()
        is_alive = status.get("is_running", False)
        if is_alive and verify_alive and hasattr(self._active_adapter, "check_liveness"):
            if not self._active_adapter.check_liveness():
                self.stop_tunnel()
                is_alive = False
        uptime = int(time.time() - self._start_time) if is_alive else 0
        prov = status.get("provider") if is_alive else None
        prov_name = ""
        if prov:
            cls = TunnelRegistry.get(prov)
            prov_name = getattr(cls, "DISPLAY_NAME", prov.upper()) if cls else prov.upper()
        return {
            "is_running": is_alive,
            "public_url": status.get("public_url") if is_alive else None,
            "provider": prov,
            "provider_name": prov_name,
            "uptime_seconds": uptime,
        }

    @staticmethod
    def _get_tunnel_config() -> dict:
        """安全读取当前系统配置中的 tunnel 段落"""
        try:
            from core.config.config import load_config
            sys_cfg = load_config()
            raw_t = getattr(sys_cfg, "tunnel", {})
            if isinstance(raw_t, dict):
                return raw_t
            if hasattr(raw_t, "model_dump"):
                return raw_t.model_dump()
        except Exception:
            pass
        return {}

    def list_available_drivers(self, only_enabled: bool = False) -> list:
        """获取当前系统中所有已注册且已启用的穿透驱动 (支持按当前品牌启用状态过滤)"""
        tunnel_cfg = self._get_tunnel_config()
        active_driver = tunnel_cfg.get("active_driver", "")
        default_driver = TunnelRegistry.get_default_driver_id()

        drivers = []
        for p_id, cls in TunnelRegistry.list_all().items():
            cfg = tunnel_cfg.get(p_id, {}) if isinstance(tunnel_cfg, dict) else {}
            # 🛡️ 凭据就绪校验：若缺少核心参数（如 ngrok token、frp 域名），强制视为未启用
            is_ready = True
            if p_id == "ngrok":
                is_ready = bool((cfg.get("authtoken") or "").strip())
            elif p_id == "frp":
                is_ready = bool((cfg.get("server_addr") or "").strip())

            if not is_ready:
                is_enabled = False
            elif "enabled" in cfg:
                is_enabled = bool(cfg.get("enabled"))
            else:
                is_enabled = (p_id in ["localhost_run", "serveo", "pinggy"])

            if only_enabled and not is_enabled:
                continue

            name = getattr(cls, "DISPLAY_NAME", p_id.upper())
            desc = getattr(cls, "SHORT_DESC", "") or getattr(cls, "DESCRIPTION", "网络穿透通道")
            icon = getattr(cls, "ICON", "⚡")
            pref_driver = active_driver if (active_driver and (active_driver not in ["ngrok", "frp"] or bool(tunnel_cfg.get(active_driver, {}).get("authtoken" if active_driver == "ngrok" else "server_addr")))) else default_driver
            is_pref = (p_id == pref_driver)
            drivers.append({
                "id": p_id,
                "name": name,
                "desc": desc,
                "icon": icon,
                "is_enabled": is_enabled,
                "is_preferred": is_pref,
            })
        order_priority = {
            "localhost_run": 0,
            "serveo": 1,
            "cloudflare": 2,
            "pinggy": 3,
            "cpolar": 4,
            "ngrok": 5,
            "frp": 6,
            "tailscale": 7,
        }
        drivers.sort(key=lambda d: order_priority.get(d["id"], 99))
        if only_enabled and not drivers:
            # 兜底：若所有驱动被停用，至少保留首选驱动
            return self.list_available_drivers(only_enabled=False)[:1]
        return drivers

    def start_tunnel(self, port: int = 43212, timeout_seconds: int = 15, driver: Optional[str] = None) -> Dict[str, Any]:
        """唤醒临时公网隧道 (支持指定驱动或按配置优先级自动调度)"""
        cur = self.get_status(verify_alive=True)
        if cur.get("is_running") and cur.get("public_url"):
            if driver and cur.get("provider") != driver:
                self.stop_tunnel()
            else:
                return cur

        self.stop_tunnel()
        last_error = ""

        tunnel_cfg = self._get_tunnel_config()

        order_priority = {
            "localhost_run": 0,
            "serveo": 1,
            "cloudflare": 2,
            "pinggy": 3,
            "cpolar": 4,
            "ngrok": 5,
            "frp": 6,
            "tailscale": 7,
        }

        candidates = []
        if driver:
            if driver in TunnelRegistry.list_all():
                candidates = [driver]
            else:
                return {"is_running": False, "error": f"未知的网络穿透驱动: {driver}"}
        else:
            active_driver = tunnel_cfg.get("active_driver", "")
            if active_driver and active_driver in TunnelRegistry.list_all():
                candidates.append(active_driver)
            all_drivers = sorted(TunnelRegistry.list_all().keys(), key=lambda x: order_priority.get(x, 99))
            for d in all_drivers:
                if d not in candidates:
                    candidates.append(d)

        for d_id in candidates:
            cls = TunnelRegistry.get(d_id)
            if not cls:
                continue
            d_cfg = tunnel_cfg.get(d_id, {}) if isinstance(tunnel_cfg, dict) else {}
            if not driver:
                d_enabled = d_cfg.get("enabled", True if d_id in ["localhost_run", "serveo", "pinggy"] else False)
                if not d_enabled:
                    continue

            adapter = cls(config=d_cfg)
            if not driver and d_id in ["cloudflare", "cpolar", "frp", "ngrok", "tailscale"]:
                probe_res = adapter.probe()
                if not probe_res.get("healthy"):
                    last_error = probe_res.get("message", f"驱动 [{d_id}] 环境未就绪")
                    continue

            res = adapter.start_tunnel(local_port=port, timeout_seconds=timeout_seconds)
            if res.get("is_running"):
                self._active_adapter = adapter
                self._start_time = time.time()
                return self.get_status()
            last_error = res.get("error", "") or last_error

        err_msg = last_error or "未能在本机成功建立公网穿透通道"
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
