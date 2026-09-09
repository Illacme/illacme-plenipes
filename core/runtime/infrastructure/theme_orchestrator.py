#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Theme DevServer Orchestrator
职责：多主题一键 DevServer 预览编排、端口白名单收割与进程自愈中枢。
规范：SOP-01 (≤ 300行), SOP-04 (非交互后台), SOP-13 (母本绝对纯净与物理隔离)。
"""

import os
import sys
import time
import signal
import socket
import shutil
import atexit
import threading
import subprocess
import urllib.request
import urllib.error
from collections import deque
from typing import Optional, Dict, Any, Tuple, List

from core.utils.tracing import tlog
from core.utils.event_bus import bus

PROTECTED_PORTS = {43210, 43211, 43212}
ALLOWED_PREVIEW_PORTS = {43213, 43214}
ALLOWED_PROCESS_FINGERPRINTS = ("node", "next", "vite", "astro", "docusaurus", "python", "dev_server")
ACCEPTED_HEALTH_STATUS_CODES = {200, 301, 302, 307, 308}
STARTUP_TIMEOUT = 30.0
HANDSHAKE_INTERVAL = 0.3


class ThemeDevServerOrchestrator:
    """工业级多主题 DevServer 统一生命周期编排器"""

    def __init__(self):
        self.active_process: Optional[subprocess.Popen] = None
        self.active_theme: str = "sovereign"
        self.active_port: int = 43213
        self.log_ring_buffer: deque = deque(maxlen=100)
        self._is_launching: bool = False
        atexit.register(self.shutdown_all)

    def resolve_authoritative_port(self, requested_port: Optional[int] = None, engine: Any = None) -> int:
        """优先级：请求参数 > 环境变量 > 配置项 > 默认 43213"""
        if requested_port and requested_port not in PROTECTED_PORTS:
            return requested_port
        env_p = os.environ.get("ILLACME_PREVIEW_PORT")
        if env_p and env_p.isdigit() and int(env_p) not in PROTECTED_PORTS:
            return int(env_p)
        if engine and hasattr(engine, "config") and hasattr(engine.config, "system"):
            cfg_p = getattr(engine.config.system, "serve_port", 43213)
            if cfg_p not in PROTECTED_PORTS:
                return cfg_p
        return 43213

    def reclaim_port(self, port: int) -> bool:
        """端口安全白名单收割与幽灵杀手：仅收割允许范围且画像命中的进程"""
        if port in PROTECTED_PORTS:
            raise PermissionError(f"🚨 [安全拦截] 物理保护端口 {port} 严禁任何收割操作！")
        if port not in ALLOWED_PREVIEW_PORTS:
            tlog.warning(f"⚠️ [收割防线] 端口 {port} 未在允许预览端口列表内，跳过收割。")
            return False
        try:
            out = subprocess.check_output(["lsof", "-nP", "-a", f"-iTCP:{port}", "-sTCP:LISTEN", "-ti"], text=True, stderr=subprocess.DEVNULL)
            pids = [int(p.strip()) for p in out.splitlines() if p.strip().isdigit()]
        except Exception:
            try:
                out = subprocess.check_output(["lsof", "-ti", f":{port}"], text=True, stderr=subprocess.DEVNULL)
                pids = [int(p.strip()) for p in out.splitlines() if p.strip().isdigit()]
            except Exception: pids = []
        my_pid = os.getpid()
        for pid in pids:
            if pid == my_pid:
                continue
            try:
                ps_info = subprocess.check_output(["ps", "-p", str(pid), "-o", "comm=,args="], text=True).lower()
                if any(fp in ps_info for fp in ALLOWED_PROCESS_FINGERPRINTS):
                    tlog.info(f"🧹 [幽灵收割] 正在终止端口 {port} 上的进程 PID {pid}...")
                    try:
                        os.killpg(os.getpgid(pid), signal.SIGTERM)
                    except Exception:
                        try: os.kill(pid, signal.SIGTERM)
                        except Exception: pass
                    time.sleep(0.5)
                    try:
                        os.kill(pid, 0)
                        os.killpg(os.getpgid(pid), signal.SIGKILL)
                    except Exception: pass
                else:
                    tlog.warning(f"⚠️ [画像拒绝] PID {pid} 未命中预览白名单画像，安全跳过。")
            except Exception: pass
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("", port))
                return True
            except OSError:
                return False

    def check_node_runtime(self) -> Tuple[bool, str, str]:
        """Node.js 运行时探针：检测版本是否 >= 18.0.0"""
        node_bin = shutil.which("node")
        if not node_bin:
            return False, "", "本地未检测到 Node.js 运行时，无法运行前端 SSG 框架。"
        try:
            raw_v = subprocess.check_output([node_bin, "--version"], text=True, stderr=subprocess.DEVNULL).strip()
            v_num = int(raw_v.lstrip("v").split(".")[0])
            if v_num < 18:
                return False, raw_v, f"Node.js 版本 {raw_v} 过低 (需要 >= 18.0.0)。"
            return True, raw_v, ""
        except Exception as e:
            return False, "", f"Node.js 探针执行失败: {e}"

    def ensure_content_readiness(self, theme_id: str, imprint_id: str, engine: Any = None) -> str:
        """冷启动内容预装配守卫 (SOP-13 隔离)：确保派生目录具有最小多语言脚手架"""
        from core.config.config import THEMES_DIR
        imprint_root = getattr(engine, "imprint_root", os.path.join("imprints", imprint_id))
        target_cwd = os.path.abspath(os.path.join(imprint_root, "themes", theme_id))
        mother_dir = os.path.abspath(os.path.join(os.getcwd(), THEMES_DIR, theme_id))
        if not os.path.exists(target_cwd) and os.path.exists(mother_dir):
            os.makedirs(os.path.dirname(target_cwd), exist_ok=True)
            tlog.info(f"🧬 [SOP-13 派生] 从母本 {theme_id} 派生到品牌隔离区: {target_cwd}")
            shutil.copytree(mother_dir, target_cwd, ignore=shutil.ignore_patterns("node_modules", ".next", ".astro", ".docusaurus", "dist", "build", ".temp", ".git"))
        os.makedirs(target_cwd, exist_ok=True)
        target_nm, mother_nm = os.path.join(target_cwd, "node_modules"), os.path.join(mother_dir, "node_modules")
        if not os.path.exists(target_nm) and os.path.exists(mother_nm):
            try: os.symlink(mother_nm, target_nm)
            except Exception: pass
        active_langs = ["zh"]
        if engine and hasattr(engine, "config") and engine.config.i18n_settings:
            active_langs = [engine.config.i18n_settings.source.lang_code or "zh"]
            if engine.config.i18n_settings.enabled and engine.config.i18n_settings.targets:
                for t in engine.config.i18n_settings.targets:
                    if t.lang_code and t.lang_code not in active_langs:
                        active_langs.append(t.lang_code)
        if "docusaurus" in theme_id.lower():
            legacy_idx = os.path.join(target_cwd, "src/pages/index.md")
            if os.path.exists(legacy_idx) and os.path.exists(os.path.join(target_cwd, "src/pages/index.js")):
                try: os.remove(legacy_idx)
                except Exception: pass
            docs_dir = os.path.join(target_cwd, "docs")
            os.makedirs(docs_dir, exist_ok=True)
            intro_file = os.path.join(docs_dir, "intro.md")
            if not os.path.exists(intro_file):
                with open(intro_file, "w", encoding="utf-8") as f:
                    f.write("# Introduction\n\nWelcome to Illacme Plenipes.")
            for lang in active_langs:
                td = os.path.join(target_cwd, f"i18n/{lang}/docusaurus-plugin-content-docs/current")
                os.makedirs(td, exist_ok=True)
                sample_file = os.path.join(td, "intro.md")
                if not os.path.exists(sample_file):
                    with open(sample_file, "w", encoding="utf-8") as f:
                        f.write(f"# Document ({lang})\n\nWelcome to Illacme Plenipes.")
        elif "nextra" in theme_id.lower():
            pages_dir = os.path.join(target_cwd, "pages")
            os.makedirs(pages_dir, exist_ok=True)
            idx_file = os.path.join(pages_dir, "index.mdx")
            if not os.path.exists(idx_file):
                with open(idx_file, "w", encoding="utf-8") as f:
                    f.write("# Illacme Press\n\nWelcome to Nextra documentation.")
        gitignore_path = os.path.join(target_cwd, ".gitignore")
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write(".next\n.astro\n.docusaurus\ndist\nbuild\nnode_modules\n.plenipes\n*.log\n")
        return target_cwd

    def resolve_theme_command(self, theme_id: str, port: int) -> Tuple[str, Dict[str, str], bool]:
        """多框架 CLI 命令与参数异构映射，返回 (cmd, env, is_node_framework)"""
        t_lower = theme_id.lower()
        base_env = {**os.environ, "PORT": str(port), "HOST": "0.0.0.0", "BROWSER": "none"}
        if "nextra" in t_lower:
            return f"npm run dev -- -p {port}", base_env, True
        elif "docusaurus" in t_lower:
            return f"npm run build && npx -y docusaurus serve --port {port} --host 0.0.0.0 --no-open", base_env, True
        elif any(k in t_lower for k in ("starlight", "astro", "vitepress")):
            return f"npm run dev -- --port {port} --host 0.0.0.0", base_env, True
        return "", base_env, False

    def wait_http_ready(self, port: int, timeout: float = STARTUP_TIMEOUT) -> Tuple[bool, str]:
        """重定向宽容探活：接纳 200/301/302/307/308，提取 final_url"""
        start, url, final_target = time.time(), f"http://127.0.0.1:{port}/", f"http://127.0.0.1:{port}/"
        class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        opener = urllib.request.build_opener(NoRedirectHandler)
        while time.time() - start < timeout:
            if self.active_process and self.active_process.poll() is not None:
                return False, url
            for host in ("127.0.0.1", "localhost"):
                try:
                    probe_url = f"http://{host}:{port}/"
                    req = urllib.request.Request(probe_url, headers={"User-Agent": "IllacmeOrchestratorProbe/1.0"})
                    try:
                        resp = opener.open(req, timeout=1.0)
                        code = resp.getcode()
                        if resp.headers and "Location" in resp.headers: final_target = resp.headers["Location"]
                    except urllib.error.HTTPError as e:
                        code = e.code
                        if e.headers and "Location" in e.headers: final_target = e.headers["Location"]
                    if code in ACCEPTED_HEALTH_STATUS_CODES:
                        return True, final_target
                except Exception: pass
            time.sleep(HANDSHAKE_INTERVAL)
        return False, url

    def launch_dev_server(self, theme_id: str, imprint_id: str = "default", requested_port: Optional[int] = None, engine: Any = None) -> Dict[str, Any]:
        """一键点火总入口：收割、探针、预装配、异构点火与深度探活全生命周期闭环"""
        self._is_launching = True
        self.log_ring_buffer.clear()
        if self.active_process:
            try:
                os.killpg(os.getpgid(self.active_process.pid), signal.SIGTERM)
                time.sleep(0.2)
                if self.active_process.poll() is None: os.killpg(os.getpgid(self.active_process.pid), signal.SIGKILL)
            except Exception: pass
            self.active_process = None
        if engine and getattr(engine, "preview_server", None):
            try: engine.preview_server.stop()
            except Exception: pass
            engine.preview_server = None
        target_port = self.resolve_authoritative_port(requested_port, engine)
        bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"🔒 [Orchestrator] 正在锁定并净化端口 {target_port}...")
        self.reclaim_port(target_port)
        cmd, env, is_node_framework = self.resolve_theme_command(theme_id, target_port)
        if is_node_framework:
            node_ok, node_ver, reason = self.check_node_runtime()
            if not node_ok:
                bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"⚠️ [优雅降级] {reason}，已自动切回原生极速模式。")
                return self.launch_dev_server("sovereign", imprint_id, target_port, engine)
        target_cwd = self.ensure_content_readiness(theme_id, imprint_id, engine)
        if engine and hasattr(engine, 'ssg_adapter') and engine.ssg_adapter:
            try:
                engine.ssg_adapter.compile_theme_options()
            except Exception as opt_err:
                tlog.warning(f"⚠️ [Orchestrator] 启动前热编译主题选项容错: {opt_err}")
        if is_node_framework:
            bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"⚡ [Orchestrator] 正在以 PTY 模式点火 {theme_id}: {cmd}")
            try:
                proc = subprocess.Popen(cmd, shell=True, cwd=target_cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, preexec_fn=os.setpgrp)
                self.active_process, self.active_theme, self.active_port = proc, theme_id, target_port
                def _log_reader():
                    for line in iter(proc.stdout.readline, ""):
                        line_str = line.strip()
                        self.log_ring_buffer.append(line_str)
                        bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"[{theme_id}] {line_str}")
                    proc.stdout.close()
                threading.Thread(target=_log_reader, daemon=True).start()
                ready, final_url = self.wait_http_ready(target_port, timeout=STARTUP_TIMEOUT)
                if not ready:
                    time.sleep(0.3)
                    tail = list(self.log_ring_buffer)[-20:]
                    poll_code = proc.poll()
                    err_msg = f"DevServer 进程已异常退出 (Exit Code: {poll_code})。" if poll_code is not None else f"DevServer 在 {STARTUP_TIMEOUT} 秒内未响应就绪（超时熔断）。"
                    return {"status": "error", "message": err_msg, "tail_logs": tail, "port": target_port}
                bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"✨ [Orchestrator] {theme_id} 成功上线: http://localhost:{target_port}")
                return {"status": "success", "theme": theme_id, "port": target_port, "url": f"http://localhost:{target_port}", "final_url": final_url, "mode": "framework"}
            except Exception as e:
                return {"status": "error", "message": f"进程拉起异常: {e}", "tail_logs": list(self.log_ring_buffer)}
            finally:
                self._is_launching = False
        else:
            from core.utils.dev_server import DevServer
            preview_dir = getattr(engine, "paths", {}).get("site_dir", target_cwd) if engine else target_cwd
            srv = DevServer(directory=preview_dir, port=target_port)
            srv.start(blocking=False)
            if engine:
                engine.preview_server = srv
            self.active_theme, self.active_port, self._is_launching = theme_id, target_port, False
            return {"status": "success", "theme": theme_id, "port": target_port, "url": f"http://localhost:{target_port}", "mode": "static"}

    def shutdown_all(self) -> None:
        """主进程退出或全局收割钩子"""
        if self.active_process:
            try:
                os.killpg(os.getpgid(self.active_process.pid), signal.SIGTERM)
                time.sleep(0.3)
                if self.active_process.poll() is None:
                    os.killpg(os.getpgid(self.active_process.pid), signal.SIGKILL)
            except Exception: pass
            self.active_process = None
        if self.active_port:
            try: self.reclaim_port(self.active_port)
            except Exception: pass


theme_orchestrator = ThemeDevServerOrchestrator()
