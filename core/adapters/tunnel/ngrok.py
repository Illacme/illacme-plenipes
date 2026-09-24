# -*- coding: utf-8 -*-
"""
🛰️ [V126.0] Illacme Plenipes - ngrok Tunnel Adapter
模块职责：基于 ngrok 客户端的全球通用开发者网络穿透驱动。
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


class NgrokTunnelAdapter(BaseTunnelAdapter):
    """⚡ ngrok 全球开发者隧道驱动"""

    PLUGIN_ID = "ngrok"
    DISPLAY_NAME = "ngrok 开发者隧道"
    DESCRIPTION = "国际标准反向代理平台，全球多边缘接入节点，支持 Webhook 调试、流量监控与静态公网域名。"
    VERSION = "V1.0"
    ICON = "🌍"
    SHORT_DESC = "国际开发者标准 · 全球边缘加速"
    HAS_CONFIG = True

    def _locate_bin(self) -> Optional[str]:
        """定位 ngrok 二进制可执行文件"""
        custom_bin = self.config.get("bin_path", "").strip()
        if custom_bin and os.path.exists(custom_bin) and os.access(custom_bin, os.X_OK):
            return custom_bin
        ng_bin = shutil.which("ngrok")
        if not ng_bin:
            local_bin = os.path.expanduser("~/.plenipes/bin/ngrok")
            if os.path.exists(local_bin) and os.access(local_bin, os.X_OK):
                ng_bin = local_bin
        return ng_bin

    def start_tunnel(self, local_port: int, timeout_seconds: int = 15) -> Dict[str, Any]:
        """拉起 ngrok 公网通道"""
        ng_bin = self._locate_bin()
        if not ng_bin:
            return {"is_running": False, "error": "未能在本机找到可用的 ngrok 客户端 (请安装 ngrok 命令行工具)"}

        self.stop_tunnel()
        token = self.config.get("authtoken", "").strip()
        domain = self.config.get("domain", "").strip()

        cmd = [ng_bin, "http", str(local_port), "--log=stdout", "--log-format=logfmt"]
        if token:
            cmd.extend(["--authtoken", token])
        if domain:
            cmd.extend(["--domain", domain])

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
                    # 匹配 url=https://...
                    m = re.search(r"url=(https://[^\s]+)", line)
                    if m and not found_url:
                        found_url.append(m.group(1))
                        break
                    # 通用 https:// 匹配
                    m2 = re.search(r"https://[a-zA-Z0-9-]+\.(?:ngrok-free\.app|ngrok\.io|ngrok\.app)", line)
                    if m2 and not found_url:
                        found_url.append(m2.group(0))
                        break

            threading.Thread(target=_read_stream, args=(p.stdout,), daemon=True).start()
            threading.Thread(target=_read_stream, args=(p.stderr,), daemon=True).start()

            while time.time() < deadline:
                if found_url:
                    self._public_url = found_url[0]
                    self._start_time = time.time()
                    tlog.info(f"🌐 [公网隧道] ngrok 通道已建立: {self._public_url}")
                    return self.get_status()

                # 备用方案：读取本地 4040 API
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
                                    tlog.info(f"🌐 [公网隧道] ngrok Local API 提取通道成功: {self._public_url}")
                                    return self.get_status()
                except Exception:
                    pass

                if p.poll() is not None:
                    break
                time.sleep(0.3)
        except Exception as e:
            tlog.warning(f"⚠️ [公网隧道] 调起 ngrok 失败: {e}")
            self.stop_tunnel()
            return {"is_running": False, "error": f"调起 ngrok 异常: {e}"}

        self.stop_tunnel()
        return {"is_running": False, "error": "ngrok 隧道建立超时 (请检查 Authtoken 是否有效或网络是否畅通)"}

    def stop_tunnel(self) -> Dict[str, Any]:
        """关闭并注销当前 ngrok 隧道"""
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
        """探测 ngrok 二进制客户端与全球 API 连通性"""
        ng_bin = self._locate_bin()
        token = self.config.get("authtoken", "").strip()

        t0 = time.time()
        try:
            with socket.create_connection(("ngrok.com", 443), timeout=3.0):
                latency = int((time.time() - t0) * 1000)
                msg = f"ngrok 边缘网关响应正常 (时延: {latency}ms)"
                if not ng_bin:
                    msg += "，但尚未安装本地 ngrok 客户端。"
                elif token:
                    msg += "，已配置 Authtoken，通道就绪。"
                else:
                    msg += "，本地客户端已就绪 (提示: ngrok 新版要求必须配置 Authtoken)。"
                return {
                    "success": True,
                    "healthy": bool(ng_bin),
                    "message": msg,
                    "details": {"bin_path": ng_bin, "has_token": bool(token), "latency_ms": latency}
                }
        except Exception as e:
            return {
                "success": False,
                "healthy": False,
                "message": f"连接 ngrok 边缘网关超时: {e}",
                "details": {"bin_path": ng_bin}
            }
