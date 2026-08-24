# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - Batch Flow Executor
职责：自适应多段聚合分包、批次载荷装配、解包与局部精准拯救 (Selective Rescue)
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
"""
import re
import time
import random
from typing import Dict, Any, List, Set, Tuple, Optional
from core.utils.tracing import tlog
from core.utils.event_bus import bus
from core.logic.orchestration.task_orchestrator import TaskPriority
from core.logic.ai.ai_logic_hub import AILogicHub
from core.logic.ai.ai_scheduler_shards.batch_chunker import BatchChunker
from core.logic.ai.ai_scheduler_shards.batch_payload import BatchPayloadAssembler
from core.logic.ai.ai_scheduler_shards.batch_unpacker import BatchUnpacker
from core.logic.ai.ai_scheduler_shards.dispatch_ast_guard import DispatchASTGuard


class DispatchBatchFlow:
    @staticmethod
    def execute(
        engine: Any,
        rel_path: str,
        code: str,
        name: str,
        tasks: List[Any],
        blocks: List[Any],
        translated_blocks: List[Any],
        source_lang: str,
        style: Optional[str],
        style_hash: str,
        knowledge_context: str,
        glossary: Dict[str, Any],
        link_gov: Any,
        article_title_ctx: str,
        article_desc_ctx: str,
        context_refs_map: Dict[int, Any],
        is_dry_run: bool,
        priority: TaskPriority,
        active_translator: Any,
        valid_block_indices: Set[int],
        total_para_count: int
    ) -> Tuple[bool, Any]:
        """
        🚀 [V120.0] 出版级自适应多段聚合翻译与全景语境引擎 (Adaptive Batch Translation & Slot Barrier Hub)
        """
        target_health = True
        pending_slots = set(task[0] for task in tasks)

        batches = BatchChunker.chunk_tasks_into_batches(
            tasks,
            source_lang=source_lang,
            target_lang=code,
            active_translator=active_translator,
            config=engine.config,
            context_refs_map=context_refs_map
        )
        tlog.info(f"⚡ [聚合分包就绪] {rel_path} ({code}) 共生成 {len(batches)} 个批次，进入容灾算力分发管线")

        for batch in batches:
            if getattr(engine, 'abort_sync', False):
                tlog.warning(f"🛑 [Abort] 检测到中止信号，立即中断后续 Batch 分发 ({code})")
                target_health = False
                break

            # 🌟 特判：仅翻译代码注释特例隔离批次
            if len(batch.items) == 1 and batch.items[0].rule and getattr(batch.items[0].rule, 'action', '') == "parse_comments_only":
                from core.logic.ai.ai_scheduler_shards.dispatch_single_flow import DispatchSingleFlow
                item = batch.items[0]
                b_idx = item.block_idx
                b_result = DispatchSingleFlow.translate_comment_only_block(
                    item.block, b_idx, item.rule, style, active_translator,
                    engine.i18n.source.prompt_lang, name, is_dry_run, code, style_hash, engine
                )
                translated_blocks[b_idx] = b_result
                pending_slots.discard(b_idx)
                continue

            # 装配载荷
            payload, item_masks_map, dry_run_resp = BatchPayloadAssembler.assemble_batch_payload(
                batch,
                article_title=article_title_ctx,
                article_desc=article_desc_ctx,
                glossary=glossary,
                link_gov=link_gov,
                knowledge_context=knowledge_context,
                is_dry_run=is_dry_run
            )

            # 广播心跳
            bus.emit(
                "AI_PROGRESS_HEARTBEAT",
                rel_path=rel_path,
                lang=code,
                batch_id=batch.batch_id,
                total_batches=len(batches),
                active_node=active_translator.node_name
            )

            batch_retry = 0
            max_retries = 3

            while batch_retry < max_retries:
                try:
                    if is_dry_run:
                        batch_response = dry_run_resp
                    else:
                        batch_response = engine.circuit_breakers["ai"].call(
                            active_translator.translate,
                            payload, engine.i18n.source.prompt_lang, name,
                            context_type="batch_composite",
                            is_dry_run=is_dry_run,
                            knowledge_context=knowledge_context,
                            style=style,
                            priority=TaskPriority.TRANSLATION,
                            task_name=f"Batch-{batch.batch_id}-{code}"
                        )

                    if not batch_response:
                        raise ValueError("LLM 返回空批次响应")

                    # 解包与局部精准拯救 (Selective Rescue)
                    unpack_res = BatchUnpacker.unpack_and_rescue(
                        batch_response,
                        item_masks_map,
                        batch,
                        structure_validator=DispatchASTGuard.validate_block_structure
                    )

                    # 接纳成功的段落并落盘单段指纹缓存 (边界 7)
                    src_lcode = getattr(getattr(engine, 'i18n', None), 'source', None) and getattr(engine.i18n.source, 'lang_code', 'zh')
                    for s_idx, s_content in unpack_res.succeeded_blocks.items():
                        translated_blocks[s_idx] = s_content
                        pending_slots.discard(s_idx)
                        is_chinese_fallback = (code != src_lcode and re.search(r'[\u4e00-\u9fa5]', s_content) and not re.search(r'[\u4e00-\u9fa5]', blocks[s_idx].content))
                        if not is_chinese_fallback:
                            engine.block_cache.store_block(code, blocks[s_idx].fingerprint, s_content, style_hash=style_hash)

                    # 若存在局部漏译或断裂段落，执行单段精准拯救 (进阶 8)
                    if unpack_res.failed_items:
                        tlog.warning(f"🩹 [Selective Rescue] Batch {batch.batch_id} 成功拯救 {len(unpack_res.succeeded_blocks)} 段，正在对 {len(unpack_res.failed_items)} 个漏标/破损段落执行单段重试...")
                        for f_item in unpack_res.failed_items:
                            f_idx = f_item.block_idx
                            try:
                                single_res = engine.circuit_breakers["ai"].call(
                                    active_translator.translate,
                                    f_item.raw_text, engine.i18n.source.prompt_lang, name,
                                    context_type=f_item.block.type,
                                    is_dry_run=is_dry_run,
                                    knowledge_context=knowledge_context,
                                    style=style,
                                    priority=TaskPriority.TRANSLATION,
                                    task_name=f"Rescue-{f_idx}-{code}"
                                )
                                if single_res:
                                    single_res = AILogicHub.clean_translation_response(single_res)
                                    translated_blocks[f_idx] = single_res
                                    pending_slots.discard(f_idx)
                                    engine.block_cache.store_block(code, blocks[f_idx].fingerprint, single_res, style_hash=style_hash)
                                    tlog.info(f"✅ [局部拯救成功] Block {f_idx} ({code}) 单段补录完成")
                            except Exception as r_exc:
                                tlog.error(f"❌ [单段补录失败] Block {f_idx} ({code}): {r_exc}")

                    # 汇报实时进度
                    done_valid_count = len([i for i in valid_block_indices if translated_blocks[i] is not None])
                    if hasattr(engine, 'active_translation_progress') and (rel_path, code) in engine.active_translation_progress:
                        engine.active_translation_progress[(rel_path, code)]["translated_paras"] = min(total_para_count, done_valid_count)

                    break
                except Exception as be:
                    batch_retry += 1
                    tlog.warning(f"⚠️ [批次瞬时故障] Batch {batch.batch_id} ({code}) 尝试 {batch_retry}/{max_retries} 失败: {be}")
                    if "429" in str(be) or "rate" in str(be).lower():
                        jitter = random.uniform(0.5, 1.5)
                        time.sleep(1.0 * (2 ** batch_retry) + jitter)

                    if batch_retry < max_retries:
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
                            tlog.warning(f"🩹 [热接力] Batch {batch.batch_id} ({code}) 自动切换至备用节点 {failover_node} 进行重试...")
                            from core.logic.ai.ai_factory import TranslatorFactory
                            try:
                                active_translator = TranslatorFactory._build_node(failover_node, engine.config.translation)
                            except Exception as fe:
                                tlog.error(f"❌ [热接力失败] 无法实例化备用节点 {failover_node}: {fe}")
                        else:
                            time.sleep(1.0)
                    else:
                        tlog.error(f"❌ [批次翻译彻底故障] Batch {batch.batch_id} 重试耗尽，回退至单段兜底翻译")
                        for fb_item in batch.items:
                            f_idx = fb_item.block_idx
                            f_block = fb_item.block
                            f_rule = fb_item.rule

                            f_style = style
                            f_remedy = None
                            if f_rule:
                                if f_rule.style_override:
                                    f_style = f_rule.style_override
                                if f_rule.prompt_override:
                                    f_remedy = f_rule.prompt_override

                            if glossary:
                                f_m_glossary, f_g_masks = AILogicHub.mask_glossary(f_block.content, glossary)
                            else:
                                f_m_glossary, f_g_masks = f_block.content, {}

                            f_masked, f_b_masks = AILogicHub.mask_block(
                                f_m_glossary,
                                translate_labels=link_gov.translate_labels if link_gov else True,
                                external_mask_mode=link_gov.external_links_mask_mode if link_gov else "url_only"
                            )

                            try:
                                f_res = engine.circuit_breakers["ai"].call(
                                    active_translator.translate,
                                    f_masked, engine.i18n.source.prompt_lang, name,
                                    context_type=f_block.type,
                                    is_dry_run=is_dry_run,
                                    knowledge_context=knowledge_context,
                                    style=f_style,
                                    remedy_instruction=f_remedy,
                                    priority=TaskPriority.TRANSLATION,
                                    task_name=f"Block-{f_idx}-{code}-fallback"
                                )
                                if f_res:
                                    f_res = AILogicHub.clean_translation_response(f_res)
                                    f_res = AILogicHub.unmask_block(f_res, f_b_masks)
                                    if f_g_masks:
                                        f_res = AILogicHub.unmask_glossary(f_res, f_g_masks)

                                    f_res = re.sub(r'^\s*###\s*(?:Çeviri|Translation|Translate|Çevirisi|İçəridən|İçerik|Content|翻译)\s*###\s*', '', f_res, flags=re.IGNORECASE)
                                    f_res = re.sub(r'^\s*(?:Çeviri|Translation|Translate|Çevirisi|İçəridən|İçerik|Content|翻译)\s*(?:###|:|：|\n)\s*', '', f_res, flags=re.IGNORECASE)
                                    f_res = re.sub(r'(?:Çeviri|Translation|Translate|Çevirisi|İçəridən|İçerik|Content|翻译)\s*###\s*', '', f_res, flags=re.IGNORECASE)
                                    f_res = re.sub(r'([^\n#])\s*(#{1,6}\s+)', r'\1\n\n\2', f_res)
                                    f_res = re.sub(r'^(#{1,6}\s+.*?)\n([^\n#])', r'\1\n\n\2', f_res, flags=re.MULTILINE)
                                    f_res = f_res.strip()

                                    translated_blocks[f_idx] = f_res
                                    pending_slots.discard(f_idx)
                                    src_lcode = getattr(getattr(engine, 'i18n', None), 'source', None) and getattr(engine.i18n.source, 'lang_code', 'zh')
                                    is_chinese_fb = (code != src_lcode and re.search(r'[\u4e00-\u9fa5]', f_res) and not re.search(r'[\u4e00-\u9fa5]', f_block.content))
                                    if not is_chinese_fb:
                                        engine.block_cache.store_block(code, f_block.fingerprint, f_res, style_hash=style_hash)
                            except Exception as fe_single:
                                tlog.warning(f"⚠️ [单段兜底失败] Block {f_idx} ({code}): {fe_single}")

        # 释放 Slot Barrier 槽位校验 (边界 6)
        if pending_slots:
            for remaining_idx in list(pending_slots):
                tlog.warning(f"⚠️ [Slot Barrier 门禁拦截] Block {remaining_idx} ({code}) 未就绪，降级回退至母语原文")
                translated_blocks[remaining_idx] = blocks[remaining_idx].content
                pending_slots.discard(remaining_idx)
            target_health = False

        return target_health, active_translator
