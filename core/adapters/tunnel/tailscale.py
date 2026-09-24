# -*- coding: utf-8 -*-
"""
🛰️ [V126.0] Illacme Plenipes - Tailscale Funnel Adapter
模块职责：基于 Tailscale Funnel / Serve 的安全虚拟私网与公网安全发布驱动。
🛡️ [SOP-01 规范]：单文件代码行数严格 ≤ 300 行。
"""

import os
import time
import json
import shutil
import subprocess
from typing import Dict, Any, Optional

from .base import BaseTunnelAdapter
from core.utils.tracing import tlog


class TailscaleTunnelAdapter(BaseTunnelAdapter):
    """⚡ Tailscale Funnel / Serve 网格穿透驱动"""

    PLUGIN_ID = "tailscale"
    DISPLAY_NAME = "Tailscale Funnel"
    DESCRIPTION = "依托 Tailscale 安全虚拟私网与官方 Funnel 功能，将本地端口发布为带有 Let's Encrypt 证书的安全公网或网格端点。"
    VERSION = "V1.0"
    ICON = "🔒"
    SHORT_DESC = "Tailscale 网格 · 官方 Funnel 安全端点"
    HAS_CONFIG = True

    def _locate_bin(self) -> Optional[str]:
        """定位 tailscale 可执行文件路径"""
        custom_bin = self.config.get("bin_path", "").strip()
        if custom_bin and os.path.exists(custom_bin) and os.access(custom_bin, os.X_OK):
            return custom_bin
        for candidate in [
            shutil.which("tailscale"),
            "/Applications/Tailscale.app/Contents/MacOS/Tailscale",
            "/usr/local/bin/tailscale",
            "/usr/bin/tailscale"
        ]:
            if candidate and os.path.exists(candidate) and os.access(candidate, os.X_OK):
                return candidate
        return None

    def _get_node_domain(self, ts_bin: str) -> Optional[str]:
        """通过 tailscale status --json 提取当前节点的 FQDN 域名"""
        try:
            res = subprocess.run([ts_bin, "status", "--json"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0 and res.stdout:
                data = json.loads(res.stdout)
                dns_name = (data.get("Self", {}).get("DNSName") or "").strip().rstrip(".")
                if dns_name:
                    return dns_name
        except Exception:
            pass
        return None

    def start_tunnel(self, local_port: int, timeout_seconds: int = 15) -> Dict[str, Any]:
        """唤醒 Tailscale Funnel / Serve 端点"""
        ts_bin = self._locate_bin()
        if not ts_bin:
            return {"is_running": False, "error": "未在操作系统环境中发现 Tailscale 客户端组件"}

        domain = self._get_node_domain(ts_bin)
        if not domain:
            return {"is_running": False, "error": "Tailscale 未连接或未完成登录 (请确认 Tailscale 已启动并加入网络)"}

        self.stop_tunnel()
        funnel_mode = self.config.get("funnel_mode", "funnel").strip()

        # 根据配置决定开启公网 Funnel 还是 Tailnet 内网 Serve
        if funnel_mode == "serve":
            cmd = [ts_bin, "serve", f"http://127.0.0.1:{local_port}"]
        else:
            cmd = [ts_bin, "funnel", str(local_port)]

        try:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid
            )
            self._process = p
            deadline = time.time() + timeout_seconds

            while time.time() < deadline:
                # 检查进程存活且 domain 就绪
                if p.poll() is None:
                    self._public_url = f"https://{domain}"
                    self._start_time = time.time()
                    tlog.info(f"🌐 [公网隧道] Tailscale Funnel 通道已建立: {self._public_url}")
                    return self.get_status()
                else:
                    _, err = p.communicate(timeout=1)
                    return {"is_running": False, "error": f"Tailscale 启动异常: {err.strip()}"}
                time.sleep(0.3)
        except Exception as e:
            tlog.warning(f"⚠️ [公网隧道] 调起 Tailscale 失败: {e}")
            self.stop_tunnel()
            return {"is_running": False, "error": f"调起 Tailscale 异常: {e}"}

        self.stop_tunnel()
        return {"is_running": False, "error": "Tailscale Funnel 握手超时"}

    def stop_tunnel(self) -> Dict[str, Any]:
        """关闭并注销当前 Tailscale 隧道"""
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

        # 重置 funnel / serve 状态
        ts_bin = self._locate_bin()
        if ts_bin:
            try:
                subprocess.run([ts_bin, "funnel", "reset"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            except Exception:
                pass

        self._public_url = None
        self._start_time = 0
        return {"is_running": False, "success": True}

    def probe(self) -> Dict[str, Any]:
        """探测本地 Tailscale 客户端状态与网格连接性"""
        ts_bin = self._locate_bin()
        if not ts_bin:
            return {
                "success": False,
                "healthy": False,
                "message": "未在操作系统环境中发现 Tailscale 客户端组件。",
                "details": {}
            }

        domain = self._get_node_domain(ts_bin)
        if domain:
            return {
                "success": True,
                "healthy": True,
                "message": f"Tailscale 节点已就绪 (网格域名: {domain})，Funnel 端点就绪。",
                "details": {"bin_path": ts_bin, "domain": domain}
            }
        else:
            return {
                "success": True,
                "healthy": False,
                "message": "Tailscale 客户端已安装，但当前未连接或未登录至 Tailnet 私网。",
                "details": {"bin_path": ts_bin}
            }
