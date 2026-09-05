#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Framework Dev Server Shard
模块职责：负责 Astro, Vite, Docusaurus 等主流前端框架的异步预览服务。
"""

import os
import sys
import pty
import io
import threading
import subprocess
import time
import socket
from typing import Optional, Callable, Any

from core.utils.tracing import tlog

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
                except OSError:
                    try: self.process.terminate()
                    except OSError: pass
                self.process = None

    def is_alive(self) -> bool:
        """判断预览进程是否依然存活或正在拉起"""
        with self._lock:
            if self._is_starting:
                return True
        if self.process and self.process.poll() is None:
            return True
        return False

    def wait_until_ready(self, timeout: float = 6.0) -> bool:
        """🚀 [V55.9] 探活探测：等待 DevServer 成功绑定端口并响应"""
        start = time.time()
        while time.time() - start < timeout:
            if not self._is_starting and self.process and self.process.poll() is not None:
                return False
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    if s.connect_ex(("127.0.0.1", self.port)) == 0:
                        return True
            except Exception:
                pass
            time.sleep(0.3)
        return self.is_alive()

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
            except Exception: pass
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
            if os.path.exists(os.path.join(self.directory, "docusaurus.config.js")):
                for p in ["docusaurus-plugin-content-docs/current", "docusaurus-plugin-content-blog", "docusaurus-plugin-content-pages"]:
                    td = os.path.join(self.directory, "i18n/zh-Hans", p)
                    os.makedirs(td, exist_ok=True)
                    if not any(x.endswith((".md", ".mdx")) for x in os.listdir(td)):
                        with open(os.path.join(td, "placeholder.md"), "w", encoding="utf-8") as f:
                            f.write("# Placeholder\n\nThis is a temporary placeholder.")
            
            # 🚀 [V80.0] 端口物理冲突自愈探测
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
                    tlog.warning(f"⚠️ [FrameworkDev] 探测到端口 {current_port} 已被占用，正在尝试顺延自愈避让...")
                    if callback: callback(f"⚠️ [系统感知] 探测到端口 {current_port} 已被占用，正在尝试顺延自愈避让...")
                    current_port += 1
                    max_attempts -= 1
            
            if not port_healed:
                tlog.error("🚨 [FrameworkDev] 连续尝试了 50 个端口均被占用，启动失败。")
                if callback: callback("❌ [系统异常] 连续尝试 50 个端口均被占用，无法启动。")
                with self._lock: self._is_starting = False
                return False
                
            if self.port != original_port:
                tlog.success(f"✅ [FrameworkDev] 端口自愈避让成功：{original_port} -> {self.port}")
                if callback: callback(f"✅ [系统感知] 端口自愈避让成功：{original_port} -> {self.port}")
            
            # 2. 依赖自愈阶段
            node_modules = os.path.join(self.directory, "node_modules")
            if not os.path.exists(node_modules):
                try: tlog.warning("⚠️ [依赖缺失] 正在启动自动补全...")
                except Exception: pass
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
                    except OSError: pass
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
                    except Exception:
                        try: os.close(master_fd)
                        except OSError: pass
                
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
            except Exception: pass
            
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
                except OSError: pass
                if callback: callback(f"❌ [系统异常] 启动失败: {str(e)}")
                with self._lock: self._is_starting = False
                return False
            
            with self._lock: self._is_starting = False

            try:
                import re
                master_reader = io.open(master_fd, 'r', encoding='utf-8', errors='replace')
                while True:
                    if proc.poll() is not None: break
                    line = master_reader.readline()
                    if not line: break
                    line_str = line.strip()
                    # 🚀 自动感知并对正子进程实际绑定的端口
                    port_match = re.search(r'https?://(?:localhost|127\.0\.0\.1):(\d+)', line_str)
                    if port_match:
                        try:
                            actual_port = int(port_match.group(1))
                            if actual_port != self.port:
                                self.port = actual_port
                                tlog.info(f"🟢 [FrameworkDev] 感知到框架实际服务端口已对正为: {self.port}")
                        except Exception: pass
                    if callback: callback(line_str)
            except Exception as e:
                tlog.debug(f"ℹ️ [FrameworkDev] PTY 流已中断: {e}")
            finally:
                try: master_reader.close()
                except Exception:
                    try: os.close(master_fd)
                    except OSError: pass
            
            if proc:
                proc.wait()
            return True
        except Exception as e:
            try: tlog.error(f"🚨 [FrameworkDev] 异步启动发生未预期错误: {e}")
            except Exception: pass
            if callback: callback(f"❌ [系统异常] 异步启动失败: {str(e)}")
            with self._lock: self._is_starting = False
            return False
