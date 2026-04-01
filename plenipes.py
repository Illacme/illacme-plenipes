#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes (v13.6.2) - 工业级架构优化版 (CLI Entry)
模块职责：本地运行的命令行入口客户端。
架构升级：彻底解耦 Watchdog 事件捕获与重型 AI 编译管线，引入独立事件调度池。
装载了防撕裂的信号拦截（Signal Interception）、优雅停机（Graceful Shutdown）
以及 OS 级别的单例进程互斥锁 (Singleton Process Lock)，物理免疫双开灾难。

[v13.6.2 特殊修正]：
1. 终极融合：将 v13.5 的资产审计配置、单次 Sync 状态机感知与 v13.6 的 I/O 级防抖、幽灵任务拦截完美合并。
2. 依赖对齐：修复了全局漏掉 import threading 导致看门狗守护线程初始化的崩溃问题。
3. 稀疏存储：彻底摒弃无意义的 asset: [] 占位，保持元数据极简。
4. 交叉审计：引入全量基线的双向交叉验证逻辑，仅统计真正拥有资产的文档。
"""

import os
import time
from datetime import datetime
import signal
import sys
import argparse
import socket
import traceback
import yaml
import shutil  # 🚀 系统级文件拷贝依赖
import platform   # 🚀 新增：用于精准识别 OS 环境
import subprocess # 🚀 新增：用于调用系统原生通知指令
import threading  # 🚀 [Hotfix] 注入多线程防抖依赖，修复 Watchdog 崩溃
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

# 🚀 引入我们解耦拆分出来的核心域服务
from core.utils import setup_logger
from core.engine import IllacmeEngine

logger = setup_logger()

# 全局句柄，用于捕获退出信号时安全卸载资源，以及维持 Socket 锁的生命周期
global_engine = None
global_observer = None
global_watch_pool = None
_SINGLETON_SOCKET = None

def send_notification(title, message):
    """
    🚀 跨平台系统通知调度器
    支持：macOS (osascript), Linux (notify-send), Windows (PowerShell)
    """
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            cmd = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", cmd], check=False)
        elif system == "Linux": # Linux
            subprocess.run(["notify-send", title, message], check=False)
        elif system == "Windows": # Windows
            # 使用 PowerShell 调用原生气泡通知
            cmd = f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('{message}', '{title}')"
            subprocess.run(["powershell", "-Command", cmd], check=False)
    except Exception as e:
        logger.debug(f"系统通知发送失败: {e}")

def acquire_singleton_lock(port=43210):
    """
    进程级单例防线 (OS-Level Singleton Mutex)
    基于配置文件动态分配防撞端口。
    核心原理：向操作系统申请绑定一个特定的高位本地端口。
    优势：完全免疫 kill -9 强杀导致的僵尸锁问题。进程一旦死亡，内核瞬间释放端口。
    """
    global _SINGLETON_SOCKET
    _SINGLETON_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # 绑定到指定端口。如果已有 plenipes.py 在后台运行，此处将抛出 Address already in use 异常
        _SINGLETON_SOCKET.bind(('127.0.0.1', port))
    except socket.error:
        # 🚀 语义降维：将“架构级防线触发”替换为小白能懂的端口冲突诊断
        logger.error(f"\n🛑 [运行冲突] 启动失败：端口 {port} 已被占用，检测到系统已经在后台运行！")
        logger.error("   └── 💡 为了保护您的文章数据和电脑内存，本次重复启动已自动拦截。")
        logger.error("   └── 请检查是否开了多个终端窗口，或者在 config.yaml 中修改 singleton_port。")
        sys.exit(1)

def graceful_shutdown(signum, frame):
    """拦截操作系统级的中断信号，执行防内存撕裂的终极快照固化"""
    # 🚀 语义降维：将“探针截获系统信号”等黑话转化为安全感十足的保存提示
    logger.warning("\n⚠️ 收到停止指令！正在安全保存数据并关闭系统...")
    
    if global_observer:
        global_observer.stop()
        logger.info("  └── [1/3] 文件夹自动监控已关闭。")
        
    if global_watch_pool:
        # shutdown(wait=False) 防止卡死，直接阻断新任务
        global_watch_pool.shutdown(wait=False)
        logger.info("  └── [2/3] 正在中断尚未开始的排队任务。")
        
    if global_engine and hasattr(global_engine, 'meta'):
        global_engine.meta.force_save()
        logger.info("  └── [3/3] 文章处理进度已 100% 安全存档。")
        
    logger.info("🛑 系统已安全关闭，下次见！")
    sys.exit(0)

# 挂载信号拦截器
signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Illacme-plenipes: 工业级 Markdown 到全量泛用型 SSG 映射同步中枢")
    parser.add_argument('--config', default='config.yaml', help="指定 YAML 配置文件路径 (默认: config.yaml)")
    parser.add_argument('--sync', action='store_true', help="发起单次全库阵列增量同步测绘")
    parser.add_argument('--watch', action='store_true', help="进入 Daemon 模式：启动系统看门狗守护进程，毫秒级监听源库变动")
    parser.add_argument('--dry-run', action='store_true', help="[安全演练模式] 阻断实际 API 扣费请求和物理写盘")
    parser.add_argument('--force', action='store_true', help="[强制重构模式] 强行撕碎 MD5 本地状态防抖指纹，强拉所有引擎模块执行覆盖重编")
    args = parser.parse_args()
    
    if not os.path.exists(args.config):
        # 🚀 盲区一修复：零配置自启 (Zero-Config Onboarding)
        example_config = 'config.example.yaml'
        if os.path.exists(example_config):
            try:
                shutil.copy2(example_config, args.config)
                logger.info(f"✨ 欢迎使用！已为您自动生成默认配置文件 '{args.config}'。")
                logger.info(f"   └── 💡 请打开该文件，填入您的 API Key 或调整文件夹路径后，再次运行本程序。")
                sys.exit(0)
            except Exception as e:
                logger.error(f"🛑 自动生成配置文件失败: {e}")
                sys.exit(1)
        else:
            logger.error(f"🛑 启动终止: 未发现配置文件 '{args.config}'，且未找到范例文件 '{example_config}'。")
            sys.exit(1)

    # 🚀 在初始化主引擎和模型加载前，单独解析系统级参数以抢占端口锁
    try:
        with open(os.path.abspath(os.path.expanduser(args.config)), 'r', encoding='utf-8') as f:
            pre_cfg = yaml.safe_load(f)
            lock_port = pre_cfg.get('system', {}).get('singleton_port', 43210)
    except Exception:
        lock_port = 43210
        
    acquire_singleton_lock(lock_port)

    # 实例化组装后的核心大引擎
    engine = IllacmeEngine(args.config)
    global_engine = engine # 挂载全局句柄防撕裂
    
    current_source_files = set()
    task_queue = []
    
    # 动态装载并发任务队列
    for route_cfg in engine.route_matrix:
        src_rel = route_cfg.get('source', '')
        prefix = route_cfg.get('prefix', '')
        abs_src = os.path.join(engine.vault_root, src_rel)
        
        if not os.path.exists(abs_src):
            logger.warning(f"路由源矩阵缺失: 无法找到映射物理目录 {abs_src}")
            continue
            
        for root, _, files in os.walk(abs_src):
            for f in files:
                if f.endswith(".md"):
                    rel_path = os.path.relpath(os.path.join(root, f), engine.vault_root).replace('\\', '/')
                    
                    if engine._is_excluded(rel_path): 
                        continue
                        
                    task_queue.append((os.path.join(root, f), prefix, src_rel))
                    current_source_files.add(rel_path)
                    engine.meta.register_document(rel_path, os.path.splitext(f)[0], route_prefix=prefix, route_source=src_rel)
                
    # 核心任务并发调度派发区 (单次 Sync 逻辑)
    if args.sync or not args.watch:
        if task_queue:
            # 🚀 [时钟探针 - 起点] 记录引擎点火的绝对时间与高精度 CPU 周期
            start_perf = time.perf_counter()
            start_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"🚀 [系统点火] 核心引擎启动 | 启动时间: {start_time_str}")

            # 🚀 语义降维：将“全栈调度系统就绪”转化为直观的算力面板
            mode_str = 'Dry-Run 安全模拟' if args.dry_run else f'物理火力: {engine.max_workers} 核同步'
            logger.info(f"🚀 [全速点火] 引擎就绪 | {mode_str} | 待处理文章: {len(task_queue)} 篇")
            
            with ThreadPoolExecutor(max_workers=engine.max_workers) as executor:
                future_to_task = {
                    executor.submit(engine.sync_document, task_path, prefix, src_rel, args.dry_run, args.force): task_path 
                    for task_path, prefix, src_rel in task_queue
                }
                
                completed_count = 0
                total_tasks = len(task_queue)
                
                # 🚀 架构级降维：设置初始打印水位线为 10%
                next_print_threshold = 10.0 
                
                for future in as_completed(future_to_task):
                    task_path = future_to_task[future]
                    completed_count += 1
                    try: 
                        future.result()
                        current_ratio = (completed_count / total_tasks) * 100
                        
                        # 🚀 防刷屏节流阀：仅在起点(第1篇)、终点(最后1篇)，或跨越 10% 整数水位线时才放行打印
                        if current_ratio >= next_print_threshold or completed_count == total_tasks or completed_count == 1:
                            logger.info(f"🔄 全局同步进度: [{completed_count}/{total_tasks}] ({current_ratio:.1f}%)")
                            
                            # 动态拔高下一个水位线，确保绝对跨度
                            while next_print_threshold <= current_ratio:
                                next_print_threshold += 10.0
                                
                    except Exception as e: 
                        logger.error(f"❌ 文章处理遇到意外故障 ({os.path.basename(task_path)}): {traceback.format_exc()}")
            
            # 1. 先强制同步一次内存元数据到磁盘，锁定最新指纹
            if not args.dry_run: 
                engine.meta.force_save() 
            
            # 2. 时钟探针 - 终点 (前置耗时结算，理顺时序，避免给用户造成管线未跑完的错觉)
            elapsed_seconds = time.perf_counter() - start_perf
            time_display = f"{elapsed_seconds:.2f} 秒" if elapsed_seconds < 60 else f"{int(elapsed_seconds // 60)} 分 {elapsed_seconds % 60:.2f} 秒"
            logger.info(f"🎉 全部文章同步动作执行完毕 | ⏱️ 阵列总耗时: {time_display}")

            # 🚀 [架构优化 13.5] 引入配置阀门，允许用户灵活接管或关闭资产审计与物理清理
            enable_audit = engine.sys_cfg.get('enable_asset_audit', True)

            if enable_audit:
                # 3. 执行资产账本的正向审计 (Forward Audit: Logical -> Physical)
                logger.info("🧹 [资产审计] 启动全量交叉验证基线管控...")
                asset_docs_count = 0
                missing_assets = []
                
                for rel_path in current_source_files:
                    doc_info = engine.meta.get_doc_info(rel_path)
                    # 遵循稀疏存储：仅当文档确实拥有 assets 且列表不为空时才介入物理统计
                    if doc_info and doc_info.get('assets'):
                        asset_docs_count += 1
                        for asset_path in doc_info['assets']:
                            # 🚀 探针防偏航校准：资产已由管线重命名并输出至前端目录，必须校验前端资产库的真实落盘情况
                            abs_asset_path = os.path.join(engine.paths['assets'], asset_path)
                            # 强校验：比对账本中的资产路径与实际物理硬盘是否存在一致性
                            if not os.path.exists(abs_asset_path):
                                missing_assets.append((rel_path, asset_path))

                logger.info(f"📊 [审计简报] 本轮参与对齐文档总数: {len(current_source_files)} 篇 | 确诊含资产文档: {asset_docs_count} 篇")

                if missing_assets:
                    logger.warning(f"⚠️ [资产断链] 警报：发现 {len(missing_assets)} 处被引用的物理资产已丢失！")
                    for doc, missing_asset in missing_assets[:5]:
                        logger.warning(f"   └── 缺链点：文档 [{doc}] 指向了不存在的 [{missing_asset}]")
                    if len(missing_assets) > 5:
                        logger.warning(f"   └── ... 等共 {len(missing_assets)} 处断链。")
                else:
                    logger.info("✨ [审计简报] 正向引用检查完美通过，物理与逻辑资产已 100% 严丝合缝。")

                # 4. 触发底层物理清理泵 (Reverse Audit & Cleanup: Physical -> Logical)
                # 将物理扫描确定的 current_source_files 白名单传给底层 GC。
                engine.gc_orphans(current_source_files, is_dry_run=args.dry_run)
                
                # 🚀 [终极自净] 触发幽灵路由清道夫，歼灭所有脱离管线的野文件
                engine.gc_ghost_nodes(is_dry_run=args.dry_run)
                
                # 再次确认存盘，锁定 GC 后的最终状态
                if not args.dry_run:
                    engine.meta.save()
            else:
                logger.info("🧹 [资产审计] 已根据配置文件 (enable_asset_audit: false) 主动跳过基线交叉验证与物理清理操作。")
            
            # 🚀 盲区二修复：故障诊断简报 (Diagnostic Summary)
            if not args.dry_run:
                send_notification("Illacme 同步完成", f"已成功同步 {len(task_queue)} 篇文章，总耗时 {time_display}")

            # 揪出本轮所有被打上空 Hash 标记的降级文件
            degraded_files = []
            for task_path, prefix, src_rel in task_queue:
                rel_path = os.path.relpath(task_path, engine.vault_root).replace('\\', '/')
                doc_info = engine.meta.get_doc_info(rel_path)
                if doc_info and doc_info.get("hash") == "":
                    degraded_files.append(rel_path)
                    
            # 🚀 诊断与结束语状态机感知重构：严丝合缝对齐命令参数
            if degraded_files:
                logger.warning(f"⚠️ [诊断简报] 发现 {len(degraded_files)} 篇文章在同步时触发了安全降级 (可能是 AI 幻觉或超时，已保留原文)。")
                logger.warning("   └── 💡 建议抽查以下文件 (下次重新启动引擎时，会自动尝试重试补全):")
                for i, df in enumerate(degraded_files[:5]):
                    logger.warning(f"       {i+1}. {df}")
                if len(degraded_files) > 5:
                    logger.warning(f"       ... 等共 {len(degraded_files)} 篇")
                
                if args.watch:
                    logger.info("👀 同步阶段结束，正在转入后台实时守护...")
                else:
                    logger.info("🛑 单次同步任务已执行完毕，引擎即将安全下线。")
            else:
                if args.watch:
                    logger.info("✨ 完美收官: 所有文章均以最高质量通过管线！正在转入后台实时守护。")
                else:
                    logger.info("✨ 完美收官: 所有文章均以最高质量通过管线！单次同步任务已执行完毕，引擎即将安全下线。")
            
        else:
            # 🚀 语义降维：提示更加清晰的检查方向
            logger.warning("⚠️ 没有找到任何 Markdown 笔记！💡 请检查 config.yaml 中的 `route_matrix` 目录配置是否正确。")

    # 看门狗实时热更探针 (Daemon 模式)
    if args.watch and HAS_WATCHDOG:
        # 🚀 语义降维：让 Watchdog 守护显得更加亲切
        logger.info(f"👀 目录监控已开启 -> 正在实时保护并监听文件夹: {engine.vault_root}")
        
        # 核心防退化重构：注入独立的热更调度池，彻底解放 FileSystemObserver 避免 I/O 拥塞
        watch_pool = ThreadPoolExecutor(max_workers=engine.max_workers)
        global_watch_pool = watch_pool
        
        class ChangeHandler(FileSystemEventHandler):
            def __init__(self):
                super().__init__()
                self._timers = {}
                self._lock = threading.Lock()
                self.debounce_delay = float(engine.sys_cfg.get('typing_idle_threshold', 5.0))
                logger.info(f"🛡️ 智能防抖引擎已挂载 | 当前静默拦截阈值: {self.debounce_delay} 秒")

            def _find_route_info_for_path(self, abs_path):
                for route_cfg in engine.route_matrix:
                    route_abs = os.path.join(engine.vault_root, route_cfg.get('source', ''))
                    if abs_path.startswith(os.path.abspath(route_abs)):
                        return route_cfg.get('prefix', ''), route_cfg.get('source', '')
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
                        fname = os.path.basename(file_path)
                        send_notification("✨ 文章已更新", f"《{fname}》已完成 AI 同步并上线")
                except Exception as e:
                    logger.error(f"⚠️ 实时同步过程发生意外崩溃: {traceback.format_exc()}")

            # 🚀 辅助方法：安全注入新资产到防撞列表
            def _add_asset(self, abs_path):
                fname = os.path.basename(abs_path)
                if fname not in engine.asset_index:
                    engine.asset_index[fname] = []
                if abs_path not in engine.asset_index[fname]:
                    engine.asset_index[fname].append(abs_path)

            # 🚀 辅助方法：从防撞列表中安全剥离废弃资产
            def _remove_asset(self, abs_path):
                fname = os.path.basename(abs_path)
                if fname in engine.asset_index and abs_path in engine.asset_index[fname]:
                    engine.asset_index[fname].remove(abs_path)
                    if not engine.asset_index[fname]: # 如果列表空了，彻底抹除这个 key
                        del engine.asset_index[fname]

            def on_created(self, event):
                if not event.is_directory:
                    if event.src_path.endswith(".md"):
                        rel_path = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                        current_source_files.add(rel_path)
                        prefix, source = self._find_route_info_for_path(event.src_path)
                        if prefix is not None and source is not None:
                            self._debounced_submit(event.src_path, prefix, source)
                    else:
                        self._add_asset(event.src_path) # 🚀 修复点

            def on_modified(self, event):
                if not event.is_directory and event.src_path.endswith(".md"):
                    rel_path = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                    current_source_files.add(rel_path) 
                    prefix, source = self._find_route_info_for_path(event.src_path)
                    if prefix is not None and source is not None:
                        self._debounced_submit(event.src_path, prefix, source)

            def on_deleted(self, event):
                if not event.is_directory:
                    if event.src_path.endswith(".md"):
                        rel_path = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                        current_source_files.discard(rel_path)
                        with self._lock:
                            if event.src_path in self._timers:
                                self._timers[event.src_path].cancel()
                                del self._timers[event.src_path]
                        if engine.sys_cfg.get('enable_asset_audit', True):
                            engine.gc_orphans(current_source_files, is_dry_run=args.dry_run)
                        if not args.dry_run: engine.meta.save()
                    else:
                        self._remove_asset(event.src_path) # 🚀 修复点

            def on_moved(self, event):
                if event.is_directory: return
                if event.src_path.endswith(".md"):
                    old_rel = os.path.relpath(event.src_path, engine.vault_root).replace('\\', '/')
                    current_source_files.discard(old_rel)
                    with self._lock:
                        if event.src_path in self._timers:
                            self._timers[event.src_path].cancel()
                            del self._timers[event.src_path]
                    if engine.sys_cfg.get('enable_asset_audit', True):
                        engine.gc_orphans(current_source_files, is_dry_run=args.dry_run)
                else:
                    self._remove_asset(event.src_path) # 🚀 修复点
                
                if hasattr(event, 'dest_path'):
                    if event.dest_path.endswith(".md"):
                        new_rel = os.path.relpath(event.dest_path, engine.vault_root).replace('\\', '/')
                        current_source_files.add(new_rel)
                        prefix, source = self._find_route_info_for_path(event.dest_path)
                        if prefix is not None and source is not None:
                            self._debounced_submit(event.dest_path, prefix, source)
                    else:
                        self._add_asset(event.dest_path) # 🚀 修复点
                
                if not args.dry_run: engine.meta.save()
                        
        observer = Observer()
        global_observer = observer
        observer.schedule(ChangeHandler(), engine.vault_root, recursive=True)
        observer.start()
        
        # 主线程进入无限休眠，维持 Daemon 生命周期
        while True: 
            time.sleep(1)