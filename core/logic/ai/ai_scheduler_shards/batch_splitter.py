# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - Batch Splitter & Estimator
职责：超长单段自适应安全标点分句切分与全库出海 Token 预算前置估算
"""

import re
from typing import List, Dict, Any, Tuple
from core.markup.base import MarkupBlock
from core.utils.language_hub import LanguageHub


def split_oversized_text(text: str, max_chars: int) -> List[str]:
    """
    🛡️ [Sub-Sentence Splitting] 超长单段自适应安全标点分句切分
    在标点符号 (。！？.!?\n\n) 处安全切分，防止单段超出上下文预算。
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


def estimate_batch_tokens(
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
