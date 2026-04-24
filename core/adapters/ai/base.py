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
            
        # 🛡️ 自动解析特定节点的配置，并支持全局超时回退
        self.timeout = getattr(self.config, 'api_timeout', getattr(trans_cfg, 'api_timeout', 60.0))
        self.max_retries = getattr(self.config, 'max_retries', getattr(trans_cfg, 'max_retries', 3))
        
    def translate(self, text: str, source_lang: str, target_lang: str, context_type: str = "content") -> str:
        """[Sovereignty] 统一翻译逻辑：集成内容净化与原子协议"""
        # 🛡️ 上下文提纯：根据配置决定是否剥离 JSX 标签
        strip_jsx = getattr(self.trans_cfg, 'ai_context_purification', '') == 'strip_jsx_tags'
        purified_text = AILogicHub.purify_content(text, strip_jsx=strip_jsx)
        
        system_prompt = (
            f"You are a professional translator. Translate from {source_lang} to {target_lang}. "
            "Return ONLY the translated text. No explanations. No reasoning."
        )
        return self.ask_ai_with_retry(system_prompt, purified_text)

    def ask_ai_with_retry(self, system_prompt: str, user_content: str) -> str:
        """🚀 [V6.2.1] 鲁棒性增强：指数退避重试包装器"""
        import time
        last_error = None
        
        for i in range(self.max_retries + 1):
            try:
                return self._ask_ai(system_prompt, user_content)
            except Exception as e:
                last_error = e
                # 识别不可重试的错误 (如 400 Bad Request，除非是网络抖动导致的异常)
                error_msg = str(e).lower()
                is_retriable = True
                if "400" in error_msg and "bad request" in error_msg:
                    # 400 错误通常是 Payload 问题，重试大概率无用，除非是临时性 API 异常
                    # 但为了稳健，我们记录详细日志并根据情况决定是否重试
                    logger.error(f"🛑 [AI 400 错误] Node: {self.node_name} | 请检查 Prompt 或 Payload 是否超限。")
                    is_retriable = False 
                
                if not is_retriable or i == self.max_retries:
                    break
                    
                wait_time = (2 ** i) * 1.5
                logger.warning(f"⚠️ [AI 重试] {self.node_name} 失败 ({i+1}/{self.max_retries}): {e} | {wait_time}s 后重试...")
                time.sleep(wait_time)
        
        raise last_error

    def describe_image(self, image_bytes: bytes, mime_type: str, context_text: str = "") -> str:
        """[Resonance] AI 视觉感知接口"""
        return ""

    def generate_slug(self, title: str, is_dry_run: bool = False) -> Tuple[str, bool]:
        """[Sovereignty] 统一逻辑：委托 LogicHub 执行工业级 Slug 清洗"""
        if is_dry_run: return f"dry-run-{title}", True
        prompts = getattr(self.trans_cfg, 'custom_prompts', {})
        system_prompt = prompts.get("slug", (
            "You are an SEO expert. Generate a URL-safe, lowercase, SEO-friendly English slug. "
            "Return ONLY the slug string. No reasoning."
        ))
        
        try:
            raw_slug = self.ask_ai_with_retry(system_prompt, title)
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
        system_prompt = prompts.get("seo", (
            f"You are an SEO expert. Provide a description (max 150 chars) and 5 keywords for {lang_name}. "
            "Return ONLY a JSON object. No reasoning."
        ))
        
        try:
            raw_json = self.ask_ai_with_retry(system_prompt, text[:2000])
            # 调用强力 JSON 提取引擎
            return AILogicHub.extract_seo_payload(raw_json)
        except Exception as e:
            logger.error(f"🛑 [SEO Generation Error]: {e}")
            return {"description": "", "keywords": []}, False

    @abc.abstractmethod
    def _ask_ai(self, system_prompt: str, user_content: str) -> str:
        """[Protocol] 纯净协议原子操作：由各适配器实现具体的网络通讯逻辑"""
        pass
