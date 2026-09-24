# -*- coding: utf-8 -*-
"""
🛰️ [V126.0] Illacme Plenipes - cpolar Tunnel Adapter
模块职责：基于 cpolar 客户端的国内低时延网络穿透驱动，优化移动扫码体验。
🛡️ [SOP-01 规范]：单文件代码行数严格 ≤ 300 行。
"""

import os
import re
import time
import json
import shutil
import socket
import urllib.request
import subprocess
import threading
from typing import Dict, Any, Optional

from .base import BaseTunnelAdapter
from core.utils.tracing import tlog


class CpolarTunnelAdapter(BaseTunnelAdapter):
    """⚡ cpolar 极点云国内穿透驱动 (支持临时通道与专属子域名)"""

    PLUGIN_ID = "cpolar"
    DISPLAY_NAME = "cpolar 极点云"
    DESCRIPTION = "国内专属优化的高性能穿透驱动，多线 BGP 节点直连，移动端扫码秒开。支持免密临时通道或配置 Authtoken 绑定专属子域名。"
    VERSION = "V1.0"
    ICON = "🚀"
    SHORT_DESC = "国内专属优化 · 移动扫码秒开"
    HAS_CONFIG = True

    def _locate_bin(self) -> Optional[str]:
        """定位 cpolar 二进制可执行文件"""
        custom_bin = self.config.get("bin_path", "").strip()
        if custom_bin and os.path.exists(custom_bin) and os.access(custom_bin, os.X_OK):
            return custom_bin
        cp_bin = shutil.which("cpolar")
        if not cp_bin:
            local_bin = os.path.expanduser("~/.plenipes/bin/cpolar")
            if os.path.exists(local_bin) and os.access(local_bin, os.X_OK):
                cp_bin = local_bin
        return cp_bin

    def start_tunnel(self, local_port: int, timeout_seconds: int = 15) -> Dict[str, Any]:
        """拉起 cpolar 公网通道"""
        cp_bin = self._locate_bin()
        if not cp_bin:
            return {"is_running": False, "error": "未能在本机找到可用的 cpolar 组件 (请安装 cpolar 享受国内极速加速)"}

        self.stop_tunnel()
        token = self.config.get("authtoken", "").strip()
        subdomain = self.config.get("subdomain", "").strip()
        region = self.config.get("region", "cn").strip() or "cn"

        # 若配置了 Token 则静默绑定
        if token:
            try:
                subprocess.run([cp_bin, "authtoken", token], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            except Exception:
                pass

        cmd = [cp_bin, "http", str(local_port), f"-region={region}", "-log=stdout"]
        if subdomain:
            cmd.append(f"-subdomain={subdomain}")

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

            def _read_stream(stream):
                nonlocal found_url
                for line in iter(stream.readline, ''):
                    m = re.search(r"https://[a-zA-Z0-9-]+\.(?:cpolar\.cn|cpolar\.top|cpolar\.io|cpolar\.com)", line)
                    if m and not found_url:
                        found_url.append(m.group(0))
                        break

            threading.Thread(target=_read_stream, args=(p.stdout,), daemon=True).start()
            threading.Thread(target=_read_stream, args=(p.stderr,), daemon=True).start()

            while time.time() < deadline:
                if found_url:
                    self._public_url = found_url[0]
                    self._start_time = time.time()
                    tlog.info(f"🌐 [公网隧道] cpolar 穿透通道已建立: {self._public_url}")
                    return self.get_status()

                # 备用方案：尝试从本地 4040/api/tunnels 提取
                try:
                    req = urllib.request.Request("http://127.0.0.1:4040/api/tunnels", headers={"User-Agent": "IllacmeTunnel/1.0"})
                    with urllib.request.urlopen(req, timeout=0.6) as resp:
                        if resp.status == 200:
                            data = json.loads(resp.read().decode("utf-8"))
                            tunnels = data.get("tunnels", [])
                            for t_item in tunnels:
                                p_url = t_item.get("public_url", "")
                                if p_url.startswith("https://"):
                                    self._public_url = p_url
                                    self._start_time = time.time()
                                    tlog.info(f"🌐 [公网隧道] cpolar Local API 提取通道成功: {self._public_url}")
                                    return self.get_status()
                except Exception:
                    pass

                if p.poll() is not None:
                    break
                time.sleep(0.3)
        except Exception as e:
            tlog.warning(f"⚠️ [公网隧道] 调起 cpolar 失败: {e}")
            self.stop_tunnel()
            return {"is_running": False, "error": f"调起 cpolar 异常: {e}"}

        self.stop_tunnel()
        return {"is_running": False, "error": "cpolar 隧道建立超时 (请检查网络或 Authtoken 配置)"}

    def stop_tunnel(self) -> Dict[str, Any]:
        """关闭并注销当前 cpolar 隧道"""
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
        """探测 cpolar 二进制客户端与国内中继网关连通性"""
        cp_bin = self._locate_bin()
        token = self.config.get("authtoken", "").strip()

        t0 = time.time()
        try:
            with socket.create_connection(("cpolar.cn", 443), timeout=3.0):
                latency = int((time.time() - t0) * 1000)
                msg = f"cpolar 国内网关链路畅通 (时延: {latency}ms)"
                if not cp_bin:
                    msg += "，但未检测到本地 cpolar 客户端组件。"
                elif token:
                    msg += "，已配置 Authtoken，专属高速通道就绪。"
                else:
                    msg += "，本地客户端已就绪 (未配置 Token，将使用免费临时通道)。"
                return {
                    "success": True,
                    "healthy": bool(cp_bin),
                    "message": msg,
                    "details": {"bin_path": cp_bin, "has_token": bool(token), "latency_ms": latency}
                }
        except Exception as e:
            return {
                "success": False,
                "healthy": False,
                "message": f"连接 cpolar 国内网关超时: {e}",
                "details": {"bin_path": cp_bin}
            }
