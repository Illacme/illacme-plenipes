# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - Target Language Runner
职责：单语种调度上下文装配、出版模式判定、块级缓存检索与管线分发串联
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
"""
import re
import hashlib
from typing import Dict, Any, List, Tuple, Optional

from core.logic.block_parser import MarkdownBlockParser
from core.markup.base import MarkupBlock
from core.utils.common import TokenCounter
from core.utils.event_bus import bus
from core.utils.tracing import tlog
from core.utils.language_hub import LanguageHub
from core.logic.orchestration.task_orchestrator import TaskPriority
from core.logic.ai.ai_scheduler_shards.dispatch_ast_guard import DispatchASTGuard
from core.logic.ai.ai_scheduler_shards.dispatch_meta_polish import DispatchMetaPolish
from core.logic.ai.ai_scheduler_shards.dispatch_batch_flow import DispatchBatchFlow
from core.logic.ai.ai_scheduler_shards.dispatch_single_flow import DispatchSingleFlow


class DispatchTargetRunner:
    @staticmethod
    def process_target(
        engine: Any,
        ctx: Any,
        target: Any,
        route_style: Optional[str],
        source_lang: str,
        rel_path: str,
        force_sync: bool,
        is_dry_run: bool,
        seo_data: Optional[Dict[str, Any]],
        priority: TaskPriority,
        target_langs: Optional[List[str]]
    ) -> Tuple[str, str, Dict[str, Any], Dict[str, Any], bool]:
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
                    if not force_sync and not getattr(ctx, 'clear_cache', False) and lang_meta.get("human_approved"):
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

            style_content = str(t_sys or "") + "\n" + str(t_user or "")
            style_hash = hashlib.md5(style_content.encode('utf-8')).hexdigest()

            knowledge_context = ""
            if hasattr(engine, "knowledge_graph"):
                related = engine.knowledge_graph.get_related(ctx.rel_path, limit=3)
                if not related and hasattr(ctx, "base_fm"):
                    keywords = ctx.base_fm.get("keywords", []) or []
                    if isinstance(keywords, str):
                        keywords = [k.strip() for k in keywords.split(",")]
                    if keywords:
                        found_nodes = []
                        for rid, node_data in engine.knowledge_graph.nodes.items():
                            if rid == ctx.rel_path:
                                continue
                            flat_entities = [e.lower() for cat in node_data.get("entities", {}).values() for e in cat]
                            if any(kw.lower() in flat_entities for kw in keywords):
                                found_nodes.append({"id": rid, "title": node_data.get("title", rid), "entities": node_data.get("entities", {}), "gist": node_data.get("gist", ""), "type": "HEURISTIC"})
                            if len(found_nodes) >= 3:
                                break
                        related = found_nodes
                from core.logic.ai.ai_logic_hub import AILogicHub
                knowledge_context = AILogicHub.format_knowledge_context(related)
                if knowledge_context:
                    tlog.debug(f"🧠 [TermGuard] 注入 {len(related)} 节点语义背景")

            parser = MarkdownBlockParser()
            content_to_parse = ctx.body_content if ctx.body_content else ctx.masked_source
            # 🚀 [V10.6] 出版模式与翻译管线联动：非全球模式禁用翻译，只进行物理复制 (主权透传)
            from core.config.models.governance import PublishingMode
            gov = getattr(engine.config, 'governance', None)
            publishing_mode = getattr(gov, 'publishing_mode', PublishingMode.GLOBAL) if gov else PublishingMode.GLOBAL

            is_explicit_force_target = bool(target_langs or force_sync or getattr(ctx, 'clear_cache', False))
            if not is_explicit_force_target and (publishing_mode in (PublishingMode.BASIC, PublishingMode.ENHANCED)
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

            # 🚀 [V105.0] 初始化全局实时翻译进度的原子字典，只统计有效正文段落，杜绝 Spacer/Header 占位误加
            if not hasattr(engine, 'active_translation_progress'):
                engine.active_translation_progress = {}

            valid_block_indices = set(
                idx for idx, b in enumerate(blocks)
                if not MarkupBlock.is_ignorable_spacer(getattr(b, 'content', ''), getattr(b, 'type', ''))
            )
            total_para_count = max(1, len(valid_block_indices))
            engine.active_translation_progress[(rel_path, code)] = {
                "translated_paras": 0,
                "total_paras": total_para_count,
                "running": True
            }

            for idx, block in enumerate(blocks):
                if block.type == "spacer" or not block.content.strip():
                    translated_blocks[idx] = block.content
                    continue

                # 1. 匹配 bypass 正则表达式
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

                # 🚀 [V75.13] 若指定清除缓存，跳过本地 Block Cache 命中，强制全量 LLM 真实重译
                cached_content = None
                if not getattr(ctx, 'clear_cache', False):
                    cached_content = engine.block_cache.get_block(code, block.fingerprint, style_hash=style_hash)
                if cached_content:
                    src_lcode = getattr(getattr(engine, 'i18n', None), 'source', None) and getattr(engine.i18n.source, 'lang_code', 'zh')
                    if code != src_lcode and re.search(r'[\u4e00-\u9fa5]', cached_content) and not re.search(r'[\u4e00-\u9fa5]', block.content):
                        tlog.warning(f"⚠️ [块级缓存防护] {rel_path} | Block {idx} ({code}) 命中残留母语脏缓存，强制作废重发 AI 翻译")
                        cached_content = None

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

                # 获取专有名词表 (Glossary)
                glossary = {}
                if gov_cfg and gov_cfg.glossary:
                    glossary = gov_cfg.glossary.get(code) or gov_cfg.glossary.get("en") or {}

                # 检查自适应分包总闸
                batch_gov = None
                if hasattr(engine.config, "translation") and hasattr(engine.config.translation, "governance"):
                    batch_gov = getattr(engine.config.translation.governance, "batch_translation", None)
                batch_enabled = getattr(batch_gov, "enabled", True) if batch_gov else True

                # Frontmatter 优先预解析大标题与描述，供正文各批次单向注入全景语境
                target_fm_preview = ctx.base_fm.copy()
                if seo_data and "i18n_seo" in seo_data and isinstance(seo_data["i18n_seo"], dict):
                    lang_seo_p = seo_data["i18n_seo"].get(code)
                    if lang_seo_p and isinstance(lang_seo_p, dict):
                        if lang_seo_p.get("seo_title"):
                            target_fm_preview['title'] = lang_seo_p["seo_title"]
                        if lang_seo_p.get("description"):
                            target_fm_preview['description'] = lang_seo_p["description"]
                article_title_ctx = target_fm_preview.get('title', ctx.title)
                article_desc_ctx = target_fm_preview.get('description', '') or ctx.base_fm.get('description', '') or ''

                # 收集相邻只读代码块/引用块作为 context_ref
                context_refs_map = {}
                for b_i, b_item in enumerate(blocks):
                    if b_item.type in ["code", "table", "blockquote"] and b_item.content.strip():
                        context_refs_map[b_i + 1] = {
                            "type": b_item.type,
                            "content": b_item.content[:500]
                        }

                if batch_enabled and len(tasks) > 1:
                    target_health, active_translator = DispatchBatchFlow.execute(
                        engine, rel_path, code, name, tasks, blocks, translated_blocks,
                        source_lang, style, style_hash, knowledge_context, glossary,
                        link_gov, article_title_ctx, article_desc_ctx, context_refs_map,
                        is_dry_run, priority, active_translator, valid_block_indices, total_para_count
                    )
                else:
                    target_health, active_translator = DispatchSingleFlow.execute(
                        engine, rel_path, code, name, tasks, translated_blocks,
                        style, style_hash, knowledge_context, glossary, link_gov,
                        is_dry_run, active_translator
                    )

            final_body = "\n".join([str(b) for b in translated_blocks])
            err_cat, err_msg = DispatchASTGuard.audit_translation(final_body, ctx.raw_content, getattr(ctx, 'masks', None))
            if err_cat and not is_dry_run:
                tlog.warning(f"⚠️ [审计警告] {rel_path} ({code}) 语义完整性核验未通过: {err_msg}")
                engine.brain.log_lesson(err_cat, err_msg, {"path": rel_path, "lang": code})

            # SEO 数据提取与元数据润色
            t_seo_data = DispatchMetaPolish.extract_seo_data(seo_data, code)
            target_fm = ctx.base_fm.copy()
            target_fm = DispatchMetaPolish.polish_metadata(
                engine, ctx, target_fm, t_seo_data, code, name,
                is_dry_run, style, translated_blocks, active_translator
            )

            # 🛡️ [V106.0] 翻译完成，清理 active_translation_progress 条目，解除 running 竞态锁
            if hasattr(engine, 'active_translation_progress'):
                engine.active_translation_progress.pop((rel_path, code), None)

            return (code, final_body, target_fm, t_seo_data, target_health)
        except Exception as e:
            tlog.error(f"🚨 [线程执行异常] {rel_path} ({code}): {e}")
            # 🛡️ [V106.0] 异常退出也必须清理 running 标记，防止死锁
            if hasattr(engine, 'active_translation_progress'):
                engine.active_translation_progress.pop((rel_path, code), None)
            return (code, "", {}, {}, False)
