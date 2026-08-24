# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - Single Block Flow Executor
职责：传统单段平滑向下兼容分支、Markdown 控制字符自愈与单段重试兜底
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
"""
import re
import time
from typing import Dict, Any, List, Tuple, Optional
from core.utils.tracing import tlog
from core.logic.orchestration.task_orchestrator import TaskPriority
from core.logic.ai.ai_logic_hub import AILogicHub
from core.logic.ai.ai_scheduler_shards.dispatch_ast_guard import DispatchASTGuard


class DispatchSingleFlow:
    @staticmethod
    def translate_comment_only_block(
        block_item: Any,
        b_idx: int,
        item_rule: Any,
        style: Optional[str],
        active_translator: Any,
        source_prompt_lang: str,
        target_prompt_name: str,
        is_dry_run: bool,
        code: str,
        style_hash: str,
        engine: Any
    ) -> str:
        """
        🌟 特判：仅翻译代码注释治理执行
        """
        block_style = item_rule.style_override if item_rule and item_rule.style_override else style
        block_remedy = item_rule.prompt_override if item_rule and item_rule.prompt_override else None
        try:
            code_lines = block_item.content.splitlines()
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
                                source_prompt_lang,
                                target_prompt_name,
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
            engine.block_cache.store_block(code, block_item.fingerprint, b_result, style_hash=style_hash)
            tlog.info(f"✅ [注释收割] Block {b_idx} ({code}) 仅翻译注释成功")
            return b_result
        except Exception as ce:
            tlog.warning(f"⚠️ [代码注释治理执行失败] Block {b_idx}: {ce}，回退至全文透传。")
            return block_item.content

    @staticmethod
    def execute(
        engine: Any,
        rel_path: str,
        code: str,
        name: str,
        tasks: List[Any],
        translated_blocks: List[Any],
        style: Optional[str],
        style_hash: str,
        knowledge_context: str,
        glossary: Dict[str, Any],
        link_gov: Any,
        is_dry_run: bool,
        active_translator: Any
    ) -> Tuple[bool, Any]:
        """
        🌟 传统单段平滑向下兼容分支 (单段或 batch_size=1 / 禁用分包)
        """
        target_health = True
        for idx, block, rule in tasks:
            if getattr(engine, 'abort_sync', False):
                tlog.warning(f"🛑 [Abort] 检测到中止信号，跳过后续 Block 翻译 ({code})")
                target_health = False
                break

            block_style = style
            block_remedy = None
            if rule:
                if rule.style_override:
                    block_style = rule.style_override
                if rule.prompt_override:
                    block_remedy = rule.prompt_override

            action = rule.action if rule else "translate"

            if action == "parse_comments_only":
                translated_blocks[idx] = DispatchSingleFlow.translate_comment_only_block(
                    block, idx, rule, style, active_translator,
                    engine.i18n.source.prompt_lang, name, is_dry_run, code, style_hash, engine
                )
                continue

            # 正常单段分支
            if glossary:
                masked_glossary_content, glossary_masks = AILogicHub.mask_glossary(block.content, glossary)
            else:
                masked_glossary_content, glossary_masks = block.content, {}

            masked_content, block_masks = AILogicHub.mask_block(
                masked_glossary_content,
                translate_labels=link_gov.translate_labels if link_gov else True,
                external_mask_mode=link_gov.external_links_mask_mode if link_gov else "url_only"
            )

            stripped = re.sub(r'__B_MASK_\d+__', '', masked_content)
            stripped = re.sub(r'\[\[STB_MASK_\d+\]\]', '', stripped)
            stripped = re.sub(r'\[\[GLOS_MASK_\d+\]\]', '', stripped)
            if not re.search(r'\w', stripped):
                translated_blocks[idx] = block.content
                engine.block_cache.store_block(code, block.fingerprint, block.content, style_hash=style_hash)
                continue

            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    current_remedy = block_remedy
                    non_empty_lines = [l for l in masked_content.strip().splitlines() if l.strip()]
                    if len(non_empty_lines) > 1:
                        line_guard = f"CRITICAL: The input content has {len(non_empty_lines)} distinct lines. You MUST translate EVERY SINGLE line (including placeholder lines like '在此输入原稿内容...'). Do NOT omit, skip, or merge any lines!"
                        current_remedy = (current_remedy + "\n" + line_guard) if current_remedy else line_guard

                    if "MASK_" in masked_content:
                        mask_guard_instruction = "CRITICAL: You MUST strictly preserve all __B_MASK_N__ or MASK tags in the translated text exactly inside their parentheses, e.g. [translated_text](__B_MASK_N__). Do NOT remove or omit any __B_MASK_N__ tags!"
                        current_remedy = (current_remedy + "\n" + mask_guard_instruction) if current_remedy else mask_guard_instruction

                    if retry_count > 0:
                        warning_msg = (
                            "⚠️ [主权自愈提示]：前一轮翻译破坏了 Markdown/HTML 控制标记结构（如代码块不闭合、Wikilinks 数量不符或粗体未闭合）。"
                            "本轮请务必严格保证译文中的代码块个数、Wikilinks 链接、URL 链接、HTML 标签及粗体标记的个数与闭合性同原文完全一致！"
                        )
                        current_remedy = (current_remedy + "\n" + warning_msg) if current_remedy else warning_msg

                    b_result = engine.circuit_breakers["ai"].call(
                        active_translator.translate,
                        masked_content, engine.i18n.source.prompt_lang, name,
                        context_type=block.type,
                        is_dry_run=is_dry_run,
                        knowledge_context=knowledge_context,
                        style=block_style,
                        remedy_instruction=current_remedy,
                        priority=TaskPriority.TRANSLATION,
                        task_name=f"Block-{idx}-{code}"
                    )
                    if b_result:
                        b_result = AILogicHub.clean_translation_response(b_result)
                        b_result = AILogicHub.unmask_block(b_result, block_masks)
                        if glossary_masks:
                            b_result = AILogicHub.unmask_glossary(b_result, glossary_masks)

                        # 标题清洗与断行自愈
                        b_result = re.sub(r'^\s*###\s*(?:Çeviri|Translation|Translate|Çevirisi|İçəridən|İçerik|Content|翻译)\s*###\s*', '', b_result, flags=re.IGNORECASE)
                        b_result = re.sub(r'^\s*(?:Çeviri|Translation|Translate|Çevirisi|İçəridən|İçerik|Content|翻译)\s*(?:###|:|：|\n)\s*', '', b_result, flags=re.IGNORECASE)
                        b_result = re.sub(r'(?:Çeviri|Translation|Translate|Çevirisi|İçəridən|İçerik|Content|翻译)\s*###\s*', '', b_result, flags=re.IGNORECASE)
                        b_result = re.sub(r'([^\n#])\s*(#{1,6}\s+)', r'\1\n\n\2', b_result)
                        b_result = re.sub(r'^(#{1,6}\s+.*?)\n([^\n#])', r'\1\n\n\2', b_result, flags=re.MULTILINE)
                        b_result = b_result.strip()

                        # 触发语法树结构校验
                        is_valid, err_detail = DispatchASTGuard.validate_block_structure(block.content, b_result)
                        if not is_valid:
                            raise ValueError(f"Markdown 语法结构断裂：{err_detail}")

                        translated_blocks[idx] = b_result
                        src_lcode = getattr(getattr(engine, 'i18n', None), 'source', None) and getattr(engine.i18n.source, 'lang_code', 'zh')
                        is_chinese_fallback = (code != src_lcode and re.search(r'[\u4e00-\u9fa5]', b_result) and not re.search(r'[\u4e00-\u9fa5]', block.content))
                        if not is_chinese_fallback:
                            engine.block_cache.store_block(code, block.fingerprint, b_result, style_hash=style_hash)
                    else:
                        translated_blocks[idx] = block.content
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
                            time.sleep(1.0)
                    else:
                        tlog.error(f"❌ [块级翻译彻底故障] {rel_path} ({code}) | Block {idx} 在重试 {max_retries} 次后依然失败。")
                        target_health = False
                        translated_blocks[idx] = block.content

        return target_health, active_translator
