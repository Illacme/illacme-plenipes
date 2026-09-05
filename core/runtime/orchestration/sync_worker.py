# -*- coding: utf-8 -*-
"""
⚙️ Illacme Orchestration - Sync Worker (并发调度核心)
职责：负责同步任务的分发、算力集群收割及生命周期钩子触发。
🛡️ [V74.8]：实现工业级同步任务流的解耦执行。
"""

import os
import time
import traceback
from datetime import datetime
from concurrent.futures import as_completed

from core.utils.event_bus import bus
from core.utils.tracing import tlog, Tracer
from core.logic.notification_hub import send_sync_lifecycle_notification
from core.logic.orchestration.task_orchestrator import global_executor, TaskPriority

def perform_sync(engine, args, task_queue, current_source_files):
    """
    核心任务并发调度派发区 (单次 Sync 逻辑执行)
    """
    if not task_queue:
        tlog.warning("⚠️ 没有找到任何内容笔记！💡 请检查【品牌设置】中的目录映射配置是否正确。")
        return

    # 🛡️ 锁定同步状态，重置中止标志
    engine.is_syncing = True
    engine.abort_sync = False

    try:
        _perform_sync_internal(engine, args, task_queue, current_source_files)
    finally:
        engine.is_syncing = False
        engine.abort_sync = False


