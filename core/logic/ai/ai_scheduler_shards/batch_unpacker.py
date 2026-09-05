# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - Batch Unpacker & Selective Rescue
职责：XML 隔离标签解析、分段独立掩码还原、AST 语法树守门校验与局部精准拯救 (Selective Rescue)
🛡️ [Rule 12.9/12.10] 纯逻辑解包与拯救计算单元
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

from core.logic.ai.ai_scheduler_shards.batch_chunker import TranslationBatch, BatchItem
from core.logic.ai.ai_logic_hub import AILogicHub
from core.utils.tracing import tlog

@dataclass
class UnpackResult:
    succeeded_blocks: Dict[int, str] = field(default_factory=dict)  # block_idx -> translated_text
    failed_items: List[BatchItem] = field(default_factory=list)      # 语法错误或漏译需重试的条目
    missing_seg_ids: List[str] = field(default_factory=list)        # 缺失的 seg_id 列表
    syntax_error_items: List[Tuple[BatchItem, str]] = field(default_factory=list) # (item, err_msg)
    is_all_success: bool = True

class BatchUnpacker:
    """🚀 [Batch Unpacker] 容错解包与精准拯救器"""

    @classmethod
    def unmask_scoped(
        cls,
        text: str,
        block_masks: Dict[str, str],
        glossary_masks: Dict[str, str]
    ) -> str:
        """
        分段独立掩码还原：先还原块级技术实体与链接，再还原术语表。
        """
        if not text:
            return text

        # 1. 还原块级技术掩码 (支持 Markdown 链接与 Wikilink 自愈)
        unmasked = AILogicHub.unmask_block(text, block_masks)

        # 2. 还原术语表掩码
        if glossary_masks:
            unmasked = AILogicHub.unmask_glossary(unmasked, glossary_masks)

        # 3. 标题与格式自愈
        # 补齐标题前后的物理空行分割，防止列表项与标题强行粘连
        unmasked = re.sub(r'([^\n#])\s*(#{1,6}\s+)', r'\1\n\n\2', unmasked)
        unmasked = re.sub(r'^(#{1,6}\s+.*?)\n([^\n#])', r'\1\n\n\2', unmasked, flags=re.MULTILINE)

        return unmasked.strip()

    @classmethod
    def parse_segments_from_response(cls, raw_response: str) -> Dict[str, str]:
        """
        从大模型返回的纯文本中强健提取 <i18n_seg id="seg_N">...</i18n_seg> 字典。
        """
        if not raw_response:
            return {}

        # 1. 物理清洗思考链与多余代码块包裹
        cleaned = AILogicHub.clean_translation_response(raw_response)

        extracted: Dict[str, str] = {}

        # 2. 标准双闭合标签正则匹配
        pattern = re.compile(
            r'<i18n_seg\s+id=["\'](?P<seg_id>[^"\']+)["\']\s*>(?P<content>.*?)</i18n_seg>',
            re.DOTALL | re.IGNORECASE
        )
        for m in pattern.finditer(cleaned):
            seg_id = m.group('seg_id').strip()
            content = m.group('content').strip()
            extracted[seg_id] = content

        # 3. 容错提取：如果最后一个标签未闭合 (因 Output Token 截断或格式幻觉)
        if not extracted or len(extracted) < len(re.findall(r'<i18n_seg\s+id=', cleaned, re.IGNORECASE)):
            unclosed_pattern = re.compile(
                r'<i18n_seg\s+id=["\'](?P<seg_id>[^"\']+)["\']\s*>(?P<content>(?:(?!<i18n_seg).)*)',
                re.DOTALL | re.IGNORECASE
            )
            for m in unclosed_pattern.finditer(cleaned):
                seg_id = m.group('seg_id').strip()
                if seg_id not in extracted:
                    content = m.group('content').strip()
                    # 剔除可能残留的尾部 </i18n_seg>
                    content = re.sub(r'</i18n_seg>$', '', content, flags=re.IGNORECASE).strip()
                    extracted[seg_id] = content

        return extracted

    @classmethod
    def unpack_and_rescue(
        cls,
        raw_response: str,
        item_masks_map: Dict[str, Dict[str, Any]],
        batch: TranslationBatch,
        structure_validator: Optional[Any] = None
    ) -> UnpackResult:
        """
        🚀 [Selective Rescue] 局部精准解包与拯救逻辑
        - 对已成功解析且通过 AST 校验的段落直接接纳入库
        - 仅将漏译或语法破损的条目放入 failed_items 以便局部单段重试
        - 冲突消解 3: 严格通过 block_idx 映射回原稿绝对槽位
        """
        result = UnpackResult()
        extracted_segments = cls.parse_segments_from_response(raw_response)

        # 临时暂存各个 block 的子切片 (处理 sub_sentence_splitting 拼接)
        sub_splits_map: Dict[int, Dict[int, str]] = {}
        sub_splits_expected_count: Dict[int, int] = {}

        for item in batch.items:
            seg_id = item.seg_id
            block_idx = item.block_idx
            masks_info = item_masks_map.get(seg_id, {})
            block_masks = masks_info.get("block_masks", {})
            glossary_masks = masks_info.get("glossary_masks", {})

            if item.is_sub_split:
                sub_splits_expected_count[block_idx] = sub_splits_expected_count.get(block_idx, 0) + 1

            if seg_id not in extracted_segments:
                # 漏译场景：放入缺失列表与失败重试列表
                tlog.warning(f"⚠️ [局部漏标] Batch {batch.batch_id} 中段落 {seg_id} 未被 LLM 闭合输出，触发单段局部精准拯救。")
                result.missing_seg_ids.append(seg_id)
                result.failed_items.append(item)
                result.is_all_success = False
                continue

            raw_seg_content = extracted_segments[seg_id]

            # 还原掩码
            unmasked_text = cls.unmask_scoped(raw_seg_content, block_masks, glossary_masks)

            # 🛡️ 标题语法守卫 (Heading Parity Guard)：若原文非标题（不以 # 开头），剥离译文开头误加的 # 标记，防范大模型标题幻觉
            if not item.raw_text.strip().startswith('#') and unmasked_text.strip().startswith('#'):
                unmasked_text = re.sub(r'^\s*#{1,6}\s*', '', unmasked_text)

            # 校验 AST 结构完整性 (如果提供了校验函数)
            if structure_validator:
                try:
                    is_valid, err_msg = structure_validator(item.raw_text, unmasked_text)
                except Exception as ve:
                    is_valid, err_msg = False, str(ve)

                if not is_valid:
                    tlog.warning(f"⚠️ [AST 校验未过] 段落 {seg_id} 语法标记断裂: {err_msg}，将进入单段自愈重试。")
                    result.syntax_error_items.append((item, err_msg))
                    result.failed_items.append(item)
                    result.is_all_success = False
                    continue

            # 成功接纳
            if item.is_sub_split:
                if block_idx not in sub_splits_map:
                    sub_splits_map[block_idx] = {}
                sub_splits_map[block_idx][item.sub_idx or 0] = unmasked_text
            else:
                result.succeeded_blocks[block_idx] = unmasked_text

        # 处理超长切片的拼接重组
        for b_idx, parts_dict in sub_splits_map.items():
            expected = sub_splits_expected_count.get(b_idx, 0)
            if len(parts_dict) == expected:
                # 所有子句均成功解包，依序号拼接
                sorted_parts = [parts_dict[i] for i in sorted(parts_dict.keys())]
                # 根据语种选择拼接分隔符 (CJK 直接拼或空格拼)
                delim = "" if batch.target_lang in ["zh", "ja", "ko"] else " "
                result.succeeded_blocks[b_idx] = delim.join(sorted_parts)
            else:
                # 子句有缺失，标记整段为失败
                missing_subs = [item for item in batch.items if item.block_idx == b_idx and item.seg_id not in extracted_segments]
                for m_item in missing_subs:
                    if m_item not in result.failed_items:
                        result.failed_items.append(m_item)
                result.is_all_success = False

        return result
