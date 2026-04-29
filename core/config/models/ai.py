#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Config - AI Models
职责：定义 AI 算力节点、提示词模板与翻译策略。
🛡️ [V24.0] Pydantic 严格校验体系：实现 AI 算力安全审计。
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from .base import StrategyType, ProviderType

class AIProviderLimits(BaseModel):
    max_concurrency: int = Field(5, ge=1, le=50)
    timeout: float = Field(60.0, ge=1)
    max_tokens_per_min: int = Field(40000, ge=1000)

class PromptTemplates(BaseModel):
    translate_system: str = "You are a professional translator. Translate the following Markdown content from {source_lang} to {target_lang}. Keep all Markdown syntax, frontmatter keys, and LaTeX formulas intact. Do not add any explanations."
    translate_user: str = "### Content ###\n{text}\n### Translation ###"
    seo_system: str = "Analyze the text and provide SEO metadata in JSON format with 'description' and 'keywords' fields in {lang_name}."
    seo_user: str = "### Text ###\n{text}"
    slug_system: str = "Generate a URL-friendly slug based on the title. Only output the slug string."
    slug_user: str = "{title}"
    expert_guideline_wrapper: str = "\n\n[Expert Remediation - ID:{iter_id}]\n{remedy_block}"
    title_system: str = "You are a professional editor. Translate and polish the following title into {target_lang}. Keep it concise and professional. Output ONLY the title."
    title_user: str = "{title}"
    metadata_system: str = "You are a professional editor. Translate and polish the provided metadata into {target_lang}. Output ONLY the result."
    metadata_user: str = "Type: {meta_type}\nValue: {text}"

class TranslationProvider(BaseModel):
    type: str = ProviderType.OPENAI
    provider: str = ProviderType.OPENAI
    model: str = "gpt-4o"
    api_key: str = ""
    base_url: Optional[str] = None
    limits: AIProviderLimits = Field(default_factory=AIProviderLimits)
    iter_id: str = "v1"

class FallbackStrategyConfig(BaseModel):
    primary: str = ""
    fallback: str = ""
    max_retries: int = Field(3, ge=0)

class TranslationSettings(BaseModel):
    """🚀 [V24.0] 翻译与算力网关配置主权"""
    enable_ai: bool = True
    strategy: StrategyType = StrategyType.SINGLE
    primary_node: str = "default"
    fallback_node: str = ""
    fallback_config: Optional[FallbackStrategyConfig] = None
    providers: Dict[str, TranslationProvider] = Field(default_factory=dict)
    prompts: PromptTemplates = Field(default_factory=PromptTemplates)
    
    # 🎯 物理算力控制阀
    llm_concurrency: int = Field(4, ge=1, le=32)
    api_timeout: float = Field(600.0, ge=1)
    max_retries: int = Field(5, ge=0)
    budget_limit: float = Field(10.0, ge=0)
    temperature: float = Field(0.2, ge=0, le=2)
    max_tokens: int = Field(8192, ge=1)
    
    # 🎯 物理内容保护规则
    max_chunk_size: int = Field(2500, ge=100)
    empty_content_threshold: int = Field(15, ge=0)
    max_slug_length: int = Field(100, ge=10)
    max_seo_description_length: int = Field(200, ge=10)
    slug_mode: str = "ai"
    
    global_proxy: str = ""
    custom_prompts: Dict[str, str] = Field(default_factory=dict)
    
    # 🚀 [V15.8] 韧性感知
    resilience: Optional[Any] = None
