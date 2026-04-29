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

from core.utils.tracing import tlog

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
                        if is_dry_run: tlog.info(f"    [Dry-Run] 拟删除空目录: {dir_path}")
                        else: os.rmdir(dir_path)
                except Exception: pass

    def gc_assets(self, current_source_files=None, is_dry_run=False):
        in_flight = any(l.locked() for l in self._processing_locks.values())
        if in_flight: return

        with self._global_engine_lock:
            tlog.debug("🧹 启动前端资产目录“大扫除”...")
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

                    # 🚀 [V11.7] 主权资产特赦：豁免主题静态资源与引擎索引文件，防止 Janitor 误删
                    amnesty_prefixes = ('css/', 'js/', 'fonts/', 'img/', 'static/')
                    protected_files = ['favicon.png', 'favicon.ico', 'search_index.json']

                    # 允许带主题后缀的索引文件 (如 link_graph_default.json)
                    is_index_file = any(p in f for p in ['search_index', 'link_graph'])

                    if f_rel.startswith(amnesty_prefixes) or f in protected_files or is_index_file:
                        continue

                    if f_rel not in active_assets:
                        if is_dry_run: tlog.info(f"    [模拟清理] 孤儿资产: {f_rel}")
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
        if to_delete:
            tlog.info(f"🧹 [清道夫] 发现 {len(to_delete)} 篇孤儿文档，正在清理...")
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
    def sync_shadow_languages(self, is_dry_run=False):
        """🚀 [V10.5] 影子语种同步：确保多语种资产的物理一致性"""
        tlog.info("🧹 [清道夫] 正在验证影子语种资产的物理一致性...")
        docs = self.meta.get_documents_snapshot()
        missing_count = 0

        target_base = self.paths.get('target_base')
        if not target_base: return

        for rel_path, info in docs.items():
            translations = info.get('translations', {})
            for lang, t_info in translations.items():
                if not t_info: continue

                # 推导物理路径
                ext = os.path.splitext(rel_path)[1].lower()
                prefix = info.get('route_prefix', '')
                sub = info.get('sub_dir', '')
                slug = info.get('slug', '')
                source_type = info.get('route_source', 'docs')

                # 🚀 [V11.7] HTML 语种感知对齐
                if self.active_theme == 'default':
                    target_ext = '.html'
                else:
                    target_ext = ext

                dest = self.route_manager.resolve_physical_path(target_base, lang, prefix, sub, slug, target_ext, source_type=source_type)

                if not os.path.exists(dest):
                    tlog.warning(f"⚠️ [影子缺失] 文档 {rel_path} 的 {lang} 版本在物理磁盘上意外失踪: {dest}")
                    missing_count += 1

        if missing_count == 0:
            tlog.info("✨ [清道夫] 影子语种对齐校验通过，物理资产完整。")
        else:
            tlog.warning(f"🚨 [清道夫] 发现 {missing_count} 处影子语种资产缺失，建议执行 --force 全量同步以强制复原。")
