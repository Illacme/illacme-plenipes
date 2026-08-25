#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Logic Hub
模块职责：提供工业级的 AI 业务处理计算单元，包括 Slug 清洗、JSON 修复与提示词渲染。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]：逻辑解耦核心，具体计算算子已物理拆解至 ai_logic_shards/。
"""

from typing import Tuple, Dict, Any, List
from .ai_logic_shards import (
    clean_slug as _clean_slug,
    clean_translation_response as _clean_translation_response,
    clean_metadata_value as _clean_metadata_value,
    purify_content as _purify_content,
    repair_json as _repair_json,
    repair_json_array as _repair_json_array,
    extract_seo_payload as _extract_seo_payload,
    mask_block as _mask_block,
    unmask_block as _unmask_block,
    split_markdown as _split_markdown,
    format_knowledge_context as _format_knowledge_context,
    mask_glossary as _mask_glossary,
    unmask_glossary as _unmask_glossary
)

class AILogicHub:
    """🚀 [TDR-Iter-025] 工业级 AI 业务逻辑计算中心 (Facade 门面)"""

    @staticmethod
    def clean_slug(raw_slug: str, max_length: int = 100) -> str:
        """[Industrial-Grade] 物理级 Slug 净化逻辑"""
        return _clean_slug(raw_slug, max_length)

    @staticmethod
    def clean_translation_response(raw_response: str) -> str:
        """🚀 [V108.0] 物理级 AI 译文提纯与 prompt 围栏防护"""
        return _clean_translation_response(raw_response)

    @staticmethod
    def clean_metadata_value(raw_response: str) -> str:
        """🚀 [V106.0] 物理级 SEO 与元数据提取算法"""
        return _clean_metadata_value(raw_response)

    @staticmethod
    def repair_json(raw_response: str) -> str:
        """[Resilience] 强力 JSON 修复算法"""
        return _repair_json(raw_response)

    @staticmethod
    def repair_json_array(raw_response: str) -> str:
        """[Resilience] 强力 JSON Array 修复算法"""
        return _repair_json_array(raw_response)

    @staticmethod
    def mask_block(text: str, translate_labels: bool = True, external_mask_mode: str = "url_only") -> Tuple[str, Dict[str, str]]:
        """🚀 [V48.3] 块级防护装甲：临时屏蔽技术实体，防止 AI 误伤"""
        return _mask_block(text, translate_labels, external_mask_mode)

    @staticmethod
    def unmask_block(text: str, masks: Dict[str, str]) -> str:
        """🚀 [V48.3] 块级护盾解除：还原被临时屏蔽的技术实体，具备 Markdown 结构自愈能力"""
        return _unmask_block(text, masks)

    @staticmethod
    def purify_content(text: str, strip_jsx: bool = False) -> str:
        """[Sovereignty] 内容净化引擎"""
        return _purify_content(text, strip_jsx)

    @staticmethod
    def extract_seo_payload(raw_json_str: str) -> Tuple[Dict[str, Any], bool]:
        """[Industrial-Grade] SEO 载荷安全提取"""
        return _extract_seo_payload(raw_json_str)

    @staticmethod
    def split_markdown(text: str, max_chunk_size: int) -> List[str]:
        """[Industrial-Grade] 语义分片算法 (Markdown 优先)"""
        return _split_markdown(text, max_chunk_size)

    @staticmethod
    def format_knowledge_context(related_nodes: List[Dict[str, Any]]) -> str:
        """🚀 [V24.5] 语义主权：将知识图谱数据转化为 AI 翻译上下文指令"""
        return _format_knowledge_context(related_nodes)

    @staticmethod
    def mask_glossary(text: str, glossary: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
        """🚀 [V24.5] 术语隔离屏蔽：在发送给 AI 前，使用占位符保护术语不被误翻译"""
        return _mask_glossary(text, glossary)

    @staticmethod
    def unmask_glossary(text: str, glossary_masks: Dict[str, str]) -> str:
        """🚀 [V24.5] 术语隔离还原：将大模型翻译后的术语占位符还原为对应的翻译目标值"""
        return _unmask_glossary(text, glossary_masks)
