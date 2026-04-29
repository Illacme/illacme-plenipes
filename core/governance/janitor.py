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
    def __init__(self, global_lock=None, processing_locks=None, paths=None, meta_manager=None, route_manager=None, i18n_cfg=None, sys_cfg=None, active_theme='starlight', engine=None):
        if engine:
            self._global_engine_lock = getattr(engine, '_global_engine_lock', None)
            self._processing_locks = getattr(engine, '_processing_locks', None)
            self.paths = getattr(engine, 'paths', None)
            self.meta = getattr(engine, 'meta', None)
            self.route_manager = getattr(engine, 'route_manager', None)
            self.i18n = getattr(engine, 'i18n', None)
            self.sys_cfg = getattr(engine, 'config', None)
            if self.sys_cfg and hasattr(self.sys_cfg, 'system'): self.sys_cfg = self.sys_cfg.system
            self.active_theme = getattr(engine, 'active_theme', 'starlight')
        else:
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
        
        import threading
        self.lock = threading.Lock()

        # 🚀 [TDR-Iter-021] 挂载子模块
        self.routes = RouteJanitor(self)

    def mark_as_fresh(self, abs_path: str):
        """🚀 [V35.2] 物理主权声明：显式标记一个物理文件为新鲜资产（最高权重）"""
        with self.lock:
            # 统一转换为规范的小写路径，杜绝大小写敏感导致的误删
            norm_path = os.path.realpath(abs_path).lower()
            self.fresh_paths.add(norm_path)
            # tlog.debug(f"🛡️ [主权记忆] 已物理锁定新鲜路径: {os.path.basename(norm_path)}")

    def mark_doc_as_fresh(self, rel_path: str):
        """
        🚀 [V35.2] 文档主权记忆：根据文档相对路径推导所有语种的物理输出路径并豁免。
        解决了冷启动或增量同步下，未更新文档被误删的问题。
        """
        doc_info = self.meta.get_doc_info(rel_path)
        if not doc_info:
            # 🚀 [V35.2] 降级逻辑：如果在数据库中查不到，说明可能是全新文档或数据库被清理
            # 此时无法推导全语种路径，需依赖策略层显式调用 mark_as_fresh。
            return

        slug = doc_info.get("slug")
        prefix = doc_info.get("route_prefix") or ""
        sub = doc_info.get("sub_dir") or ""
        
        # 遍历所有已知的语种目标
        source_code = self.i18n.source.lang_code
        all_langs = [source_code] + [t.lang_code for t in self.i18n.targets if t.lang_code]
        
        for lang in all_langs:
            # 🚀 [V35.2] 物理全量推导：覆盖 source (Markdown) 与 static (渲染产物)
            for mode in ["source", "static"]:
                root = self.paths.get('static_dir') if mode == 'static' else self.paths.get('source_dir')
                if not root: continue
                
                # 推导扩展名：优先使用适配器契约，若无则保留原始后缀
                target_ext = self.route_manager.ssg_adapter.output_extensions.get(mode)
                if not target_ext:
                    target_ext = os.path.splitext(rel_path)[1].lower()
                
                try:
                    dest = self.route_manager.resolve_physical_path(
                        root, lang, prefix, sub, slug, target_ext,
                        source_type=doc_info.get("route_source", "docs")
                    )
                    self.mark_as_fresh(dest)
                except Exception:
                    continue



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

    def purge_dist(self, is_dry_run=False):
        """🚀 [V35.2] 物理自愈清理：强力粉碎 dist 目录中过时的影子资产"""
        target_root = self.paths.get('static_dir') or self.paths.get('target_base')
        if not target_root or not os.path.exists(target_root):
            return

        tlog.info(f"🧹 [物理自愈] 正在扫描并净化分发疆域: {target_root}")
        
        removed_count = 0
        for root, _, files in os.walk(target_root):
            for f in files:
                # 保护隐藏文件与系统文件
                if f.startswith('.'): continue
                
                f_abs = os.path.join(root, f)
                norm_path = os.path.realpath(f_abs).lower()
                
                # 🚀 [调试] 路径指纹比对 (提升至 INFO 等级)
                tlog.info(f"🔍 [物理自愈] 正在比对资产: {norm_path}")
                tlog.info(f"📊 [物理自愈] 当前新鲜资产池规模: {len(self.fresh_paths)}")
                
                # 🚀 [V35.2] 核心自愈逻辑：绝对路径精准指纹比对
                is_fresh = norm_path in self.fresh_paths

                
                # 特赦：主题静态资源 (由 SSG 适配器负责)
                is_amnesty = any(term in norm_path for term in ['/static/', '/assets/', 'favicon', 'search_index', 'link_graph'])
                
                if not is_fresh and not is_amnesty:
                    if is_dry_run:
                        tlog.info(f"    [模拟清理] 过时影子文件: {f_abs}")
                    else:
                        try:
                            tlog.warning(f"🛡️ [净化审计流水] 已抹除非法资产: {f_abs}")
                            os.remove(f_abs)
                            removed_count += 1
                        except Exception: pass

        
        if removed_count > 0:
            tlog.info(f"✨ [物理自愈] 已清理 {removed_count} 个过时资产。")
            self._gc_empty_directories(target_root, is_dry_run)
        else:
            tlog.info("✨ [物理自愈] 分发疆域已是洁净状态。")

