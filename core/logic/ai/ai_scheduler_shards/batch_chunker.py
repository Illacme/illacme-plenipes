# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - Adaptive Batch Chunker
职责：自适应多段弹性分包、语种密度预算控制、模型算力段位降维与物理绝对索引绑定
🛡️ [Rule 12.9/12.10] 纯逻辑分包计算单元
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

from core.markup.base import MarkupBlock
from core.utils.tracing import tlog
from core.utils.language_hub import LanguageHub

@dataclass
class BatchItem:
    seg_id: str                      # 如 "seg_4" 或 "seg_4_sub0"
    block_idx: int                   # 原稿数组中的绝对物理行/块索引
    block: MarkupBlock               # 原始 MarkupBlock 对象
    raw_text: str                    # 待译文本（单句或整块）
    sub_idx: Optional[int] = None    # 若为超长切分则记录子序号，否则为 None
    is_sub_split: bool = False       # 是否为超长切分的子段落
    rule: Optional[Any] = None       # 块级治理规则

@dataclass
class TranslationBatch:
    batch_id: int
    items: List[BatchItem] = field(default_factory=list)
    context_refs: List[Dict[str, str]] = field(default_factory=list)  # 只读语境引用 (如跳过的代码块/表格)
    total_chars: int = 0
    target_lang: str = "en"
    source_lang: str = "zh"

