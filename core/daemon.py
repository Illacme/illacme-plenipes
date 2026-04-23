#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Watchdog Daemon
模块职责：目录监控启动中枢。
🛡️ [AEL-Iter-v5.3]：基于分层架构的 TDR 复健版本。
"""

import logging
from concurrent.futures import ThreadPoolExecutor
try:
    from watchdog.observers import Observer
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

from .services.daemon_handler import ChangeHandler

logger = logging.getLogger("Illacme.plenipes")

def start_watchdog(engine, args, current_source_files):
    """启动看门狗实时热更探针 (Daemon 模式)"""
    if not HAS_WATCHDOG:
        logger.error("🛑 无法启动守护进程：缺少 watchdog 依赖。")
        return None, None

    logger.info(f"👀 正在监听文件夹: {engine.vault_root}")
    
    watch_pool = ThreadPoolExecutor(max_workers=engine.max_workers)
    handler = ChangeHandler(engine, args, current_source_files, watch_pool)
    
    observer = Observer()
    observer.schedule(handler, engine.vault_root, recursive=True)
    observer.start()
    
    return observer, watch_pool