#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler
模块职责：负责多语种任务的并发调度与执行。
🛡️ [AEL-Iter-v10.3]：支持全量 SEO 透传与渲染管线对齐。
"""

import logging
import concurrent.futures
import time
from typing import Dict, Any, List
from core.logic.block_parser import MarkdownBlockParser
from core.markup.base import MarkupBlock
from core.utils.common import TokenCounter
from core.utils.event_bus import bus
from core.utils.tracing import Tracer, tlog, SovereignCore
from core.logic.orchestration.task_orchestrator import global_executor, ai_executor, TaskPriority

class AIScheduler:
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

    @staticmethod
    def get_best_translator(engine, preferred_node: str = None):
        """🚀 [V11.0] 智能节点选择：利用 SmartRouter 决定最优算力去向"""
        if not hasattr(engine, 'smart_router'):
            from core.logic.smart_router import SmartRouter
            engine.smart_router = SmartRouter(engine)
        
        # 如果未指定首选节点，则从当前翻译器获取
        if not preferred_node:
            preferred_node = engine.translator.node_name

        best_node_name = engine.smart_router.get_best_node(preferred_node)
        
        # 如果路由器建议了不同节点，则通过工厂创建/获取
        if best_node_name != engine.translator.node_name:
            from core.logic.ai.ai_factory import TranslatorFactory
            # 注意：此处需要访问 trans_cfg，通常在 engine.config.translation
            return TranslatorFactory.create_node(best_node_name, engine.config.translation)
        
        return engine.translator

    @staticmethod
    @SovereignCore
    def dispatch_targets(engine, ctx, targets, route_prefix, route_source, force_sync, rel_path, is_dry_run, persistence_date=None, seo_data=None, priority=TaskPriority.TRANSLATION):
        """
        🚀 [V10.3] 多语言分发调度中心
        实现语种级并行，并透传全量 SEO 渲染数据。
        """
        enable_multilingual = engine.i18n.enable_multilingual
        targets = engine.i18n.targets

        if not enable_multilingual and targets:
            tlog.debug(f"🤫 [多语言跳过] {rel_path}：检测到 i18n 总闸已关闭。")
            return

        if not targets:
            return

        # 🚀 [V24.6] 算力成本预警 (统一通过 UsageMeter 执行)
        if not engine.meter.check_and_block(ctx.masked_source, [t.lang_code for t in targets], rel_path):
            tlog.warning(f"⏭️ [跳过] 文档 {rel_path} 因成本超标已被拦截。")
            ctx.ai_health_flag[0] = False
            return {}

        def _audit_translation(body, source_raw):
            """⚖️ [V24.6] 译后主权审计探针：仅校验持久化标签的生存状态"""
            import re
            # 仅提取非掩码类的双括号标签 (如主权标签)
            source_brackets = {b for b in re.findall(r'\[\[.*?\]\]', source_raw) if "MASK" not in b}
            target_brackets = set(re.findall(r'\[\[.*?\]\]', body))

            missing = source_brackets - target_brackets
            if missing:
                first_missing = list(missing)[0]
                return "SOVEREIGNTY_SHIELD", f"主权标签 {first_missing} 在译文中丢失"
            return None, None

        @Tracer.trace_context(ctx.ael_iter_id)
        def process_target(target):
            code = target.lang_code
            name = target.prompt_lang
            target_health = True

            try:
                # 🚀 [V24.5] 语义主权：获取图谱上下文 (Term Guard)
                knowledge_context = ""
                if hasattr(engine, "knowledge_graph"):
                    # 1. 优先尝试显式图谱链路
                    related = engine.knowledge_graph.get_related(ctx.rel_path, limit=3)
                    
                    # 2. 🚀 [V24.6 实时性增强] Fallback: 如果没有显式链路，利用元数据关键词进行启发式搜索
                    if not related and hasattr(ctx, "base_fm"):
                        keywords = ctx.base_fm.get("keywords", [])
                        if isinstance(keywords, str): keywords = [k.strip() for k in keywords.split(",")]
                        
                        if keywords:
                            # 搜索包含这些关键词的节点
                            found_nodes = []
                            for rid, node_data in engine.knowledge_graph.nodes.items():
                                if rid == ctx.rel_path: continue
                                node_entities = node_data.get("entities", {})
                                # 检查实体分类中是否包含关键词
                                flat_entities = [e.lower() for cat in node_entities.values() for e in cat]
                                if any(kw.lower() in flat_entities for kw in keywords):
                                    found_nodes.append({
                                        "id": rid,
                                        "title": node_data.get("title", rid),
                                        "entities": node_entities,
                                        "gist": node_data.get("gist", ""),
                                        "type": "HEURISTIC"
                                    })
                                if len(found_nodes) >= 3: break
                            related = found_nodes

                    from core.logic.ai.ai_logic_hub import AILogicHub
                    knowledge_context = AILogicHub.format_knowledge_context(related)
                    if knowledge_context:
                        tlog.debug(f"🧠 [TermGuard] 已为 {code} 注入来自 {len(related)} 个关联节点的语义背景 (模式: {'LINK' if 'HEURISTIC' not in str(related) else 'HEURISTIC'})")

                # 🚀 [V24.6] 语义主权回归：对“未屏蔽”的原始正文进行语义切片
                # 这样可以确保解析器能识别 Callouts、Headers 等结构，而不受占位符干扰。
                parser = MarkdownBlockParser()
                blocks = parser.parse(ctx.body_content)

                # 1. 准备翻译任务清单
                translated_blocks = [None] * len(blocks)
                tasks = [] # (index, block)

                for idx, block in enumerate(blocks):
                    # 基础跳过逻辑：空行或不需要翻译的块
                    if block.type == "spacer" or not block.content.strip():
                        translated_blocks[idx] = block.content
                        continue

                    # 2. 尝试从缓存读取 (Zero-Token Reuse)
                    cached_content = engine.block_cache.get_block(code, block.fingerprint)
                    if cached_content:
                        tlog.debug(f"✨ [块级缓存命中] {rel_path} | Block {idx} | {block.fingerprint[:8]}")
                        translated_blocks[idx] = cached_content
                        # 🚀 [V7.1] 发布算力节省事件
                        bus.emit(
                            "BLOCK_CACHE_HIT",
                            tokens=TokenCounter.count(block.content),
                            node_name=engine.translator.node_name,
                            provider_config=engine.translator.config
                        )
                    else:
                        tasks.append((idx, block))

                # 3. 顺序执行块级翻译 (针对本地算力环境优化，彻底杜绝嵌套并发死锁)
                if tasks:
                    # 🚀 [V11.0] 动态获取当前最佳算力节点 (支持运行时自动故障转移)
                    active_translator = AIScheduler.get_best_translator(engine)

                    # 🚀 [V24.6] 增强型语义日志：明确任务目标
                    tlog.info(f"🔗 [AI 调用开始] 🎯 任务: [{priority.name}] | 文档: {rel_path} | 目标: {code} | 节点: {active_translator.node_name}")
                    
                    for idx, block in tasks:
                        try:
                            # 🚀 [V24.6] 块级防护装甲：临时屏蔽技术实体
                            masked_content, block_masks = AILogicHub.mask_block(block.content)
                            
                            # 🚀 [V24.6] 极致追踪：在 INFO 级别暴露块的语义定性
                            block_summary = masked_content[:30].replace('\n', ' ') + "..." if len(masked_content) > 30 else masked_content.replace('\n', ' ')
                            tlog.info(f"🔍 [算力分发] Block {idx} | 类型: {block.type} | 摘要: {block_summary}")
                            
                            # 🛡️ 熔断卫士保护下的 AI 执行
                            b_result = engine.circuit_breakers["ai"].call(
                                active_translator.translate,
                                masked_content, engine.i18n.source.prompt_lang, name,
                                context_type=block.type,
                                is_dry_run=is_dry_run,
                                knowledge_context=knowledge_context, # 🚀 注入语义背景
                                priority=TaskPriority.TRANSLATION,
                                task_name=f"Block-{idx}-{code}"
                            )
                            
                            # 🚀 [V24.6] 块级护盾解除：还原被临时屏蔽的技术实体
                            if b_result:
                                b_result = AILogicHub.unmask_block(b_result, block_masks)
                                tlog.info(f"✅ [算力收割] Block {idx} ({code}) 翻译成功 | 产物长度: {len(b_result)}")
                            else:
                                tlog.warning(f"⚠️ [算力空回] Block {idx} ({code}) 返回了空内容，将回退至原文")

                            translated_blocks[idx] = b_result or block.content
                            # 持久化到缓存
                            engine.block_cache.store_block(code, block.fingerprint, translated_blocks[idx])
                        except Exception as be:
                            tlog.error(f"❌ [块级翻译故障] {rel_path} ({code}) | Block {idx}: {be}")
                            translated_blocks[idx] = block.content # 失败回退到原文
                            target_health = False

                # 4. 文档重组
                final_body = "\n".join([str(b) for b in translated_blocks])

                # 🧪 [V24.6] 专家级自愈审计阶段：仅做审计，不再执行破坏性的全量重试
                err_cat, err_msg = _audit_translation(final_body, ctx.raw_content)

                if err_cat and not is_dry_run:
                    tlog.warning(f"⚠️ [审计警告] {rel_path} ({code}) 语义完整性核验未通过: {err_msg}")
                    engine.brain.log_lesson(err_cat, err_msg, {"path": rel_path, "lang": code})
                    # [V24.6] 彻底禁用全量重试逻辑，以防止中英内容叠加幻觉
                    # target_health = False # 可选：标记为亚健康

                # 5. [V10.3] 分语种 SEO 提取 (自动驾驶模式)
                t_seo_data = {}
                if engine.seo_cfg.autopilot_enabled and not is_dry_run:
                    tlog.info(f"🏎️ [SEO Autopilot] 正在提取 {name} 版本的语义 SEO...")
                    t_seo_data, _ = engine.translator.generate_seo_metadata(final_body, name, is_dry_run)

                # 6. [V25.1] 标题与元数据翻译
                target_fm = ctx.base_fm.copy()
                if not is_dry_run:
                    source_title = target_fm.get('title', ctx.title)
                    tlog.info(f"✍️ [Title Polish] 正在为 {name} 版本润色标题...")
                    translated_title = engine.translator.translate_title(source_title, code, is_dry_run)
                    target_fm['title'] = translated_title

                    # 🚀 [V25.5] 全量元数据翻译：Tags & Category
                    if 'tags' in target_fm:
                        tlog.info(f"🏷️ [Meta Polish] 正在为 {name} 版本翻译 Tags...")
                        target_fm['tags'] = engine.translator.translate_metadata(target_fm['tags'], 'tags', code, is_dry_run)
                    
                    if 'category' in target_fm:
                        tlog.info(f"📁 [Meta Polish] 正在为 {name} 版本翻译 Category...")
                        target_fm['category'] = engine.translator.translate_metadata(target_fm['category'], 'category', code, is_dry_run)

                return (code, final_body, target_fm, t_seo_data, target_health)
            except Exception as e:
                tlog.error(f"🚨 [线程执行异常] {rel_path} ({code}): {e}")
                return (code, "", {}, {}, False)

        # 启动线程池进行 AI 调度 (语种级并行)
        from core.logic.orchestration.task_orchestrator import ai_executor
        futures = [ai_executor.submit(process_target, t, priority=priority) for t in targets]
        # 🚀 [V11.0] 收集并返回分发结果，用于元数据账本持久化
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

                        # 引入分发间隔，防止压跨前端 Docusaurus 聚合器
                        is_watch_mode = getattr(engine.meta, 'is_watch_mode', False)
                        if is_watch_mode and not is_dry_run:
                            # 🚀 [V15.8] 使用配置定义的块级翻译延迟
                            time.sleep(engine.config.system.throttle.ai_block_delay)

                        # 🚀 [V10.3] 调用分发器，透传 SEO 数据
                        engine.dispatcher.dispatch(
                            engine.asset_index, t_fm.get('title', ctx.title), ctx.slug, t_body, t_fm, rel_path,
                            t_code, route_prefix, route_source, ctx.mapped_sub_dir, ctx.masks,
                            is_dry_run, is_target=True, node_assets=ctx.node_assets,
                            node_ext_assets=ctx.node_ext_assets, node_outlinks=ctx.node_outlinks,
                            assets_lock=ctx.assets_lock, force_persistence_date=persistence_date,
                            seo_data=t_seo_data
                        )
                except Exception as e:
                    import traceback
                    tlog.error(f"🚨 [语种调度故障] {rel_path}: {e}\n{traceback.format_exc()}")
                    ctx.ai_health_flag[0] = False

        return target_results
