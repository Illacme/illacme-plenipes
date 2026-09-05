#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Lightweight Dev Server
模块职责：提供零依赖的静态资源预览容器与端口冲突自愈探测。
🚀 [V11.7] 主权预览版本：支持物理目录映射与自动端口占用处理。
"""

import os
import sys
import re
import urllib.parse
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
    def do_GET(self):
        # 🛡️ [Anti-Recursion / Single-Page Redirect]
        # 1. 递归路径折叠 (如 /about/about/about/index.html -> /about/index.html)
        parsed = urllib.parse.urlparse(self.path)
        clean_path = parsed.path
        
        # 折叠重复路径段 (e.g. /about/about -> /about)
        dedup_path = re.sub(r'(?i)(/[^/]+)(?:\1)+', r'\1', clean_path)
        if dedup_path != clean_path:
            redirect_target = dedup_path + (f"?{parsed.query}" if parsed.query else "")
            self.send_response(302)
            self.send_header('Location', redirect_target)
            self.end_headers()
            return

        # 2. 单页虚拟目录重定向 (如 /about/ 或 /about/index.html -> /about.html)
        # 当请求的是子目录 index.html 或以 / 结尾，但物理磁盘不存在该目录/index.html，而父级存在同名单页时，发 302 重定向到父级单页
        base_dir = os.path.abspath(getattr(self, 'directory', '.'))
        rel_req = clean_path.lstrip('/')
        disk_path = os.path.abspath(os.path.join(base_dir, rel_req))
        
        if not os.path.exists(disk_path):
            norm_parts = [p for p in clean_path.strip('/').split('/') if p]
            if len(norm_parts) >= 1:
                last_part = norm_parts[-1]
                slug_candidate = norm_parts[-2] if (last_part in ('index.html', 'index') and len(norm_parts) >= 2) else norm_parts[-1]
                slug_candidate = os.path.splitext(slug_candidate)[0]
                
                prefix_parts = norm_parts[:-2] if (last_part in ('index.html', 'index') and len(norm_parts) >= 2) else norm_parts[:-1]
                parent_disk = os.path.join(base_dir, *prefix_parts)
                parent_single_page = os.path.join(parent_disk, f"{slug_candidate}.html")
                
                # 确认父级确实有该单页且不是 docs/blog 这种有子目录索引的实体目录
                if os.path.exists(parent_single_page) and os.path.isfile(parent_single_page):
                    sub_dir = os.path.join(parent_disk, slug_candidate)
                    if not (os.path.exists(sub_dir) and os.path.exists(os.path.join(sub_dir, "index.html"))):
                        parent_url_prefix = "/" + "/".join(prefix_parts) if prefix_parts else ""
                        target_url = f"{parent_url_prefix}/{slug_candidate}.html".replace('//', '/')
                        if parsed.query:
                            target_url += f"?{parsed.query}"
                        self.send_response(302)
                        self.send_header('Location', target_url)
                        self.end_headers()
                        return

        return super().do_GET()
    def guess_type(self, path):
        ctype = super().guess_type(path)
        if ctype and (ctype.startswith('text/') or ctype in ('application/javascript', 'application/json')):
            if 'charset=' not in ctype:
                ctype += '; charset=utf-8'
        return ctype

    def end_headers(self):
        # 🚫 [Anti-Cache] 本地静态预览开发态响应头：彻底阻断浏览器强缓存
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()

    def translate_path(self, path):
        translated = super().translate_path(path)
        if not os.path.exists(translated):
            dirname, basename = os.path.split(translated)
            stem, ext = os.path.splitext(basename)
            clean_stem = stem.lower().replace('_', '-').strip('-')

            # 1. 尝试当前目录中的准确同名或三模态索引变体 (如 blog.html, blog-index.html)
            if ext in ('.html', '') and os.path.exists(dirname):
                for variant in (f"{clean_stem}.html", f"{clean_stem}-index.html"):
                    v_path = os.path.join(dirname, variant)
                    if os.path.exists(v_path) and os.path.isfile(v_path):
                        return v_path
                
                # 尝试子目录跨层级三模态寻路 (如 blog/index.html, docs/index.html)
                sub_dir = os.path.join(dirname, clean_stem)
                if os.path.exists(sub_dir) and os.path.isdir(sub_dir):
                    sub_idx = os.path.join(sub_dir, 'index.html')
                    if os.path.exists(sub_idx):
                        return sub_idx

            # 2. 🚀 [跨层级自愈 A] 若请求子目录 index.html (如 /docs/index.html)，尝试父级目录扁平化文件 (如 docs.html)
            parent_dir = os.path.dirname(dirname)
            sub_folder = os.path.basename(dirname).lower().replace('_', '-').strip('-')
            if clean_stem in ('index', '') and os.path.exists(parent_dir):
                for variant in (f"{sub_folder}.html", f"{sub_folder}-index.html"):
                    p_variant = os.path.join(parent_dir, variant)
                    if os.path.exists(p_variant) and os.path.isfile(p_variant):
                        return p_variant

            # 3. 🚀 [跨层级自愈 B] 若请求子目录下普通文档 (如 /docs/quick-start.html 或 /docs/blog.html)，尝试父级同名文档或子目录索引
            if clean_stem not in ('index', '') and os.path.exists(parent_dir):
                p_doc = os.path.join(parent_dir, f"{clean_stem}.html")
                if os.path.exists(p_doc) and os.path.isfile(p_doc):
                    return p_doc
                p_child_idx = os.path.join(parent_dir, clean_stem, "index.html")
                if os.path.exists(p_child_idx) and os.path.isfile(p_child_idx):
                    return p_child_idx

            # 4. 🚀 [跨层级自愈 C] 若请求父级扁平频道页 (如 /docs.html)，但在子目录下存在 (如 /docs/index.html)
            if clean_stem not in ('index', '') and os.path.exists(dirname):
                child_idx = os.path.join(dirname, clean_stem, 'index.html')
                if os.path.exists(child_idx) and os.path.isfile(child_idx):
                    return child_idx

            # 5. 🚀 [跨层级自愈 D] 逐层剥离虚拟前缀探测 (如 /docs/en/docs.html -> /en/docs.html)
            base_dir = os.path.abspath(getattr(self, 'directory', '.'))
            try:
                rel_to_base = os.path.relpath(translated, base_dir).replace('\\', '/')
                parts = [p for p in rel_to_base.split('/') if p and p != '.']
                for i in range(1, len(parts)):
                    sub_candidate = os.path.join(base_dir, *parts[i:])
                    if os.path.exists(sub_candidate) and os.path.isfile(sub_candidate):
                        return sub_candidate
            except Exception:
                pass

        return translated


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
            except OSError:
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
            # 🛡️ [V76.5] 动态绑定 DevServer 实例，支持在线热替换目录 (Hot Directory Swapping)
            server_instance = self
            class BoundHandler(SovereignHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=server_instance.directory, **kwargs)

                def translate_path(self, path):
                    self.directory = server_instance.directory
                    return super().translate_path(path)
            
            class SovereignTCPServer(socketserver.TCPServer):
                allow_reuse_address = True

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
            except Exception:
                pass
            self.httpd = None
            self.thread = None
            return False

    def update_directory(self, new_dir: str):
        """🚀 [Hot Reload] 在线热替换服务物理目录，无需重启端口与重建 socket"""
        with self._lock:
            self.directory = os.path.abspath(new_dir)
            tlog.info(f"🔄 [DevServer] 预览服务物理目录已动态热重定向至: {self.directory}")

    def stop(self):
        """停止服务器"""
        with self._lock:
            if self.httpd:
                try:
                    self.httpd.shutdown()
                except Exception as e:
                    tlog.debug(f"ℹ️ [DevServer] 尝试 shutdown 发生异常: {e}")
                try:
                    self.httpd.server_close()
                except Exception as e:
                    tlog.debug(f"ℹ️ [DevServer] 尝试 server_close 发生异常: {e}")
                if self.thread and self.thread.is_alive() and self.thread != threading.current_thread():
                    try:
                        self.thread.join(timeout=1.0)
                    except Exception:
                        pass
                self.httpd = None
                self.thread = None
