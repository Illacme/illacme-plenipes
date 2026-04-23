#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Base Adapter
模块职责：定义 AI 适配器的基类、配置解析与协议契约。
🛡️ [AEL-Iter-v5.3]：基于 TDR 复健的解耦适配器基座。
"""

import abc
import logging
from typing import List, Dict, Any, Optional, Tuple

from core.logic.ai_logic_hub import AILogicHub

logger = logging.getLogger("Illacme.plenipes")

class BaseTranslator(abc.ABC):
    """🚀 [TDR-Iter-025] AI 适配器契约化基类 (Logic Orchestrator)"""
    def __init__(self, node_name, trans_cfg):
        self.node_name = node_name
        self.trans_cfg = trans_cfg
        # 🛡️ 自动解析特定节点的配置
        self.config = trans_cfg.providers.get(node_name)
        if not self.config:
            raise ValueError(f"未找到节点配置: {node_name}")
            
        self.timeout = getattr(self.config, 'api_timeout', 60.0)
        self.max_retries = getattr(self.config, 'max_retries', 3)
        
    def translate(self, text: str, source_lang: str, target_lang: str, context_type: str = "content") -> str:
        """[Sovereignty] 统一翻译逻辑：集成内容净化与原子协议"""
        # 🛡️ 上下文提纯：根据配置决定是否剥离 JSX 标签
        strip_jsx = getattr(self.trans_cfg, 'ai_context_purification', '') == 'strip_jsx_tags'
        purified_text = AILogicHub.purify_content(text, strip_jsx=strip_jsx)
        
        system_prompt = f"You are a professional translator. Translate the following text from {source_lang} to {target_lang}. Return only the translation without any explanation."
        return self._ask_ai(system_prompt, purified_text)

    def describe_image(self, image_bytes: bytes, mime_type: str, context_text: str = "") -> str:
        """[Resonance] AI 视觉感知接口"""
        return ""

    def generate_slug(self, title: str, is_dry_run: bool = False) -> Tuple[str, bool]:
        """[Sovereignty] 统一逻辑：委托 LogicHub 执行工业级 Slug 清洗"""
        if is_dry_run: return f"dry-run-{title}", True
        prompts = getattr(self.trans_cfg, 'custom_prompts', {})
        system_prompt = prompts.get("slug", "You are an SEO expert. Generate a URL-safe, lowercase, SEO-friendly English slug for the given title. Return ONLY the slug string, no quotes, no extra text.")
        
        try:
            raw_slug = self._ask_ai(system_prompt, title)
            # 调用工业级清洗引擎
            clean_slug = AILogicHub.clean_slug(raw_slug)
            return clean_slug, True
        except Exception as e:
            logger.error(f"🛑 [Slug Generation Error]: {e}")
            return None, False

    def generate_seo_metadata(self, text: str, lang_name: str, is_dry_run: bool = False) -> Tuple[dict, bool]:
        """[Sovereignty] 统一逻辑：委托 LogicHub 执行强力 JSON 修复与提取"""
        if is_dry_run: return {"description": "Dry run SEO", "keywords": "test"}, True
        prompts = getattr(self.trans_cfg, 'custom_prompts', {})
        system_prompt = prompts.get("seo", f"You are an SEO expert. Analyze the following {lang_name} text and provide a concise description (max 150 chars) and 5-8 relevant keywords. Return ONLY a valid JSON object with 'description' and 'keywords' keys.")
        
        try:
            raw_json = self._ask_ai(system_prompt, text[:2000])
            # 调用强力 JSON 提取引擎
            return AILogicHub.extract_seo_payload(raw_json)
        except Exception as e:
            logger.error(f"🛑 [SEO Generation Error]: {e}")
            return {"description": "", "keywords": []}, False

    @abc.abstractmethod
    def _ask_ai(self, system_prompt: str, user_content: str) -> str:
        """[Protocol] 纯净协议原子操作：由各适配器实现具体的网络通讯逻辑"""
        pass
