#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Janitor Engine (GC & Cleanup)
模块职责：幽灵清道夫与垃圾回收微内核。
接管所有的自底向上的物理资产清理、孤儿路由拔除与状态机自愈逻辑。
架构原则：严格依赖注入 (DI)，挂载全局并发锁，绝对免疫对正在生成中文件的误杀。
🚀 [V16.1 架构升级]：全面修复多语言键名脱靶 bug，并注入主引擎同源的物理寻址探针，彻底消灭脑裂误杀。
"""

import os
import re
import uuid
import logging
import tempfile

logger = logging.getLogger("Illacme.plenipes")

class JanitorService:
    """
    🚀 独立垃圾回收中枢
    在执行任何物理删除前，必须侦测全局引擎锁与处理中互斥锁，确保 I/O 安全。
    """
    def __init__(self, global_lock, processing_locks, paths, meta_manager, route_manager, i18n_cfg, sys_cfg=None, active_theme='starlight'):
        self._global_engine_lock = global_lock
        self._processing_locks = processing_locks
        self.paths = paths
        self.meta = meta_manager
        self.route_manager = route_manager
        self.i18n = i18n_cfg
        self.sys_cfg = sys_cfg or {}
        self.active_theme = active_theme
        # 🚀 [V17.6] 物理白名单高速缓存：存储本轮同步中确认为“合法”且“新鲜”的路径
        self.fresh_paths = set()
        self.amnesty_paths = set()  # 🚀 [V11] GC 赦免名单

    def mark_as_fresh(self, path):
        """由 Dispatcher 调用，为刚写盘的文件颁发物理豁免牌"""
        norm_path = os.path.realpath(path).lower()
        self.fresh_paths.add(norm_path)
        self.amnesty_paths.add(norm_path) # 🚀 [V11] 注册赦免，防止回位移动被误杀

    def _gc_empty_directories(self, target_dir, is_dry_run=False):
        """🚀 幽灵空目录清道夫：自底向上抹除无用文件夹，提升前端编译极速性能"""
        if not os.path.exists(target_dir): return
        for root, dirs, files in os.walk(target_dir, topdown=False):
            for d in dirs:
                dir_path = os.path.join(root, d)
                try:
                    if not os.listdir(dir_path):
                        # 🚀 [V18.6 V6] 在监控模式下，绝对禁止删除空目录。删除目录是 Docusaurus 崩溃的高危诱因。
                        # 保留空目录对性能无影响，但能极大提升热更新稳定性。
                        is_watch_mode = getattr(self.meta, 'is_watch_mode', False)
                        if is_watch_mode:
                            logger.debug(f"    [监控保护] 已跳过空目录清理: {dir_path}")
                            continue

                        if is_dry_run:
                            logger.info(f"    [Dry-Run 模拟清理] 拟删除空目录: {dir_path}")
                        else:
                            os.rmdir(dir_path)
                            logger.info(f"    [空目录清理] 物理移除无用空目录: {dir_path}")
                except Exception as e:
                    pass

    def gc_assets(self, current_source_files=None, is_dry_run=False):
        """物理瘦身逻辑：带全局写保护屏障的物理资产清算器"""
        in_flight = any(l.locked() for l in self._processing_locks.values())
        if in_flight:
            logger.warning("🚧 [GC 熔断] 检测到有文章正在处理中，为防止误删生成中的新生资产，已强行熔断本次物理清理泵。")
            return

        with self._global_engine_lock:
            logger.info("🧹 启动前端资产目录“大扫除” (gc_assets)...")
            active_assets = set()
            
            docs = self.meta.get_documents_snapshot()
            total_docs = len(docs)
            
            if current_source_files is None and total_docs > 0:
                logger.warning("🚧 资产账本未接收到全量物理扫描基线，为了保护您的附件不被误删，已自动跳过本次清理。")
                return
            
            for doc in docs.values():
                assets = doc.get("assets", [])
                if isinstance(assets, list):
                    for a in assets:
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

            mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run, allow_ai=False)
            ext = os.path.splitext(rel_path)[1].lower()

            langs = []
            source_code = self.i18n.source.get('lang_code', 'zh-cn')
            if source_code is not None: langs.append(source_code)
            
            if self.i18n.enabled:
                for t in self.i18n.targets:
                    t_code = t.get('lang_code') 
                    if t_code is not None: langs.append(t_code)
                    
            for code in langs:
                # 🚀 架构升维：直接调用注入的 RouteManager 中枢探针
                dest = self.route_manager.resolve_physical_path(self.paths['target_base'], code, prefix, mapped_sub_dir, slug, ext)
                if os.path.exists(dest):
                    # 🚀 [V11] 最终死刑复核：如果在保洁泵触发前，该文件已“重生”，则赦免物理删除
                    dest_norm = os.path.realpath(dest).lower()
                    if dest_norm in self.amnesty_paths:
                        logger.debug(f"⚖️ [GC 赦免] 检测到重生文件 {os.path.basename(dest)}，取消死刑执行。")
                        continue

                    if is_dry_run: 
                        logger.info(f"    [Dry-Run 模拟回收] 拟删除文章文件: {dest}")
                    else: 
                        try:
                            # 🚀 [V18.6 V12] 长生协议：监控模式下严禁物理删除博文路径
                            is_watch_mode = getattr(self.meta, 'is_watch_mode', False)
                            if is_watch_mode:
                                logger.debug(f"    [长生守卫] 已拦截物理删除，保持路径连续性: {dest}")
                                continue
                                
                            os.remove(dest)
                        except Exception as e: logger.error(f"回收文章文件失败 {dest}: {e}")
                            
        if not is_dry_run: self.meta.remove_document(rel_path)

    def fast_tombstone(self, rel_path, route_prefix, route_source):
        """
        🚀 [元数据污染防御] 原子墓碑化：立即将物理文件重命名，使其对 Docusaurus 不可见
        """
        doc_info = self.meta.get_doc_info(rel_path)
        slug = doc_info.get("slug")
        if not slug: return

        prefix = doc_info.get("prefix", route_prefix)
        source = doc_info.get("source", route_source)
        ext = os.path.splitext(rel_path)[1].lower()

        # 构造所有语种的物理路径并执行重命名
        langs = [self.i18n.source.get('lang_code', 'zh-cn')]
        if self.i18n.enabled:
            langs.extend([t.get('lang_code') for t in self.i18n.targets if t.get('lang_code')])

        for code in langs:
            # 推导子目录映射
            t_abs = os.path.join(self.paths['vault'], rel_path)
            t_src_abs = os.path.join(self.paths['vault'], source)
            try:
                t_sub_rel = os.path.relpath(t_abs, t_src_abs).replace('\\', '/')
                t_sub_dir = os.path.dirname(t_sub_rel).replace('\\', '/')
                if t_sub_dir == '.': t_sub_dir = ""
                mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, allow_ai=False)
                
                dest = self.route_manager.resolve_physical_path(self.paths['target_base'], code, prefix, mapped_sub_dir, slug, ext)
                if os.path.exists(dest):
                    # 🚀 [V6 保护位] 绝对禁止立碑已经在新位置生成的“新鲜”博文
                    dest_norm = os.path.realpath(dest).lower()
                    if dest_norm in self.fresh_paths:
                        logger.debug(f"🛡️ [墓碑拦截] 目标路径 {os.path.basename(dest)} 处于 Fresh 状态，已放弃立碑。")
                        continue

                    # 🚀 [V18.6 V16] 彻底弃用幽灵协议，恢复物理删除
                    # 此时删除动作已由 daemon.py 错峰至 1.5s 之后，绝对安全。
                    try:
                        os.remove(dest)
                        logger.debug(f"🧹 [错峰删除] 已清理老路径资产: {os.path.basename(dest)}")
                    except Exception as e:
                        logger.error(f"⚠️ [清理失败] 无法移除旧路径 {dest}: {e}")
            except Exception as e:
                logger.debug(f"锚定墓碑失败 {rel_path}: {e}")

    def physical_handover(self, old_rel, new_rel, prefix_old, source_old, prefix_new, source_new):
        """
        🚀 [V18.6 V19] 物理原子迁移协议：
        根据影子仓库架构，同步对影子层 (Shadow) 和出口层 (SSG) 执行物理重命名。
        确保 Docusaurus 看到的是 Move 事件，而不是 Delete + Add。
        """
        try:
            # 1. 提前回溯旧文档元数据
            doc_info = self.meta.get_doc_info(old_rel)
            if not doc_info: return
            
            old_slug = doc_info.get('slug')
            if not old_slug: return
            
            # 2. 预演新博文的 Slug (保持指纹继承一致性)
            # 简单起见，如果 new_rel 没变化太多，复用旧 Slug（这是我们的默认策略）
            new_slug = old_slug 
            ext = os.path.splitext(old_rel)[1]
            
            # 3. 获取所有语种池 (V29 对齐方案)
            src_code = self.i18n.source.get('lang_code', 'zh-cn')
            langs = [src_code]
            if self.i18n.enabled:
                langs.extend([t.get('lang_code') for t in self.i18n.targets if t.get('lang_code')])
            
            # 4. 级联重命名
            for lang in set(langs):
                # 计算新旧子目录映射
                sub_old = os.path.dirname(os.path.relpath(os.path.join(self.paths['vault'], old_rel), os.path.join(self.paths['vault'], source_old))).replace('\\', '/')
                if sub_old == '.': sub_old = ""
                mapped_sub_old = self.route_manager.get_mapped_sub_dir(sub_old, is_dry_run=False, allow_ai=False)
                
                sub_new = os.path.dirname(os.path.relpath(os.path.join(self.paths['vault'], new_rel), os.path.join(self.paths['vault'], source_new))).replace('\\', '/')
                if sub_new == '.': sub_new = ""
                mapped_sub_new = self.route_manager.get_mapped_sub_dir(sub_new, is_dry_run=False, allow_ai=False)
                
                # 定义四种物理路径 (Shadow x 2, SSG x 2)
                for base_dir_key in ['shadow', 'target_base']:
                    base_root = self.paths.get(base_dir_key)
                    if not base_root: continue
                    
                    old_p = self.resolve_physical_path(base_root, lang, prefix_old, mapped_sub_old, old_slug, ext)
                    new_p = self.resolve_physical_path(base_root, lang, prefix_new, mapped_sub_new, new_slug, ext)
                    
                    if os.path.exists(old_p):
                        try:
                            os.makedirs(os.path.dirname(new_p), exist_ok=True)
                            os.replace(old_p, new_p)
                            logger.debug(f"🚚 [物理平移] 已将 {base_dir_key} 资产从老路径移至新路径: {os.path.basename(new_p)}")
                            # 豁免新路径，防止接下来的保洁误杀
                            self.mark_as_fresh(new_p)
                        except Exception as e:
                            logger.warning(f"⚠️ [平移失败] {base_dir_key} 层级冲突: {e}")
        except Exception as e:
            logger.error(f"🛑 [原子迁移协议崩溃]: {e}")

    def resolve_physical_path(self, base_root, lang, prefix, sub_dir, slug, ext):
        """私有寻址中继器"""
        return self.route_manager.resolve_physical_path(base_root, lang, prefix, sub_dir, slug, ext)

    def gc_orphans(self, current_source_files, is_dry_run=False):
        """级联孤儿回收泵"""
        docs_snapshot = self.meta.get_documents_snapshot()
        to_delete = [p for p in list(docs_snapshot.keys()) if p not in current_source_files]
        for rel_path in to_delete:
            prefix = docs_snapshot[rel_path].get("prefix", "")
            source = docs_snapshot[rel_path].get("source", "")
            
            # 🚀 [V20.6 V21] 日志真实性校验
            # 只有当物理文件还存在时，才报“移除已删除的文章”。
            # 如果是搬家流（物理已 replace），这里应该保持静默，避免用户困惑。
            slug_for_log = docs_snapshot[rel_path].get("slug")
            if not slug_for_log: continue
            
            ext = os.path.splitext(rel_path)[1]
            dest_for_log = self.route_manager.resolve_physical_path(
                self.paths['target_base'], 'zh-Hans', prefix, "", slug_for_log, ext
            )
            
            if os.path.exists(dest_for_log):
                if not is_dry_run: logger.info(f"  └── [回收清理] 物理移除已删除的文章: {rel_path}")
                
            self.gc_node(rel_path, prefix, source, is_dry_run)
        
        # 🚀 [V18.6] 同时收割所有 30s 前立下的残留墓碑
        self.gc_tombstones(is_dry_run)
        self.gc_assets(current_source_files, is_dry_run)

    def gc_tombstones(self, is_dry_run=False):
        """收割所有逻辑删除的墓碑文件"""
        scan_root = os.path.abspath(self.paths['target_base'])
        for root, _, files in os.walk(scan_root):
            for f in files:
                if f.endswith(".tombstone"):
                    f_abs = os.path.join(root, f)
                    if is_dry_run:
                        logger.info(f"    [模拟清理] 拟收割墓碑: {f}")
                    else:
                        try:
                            # 🚀 [V18.6 V12] 监控模式下不收割墓碑，防止 Rspack 路径报错
                            if getattr(self.meta, 'is_watch_mode', False):
                                continue
                            os.remove(f_abs)
                            logger.debug(f"🪦 [墓碑收割] 已彻底移除残留缓存: {f}")
                        except: pass

    def gc_ghost_nodes(self, is_dry_run=False):
        """幽灵路由清道夫：支持 MDX 清洗与账本自愈"""
        in_flight = any(l.locked() for l in self._processing_locks.values())
        if in_flight:
            logger.warning("🚧 [路由清洗熔断] 检测到有文章正在生成中，为防止误删写入一半的新文章，已强行熔断本次路由清洗。")
            return

        with self._global_engine_lock:
            logger.info("🧹 启动前端路由目录“幽灵清洗” (gc_ghost_nodes)...")
            
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
            
            valid_dest_paths = set()
            docs = self.meta.get_documents_snapshot()
            
            langs = []
            # 🚀 修复点 4：纠正语言代码键名
            source_code = self.i18n.source.get('lang_code', 'zh-cn')
            if source_code is not None: langs.append(source_code)
                
            if self.i18n.enabled:
                for t in self.i18n.targets:
                    t_code = t.get('lang_code') # 🚀 修复点 5
                    if t_code is not None: langs.append(t_code)
            
            valid_dest_paths = set()
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
                
                mapped_sub_dir = self.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=is_dry_run, allow_ai=False)
                ext = os.path.splitext(rel_path)[1].lower()
                
                for code in langs:
                    # 🚀 架构升维：直接调用注入的 RouteManager 中枢探针生成白名单字典
                    dest = self.route_manager.resolve_physical_path(self.paths['target_base'], code, prefix, mapped_sub_dir, slug, ext)
                    valid_dest_paths.add(os.path.realpath(dest).lower())
                    
            # 🚀 修复点 7 (终极护城河版)：锁定根目录，但强行熔断系统目录的扫描权限
            scan_root = os.path.abspath(self.paths['target_base'])
            deleted_count = 0

            # 🛡️ [V14.3 全域物理防护矩阵]：由原来的硬编码重构为由 config.yaml 驱动的动态排除逻辑
            janitor_opts = self.sys_cfg.janitor_settings
            global_exclude = janitor_opts.global_exclude
            theme_exclude = janitor_opts.theme_exclude.get(self.active_theme, [])
            all_exclude = set(global_exclude + theme_exclude)
            
            for root, dirs, files in os.walk(scan_root):
                # 🛡️ 绝对物理隔离带：由原来的硬编码重构为由 config.yaml 驱动的动态排除逻辑
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in all_exclude]
                
                # 🛡️ 根文件保护伞：绝对禁止抹除项目根目录下的文件 (如 README.md)
                if root == scan_root:
                    continue 
                    
                for f in files:
                    if f.endswith(('.md', '.mdx')):
                        f_abs_normalized = os.path.realpath(os.path.join(root, f)).lower()
                        
                        # 豁免机制：如果该文件不在 Illacme 的受控白名单中，且没有新鲜豁免权，执行销毁
                        if f_abs_normalized not in valid_dest_paths and f_abs_normalized not in self.fresh_paths:
                            if is_dry_run:
                                logger.info(f"    [Dry-Run 模拟清洗] 拟删除幽灵路由文件: {f_abs_normalized}")
                            else:
                                try:
                                    # 🚀 [V18.6 V12] 监控模式下物理隔离路由清理
                                    if getattr(self.meta, 'is_watch_mode', False):
                                        logger.debug(f"    [长生守卫] 路由清洗已拦截物理路径删除: {f_abs_normalized}")
                                        continue

                                    os.remove(f_abs_normalized)
                                    logger.info(f"    [路由清洗] 物理移除未受控的幽灵文章: {f_abs_normalized}")
                                    deleted_count += 1
                                except Exception as e:
                                    logger.error(f"    [清洗失败] 无法删除幽灵文件 {f_abs_normalized}: {e}")

            # 同样对空目录清理加上隔离，只清理受控的 i18n, docs 等目录
            for safe_dir in [d for d in os.listdir(scan_root) if d not in ['.git', 'node_modules', 'src', 'static', 'public']]:

                safe_abs_dir = os.path.join(scan_root, safe_dir)
                if os.path.isdir(safe_abs_dir):
                    self._gc_empty_directories(safe_abs_dir, is_dry_run)
                                        
            if deleted_count > 0:
                logger.info(f"✨ 幽灵清洗完成，共斩断了 {deleted_count} 个脱离管线的野路由。")
            else:
                logger.info("✨ 路由健康度 100%，未发现任何幽灵文件。")