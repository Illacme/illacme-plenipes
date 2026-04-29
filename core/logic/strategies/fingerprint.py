#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
from .base import BaseSyncStrategy
from core.utils.tracing import Tracer, tlog, SovereignCore
from core.utils.event_bus import bus
from core.logic.ai.ai_scheduler import AIScheduler
from core.logic.orchestration.task_orchestrator import TaskPriority

class FingerprintSyncStrategy(BaseSyncStrategy):
    """🚀 [V11.0] 指纹同步策略：基于文件哈希与影子自愈的工业级同步实现"""

    @SovereignCore
    def execute(self, rel_path, route_prefix, route_source, is_dry_run, force_sync=False, is_sandbox=False):
        from core.editorial.context import SyncContext
        from core.logic.orchestration.concurrency_controller import concurrency_controller

        engine = self.engine
        # 🚀 [V11.0] 动态计算任务优先级：根目录或索引文档享有最高调度权
        priority = TaskPriority.TRANSLATION
        index_files = engine.config.system.index_filenames
        if rel_path.lower() in index_files or "/" not in rel_path.replace("\\", "/"):
            priority = TaskPriority.CRITICAL
            tlog.info(f"💎 [优先级提升] 文档 {rel_path} 已标记为 CRITICAL 任务")

        start_time = time.time()
        success = False
        error_code = 0

        # 🧪 物理路径对齐
        abs_src_path = os.path.join(engine.paths.get('vault', '.'), rel_path)

        # 🚀 [V11.0] 初始化 SyncContext (传入绝对路径以确保物理寻址)
        ctx = SyncContext(engine, abs_src_path, route_prefix, route_source, is_dry_run, force_sync, is_sandbox=is_sandbox)

        # 🛡️ 服务注册表注入
        ctx.services.staticizer = engine.staticizer
        ctx.services.translator = engine.translator
        ctx.services.meta = engine.meta
        ctx.asset_index = engine.asset_index

        # 🚀 [V35.0] 路径指纹对齐：确保 rel_path 始终相对于 vault_root
        rel_path = ctx.rel_path


        # 🚀 [V15.5] 优先消费 Batcher 预处理的算力产物
        cached_info = engine._old_info_cache.get(rel_path)
        if cached_info and "seo_data" in cached_info:
            ctx.seo_data = cached_info["seo_data"]
            if not ctx.slug:
                ctx.slug = ctx.seo_data.get('slug')
            ctx._is_batch_hit = True
            tlog.info(f"⚡ [Batcher Hit] 已命中批处理预选产物: {rel_path}")

        try:
            # 🚀 [V10.0] 语义化继承：优先继承来自编排器的描述性 ID
            trace_id = ctx.ael_iter_id or Tracer.get_id() or Tracer.generate_id()
            ctx.ael_iter_id = trace_id
            Tracer.set_id(trace_id)

            tlog.info(f"🧬 [追踪开始] 文档: {rel_path}")
            bus.emit("SYNC_DOC_START", rel_path=rel_path, trace_id=trace_id)

            # 1. 预处理
            with open(abs_src_path, 'r', encoding='utf-8') as f:
                ctx.raw_content = f.read()

            # 2. 执行管线
            engine.pipeline.execute(ctx)
            if ctx.is_aborted:
                if ctx.is_skipped:
                    tlog.info(f"🔄 [同步跳过] 指纹未变: {rel_path}")
                    engine.janitor.mark_doc_as_fresh(rel_path)
                    success = True
                    return "SKIP"
                tlog.warning(f"⏭️ [同步中止] 管线拦截: {rel_path}")
                engine.janitor.mark_doc_as_fresh(rel_path)
                success = True
                return "SKIP"

            # 🚀 [V15.1] 幻觉护卫
            if not engine.no_ai:
                engine.qa_guard.audit_context(ctx)

            # 3. 后置阶段：SEO 注入与分发
            src_code = engine.i18n.source.lang_code or 'zh-cn'
            src_fm = ctx.base_fm.copy()

            # 🚀 [Bugfix] 影子自愈与增量跳过逻辑
            # [V16.7] 修复：必须优先查询物理账本 (engine.meta)，而不是仅依赖 AIBatcher 的临时内存缓存。
            old_info = engine.meta.get_doc_info(rel_path)
            can_recover = (not force_sync and old_info.get("source_hash") == ctx.current_hash)
            
            # 🚀 [V24.6] 物理一致性防护：不仅校验哈希，还要校验目标物理文件是否真实存在
            target_base = engine.paths.get('source_dir')
            ext = os.path.splitext(rel_path)[1].lower()
            dest_path = engine.route_manager.resolve_physical_path(target_base, src_code, ctx.route_prefix, ctx.mapped_sub_dir, ctx.slug, ext)
            
            shadow_path = engine.paths.get('shadow')
            shadow_src_path = engine.route_manager.resolve_physical_path(shadow_path, src_code, ctx.route_prefix, ctx.mapped_sub_dir, ctx.slug, ext) if shadow_path else ""
            
            dest_exists = os.path.exists(dest_path)
            if can_recover and shadow_src_path and os.path.exists(shadow_src_path) and dest_exists:
                try:
                    with open(shadow_src_path, 'r', encoding='utf-8') as sf:
                        from core.utils import extract_frontmatter
                        s_fm, _ = extract_frontmatter(sf.read())
                        ctx.seo_data = s_fm.get('seo_data') or {'description': s_fm.get('description', ''), 'keywords': s_fm.get('keywords', [])}
                except Exception: pass

                target_base = engine.paths.get('target_base', '.')
                display_dest = engine.route_manager.resolve_physical_path(target_base, src_code, ctx.route_prefix, ctx.mapped_sub_dir, ctx.slug, ext)
                tlog.info(f"🔄 [同步跳过] {rel_path} -> {os.path.relpath(display_dest, target_base)}")
                engine.janitor.mark_doc_as_fresh(rel_path)
                success = True
                return "SKIP"


            # 🚀 [V10.4] 中间件：Pre-Dispatch 钩子
            for hook in engine._hooks["pre_dispatch"]:
                hook(ctx)

            # 🚀 [V34.9] 全量异步化
            source_seo_future = None
            if not ctx.seo_data and not engine.no_ai:
                lang_name = engine.get_lang_name_by_code(src_code)
                tlog.info(f"🏎️ [SEO Autopilot] 已调度源语种 ({lang_name}) SEO 异步任务...")
                source_seo_future = AIScheduler.generate_source_seo(engine, ctx, lang_name, ctx.is_dry_run, priority=priority)

            # 🚀 [V10.3] 多语言分发
            target_results = AIScheduler.dispatch_targets(
                engine, ctx, None, ctx.route_prefix, ctx.route_source, force_sync,
                rel_path, ctx.is_dry_run, persistence_date=None,
                seo_data=ctx.seo_data, priority=priority
            )

            # 🚀 等待源语种 SEO 结果
            if source_seo_future:
                try:
                    seo_res, ok = source_seo_future.result()
                    if ok:
                        ctx.seo_data = seo_res
                        tlog.info(f"✨ [SEO Autopilot] 异步补全成功: {len(seo_res.get('keywords', []))} 个关键词")
                except Exception as e:
                    tlog.error(f"❌ [SEO Autopilot] 异步执行故障: {e}")

            # 🚀 [V10.3] 分发源语种版本
            primary_shadow_hash, persistence_date = engine.dispatcher.dispatch(
                engine.asset_index, ctx.title, ctx.slug, ctx.masked_source, src_fm, rel_path,
                src_code, ctx.route_prefix, ctx.route_source, ctx.mapped_sub_dir, ctx.masks,
                ctx.is_dry_run, is_target=True, node_assets=ctx.node_assets, node_ext_assets=ctx.node_ext_assets,
                node_outlinks=ctx.node_outlinks, assets_lock=ctx.assets_lock,
                seo_data=ctx.seo_data, is_sandbox=ctx.is_sandbox
            )


            # 🚀 [V10.4] 中间件：Post-Dispatch 钩子
            for hook in engine._hooks["post_dispatch"]:
                hook(ctx, target_results)

            # 4. 终态记录
            if not ctx.is_dry_run:
                engine.meta.register_document(ctx.rel_path, ctx.title, slug=ctx.slug, source_hash=ctx.current_hash, shadow_hash=primary_shadow_hash, seo_data=ctx.seo_data, route_prefix=ctx.route_prefix, route_source=ctx.route_source, sub_dir=ctx.mapped_sub_dir, assets=list(ctx.node_assets), ext_assets=list(ctx.node_ext_assets), outlinks=list(ctx.node_outlinks), persistent_date=persistence_date, translations=target_results)
                engine.meta.save()

                status = "UPDATED" if ctx.ai_health_flag[0] else "DEGRADED"
                engine.timeline.update_event_status(ctx.rel_path, status, f"资产: {len(ctx.node_assets)}")

                if status == "UPDATED" and not ctx.is_silent_edit:
                    engine.bus.emit("DOCUMENT_PUBLISHED", title=ctx.title, path=ctx.rel_path, lang=src_code, sub_dir=ctx.mapped_sub_dir, slug=ctx.slug)


                if hasattr(engine, 'sentinel'):
                    engine.sentinel.verify_docs_sync_hook(rel_path)

                # 🚀 [V14.0] 语义索引增量更新 (Semantic Indexing)
                if engine.embedding_adapter and not ctx.is_dry_run:
                    try:
                        # 仅对正文部分生成向量 (去除噪声)
                        from core.logic.context_compressor import ContextCompressor
                        clean_text = ContextCompressor.compress_markdown(ctx.masked_source, max_chars=1000)
                        vector = engine.embedding_adapter.get_embedding(clean_text)
                        if vector:
                            engine.vector_index.update_document(ctx.rel_path, vector)
                            engine.vector_index.save()
                    except Exception as ve:
                        tlog.warning(f"⚠️ [语义索引失败] {rel_path}: {ve}")

                success = True
                return status

            success = True
            return "UPDATED"
        except Exception as e:
            tlog.error(f"🚨 [同步引擎故障] {rel_path}: {e}")
            if "429" in str(e): error_code = 429
            raise
        finally:
            duration = time.time() - start_time
            concurrency_controller.report_result(duration, success, error_code)