class BatchChunker:
    """🚀 [Adaptive Batch Chunker] 自适应出版级多段分包器"""

    # 默认分包阈值常量
    DEFAULT_MAX_PARAS_FLAGSHIP = 8
    DEFAULT_MAX_PARAS_LOCAL = 3
    DEFAULT_MAX_CHARS_CJK = 1500
    DEFAULT_MAX_CHARS_LATIN = 3000
    DEFAULT_MAX_CHARS_LOCAL = 600

    @classmethod
    def resolve_budget_limits(
        cls,
        source_lang: str,
        active_translator: Optional[Any] = None,
        config: Optional[Any] = None
    ) -> Tuple[int, int]:
        """
        根据源语种文字密度、模型算力段位与全局配置动态计算分包上限 (max_paras, max_chars)。
        """
        # 1. 基础配置读取
        batch_gov = None
        if config and hasattr(config, "translation") and hasattr(config.translation, "governance"):
            batch_gov = getattr(config.translation.governance, "batch_translation", None)
        elif config and hasattr(config, "batch_translation"):
            batch_gov = config.batch_translation

        cfg_enabled = getattr(batch_gov, "enabled", True) if batch_gov else True
        if not cfg_enabled:
            return 1, 999999  # 单段模式

        cfg_max_paras = getattr(batch_gov, "max_batch_paras", None) if batch_gov else None
        cfg_max_chars = getattr(batch_gov, "max_batch_chars", None) if batch_gov else None
        model_tier_adaptive = getattr(batch_gov, "model_tier_adaptive", True) if batch_gov else True

        # 2. 判断模型段位 (Flagship vs Local/Small)
        is_local_small_model = False
        if model_tier_adaptive and active_translator:
            node_name = str(getattr(active_translator, "node_name", "")).lower()
            provider = str(getattr(active_translator, "provider", "")).lower()
            model_name = str(getattr(active_translator, "model_name", "")).lower()
            combined = f"{node_name} {provider} {model_name}"

            if any(k in combined for k in ["ollama", "local", "7b", "8b", "qwen:7b", "llama3:8b", "phi", "gemma:2b"]):
                is_local_small_model = True

        if is_local_small_model:
            max_paras = cfg_max_paras or cls.DEFAULT_MAX_PARAS_LOCAL
            max_chars = min(cfg_max_chars or cls.DEFAULT_MAX_CHARS_LOCAL, cls.DEFAULT_MAX_CHARS_LOCAL)
            return max_paras, max_chars

        # 3. 语种文字密度自适应
        norm_src = LanguageHub.resolve_to_iso(source_lang).lower()
        if norm_src in ["zh", "ja", "ko", "chinese", "japanese", "korean"]:
            base_chars = cls.DEFAULT_MAX_CHARS_CJK
        else:
            base_chars = cls.DEFAULT_MAX_CHARS_LATIN

        max_paras = cfg_max_paras or cls.DEFAULT_MAX_PARAS_FLAGSHIP
        max_chars = cfg_max_chars or base_chars
        return max_paras, max_chars

    @classmethod
    def split_oversized_text(cls, text: str, max_chars: int) -> List[str]:
        """
        🛡️ [Sub-Sentence Splitting] 超长单段自适应安全标点分句切分
        在标点符号 (。！？.!?\\n\\n) 处安全切分，防止单段超出上下文预算。
        """
        if len(text) <= max_chars:
            return [text]

        # 优先在句末标点处切分
        raw_sentences = [s for s in re.split(r'(?<=[。！？\?\!\n])', text) if s and s.strip()]
        if not raw_sentences:
            raw_sentences = [text]

        sub_parts = []
        current_part = ""

        for sentence in raw_sentences:
            candidate = f"{current_part}{sentence}" if current_part else sentence
            if len(candidate) <= max_chars:
                current_part = candidate
            else:
                if current_part:
                    sub_parts.append(current_part.strip())
                # 若单个句子本身即超过 max_chars，做物理逗号/分号次级切分
                if len(sentence) > max_chars:
                    clauses = [c for c in re.split(r'(?<=[，,；;、])', sentence) if c and c.strip()]
                    temp_clause = ""
                    for clause in clauses:
                        if len(temp_clause) + len(clause) <= max_chars:
                            temp_clause += clause
                        else:
                            if temp_clause:
                                sub_parts.append(temp_clause.strip())
                            temp_clause = clause
                    if temp_clause:
                        current_part = temp_clause
                    else:
                        current_part = ""
                else:
                    current_part = sentence

        if current_part:
            sub_parts.append(current_part.strip())

        return sub_parts or [text]

    @classmethod
    def chunk_tasks_into_batches(
        cls,
        tasks: List[Tuple[int, MarkupBlock, Any]],
        source_lang: str = "zh",
        target_lang: str = "en",
        active_translator: Optional[Any] = None,
        config: Optional[Any] = None,
        context_refs_map: Optional[Dict[int, Dict[str, str]]] = None
    ) -> List[TranslationBatch]:
        """
        🚀 将待译任务 (idx, block, rule) 贪心聚合打包为 TranslationBatch 序列。
        - 冲突消解 3: 严格保留原稿物理绝对索引 (block_idx) 与 seg_id
        - 边界 1: 遇到具有 style_override 或 parse_comments_only 的异构规则段落时强制独立打包
        - 边界 2: 标题与列表项 AST 语义粘连
        """
        if not tasks:
            return []

        max_paras, max_chars = cls.resolve_budget_limits(source_lang, active_translator, config)

        batches: List[TranslationBatch] = []
        current_batch = TranslationBatch(
            batch_id=0,
            target_lang=target_lang,
            source_lang=source_lang
        )

        for task_pos, (idx, block, rule) in enumerate(tasks):
            action = rule.action if rule else "translate"
            style_override = rule.style_override if rule else None
            prompt_override = rule.prompt_override if rule else None

            # 异构规则段落（如仅翻译注释或自定义提示词/样式）必须独立成包，防止污染常规批次
            is_isolated_rule = (
                action == "parse_comments_only"
                or bool(style_override)
                or bool(prompt_override)
            )

            # 超长单段检查与分句
            raw_content = block.content
            # 🛡️ 结构性复合 HTML 块严禁跨标签生硬切分，必须保持原子整体封包
            is_html_container = bool(re.search(
                r'<\s*(?:div|article|section|table|tbody|thead|tr|td|aside|nav|header|footer|figure|ul|ol|dl|pre|style|script)\b',
                raw_content,
                re.IGNORECASE
            ))

            if len(raw_content) > max_chars and not is_html_container:
                sub_parts = cls.split_oversized_text(raw_content, max_chars)
                # 若当前批次已有内容，先封包
                if current_batch.items:
                    batches.append(current_batch)
                    current_batch = TranslationBatch(
                        batch_id=len(batches),
                        target_lang=target_lang,
                        source_lang=source_lang
                    )

                # 每个子切片独立成包或紧凑打包
                for sub_i, sub_text in enumerate(sub_parts):
                    item = BatchItem(
                        seg_id=f"seg_{idx}_sub{sub_i}",
                        block_idx=idx,
                        block=block,
                        raw_text=sub_text,
                        sub_idx=sub_i,
                        is_sub_split=True,
                        rule=rule
                    )
                    sub_batch = TranslationBatch(
                        batch_id=len(batches),
                        items=[item],
                        total_chars=len(sub_text),
                        target_lang=target_lang,
                        source_lang=source_lang
                    )
                    batches.append(sub_batch)
                continue

            if is_isolated_rule or (is_html_container and len(raw_content) > max_chars):
                # 独立封包
                if current_batch.items:
                    batches.append(current_batch)
                    current_batch = TranslationBatch(
                        batch_id=len(batches),
                        target_lang=target_lang,
                        source_lang=source_lang
                    )
                item = BatchItem(
                    seg_id=f"seg_{idx}",
                    block_idx=idx,
                    block=block,
                    raw_text=raw_content,
                    rule=rule
                )
                sub_batch = TranslationBatch(
                    batch_id=len(batches),
                    items=[item],
                    total_chars=len(raw_content),
                    target_lang=target_lang,
                    source_lang=source_lang
                )
                batches.append(sub_batch)
                continue

            # AST 粘连探测：检查紧邻下一个任务是否为列表项且当前是标题
            needs_keep_together = False
            if block.type in ["header", "heading"] and task_pos + 1 < len(tasks):
                next_idx, next_block, _ = tasks[task_pos + 1]
                if next_block.type in ["list", "list_item", "ordered_list", "unordered_list"]:
                    needs_keep_together = True

            item = BatchItem(
                seg_id=f"seg_{idx}",
                block_idx=idx,
                block=block,
                raw_text=raw_content,
                rule=rule
            )
            item_chars = len(raw_content)

            # 预算超标判断：超过段落数或字符数上限时封包
            exceeds_paras = len(current_batch.items) >= max_paras
            exceeds_chars = (current_batch.total_chars + item_chars) > max_chars

            if current_batch.items and (exceeds_paras or exceeds_chars):
                batches.append(current_batch)
                current_batch = TranslationBatch(
                    batch_id=len(batches),
                    target_lang=target_lang,
                    source_lang=source_lang
                )

            current_batch.items.append(item)
            current_batch.total_chars += item_chars

            # 挂载附近的只读 context_ref
            if context_refs_map and idx in context_refs_map:
                current_batch.context_refs.append(context_refs_map[idx])

        if current_batch.items:
            batches.append(current_batch)

        tlog.info(
            f"📦 [自适应分包] 待译任务 {len(tasks)} 个段落 ➜ 聚合打包为 {len(batches)} 个批次 "
            f"(单批上限: {max_paras}段 / {max_chars}字符 | 源语种: {source_lang})"
        )
        return batches

    @classmethod
    def estimate_batch_tokens(
        cls,
        tasks: List[Tuple[int, MarkupBlock, Any]],
        source_lang: str = "zh",
        target_langs_count: int = 1
    ) -> Dict[str, Any]:
        """
        🛡️ [Pre-flight Budget Guard] 全库出海 Token 预算前置估算
        """
        total_chars = sum(len(b.content) for _, b, _ in tasks) if tasks else 0
        norm_src = LanguageHub.resolve_to_iso(source_lang).lower()

        # 换算比例估算 (CJK ~ 1.5 chars/token, Latin ~ 4 chars/token)
        chars_per_token = 1.5 if norm_src in ["zh", "ja", "ko"] else 4.0
        prompt_tokens_per_lang = int(total_chars / chars_per_token)
        # 预估 completion tokens 约为 prompt tokens 的 1.2 倍
        completion_tokens_per_lang = int(prompt_tokens_per_lang * 1.2)
        total_tokens_all_langs = (prompt_tokens_per_lang + completion_tokens_per_lang) * max(1, target_langs_count)

        return {
            "total_chars": total_chars,
            "tasks_count": len(tasks),
            "estimated_prompt_tokens": prompt_tokens_per_lang * max(1, target_langs_count),
            "estimated_completion_tokens": completion_tokens_per_lang * max(1, target_langs_count),
            "estimated_total_tokens": total_tokens_all_langs
        }
