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
    translate_system: str = "You are a professional translator. Translate the following Markdown content from {source_lang} to {target_lang}. Keep all Markdown syntax, frontmatter keys, and LaTeX formulas intact. Do not add any explanations."
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
    title_system: str = "You are a professional editor. Translate and polish the following title into {target_lang}. Keep it concise and professional. Output ONLY the title."
    title_user: str = "{title}"
    metadata_system: str = "You are a professional editor. Translate and polish the provided metadata into {target_lang}. Output ONLY the result."
    metadata_user: str = "Type: {meta_type}\nValue: {text}"

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
    bypass_block_patterns: List[str] = Field(default_factory=list)
    glossary: Dict[str, Dict[str, str]] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def migrate_glossary(cls, data):
        if isinstance(data, dict) and "glossary" in data:
            glossary_val = data["glossary"]
            if isinstance(glossary_val, dict):
                is_old_format = len(glossary_val) > 0 and all(isinstance(v, str) for v in glossary_val.values())
                if is_old_format:
                    data["glossary"] = {"en": glossary_val}
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
    
    # 🎯 物理内容保护规则
    max_chunk_size: int = Field(2500, ge=100)
    empty_content_threshold: int = Field(15, ge=0)
    max_slug_length: int = Field(100, ge=10)
    max_seo_description_length: int = Field(200, ge=10)
    slug_mode: str = "ai"
    slug_dir_mode: str = "flat"  # 可选: "flat", "prefix", "nested"
    
    global_proxy: str = ""
    custom_prompts: Dict[str, str] = Field(default_factory=dict)
    
    # 🚀 [V15.8] 韧性感知
    resilience: Optional[Any] = None
    
    # 🎯 里程碑升级：Markdown 翻译高级治理控制
    governance: ContentGovernanceConfig = Field(default_factory=ContentGovernanceConfig)
