#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Lightweight Dev Server
模块职责：提供零依赖的静态资源预览容器。
🚀 [V11.7] 主权预览版本：支持物理目录映射与自动端口占用处理。
"""

import os
import sys
import http.server
import socketserver
import threading
import logging
from typing import Optional

from core.utils.tracing import tlog

class SovereignHandler(http.server.SimpleHTTPRequestHandler):
    """
    🚀 [V15.9] 主权增强型处理器：支持 SSE 热加载脚本注入
    """
    def __init__(self, *args, **kwargs):
        self.target_dir = kwargs.pop('directory', os.getcwd())
        self.reload_event = kwargs.pop('reload_event', None)
        super().__init__(*args, directory=self.target_dir, **kwargs)

    def do_GET(self):
        # 🟢 处理热加载长连接请求
        if self.path == '/live-reload':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()

            # 等待重新加载信号
            if self.reload_event:
                self.reload_event.wait()
                self.wfile.write(b"data: reload\n\n")
                self.wfile.flush()
            return

        return super().do_GET()

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()

        # 💉 针对 HTML 文件进行主权脚本注入
        if path.endswith(".html"):
            try:
                with open(path, 'rb') as f:
                    content = f.read().decode('utf-8')

                # 注入热加载监听脚本
                reload_script = """
                <script id="sovereign-reload-script">
                    const evtSource = new EventSource("/live-reload");
                    evtSource.onmessage = function(event) {
                        if (event.data === "reload") {
                            console.log("🚀 [Sovereign] 检测到物理主权更新，正在重载...");
                            window.location.reload();
                        }
                    };
                </script>
                """
                if "</body>" in content:
                    content = content.replace("</body>", f"{reload_script}</body>")
                else:
                    content += reload_script

                encoded = content.encode('utf-8')
                import io
                f_mem = io.BytesIO(encoded)

                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                return f_mem
            except Exception as e:
                tlog.error(f"🛑 脚本注入失败: {e}")

        return super().send_head()

    def log_message(self, format, *args):
        pass

class DevServer:
    def __init__(self, directory: str, host: str = "127.0.0.1", port: int = 43212):
        self.directory = os.path.abspath(directory)
        self.host = host
        self.port = port
        self.server: Optional[socketserver.TCPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.reload_event = threading.Event()

    def notify_reload(self):
        """发送重载信号"""
        tlog.info("📡 [热加载] 正在向预览页面同步主权变更...")
        self.reload_event.set()
        # 短暂延迟后重置，为下次变更做准备
        threading.Timer(0.5, self.reload_event.clear).start()

    def start(self, blocking: bool = False):
        """
        启动预览服务器。
        blocking: 是否阻塞主线程（通常在命令行模式下设为 True）
        """
        if not os.path.exists(self.directory):
            tlog.error(f"🛑 [DevServer] 预览目录不存在: {self.directory}")
            return False

        try:
            # 🚀 [V15.9] 注入热加载事件句柄
            handler = lambda *args, **kwargs: SovereignHandler(
                *args,
                directory=self.directory,
                reload_event=self.reload_event,
                **kwargs
            )

            # 🚀 [V48.3] 工业级并发加固：使用 ThreadingTCPServer 以支持并发请求
            class ThreadingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
                daemon_threads = True
                allow_reuse_address = True

            self.server = ThreadingServer((self.host, self.port), handler)

            tlog.info("🚀 [预览就绪] 主权网页已在本地托管:")
            tlog.info(f"   🔗 预览地址: http://localhost:{self.port}")
            tlog.info(f"   📂 物理目录: {self.directory}")
            tlog.info("   按 Ctrl+C 可停止预览。")

            if blocking:
                self.server.serve_forever()
            else:
                self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
                self.thread.start()
            return True
        except Exception as e:
            tlog.error(f"🛑 [DevServer] 启动失败: {e}")
            if "Address already in use" in str(e):
                tlog.warning(f"⚠️ 提示: 端口 {self.port} 已被占用，请检查是否已有预览实例在运行。")
            return False

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            tlog.info("🛑 [DevServer] 预览服务器已安全下线。")
