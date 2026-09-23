# -*- coding: utf-8 -*-
"""
🛰️ [V126.0] Illacme Plenipes - Cloudflare Tunnel Adapter
模块职责：基于 Cloudflare (Argo) Quick Tunnel 或自建 Token 的高质量 Anycast 穿透驱动。
🛡️ [SOP-01 规范]：单文件代码行数严格 ≤ 300 行。
"""

import os
import re
import time
import shutil
import socket
import subprocess
import threading
from typing import Dict, Any, Optional

from .base import BaseTunnelAdapter
from core.utils.tracing import tlog


class CloudflareTunnelAdapter(BaseTunnelAdapter):
    """⚡ Cloudflare Tunnel 穿透驱动 (支持 Quick 免配置或专属 Tunnel Token)"""

    PLUGIN_ID = "cloudflare"
    DISPLAY_NAME = "Cloudflare Tunnel"
    DESCRIPTION = "基于 Cloudflare 全球 Anycast 网络的工业级穿透驱动。支持免密临时通道，或配置自建 Tunnel Token 享受专属域名加速。"
    VERSION = "V1.0"
    HAS_CONFIG = True

    def _locate_bin(self) -> Optional[str]:
        """定位 cloudflared 可执行二进制文件"""
        cf_bin = shutil.which("cloudflared")
        if not cf_bin:
            local_bin = os.path.expanduser("~/.plenipes/bin/cloudflared")
            if os.path.exists(local_bin) and os.access(local_bin, os.X_OK):
                cf_bin = local_bin
        return cf_bin

    def start_tunnel(self, local_port: int, timeout_seconds: int = 15) -> Dict[str, Any]:
        """建立 Cloudflare 公网通道"""
        cf_bin = self._locate_bin()
        if not cf_bin:
            return {"is_running": False, "error": "未能在本机找到可用的 cloudflared 组件 (请安装 cloudflared 获取企业级加速)"}

        self.stop_tunnel()
        token = self.config.get("tunnel_token", "").strip()

        if token:
            # 专属自建 Tunnel Token 模式
            cmd = [cf_bin, "tunnel", "run", "--token", token]
        else:
            # 零配置 Quick Tunnel 模式
            cmd = [cf_bin, "tunnel", "--url", f"http://127.0.0.1:{local_port}", "--no-autoupdate"]

        try:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid
            )
            self._process = p
            found_url = []
            deadline = time.time() + timeout_seconds

            def _read_err():
                nonlocal found_url
                for line in iter(p.stderr.readline, ''):
                    m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                    if m and not found_url:
                        found_url.append(m.group(0))
                        break

            t = threading.Thread(target=_read_err, daemon=True)
            t.start()

            # 自定义 Token 模式若预置了 hostname，直接采用配置的域名
            custom_hostname = self.config.get("hostname", "").strip()
            if token and custom_hostname:
                self._public_url = f"https://{custom_hostname}" if not custom_hostname.startswith("http") else custom_hostname
                self._start_time = time.time()
                tlog.info(f"🌐 [公网隧道] Cloudflare 专属通道已拉起: {self._public_url}")
                return self.get_status()

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

    def stop_tunnel(self) -> Dict[str, Any]:
        """关闭并注销当前 Cloudflare 隧道"""
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
        self._public_url = None
        self._start_time = 0
        return {"is_running": False, "success": True}

    def probe(self) -> Dict[str, Any]:
        """探测 cloudflared 状态与 Cloudflare Anycast 边缘网络握手"""
        cf_bin = self._locate_bin()
        token = self.config.get("tunnel_token", "").strip()

        # 探测 trycloudflare.com:443 连通性
        t0 = time.time()
        try:
            with socket.create_connection(("trycloudflare.com", 443), timeout=3.0):
                latency = int((time.time() - t0) * 1000)
                msg = f"Cloudflare Anycast 边缘网关连接正常 (时延: {latency}ms)"
                if not cf_bin:
                    msg += "，但尚未安装本地 cloudflared 二进制组件。"
                    if token:
                        msg += " (已预先配置专属 Tunnel Token)"
                elif token:
                    custom_host = self.config.get("hostname", "").strip()
                    host_info = f" -> {custom_host}" if custom_host else ""
                    msg += f"，已配置专属 Tunnel Token{host_info}，企业级 Anycast 节点就绪。"
                else:
                    msg += "，且本地 cloudflared 已就绪 (未配置 Token，将使用 Quick 临时通道)。"
                return {
                    "success": True,
                    "healthy": bool(cf_bin),
                    "message": msg,
                    "details": {
                        "bin_path": cf_bin,
                        "has_token": bool(token),
                        "hostname": self.config.get("hostname", "").strip(),
                        "latency_ms": latency
                    }
                }
        except Exception as e:
            return {
                "success": False,
                "healthy": False,
                "message": f"连接 Cloudflare 边缘网关异常或超时: {e}",
                "details": {"bin_path": cf_bin}
            }