def _perform_sync_internal(engine, args, task_queue, current_source_files):
    # 🚀 广播启动通知
    send_sync_lifecycle_notification(engine, "START", "开始全量发布任务", f"同步队列中包含 {len(task_queue)} 篇文档。")

    # 🛡️ [V76.8] 翻译矩阵与算力可用性强关联校验熔断门禁
    i18n = engine.config.i18n_settings
    if i18n and i18n.enabled and i18n.targets:
        if engine.no_ai:
            tlog.warning("⚠️ [离线运行] 翻译矩阵已开启，且系统当前处于 NO-AI 模式，将以离线降级模式直出物理文件（未翻译块复用原文）。")
            bus.emit("UI_TERMINAL_DATA", type="LOG", data="⚠️ [离线运行] 翻译矩阵已开启，且系统当前处于 NO-AI 模式，将以离线降级模式直出物理文件（未翻译块复用原文）。")
        else:
            from core.governance.checks.ai import AIChecker
            ai_report = AIChecker.check(engine)
            if ai_report.get("status") == "FAIL":
                err_msg = "、".join(ai_report.get("details", []))
                tlog.error(f"🛑 [发布拦截] 翻译矩阵已开启，但 AI 算力网关诊断失败: {err_msg}")
                bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"🛑 [发布拦截] 翻译矩阵已开启，但 AI 算力不可用，发布已物理熔断！故障详情: {err_msg}")
                send_sync_lifecycle_notification(engine, "FAIL", "发布物理熔断", f"翻译矩阵已开启，但 AI 算力网关诊断失败: {err_msg}")
                raise RuntimeError(f"翻译矩阵已开启，但 AI 算力不可用。诊断详情: {err_msg}")

    start_perf = time.perf_counter()

    # 1. 触发同步前元数据快照锁定 (Checkpoint)
    if not args.dry_run:
        engine.meta.create_checkpoint("pre_sync")

    # 2. 发布启动事件
    bus.emit("ENGINE_STARTED", mode="sync", dry_run=args.dry_run)
    tlog.info(f"🚀 [系统点火] 核心引擎启动 | 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    stats = {"UPDATED": 0, "SKIP": 0, "OFFLINE": 0, "DEGRADED": 0, "ERROR": 0}
    total_tasks = len(task_queue)

    # 3. 触发主题钩子与 AI 预处理
    engine.theme_hooks.trigger("pre_sync")
    if not engine.no_ai:
        tlog.info("🏎️ [预处理] 正在检测缺失元数据的资产...")
        engine.ai_batcher.batch_generate_seo(task_queue)

    # 4. 进度管理与任务分发
    bus.emit("UI_PROGRESS_START", total=total_tasks, description="正在并发加工全量文档 (调度算力池)...")

    future_to_task = {}
    for task_path, prefix, src_rel, target_slot in task_queue:
        doc_trace_id = f"Sync:{os.path.basename(task_path)[:12]}"
        with Tracer.trace_scope(doc_trace_id):
            future = global_executor.submit(
                engine.sync_document,
                task_path, prefix, src_rel,
                args.dry_run, args.force,
                is_sandbox=getattr(args, 'sandbox', False),
                priority=TaskPriority.INGRESS,
                task_name=f"Sync-{os.path.basename(task_path)}",
                target_slot=target_slot,
                target_langs=getattr(args, 'target_langs', None),
                clear_cache=getattr(args, 'clean', False)
            )
            future_to_task[future] = task_path

    tlog.info(f"📡 [调度中心] 已分发 {total_tasks} 个同步任务，正在等待算力集群响应...")

    def _on_task_done(future):
        bus.emit("UI_PROGRESS_ADVANCE", amount=1)

    for future in future_to_task:
        future.add_done_callback(_on_task_done)

    # 5. 阻塞收割与结果统计
    for future in as_completed(future_to_task):
        # 🛡️ [Abort] 协同中止检测
        if getattr(engine, "abort_sync", False):
            tlog.warning("🛑 [同步中止] 感应到用户手动中止指令，正在紧急取消后续任务...")
            for f in future_to_task:
                if not f.done():
                    f.cancel()
            break

        task_path = future_to_task[future]
        try:
            status = future.result()
            if status in stats:
                stats[status] += 1
            engine.theme_hooks.trigger("document_synced", rel_path=task_path, status=status)
        except Exception as e:
            if getattr(engine, "abort_sync", False):
                break
            bus.emit("UI_ERROR", path=task_path, error=str(e))
            tlog.error(f"❌ 文章处理故障 ({os.path.basename(task_path)}): {traceback.format_exc()}")
            stats["ERROR"] += 1

    # 🛡️ [Abort] 若已触发中止，立即物理熔断退出，绝不执行后续 AI 收割、图谱重建及分发插件
    if getattr(engine, "abort_sync", False):
        tlog.warning("🛑 [同步中止] 发布流水线已被用户手动中止，跳过残留算力收割与全息图谱重建。")
        bus.emit("UI_PROGRESS_STOP")
        bus.emit("UI_TERMINAL_DATA", type="LOG", data="🛑 [同步中止] 发布流水线已成功停止，后续所有任务与大模型调用已全部取消。")
        send_sync_lifecycle_notification(engine, "WARN", "同步任务已中止", "用户手动中止了同步流程。")
        return

    # 6. 异步算力屏障 (AI/Assets 收割)
    if not engine.no_ai:
        from core.logic.orchestration.task_orchestrator import ai_executor, asset_executor
        bus.emit("UI_PROGRESS_START", total=0, description="正在收割残留 AI/资产 异步任务 (请稍候)...")
        ai_executor.wait_until_idle()
        asset_executor.wait_until_idle()

    bus.emit("UI_PROGRESS_STOP")

    # 🚀 [混合渐进式自愈] 在下游插件和 API 调用前，重新物理扫描并自愈更新内存中的物理双链拓扑
    from core.editorial.vault_indexer import VaultIndexer
    try:
        engine.md_index, engine.asset_index, engine.link_graph = VaultIndexer.build_indexes(
            engine.manuscript_source, config=engine.config, ledger=engine.meta
        )
        tlog.info(f"🌌 [混合图谱] 物理双链自愈扫描完成，当前物理节点数: {len(engine.link_graph)}")

        # 🪐 [混合渐进式] 构建增量星系数据并通过 EventBus 推送至 Dashboard
        batch_nodes = []
        batch_links = []
        seen_links = set()
        for rel_path, data in engine.link_graph.items():
            meta = data.get("metadata", {})
            batch_nodes.append({
                "id": rel_path,
                "title": meta.get("title") or os.path.splitext(os.path.basename(rel_path))[0],
                "val": 1.0,
                "group": "document",
                "is_skeleton": True
            })
            for target in data.get("links", []):
                resolved = engine.meta.resolve_link(target)
                if resolved:
                    target_key = resolved
                else:
                    target_key = target
                    if target not in engine.link_graph:
                        for k in engine.link_graph:
                            if os.path.basename(k) == target or os.path.splitext(os.path.basename(k))[0] == target:
                                target_key = k
                                break
                link_id = tuple(sorted([rel_path, target_key]))
                if link_id not in seen_links:
                    seen_links.add(link_id)
                    batch_links.append({
                        "source": rel_path,
                        "target": target_key,
                        "strength": 1.0,
                        "type": "wikilink",
                        "is_manual": False,
                        "is_skeleton": True
                    })
        bus.emit("KNOWLEDGE_BATCH_READY",
                 batch_index=1,
                 total_batches=1,
                 nodes=batch_nodes,
                 links=batch_links)
        tlog.info(f"📡 [混合图谱] 已推送 KNOWLEDGE_BATCH_READY: {len(batch_nodes)} 节点, {len(batch_links)} 连线")
    except Exception as ex:
        tlog.error(f"❌ [混合图谱] 物理双链自愈扫描失败: {ex}")

    # 7. 性能审计与下游生命周期
    elapsed_seconds = time.perf_counter() - start_perf
    time_display = f"{elapsed_seconds:.2f} 秒" if elapsed_seconds < 60 else f"{int(elapsed_seconds // 60)} 分 {elapsed_seconds % 60:.2f} 秒"
    
    # 🚀 [V1.2] 优先触发主题的 post_sync 生命周期钩子 (合成 index.html 网页入口与根重定向)
    engine.theme_hooks.trigger("post_sync")

    all_docs_snapshot = engine.meta.get_documents_snapshot()
    from core.services.post_sync import LifecycleManager
    # ⚡ 统一执行全量下游生命周期插件 (包括一次性全量分发 SovereignDeploymentPlugin)
    LifecycleManager.execute_all(engine, stats, all_docs_snapshot, args)

    if not args.dry_run:
        engine.meta.save()
        engine.meter.persist()
        bus.emit("SYNC_COMPLETED", stats=stats, engine=engine, is_dry_run=args.dry_run, all_docs_snapshot=all_docs_snapshot, local_only=getattr(args, 'local_only', False))
        if getattr(engine, "abort_sync", False):
            send_sync_lifecycle_notification(engine, "WARN", "同步任务已中止", f"用户手动中止了同步流程，总耗时 {time_display}")
        else:
            send_sync_lifecycle_notification(engine, "SUCCESS", "同步任务完成", f"已成功同步 {len(task_queue)} 篇文章，总耗时 {time_display}")
    else:
        tlog.info("🧪 [演练结束] Dry-run 模式下未执行物理变更。")

    # 8. 降级诊断中心
    degraded_files = []
    for task_path, _, _, _ in task_queue:
        rel_path = os.path.relpath(task_path, engine.vault_root).replace('\\', '/')
        doc_info = engine.meta.get_doc_info(rel_path)
        if doc_info and doc_info.get("hash") == "":
            degraded_files.append(rel_path)
    
    bus.emit("UI_DIAGNOSTIC_RESULTS", degraded_files=degraded_files, is_watch_mode=getattr(args, 'watch', False))
