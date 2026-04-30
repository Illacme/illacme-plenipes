#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Task Mixin
模块职责：提供上下文感知的出版任务处理逻辑。
"""

from typing import List, Dict, Any, Tuple, Optional
from core.logic.ai.ai_logic_hub import AILogicHub
from .payload_manager import PayloadManager
from core.utils.tracing import tlog

class AITaskMixin:
    """🚀 [V35.0] 出版任务逻辑集合，支持通过适配器执行特定业务推理"""
    
    def translate(self, text: str, source_lang: str, target_lang: str, context_type: str = "content", remedy_instruction: str = None, is_dry_run: bool = False, **kwargs) -> str:
        # 🛡️ 上下文提纯与语种解析
        from core.utils.language_hub import LanguageHub
        s_name = LanguageHub.resolve_to_name(source_lang)
        t_name = LanguageHub.resolve_to_name(target_lang)

        p = self.trans_cfg.prompts
        system_prompt = PayloadManager.format_prompt(p.translate_system, source_lang=s_name, target_lang=t_name)
        
        if kwargs.get('knowledge_context'):
            system_prompt += f"\n\n[CONTEXT_GUARD]\n{kwargs['knowledge_context']}\n[/CONTEXT_GUARD]"

        if remedy_instruction:
            system_prompt += f"\n[REMEDY]\n{remedy_instruction}\n[/REMEDY]"

        user_content = PayloadManager.format_prompt(p.translate_user, source_lang=s_name, target_lang=t_name, text=text)
        payload = PayloadManager.prepare_payload(self, system_prompt, user_content, is_json=False)
        return self.ask_ai_with_retry(payload)

    def generate_slug(self, title: str, is_dry_run: bool = False, **kwargs) -> Tuple[str, bool]:
        p = self.trans_cfg.prompts
        system_prompt = PayloadManager.format_prompt(p.slug_system)
        user_content = PayloadManager.format_prompt(p.slug_user, title=title)
        try:
            payload = PayloadManager.prepare_payload(self, system_prompt, user_content, is_json=False)
            payload["params"]["max_tokens"] = 64
            raw_slug = self.ask_ai_with_retry(payload)
            return AILogicHub.clean_slug(raw_slug), True
        except:
            return AILogicHub.clean_slug(title), False

    def translate_title(self, title: str, target_lang: str, is_dry_run: bool = False, **kwargs) -> str:
        from core.utils.language_hub import LanguageHub
        t_name = LanguageHub.resolve_to_name(target_lang)
        p = self.trans_cfg.prompts
        system_prompt = PayloadManager.format_prompt(p.title_system, target_lang=t_name)
        user_content = PayloadManager.format_prompt(p.title_user, title=title)
        payload = PayloadManager.prepare_payload(self, system_prompt, user_content, is_json=False)
        return self.ask_ai_with_retry(payload) or title

    def generate_seo_metadata(self, text: str, lang_name: str, is_dry_run: bool = False, **kwargs) -> Tuple[dict, bool]:
        from core.logic.context_compressor import ContextCompressor
        p = self.trans_cfg.prompts
        core_semantics = ContextCompressor.extract_core_semantics(text)
        system_prompt = PayloadManager.format_prompt(p.seo_system, lang_name=lang_name)
        user_content = PayloadManager.format_prompt(p.seo_user, lang_name=lang_name, text=core_semantics)
        try:
            payload = PayloadManager.prepare_payload(self, system_prompt, user_content, is_json=True)
            payload["params"]["max_tokens"] = 256
            raw_json = self.ask_ai_with_retry(payload)
            return AILogicHub.extract_seo_payload(raw_json)
        except:
            return {"description": "", "keywords": []}, False
