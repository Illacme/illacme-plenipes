#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Models
模块职责：定义全域强类型配置容器与数据校验模型。
🛡️ [AEL-Iter-v5.3]：核心配置模型分层版本。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class SyntaxPreset(Enum):
    ADMONITIONS = "admonitions"
    CONTAINERS = "containers"
    LEGACY = "legacy"
    NONE = "none"

@dataclass
class WatchdogSettings:
    exclude_dirs: List[str] = field(default_factory=lambda: [".git", "node_modules"])
    exclude_patterns: List[str] = field(default_factory=lambda: [".lock", ".tmp"])
    heavy_task_delay: float = 0.8
    gc_delay: float = 5.0
    handover_delay: float = 0.05

@dataclass
class JanitorSettings:
    global_exclude: List[str] = field(default_factory=lambda: [".git", "node_modules"])
    theme_exclude: Dict[str, List[str]] = field(default_factory=dict)

@dataclass
class NetworkSettings:
    ignored_domains: List[str] = field(default_factory=lambda: [
        'img.shields.io', 'badgen.net', 'badge.fury.io', 'skillicons.dev',
        'github-readme-stats.vercel.app', 'github-readme-streak-stats.herokuapp.com',
        'komarev.com', 'wakatime.com', 'visitor-badge.laobi.icu', 'visitor-badge.glitch.me', 
        'api.visitorbadge.io', 'hits.seeyoufarm.com', 'count.getloli.com'
    ])

@dataclass
class PurificationSettings:
    strip_styles: bool = True
    strip_mdx_imports: bool = True
    strip_comments: bool = True
    strip_code_blocks: bool = True
    strip_jsx_tags: bool = True

@dataclass
class SystemSettings:
    max_workers: int = 8
    log_level: str = "INFO"
    verbose_ai_logs: bool = True
    singleton_port: int = 43210
    auto_save_interval: float = 2.0
    typing_idle_threshold: float = 5.0
    max_depth: int = 3
    enable_asset_audit: bool = True
    ai_context_purification: PurificationSettings = field(default_factory=PurificationSettings)
    watchdog_settings: WatchdogSettings = field(default_factory=WatchdogSettings)
    janitor_settings: JanitorSettings = field(default_factory=JanitorSettings)
    network_settings: NetworkSettings = field(default_factory=NetworkSettings)

@dataclass
class TranslationProvider:
    type: str = "openai-compatible"
    base_url: Optional[str] = None
    url: Optional[str] = None
    api_key: Optional[str] = None
    model: str = "gpt-4o"
    proxy: str = ""

@dataclass
class TranslationSettings:
    strategy: str = "single"
    global_proxy: str = ""
    primary_node: str = "default"
    fallback_node: Optional[str] = None
    routing_threshold: int = 1000
    providers: Dict[str, TranslationProvider] = field(default_factory=dict)
    llm_concurrency: int = 1
    slug_mode: str = "ai"
    api_timeout: float = 600.0
    max_retries: int = 3
    empty_content_threshold: int = 15
    max_chunk_size: int = 2500
    temperature: float = 0.2
    max_tokens: int = 8192
    max_slug_length: int = 100
    max_seo_description_length: int = 200
    custom_prompts: Dict[str, str] = field(default_factory=dict)

@dataclass
class IngressSource:
    path: str
    prefix: str = ""
    type: str = "obsidian"

@dataclass
class IngressSettings:
    sources: List[IngressSource] = field(default_factory=list)
    active_dialects: List[str] = field(default_factory=lambda: ["obsidian"])
    custom_sanitizers: Dict[str, str] = field(default_factory=dict)
    staticize_components: List[str] = field(default_factory=list)
    hard_line_break: bool = False

@dataclass
class SEOSettings:
    enabled: bool = True
    generate_description: bool = True
    generate_keywords: bool = True

@dataclass
class ThemeSettings:
    output_paths: Dict[str, str] = field(default_factory=dict)
    lang_mapping: Dict[str, str] = field(default_factory=dict)
    syntax_preset: SyntaxPreset = SyntaxPreset.NONE
    callout_template: Optional[str] = None
    type_mapping: Dict[str, str] = field(default_factory=dict)
    shortcode_mappings: Dict[str, str] = field(default_factory=dict)
    component_mappings: Dict[str, str] = field(default_factory=dict)
    metadata_mapping: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DevToSettings:
    enabled: bool = False
    api_key: str = ""

@dataclass
class MediumSettings:
    enabled: bool = False
    token: str = ""
    author_id: str = ""

@dataclass
class HashnodeSettings:
    enabled: bool = False
    token: str = ""
    publication_id: str = ""

@dataclass
class WordPressSettings:
    enabled: bool = False
    url: str = ""
    username: str = ""
    app_password: str = ""

@dataclass
class GhostSettings:
    enabled: bool = False
    url: str = ""
    admin_api_key: str = ""

@dataclass
class LinkedInSettings:
    enabled: bool = False
    access_token: str = ""
    person_urn: str = ""

@dataclass
class UniversalWebhookSettings:
    enabled: bool = False
    url: str = ""
    auth_token: str = ""

@dataclass
class SyndicationSettings:
    enabled: bool = False
    targets: List[Dict[str, Any]] = field(default_factory=list)
    timeout: float = 10.0
    devto: DevToSettings = field(default_factory=DevToSettings)
    medium: MediumSettings = field(default_factory=MediumSettings)
    hashnode: HashnodeSettings = field(default_factory=HashnodeSettings)
    wordpress: WordPressSettings = field(default_factory=WordPressSettings)
    ghost: GhostSettings = field(default_factory=GhostSettings)
    linkedin: LinkedInSettings = field(default_factory=LinkedInSettings)
    universal_webhook: UniversalWebhookSettings = field(default_factory=UniversalWebhookSettings)

@dataclass
class I18nSource:
    lang_code: str = "zh-cn"
    name: str = "Chinese"

@dataclass
class I18nTarget:
    lang_code: str = ""
    name: str = ""
    translate_body: bool = True
    translate_title: bool = True
    slug_mode: Optional[str] = None

@dataclass
class I18nSettings:
    enabled: bool = False
    source: I18nSource = field(default_factory=I18nSource)
    targets: List[I18nTarget] = field(default_factory=list)

@dataclass
class PublishControl:
    exclude_patterns: List[str] = field(default_factory=list)
    webhook_enabled: bool = False
    webhook_urls: List[str] = field(default_factory=list)
    webhook_timeout: float = 3.0
    append_credit: bool = False
    credit_text: str = ""

@dataclass
class TimelineSettings:
    enabled: bool = True
    json_path: str = ".plenipes/plenipes_timeline.json"
    markdown_path: str = ".plenipes/timeline.md"
    max_entries: int = 1000

@dataclass
class ImageSettings:
    base_url: str = "/assets/"
    process_images: bool = True
    generate_alt: bool = True
    multilingual_alt: bool = False
    deduplication: bool = False
    enabled: bool = True
    format: str = "webp"
    max_width: int = 1400
    quality: int = 80
