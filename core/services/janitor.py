#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Janitor Engine (GC & Cleanup)
模块职责：清道夫中枢。
🛡️ [AEL-Iter-v5.3]：基于分层架构的 TDR 复健版本。
"""

import os
import logging
from .janitor_routes import RouteJanitor

logger = logging.getLogger("Illacme.plenipes")

class JanitorService:
    def __init__(self, global_lock, processing_locks, paths, meta_manager, route_manager, i18n_cfg, sys_cfg=None, active_theme='starlight'):
        self._global_engine_lock = global_lock
        self._processing_locks = processing_locks
        self.paths = paths
        self.meta = meta_manager
        self.route_manager = route_manager
        self.i18n = i18n_cfg
        self.sys_cfg = sys_cfg
        self.active_theme = active_theme
        self.fresh_paths = set()
        self.amnesty_paths = set()
        
        # 🚀 [TDR-Iter-021] 挂载子模块
        self.routes = RouteJanitor(self)

    def mark_as_fresh(self, path):
        norm_path = os.path.realpath(path).lower()
        self.fresh_paths.add(norm_path)
        self.amnesty_paths.add(norm_path)

    def _gc_empty_directories(self, target_dir, is_dry_run=False):
        if not os.path.exists(target_dir): return
        for root, dirs, files in os.walk(target_dir, topdown=False):
            for d in dirs:
                dir_path = os.path.join(root, d)
                try:
                    if not os.listdir(dir_path):
                        if getattr(self.meta, 'is_watch_mode', False): continue
                        if is_dry_run: logger.info(f"    [Dry-Run] 拟删除空目录: {dir_path}")
                        else: os.rmdir(dir_path)
                except Exception: pass

    def gc_assets(self, current_source_files=None, is_dry_run=False):
        in_flight = any(l.locked() for l in self._processing_locks.values())
        if in_flight: return

        with self._global_engine_lock:
            logger.info("🧹 启动前端资产目录“大扫除”...")
            active_assets = set()
            docs = self.meta.get_documents_snapshot()
            
            if current_source_files is None and len(docs) > 0: return
            
            for doc in docs.values():
                assets = doc.get("assets", [])
                if isinstance(assets, list):
                    for a in assets:
                        if not str(a).startswith(('http://', 'https://', 'ftp://', 'data:', '//')):
                            active_assets.add(a)
            
            assets_path = self.paths.get('assets')
            if not assets_path or not os.path.exists(assets_path): return

            for root, _, files in os.walk(assets_path):
                for f in files:
                    if f.startswith('.'): continue
                    f_abs = os.path.join(root, f)
                    f_rel = os.path.relpath(f_abs, assets_path).replace('\\', '/')
                    if f_rel not in active_assets:
                        if is_dry_run: logger.info(f"    [模拟清理] 孤儿资产: {f_rel}")
                        else:
                            try: os.remove(f_abs)
                            except Exception: pass

            self._gc_empty_directories(assets_path, is_dry_run)

    def gc_node(self, *args, **kwargs): return self.routes.gc_node(*args, **kwargs)
    def fast_tombstone(self, *args, **kwargs): return self.routes.fast_tombstone(*args, **kwargs)
    def physical_handover(self, *args, **kwargs): return self.routes.physical_handover(*args, **kwargs)
    def gc_ghost_nodes(self, *args, **kwargs): return self.routes.gc_ghost_nodes(*args, **kwargs)

    def gc_orphans(self, current_source_files, is_dry_run=False):
        docs_snapshot = self.meta.get_documents_snapshot()
        to_delete = [p for p in list(docs_snapshot.keys()) if p not in current_source_files]
        for rel_path in to_delete:
            self.gc_node(rel_path, docs_snapshot[rel_path].get("prefix", ""), docs_snapshot[rel_path].get("source", ""), is_dry_run)
        
        self.gc_tombstones(is_dry_run)
        self.gc_assets(current_source_files, is_dry_run)

    def gc_tombstones(self, is_dry_run=False):
        scan_root = os.path.abspath(self.paths.get('target_base', '.'))
        if not os.path.exists(scan_root): return
        for root, _, files in os.walk(scan_root):
            for f in files:
                if f.endswith(".tombstone"):
                    if is_dry_run: continue
                    try:
                        if getattr(self.meta, 'is_watch_mode', False): continue
                        os.remove(os.path.join(root, f))
                    except: pass