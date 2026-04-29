#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Route Janitor Service
模块职责：负责失效路由的物理回收、幽灵节点清理以及文章搬家时的物理原子迁移。
🛡️ [AEL-Iter-v5.3]：基于 TDR 复健的解耦服务组件。
"""
import os
import logging

from core.utils.tracing import tlog

class RouteJanitor:
    """🚀 [TDR-Iter-021] 路由清道夫：专注处理文章、路由及墓碑的物理回收"""

    def __init__(self, service):
        self.service = service
        self.paths = service.paths
        self.meta = service.meta
        self.route_manager = service.route_manager
        self.i18n = service.i18n

    def gc_node(self, rel_path, route_prefix, route_source, is_dry_run=False):
        """精准拔除单篇失效文章及其各语种路由"""
        doc_info = self.meta.get_doc_info(rel_path)
        slug = doc_info.get("slug")
        prefix = doc_info.get("prefix", route_prefix)
        source = doc_info.get("source", route_source)

        if slug:
            t_abs = os.path.join(self.paths.get('vault', '.'), rel_path)
            t_src_abs = os.path.join(self.paths.get('vault', '.'), source)
            t_sub_rel = os.path.relpath(t_abs, t_src_abs).replace('\\', '/')
            t_sub_dir = os.path.dirname(t_sub_rel).replace('\\', '/')
            if t_sub_dir == '.': t_sub_dir = ""

            mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run, allow_ai=False)
            ext = os.path.splitext(rel_path)[1].lower()

            langs = [self.i18n.source.lang_code] if self.i18n.source.lang_code else []
            if self.i18n.enable_multilingual:
                langs.extend([t.lang_code for t in self.i18n.targets if t.lang_code])

            for code in langs:
                dest = self.route_manager.resolve_physical_path(self.paths.get('target_base'), code, prefix, mapped_sub_dir, slug, ext)
                if os.path.exists(dest):
                    dest_norm = os.path.realpath(dest).lower()
                    if dest_norm in self.service.amnesty_paths:
                        continue

                    if is_dry_run:
                        tlog.info(f"    [模拟回收] 拟删除文件: {dest}")
                    else:
                        try:
                            if getattr(self.meta, 'is_watch_mode', False): continue
                            os.remove(dest)
                        except Exception as e: tlog.error(f"回收失败 {dest}: {e}")

        if not is_dry_run: self.meta.remove_document(rel_path)

    def fast_tombstone(self, rel_path, route_prefix, route_source):
        """原子墓碑化与错峰删除"""
        doc_info = self.meta.get_doc_info(rel_path)
        slug = doc_info.get("slug")
        if not slug: return

        prefix = doc_info.get("prefix", route_prefix)
        source = doc_info.get("source", route_source)
        ext = os.path.splitext(rel_path)[1].lower()

        langs = [self.i18n.source.lang_code]
        if self.i18n.enabled:
            langs.extend([t.lang_code for t in self.i18n.targets if t.lang_code])

        for code in langs:
            t_abs = os.path.join(self.paths.get('vault', '.'), rel_path)
            t_src_abs = os.path.join(self.paths.get('vault', '.'), source)
            try:
                t_sub_rel = os.path.relpath(t_abs, t_src_abs).replace('\\', '/')
                t_sub_dir = os.path.dirname(t_sub_rel).replace('\\', '/')
                if t_sub_dir == '.': t_sub_dir = ""
                mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, allow_ai=False)

                dest = self.route_manager.resolve_physical_path(self.paths.get('target_base'), code, prefix, mapped_sub_dir, slug, ext)
                if os.path.exists(dest):
                    dest_norm = os.path.realpath(dest).lower()
                    if dest_norm in self.service.fresh_paths: continue
                    try:
                        os.remove(dest)
                        tlog.debug(f"🧹 [错峰删除] 已清理老路径: {os.path.basename(dest)}")
                    except Exception: pass
            except Exception: pass

    def physical_handover(self, old_rel, new_rel, prefix_old, source_old, prefix_new, source_new):
        """物理原子迁移协议"""
        try:
            doc_info = self.meta.get_doc_info(old_rel)
            if not doc_info or not doc_info.get('slug'): return

            old_slug = doc_info['slug']
            new_slug = old_slug
            ext = os.path.splitext(old_rel)[1]

            langs = [self.i18n.source.lang_code]
            if self.i18n.enable_multilingual:
                langs.extend([t.lang_code for t in self.i18n.targets if t.lang_code])

            for lang in set(langs):
                sub_old = os.path.dirname(os.path.relpath(os.path.join(self.paths.get('vault', '.'), old_rel), os.path.join(self.paths.get('vault', '.'), source_old))).replace('\\', '/')
                if sub_old == '.': sub_old = ""
                mapped_sub_old = self.route_manager.get_mapped_sub_dir(sub_old, allow_ai=False)

                sub_new = os.path.dirname(os.path.relpath(os.path.join(self.paths.get('vault', '.'), new_rel), os.path.join(self.paths.get('vault', '.'), source_new))).replace('\\', '/')
                if sub_new == '.': sub_new = ""
                mapped_sub_new = self.route_manager.get_mapped_sub_dir(sub_new, allow_ai=False)

                for base_dir_key in ['shadow', 'target_base']:
                    base_root = self.paths.get(base_dir_key)
                    if not base_root: continue

                    old_p = self.route_manager.resolve_physical_path(base_root, lang, prefix_old, mapped_sub_old, old_slug, ext)
                    new_p = self.route_manager.resolve_physical_path(base_root, lang, prefix_new, mapped_sub_new, new_slug, ext)

                    if os.path.exists(old_p):
                        try:
                            os.makedirs(os.path.dirname(new_p), exist_ok=True)
                            os.replace(old_p, new_p)
                            self.service.mark_as_fresh(new_p)
                        except Exception: pass
        except Exception as e:
            tlog.error(f"🛑 [原子迁移协议崩溃]: {e}")

    def gc_ghost_nodes(self, is_dry_run=False):
        """幽灵路由清道夫 - 优化版：显著降低 I/O 压力，解决网络挂载盘下的遍历挂起问题"""
        with self.service._global_engine_lock:
            tlog.debug("🧹 启动“幽灵清洗” (gc_ghost_nodes)...")

            # 1. 清理元数据中不存在于物理世界的节点
            current_docs = self.meta.get_documents_snapshot()
            vault_root = self.paths.get('vault', '.')
            for rel_path in list(current_docs.keys()):
                if not os.path.exists(os.path.join(vault_root, rel_path)):
                    if not is_dry_run: self.meta.remove_document(rel_path)

            # 2. 收集当前合法的所有物理路径 (Normalized)
            valid_dest_paths = set()
            docs = self.meta.get_documents_snapshot()

            langs = [self.i18n.source.lang_code] if self.i18n.source.lang_code else []
            if self.i18n.enable_multilingual:
                langs.extend([t.lang_code for t in self.i18n.targets if t.lang_code])

            target_base = self.paths.get('target_base', '.')
            # 🚀 [V34.9] 预先归一化，减少循环内系统调用
            tlog.info("🧹 [清道夫] 正在收集合法物理路径...")
            target_base_abs = os.path.realpath(target_base).lower()

            for rel_path, doc in docs.items():
                slug = doc.get("slug")
                if not slug: continue
                prefix = doc.get("prefix", "")
                source = doc.get("source", "")
                ext = os.path.splitext(rel_path)[1].lower()

                t_abs = os.path.join(vault_root, rel_path)
                t_src_abs = os.path.join(vault_root, source)
                try:
                    t_sub_rel = os.path.relpath(t_abs, t_src_abs).replace('\\', '/')
                    t_sub_dir = os.path.dirname(t_sub_rel).replace('\\', '/')
                    if t_sub_dir == '.': t_sub_dir = ""
                    mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, allow_ai=False)

                    for code in langs:
                        dest = self.route_manager.resolve_physical_path(target_base, code, prefix, mapped_sub_dir, slug, ext)
                        valid_dest_paths.add(os.path.abspath(dest).lower())
                except Exception: continue

            tlog.info(f"🧹 [清道夫] 已识别 {len(valid_dest_paths)} 个合法路径。正在遍历物理磁盘...")

            # 3. 递归清洗物理世界的幽灵路由
            scan_root = os.path.abspath(target_base)
            if not os.path.exists(scan_root): return

            janitor_opts = self.service.sys_cfg.janitor_settings
            all_exclude = set(janitor_opts.global_exclude + janitor_opts.theme_exclude.get(self.service.active_theme, []))

            # 🚀 [V34.9] 预先处理豁免路径
            fresh_paths_norm = {os.path.abspath(p).lower() for p in self.service.fresh_paths}

            deleted_count = 0
            for root, dirs, files in os.walk(scan_root):
                # 剪枝：跳过隐藏目录与排除目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in all_exclude]
                if root == scan_root: continue

                for f in files:
                    # 仅回收 Markdown 类型路由，不触动静态资产
                    if f.endswith(('.md', '.mdx')):
                        f_abs = os.path.abspath(os.path.join(root, f)).lower()
                        if f_abs not in valid_dest_paths and f_abs not in fresh_paths_norm:
                            if is_dry_run:
                                tlog.info(f"    [模拟清洗] 拟删除幽灵路由: {f_abs}")
                            else:
                                try:
                                    if getattr(self.meta, 'is_watch_mode', False): continue
                                    os.remove(f_abs)
                                    deleted_count += 1
                                except Exception: pass

            if deleted_count > 0: tlog.debug(f"✨ 幽灵清洗完成，斩断了 {deleted_count} 个野路由。")
