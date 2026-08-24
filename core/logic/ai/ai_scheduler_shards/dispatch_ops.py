# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - Dispatch Operations (Central Hub)
职责：多语言并行分发调度中枢、并发管理与主权分发协调
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
"""
import concurrent.futures
import time
from typing import Dict, Any, List, Optional, Tuple

from core.utils.tracing import Tracer, tlog
from core.utils.language_hub import LanguageHub
from core.logic.orchestration.task_orchestrator import ai_executor, TaskPriority
from core.logic.ai.ai_scheduler_shards.dispatch_ast_guard import DispatchASTGuard
from core.logic.ai.ai_scheduler_shards.dispatch_target_runner import DispatchTargetRunner


class AISchedulerDispatchOps:
    @staticmethod
    def validate_block_structure(source: str, translated: str) -> Tuple[bool, str]:
        """
        🛡️ [P4] 块级 AST 结构守恒核验防线 (委派至 DispatchASTGuard)
        """
        return DispatchASTGuard.validate_block_structure(source, translated)

    @staticmethod
    def dispatch_targets(
        engine: Any,
        ctx: Any,
        targets: Optional[List[Any]],
        route_prefix: str,
        route_source: Optional[str],
        force_sync: bool,
        rel_path: str,
        is_dry_run: bool,
        persistence_date: Optional[str] = None,
        seo_data: Optional[Dict[str, Any]] = None,
        priority: TaskPriority = TaskPriority.TRANSLATION,
        target_slot: str = "docs",
        target_langs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        🚀 [V10.3] 多语言分发调度中心
        实现语种级并行，并透传全量 SEO 渲染数据。
        """
        targets = targets or engine.i18n.targets
        if target_langs:
            targets = [t for t in targets if t.lang_code in target_langs]

        from core.governance.license_guard import LicenseGuard
        if not LicenseGuard.is_pro_feature_allowed("subfolder_ingress") and route_prefix != "":
            tlog.warning(f"🛡️ [License Guard] 社区版限制：拦截分发路由前缀 [{route_prefix}]，强制回归根目录。")
            route_prefix = ""
        if not engine.i18n.enabled and engine.i18n.targets:
            tlog.debug(f"🤫 [多语言跳过] {rel_path}：检测到 i18n 总闸已关闭。")
            return {}
        if not engine.i18n.targets:
            return {}

        source_lang = engine.i18n.source.lang_code
        if source_lang == "auto":
            detect_sample = ctx.raw_content[:2000] if ctx.raw_content else (ctx.masked_source[:1000] if ctx.masked_source else ctx.body_content[:1000])
            source_lang = LanguageHub.detect_source_lang(detect_sample, engine.translator)
            tlog.info(f"🔍 [语种智感] 自动探测结果: {source_lang} (Source: Auto)")
        else:
            tlog.debug(f"ℹ️ [语种固定] 使用显式源语种: {source_lang}")

        if not engine.meter.check_and_block(ctx.masked_source, [t.lang_code for t in engine.i18n.targets], rel_path):
            tlog.warning(f"⏭️ [跳过] 文档 {rel_path} 因成本超标已被拦截。")
            ctx.ai_health_flag[0] = False
            return {}

        route_style = None
        if LicenseGuard.is_pro_feature_allowed("multi_dialect"):
            for item in engine.config.route_matrix:
                if getattr(item, 'source', None) == route_source:
                    route_style = getattr(item, 'style', None)
                    break
        else:
            tlog.debug(f"🛡️ [License Guard] 社区版限制：忽略频道 [{route_source}] 风格偏移")

        @Tracer.trace_context(ctx.ael_iter_id)
        def process_target(target: Any) -> Tuple[str, str, Dict[str, Any], Dict[str, Any], bool]:
            return DispatchTargetRunner.process_target(
                engine, ctx, target, route_style, source_lang,
                rel_path, force_sync, is_dry_run, seo_data,
                priority, target_langs
            )

        llm_concurrency = 1
        if hasattr(engine, 'config') and engine.config:
            translation_cfg = getattr(engine.config, 'translation', None)
            if translation_cfg:
                val = getattr(translation_cfg, 'llm_concurrency', 1)
                if isinstance(val, (int, float)):
                    llm_concurrency = int(val)

        if llm_concurrency <= 1:
            # 🛡️ 架构纯化：AI 任务统一提交至 ai_executor 以遵守 ai_workers 并发限制
            futures = [concurrent.futures.Future() for _ in targets]

            def serial_executor_task(targets_list: List[Any], futures_list: List[Any]) -> None:
                for t_item, f_item in zip(targets_list, futures_list):
                    if getattr(engine, 'abort_sync', False):
                        f_item.cancel()
                        continue
                    try:
                        res = process_target(t_item)
                        if not f_item.cancelled():
                            f_item.set_result(res)
                    except Exception as exc:
                        try:
                            if not f_item.cancelled():
                                f_item.set_exception(exc)
                        except Exception:
                            pass
            ai_executor.submit(serial_executor_task, targets, futures, priority=priority, task_name=f"Trans-Serial-{rel_path}")
        else:
            # 🚀 [V100.3] 委托隔离算力池
            futures = [ai_executor.submit(process_target, t, priority=priority, task_name=f"Trans-{t.lang_code}-{rel_path}") for t in targets]

        target_results = {}
        for future in concurrent.futures.as_completed(futures):
            try:
                res = future.result()
                if res:
                    t_code, t_body, t_fm, t_seo_data, t_health = res
                    if not t_health:
                        ctx.ai_health_flag[0] = False

                    target_results[t_code] = {
                        "health": t_health,
                        "seo": t_seo_data
                    }

                    is_watch_mode = getattr(engine.meta, 'is_watch_mode', False)
                    if is_watch_mode and not is_dry_run:
                        time.sleep(engine.config.system.throttle.ai_block_delay)
                    if t_health:
                        engine.dispatcher.dispatch(
                            engine.asset_index, t_fm.get('title', ctx.title), ctx.slug, t_body, t_fm, rel_path,
                            t_code, route_prefix, route_source, ctx.mapped_sub_dir, ctx.masks,
                            is_dry_run, is_target=True, node_assets=ctx.node_assets,
                            node_ext_assets=ctx.node_ext_assets, node_outlinks=ctx.node_outlinks,
                            assets_lock=ctx.assets_lock, force_persistence_date=persistence_date,
                            seo_data=t_seo_data,
                            target_slot=getattr(ctx, 'target_slot', 'docs')
                        )
                    else:
                        tlog.warning(f"🛑 [主权护盾] 语种 {t_code} 翻译有故障块，拦截物理分发，防止污染。")
            except Exception as e:
                import traceback
                tlog.error(f"🚨 [语种调度故障] {rel_path}: {e}\n{traceback.format_exc()}")
                ctx.ai_health_flag[0] = False

        return target_results
