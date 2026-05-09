#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Task Mixin
模块职责：提供上下文感知的出版任务处理逻辑。
"""

from typing import List, Dict, Any, Tuple, Optional
from core.logic.ai.ai_logic_hub import AILogicHub
from core.adapters.ai.payload_manager import PayloadManager
from core.utils.tracing import tlog

class AITaskMixin:
    """🚀 [V35.0] 出版任务逻辑集合，支持通过适配器执行特定业务推理"""
    
    def translate(self, text: str, source_lang: str, target_lang: str, context_type: str = "content", remedy_instruction: str = None, is_dry_run: bool = False, style: str = None, **kwargs) -> str:
        # 🛡️ 上下文提纯与语种解析
        from core.utils.language_hub import LanguageHub
        s_name = LanguageHub.resolve_to_name(source_lang)
        t_name = LanguageHub.resolve_to_name(target_lang)

        # 🚀 [V55.26] 动态方言映射
        p = self.trans_cfg.prompts
        if style:
            from core.logic.ai.ai_factory import TranslatorFactory
            # 动态获取该风格对应的提示词，优先级最高
            p = TranslatorFactory.get_prompts_for_style(style, getattr(self, 'imprint_id', 'default'), p)

        system_prompt = PayloadManager.format_prompt(p.translate_system, source_lang=s_name, target_lang=t_name)
        
        if kwargs.get('knowledge_context'):
            system_prompt += f"\n\n[CONTEXT_GUARD]\n{kwargs.get('knowledge_context')}\n[/CONTEXT_GUARD]"

        if remedy_instruction:
            system_prompt += f"\n[REMEDY]\n{remedy_instruction}\n[/REMEDY]"

        user_content = PayloadManager.format_prompt(p.translate_user, source_lang=s_name, target_lang=t_name, text=text)
        payload = PayloadManager.prepare_payload(self, system_prompt, user_content, is_json=False)
        return self.ask_ai_with_retry(payload)

    def generate_slug(self, title: str, is_dry_run: bool = False, style: str = None, **kwargs) -> Tuple[str, bool]:
        p = self.trans_cfg.prompts
        if style:
            from core.logic.ai.ai_factory import TranslatorFactory
            p = TranslatorFactory.get_prompts_for_style(style, getattr(self, 'imprint_id', 'default'), p)
            
        system_prompt = PayloadManager.format_prompt(p.slug_system)
        user_content = PayloadManager.format_prompt(p.slug_user, title=title)
        try:
            payload = PayloadManager.prepare_payload(self, system_prompt, user_content, is_json=False)
            if "params" not in payload: payload["params"] = {}
            payload["params"]["max_tokens"] = 64
            raw_slug = self.ask_ai_with_retry(payload)
            return AILogicHub.clean_slug(raw_slug), True
        except:
            return AILogicHub.clean_slug(title), False

    def translate_title(self, title: str, target_lang: str, is_dry_run: bool = False, style: str = None, **kwargs) -> str:
        from core.utils.language_hub import LanguageHub
        t_name = LanguageHub.resolve_to_name(target_lang)
        
        p = self.trans_cfg.prompts
        if style:
            from core.logic.ai.ai_factory import TranslatorFactory
            p = TranslatorFactory.get_prompts_for_style(style, getattr(self, 'imprint_id', 'default'), p)

        system_prompt = PayloadManager.format_prompt(p.title_system, target_lang=t_name)
        user_content = PayloadManager.format_prompt(p.title_user, title=title)
        payload = PayloadManager.prepare_payload(self, system_prompt, user_content, is_json=False)
        return self.ask_ai_with_retry(payload) or title

    def generate_seo_metadata(self, text: str, lang_name: str, is_dry_run: bool = False, style: str = None, **kwargs) -> Tuple[dict, bool]:
        from core.logic.context_compressor import ContextCompressor
        p = self.trans_cfg.prompts
        if style:
            from core.logic.ai.ai_factory import TranslatorFactory
            p = TranslatorFactory.get_prompts_for_style(style, getattr(self, 'imprint_id', 'default'), p)
            
        core_semantics = ContextCompressor.extract_core_semantics(text)
        system_prompt = PayloadManager.format_prompt(p.seo_system, lang_name=lang_name)
        user_content = PayloadManager.format_prompt(p.seo_user, lang_name=lang_name, text=core_semantics)
        try:
            payload = PayloadManager.prepare_payload(self, system_prompt, user_content, is_json=True)
            if "params" not in payload: payload["params"] = {}
            payload["params"]["max_tokens"] = 256
            raw_json = self.ask_ai_with_retry(payload)
            return AILogicHub.extract_seo_payload(raw_json)
        except:
            return {"description": "", "keywords": []}, False

    def translate_metadata(self, text: Any, meta_type: str, target_lang: str, is_dry_run: bool = False, style: str = None, **kwargs) -> Any:
        """🚀 [V25.5] 元数据翻译：支持 Tags, Category 等非正文内容的方言对正"""
        from core.utils.language_hub import LanguageHub
        t_name = LanguageHub.resolve_to_name(target_lang)
        
        p = self.trans_cfg.prompts
        if style:
            from core.logic.ai.ai_factory import TranslatorFactory
            p = TranslatorFactory.get_prompts_for_style(style, getattr(self, 'imprint_id', 'default'), p)
            
        system_prompt = PayloadManager.format_prompt(p.metadata_system, target_lang=t_name, meta_type=meta_type)
        user_content = PayloadManager.format_prompt(p.metadata_user, target_lang=t_name, text=str(text), meta_type=meta_type)
        
        try:
            payload = PayloadManager.prepare_payload(self, system_prompt, user_content, is_json=False)
            res = self.ask_ai_with_retry(payload)
            return res or text
        except:
            return text
