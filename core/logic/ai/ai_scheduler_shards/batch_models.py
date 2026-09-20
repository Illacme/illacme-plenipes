# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - Batch Models
职责：定义自适应批处理数据项 (BatchItem) 与批次容器 (TranslationBatch)
🛡️ [Rule 12.9/12.10] 纯数据契约结构
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from core.markup.base import MarkupBlock


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
