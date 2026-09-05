#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Config - AI Models
职责：定义 AI 算力节点、提示词模板与翻译策略。
🛡️ [V24.0] Pydantic 严格校验体系：实现 AI 算力安全审计。
"""
from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Optional, Any
from .base import StrategyType, ProviderType

class AIProviderLimits(BaseModel):
    """🚀 AI 服务提供商限流与并发阈值设定"""
    max_concurrency: int = Field(5, ge=1, le=50)
    timeout: float = Field(60.0, ge=1)
    max_tokens_per_min: int = Field(40000, ge=1000)
    rate_limit_qps: float = Field(10.0, ge=0.1)
    rate_limit_burst: int = Field(20, ge=1)

class PromptTemplates(BaseModel):
    """🚀 大模型指令母本与提示词策略库"""
    translate_system: str = "You are a professional translator. Translate all sentences and lines of the provided Markdown content from {source_lang} to {target_lang}. Do NOT omit or skip any lines (including placeholder text like '在此输入原稿内容...'). Use natural, idiomatic phrasing in {target_lang} (for Japanese, use proper Kanji/Hiragana/Katakana like '無題の原稿'). Keep all Markdown links and tags intact. Do NOT add section wrappers or explanations. Output ONLY the translated text."
    translate_user: str = "### Content ###\n{text}\n### Translation ###"
    seo_system: str = """You are an expert SEO strategist specializing in search engine algorithm optimization.
Analyze the provided content and generate SEO metadata optimized for maximum Click-Through Rate (CTR).

Your output MUST be a valid JSON object with these fields:
- "seo_title": A compelling, click-worthy title (max 60 chars) optimized for search engines
- "description": A persuasive meta description (max 160 chars) with high-value search terms naturally embedded
- "keywords": An array of 5-8 high-relevance keywords/phrases that match current search trends
- "og_title": An Open Graph title optimized for social sharing (can differ from seo_title)

Rules:
- Prioritize clarity and relevance over clickbait
- Include the primary topic keyword in the first 30 chars of the title
- Use natural language that matches search intent
- The description should answer the searcher's likely question
- Output language: {lang_name}"""
    seo_user: str = """### Content to Optimize ###
Title: {title}
Body (excerpt):
{text}

### Generate SEO JSON ###"""
    slug_system: str = "Generate a URL-friendly slug based on the title. Only output the slug string."
    slug_user: str = "{title}"
    expert_guideline_wrapper: str = "\n\n[Expert Remediation - ID:{iter_id}]\n{remedy_block}"
    title_system: str = "You are a professional translator. Translate the following title strictly into {target_lang}. Use natural, idiomatic phrasing in {target_lang} (for Japanese, use proper Kanji/Hiragana/Katakana like '無題の原稿 1' instead of pure Chinese Hanzi). Output ONLY the translated title."
    title_user: str = "{title}"
    metadata_system: str = "You are a professional translator. Translate the given text into {target_lang}. Output ONLY the raw translated text value without any label prefixes, keys, or JSON formatting."
    metadata_user: str = "{text}"

class ComputeNode(BaseModel):
    """🚀 [V66.5] 物理算力节点 - 承载 API 密钥与物理链路"""
    id: str = ""
    type: str = ProviderType.OPENAI
    api_key: str = ""
    base_url: Optional[str] = None
    model: Optional[str] = None
    enabled: bool = True
    last_updated: float = 0
    limits: AIProviderLimits = Field(default_factory=AIProviderLimits)

class FallbackStrategyConfig(BaseModel):
    """🚀 主备算力故障切换的策略配置"""
    primary: str = ""
    fallback: str = ""
    max_retries: int = Field(3, ge=0)

class BlockAction(str, Enum):
    """🚀 块级治理的分流动作枚举"""
    TRANSLATE = "translate"
    BYPASS = "bypass"
    STRIP = "strip"
    PARSE_COMMENTS_ONLY = "parse_comments_only"

class BlockRule(BaseModel):
    """🚀 针对特定语义块设定的专属处理规则"""
    action: BlockAction = BlockAction.TRANSLATE
    style_override: Optional[str] = None
    prompt_override: Optional[str] = None
    mask_strategy: Optional[str] = "default"

class LinkGovernance(BaseModel):
    """🚀 外部与内部超链接遮蔽、翻译与自愈路由设置"""
    translate_labels: bool = True
    translate_anchors: bool = True
    auto_localize_internal_links: bool = True
    external_links_mask_mode: str = "url_only"

