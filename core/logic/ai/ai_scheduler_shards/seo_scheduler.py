# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - SEO Scheduler
职责：源语种 SEO 异步生成与 AI 任务调度原子 Shard
🛡️ [AEL-Iter-v10.3]：完美恢复源语种异步任务封装
"""
from core.logic.orchestration.task_orchestrator import ai_executor, TaskPriority

class AISchedulerSeoScheduler:
    @staticmethod
    def generate_source_seo(engine, ctx, lang_name, is_dry_run, priority=TaskPriority.SEO):
        """🚀 [V34.9] 异步 SEO 生成：将源语种 SEO 任务推入 AI 算力池"""
        return ai_executor.submit(
            engine.circuit_breakers["ai"].call,
            engine.translator.generate_seo_metadata,
            ctx.masked_source, lang_name, is_dry_run,
            priority=priority,
            task_name=f"SourceSEO-{ctx.rel_path}"
        )
