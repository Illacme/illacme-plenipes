# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Desktop Application Launcher
模块职责：独立桌面端入口，实现单例检测、后台网关点火、系统原生窗口与浏览器双模唤起。
🛡️ [SOP-01 规范]：单文件行数严格 ≤ 300 行。
"""

import os
import sys
import time
import socket
import signal
import threading
import webbrowser
from typing import Optional

from core.utils.tracing import tlog
from core.utils.frozen_paths import FrozenPathResolver

# 遵从 Rule #6 系统默认端口规划
SINGLETON_PORT = 43210
API_PORT = 43212
API_URL = f"http://127.0.0.1:{API_PORT}/"
HEALTH_URL = f"http://127.0.0.1:{API_PORT}/health"

_lock_socket: Optional[socket.socket] = None
_server_thread: Optional[threading.Thread] = None
_should_exit = threading.Event()


def acquire_singleton_lock(port: int = SINGLETON_PORT) -> bool:
    """尝试绑定单例锁端口。若绑定失败说明已有实例正在运行"""
    global _lock_socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        s.bind(("127.0.0.1", port))
        s.listen(1)
        _lock_socket = s
        return True
    except (socket.error, OSError):
        return False


def release_singleton_lock() -> None:
    """释放单例锁句柄"""
    global _lock_socket
    if _lock_socket:
        try:
            _lock_socket.close()
        except Exception:
            pass
        _lock_socket = None


def wait_for_api_ready(timeout_sec: float = 15.0) -> bool:
    """轮询探测后台 API 服务是否健康就绪"""
    start = time.time()
    while time.time() - start < timeout_sec:
        if _should_exit.is_set():
            return False
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            res = sock.connect_ex(("127.0.0.1", API_PORT))
            sock.close()
            if res == 0:
                return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def _run_server_background() -> None:
    """后台工作线程：拉起 FastAPI API 服务"""
    try:
        from services.api.server import start_api_server
        start_api_server(host="127.0.0.1", port=API_PORT, blocking=True)
    except Exception as e:
        tlog.error(f"❌ [桌面网关] 启动异常: {e}")


def _launch_native_window(target_url: str) -> bool:
    """尝试使用 pywebview 打开独立的毛玻璃高质感原生窗口"""
    try:
        import webview
        tlog.info("🖥️ [桌面应用] 正在唤起系统原生 WebKit/WebView2 窗口...")

        def _on_closed():
            _should_exit.set()
            release_singleton_lock()
            tlog.info("🛑 [桌面应用] 原生窗口已关闭，优雅退出进程。")

        window = webview.create_window(
            title="Illacme Plenipes · 全球私人出版社",
            url=target_url,
            width=1280,
            height=820,
            min_size=(960, 600),
            background_color="#0b1219"
        )
        window.events.closed += _on_closed
        webview.start(debug=False)
        return True
    except ImportError:
        tlog.info("ℹ️ [桌面应用] 当前环境未集成 pywebview，自动降级为默认浏览器伴侣模式。")
        return False
    except Exception as e:
        tlog.warning(f"⚠️ [桌面应用] 原生窗口初始化失败，切换为浏览器模式: {e}")
        return False


def run_desktop_app() -> int:
    """桌面应用程序主函数"""
    tlog.info("🚀 [桌面应用] 正在启动 Illacme Plenipes 独立桌面工作台...")

    # 1. 单例进程检测 (Rule #6 端口规划)
    if not acquire_singleton_lock(SINGLETON_PORT):
        tlog.info("ℹ️ [单例检测] 检测到已存在活跃的出版社内核，直接唤起浏览器控制台。")
        webbrowser.open(API_URL)
        return 0

    # 2. 注册系统退出信号监听
    def _sig_handler(signum, frame):
        _should_exit.set()
        release_singleton_lock()
        sys.exit(0)

    signal.signal(signal.SIGINT, _sig_handler)
    signal.signal(signal.SIGTERM, _sig_handler)

    try:
        # 3. 后台启动核心网关服务
        server_thread = threading.Thread(target=_run_server_background, daemon=True, name="DesktopAPIServer")
        server_thread.start()

        # 4. 等待服务就绪
        if not wait_for_api_ready(timeout_sec=15.0):
            tlog.error("❌ [桌面应用] 服务启动超时，请检查端口占用或系统防火墙。")
            release_singleton_lock()
            return 1

        tlog.info(f"✨ [桌面应用] 出版社网关已就绪: {API_URL}")

        # 5. 双模呈现：优先原生独立窗口，降级浏览器标签页
        native_success = _launch_native_window(API_URL)
        if not native_success:
            webbrowser.open(API_URL)
            tlog.info("💡 [伴侣模式] 仪表盘已在默认浏览器打开。按 Ctrl+C 可停止桌面服务。")
            while not _should_exit.is_set():
                time.sleep(1)

        return 0

    except KeyboardInterrupt:
        tlog.info("🛑 [桌面应用] 接收到退出中断信号。")
        return 0
    finally:
        release_singleton_lock()


if __name__ == "__main__":
    sys.exit(run_desktop_app())
