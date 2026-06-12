# -*- coding: utf-8 -*-
"""
⚙️ Illacme Plenipes - Sovereign Orchestrator Hub
职责：全域主权编排中枢。负责任务流的代理调度与异步互斥管理。
🛡️ [V74.8 Decoupled]：逻辑分片架构，扫描与同步核心已委托至 .orchestration 模块。
"""

import threading
from typing import List, Tuple, Set, Optional, Any

from core.utils.tracing import tlog
from core.logic.orchestration.task_orchestrator import global_executor, TaskPriority

# 🚀 导入分片后的扫描引擎与同步核心
from .orchestration.scanner import build_task_queue
from .orchestration.sync_worker import perform_sync

def prepare_sync_tasks(engine: Any, requested_paths: Optional[List[str]] = None) -> Tuple[List[Any], Set[str]]:
    """🚀 [代理模式] 根据路由矩阵扫描物理目录，建立同步初始化队列"""
    return build_task_queue(engine, requested_paths)

def execute_full_sync(engine: Any, args: Any, task_queue: List[Any], current_source_files: Set[str]) -> None:
    """🚀 [代理模式] 核心任务并发调度派发区 (单次 Sync 逻辑)"""
    return perform_sync(engine, args, task_queue, current_source_files)

# 🔒 [V52.3] 主权原子锁：防止出版流水线重入与进度条飞涨
_publish_lock = threading.Lock()
_is_publishing = False

def start_asynchronous_sync(engine: Any, dry_run: bool = False, force: bool = False, sandbox: bool = False, requested_paths: Optional[List[str]] = None, target_langs: Optional[List[str]] = None) -> Optional[int]:
    """
    🚀 [V51.0] 异步同步触发器：专供 API/Dashboard 调用
    [V52.3 升级]：加入主权互斥检查，确保全球范围内只有一个出版流在运行。
    """
    global _is_publishing
    
    if _is_publishing:
        tlog.warning("⚠️ [主权拦截] 探测到已有出版任务正在运行，本次点火已取消以防止算力碰撞。")
        from core.logic.notification_hub import send_sync_lifecycle_notification
        send_sync_lifecycle_notification(engine, "BLOCKED", "出版点火被拦截", "已有出版任务正在后台运行，本次启动已取消。")
        return None

    # 1. 模拟 CLI 参数
    class MockArgs:
        def __init__(self):
            self.dry_run = dry_run
            self.force = force
            self.sandbox = sandbox
            self.watch = False
            self.path = requested_paths
            self.target_langs = target_langs
    
    args = MockArgs()
    
    # 2. 定义后台执行逻辑 (使用闭包保持对 engine 的引用)
    def _background_job():
        global _is_publishing
        with _publish_lock:
            try:
                _is_publishing = True
                tlog.info(f"⚡ [异步出版] 正在启动后台出版流水线 (DryRun: {dry_run}, Sandbox: {sandbox}, Paths: {requested_paths})...")
                task_queue, current_source_files = build_task_queue(engine, requested_paths)
                perform_sync(engine, args, task_queue, current_source_files)
                tlog.info("✅ [异步出版] 后台流水线任务已全量闭环。")
            except Exception as e:
                import traceback
                tlog.error(f"❌ [异步出版] 流水线溃决: {str(e)}\n{traceback.format_exc()}")
                from core.logic.notification_hub import send_sync_lifecycle_notification
                send_sync_lifecycle_notification(engine, "FAIL", "异步出版流水线异常崩溃", str(e))
            finally:
                _is_publishing = False
                # 🚀 [V78.6] 安全兜底：流水线跑完后，强制唤醒可能被挂起的监控狗
                if hasattr(engine, 'is_watchdog_suspended') and engine.is_watchdog_suspended:
                    engine.is_watchdog_suspended = False
                    tlog.info("🐕 [后台闭环] 已强行唤醒处于休眠状态的监控狗。")

    # 3. 提交至全局执行器 (优先级设为 CRITICAL 以确保立即响应)
    future = global_executor.submit(_background_job, priority=TaskPriority.CRITICAL, task_name="Async-Full-Publish")
    return id(future)

