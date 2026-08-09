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
_pending_sync_queue = []

def start_asynchronous_sync(engine: Any, dry_run: bool = False, force: bool = False, sandbox: bool = False, requested_paths: Optional[List[str]] = None, target_langs: Optional[List[str]] = None, clear_cache: bool = False) -> Optional[int]:
    """
    🚀 [V51.0] 异步同步触发器：专供 API/Dashboard 调用
    [V52.3 升级]：支持任务排队与语种无缝追加机制，杜绝二次并发碰撞拦截。
    """
    global _is_publishing, _pending_sync_queue
    
    with _publish_lock:
        if _is_publishing:
            tlog.info(f"⏳ [排队追加] 探测到已有出版任务在运行，已将 requested_paths={requested_paths}, target_langs={target_langs} 压入排队队列...")
            _pending_sync_queue.append({
                'dry_run': dry_run, 'force': force, 'sandbox': sandbox,
                'requested_paths': requested_paths, 'target_langs': target_langs,
                'clear_cache': clear_cache
            })
            return 999999  # 返回排队标记 ID

    # 1. 模拟 CLI 参数
    class MockArgs:
        def __init__(self):
            self.dry_run = dry_run
            self.force = force
            self.clean = clear_cache or force
            self.sandbox = sandbox
            self.watch = False
            self.path = requested_paths
            self.target_langs = target_langs
    
    args = MockArgs()
    
    langs_to_clean = target_langs
    if not langs_to_clean and hasattr(engine, "config") and getattr(engine.config, "i18n_settings", None):
        langs_to_clean = [t.lang_code for t in engine.config.i18n_settings.targets]

    cleaned_bak_files = []
    if langs_to_clean:
        try:
            task_queue, _ = build_task_queue(engine, requested_paths)
            import os
            for task_path, prefix, src_rel, target_slot in task_queue:
                # 🚀 [V10.8] 正确推导出相对于 vault 根目录的相对路径，以解决命名冲突造成的元数据 ledger 查找失败
                rel_file_path = os.path.relpath(task_path, engine.paths.get('vault', '.')).replace('\\', '/')
                doc_info = engine.meta.get_doc_info(rel_file_path) if hasattr(engine, "meta") and engine.meta else {}
                sub_dir = doc_info.get("sub_dir", "")
                slug = doc_info.get("slug")
                if slug and hasattr(engine, "route_manager") and hasattr(engine, "paths"):
                    cache_dir = engine.paths.get("cache")
                    target_ext = os.path.splitext(rel_file_path)[1].lower() or ".md"
                    for lang in langs_to_clean:
                        try:
                            cache_mirror = engine.route_manager.resolve_physical_path(
                                cache_dir, lang, prefix, sub_dir, slug, target_ext, source_type=target_slot
                            )
                            if os.path.exists(cache_mirror):
                                bak_file = cache_mirror + ".bak"
                                tlog.info(f"🧹 [主线程缓存保护] 创建旧快照备份: {cache_mirror} -> {bak_file}")
                                os.replace(cache_mirror, bak_file)
                                cleaned_bak_files.append((cache_mirror, bak_file))
                        except Exception as ce:
                            tlog.warning(f"⚠️ [主线程清理缓存失败] {src_rel} / {lang}: {ce}")
        except Exception as qe:
            tlog.warning(f"⚠️ [主线程清理缓存构建队列失败]: {qe}")

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
                # 任务成功闭环，物理删除旧快照备份
                import os
                for orig_file, bak_file in cleaned_bak_files:
                    if os.path.exists(bak_file):
                        try: os.remove(bak_file)
                        except Exception: pass
            except Exception as e:
                import traceback
                import os
                tlog.error(f"❌ [异步出版] 流水线溃决: {str(e)}\n{traceback.format_exc()}")
                # 🚀 发生异常时，自动回滚恢复原快照，避免物理 missing 死锁
                for orig_file, bak_file in cleaned_bak_files:
                    if os.path.exists(bak_file) and not os.path.exists(orig_file):
                        try:
                            os.replace(bak_file, orig_file)
                            tlog.info(f"🛡️ [灾难自愈] 自动还原崩溃前快照: {orig_file}")
                        except Exception: pass
                from core.logic.notification_hub import send_sync_lifecycle_notification
                send_sync_lifecycle_notification(engine, "FAIL", "异步出版流水线异常崩溃", str(e))
            finally:
                _is_publishing = False
                # 🚀 [V78.6] 安全兜底：流水线跑完后，强制唤醒可能被挂起的监控狗
                if hasattr(engine, 'is_watchdog_suspended') and engine.is_watchdog_suspended:
                    engine.is_watchdog_suspended = False
                    tlog.info("🐕 [后台闭环] 已强行唤醒处于休眠状态的监控狗。")

                # 🚀 自动消费排队队列中的下一个翻译任务
                if _pending_sync_queue:
                    next_item = _pending_sync_queue.pop(0)
                    tlog.info(f"🔄 [排队自动接力] 正在为排队任务启动点火: {next_item['requested_paths']} / {next_item['target_langs']}")
                    start_asynchronous_sync(
                        engine,
                        dry_run=next_item.get('dry_run', False),
                        force=next_item.get('force', False),
                        sandbox=next_item.get('sandbox', False),
                        requested_paths=next_item.get('requested_paths'),
                        target_langs=next_item.get('target_langs'),
                        clear_cache=next_item.get('clear_cache', False)
                    )

    # 3. 提交至全局执行器 (优先级设为 CRITICAL 以确保立即响应)
    # 🚀 [V10.3] 线程隔离优化：启动专用的协调器线程运行后台任务，避免占用全局执行池而引发嵌套提交死锁及救援警告
    t = threading.Thread(target=_background_job, name="SyncCoordinatorThread", daemon=True)
    t.start()
    return id(t)

