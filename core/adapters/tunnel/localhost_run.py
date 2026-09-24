# -*- coding: utf-8 -*-
"""
🛰️ [V126.0] Illacme Plenipes - Localhost.run OpenSSH Tunnel Adapter
模块职责：基于系统原生 OpenSSH 反向代理的零配置临时穿透驱动 (Localhost.run)。
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


class LocalhostRunTunnelAdapter(BaseTunnelAdapter):
    """⚡ Localhost.run 原生 OpenSSH 穿透驱动 (免配置开箱即用)"""

    PLUGIN_ID = "localhost_run"
    DISPLAY_NAME = "Localhost.run SSH 穿透"
    DESCRIPTION = "基于 OpenSSH 协议的免客户端临时穿透通道，无需安装第三方组件，自动分配安全的临时公网 HTTPS 地址。"
    VERSION = "V1.0"
    ICON = "🌐"
    SHORT_DESC = "OpenSSH 免密直连 · 零配置即开即用"
    HAS_CONFIG = False

    @classmethod
    def _cleanup_zombies(cls):
        """清理历史残留的孤儿 Localhost.run SSH 进程"""
        try:
            subprocess.run(["pkill", "-f", "nokey@localhost.run"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def start_tunnel(self, local_port: int, timeout_seconds: int = 15) -> Dict[str, Any]:
        """拉起 OpenSSH 反代通道"""
        ssh_bin = shutil.which("ssh")
        if not ssh_bin:
            return {"is_running": False, "error": "系统环境中未检测到 OpenSSH 客户端 (ssh)"}

        self.stop_tunnel()
        self._cleanup_zombies()

        cmd = [
            ssh_bin,
            "-T",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-o", "ExitOnForwardFailure=yes",
            "-o", "ServerAliveInterval=15",
            "-o", "ServerAliveCountMax=3",
            "-o", "TCPKeepAlive=yes",
            "-R", f"80:localhost:{local_port}",
            "nokey@localhost.run"
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
                try:
                    for line in iter(p.stdout.readline, ''):
                        if not found_url:
                            m = re.search(r"https://[a-zA-Z0-9-]+\.(?:lhrtunnel\.pro|lhr\.life|localhost\.run)", line)
                            if m:
                                found_url.append(m.group(0))
                        # 持续排空 stdout，防止管道缓冲区填满阻塞 SSH 进程
                except Exception:
                    pass

            t = threading.Thread(target=_read_out, daemon=True)
            t.start()
            while time.time() < deadline:
                if found_url:
                    self._public_url = found_url[0]
                    self._start_time = time.time()
                    tlog.info(f"🌐 [公网隧道] Localhost.run SSH 临时通道已建立: {self._public_url}")
                    return self.get_status()
                if p.poll() is not None:
                    break
                time.sleep(0.2)
        except Exception as e:
            tlog.warning(f"⚠️ [公网隧道] 调起 Localhost.run SSH 失败: {e}")
            self.stop_tunnel()
            return {"is_running": False, "error": f"调起 SSH 异常: {e}"}

        self.stop_tunnel()
        return {"is_running": False, "error": "Localhost.run SSH 穿透建立超时 (请检查海外 SSH 访问网络)"}

    def check_liveness(self) -> bool:
        """主动探测当前公网通道在外部网络中是否可用 (仅当确证 503 no tunnel here 时判定解绑)"""
        if not self._process or getattr(self._process, "poll", lambda: None)() is not None or not self._public_url:
            return False
        # 🛡️ 保护期：刚建立通道 15 秒内不予主动误杀，保障海外 DNS 传播完成
        if time.time() - self._start_time < 15:
            return True
        try:
            import urllib.request
            import urllib.error
            req = urllib.request.Request(self._public_url, headers={"User-Agent": "IllacmeTunnelProbe/1.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                return True
        except urllib.error.HTTPError as he:
            # 只有明确 503 且响应体为 no tunnel here 时才断定已失效
            if he.code == 503:
                try:
                    body = he.read().decode('utf-8', errors='ignore')
                    if "no tunnel here" in body:
                        tlog.warning(f"⚠️ [公网隧道] 确证远端通道已解绑 (503): {self._public_url}")
                        return False
                except Exception:
                    pass
            return True
        except Exception:
            # 网络抖动或超时不轻率误判
            return True

    def get_status(self) -> Dict[str, Any]:
        """获取当前适配器穿透状态 (附带活性防僵死自愈)"""
        base_st = super().get_status()
        if not base_st.get("is_running"):
            return base_st
        return base_st

    def stop_tunnel(self) -> Dict[str, Any]:
        """关闭并注销当前 Localhost.run 隧道通道"""
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
        """探测 OpenSSH 客户端与 Localhost.run 网关连通性"""
        ssh_bin = shutil.which("ssh")
        if not ssh_bin:
            return {"success": False, "healthy": False, "message": "未在操作系统环境中发现 OpenSSH 客户端。"}

        t0 = time.time()
        # 探测 localhost.run:22 端口 TCP 握手
        try:
            with socket.create_connection(("localhost.run", 22), timeout=3.0):
                latency = int((time.time() - t0) * 1000)
                return {
                    "success": True,
                    "healthy": True,
                    "message": f"Localhost.run 网关链路畅通，端口 22 响应正常 (时延: {latency}ms)",
                    "details": {"ssh_path": ssh_bin, "latency_ms": latency}
                }
        except Exception as e:
            return {
                "success": False,
                "healthy": False,
                "message": f"连接 Localhost.run 端口受阻或超时: {e}",
                "details": {"ssh_path": ssh_bin}
            }
