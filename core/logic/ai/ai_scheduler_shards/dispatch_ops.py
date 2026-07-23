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
    def validate_block_structure(source: str, translated: str) -> tuple:
        """
        🛡️ [P4] 块级 AST 结构守恒核验防线
        比对原文与译文的 Markdown/HTML 控制标记的一致性与完整性。
        """
        import re
        # 1. 校验代码块数量与闭合性
        s_code = len(re.findall(r'```', source))
        t_code = len(re.findall(r'```', translated))
        if s_code % 2 == 0:
            if t_code % 2 != 0:
                return False, "译文中代码块未闭合"
            if s_code != t_code:
                return False, f"代码块数量不匹配 (原文 {s_code//2} vs 译文 {t_code//2})"
        else:
            if s_code != t_code:
                return False, f"代码块标记个数不一致 (原文 {s_code} vs 译文 {t_code})"

        # 2. 校验双链 Wikilinks 数量
        s_wiki = len(re.findall(r'\[\[.*?\]\]', source))
        t_wiki = len(re.findall(r'\[\[.*?\]\]', translated))
        if s_wiki != t_wiki:
            return False, f"双链 Wikilink 数量不匹配 (原文 {s_wiki} vs 译文 {t_wiki})"

        # 3. 校验标准 Markdown 链接数量
        s_urls = len(re.findall(r'\]\(([^)]+)\)', source))
        t_urls = len(re.findall(r'\]\(([^)]+)\)', translated))
        if s_urls != t_urls:
            return False, f"Markdown 链接数量不匹配 (原文 {s_urls} vs 译文 {t_urls})"

        # 4. 校验 HTML 标签对称性
        s_tags = len(re.findall(r'<\/?([a-zA-Z0-9]+)', source))
        t_tags = len(re.findall(r'<\/?([a-zA-Z0-9]+)', translated))
        if s_tags != t_tags:
            return False, f"HTML 标签数量不匹配 (原文 {s_tags} vs 译文 {t_tags})"

        # 5. 校验粗体/斜体闭合性
        s_bold = len(re.findall(r'\*\*|__', source))
        t_bold = len(re.findall(r'\*\*|__', translated))
        if s_bold % 2 == 0 and t_bold % 2 != 0:
            return False, "译文中粗体/斜体控制符未闭合"

        return True, ""

    @staticmethod
    def dispatch_targets(engine, ctx, targets, route_prefix, route_source, force_sync, rel_path, is_dry_run, persistence_date=None, seo_data=None, priority=TaskPriority.TRANSLATION, target_slot="docs", target_langs=None):

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

        def _audit_translation(body, source_raw):
            import re
            def normalize_wikilink(link):
                content = link.strip('[]')
                target = content.split('|')[0].strip()
                if target.lower().endswith('.md'):
                    target = target[:-3]
                elif target.lower().endswith('.markdown'):
                    target = target[:-9]
                return target.lower()

            source_raw_links = [b for b in re.findall(r'\[\[.*?\]\]', source_raw) if "MASK" not in b]
            if not source_raw_links:
                return None, None
                
            source_targets = {normalize_wikilink(b) for b in source_raw_links}
            target_raw_links = re.findall(r'\[\[.*?\]\]', body)
            target_targets = {normalize_wikilink(b) for b in target_raw_links}
            
            body_lower = body.lower()
            missing_targets = set()
            for src_target in source_targets:
                clean_src = src_target[:-3] if src_target.endswith('.md') else src_target
                if src_target not in target_targets and clean_src not in target_targets and src_target not in body_lower and clean_src not in body_lower:
                    missing_targets.add(src_target)
                    
            if missing_targets:
                return "SOVEREIGNTY_SHIELD", f"主权标签 [[{list(missing_targets)[0]}]] 在译文中丢失"
            return None, None

        route_style = None
        if LicenseGuard.is_licensed():
            for item in engine.config.route_matrix:
                if getattr(item, 'source', None) == route_source:
                    route_style = getattr(item, 'style', None)
                    break
        else:
            tlog.debug(f"🛡️ [License Guard] 社区版限制：忽略频道 [{route_source}] 风格偏移")

        @Tracer.trace_context(ctx.ael_iter_id)
        def process_target(target):
            code = target.lang_code
            name = target.prompt_lang
            target_health = True
            style = route_style

            # 🔒 [I5] 人工校对锁前置拦截：若检测到已有人工校对锁定，直接提取已锁内容并返回，绕过一切 LLM 调用与块解析
            if hasattr(engine, "meta") and engine.meta and hasattr(engine.meta, "get_doc_info"):
                doc_info = engine.meta.get_doc_info(rel_path)
                if isinstance(doc_info, dict) and type(doc_info).__name__ not in ('MagicMock', 'Mock'):
                    lang_meta = (doc_info.get("translations") or {}).get(code, {})
                    if isinstance(lang_meta, dict) and type(lang_meta).__name__ not in ('MagicMock', 'Mock'):
                        if lang_meta.get("human_approved"):
                            tlog.info(f"🔒 [I5校对锁] 检测到 {rel_path} / {code} 已被人工校对锁定，跳过 AI 自动翻译。")
                            reviewed_body = lang_meta.get("reviewed_body") or ""
                            reviewed_title = lang_meta.get("reviewed_title") or ctx.title
                            reviewed_desc = lang_meta.get("reviewed_desc")
                            t_seo_data = {}
                            if reviewed_desc:
                                t_seo_data = {"description": reviewed_desc, "keywords": []}
                            target_fm = ctx.base_fm.copy()
                            if reviewed_title:
                                target_fm['title'] = reviewed_title

                            return (code, reviewed_body, target_fm, t_seo_data, True)

            try:
                # 🚀 确定翻译风格，并计算风格指纹用于缓存防串味
                resolved_style = style or getattr(engine.config.translation, 'active_style', 'default')
                p_style = engine.config.translation.prompts
                if resolved_style:
                    from core.logic.ai.ai_factory import TranslatorFactory
                    p_style = TranslatorFactory.get_prompts_for_style(resolved_style, getattr(engine, 'imprint_id', 'default'), p_style)
                
                # 汇总 System 和 User 模板来计算哈希值（规避 Mock 污染）
                t_sys = getattr(p_style, "translate_system", "")
                t_user = getattr(p_style, "translate_user", "")
                if type(t_sys).__name__ in ('MagicMock', 'Mock'):
                    t_sys = ""
                if type(t_user).__name__ in ('MagicMock', 'Mock'):
                    t_user = ""
                
                import hashlib
                style_content = str(t_sys or "") + "\n" + str(t_user or "")
                style_hash = hashlib.md5(style_content.encode('utf-8')).hexdigest()

                knowledge_context = ""
                if hasattr(engine, "knowledge_graph"):
                    related = engine.knowledge_graph.get_related(ctx.rel_path, limit=3)
                    if not related and hasattr(ctx, "base_fm"):
                        keywords = ctx.base_fm.get("keywords", []) or []
                        if isinstance(keywords, str): keywords = [k.strip() for k in keywords.split(",")]
                        if keywords:
                            found_nodes = []
                            for rid, node_data in engine.knowledge_graph.nodes.items():
                                if rid == ctx.rel_path: continue
                                flat_entities = [e.lower() for cat in node_data.get("entities", {}).values() for e in cat]
                                if any(kw.lower() in flat_entities for kw in keywords):
                                    found_nodes.append({"id": rid, "title": node_data.get("title", rid), "entities": node_data.get("entities", {}), "gist": node_data.get("gist", ""), "type": "HEURISTIC"})
                                if len(found_nodes) >= 3: break
                            related = found_nodes
                    from core.logic.ai.ai_logic_hub import AILogicHub
                    knowledge_context = AILogicHub.format_knowledge_context(related)
                    if knowledge_context:
                        tlog.debug(f"🧠 [TermGuard] 注入 {len(related)} 节点语义背景")

                parser = MarkdownBlockParser()
                content_to_parse = ctx.masked_source if ctx.masked_source else ctx.body_content
                # 🚀 [V10.6] 出版模式与翻译管线联动：非全球模式禁用翻译，只进行物理复制 (主权透传)
                from core.config.models.governance import PublishingMode
                gov = getattr(engine.config, 'governance', None)
                publishing_mode = getattr(gov, 'publishing_mode', PublishingMode.GLOBAL) if gov else PublishingMode.GLOBAL

                if (publishing_mode in (PublishingMode.BASIC, PublishingMode.ENHANCED)
                        or LanguageHub.resolve_to_iso(source_lang) == LanguageHub.resolve_to_iso(code)):
                    tlog.info(f"⚖️ [主权透传] {rel_path} ({code})：当前出版模式为 {publishing_mode.value if publishing_mode else 'None'} 或语种一致，跳过 AI 翻译。")
                    return (code, content_to_parse, ctx.base_fm.copy(), {}, True)

                # 🌟 获取配置中的块级治理规则
                gov_cfg = getattr(engine.config.translation, "governance", None)
                block_rules = gov_cfg.block_rules if gov_cfg else {}
                bypass_patterns = gov_cfg.bypass_block_patterns if gov_cfg else []
                link_gov = gov_cfg.link_governance if gov_cfg else None

                blocks = parser.parse(content_to_parse)
                translated_blocks = [None] * len(blocks)
                tasks = []
                for idx, block in enumerate(blocks):
                    if block.type == "spacer" or not block.content.strip():
                        translated_blocks[idx] = block.content
                        continue

                    # 1. 匹配 bypass 正则表达式
                    import re
                    is_pattern_bypass = False
                    for pattern in bypass_patterns:
                        try:
                            if re.search(pattern, block.content, re.MULTILINE):
                                is_pattern_bypass = True
                                break
                        except Exception as pe:
                            tlog.warning(f"⚠️ [Bypass 正则错误] Pattern {pattern} 解析失败: {pe}")

                    if is_pattern_bypass:
                        translated_blocks[idx] = block.content
                        continue

                    # 2. 检索 Block 专属治理动作
                    rule = block_rules.get(block.type) if block_rules else None
                    action = rule.action if rule else "translate"

                    if action == "bypass":
                        translated_blocks[idx] = block.content
                        continue
                    elif action == "strip":
                        translated_blocks[idx] = ""
                        continue

                    # 🚀 [V75.13] 若指定清除缓存，则不从本地缓存中加载，强制重新发起翻译
                    cached_content = None
                    if not getattr(ctx, 'clear_cache', False):
                        cached_content = engine.block_cache.get_block(code, block.fingerprint, style_hash=style_hash)
                    if cached_content:
                        tlog.debug(f"✨ [块级缓存命中] {rel_path} | Block {idx} | {block.fingerprint[:8]} | Style: {style_hash[:8]}")
                        translated_blocks[idx] = cached_content
                        t_node_name = engine.translator.node_name if getattr(engine, 'translator', None) else "Offline"
                        t_provider_config = engine.translator.config if getattr(engine, 'translator', None) else None
                        bus.emit("BLOCK_CACHE_HIT", tokens=TokenCounter.count(block.content), node_name=t_node_name, provider_config=t_provider_config)
                    else:
                        if getattr(engine, 'no_ai', False):
                            # 🚀 [V105.0] NO-AI 离线降级模式：直接将原文作为译文填充，跳过 AI 请求
                            translated_blocks[idx] = block.content
                        else:
                            tasks.append((idx, block, rule))
                from core.logic.ai.ai_scheduler import AIScheduler
                active_translator = AIScheduler.get_best_translator(engine)

                if tasks:
                    tlog.info(f"🔗 [AI 调用开始] 🎯 任务: [{priority.name}] | 文档: {rel_path} | 目标: {code} | 节点: {active_translator.node_name}")
                    max_retries = 3
                    
                    # 获取专有名词表 (Glossary)
                    glossary = {}
                    if gov_cfg and gov_cfg.glossary:
                        glossary = gov_cfg.glossary.get(code) or gov_cfg.glossary.get("en") or {}

                    for idx, block, rule in tasks:
                        if getattr(engine, 'abort_sync', False):
                            tlog.warning(f"🛑 [Abort] 检测到中止信号，跳过后续 Block 翻译 ({code})")
                            target_health = False
                            break
                        from core.logic.ai.ai_logic_hub import AILogicHub
                        
                        # 获取该 block 对应的覆盖样式与覆盖提示词
                        block_style = style
                        block_remedy = None
                        if rule:
                            if rule.style_override: block_style = rule.style_override
                            if rule.prompt_override: block_remedy = rule.prompt_override

                        action = rule.action if rule else "translate"

                        # 🌟 仅翻译代码注释特判分支
                        if action == "parse_comments_only":
                            try:
                                code_lines = block.content.splitlines()
                                new_lines = []
                                for line in code_lines:
                                    comment_match = re.search(r'(?P<code_part>.*?)(?P<comment_symbol>//|#)(?P<comment_text>.*)', line)
                                    if comment_match:
                                        code_part = comment_match.group('code_part')
                                        symbol = comment_match.group('comment_symbol')
                                        comment_text = comment_match.group('comment_text')
                                        
                                        if comment_text.strip() and re.search(r'\w', comment_text):
                                            try:
                                                translated_text = active_translator.translate(
                                                    comment_text.strip(),
                                                    engine.i18n.source.prompt_lang,
                                                    name,
                                                    context_type="comment",
                                                    is_dry_run=is_dry_run,
                                                    style=block_style,
                                                    remedy_instruction=block_remedy
                                                )
                                                new_lines.append(f"{code_part}{symbol} {translated_text}")
                                            except Exception as te:
                                                tlog.warning(f"⚠️ [注释翻译失败]: {te}")
                                                new_lines.append(line)
                                        else:
                                            new_lines.append(line)
                                    else:
                                        new_lines.append(line)
                                
                                b_result = "\n".join(new_lines)
                                tlog.info(f"✅ [注释收割] Block {idx} ({code}) 仅翻译注释成功")
                                translated_blocks[idx] = b_result
                                engine.block_cache.store_block(code, block.fingerprint, b_result, style_hash=style_hash)
                            except Exception as ce:
                                tlog.warning(f"⚠️ [代码注释治理执行失败] Block {idx}: {ce}，回退至全文透传。")
                                translated_blocks[idx] = block.content
                            continue

                        # 🌟 正常翻译分支
                        
                        # A. 术语隔离屏蔽
                        if glossary:
                            masked_glossary_content, glossary_masks = AILogicHub.mask_glossary(block.content, glossary)
                        else:
                            masked_glossary_content, glossary_masks = block.content, {}

                        # B. 块级防护屏蔽
                        masked_content, block_masks = AILogicHub.mask_block(
                            masked_glossary_content,
                            translate_labels=link_gov.translate_labels if link_gov else True,
                            external_mask_mode=link_gov.external_links_mask_mode if link_gov else "url_only"
                        )
                        
                        # 🚀 [Optimization] Check if it's a pure mask/punctuation block to bypass LLM
                        import re
                        stripped = re.sub(r'__B_MASK_\d+__', '', masked_content)
                        stripped = re.sub(r'\[\[STB_MASK_\d+\]\]', '', stripped)
                        stripped = re.sub(r'\[\[GLOS_MASK_\d+\]\]', '', stripped)
                        if not re.search(r'\w', stripped):
                            tlog.info(f"⚡ [块级跳过] Block {idx} ({code}) 仅包含占位符/标点，跳过 AI 调用直接还原")
                            translated_blocks[idx] = block.content
                            engine.block_cache.store_block(code, block.fingerprint, block.content, style_hash=style_hash)
                            continue

                        block_summary = masked_content[:30].replace('\n', ' ') + "..." if len(masked_content) > 30 else masked_content.replace('\n', ' ')
                        tlog.info(f"🔍 [算力分发] Block {idx} | 类型: {block.type} | 摘要: {block_summary}")
                        
                        success = False
                        retry_count = 0
                        
                        while retry_count < max_retries:
                            try:
                                # 🛡️ [P4] 重试与屏蔽保护：注入结构对准与遮罩保留提示指令
                                current_remedy = block_remedy
                                if "MASK_" in masked_content:
                                    mask_guard_instruction = "CRITICAL: You MUST strictly preserve all __B_MASK_N__ or MASK tags in the translated text exactly inside their parentheses, e.g. [translated_text](__B_MASK_N__). Do NOT remove or omit any __B_MASK_N__ tags!"
                                    current_remedy = (current_remedy + "\n" + mask_guard_instruction) if current_remedy else mask_guard_instruction

                                if retry_count > 0:
                                    warning_msg = (
                                        "⚠️ [主权自愈提示]：前一轮翻译破坏了 Markdown/HTML 控制标记结构（如代码块不闭合、Wikilinks 数量不符或粗体未闭合）。"
                                        "本轮请务必严格保证译文中的代码块个数、Wikilinks 链接、URL 链接、HTML 标签及粗体标记的个数与闭合性同原文完全一致！"
                                    )
                                    current_remedy = (current_remedy + "\n" + warning_msg) if current_remedy else warning_msg

                                # 🛡️ 熔断卫士保护下的 AI 执行
                                b_result = engine.circuit_breakers["ai"].call(
                                    active_translator.translate,
                                    masked_content, engine.i18n.source.prompt_lang, name,
                                    context_type=block.type,
                                    is_dry_run=is_dry_run,
                                    knowledge_context=knowledge_context, # 🚀 注入语义背景
                                    style=block_style, # 🚀 [V55.26] 注入专属或频道级风格
                                    remedy_instruction=current_remedy, # 🚀 注入覆盖提示词
                                    priority=TaskPriority.TRANSLATION,
                                    task_name=f"Block-{idx}-{code}"
                                )
                                
                                # 🚀 [V48.3] 块级护盾解除：还原被临时屏蔽的技术实体
                                if b_result:
                                    b_result = AILogicHub.unmask_block(b_result, block_masks)
                                    # C. 术语还原
                                    if glossary_masks:
                                        b_result = AILogicHub.unmask_glossary(b_result, glossary_masks)

                                    # 🚀 [V10.5] 清洗大模型指令遵循抖动产生的分隔符残留 (如 ### Content ### 及其多语言变体)
                                    import re
                                    b_result = re.sub(r'^\s*###\s*[^#\n]+\s*###\s*\n?', '', b_result)
                                    b_result = re.sub(r'\n?\s*###\s*[^#\n]+\s*###\s*$', '', b_result)
                                    b_result = b_result.strip()
                                    
                                    # 🛡️ [P4] 触发语法树及标记结构完整性校验
                                    is_valid, err_detail = AISchedulerDispatchOps.validate_block_structure(block.content, b_result)
                                    if not is_valid:
                                        raise ValueError(f"Markdown 语法结构断裂：{err_detail}")

                                    tlog.info(f"✅ [算力收割] Block {idx} ({code}) 翻译成功 | 产物长度: {len(b_result)}")
                                    translated_blocks[idx] = b_result
                                    engine.block_cache.store_block(code, block.fingerprint, b_result, style_hash=style_hash)
                                else:
                                    tlog.warning(f"⚠️ [算力空回] Block {idx} ({code}) 返回了空内容，将回退至原文并跳过写入缓存")
                                    translated_blocks[idx] = block.content
                                success = True
                                break
                            except Exception as be:
                                retry_count += 1
                                tlog.warning(f"⚠️ [算力瞬时故障] Block {idx} ({code}) 尝试 {retry_count}/{max_retries} 失败: {be}")
                                if retry_count < max_retries:
                                    from core.logic.ai.model_intelligence import ModelIntelligenceHub
                                    ModelIntelligenceHub.record_failure(active_translator.node_name, reason=str(be))
                                    failover_node = None
                                    strategy = getattr(engine.config.translation, 'strategy', 'single')
                                    if strategy != 'single':
                                        if not hasattr(engine, 'smart_router'):
                                            from core.logic.smart_router import SmartRouter
                                            engine.smart_router = SmartRouter(engine)
                                        failover_node = engine.smart_router.get_failover_node(active_translator.node_name)
                                    if failover_node:
                                        tlog.warning(f"🩹 [热接力] Block {idx} ({code}) 正在从 {active_translator.node_name} 自动切换至备用算力节点 {failover_node} 进行重试...")
                                        from core.logic.ai.ai_factory import TranslatorFactory
                                        try:
                                            active_translator = TranslatorFactory._build_node(failover_node, engine.config.translation)
                                        except Exception as fe:
                                            tlog.error(f"❌ [热接力失败] 无法实例化备用节点 {failover_node}: {fe}")
                                    else:
                                        tlog.warning(f"ℹ️  未找到其他可用健康的备用算力节点，将在原节点 {active_translator.node_name} 原地退避重试。")
                                        time.sleep(1.0)
                                else:
                                    tlog.error(f"❌ [块级翻译彻底故障] {rel_path} ({code}) | Block {idx} 在重试 {max_retries} 次后依然失败。")
                                    translated_blocks[idx] = block.content
                                    target_health = False

                final_body = "\n".join([str(b) for b in translated_blocks])
                err_cat, err_msg = _audit_translation(final_body, ctx.raw_content)
                if err_cat and not is_dry_run:
                    tlog.warning(f"⚠️ [审计警告] {rel_path} ({code}) 语义完整性核验未通过: {err_msg}")
                    engine.brain.log_lesson(err_cat, err_msg, {"path": rel_path, "lang": code})
                # 🚀 优先使用新出版模式（global 模式）预先生成的译文 SEO 数据
                t_seo_data = {}
                if seo_data and "i18n_seo" in seo_data and isinstance(seo_data["i18n_seo"], dict):
                    lang_seo = seo_data["i18n_seo"].get(code)
                    if lang_seo and isinstance(lang_seo, dict):
                        # 对齐格式，转换为最终需要的 SEO 结构
                        t_seo_data = {
                            "description": lang_seo.get("description", ""),
                            "keywords": lang_seo.get("keywords", []),
                            "og_title": lang_seo.get("seo_title", "")
                        }
                        if "search_intent_note" in lang_seo:
                            t_seo_data["search_intent_note"] = lang_seo["search_intent_note"]
                        tlog.info(f"✨ [SEO] 命中新版全局模式预生成的译文 SEO 数据 ({code})")

                target_fm = ctx.base_fm.copy()

                # 🚀 [V10.5] 优先注入：如果 AI SEO 处理器产出了对应语种数据，直接反向覆盖 Frontmatter
                if t_seo_data:
                    if t_seo_data.get("description"):
                        target_fm["description"] = t_seo_data["description"]
                    if t_seo_data.get("keywords"):
                        target_fm["keywords"] = t_seo_data["keywords"]

                if not is_dry_run and not getattr(engine, 'no_ai', False):
                    source_title = target_fm.get('title', ctx.title)
                    # 🚀 [V80.0] 性能优化：如果全局预生成的 SEO 译文中已经包含了 SEO Title 或者是 og_title，直接使用该结果，跳过大模型标题润色串行调用
                    if t_seo_data and t_seo_data.get("og_title"):
                        target_fm['title'] = t_seo_data["og_title"]
                        tlog.info(f"✨ [Title Polish] 命中缓存 SEO 标题，跳过大模型润色 ({code})")
                    else:
                        tlog.info(f"✍️ [Title Polish] 正在为 {name} 版本润色标题...")
                        translated_title = engine.circuit_breakers["ai"].call(
                            active_translator.translate_title,
                            source_title, code, is_dry_run, style=style
                        )
                        target_fm['title'] = translated_title
                    
                    if 'tags' in target_fm:
                        # 🚀 [V80.0] 性能优化：若有预生成 SEO 缓存，说明此篇已在缓存层闭环，不再高频翻译 Tags
                        if t_seo_data:
                            tlog.info(f"✨ [Meta Polish] 命中缓存，跳过 Tags 大模型翻译 ({code})")
                        else:
                            tlog.info(f"🏷️ [Meta Polish] 正在为 {name} 版本翻译 Tags...")
                            target_fm['tags'] = engine.circuit_breakers["ai"].call(
                                active_translator.translate_metadata,
                                target_fm['tags'], 'tags', code, is_dry_run, style=style
                            )

                    # 🚀 [V10.5] 翻译兜底：若 Frontmatter 仍为源语种的 description，调用翻译网关
                    if 'description' in target_fm and target_fm['description'] == ctx.base_fm.get('description'):
                        tlog.info(f"📝 [Meta Polish] 正在为 {name} 版本翻译 Description...")
                        target_fm['description'] = engine.circuit_breakers["ai"].call(
                            active_translator.translate_metadata,
                            target_fm['description'], 'description', code, is_dry_run, style=style
                        )

                    # 🚀 [V10.5] 翻译兜底：对 Keywords 进行翻译处理（支持列表与单字符串结构）
                    if 'keywords' in target_fm and target_fm['keywords'] == ctx.base_fm.get('keywords'):
                        tlog.info(f"🔑 [Meta Polish] 正在为 {name} 版本翻译 Keywords...")
                        kws = target_fm['keywords']
                        if isinstance(kws, list):
                            translated_kws = []
                            for kw in kws:
                                t_kw = engine.circuit_breakers["ai"].call(
                                    active_translator.translate_metadata,
                                    kw, 'keywords', code, is_dry_run, style=style
                                )
                                if t_kw:
                                    translated_kws.append(t_kw)
                            target_fm['keywords'] = translated_kws
                        else:
                            target_fm['keywords'] = engine.circuit_breakers["ai"].call(
                                    active_translator.translate_metadata,
                                    kws, 'keywords', code, is_dry_run, style=style
                                )
                    
                    if 'category' in target_fm:
                        # 🚀 [V80.0] 性能优化：若有预生成 SEO 缓存，说明此篇已在缓存层闭环，不再高频翻译 Category
                        if t_seo_data:
                            tlog.info(f"✨ [Meta Polish] 命中缓存，跳过 Category 大模型翻译 ({code})")
                        else:
                            tlog.info(f"📁 [Meta Polish] 正在为 {name} 版本翻译 Category...")
                            target_fm['category'] = engine.circuit_breakers["ai"].call(
                                active_translator.translate_metadata,
                                target_fm['category'], 'category', code, is_dry_run, style=style
                            )

                return (code, final_body, target_fm, t_seo_data, target_health)
            except Exception as e:
                tlog.error(f"🚨 [线程执行异常] {rel_path} ({code}): {e}")
                return (code, "", {}, {}, False)
        llm_concurrency = 1
        if hasattr(engine, 'config') and engine.config:
            translation_cfg = getattr(engine.config, 'translation', None)
            if translation_cfg:
                val = getattr(translation_cfg, 'llm_concurrency', 1)
                if isinstance(val, (int, float)):
                    llm_concurrency = int(val)
        
        if llm_concurrency <= 1:
            # 🛡️ 架构纯化：AI 任务无论并发设置如何，必须统一提交至 ai_executor 以遵守 ai_workers 并发限制。
            # 我们通过向隔离池提交一个串行包裹任务逐个填充各个 Future，达成零逃逸和串行执行。
            futures = [concurrent.futures.Future() for _ in targets]
            def serial_executor_task(targets_list, futures_list):
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
                                seo_data=t_seo_data
                            )
                        else:
                            tlog.warning(f"🛑 [主权护盾] 语种 {t_code} 翻译有故障块，拦截物理分发，防止污染。")
                except Exception as e:
                    import traceback
                    tlog.error(f"🚨 [语种调度故障] {rel_path}: {e}\n{traceback.format_exc()}")
                    ctx.ai_health_flag[0] = False

        return target_results
