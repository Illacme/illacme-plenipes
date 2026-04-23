#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Daemon Event Handler
模块职责：负责 Watchdog 事件的异步捕获、冲突消减与同步工序调度。
🛡️ [AEL-Iter-v5.3]：基于 TDR 复健的解耦服务组件。
"""
import os
import threading
import traceback
import logging
from core.cli_bootstrap import send_notification
from core.garden_exporter import export_digital_garden

try:
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

logger = logging.getLogger("Illacme.plenipes")

class ChangeHandler(FileSystemEventHandler):
    """🚀 [TDR-Iter-021] 守护进程事件处理器：专注 FS 拦截、防抖与分发"""
    
    def __init__(self, engine, args, current_source_files, watch_pool):
        super().__init__()
        self.engine = engine
        self.args = args
        self.current_source_files = current_source_files
        self.watch_pool = watch_pool
        self._timers = {}
        self._lock = threading.Lock()
        
        watch_cfg = engine.config.system.watchdog_settings
        self._gc_timer = None
        self._heavy_timer = None
        self.exclude_dirs = set(watch_cfg.exclude_dirs)
        self.exclude_patterns = set(watch_cfg.exclude_patterns)
        self.debounce_delay = engine.config.system.typing_idle_threshold
        self.heavy_task_delay = watch_cfg.heavy_task_delay
        self.gc_delay = watch_cfg.gc_delay
        self.handover_delay = watch_cfg.handover_delay

    def _should_skip(self, path):
        abs_path = os.path.normcase(os.path.realpath(path))
        parts = abs_path.replace('\\', '/').split('/')
        if any(eb in parts for eb in self.exclude_dirs): return True
        
        silent_zones = [
            self.engine.paths.get('shadow'),
            self.engine.paths.get('target_base'),
            os.path.dirname(self.engine.paths.get('ledger_cache', ''))
        ]
        for zone in silent_zones:
            if zone and abs_path.startswith(os.path.normcase(os.path.realpath(zone))): return True
        
        fname = os.path.basename(path)
        if any(fname.endswith(p) for p in self.exclude_patterns): return True
        return fname.startswith(('~$', 'tmp_'))

    def _find_route_info(self, abs_path):
        norm_abs = os.path.normcase(os.path.realpath(abs_path))
        sorted_matrix = sorted(self.engine.route_matrix, key=lambda x: len(x.get('source', '')), reverse=True)
        for route in sorted_matrix:
            src = route.get('source', '')
            route_abs = os.path.normcase(os.path.realpath(os.path.join(self.engine.vault_root, src)))
            route_dir = route_abs if route_abs.endswith(os.sep) else route_abs + os.sep
            if norm_abs.startswith(route_dir): return route.get('prefix', ''), src
        return None, None

    def _debounced_submit(self, file_path, prefix, source, delay=None):
        with self._lock:
            if file_path in self._timers: self._timers[file_path].cancel()
            def task_wrapper():
                try: self.watch_pool.submit(self._dispatch_task, file_path, prefix, source)
                finally:
                    with self._lock:
                        if file_path in self._timers: del self._timers[file_path]
            timer = threading.Timer(delay or self.debounce_delay, task_wrapper)
            self._timers[file_path] = timer
            timer.start()

    def _dispatch_task(self, file_path, prefix, source):
        try:
            self.engine.sync_document(file_path, prefix, source, is_dry_run=self.args.dry_run, force_sync=self.args.force)
            if not self.args.dry_run:
                self._lazy_gc_trigger()
                self._debounced_heavy_tasks()
                send_notification("✨ 文章已更新", f"《{os.path.basename(file_path)}》已上线")
        except Exception:
            logger.error(f"⚠️ 实时同步意外崩溃: {traceback.format_exc()}")

    def _lazy_gc_trigger(self):
        with self._lock:
            if self._gc_timer: self._gc_timer.cancel()
            def run_gc():
                if self.engine.config.system.enable_asset_audit:
                    self.engine.janitor.gc_orphans(self.current_source_files, is_dry_run=self.args.dry_run)
                    if not self.args.dry_run: self.engine.meta.save()
            self._gc_timer = threading.Timer(self.gc_delay, run_gc)
            self._gc_timer.start()

    def _debounced_heavy_tasks(self):
        with self._lock:
            if self._heavy_timer: self._heavy_timer.cancel()
            def task():
                try:
                    self.engine.sentinel.run_health_check(auto_fix=True)
                    self.engine.meta.save()
                    export_digital_garden(self.engine)
                except Exception as e: logger.error(f"🛑 [重型延迟任务失败]: {e}")
            self._heavy_timer = threading.Timer(self.heavy_task_delay, task)
            self._heavy_timer.start()

    def on_created(self, event):
        if event.is_directory or self._should_skip(event.src_path): return
        if event.src_path.lower().endswith((".md", ".mdx")):
            rel_path = os.path.relpath(event.src_path, self.engine.vault_root).replace('\\', '/')
            self.engine.timeline.log_event("CREATED", rel_path, "PENDING", "探测到物理新增")
            self.current_source_files.add(rel_path)
            prefix, source = self._find_route_info(event.src_path)
            if prefix is not None: self._debounced_submit(event.src_path, prefix, source)

    def on_modified(self, event):
        if event.is_directory or self._should_skip(event.src_path): return
        if event.src_path.lower().endswith((".md", ".mdx")):
            rel_path = os.path.relpath(event.src_path, self.engine.vault_root).replace('\\', '/')
            self.engine.timeline.log_event("MODIFIED", rel_path, "PENDING", "探测到物理内容变化")
            self.current_source_files.add(rel_path) 
            prefix, source = self._find_route_info(event.src_path)
            if prefix is not None: self._debounced_submit(event.src_path, prefix, source)

    def on_deleted(self, event):
        if self._should_skip(event.src_path): return
        if event.is_directory:
            rel_dir = os.path.relpath(event.src_path, self.engine.vault_root).replace('\\', '/')
            to_remove = [f for f in self.current_source_files if f.startswith(rel_dir + '/')]
            for f in to_remove: self.current_source_files.discard(f)
            if to_remove: self._lazy_gc_trigger()
            return
        if event.src_path.lower().endswith((".md", ".mdx")):
            rel_path = os.path.relpath(event.src_path, self.engine.vault_root).replace('\\', '/')
            self.engine.timeline.log_event("DELETED", rel_path, "REMOVED", "探测到物理下线")
            self.current_source_files.discard(rel_path)
            self._lazy_gc_trigger()
            self._debounced_heavy_tasks()

    def on_moved(self, event):
        if os.path.realpath(event.src_path) == os.path.realpath(event.dest_path):
            if not event.is_directory:
                prefix, source = self._find_route_info(event.dest_path)
                if prefix: self._debounced_submit(event.dest_path, prefix, source, delay=0.1)
            return
        if self._should_skip(event.src_path) and self._should_skip(event.dest_path): return
        
        if event.is_directory:
            old_rel = os.path.relpath(event.src_path, self.engine.vault_root).replace('\\', '/')
            to_remove = [f for f in self.current_source_files if f.startswith(old_rel + '/')]
            for f in to_remove: self.current_source_files.discard(f)
            self._lazy_gc_trigger()
            return

        if event.src_path.lower().endswith((".md", ".mdx")):
            old_rel = os.path.relpath(event.src_path, self.engine.vault_root).replace('\\', '/')
            self.engine.timeline.log_event("MOVED", old_rel, "MOVED", f"迁移轨迹触发")
            self.current_source_files.discard(old_rel)
            
            prefix_new, source_new = self._find_route_info(event.dest_path)
            if prefix_new is not None:
                new_rel = os.path.relpath(event.dest_path, self.engine.vault_root).replace('\\', '/')
                self.current_source_files.add(new_rel)
                self._debounced_submit(event.dest_path, prefix_new, source_new, delay=0.1)
                self._debounced_heavy_tasks()
