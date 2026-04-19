#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes (v14.2) - 工业级架构双向解耦版 (CLI Entry)
模块职责：本地运行的命令行入口客户端。
"""

import time
import signal
import os
import shutil

from core.utils import setup_logger
from core.engine import IllacmeEngine
from core.cli_bootstrap import parse_args_and_lock
from core.orchestrator import prepare_sync_tasks, execute_full_sync
from core.daemon import start_watchdog

logger = setup_logger()

# 全局句柄，用于捕获退出信号时安全卸载资源
global_engine = None
global_observer = None
global_watch_pool = None

def graceful_shutdown(signum, frame):
    """拦截操作系统级的中断信号，执行防内存撕裂的终极快照固化"""
    logger.warning("\n⚠️ 收到停止指令！正在尝试安全保存数据并关闭系统...")
    
    if global_observer:
        global_observer.stop()
        logger.info("  └── [1/3] 文件夹自动监控已关闭。")
        
    if global_watch_pool:
        global_watch_pool.shutdown(wait=False)
        logger.info("  └── [2/3] 正在中断尚未开始的排队任务。")
        
    if global_engine and hasattr(global_engine, 'meta'):
        try:
            # 加入 try-except 保护，防止极低概率的 I/O 阻塞导致无法走到退出这一步
            global_engine.meta.force_save()
            logger.info("  └── [3/3] 文章处理进度已 100% 安全存档。")
        except Exception as e:
            logger.error(f"  └── ⚠️ 账本存档发生异常: {e}")
            
    logger.info("🛑 物理主进程已切断，系统强行下线！")
    
    # 🚀 核弹级物理熄火开关：无视所有挂起的子线程和网络 I/O，直接呼叫 OS 杀掉整个进程树！
    import os
    os._exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

if __name__ == "__main__":
    args = parse_args_and_lock()
    
    # 挂载主引擎
    engine = IllacmeEngine(args.config, no_ai=args.no_ai)
    global_engine = engine 

    # 🚀 [V31.2] 一键重置（物理清理模式）
    if args.clean:
        logger.info("🧹 [系统维护] 正在响应 --clean 指令，物理重置同步状态...")
        
        # 1. 清理分身影子库
        shadow_dir = engine.paths.get('shadow')
        if shadow_dir and os.path.exists(shadow_dir):
            import shutil
            shutil.rmtree(shadow_dir)
            logger.info(f"   └── ✨ 已清除影子资产目录: {shadow_dir}")
            
        # 2. 清理元数据账本
        db_path = engine.config.metadata_db
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"   └── ✨ 已清除元数据账本: {db_path}")
            
        logger.info("✨ 重置完成！后续将以全量同步模式启动。")

    # 🛡️ [V34.6 Sentinel v2.0] 主动哨兵模式
    if args.sentinel:
        engine.sentinel.run_health_check(auto_fix=True)
        sys.exit(0)

    # 构建任务队列 (接入选择性路径过滤)
    task_queue, current_source_files = prepare_sync_tasks(engine, requested_paths=args.path)
    
    # 单次全量/增量测绘
    if args.sync or not args.watch:
        execute_full_sync(engine, args, task_queue, current_source_files)
        from core.garden_exporter import export_digital_garden
        export_digital_garden(engine)
        
    # 启动看门狗守护
    if args.watch:
        # 🚀 [V18.6 V6] 物理保护位：通知引擎目前处于监控模式，激活针对 Docusaurus 的并发写保护逻辑
        engine.meta.is_watch_mode = True
        global_observer, global_watch_pool = start_watchdog(engine, args, current_source_files)
        while True: 
            time.sleep(1)