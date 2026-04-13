#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Janitor Engine (GC & Cleanup)
模块职责：幽灵清道夫与垃圾回收微内核。
接管所有的自底向上的物理资产清理、孤儿路由拔除与状态机自愈逻辑。
架构原则：严格依赖注入 (DI)，挂载全局并发锁，绝对免疫对正在生成中文件的误杀。
🚀 [V14.6 架构升级]：全面接入状态机快照引擎 (Snapshot)，物理切断数据争用 (Data Race)。
"""

import os
import logging

logger = logging.getLogger("Illacme.plenipes")

class JanitorService:
    """
    🚀 独立垃圾回收中枢
    在执行任何物理删除前，必须侦测全局引擎锁与处理中互斥锁，确保 I/O 安全。
    """
    def __init__(self, global_lock, processing_locks, paths, meta_manager, route_manager, i18n_cfg):
        self._global_engine_lock = global_lock
        self._processing_locks = processing_locks
        self.paths = paths
        self.meta = meta_manager
        self.route_manager = route_manager
        self.i18n = i18n_cfg

    def _gc_empty_directories(self, target_dir, is_dry_run=False):
        """🚀 幽灵空目录清道夫：自底向上抹除无用文件夹，提升前端编译极速性能"""
        if not os.path.exists(target_dir): return
        # 自底向上遍历，确保子目录删空后，父目录也能被正确判断为空并删除
        for root, dirs, files in os.walk(target_dir, topdown=False):
            for d in dirs:
                dir_path = os.path.join(root, d)
                try:
                    if not os.listdir(dir_path):
                        if is_dry_run:
                            logger.info(f"    [Dry-Run 模拟清理] 拟删除空目录: {dir_path}")
                        else:
                            os.rmdir(dir_path)
                            logger.info(f"    [空目录清理] 物理移除无用空目录: {dir_path}")
                except Exception as e:
                    pass

    def gc_assets(self, current_source_files=None, is_dry_run=False):
        """
        物理瘦身逻辑：带全局写保护屏障的物理资产清算器。
        🚀 V14.3 升级：彻底免疫 HTTP 远程图床链接的误杀。
        """
        in_flight = any(l.locked() for l in self._processing_locks.values())
        if in_flight:
            logger.warning("🚧 [GC 熔断] 检测到有文章正在处理中，为防止误删生成中的新生资产，已强行熔断本次物理清理泵。")
            return

        with self._global_engine_lock:
            logger.info("🧹 启动前端资产目录“大扫除” (gc_assets)...")
            active_assets = set()
            
            # 🚀 核心防线接管：通过深度拷贝的快照获取数据，免疫 RuntimeError
            docs = self.meta.get_documents_snapshot()
            total_docs = len(docs)
            
            if current_source_files is None and total_docs > 0:
                logger.warning("🚧 资产账本未接收到全量物理扫描基线，为了保护您的附件不被误删，已自动跳过本次清理。")
                return
            
            for doc in docs.values():
                assets = doc.get("assets", [])
                if isinstance(assets, list):
                    for a in assets:
                        # 🚀 终极过滤防线：即使历史脏数据导致 http 链接混入了本地资产账本，在此处也会被强行弹回，绝对不参与物理比对！
                        if not str(a).startswith(('http://', 'https://', 'ftp://', 'data:', '//')):
                            active_assets.add(a)
            
            if not os.path.exists(self.paths['assets']): return

            for root, _, files in os.walk(self.paths['assets']):
                for f in files:
                    if f.startswith('.'): continue
                    
                    f_abs = os.path.join(root, f)
                    f_rel = os.path.relpath(f_abs, self.paths['assets']).replace('\\', '/')
                    
                    if f_rel not in active_assets:
                        if is_dry_run:
                            logger.info(f"    [模拟清理] 发现孤儿本地资产: {f_rel}")
                        else:
                            try:
                                os.remove(f_abs)
                                logger.info(f"    [清理成功] 物理移除冗余本地资产: {f_rel}")
                            except Exception as e:
                                logger.error(f"    [清理失败] 无法删除文件 {f_rel}: {e}")

            self._gc_empty_directories(self.paths['assets'], is_dry_run)

    def gc_node(self, rel_path, route_prefix, route_source, is_dry_run=False):
        """精准拔除单篇失效文章及其各语种路由"""
        doc_info = self.meta.get_doc_info(rel_path)
        slug = doc_info.get("slug")
        prefix = doc_info.get("prefix", route_prefix)
        source = doc_info.get("source", route_source)
        
        if slug:
            t_abs = os.path.join(self.paths['vault'], rel_path)
            t_src_abs = os.path.join(self.paths['vault'], source)
            t_sub_rel = os.path.relpath(t_abs, t_src_abs).replace('\\', '/')
            t_sub_dir = os.path.dirname(t_sub_rel).replace('\\', '/')
            if t_sub_dir == '.': t_sub_dir = ""

            # 🚀 路由引擎调用对齐：禁止此处呼叫 AI，仅提取已有映射
            mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run, allow_ai=False)

            # 🚀 动态继承源文件的真实扩展名，确保精准歼灭
            ext = os.path.splitext(rel_path)[1].lower()

            # 🚀 [架构补丁]：同步总闸感知
            langs = []
            source_code = self.i18n.get('source', {}).get('code', "")
            langs.append(source_code)
            
            # 只有总闸开启时，才将目标语言路径纳入歼灭清单
            if self.i18n.get('enabled', True):
                for t in self.i18n.get('targets', []):
                    if t.get('code') is not None:
                        langs.append(t['code'])
                    
            for code in langs:
                dest = os.path.join(self.paths['target_base'], code, prefix, mapped_sub_dir, f"{slug}{ext}")
                if os.path.exists(dest):
                    if is_dry_run: 
                        logger.info(f"    [Dry-Run 模拟回收] 拟删除文章文件: {dest}")
                    else: 
                        try: os.remove(dest)
                        except Exception as e: logger.error(f"回收文章文件失败 {dest}: {e}")
                            
        if not is_dry_run: self.meta.remove_document(rel_path)

    def gc_orphans(self, current_source_files, is_dry_run=False):
        """级联孤儿回收泵"""
        # 🚀 核心防线接管：从防撕裂的快照中提取文章主键列表
        docs_snapshot = self.meta.get_documents_snapshot()
        to_delete = [p for p in list(docs_snapshot.keys()) if p not in current_source_files]
        for rel_path in to_delete:
            if not is_dry_run: logger.info(f"  └── [文件清理] 自动移除已删除的文章: {rel_path}")
            prefix = docs_snapshot[rel_path].get("prefix", "")
            source = docs_snapshot[rel_path].get("source", "")
            self.gc_node(rel_path, prefix, source, is_dry_run)
        
        # 🚀 [联动清理] 将全量基线 current_source_files 穿透传递，解锁物理大扫除
        self.gc_assets(current_source_files, is_dry_run)

    def gc_ghost_nodes(self, is_dry_run=False):
        """幽灵路由清道夫：支持 MDX 清洗与账本自愈"""
        in_flight = any(l.locked() for l in self._processing_locks.values())
        if in_flight:
            logger.warning("🚧 [路由清洗熔断] 检测到有文章正在生成中，为防止误删写入一半的新文章，已强行熔断本次路由清洗。")
            return

        with self._global_engine_lock:
            logger.info("🧹 启动前端路由目录“幽灵清洗” (gc_ghost_nodes)...")
            
            # 🚀 [V14.12 核心防线] 状态机账本自愈 (Ledger Pruning)
            # 🚀 核心防线接管：从防撕裂的快照中读取，免疫运行时崩溃
            current_docs = self.meta.get_documents_snapshot()
            orphans = []
            for rel_path in current_docs.keys():
                src_abs = os.path.join(self.paths['vault'], rel_path)
                if not os.path.exists(src_abs):
                    orphans.append(rel_path)
            
            for orphan in orphans:
                logger.info(f"🩹 [状态机自愈] 侦测到源文件已物理消失，正在剥离失效的账本记录: {orphan}")
                if not is_dry_run:
                    self.meta.remove_document(orphan)
            
            # 重新获取脱水后的干净账本快照
            valid_dest_paths = set()
            docs = self.meta.get_documents_snapshot()
            
            # 🚀 [架构补丁]：同步总闸感知
            langs = []
            source_code = self.i18n.get('source', {}).get('code', "")
            langs.append(source_code)
                
            if self.i18n.get('enabled', True):
                for t in self.i18n.get('targets', []):
                    t_code = t.get('code')
                    if t_code is not None:
                        langs.append(t_code)
            
            for rel_path, doc in docs.items():
                slug = doc.get("slug")
                if not slug: continue
                
                prefix = doc.get("prefix", "")
                source = doc.get("source", "")
                
                t_abs = os.path.join(self.paths['vault'], rel_path)
                t_src_abs = os.path.join(self.paths['vault'], source)
                t_sub_rel = os.path.relpath(t_abs, t_src_abs).replace('\\', '/')
                t_sub_dir = os.path.dirname(t_sub_rel).replace('\\', '/')
                if t_sub_dir == '.': t_sub_dir = ""
                
                # 🚀 路由对齐
                mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=False)
                ext = os.path.splitext(rel_path)[1].lower()
                
                for code in langs:
                    dest = os.path.abspath(os.path.join(self.paths['target_base'], code, prefix, mapped_sub_dir, f"{slug}{ext}"))
                    valid_dest_paths.add(dest)
                    
            controlled_roots = [os.path.abspath(os.path.join(self.paths['target_base'], code)) for code in langs]
            
            deleted_count = 0
            for scan_root in controlled_roots:
                if not os.path.exists(scan_root): continue
                
                for root, _, files in os.walk(scan_root):
                    for f in files:
                        if f.endswith(('.md', '.mdx')):
                            f_abs = os.path.abspath(os.path.join(root, f))
                            
                            if f_abs not in valid_dest_paths:
                                if is_dry_run:
                                    logger.info(f"    [Dry-Run 模拟清洗] 拟删除幽灵路由文件: {f_abs}")
                                else:
                                    try:
                                        os.remove(f_abs)
                                        logger.info(f"    [路由清洗] 物理移除未受控的幽灵文章: {f_abs}")
                                        deleted_count += 1
                                    except Exception as e:
                                        logger.error(f"    [清洗失败] 无法删除幽灵文件 {f_abs}: {e}")

            for scan_root in controlled_roots:
                self._gc_empty_directories(scan_root, is_dry_run)
                                        
            if deleted_count > 0:
                logger.info(f"✨ 幽灵清洗完成，共斩断了 {deleted_count} 个脱离管线的野路由。")
            else:
                logger.info("✨ 路由健康度 100%，未发现任何幽灵文件。")