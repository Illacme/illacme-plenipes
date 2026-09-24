# -*- coding: utf-8 -*-
"""
🛰️ [V126.0] Illacme Plenipes - FRP Tunnel Adapter
模块职责：基于 frpc 客户端的高性能自建反向代理驱动，支持私有云服务器与独享带宽。
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


class FrpTunnelAdapter(BaseTunnelAdapter):
    """⚡ FRP 自建反向代理驱动 (私有云独享带宽)"""

    PLUGIN_ID = "frp"
    DISPLAY_NAME = "FRP 自建内网穿透"
    DESCRIPTION = "高性能自建反向代理驱动，支持国内云服务器私有化部署、独享私有带宽与自定义域名。"
    VERSION = "V1.0"
    ICON = "🛡️"
    SHORT_DESC = "自建 VPS 私有化 · 独享带宽无限制"
    HAS_CONFIG = True

    def _locate_bin(self) -> Optional[str]:
        """定位 frpc 可执行二进制文件"""
        custom_bin = self.config.get("bin_path", "").strip()
        if custom_bin and os.path.exists(custom_bin) and os.access(custom_bin, os.X_OK):
            return custom_bin
        f_bin = shutil.which("frpc")
        if not f_bin:
            local_bin = os.path.expanduser("~/.plenipes/bin/frpc")
            if os.path.exists(local_bin) and os.access(local_bin, os.X_OK):
                f_bin = local_bin
        return f_bin

    def _get_frpc_version(self, f_bin: str) -> str:
        """获取本地 frpc 版本号"""
        try:
            res = subprocess.run([f_bin, "-v"], capture_output=True, text=True, timeout=2)
            return res.stdout.strip() or res.stderr.strip()
        except Exception:
            return ""

    def _build_config_file(self, local_port: int, f_bin: str) -> str:
        """生成运行时临时配置文件 (自动适配 TOML 或 INI 语法)"""
        run_dir = os.path.expanduser("~/.plenipes/run")
        os.makedirs(run_dir, exist_ok=True)

        server_addr = self.config.get("server_addr", "127.0.0.1").strip()
        server_port = int(self.config.get("server_port", 7000) or 7000)
        token = self.config.get("token", "").strip()
        custom_domain = self.config.get("custom_domain", "").strip()
        subdomain = self.config.get("subdomain", "").strip()
        remote_port = self.config.get("remote_port", "")

        version = self._get_frpc_version(f_bin)
        # frp 0.52+ 采用 toml 格式
        is_toml = False
        if version:
            m = re.search(r"(\d+)\.(\d+)", version)
            if m and (int(m.group(1)) > 0 or int(m.group(2)) >= 52):
                is_toml = True

        if is_toml:
            cfg_path = os.path.join(run_dir, "frpc_illacme.toml")
            lines = [
                f'serverAddr = "{server_addr}"',
                f'serverPort = {server_port}'
            ]
            if token:
                lines.append(f'auth.token = "{token}"')
            lines.extend([
                '',
                '[[proxies]]',
                'name = "illacme_press"',
                'type = "http"',
                f'localPort = {local_port}'
            ])
            if custom_domain:
                lines.append(f'customDomains = ["{custom_domain}"]')
            elif subdomain:
                lines.append(f'subdomain = "{subdomain}"')
            elif remote_port:
                lines[lines.index('type = "http"')] = 'type = "tcp"'
                lines.append(f'remotePort = {remote_port}')
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            return cfg_path
        else:
            cfg_path = os.path.join(run_dir, "frpc_illacme.ini")
            lines = [
                '[common]',
                f'server_addr = {server_addr}',
                f'server_port = {server_port}'
            ]
            if token:
                lines.append(f'token = {token}')
            lines.extend([
                '',
                '[illacme_press]',
                'type = http',
                f'local_port = {local_port}'
            ])
            if custom_domain:
                lines.append(f'custom_domains = {custom_domain}')
            elif subdomain:
                lines.append(f'subdomain = {subdomain}')
            elif remote_port:
                lines[lines.index('type = http')] = 'type = tcp'
                lines.append(f'remote_port = {remote_port}')
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            return cfg_path

    def start_tunnel(self, local_port: int, timeout_seconds: int = 15) -> Dict[str, Any]:
        """拉起 FRP 客户端进程"""
        f_bin = self._locate_bin()
        if not f_bin:
            return {"is_running": False, "error": "未能在本机找到可用的 frpc 客户端 (请安装 frpc 组件)"}

        server_addr = self.config.get("server_addr", "").strip()
        if not server_addr:
            return {"is_running": False, "error": "FRP 穿透需要配置 server_addr 服务端地址"}

        self.stop_tunnel()
        cfg_file = self._build_config_file(local_port, f_bin)

        cmd = [f_bin, "-c", cfg_file]
        try:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid
            )
            self._process = p
            deadline = time.time() + timeout_seconds
            success_logged = False
            last_lines = []

            def _read_out():
                nonlocal success_logged, last_lines
                for line in iter(p.stdout.readline, ''):
                    last_lines.append(line.strip())
                    if len(last_lines) > 10:
                        last_lines.pop(0)
                    if "start proxy success" in line.lower() or "login to server success" in line.lower():
                        success_logged = True

            threading.Thread(target=_read_out, daemon=True).start()

            custom_domain = self.config.get("custom_domain", "").strip()
            subdomain = self.config.get("subdomain", "").strip()
            remote_port = self.config.get("remote_port", "")

            while time.time() < deadline:
                if success_logged:
                    if custom_domain:
                        self._public_url = f"https://{custom_domain}" if not custom_domain.startswith("http") else custom_domain
                    elif subdomain:
                        self._public_url = f"http://{subdomain}.{server_addr}"
                    elif remote_port:
                        self._public_url = f"http://{server_addr}:{remote_port}"
                    else:
                        self._public_url = f"http://{server_addr}"
                    self._start_time = time.time()
                    tlog.info(f"🌐 [公网隧道] FRP 通道已建立: {self._public_url}")
                    return self.get_status()
                if p.poll() is not None:
                    break
                time.sleep(0.3)
        except Exception as e:
            tlog.warning(f"⚠️ [公网隧道] 调起 frpc 失败: {e}")
            self.stop_tunnel()
            return {"is_running": False, "error": f"调起 frpc 异常: {e}"}

        self.stop_tunnel()
        err_hint = ("\n".join(last_lines[-3:])) if last_lines else "FRP 隧道建立超时 (请检查 server_addr 与服务端通信)"
        return {"is_running": False, "error": f"FRP 启动失败: {err_hint}"}

    def stop_tunnel(self) -> Dict[str, Any]:
        """关闭并注销当前 FRP 隧道"""
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
        """探测 frpc 客户端与自建 FRP 服务端连通性"""
        f_bin = self._locate_bin()
        server_addr = self.config.get("server_addr", "").strip()
        server_port = int(self.config.get("server_port", 7000) or 7000)

        if not server_addr:
            return {
                "success": bool(f_bin),
                "healthy": False,
                "message": "FRP 客户端未配置 server_addr (请在设置中填入自建服务器 IP 或域名)。",
                "details": {"bin_path": f_bin}
            }

        t0 = time.time()
        try:
            with socket.create_connection((server_addr, server_port), timeout=3.0):
                latency = int((time.time() - t0) * 1000)
                msg = f"FRP 自建服务端 ({server_addr}:{server_port}) 响应正常 (时延: {latency}ms)"
                if not f_bin:
                    msg += "，但未检测到本地 frpc 客户端组件。"
                else:
                    msg += "，本地客户端与服务端均就绪。"
                return {
                    "success": True,
                    "healthy": bool(f_bin),
                    "message": msg,
                    "details": {"bin_path": f_bin, "server": f"{server_addr}:{server_port}", "latency_ms": latency}
                }
        except Exception as e:
            return {
                "success": False,
                "healthy": False,
                "message": f"连接 FRP 服务端 ({server_addr}:{server_port}) 失败: {e}",
                "details": {"bin_path": f_bin}
            }
