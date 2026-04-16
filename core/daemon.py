#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Watchdog Daemon
模块职责：目录监控与防抖事件总线。
利用 FileSystemObserver 提供毫秒级的 FS 事件拦截，通过防抖延迟锁防止重复派发。
"""

import os
import time
import threading
import traceback
import logging
from concurrent.futures import ThreadPoolExecutor
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

from .cli_bootstrap import send_notification
from .garden_exporter import export_digital_garden

logger = logging.getLogger("Illacme.plenipes")

def start_watchdog(engine, args, current_source_files):
    """启动看门狗实时热更探针 (Daemon 模式)"""
    if not HAS_WATCHDOG:
        logger.error("🛑 无法启动守护进程：缺少 watchdog 依赖。请执行 pip install watchdog")
        return None, None

    logger.info(f"👀 目录监控已开启 -> 正在实时保护并监听文件夹: {engine.vault_root}")
    
    watch_pool = ThreadPoolExecutor(max_workers=engine.max_workers)
    
    class ChangeHandler(FileSystemEventHandler):
        def __init__(self):
            super().__init__()
            self._timers = {}
            self._lock = threading.Lock()
            self.debounce_delay = float(engine.sys_cfg.get('typing_idle_threshold', 5.0))
            logger.info(f"🛡️ 智能防抖引擎已挂载 | 当前静默拦截阈值: {self.debounce_delay} 秒")

        def _find_route_info_for_path(self, abs_path):
            norm_abs = os.path.normcase(os.path.abspath(abs_path))
            sorted_matrix = sorted(engine.route_matrix, key=lambda x: len(x.get('source', '')), reverse=True)
            
            for route_cfg in sorted_matrix:
                src = route_cfg.get('source', '')
                route_abs = os.path.normcase(os.path.abspath(os.path.join(engine.vault_root, src)))
                route_dir = route_abs if route_abs.endswith(os.sep) else route_abs + os.sep
                
                if norm_abs.startswith(route_dir):
                    return route_cfg.get('prefix', ''), src
            return None, None

        def _debounced_submit(self, file_path, prefix, source):
            with self._lock:
                if file_path in self._timers:
                    self._timers[file_path].cancel()
                def task_wrapper():
                    try:
                        watch_pool.submit(self._dispatch_task, file_path, prefix, source)
                    finally:
                        with self._lock:
                            if file_path in self._timers:
                                del self._timers[file_path]
                timer = threading.Timer(self.debounce_delay, task_wrapper)
                self._timers[file_path] = timer
                timer.start()

        def _dispatch_task(self, file_path, prefix, source):
            try:
                engine.sync_document(file_path, prefix, source, is_dry_run=args.dry_run, force_sync=args.force)
                if not args.dry_run: 
                    engine.meta.save() 
                    export_digital_garden(engine)
                    fname = os.path.basename(file_path)
                    send_notification("✨ 文章已更新", f"《{fname}》已完成 AI 同步并上线")
            except Exception as e:
                logger.error(f"⚠️ 实时同步过程发生意外崩溃: {traceback.format_exc()}")

        def _add_asset(self, abs_path):
            fname = os.path.basename(abs_path)
            if fname not in engine.asset_index:
                engine.asset_index[fname] = []
            if abs_path not in engine.asset_index[fname]:
                engine.asset_index[fname].append(abs_path)

        def _remove_asset(self, abs_path):
            fname = os.path.basename(abs_path)
            if fname in engine.asset_index and abs_path in engine.asset_index[fname]:
                engine.asset_index[fname].remove(abs_path)
                if not engine.asset_index[fname]: 
                    del engine.asset_index[fname]

        def on_created(self, event):
            if not event.is_directory:
                if event.src_path.endswith((".md", ".mdx")):
                    rel_path = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                    current_source_files.add(rel_path)
                    prefix, source = self._find_route_info_for_path(event.src_path)
                    if prefix is not None and source is not None:
                        self._debounced_submit(event.src_path, prefix, source)
                else:
                    self._add_asset(event.src_path)

        def on_modified(self, event):
            if not event.is_directory and event.src_path.endswith((".md", ".mdx")):
                rel_path = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                current_source_files.add(rel_path) 
                prefix, source = self._find_route_info_for_path(event.src_path)
                if prefix is not None and source is not None:
                    self._debounced_submit(event.src_path, prefix, source)

        def on_deleted(self, event):
            if event.is_directory:
                rel_dir = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                to_remove = [f for f in current_source_files if f.startswith(rel_dir + '/')]
                for f in to_remove:
                    current_source_files.discard(f)
                    with self._lock:
                        abs_f = os.path.join(engine.vault_root, f)
                        if abs_f in self._timers:
                            self._timers[abs_f].cancel()
                            del self._timers[abs_f]
                
                if to_remove:
                    logger.info(f"📂 检测到批量目录移除 ({rel_dir})，正在激活级联回收泵...")
                    if engine.sys_cfg.get('enable_asset_audit', True):
                        engine.janitor.gc_orphans(current_source_files, is_dry_run=args.dry_run)
                    if not args.dry_run: 
                        engine.meta.save()
                        export_digital_garden(engine)
                return

            if not event.is_directory:
                if event.src_path.endswith((".md", ".mdx")):
                    rel_path = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                    current_source_files.discard(rel_path)
                    with self._lock:
                        if event.src_path in self._timers:
                            self._timers[event.src_path].cancel()
                            del self._timers[event.src_path]
                    if engine.sys_cfg.get('enable_asset_audit', True):
                        engine.janitor.gc_orphans(current_source_files, is_dry_run=args.dry_run)
                    if not args.dry_run: 
                        engine.meta.save()
                        export_digital_garden(engine)
                else:
                    self._remove_asset(event.src_path)

        def on_moved(self, event):
            if event.is_directory:
                old_rel_dir = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                to_remove = [f for f in current_source_files if f.startswith(old_rel_dir + '/')]
                for f in to_remove:
                    current_source_files.discard(f)
                    with self._lock:
                        abs_f = os.path.join(engine.vault_root, f)
                        if abs_f in self._timers:
                            self._timers[abs_f].cancel()
                            del self._timers[abs_f]
                            
                if hasattr(event, 'dest_path'):
                    for root, _, files in os.walk(event.dest_path):
                        for f in files:
                            if f.endswith(('.md', '.mdx')):
                                abs_new = os.path.join(root, f)
                                new_rel = os.path.relpath(abs_new, engine.vault_root).replace('\\', '/')
                                current_source_files.add(new_rel)
                                prefix, source = self._find_route_info_for_path(abs_new)
                                if prefix is not None and source is not None:
                                    self._debounced_submit(abs_new, prefix, source)
                                    
                if to_remove:
                    logger.info(f"📂 检测到目录重命名/移动 ({old_rel_dir})，正在激活级联路由更替...")
                    if engine.sys_cfg.get('enable_asset_audit', True):
                        engine.janitor.gc_orphans(current_source_files, is_dry_run=args.dry_run)
                    if not args.dry_run: 
                        engine.meta.save()
                        export_digital_garden(engine)
                return

            if event.src_path.endswith((".md", ".mdx")):
                old_rel = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                current_source_files.discard(old_rel)
                with self._lock:
                    if event.src_path in self._timers:
                        self._timers[event.src_path].cancel()
                        del self._timers[event.src_path]
                if engine.sys_cfg.get('enable_asset_audit', True):
                    engine.janitor.gc_orphans(current_source_files, is_dry_run=args.dry_run)
            else:
                self._remove_asset(event.src_path) 
            
            if hasattr(event, 'dest_path'):
                if event.dest_path.endswith((".md", ".mdx")):
                    new_rel = os.path.relpath(event.dest_path, engine.vault_root).replace('\\', '/')
                    current_source_files.add(new_rel)
                    prefix, source = self._find_route_info_for_path(event.dest_path)
                    if prefix is not None and source is not None:
                        self._debounced_submit(event.dest_path, prefix, source)
                else:
                    self._add_asset(event.dest_path)
            
            if not args.dry_run: 
                engine.meta.save()
                export_digital_garden(engine)
                    
    observer = Observer()
    observer.schedule(ChangeHandler(), engine.vault_root, recursive=True)
    observer.start()
    
    return observer, watch_pool