class BatchTranslationConfig(BaseModel):
    """🚀 [V120.0] 出版级自适应多段聚合翻译与分包调度控制"""
    enabled: bool = True
    max_batch_paras: int = Field(8, ge=1, le=30)
    max_batch_chars: int = Field(1500, ge=100, le=10000)
    model_tier_adaptive: bool = True
    fallback_on_error: bool = True

class ContentGovernanceConfig(BaseModel):
    """🚀 内容级别的高级翻译治理控制与专有名词对照表"""
    enabled: bool = True
    block_rules: Dict[str, BlockRule] = Field(
        default_factory=lambda: {
            "header": BlockRule(action=BlockAction.TRANSLATE),
            "paragraph": BlockRule(action=BlockAction.TRANSLATE),
            "table": BlockRule(action=BlockAction.TRANSLATE),
            "callout": BlockRule(action=BlockAction.TRANSLATE),
            "code": BlockRule(action=BlockAction.BYPASS),
            "html": BlockRule(action=BlockAction.BYPASS),
            "comment": BlockRule(action=BlockAction.BYPASS)
        }
    )
    link_governance: LinkGovernance = Field(default_factory=LinkGovernance)
    batch_translation: BatchTranslationConfig = Field(default_factory=BatchTranslationConfig)
    bypass_block_patterns: List[str] = Field(default_factory=list)
    glossary: Dict[str, Dict[str, str]] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def migrate_glossary(cls, data):
        if isinstance(data, dict) and "glossary" in data:
            glossary_val = data["glossary"]
            if isinstance(glossary_val, dict):
                # 🚀 智能自愈混合格式：将所有单层键值（旧格式的非 dict）提取出来，并并入默认的 "en" 字典下
                new_glossary = {}
                old_keys = {}
                for k, v in glossary_val.items():
                    if isinstance(v, dict):
                        new_glossary[k] = v
                    else:
                        old_keys[k] = str(v)
                if old_keys:
                    if "en" not in new_glossary:
                        new_glossary["en"] = {}
                    new_glossary["en"].update(old_keys)
                data["glossary"] = new_glossary
        return data

class TranslationSettings(BaseModel):
    """🚀 [V66.5] 翻译与算力网关配置主权 - 物理与策略已完全解耦"""
    enable_ai: bool = True
    strategy: StrategyType = StrategyType.SINGLE
    
    # 🎯 品牌策略层：定义选派逻辑 (🛡️ 产品发布安全版：默认本地算力优先)
    primary_node: str = "lmstudio_local"
    primary_model: str = "qwen/qwen3.5-9b"
    fallback_node: str = "ollama_local"
    fallback_model: str = "qwen/qwen3.5-9b"
    
    active_style: str = "default"
    fallback_config: Optional[FallbackStrategyConfig] = None
    
    # 🛰️ 物理底座层：承载物理连接
    compute_nodes: Dict[str, ComputeNode] = Field(default_factory=dict)
    
    prompts: PromptTemplates = Field(default_factory=PromptTemplates)
    
    # 🎯 物理算力控制阀
    llm_concurrency: int = Field(1, ge=1, le=32)
    api_timeout: float = Field(600.0, ge=1)
    max_retries: int = Field(5, ge=0)
    budget_limit: float = Field(10.0, ge=0)
    temperature: float = Field(0.2, ge=0, le=2)
    max_tokens: int = Field(2048, ge=1)
    enable_thinking: bool = Field(False, description="是否全局启用思维链推理")
    ai_semaphore_timeout: int = Field(3600, ge=1)
    
    # 🎯 物理内容保护规则
    max_chunk_size: int = Field(2500, ge=100)
    empty_content_threshold: int = Field(15, ge=0)
    max_slug_length: int = Field(100, ge=10)
    max_seo_description_length: int = Field(200, ge=10)
    slug_mode: str = "ai"
    slug_dir_mode: str = "nested"  # 默认: "nested" (目录树复刻); 可选: "nested", "flat", "prefix"
    
    global_proxy: str = ""
    custom_prompts: Dict[str, str] = Field(default_factory=dict)
    
    # 🚀 [V15.8] 韧性感知
    resilience: Optional[Any] = None
    
    # 🎯 里程碑升级：Markdown 翻译高级治理控制
    governance: ContentGovernanceConfig = Field(default_factory=ContentGovernanceConfig)
