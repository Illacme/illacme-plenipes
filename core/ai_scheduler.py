#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Multilingual Scheduler
模块职责：多语言 AI 并发调度中枢。
负责在主线任务外，使用线程池并行拉起多个目标语种的 AI 翻译、SEO 生成与物理分发。
🚀 [V16.4 架构重构]：彻底从 engine.py 中剥离，解耦并发调度逻辑。
"""

import os
import time
import logging
import concurrent.futures
from .utils import extract_frontmatter, sanitize_ai_response

logger = logging.getLogger("Illacme.plenipes")

class AIScheduler:
    @staticmethod
    def dispatch_targets(engine, ctx, inject_seo_fn, route_prefix, route_source, cli_force, rel_path, is_dry_run, persistence_date=None):
        """
        🚀 静态并发中枢：无情地接管所有目标语种的 AI 翻译任务并向外分发
        """
        i18n_enabled = engine.i18n.enabled
        targets = engine.i18n.targets

        if not i18n_enabled and targets:
            logger.debug(f"🤫 [多语言跳过] {rel_path}：检测到 i18n 总闸已关闭，已绕过所有目标语种翻译任务。")
            return

        if not targets:
            return

        if ctx.is_silent_edit:
            # 💡 静默模式直传
            for t in targets:
                code = t.lang_code
                if code:
                    engine.dispatcher.dispatch(
                        engine.asset_index, ctx.title, ctx.slug, ctx.masked_source,
                        ctx.base_fm.copy(), rel_path, code, route_prefix, route_source,
                        ctx.mapped_sub_dir, ctx.masks, is_dry_run, is_target=True,
                        node_assets=ctx.node_assets, node_ext_assets=ctx.node_ext_assets,
                        node_outlinks=ctx.node_outlinks, assets_lock=ctx.assets_lock,
                        force_persistence_date=persistence_date
                    )
            return

        # AI 翻译模式
        def process_target(target):
            code = target.lang_code
            if not code: 
                return None
            
            # 🚀 [V16 影子探针] 确保影子目标语言路径严格对齐
            doc_info = engine.meta.get_doc_info(rel_path)
            can_recover_from_shadow = (not cli_force and doc_info.get("source_hash") == ctx.current_hash and not ctx.is_silent_edit)
            ext = os.path.splitext(rel_path)[1].lower()
            shadow_tgt_path = engine.route_manager.resolve_physical_path(
                engine.paths['shadow'], code, route_prefix, ctx.mapped_sub_dir, ctx.slug, ext
            )
            
            if can_recover_from_shadow and os.path.exists(shadow_tgt_path):
                logger.debug(f"⚡️ [影子自愈] {rel_path} ({code}) 翻译资产已就位，物理拦截 API 请求。")
                try:
                    with open(shadow_tgt_path, 'r', encoding='utf-8') as sf:
                        s_content = sf.read()
                    s_fm, s_body = extract_frontmatter(s_content)
                    # 🚀 [V16.6 自愈引擎] 在影子恢复阶段自动剔除非法标签与碎屑词，无需 AI 参与即可修复损坏文件
                    s_body = sanitize_ai_response(s_body)
                    return (code, s_body, s_fm, True)
                except Exception as e:
                    logger.debug(f"读取影子资产失败，降级触发 AI: {e}")
            
            # --- AI 翻译流程 ---
            final_body, target_health = ctx.masked_source, True
            target_fm = ctx.base_fm.copy() 

            if target.translate_body:
                if is_dry_run:
                    final_body = f"[DRY-RUN]\n{ctx.masked_source}"
                    target_fm['title'] = f"[EN] {target_fm.get('title', '')}"
                else:
                    try:
                        target_lang_name = target.name or code
                        source_lang_name = engine.i18n.source.name or "中文"
                        
                        if engine.config.system.verbose_ai_logs:
                            logger.info(f"🌐 [AI 翻译] 正在将正文及元数据转换为目标语言 ({code})...")
                        
                        final_body = engine.translator.translate(ctx.masked_source, source_lang_name, target_lang_name)
                        
                        if target_fm.get('title'):
                            meta_prompt = f"Target: Translate this title to {target_lang_name}. Rule: Output ONLY the translated string, NO quotes, NO explanation, NO conversational filler. Title: '{target_fm['title']}'"
                            raw_title = engine.translator.translate(meta_prompt, "Auto", "Meta Title")
                            target_fm['title'] = raw_title.replace('"', '').replace('\n', '').strip()
                            
                    except Exception as e:
                        logger.warning(f"⚠️ [翻译失败] 文章 {rel_path} ({code}) 翻译过程中断: {e}")
                        target_health = False
            
            return (code, final_body, target_fm, target_health)

        # 启动线程池进行 AI 调度
        max_workers = engine.config.translation.llm_concurrency
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_target, t) for t in targets]
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    t_code, t_body, t_fm, t_health = res
                    if not t_health: 
                        ctx.ai_health_flag[0] = False
                    
                    # 🚀 [V18.6 V6] 在监控模式下引入 200ms 的分发间隔，防止压跨 Docusaurus 的 JSON 聚合器
                    is_watch_mode = getattr(engine.meta, 'is_watch_mode', False)
                    if is_watch_mode and not is_dry_run:
                        time.sleep(0.2)
                        
                    engine.dispatcher.dispatch(
                        engine.asset_index, ctx.title, ctx.slug, t_body, t_fm, rel_path,
                        t_code, route_prefix, route_source, ctx.mapped_sub_dir, ctx.masks,
                        is_dry_run, is_target=True, node_assets=ctx.node_assets,
                        node_ext_assets=ctx.node_ext_assets, node_outlinks=ctx.node_outlinks,
                        assets_lock=ctx.assets_lock, force_persistence_date=persistence_date
                    )