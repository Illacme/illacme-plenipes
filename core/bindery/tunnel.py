# -*- coding: utf-8 -*-
"""
⚡ [V125.4] Bindery Public Tunnel Manager
职责：实现零配置免注册的临时公网穿透（Cloudflare Quick Tunnel / Native SSH 反代），
以及面向移动设备的单点出版物 30 分钟限时防越权安全令牌管理。
规范：遵循工业主权架构，单文件行数严格 ≤ 300 行。
"""

import os
import re
import time
import secrets
import shutil
import subprocess
import threading
from typing import Dict, Any, Optional

from core.utils.tracing import tlog


class TunnelHub:
    """⚡ 零配置临时公网隧道与临时安全凭证单例中枢"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TunnelHub, cls).__new__(cls)
                cls._instance._init_hub()
            return cls._instance

    def _init_hub(self):
        self._process: Optional[subprocess.Popen] = None
        self._public_url: Optional[str] = None
        self._provider: Optional[str] = None
        self._start_time: float = 0
        self._tokens: Dict[str, Dict[str, Any]] = {}  # {token: {filename, expires_at}}
        self._monitor_thread: Optional[threading.Thread] = None

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
        is_alive = bool(self._process and self._process.poll() is None and self._public_url)
        uptime = int(time.time() - self._start_time) if is_alive else 0
        return {
            "is_running": is_alive,
            "public_url": self._public_url if is_alive else None,
            "provider": self._provider if is_alive else None,
            "uptime_seconds": uptime,
        }

    def start_tunnel(self, port: int = 43212, timeout_seconds: int = 15) -> Dict[str, Any]:
        """唤醒临时公网隧道 (优先 Cloudflare Quick Tunnel，备选 Native SSH)"""
        if self._process and self._process.poll() is None and self._public_url:
            return self.get_status()

        self.stop_tunnel()
        last_error = ""

        # 1. 尝试 Cloudflare Quick Tunnel
        cf_bin = shutil.which("cloudflared")
        if not cf_bin:
            local_bin = os.path.expanduser("~/.plenipes/bin/cloudflared")
            if os.path.exists(local_bin) and os.access(local_bin, os.X_OK):
                cf_bin = local_bin

        if cf_bin:
            res = self._spawn_cloudflare(cf_bin, port, timeout_seconds)
            if res.get("is_running"):
                return res
            last_error = res.get("error", "")

        # 2. 备选方案：尝试原生系统 OpenSSH 反向代理 (Pinggy / Localhost.run)
        ssh_bin = shutil.which("ssh")
        if ssh_bin:
            res = self._spawn_ssh_tunnel(ssh_bin, port, timeout_seconds)
            if res.get("is_running"):
                return res
            last_error = res.get("error", "") or last_error

        err_msg = last_error or "未能在本机找到可用的公网穿透组件 (可安装 cloudflared 获取最佳体验)"
        return {
            "is_running": False,
            "error": err_msg,
        }

    def _spawn_cloudflare(self, bin_path: str, port: int, timeout: int) -> Dict[str, Any]:
        """拉起 Cloudflare Quick Tunnel 临时通道"""
        cmd = [bin_path, "tunnel", "--url", f"http://127.0.0.1:{port}", "--no-autoupdate"]
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            self._process = p
            self._provider = "cloudflare"

            found_url = []
            err_lines = []
            deadline = time.time() + timeout

            def _read_err():
                nonlocal found_url, err_lines
                for line in iter(p.stderr.readline, ''):
                    if len(err_lines) < 5 and line.strip():
                        err_lines.append(line.strip())
                    m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                    if m:
                        found_url.append(m.group(0))
                        break

            t = threading.Thread(target=_read_err, daemon=True)
            t.start()
            while time.time() < deadline:
                if found_url:
                    self._public_url = found_url[0]
                    self._start_time = time.time()
                    tlog.info(f"🌐 [公网隧道] Cloudflare 临时通道已建立: {self._public_url}")
                    return self.get_status()
                if p.poll() is not None:
                    break
                time.sleep(0.2)
        except Exception as e:
            tlog.warning(f"⚠️ [公网隧道] 调起 Cloudflare 失败: {e}")
            self.stop_tunnel()
            return {"is_running": False, "error": f"调起 Cloudflare 异常: {e}"}
        self.stop_tunnel()
        return {"is_running": False, "error": "Cloudflare 隧道启动超时或网络未连通"}

    def _spawn_ssh_tunnel(self, bin_path: str, port: int, timeout: int) -> Dict[str, Any]:
        """利用原生 OpenSSH 拉起零安装快速穿透"""
        cmd = [
            bin_path, "-p", "443",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-o", "ServerAliveInterval=30",
            "-R", f"0:localhost:{port}",
            "qr@a.pinggy.io"
        ]
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            self._process = p
            self._provider = "pinggy_ssh"

            found_url = []
            out_lines = []
            deadline = time.time() + timeout

            def _read_out():
                nonlocal found_url, out_lines
                for line in iter(p.stdout.readline, ''):
                    if len(out_lines) < 5 and line.strip():
                        out_lines.append(line.strip())
                    m = re.search(r"https://[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]*(?:pinggy\.net|pinggy-free\.link|pinggy\.link|localhost\.run)", line)
                    if m and not found_url:
                        found_url.append(m.group(0))
                        break

            t = threading.Thread(target=_read_out, daemon=True)
            t.start()
            while time.time() < deadline:
                if found_url:
                    self._public_url = found_url[0]
                    self._start_time = time.time()
                    tlog.info(f"🌐 [公网隧道] 原生 SSH 临时通道已建立: {self._public_url}")
                    return self.get_status()
                if p.poll() is not None:
                    break
                time.sleep(0.2)
        except Exception as e:
            tlog.warning(f"⚠️ [公网隧道] 调起 SSH 隧道失败: {e}")
            self.stop_tunnel()
            return {"is_running": False, "error": f"调起 SSH 隧道异常: {e}"}
        self.stop_tunnel()
        return {"is_running": False, "error": "SSH 穿透建立超时 (请检查 Pinggy 443 端口网络访问)"}

    def stop_tunnel(self) -> Dict[str, Any]:
        """关闭并注销当前公网隧道，收缩回局域网隔离状态"""
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
            self._process = None
        self._public_url = None
        self._provider = None
        self._start_time = 0
        tlog.info("🔒 [公网隧道] 已安全关闭临时公网通道，收缩至局域网保护模式。")
        return {"is_running": False, "success": True}


def get_tunnel_hub() -> TunnelHub:
    """获取隧道管理器单例"""
    return TunnelHub()
