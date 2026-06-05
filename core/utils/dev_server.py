#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Lightweight Dev Server
模块职责：提供零依赖的静态资源预览容器与端口冲突自愈探测。
🚀 [V11.7] 主权预览版本：支持物理目录映射与自动端口占用处理。
"""

import os
import sys
import http.server
import socketserver
import threading
import socket
from typing import Optional

from core.utils.tracing import tlog
from core.utils.framework_dev_server import FrameworkDevServer

class SovereignHandler(http.server.SimpleHTTPRequestHandler):
    """
    🚀 [V11.7] 主权处理器：支持 CORS 与跨域预览。
    """
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

class DevServer:
    """
    🚀 [V11.7] 静态资源预览服务器。
    """
    def __init__(self, directory: str, port: int):
        self.directory = directory
        self.port = port
        self.httpd = None
        self.thread = None
        self._lock = threading.Lock()

    def start(self, blocking: bool = False) -> bool:
        """启动服务器"""
        with self._lock:
            if self.httpd:
                return True

        if not os.path.exists(self.directory):
            try:
                os.makedirs(self.directory, exist_ok=True)
            except:
                return False

        # 🚀 [V80.0] 静态预览服务器端口自愈探测
        original_port = self.port
        max_attempts = 50
        current_port = original_port
        port_healed = False
        
        while max_attempts > 0:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(("", current_port))
                self.port = current_port
                port_healed = True
                break
            except OSError:
                tlog.warning(f"⚠️ [DevServer] 探测到端口 {current_port} 已被占用，正在尝试顺延自愈避让...")
                current_port += 1
                max_attempts -= 1
                
        if not port_healed:
            tlog.error("🚨 [DevServer] 连续尝试了 50 个端口均被占用，启动失败。")
            return False
            
        if self.port != original_port:
            tlog.success(f"✅ [DevServer] 端口自愈避让成功：{original_port} -> {self.port}")

        try:
            # 🛡️ [V76.5] 闭包锁定：动态注入目标物理目录以对抗 SimpleHTTPRequestHandler 初始化回退
            target_dir = self.directory
            class BoundHandler(SovereignHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=target_dir, **kwargs)
            
            class SovereignTCPServer(socketserver.TCPServer):
                def handle_error(self, request, client_address):
                    # 🛡️ [V80.0] 物理级良性异常静默：过滤 ConnectionResetError 和 BrokenPipeError
                    import sys
                    exc_type, exc_value, _ = sys.exc_info()
                    if exc_type in (ConnectionResetError, BrokenPipeError):
                        tlog.debug(f"ℹ️ [DevServer] 客户端已重置连接: {exc_value}")
                    else:
                        super().handle_error(request, client_address)

            self.httpd = SovereignTCPServer(("", self.port), BoundHandler, bind_and_activate=False)
            self.httpd.allow_reuse_address = True
            self.httpd.server_bind()
            self.httpd.server_activate()
            
            if blocking:
                self.thread = threading.current_thread()
                self.httpd.serve_forever()
            else:
                self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
                self.thread.start()
            return True
        except Exception as e:
            try:
                tlog.error(f"🚨 [DevServer] 启动失败: {e}")
            except:
                pass
            self.httpd = None
            self.thread = None
            return False

    def stop(self):
        """停止服务器"""
        with self._lock:
            if self.httpd:
                try:
                    if self.thread and self.thread.is_alive() and self.thread != threading.current_thread():
                        self.httpd.shutdown()
                except Exception as e:
                    tlog.debug(f"ℹ️ [DevServer] 尝试 shutdown 发生异常: {e}")
                try:
                    self.httpd.server_close()
                except Exception as e:
                    tlog.debug(f"ℹ️ [DevServer] 尝试 server_close 发生异常: {e}")
                self.httpd = None
                self.thread = None
