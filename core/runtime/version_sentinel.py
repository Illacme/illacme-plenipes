#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Version Sentinel & Process Lifecycle Guardian
模块职责：负责运行时源码指纹采样、代码漂移（Drift）感知，以及 API 内核平滑自我接力重启。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import sys
import time
import threading
import subprocess
from typing import Dict, Any, List
from core.utils.tracing import tlog

class VersionSentinel:
    """🛰️ 运行时版本感知中枢与自愈看门狗"""
    
    _process_start_time: float = time.time()
    _monitored_dirs: List[str] = ["core", "services", "adapters"]
    _initial_max_mtime: float = 0.0
    _watcher_thread: threading.Thread = None
    _is_watching: bool = False
    _is_restarting: bool = False

    @classmethod
    def initialize(cls) -> None:
        """初始化进程启动指纹"""
        cls._process_start_time = time.time()
        cls._initial_max_mtime = cls.get_latest_code_mtime()
        tlog.debug(f"🛰️ [版本哨兵] 初始化就绪，基线代码时间戳: {cls._initial_max_mtime:.2f}")

    @classmethod
    def get_latest_code_mtime(cls) -> float:
        """快速扫描核心目录获取最新的 .py 文件物理修改时间"""
        max_mtime = 0.0
        cwd = os.getcwd()
        for d in cls._monitored_dirs:
            abs_dir = os.path.join(cwd, d)
            if not os.path.exists(abs_dir):
                continue
            for root, _, files in os.walk(abs_dir):
                for f in files:
                    if f.endswith(".py"):
                        try:
                            m = os.path.getmtime(os.path.join(root, f))
                            if m > max_mtime:
                                max_mtime = m
                        except OSError:
                            continue
        return max_mtime

    @classmethod
    def check_drift(cls) -> Dict[str, Any]:
        """
        探测磁盘源码较当前进程启动时是否发生代码漂移。
        返回漂移详情，供 API / UI 进行状态感知。
        """
        current_max = cls.get_latest_code_mtime()
        # 若最新修改时间晚于进程启动时间且晚于初始加载时间超过 1 秒，判定为代码已更新
        is_drifted = (current_max > cls._process_start_time) and (current_max > cls._initial_max_mtime + 0.5)
        
        drift_files = []
        if is_drifted:
            cwd = os.getcwd()
            for d in cls._monitored_dirs:
                abs_dir = os.path.join(cwd, d)
                if not os.path.exists(abs_dir):
                    continue
                for root, _, files in os.walk(abs_dir):
                    for f in files:
                        if f.endswith(".py"):
                            fp = os.path.join(root, f)
                            try:
                                if os.path.getmtime(fp) > cls._process_start_time:
                                    rel_p = os.path.relpath(fp, cwd)
                                    drift_files.append(rel_p)
                                    if len(drift_files) >= 5:
                                        break
                            except OSError:
                                pass
                    if len(drift_files) >= 5:
                        break

        uptime = round(time.time() - cls._process_start_time, 1)
        return {
            "is_drifted": is_drifted,
            "process_start_time": cls._process_start_time,
            "uptime_seconds": uptime,
            "latest_code_mtime": current_max,
            "drift_files": drift_files,
            "status": "drifted" if is_drifted else "aligned"
        }

    @classmethod
    def trigger_process_restart(cls, delay_seconds: float = 0.3) -> None:
        """
        优雅注销当前进程并执行原地接力重启（os.execv 继承参数与端口）。
        """
        if cls._is_restarting:
            return
        cls._is_restarting = True
        tlog.warning("🔄 [内核重启] 正在准备释放资源并平滑接力重启当前进程...")

        def _restart_worker():
            time.sleep(delay_seconds)
            try:
                from core.runtime.engine_singleton import get_global_engine, _SINGLETON_SOCKET
                engine = get_global_engine()
                
                # 1. 安全关闭 DevServer
                if engine and hasattr(engine, 'preview_server') and engine.preview_server:
                    try:
                        engine.preview_server.stop()
                    except Exception:
                        pass

                # 2. 安全关闭看门狗
                from core.runtime.engine_singleton import get_global_observer
                obs = get_global_observer()
                if obs:
                    try:
                        obs.stop()
                    except Exception:
                        pass

                # 3. 释放单例网络锁（关闭 socket 释放 43210 端口）
                import core.runtime.engine_singleton as es
                if es._SINGLETON_SOCKET:
                    try:
                        es._SINGLETON_SOCKET.close()
                        es._SINGLETON_SOCKET = None
                    except Exception:
                        pass
                
                # 短暂等待套接字完全进入 TIME_WAIT 之外的状态
                time.sleep(0.3)
                
                # 4. 原地 execv 重启当前 Python 进程
                executable = sys.executable
                args = [executable] + sys.argv
                tlog.success(f"🚀 [内核重启] 即刻激活全新进程: {args}")
                if os.name == 'nt':
                    subprocess.Popen(args)
                    os._exit(0)
                else:
                    os.execv(executable, args)
            except Exception as e:
                tlog.error(f"🛑 [内核重启失败]: {e}")
                cls._is_restarting = False

        threading.Thread(target=_restart_worker, daemon=True).start()

    @classmethod
    def start_auto_reload_watcher(cls, check_interval: float = 2.0) -> None:
        """启动后台看门狗，当检测到核心代码变更时自动触发进程重载"""
        if cls._is_watching:
            return
        cls._is_watching = True
        cls.initialize()

        def _watch_loop():
            tlog.info("🐕 [热重载看门狗] 核心代码感知已激活 (core, services, adapters)...")
            consecutive_hits = 0
            while cls._is_watching and not cls._is_restarting:
                time.sleep(check_interval)
                status = cls.check_drift()
                if status["is_drifted"]:
                    consecutive_hits += 1
                    # 连续检测到两次变动，防抖确认后执行重启
                    if consecutive_hits >= 2:
                        tlog.warning(f"⚡ [代码变更感知] 检测到核心代码已更新 ({', '.join(status['drift_files'])}), 正在自动平滑重启...")
                        cls.trigger_process_restart(delay_seconds=0.2)
                        break
                else:
                    consecutive_hits = 0

        cls._watcher_thread = threading.Thread(target=_watch_loop, daemon=True)
        cls._watcher_thread.start()

# 模块导入时自动预热基线
VersionSentinel.initialize()
