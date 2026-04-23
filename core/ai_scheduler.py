#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Multilingual Scheduler
模块职责：多语言 AI 并发调度中枢。
负责在主线任务外，使用线程池并行拉起多个目标语种的 AI 翻译、SEO 生成与物理分发。
🚀 [Stage V6]：引入 Delta Block Engine，支持块级增量翻译与缓存复用。
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
            logger.debug(f"🤫 [多语言跳过] {rel_path}：检测到 i18n 总闸已关闭。")
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
            if not code: return None
            
            # 1. 尝试全文件级别影子恢复 (Fast Path)
            doc_info = engine.meta.get_doc_info(rel_path)
            can_recover_full = (not cli_force and doc_info.get("source_hash") == ctx.current_hash and not ctx.is_silent_edit)
            ext = os.path.splitext(rel_path)[1].lower()
            shadow_tgt_path = engine.route_manager.resolve_physical_path(
                engine.paths['shadow'], code, route_prefix, ctx.mapped_sub_dir, ctx.slug, ext
            )
            
            if can_recover_full and os.path.exists(shadow_tgt_path):
                logger.debug(f"⚡️ [文件级自愈] {rel_path} ({code}) 翻译资产已就位。")
                try:
                    with open(shadow_tgt_path, 'r', encoding='utf-8') as sf:
                        s_content = sf.read()
                    s_fm, s_body = extract_frontmatter(s_content)
                    return (code, sanitize_ai_response(s_body), s_fm, True)
                except Exception: pass

            # 2. [Stage V6] 启动增量块级翻译 (Delta Block Engine)
            final_body, target_health = "", True
            target_fm = ctx.base_fm.copy() 
            
            if target.translate_body:
                source_lang = engine.i18n.source.name or "中文"
                target_lang = target.name or code
                
                # 执行语义切片
                blocks = engine.block_parser.parse(ctx.masked_source)
                translated_blocks = []
                new_block_fingerprints = []
                
                if is_dry_run:
                    # [DRY-RUN] 模拟分片过程并存入缓存以验证增量逻辑
                    for block in blocks:
                        new_block_fingerprints.append(block.fingerprint)
                        if block.type == "spacer":
                            translated_blocks.append(block.content)
                            continue
                        
                        # 尝试模拟命中
                        cached = engine.block_cache.get_block(code, block.fingerprint)
                        if cached:
                            if engine.config.system.verbose_ai_logs:
                                logger.info(f"⚡️ [DRY-BLOCK-HIT] ({code}) [{block.fingerprint[:8]}]")
                            translated_blocks.append(cached)
                        else:
                            if engine.config.system.verbose_ai_logs:
                                logger.info(f"🆕 [DRY-BLOCK-MISS] ({code}) [{block.fingerprint[:8]}]")
                            simulated_content = f"[DRY-BLOCK-{block.type}] {block.content}"
                            translated_blocks.append(simulated_content)
                            engine.block_cache.store_block(code, block.fingerprint, simulated_content)
                    
                    final_body = "\n".join(translated_blocks)
                    engine.meta.update_doc_blocks(rel_path, new_block_fingerprints)
                    target_fm['title'] = f"[DRY] {target_fm.get('title', '')}"
                else:
                    try:
                        for block in blocks:
                            new_block_fingerprints.append(block.fingerprint)
                            
                            if block.type == "spacer":
                                translated_blocks.append(block.content)
                                continue
                            
                            cached_content = engine.block_cache.get_block(code, block.fingerprint)
                            if cached_content is not None:
                                translated_blocks.append(cached_content)
                                continue
                            
                            if engine.config.system.verbose_ai_logs:
                                logger.info(f"🌐 [AI 块级翻译] ({code}) <- {block.type} [{block.fingerprint[:8]}]")
                            
                            t_block_content = engine.translator.translate(block.content, source_lang, target_lang)
                            translated_blocks.append(t_block_content)
                            engine.block_cache.store_block(code, block.fingerprint, t_block_content)
                        
                        final_body = "\n".join(translated_blocks)
                        engine.meta.update_doc_blocks(rel_path, new_block_fingerprints)

                        # 标题翻译
                        if target_fm.get('title'):
                            meta_prompt = f"Target: Translate this title to {target_lang}. Rule: Output ONLY the translated string. Title: '{target_fm['title']}'"
                            target_fm['title'] = engine.translator.translate(meta_prompt, "Auto", "Meta Title").replace('"', '').strip()

                    except Exception as e:
                        logger.warning(f"⚠️ [块级翻译失败] {rel_path} ({code}): {e}")
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
                    
                    # 引入分发间隔，防止压跨前端 Docusaurus 聚合器
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