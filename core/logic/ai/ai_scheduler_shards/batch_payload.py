# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - Batch Payload Assembler
职责：分段独立命名空间掩码、长词优先术语保护、全景语境装配与 Dry-Run 仿真
🛡️ [Rule 12.9/12.10] 纯逻辑载荷装配计算单元
"""

import re
from typing import Dict, Any, List, Optional, Tuple

from core.logic.ai.ai_scheduler_shards.batch_chunker import TranslationBatch, BatchItem
from core.utils.tracing import tlog

class BatchPayloadAssembler:
    """🚀 [Batch Payload Assembler] 聚合载荷装配器"""

    @classmethod
    def mask_glossary_scoped(
        cls,
        text: str,
        glossary: Dict[str, str],
        block_idx: int
    ) -> Tuple[str, Dict[str, str]]:
        """
        🚀 [Longest-Match First] 术语隔离屏蔽（分段独立命名空间）
        按术语长度降序匹配，防止复合词被短词撕裂；使用 __GLOS_B{block_idx}_{id}__ 保证命名空间唯一。
        """
        if not text or not glossary:
            return text, {}

        glossary_masks: Dict[str, str] = {}
        processed_text = text
        mask_counter = 0

        # 按键长度降序排序
        for orig_word in sorted(glossary.keys(), key=len, reverse=True):
            target_val = glossary[orig_word]
            if not orig_word.strip():
                continue

            # 中文或全角字符直接 escape，英文使用词界
            if re.search(r'[\u4e00-\u9fa5]', orig_word):
                pattern = re.compile(re.escape(orig_word))
            else:
                pattern = re.compile(rf'\b{re.escape(orig_word)}\b', re.IGNORECASE)

            matches = pattern.findall(processed_text)
            for m in set(matches):
                # 排除已是掩码标记的字符串
                if "__MASK_B" in m or "__GLOS_B" in m:
                    continue
                placeholder = f"__GLOS_B{block_idx}_{mask_counter}__"
                glossary_masks[placeholder] = target_val
                processed_text = processed_text.replace(m, placeholder)
                mask_counter += 1

        return processed_text, glossary_masks

    @classmethod
    def mask_block_scoped(
        cls,
        text: str,
        block_idx: int,
        translate_labels: bool = True,
        external_mask_mode: str = "url_only"
    ) -> Tuple[str, Dict[str, str]]:
        """
        🚀 [Scoped Block Masking] 块级技术实体屏蔽（分段独立命名空间）
        使用 __MASK_B{block_idx}_{id}__ 作为占位符，彻底阻断跨段掩码串扰（冲突消解 1）。
        """
        if not text:
            return text, {}

        masks: Dict[str, str] = {}

        patterns = [
            r'<!--.*?-->',
            r'\!\[(?P<md_img_label>.*?)\]\((?P<md_img_url>.*?)\)',
            r'\[\[(?P<wiki_body>.*?)\]\]',
            r'\[(?P<md_link_label>.*?)\]\((?P<md_link_url>.*?)\)'
        ]

        def repl(m: re.Match) -> str:
            # 1. HTML Comment
            full_match = m.group(0)
            if full_match.startswith('<!--') and full_match.endswith('-->'):
                key = f"__MASK_B{block_idx}_{len(masks)}__"
                masks[key] = full_match
                return key

            # 2. Wikilink [[...]]
            try:
                wiki_body = m.group('wiki_body')
            except IndexError:
                wiki_body = None

            if wiki_body is not None:
                if not translate_labels:
                    key = f"__MASK_B{block_idx}_{len(masks)}__"
                    masks[key] = full_match
                    return key
                if '|' in wiki_body:
                    target_part, alias_part = wiki_body.split('|', 1)
                    key = f"__MASK_B{block_idx}_{len(masks)}__"
                    masks[key] = target_part
                    return f"[[{key}|{alias_part}]]"
                else:
                    key = f"__MASK_B{block_idx}_{len(masks)}__"
                    masks[key] = wiki_body
                    return f"[[{key}|{wiki_body}]]"

            # 3. Markdown Link [label](url)
            try:
                md_link_url = m.group('md_link_url')
                md_link_label = m.group('md_link_label')
            except IndexError:
                md_link_url = None
                md_link_label = None

            if md_link_url is not None:
                is_ext = md_link_url.startswith(('http://', 'https://', 'mailto:', 'tel:'))
                if not translate_labels or (is_ext and external_mask_mode == "all"):
                    key = f"__MASK_B{block_idx}_{len(masks)}__"
                    masks[key] = full_match
                    return key
                key = f"__MASK_B{block_idx}_{len(masks)}__"
                masks[key] = md_link_url
                return f"[{md_link_label}]({key})"

            # 4. Markdown Image ![label](url)
            try:
                md_img_url = m.group('md_img_url')
                md_img_label = m.group('md_img_label')
            except IndexError:
                md_img_url = None
                md_img_label = None

            if md_img_url is not None:
                is_ext = md_img_url.startswith(('http://', 'https://', 'mailto:', 'tel:'))
                if not translate_labels or (is_ext and external_mask_mode == "all"):
                    key = f"__MASK_B{block_idx}_{len(masks)}__"
                    masks[key] = full_match
                    return key
                key = f"__MASK_B{block_idx}_{len(masks)}__"
                masks[key] = md_img_url
                return f"![{md_img_label}]({key})"

            # 兜底
            key = f"__MASK_B{block_idx}_{len(masks)}__"
            masks[key] = full_match
            return key

        combined_pattern = "|".join(patterns)
        masked_text = re.sub(combined_pattern, repl, text, flags=re.DOTALL)
        return masked_text, masks

    @classmethod
    def assemble_batch_payload(
        cls,
        batch: TranslationBatch,
        article_title: str = "",
        article_desc: str = "",
        glossary: Optional[Dict[str, str]] = None,
        link_gov: Optional[Any] = None,
        knowledge_context: str = "",
        is_dry_run: bool = False
    ) -> Tuple[str, Dict[str, Dict[str, Any]], str]:
        """
        🚀 装配包含全景语境、分段 XML 隔离与独立掩码的高鲁棒性 Prompt 载荷。
        执行顺序：先执行块级技术实体屏蔽 (保护 URL/Wikilink targets)，再对参与翻译的文本进行术语屏蔽。
        返回: (assembled_payload_text, item_masks_map, dry_run_response)
        """
        item_masks_map: Dict[str, Dict[str, Any]] = {}
        segments_xml: List[str] = []
        dry_run_parts: List[str] = []

        translate_labels = link_gov.translate_labels if link_gov else True
        external_mask_mode = link_gov.external_links_mask_mode if link_gov else "url_only"

        for item in batch.items:
            raw = item.raw_text

            # 1. 优先执行块级技术实体掩码处理 (分段命名空间，保护 URL、Image URL、Wikilink Target)
            masked_block, block_masks = cls.mask_block_scoped(
                raw,
                item.block_idx,
                translate_labels=translate_labels,
                external_mask_mode=external_mask_mode
            )

            # 2. 对剩余展示文本与正文进行术语掩码处理 (分段命名空间)
            if glossary:
                masked_content, glos_masks = cls.mask_glossary_scoped(masked_block, glossary, item.block_idx)
            else:
                masked_content, glos_masks = masked_block, {}

            # 记录该 item 专属的掩码表
            item_masks_map[item.seg_id] = {
                "block_masks": block_masks,
                "glossary_masks": glos_masks,
                "block_idx": item.block_idx,
                "sub_idx": item.sub_idx,
                "is_sub_split": item.is_sub_split
            }

            # 3. 组装分段 XML 标签
            seg_xml = f'<i18n_seg id="{item.seg_id}">\n{masked_content}\n</i18n_seg>'
            segments_xml.append(seg_xml)

            # 4. Dry-Run 仿真产物生成
            dry_run_parts.append(
                f'<i18n_seg id="{item.seg_id}">\n[DRY-RUN {batch.target_lang.upper()} TRANSLATION OF {item.seg_id}]: {masked_content}\n</i18n_seg>'
            )

        # 5. 全景语境注入 (冲突消解 2: Frontmatter 优先单向注入已译大标题)
        context_parts = []
        if article_title or article_desc:
            ctx_xml = "<article_context>\n"
            if article_title:
                ctx_xml += f"  <article_title>{article_title}</article_title>\n"
            if article_desc:
                ctx_xml += f"  <article_summary>{article_desc}</article_summary>\n"
            ctx_xml += "</article_context>\n"
            context_parts.append(ctx_xml)

        # 6. 只读代码/表格语境注入 (进阶 6)
        if batch.context_refs:
            refs_xml = "<readonly_references>\n"
            for ref in batch.context_refs:
                ref_type = ref.get("type", "code")
                ref_content = ref.get("content", "")
                refs_xml += f'  <context_ref type="{ref_type}">\n{ref_content}\n  </context_ref>\n'
            refs_xml += "</readonly_references>\n"
            context_parts.append(refs_xml)

        # 7. 拼接最终 Prompt Body
        body_segments = "\n\n".join(segments_xml)
        header_context = "\n".join(context_parts) if context_parts else ""

        assembled_prompt = ""
        if header_context:
            assembled_prompt += f"{header_context}\n"
        assembled_prompt += f"{body_segments}"

        dry_run_response = "\n\n".join(dry_run_parts)
        return assembled_prompt, item_masks_map, dry_run_response
