#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Sovereign Orchestrator
职责：全域主权编排中枢。负责算力派遣、稿件审计与分发任务的跨线程指挥。
🛡️ [V35.2]：工业级主权分发指挥部。
"""

import os
import time
import logging
import traceback
import requests
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from core.utils.event_bus import bus
from core.runtime.cli_bootstrap import send_notification
from core.pipeline.vault_indexer import VaultIndexer

from core.utils.tracing import tlog, Tracer
from core.logic.orchestration.task_orchestrator import global_executor, TaskPriority

def prepare_sync_tasks(engine, requested_paths=None):
    """根据路由矩阵，扫描物理目录，建立同步初始化队列"""
    current_source_files = set()
    task_queue = []

    # [V31.3] 路径列表归一化
    normalized_requests = []
    if requested_paths:
        normalized_requests = [p.replace('\\', '/').rstrip('/') for p in requested_paths]

    allowed_exts = engine.config.system.allowed_extensions
    for route_cfg in engine.route_matrix:
        src_rel = route_cfg.get('source', '')
        prefix = route_cfg.get('prefix', '')
        abs_src = os.path.join(engine.vault_root, src_rel)

        if not os.path.exists(abs_src):
            tlog.warning(f"路由源矩阵缺失: 无法找到映射物理目录 {abs_src}")
            continue

        for root, _, files in os.walk(abs_src):
            for f in files:
                if any(f.lower().endswith(ext) for ext in allowed_exts):
                    rel_path = os.path.relpath(os.path.join(root, f), engine.vault_root).replace('\\', '/')

                    # [V31.3] 多路径/目录前缀混合过滤
                    if normalized_requests:
                        match_found = False
                        for req in normalized_requests:
                            if rel_path == req or rel_path.startswith(req + '/'):
                                match_found = True
                                break
                        if not match_found:
                            continue

                    if engine._is_excluded(rel_path):
                        continue

                    task_queue.append((os.path.join(root, f), prefix, src_rel))
                    current_source_files.add(rel_path)
                    engine.meta.register_document(rel_path, os.path.splitext(f)[0], route_prefix=prefix, route_source=src_rel)

    return task_queue, current_source_files

def execute_full_sync(engine, args, task_queue, current_source_files):
    """
    核心任务并发调度派发区 (单次 Sync 逻辑)
    🚀 [架构升级 V14.3]：全面引入 Rich 工业级全息仪表盘。
    """
    if not task_queue:
        tlog.warning("⚠️ 没有找到任何 Markdown 笔记！💡 请检查 config.yaml 中的 `route_matrix` 目录配置是否正确。")
        return

    start_perf = time.perf_counter()

    # 🚀 [V12.2] 触发同步前元数据快照锁定 (Pre-Sync Checkpoint)
    if not args.dry_run:
        engine.meta.create_checkpoint("pre_sync")

    # 🚀 [V7.1] 发布引擎点火事件
    bus.emit("ENGINE_STARTED", mode="sync", dry_run=args.dry_run)

    tlog.info(f"🚀 [系统点火] 核心引擎启动 | 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 📊 状态计数器
    stats = {
        "UPDATED": 0,
        "SKIP": 0,
        "OFFLINE": 0,
        "DEGRADED": 0,
        "ERROR": 0
    }

    total_tasks = len(task_queue)

    # 🚀 [V11.2] 触发 Pre-Sync 钩子
    engine.theme_hooks.trigger("pre_sync")

    # 🚀 [V15.0] AI 批处理阶段：预先补全缺失元数据 (SEO/Slugs)
    if not engine.no_ai:
        tlog.info("🏎️ [预处理] 正在检测缺失元数据的资产...")
        engine.ai_batcher.batch_generate_seo(task_queue)

    # 🚀 [V11.0] 进度管理委托给 UI 监听器
    bus.emit("UI_PROGRESS_START", total=total_tasks, description="正在并发加工全量文档 (调度算力池)...")

    # 🚀 [V10.0] 提交任务至全局编排执行器
    future_to_task = {}
    for task_path, prefix, src_rel in task_queue:
        doc_trace_id = f"Sync:{os.path.basename(task_path)[:12]}"
        with Tracer.trace_scope(doc_trace_id):
            future = global_executor.submit(
                engine.sync_document,
                task_path, prefix, src_rel,
                args.dry_run, args.force,
                is_sandbox=getattr(args, 'sandbox', False),
                priority=TaskPriority.INGRESS,
                task_name=f"Sync-{os.path.basename(task_path)}"
            )
            future_to_task[future] = task_path

    tlog.info(f"📡 [调度中心] 已分发 {total_tasks} 个同步任务，正在等待算力集群响应...")

    def _on_task_done(future):
        bus.emit("UI_PROGRESS_ADVANCE", amount=1)

    for future in future_to_task:
        future.add_done_callback(_on_task_done)

    # 阻塞等待结果收割 (保留统计逻辑)
    for future in as_completed(future_to_task):
        task_path = future_to_task[future]
        try:
            status = future.result()
            if status in stats:
                stats[status] += 1

            # 🚀 [V11.2] 触发单文件同步完成钩子
            engine.theme_hooks.trigger("document_synced", rel_path=task_path, status=status)

        except Exception as e:
            # 🚀 [V11.0] 错误反馈通过事件广播
            bus.emit("UI_ERROR", path=task_path, error=str(e))
            tlog.error(f"❌ 文章处理故障 ({os.path.basename(task_path)}): {traceback.format_exc()}")
            stats["ERROR"] += 1

    # 🚀 [V24.6] 强制同步屏障：等待所有异步 AI/资产 任务完成，确保进度闭环
    if not engine.no_ai:
        from core.logic.orchestration.task_orchestrator import ai_executor, asset_executor
        bus.emit("UI_PROGRESS_START", total=0, description="正在收割残留 AI/资产 异步任务 (请稍候)...")
        ai_executor.wait_until_idle()
        asset_executor.wait_until_idle()

    bus.emit("UI_PROGRESS_STOP")

    # === 进度条走满结束，重新接管后续串行清理逻辑 ===
    elapsed_seconds = time.perf_counter() - start_perf
    time_display = f"{elapsed_seconds:.2f} 秒" if elapsed_seconds < 60 else f"{int(elapsed_seconds // 60)} 分 {elapsed_seconds % 60:.2f} 秒"

    # 🚀 [V16.8] 性能优化：提前抓取全量元数据快照，避免后续各模块重复扫描 DB (O(N) 陷阱)
    all_docs_snapshot = engine.meta.get_documents_snapshot()

    # 🚀 [V16.8] 生命周期解耦：点火所有下游插件 (插件内部会自行判断 dry_run)
    from core.services.post_sync import LifecycleManager
    LifecycleManager.execute_all(engine, stats, all_docs_snapshot, args)

    if not args.dry_run:
        # 5. 持久化状态与记账
        engine.meta.save()
        engine.meter.persist()

        # 🚀 [V7.1] 发布同步完成事件 (透传快照以加速 Sitemap 等第三方监听)
        bus.emit("SYNC_COMPLETED", stats=stats, engine=engine, is_dry_run=args.dry_run, all_docs_snapshot=all_docs_snapshot)

    if not args.dry_run:
        send_notification("Illacme 同步完成", f"已成功同步 {len(task_queue)} 篇文章，总耗时 {time_display}")
    else:
        tlog.info("🧪 [演练结束] Dry-run 模式下未执行物理变更。")

    degraded_files = []
    for task_path, prefix, src_rel in task_queue:
        rel_path = os.path.relpath(task_path, engine.vault_root).replace('\\', '/')
        doc_info = engine.meta.get_doc_info(rel_path)
        if doc_info and doc_info.get("hash") == "":
            degraded_files.append(rel_path)

    # 🚀 [V11.0] 诊断中心信号
    bus.emit("UI_DIAGNOSTIC_RESULTS", degraded_files=degraded_files, is_watch_mode=getattr(args, 'watch', False))
