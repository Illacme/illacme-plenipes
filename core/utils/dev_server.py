#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Lightweight Dev Server
模块职责：提供零依赖的静态资源预览容器。
🚀 [V11.7] 主权预览版本：支持物理目录映射与自动端口占用处理。
"""

import os
import sys
import pty
import io
import http.server
import socketserver
import threading
import logging
import subprocess
import time
from typing import Optional, Callable, Any

from core.utils.tracing import tlog

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

class FrameworkDevServer:
    """
    🚀 [V45.2] 框架预览引擎：支持 Astro, Vite, Docusaurus 等主流前端框架的异步预览。
    """
    def __init__(self, directory: str, port: int, command: str = "npm run dev"):
        self.directory = directory
        self.port = port
        self.command = command
        self.process = None
        self._lock = threading.Lock()
        self._is_starting = False

    def stop(self):
        """强制终止预览进程"""
        with self._lock:
            if self.process:
                try:
                    import signal
                    # 🚀 [V55.9] 物理级强杀：确保清理所有 PTY 子进程
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                    time.sleep(0.5)
                    if self.process.poll() is None:
                        os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                except:
                    try: self.process.terminate()
                    except: pass
                self.process = None

    def start_with_callback(self, callback: Optional[Callable] = None):
        """
        🚀 [V55.8] 回调点火：支持将日志实时透传至 UI 终端。
        """
        return self.start(blocking=False, callback=callback)

    def start(self, blocking: bool = True, callback: Optional[Callable] = None) -> bool:
        """
        启动预览服务。
        :param blocking: 是否阻塞当前线程
        :param callback: 日志回调函数
        """
        with self._lock:
            if self._is_starting:
                return True
            self._is_starting = True

        if not os.path.exists(self.directory):
            with self._lock: self._is_starting = False
            try: tlog.error(f"🛑 [FrameworkDev] 目录不存在: {self.directory}")
            except: pass
            return False

        if blocking:
            return self._async_start(callback)
        else:
            threading.Thread(target=self._async_start, args=(callback,), daemon=True).start()
            return True

    def _async_start(self, callback: Optional[Callable] = None):
        try:
            # 1. 终止旧进程
            self.stop()
            
            # 2. 依赖自愈阶段
            node_modules = os.path.join(self.directory, "node_modules")
            if not os.path.exists(node_modules):
                try: tlog.warning("⚠️ [依赖缺失] 正在启动自动补全...")
                except: pass
                if callback: callback("⚠️ [系统感知] 检测到主题依赖缺失，正在启动物理补全 (npm install)...")
                
                install_cmd = "npm install"
                if os.path.exists(os.path.join(self.directory, "pnpm-lock.yaml")): install_cmd = "pnpm install"
                elif os.path.exists(os.path.join(self.directory, "yarn.lock")): install_cmd = "yarn install"

                # 🚀 [V55.9] 物理劫持：安装阶段也必须使用 PTY，防止日志闷死在缓冲区
                master_fd, slave_fd = pty.openpty()
                try:
                    install_proc = subprocess.Popen(
                        install_cmd, shell=True, cwd=self.directory,
                        stdout=slave_fd, stderr=slave_fd,
                        text=True, bufsize=1,
                        start_new_session=True,
                        close_fds=True
                    )
                    os.close(slave_fd)
                except Exception as e:
                    os.close(master_fd)
                    try: os.close(slave_fd)
                    except: pass
                    if callback: callback(f"❌ [依赖补全异常] 无法启动安装进程: {str(e)}")
                    with self._lock: self._is_starting = False
                    return False

                try:
                    master_reader = io.open(master_fd, 'r', encoding='utf-8', errors='replace')
                    while True:
                        if install_proc.poll() is not None: break
                        line = master_reader.readline()
                        if not line: break
                        line_str = line.strip()
                        if callback: callback(f"[Install] {line_str}")
                except Exception as e:
                    tlog.debug(f"ℹ️ [Install] PTY 流已中断: {e}")
                finally:
                    try: master_reader.close()
                    except:
                        try: os.close(master_fd)
                        except: pass
                
                install_proc.wait()
                
                if install_proc.returncode == 0:
                    if callback: callback("✅ [系统感知] 依赖补全成功，正在准备正式点火...")
                else:
                    if callback: callback(f"❌ [系统感知] 依赖补全失败 (Exit: {install_proc.returncode})，请手动检查网络。")
                    with self._lock: self._is_starting = False
                    return False

            # 3. 正式点火阶段
            cmd = self.command.replace("{port}", str(self.port))
            try: tlog.info(f"🚀 [框架预览] 正在执行异步点火: {cmd}")
            except: pass
            
            # 🚀 [V55.9] 终端镜像：使用 PTY 伪终端欺骗子进程，强制开启行缓冲
            master_fd, slave_fd = pty.openpty()
            
            popen_kwargs = {
                "shell": True, "cwd": self.directory,
                "stdout": slave_fd, "stderr": slave_fd,
                "text": True, "bufsize": 1,
                "env": {**os.environ, "PORT": str(self.port)},
                "start_new_session": True,
                "close_fds": True
            }

            try:
                proc = subprocess.Popen(cmd, **popen_kwargs)
                self.process = proc
                os.close(slave_fd)
            except Exception as e:
                os.close(master_fd)
                try: os.close(slave_fd)
                except: pass
                if callback: callback(f"❌ [系统异常] 启动失败: {str(e)}")
                with self._lock: self._is_starting = False
                return False
            
            with self._lock: self._is_starting = False

            try:
                master_reader = io.open(master_fd, 'r', encoding='utf-8', errors='replace')
                while True:
                    if proc.poll() is not None: break
                    line = master_reader.readline()
                    if not line: break
                    line_str = line.strip()
                    if callback: callback(line_str)
            except Exception as e:
                tlog.debug(f"ℹ️ [FrameworkDev] PTY 流已中断: {e}")
            finally:
                try: master_reader.close()
                except:
                    try: os.close(master_fd)
                    except: pass
            
            if proc:
                proc.wait()
            return True
        except Exception as e:
            try: tlog.error(f"🚨 [FrameworkDev] 异步启动发生未预期错误: {e}")
            except: pass
            if callback: callback(f"❌ [系统异常] 异步启动失败: {str(e)}")
            with self._lock: self._is_starting = False
            return False

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
            return False

        try:
            # 🛡️ [V76.5] 闭包锁定：动态注入目标物理目录以对抗 SimpleHTTPRequestHandler 初始化回退
            target_dir = self.directory
            class BoundHandler(SovereignHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=target_dir, **kwargs)
            
            self.httpd = socketserver.TCPServer(("", self.port), BoundHandler, bind_and_activate=False)
            self.httpd.allow_reuse_address = True
            self.httpd.server_bind()
            self.httpd.server_activate()
            
            if blocking:
                self.httpd.serve_forever()
            else:
                self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
                self.thread.start()
            return True
        except Exception as e:
            try: tlog.error(f"🚨 [DevServer] 启动失败: {e}")
            except: pass
            return False

    def stop(self):
        """停止服务器"""
        with self._lock:
            if self.httpd:
                self.httpd.shutdown()
                self.httpd.server_close()
                self.httpd = None
                self.thread = None
