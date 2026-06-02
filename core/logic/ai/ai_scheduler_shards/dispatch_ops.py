# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - Dispatch Operations
职责：多语言并行分发核心算子、块级缓存、审计与自愈原子 Shard
🛡️ [AEL-Iter-v10.3]：完美恢复多语言分发引擎与主权盾
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
from core.utils.language_hub import LanguageHub
from core.logic.orchestration.task_orchestrator import global_executor, ai_executor, TaskPriority

class AISchedulerDispatchOps:
    @staticmethod
    def dispatch_targets(engine, ctx, targets, route_prefix, route_source, force_sync, rel_path, is_dry_run, persistence_date=None, seo_data=None, priority=TaskPriority.TRANSLATION, target_slot="docs"):
        """
        🚀 [V10.3] 多语言分发调度中心
        实现语种级并行，并透传全量 SEO 渲染数据。
        """
        # 🚀 [V55.26] 语义化主权栅栏：拦截子目录分发映射
        from core.governance.license_guard import LicenseGuard
        if not LicenseGuard.is_pro_feature_allowed("subfolder_ingress") and route_prefix != "":
            tlog.warning(f"🛡️ [License Guard] 社区版限制：拦截分发路由前缀 [{route_prefix}]，强制回归根目录。")
            route_prefix = ""
        enabled = engine.i18n.enabled
        targets = engine.i18n.targets
        if not enabled and targets:
            tlog.debug(f"🤫 [多语言跳过] {rel_path}：检测到 i18n 总闸已关闭。")
            return
        if not targets:
            return
        # 🚀 [V55.0] 智能源语种探测：仅在源设置为 auto 时执行一次
        source_lang = engine.i18n.source.lang_code
        if source_lang == "auto":
            # 获取一部分文本用于探测
            detect_sample = ctx.masked_source[:1000] if ctx.masked_source else ctx.body_content[:1000]
            source_lang = LanguageHub.detect_source_lang(detect_sample, engine.translator)
            tlog.info(f"🔍 [语种智感] 自动探测结果: {source_lang} (Source: Auto)")
        else:
            tlog.debug(f"ℹ️ [语种固定] 使用显式源语种: {source_lang}")
        # 🚀 [V48.3] 算力成本预警 (统一通过 UsageMeter 执行)
        if not engine.meter.check_and_block(ctx.masked_source, [t.lang_code for t in targets], rel_path):
            tlog.warning(f"⏭️ [跳过] 文档 {rel_path} 因成本超标已被拦截。")
            ctx.ai_health_flag[0] = False
            return {}
        def _audit_translation(body, source_raw):
            """⚖️ [V48.3] 译后主权审计探针：仅校验持久化标签的生存状态"""
            import re
            # 仅提取非掩码类的双括号标签 (如主权标签)
            source_brackets = {b for b in re.findall(r'\[\[.*?\]\]', source_raw) if "MASK" not in b}
            target_brackets = set(re.findall(r'\[\[.*?\]\]', body))
            missing = source_brackets - target_brackets
            if missing:
                first_missing = list(missing)[0]
                return "SOVEREIGNTY_SHIELD", f"主权标签 {first_missing} 在译文中丢失"
            return None, None
        # 🚀 [V55.26] 路由感知的方言锚点提取
        route_style = None
        from core.governance.license_guard import LicenseGuard
        if LicenseGuard.is_licensed():
            for item in engine.config.route_matrix:
                if getattr(item, 'source', None) == route_source:
                    route_style = getattr(item, 'style', None)
                    break
        else:
            tlog.debug(f"🛡️ [License Guard] 社区版限制：忽略频道 [{route_source}] 的风格偏移，强制回归全域默认。")
        @Tracer.trace_context(ctx.ael_iter_id)
        def process_target(target):
            code = target.lang_code
            name = target.prompt_lang
            target_health = True
            # 使用提取到的路由风格，若无则保持 None (由 Mixin 决定是否降级为全局)
            style = route_style
            try:
                # 🚀 [V24.5] 语义主权：获取图谱上下文 (Term Guard)
                knowledge_context = ""
                if hasattr(engine, "knowledge_graph"):
                    # 1. 优先尝试显式图谱链路
                    related = engine.knowledge_graph.get_related(ctx.rel_path, limit=3)
                    # 2. 🚀 [V48.3 实时性增强] Fallback: 如果没有显式链路，利用元数据关键词进行启发式搜索
                    if not related and hasattr(ctx, "base_fm"):
                        keywords = ctx.base_fm.get("keywords", [])
                        if isinstance(keywords, str): keywords = [k.strip() for k in keywords.split(",")]
                        if keywords:
                            # 搜索包含这些关键词 of 节点
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
                parser = MarkdownBlockParser()
                content_to_parse = ctx.masked_source if ctx.masked_source else ctx.body_content
                # 🚀 [V55.1] 幂等性校验：如果源语种与目标语种一致，则执行“主权透传”
                # 统一 ISO 代码格式进行对比
                iso_source = LanguageHub.resolve_to_iso(source_lang)
                iso_target = LanguageHub.resolve_to_iso(code)
                if iso_source == iso_target:
                    tlog.info(f"⚖️ [主权透传] {rel_path} ({code})：源语种与目标语种一致，跳过翻译算力。")
                    # 直接模拟翻译完成的状态
                    target_fm = ctx.base_fm.copy()
                    return (code, content_to_parse, target_fm, {}, True)
                blocks = parser.parse(content_to_parse)
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
                    from core.logic.ai.ai_scheduler import AIScheduler
                    active_translator = AIScheduler.get_best_translator(engine)

                    # 🚀 [V48.3] 增强型语义日志：明确任务目标
                    tlog.info(f"🔗 [AI 调用开始] 🎯 任务: [{priority.name}] | 文档: {rel_path} | 目标: {code} | 节点: {active_translator.node_name}")
                    
                    for idx, block in tasks:
                        try:
                            # 🚀 [V48.3] 块级防护装甲：临时屏蔽技术实体
                            from core.logic.ai.ai_logic_hub import AILogicHub
                            masked_content, block_masks = AILogicHub.mask_block(block.content)
                            
                            # 🚀 [V48.3] 极致追踪：在 INFO 级别暴露块的语义定性
                            block_summary = masked_content[:30].replace('\n', ' ') + "..." if len(masked_content) > 30 else masked_content.replace('\n', ' ')
                            tlog.info(f"🔍 [算力分发] Block {idx} | 类型: {block.type} | 摘要: {block_summary}")
                            
                            # 🛡️ 熔断卫士保护下的 AI 执行
                            b_result = engine.circuit_breakers["ai"].call(
                                active_translator.translate,
                                masked_content, engine.i18n.source.prompt_lang, name,
                                context_type=block.type,
                                is_dry_run=is_dry_run,
                                knowledge_context=knowledge_context, # 🚀 注入语义背景
                                style=style, # 🚀 [V55.26] 注入频道级风格
                                priority=TaskPriority.TRANSLATION,
                                task_name=f"Block-{idx}-{code}"
                            )
                            
                            # 🚀 [V48.3] 块级护盾解除：还原被临时屏蔽的技术实体
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

                # 🧪 [V48.3] 专家级自愈审计阶段：仅做审计，不再执行破坏性的全量重试
                err_cat, err_msg = _audit_translation(final_body, ctx.raw_content)

                if err_cat and not is_dry_run:
                    tlog.warning(f"⚠️ [审计警告] {rel_path} ({code}) 语义完整性核验未通过: {err_msg}")
                    engine.brain.log_lesson(err_cat, err_msg, {"path": rel_path, "lang": code})
                    # [V48.3] 彻底禁用全量重试逻辑，以防止中英内容叠加幻觉
                    # target_health = False # 可选：标记为亚健康

                # 5. [V10.3] 分语种 SEO 提取 (自动驾驶模式)
                t_seo_data = {}
                if engine.seo_cfg.autopilot_enabled and not is_dry_run:
                    tlog.info(f"🏎️ [SEO Autopilot] 正在提取 {name} 版本的语义 SEO...")
                    t_seo_data, _ = engine.circuit_breakers["ai"].call(
                        engine.translator.generate_seo_metadata,
                        final_body, name, is_dry_run, style=style
                    )

                # 6. [V25.1] 标题与元数据翻译
                target_fm = ctx.base_fm.copy()
                if not is_dry_run:
                    source_title = target_fm.get('title', ctx.title)
                    tlog.info(f"✍️ [Title Polish] 正在为 {name} 版本润色标题...")
                    translated_title = engine.circuit_breakers["ai"].call(
                        engine.translator.translate_title,
                        source_title, code, is_dry_run, style=style
                    )
                    target_fm['title'] = translated_title

                    # 🚀 [V25.5] 全量元数据翻译：Tags & Category
                    if 'tags' in target_fm:
                        tlog.info(f"🏷️ [Meta Polish] 正在为 {name} 版本翻译 Tags...")
                        target_fm['tags'] = engine.circuit_breakers["ai"].call(
                            engine.translator.translate_metadata,
                            target_fm['tags'], 'tags', code, is_dry_run, style=style
                        )
                    
                    if 'category' in target_fm:
                        tlog.info(f"📁 [Meta Polish] 正在为 {name} 版本翻译 Category...")
                        target_fm['category'] = engine.circuit_breakers["ai"].call(
                            engine.translator.translate_metadata,
                            target_fm['category'], 'category', code, is_dry_run, style=style
                        )

                return (code, final_body, target_fm, t_seo_data, target_health)
            except Exception as e:
                tlog.error(f"🚨 [线程执行异常] {rel_path} ({code}): {e}")
                return (code, "", {}, {}, False)

        # 启动线程池进行 AI 调度 (语种级并行)
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
