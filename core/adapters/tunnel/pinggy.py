# -*- coding: utf-8 -*-
"""
🛰️ [V126.0] Illacme Plenipes - Pinggy OpenSSH Tunnel Adapter
模块职责：基于系统原生 OpenSSH 管道的免安装零配置临时穿透驱动。
🛡️ [SOP-01 规范]：单文件代码行数严格 ≤ 300 行。
"""

import os
import re
import time
import shutil
import socket
import subprocess
import threading
from typing import Dict, Any

from .base import BaseTunnelAdapter
from core.utils.tracing import tlog


class PinggyTunnelAdapter(BaseTunnelAdapter):
    """⚡ Pinggy 原生 OpenSSH 穿透驱动 (免配置开箱即用)"""

    PLUGIN_ID = "pinggy"
    DISPLAY_NAME = "Pinggy SSH 极速穿透"
    DESCRIPTION = "基于原生 OpenSSH 反向代理的零配置临时穿透通道，开箱即用，无需安装第三方组件。"
    VERSION = "V1.0"
    HAS_CONFIG = False

    @classmethod
    def _cleanup_zombies(cls):
        """清理历史残留的孤儿 Pinggy SSH 进程，释放单连接配额"""
        try:
            subprocess.run(["pkill", "-f", "qr@a.pinggy.io"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def start_tunnel(self, local_port: int, timeout_seconds: int = 15) -> Dict[str, Any]:
        """拉起 OpenSSH 反代通道 (-T 禁用伪终端，强制纯文本流)"""
        ssh_bin = shutil.which("ssh")
        if not ssh_bin:
            return {"is_running": False, "error": "系统环境中未检测到 OpenSSH 客户端 (ssh)"}

        self.stop_tunnel()
        self._cleanup_zombies()

        cmd = [
            ssh_bin, "-p", "443",
            "-T",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-o", "ServerAliveInterval=30",
            "-R", f"0:localhost:{local_port}",
            "qr@a.pinggy.io"
        ]
        sub_env = dict(os.environ)
        sub_env["TERM"] = "dumb"

        try:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=sub_env,
                preexec_fn=os.setsid
            )
            self._process = p
            found_url = []
            deadline = time.time() + timeout_seconds

            def _read_out():
                nonlocal found_url
                for line in iter(p.stdout.readline, ''):
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
                    tlog.info(f"🌐 [公网隧道] Pinggy SSH 临时通道已建立: {self._public_url}")
                    return self.get_status()
                if p.poll() is not None:
                    break
                time.sleep(0.2)
        except Exception as e:
            tlog.warning(f"⚠️ [公网隧道] 调起 Pinggy SSH 失败: {e}")
            self.stop_tunnel()
            return {"is_running": False, "error": f"调起 SSH 异常: {e}"}

        self.stop_tunnel()
        return {"is_running": False, "error": "SSH 穿透建立超时 (请检查 Pinggy 443 端口网络访问)"}

    def stop_tunnel(self) -> Dict[str, Any]:
        """关闭并注销当前 Pinggy 隧道通道"""
        if self._process:
            try:
                os.killpg(os.getpgid(self._process.pid), 15)
                self._process.wait(timeout=2)
            except Exception:
                try:
                    os.killpg(os.getpgid(self._process.pid), 9)
                except Exception:
                    pass
            self._process = None
        self._cleanup_zombies()
        self._public_url = None
        self._start_time = 0
        return {"is_running": False, "success": True}

    def probe(self) -> Dict[str, Any]:
        """探测 OpenSSH 客户端与 Pinggy 网关端口连通性"""
        ssh_bin = shutil.which("ssh")
        if not ssh_bin:
            return {"success": False, "healthy": False, "message": "未在操作系统环境中发现 OpenSSH 客户端。"}

        # 探测 a.pinggy.io:443 端口 TCP 握手
        t0 = time.time()
        try:
            with socket.create_connection(("a.pinggy.io", 443), timeout=3.0):
                latency = int((time.time() - t0) * 1000)
                return {
                    "success": True,
                    "healthy": True,
                    "message": f"Pinggy 网关链路畅通，端口 443 响应正常 (时延: {latency}ms)",
                    "details": {"ssh_path": ssh_bin, "latency_ms": latency}
                }
        except Exception as e:
            return {
                "success": False,
                "healthy": False,
                "message": f"连接 Pinggy 443 端口受阻或超时: {e}",
                "details": {"ssh_path": ssh_bin}
            }
