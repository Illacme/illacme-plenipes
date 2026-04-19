#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Watchdog Daemon
模块职责：目录监控与防抖事件总线。
利用 FileSystemObserver 提供毫秒级的 FS 事件拦截，通过防抖延迟锁防止重复派发。
"""

import os
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
            self.debounce_delay = engine.config.system.typing_idle_threshold
            
            # 🚀 [V18.6 全平台过滤矩阵与延迟保洁泵]
            watch_cfg = engine.config.system.watchdog_settings
            self._gc_timer = None
            self._heavy_timer = None # 🚀 [V11] 重型任务全局防抖计时器
            self._tombstone_timers = {} # 🚀 [V8] 单独管理墓碑延迟，实现“先生后杀”
            
            # 从配置读取过滤黑名单
            self.exclude_dirs = set(watch_cfg.exclude_dirs)
            self.exclude_patterns = set(watch_cfg.exclude_patterns)
            
            # 从配置读取阶梯式延迟参数
            self.heavy_task_delay = watch_cfg.heavy_task_delay
            self.gc_delay = watch_cfg.gc_delay
            self.handover_delay = watch_cfg.handover_delay

            logger.info(f"🛡️ 智能监听矩阵已就绪 | 防抖: {self.debounce_delay}s | 过滤黑名单: {list(self.exclude_dirs)}")

        def _should_skip(self, path):
            """
            🚀 [V20.1] 极致隔离协议：按绝对路径前缀进行监听降噪
            绝对禁止监听影子仓库 (Shadow) 和出口目录 (SSG)
            """
            abs_path = os.path.normcase(os.path.realpath(path))
            
            # 1. 静态黑名单过滤 (零件名匹配)
            parts = abs_path.replace('\\', '/').split('/')
            if any(eb in parts for eb in self.exclude_dirs): return True
            
            # 2. 动态输出隔离 (绝对路径前缀匹配)
            # 屏蔽影子仓库、SSG 根目录以及元数据存储区
            silent_zones = [
                engine.paths.get('shadow'),
                engine.paths.get('target_base'),
                os.path.dirname(engine.paths.get('ledger_cache', ''))
            ]
            
            for zone in silent_zones:
                if zone:
                    norm_zone = os.path.normcase(os.path.realpath(zone))
                    # 只要事件路径在静默区内，立即拦截
                    if abs_path.startswith(norm_zone):
                        return True
            
            # 3. 检查文件名后缀/前缀黑名单
            fname = os.path.basename(path)
            if any(fname.endswith(p) for p in self.exclude_patterns): return True
            if fname.startswith(('~$', 'tmp_')): return True
            
            return False

        def _find_route_info_for_path(self, abs_path):
            # 🚀 跨平台路径对齐补丁：使用 realpath 消除 Mac 挂载别名与 Windows 盘符大小写差异
            norm_abs = os.path.normcase(os.path.realpath(abs_path))
            sorted_matrix = sorted(engine.route_matrix, key=lambda x: len(x.get('source', '')), reverse=True)
            
            for route_cfg in sorted_matrix:
                src = route_cfg.get('source', '')
                route_abs = os.path.normcase(os.path.realpath(os.path.join(engine.vault_root, src)))
                # 确保路径以分隔符结尾，防止 "Blog-Backup" 误匹配 "Blog"
                route_dir = route_abs if route_abs.endswith(os.sep) else route_abs + os.sep
                
                if norm_abs.startswith(route_dir):
                    return route_cfg.get('prefix', ''), src
            return None, None

        def _debounced_submit(self, file_path, prefix, source, delay=None):
            actual_delay = delay if delay is not None else self.debounce_delay
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
                timer = threading.Timer(actual_delay, task_wrapper)
                self._timers[file_path] = timer
                timer.start()

        def _lazy_gc_trigger(self):
            """
            🚀 [核心稳定性补丁：延迟保洁泵]
            为了防止 Docusaurus (Rspack) 崩溃，在监控模式下，物理文件的删除将推迟到操作停止 30 秒后执行。
            """
            with self._lock:
                if self._gc_timer:
                    self._gc_timer.cancel()
                
                def run_gc():
                    with self._lock:
                        self._gc_timer = None
                    if engine.config.system.enable_asset_audit:
                        logger.info("🧹 [延迟保洁] 侦测到环境已进入静默期，正在执行周期性物理资产审计与清理...")
                        engine.janitor.gc_orphans(current_source_files, is_dry_run=args.dry_run)
                        if not args.dry_run: engine.meta.save()

                self._gc_timer = threading.Timer(self.gc_delay, run_gc)
                self._gc_timer.start()

        def _debounced_heavy_tasks(self):
            """🚀 [V11] 重型任务聚合执行器：Meta 账本同步 & 数字花园导出"""
            with self._lock:
                if self._heavy_timer:
                    self._heavy_timer.cancel()
                
                def task():
                    try:
                        logger.info("🕸️ [守护进程] 环境已进入静默期，正在执行重型同步任务 (Meta & Garden)...")
                        # 🛡️ [V34.6 Sentinel] 执行主动健康审计与自愈
                        engine.sentinel.run_health_check(auto_fix=True)
                        
                        engine.meta.save()
                        export_digital_garden(engine)
                    except Exception as e:
                        logger.error(f"🛑 [重型延迟任务失败]: {e}")
                    finally:
                        with self._lock:
                            self._heavy_timer = None

                # 🚀 [V18.6 V13] 静默期收紧：提供更快的交互反馈，同时保留 Rspack 缓冲
                self._heavy_timer = threading.Timer(self.heavy_task_delay, task)
                self._heavy_timer.start()

        def _debounced_handover(self, old_rel, new_rel, prefix_old, source_old, prefix_new, source_new):
            """
            🚀 [V18.6 V19] 影子镜像迁移调度器
            """
            def task():
                try:
                    logger.info("🚚 [迁移协议] 正在执行 Shadow -> SSG 物理平移交接...")
                    engine.janitor.physical_handover(old_rel, new_rel, prefix_old, source_old, prefix_new, source_new)
                except Exception as e:
                    logger.error(f"🛑 [迁移中断]: {e}")
            
            # 使用配置的迁移延迟，确保 Meta 状态预热完成
            threading.Timer(self.handover_delay, task).start()

        def _dispatch_task(self, file_path, prefix, source, delay=None):
            try:
                engine.sync_document(file_path, prefix, source, is_dry_run=args.dry_run, force_sync=args.force)
                
                # 🚀 [V18.6 V11 稳定性升级] 账本和花园任务进入全局防抖泵，不再即时触发
                if not args.dry_run:
                    self._lazy_gc_trigger()
                    self._debounced_heavy_tasks()
                    fname = os.path.basename(file_path)
                    send_notification("✨ 文章已更新", f"《{fname}》已完成 AI 同步并上线")
            except Exception:
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
            if event.is_directory or self._should_skip(event.src_path): return
            
            logger.info(f"👀 [监听] 捕捉到新文件 (Created): {os.path.basename(event.src_path)}")
            if event.src_path.lower().endswith((".md", ".mdx")):
                rel_path = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                # 🚀 [V34.5] 记录初次发现
                engine.timeline.log_event("CREATED", rel_path, "PENDING", "探测到物理新增")
                
                current_source_files.add(rel_path)
                prefix, source = self._find_route_info_for_path(event.src_path)
                if prefix is not None and source is not None:
                    logger.info(f"🚀 [监听] 正在调度同步任务: {rel_path}")
                    self._debounced_submit(event.src_path, prefix, source)
            else:
                self._add_asset(event.src_path)

        def on_modified(self, event):
            if event.is_directory or self._should_skip(event.src_path): return
            
            if event.src_path.lower().endswith((".md", ".mdx")):
                rel_path = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                # 🚀 [V34.5] 记录修改行为
                engine.timeline.log_event("MODIFIED", rel_path, "PENDING", "探测到物理内容变化")
                
                current_source_files.add(rel_path) 
                prefix, source = self._find_route_info_for_path(event.src_path)
                if prefix is not None and source is not None:
                    logger.info(f"📝 [监听] 捕捉到内容修改 (Modified): {rel_path}")
                    self._debounced_submit(event.src_path, prefix, source)

        def on_deleted(self, event):
            if self._should_skip(event.src_path): return

            if event.is_directory:
                logger.info(f"🗑️ [监听] 捕捉到目录删除: {os.path.basename(event.src_path)}")
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
                    logger.info(f"📂 [监听] 批量目录移除 ({rel_dir})，延迟回收已激活...")
                    self._lazy_gc_trigger()
                    # 🚀 [V18.6 V18] 移除同步写盘，交给延迟保洁泵和重型任务泵统一处理
                return

            if not event.is_directory:
                if event.src_path.lower().endswith((".md", ".mdx")):
                    logger.info(f"🗑️ [监听] 捕捉到文件删除: {os.path.basename(event.src_path)}")
                    rel_path = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                    # 🚀 [V34.5] 记录删除行为
                    engine.timeline.log_event("DELETED", rel_path, "REMOVED", "探测到物理下线")
                    
                    current_source_files.discard(rel_path)
                    
                    # 🚀 [V18.6 V9] 幽灵协议：立即（0.05s）原地覆盖，释放 Slug 占位，且保持物理不间断
                    # 🚀 [V16] 物理删除已由延迟保洁泵接管
                    # 此处不再执行原地操作，直接进入延迟保洁泵 (30s)
                    
                    # 触发延迟保洁泵 (30s)
                    self._lazy_gc_trigger()
                    # 🚀 [V11] 账本和花园任务推迟到静默期执行
                    self._debounced_heavy_tasks()
                else:
                    self._remove_asset(event.src_path)

        def on_moved(self, event):
            # 🚀 [V18.6 V7] 原地移动防御：如果源和目标一致（常发生于大小写重命名或 Mac 拖拽误触），严禁立碑
            if os.path.realpath(event.src_path) == os.path.realpath(event.dest_path):
                logger.debug(f"🛡️ [监听] 侦测到原地移动 ({os.path.basename(event.src_path)})，已拦截自残式立碑逻辑。")
                if not event.is_directory:
                    # 依然触发一次静注同步，防止内容有细微变动（比如 touch）
                    prefix, source = self._find_route_info_for_path(event.dest_path)
                    if prefix: self._debounced_submit(event.dest_path, prefix, source, delay=0.1)
                return

            # 对源路径和目标路径都进行过滤判定
            if self._should_skip(event.src_path) and self._should_skip(event.dest_path):
                return

            if event.is_directory:
                logger.info(f"🚚 [监听] 捕捉到目录移动 (Moved): {os.path.basename(event.src_path)} -> {os.path.basename(event.dest_path)}")
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
                            if f.lower().endswith(('.md', '.mdx')):
                                abs_new = os.path.join(root, f)
                                new_rel = os.path.relpath(abs_new, engine.vault_root).replace('\\', '/')
                                current_source_files.add(new_rel)
                                prefix, source = self._find_route_info_for_path(abs_new)
                                if prefix is not None and source is not None:
                                    self._debounced_submit(abs_new, prefix, source)
                                    
                if to_remove:
                    logger.info(f"📂 [监听] 目录更替中 ({old_rel_dir})，延迟回收已激活...")
                    self._lazy_gc_trigger()
                    if not args.dry_run: 
                        engine.meta.save()
                        export_digital_garden(engine)
                return

            # 🚀 [V18.6] 物理移动原子化逻辑：实现 0.1s 极速平滑迁移
            prefix_new, source_new = None, None
            new_rel = None
            if hasattr(event, 'dest_path') and event.dest_path.lower().endswith((".md", ".mdx")):
                new_rel = os.path.relpath(event.dest_path, engine.vault_root).replace('\\', '/')
                prefix_new, source_new = self._find_route_info_for_path(event.dest_path)

            if event.src_path.lower().endswith((".md", ".mdx")):
                logger.info(f"🚚 [监听] 捕捉到文件移动 (Moved): {os.path.basename(event.src_path)} -> {os.path.basename(event.dest_path)}")
                old_rel = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                new_rel_tmp = os.path.relpath(event.dest_path, engine.vault_root).replace('\\', '/')
                # 🚀 [V34.5] 记录移动轨迹
                engine.timeline.log_event("MOVED", old_rel, "MOVED", f"迁移至: {new_rel_tmp}")
                
                old_rel = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                
                # 🚀 [V18.6 V7] 深度碰撞检测：如果搬家前后的 Slug 同步到了同一个 SSG 物理位置，严禁立碑
                doc_info = engine.meta.get_doc_info(old_rel)
                prefix_old, source_old = self._find_route_info_for_path(event.src_path)
                
                # 判定是否有物理路径重叠
                should_tombstone = True
                if doc_info and doc_info.get('slug') and prefix_old is not None and prefix_new is not None:
                    # 🚀 [V18.6 V7] 极致碰撞探测：必须“语种池、源目录、子目录”全量对齐且 Slug 没变
                    if prefix_old == prefix_new and source_old == source_new:
                        # 计算子目录相对路径
                        sub_old = os.path.dirname(os.path.relpath(event.src_path, os.path.join(engine.vault_root, source_old))).replace('\\', '/')
                        sub_new = os.path.dirname(os.path.relpath(event.dest_path, os.path.join(engine.vault_root, source_new))).replace('\\', '/')
                        
                        if sub_old == sub_new:
                            logger.debug(f"🛡️ [监听] 检测到物理路径完全对齐 ({doc_info.get('slug')})，跳过墓碑阶段。")
                            should_tombstone = False

                if should_tombstone and prefix_old is not None and new_rel:
                    # 🚀 [V18.6 V19] 影子镜像迁移：立即执行物理平移，让 Docusaurus 看到一次合法的 Move
                    self._debounced_handover(old_rel, new_rel, prefix_old, source_old, prefix_new, source_new)

                current_source_files.discard(old_rel)
                with self._lock:
                    if event.src_path in self._timers:
                        self._timers[event.src_path].cancel()
                        del self._timers[event.src_path]

            if new_rel:
                current_source_files.add(new_rel)
                if prefix_new is not None and source_new is not None:
                    logger.info(f"🚀 [监听] 正在调度新路径同步 (错峰模式): {new_rel}")
                    # 🚀 [V18.6 V16] 缩短响应时间（0.1s），让 B 尽快上线
                    self._debounced_submit(event.dest_path, prefix_new, source_new, delay=0.1)
                    # 🚀 [V11] 任务防抖化
                    self._debounced_heavy_tasks()
            else:
                if not event.is_directory:
                    self._add_asset(event.dest_path)

            # 🚀 [V18.6 V18] 移除此处极其不合理的同步阻塞写盘，所有状态固化均通过异步防抖泵执行
            # 这样可以确保移动操作期间，Docusaurus 不会被零散的写入节奏带偏
                    
    observer = Observer()
    observer.schedule(ChangeHandler(), engine.vault_root, recursive=True)
    observer.start()
    
    return observer, watch_pool