# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Illacme-plenipes Engine Singleton & State Management
职责：负责引擎全局单例的下沉管理、物理单例锁抢占及状态跨层传输。
架构：已按 SOP-04 执行物理降解，实现状态与启动入口的解耦。
"""

import socket
import sys
import time
from core.utils.tracing import tlog

# 🚀 [主权容器] 全局单例物理挂载点
_SINGLETON_SOCKET = None
_GLOBAL_ENGINE = None
_GLOBAL_OBSERVER = None
_GLOBAL_ARGS = None

def set_global_args(args):
    global _GLOBAL_ARGS
    _GLOBAL_ARGS = args

def get_global_args():
    return _GLOBAL_ARGS

def get_global_engine():
    """🚀 获取引擎全局单例 (供 SSG 适配器或管线深度组件调用)"""
    return _GLOBAL_ENGINE

def set_global_engine(engine):
    """🛡️ 注册引擎全局单例 (支持热重载清理)"""
    global _GLOBAL_ENGINE
    if _GLOBAL_ENGINE and hasattr(_GLOBAL_ENGINE, 'sentinel'):
        try:
            tlog.debug("🔄 [热重载清理] 正在释放旧引擎的哨兵资源...")
            _GLOBAL_ENGINE.sentinel.stop()
        except: pass
    _GLOBAL_ENGINE = engine

def get_global_observer():
    return _GLOBAL_OBSERVER

def set_global_observer(observer):
    global _GLOBAL_OBSERVER
    if _GLOBAL_OBSERVER:
        try:
            tlog.debug("🔄 [热重载清理] 正在安全切断旧金库的实时监听...")
            _GLOBAL_OBSERVER.stop()
            _GLOBAL_OBSERVER.join(timeout=2.0)
        except: pass
    _GLOBAL_OBSERVER = observer

def acquire_singleton_lock(port=43210, is_service=True):
    """
    进程级单例防线 (OS-Level Singleton Mutex)
    基于配置文件动态分配防撞端口。
    🚀 [V50.5] 增强：增加 5 秒宽容期，支持主权接力时的平滑过渡。
    当为 CLI 瞬时操作时，端口冲突仅发出并发警告，不强制退出。
    """
    global _SINGLETON_SOCKET
    
    attempts = 0
    max_attempts = 5
    while attempts < max_attempts:
        _SINGLETON_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            _SINGLETON_SOCKET.bind(('127.0.0.1', port))
            return # 成功夺取主权锁
        except socket.error:
            if attempts == 0:
                tlog.debug(f"⏳ [端口竞争] 正在等待端口 {port} 释放主权 (尝试 {attempts+1}/{max_attempts})...")
            
            attempts += 1
            if attempts < max_attempts:
                time.sleep(1)
            else:
                if is_service:
                    tlog.error(f"\n🛑 [运行冲突] 启动失败：端口 {port} 已被占用，检测到系统已经在后台运行！")
                    tlog.error("   └── 💡 为了保护您的文章数据和电脑内存，本次重复启动已自动拦截。")
                    tlog.error("   └── 请检查是否开了多个终端窗口，或者在 config.yaml 中修改 singleton_port。")
                    sys.exit(1)
                else:
                    tlog.warning(f"\n⚠️ [并发警示] 检测到端口 {port} 已被常驻服务或其他进程占用，但本次为瞬时 CLI 命令，系统已自动降级放行并启动 SQLite 共享并发锁。")
                    tlog.warning("   └── 💡 此时多个进程可能同时在运行同步或查询任务，这通常是安全的，但请避免对同一篇文章发起冲突的操作。")
                    _SINGLETON_SOCKET = None
                    return

def send_notification(title, message):
    """
    🚀 跨平台系统通知调度器
    支持：macOS (osascript), Linux (notify-send), Windows (PowerShell)
    """
    import platform
    import subprocess
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            cmd = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", cmd], check=False)
        elif system == "Linux": # Linux
            subprocess.run(["notify-send", title, message], check=False)
        elif system == "Windows": # Windows
            cmd = f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('{message}', '{title}')"
            subprocess.run(["powershell", "-Command", cmd], check=False)
    except Exception as e:
        tlog.debug(f"系统通知发送失败: {e}")
