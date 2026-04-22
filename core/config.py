#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Manager (强类型配置中枢)
模块职责：提供统一、强类型、具备自愈能力的配置访问接口。
🚀 [V32.4 工业级复归版]：具备单例缓存、本地覆盖、深度合并与物理核验能力。
"""

import os
import sys
import yaml
import logging
import collections.abc
import inspect
from dataclasses import dataclass, field, fields
from typing import Dict, List, Any, Optional
from enum import Enum

logger = logging.getLogger("Illacme.plenipes")

# 🚀 [V32.4] 模块级单例缓存，防止重复点火期间的冗余加载
_config_cache: Optional['Configuration'] = None

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
        'komarev.com', 'wakatime.com',
        'visitor-badge.laobi.icu', 'visitor-badge.glitch.me', 
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
    proxy: str = ""  # 🚀 [V36.0] 节点级专属代理

@dataclass
class TranslationSettings:
    strategy: str = "single"
    global_proxy: str = ""  # 🚀 [V36.0] 全局算力代理
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
class IngressSettings:
    active_dialects: Any = "auto"
    staticize_components: bool = True
    hard_line_break: bool = False
    custom_sanitizers: Dict[str, Dict[str, str]] = field(default_factory=dict)

@dataclass
class SEOSettings:
    enabled: bool = True
    generate_description: bool = True
    generate_keywords: bool = True

@dataclass
class DevToConfig:
    enabled: bool = False
    api_key: str = ""

@dataclass
class MediumConfig:
    enabled: bool = False
    token: str = ""
    author_id: str = ""

@dataclass
class HashnodeConfig:
    enabled: bool = False
    token: str = ""
    publication_id: str = ""

@dataclass
class WordPressConfig:
    enabled: bool = False
    url: str = ""
    username: str = ""
    app_password: str = ""

@dataclass
class LinkedInConfig:
    enabled: bool = False
    access_token: str = ""
    person_urn: str = ""

@dataclass
class GhostConfig:
    enabled: bool = False
    url: str = ""
    admin_api_key: str = ""

@dataclass
class UniversalWebhookConfig:
    enabled: bool = False
    url: str = ""
    auth_token: str = ""

@dataclass
class SyndicationSettings:
    enabled: bool = False
    timeout: float = 15.0
    devto: DevToConfig = field(default_factory=DevToConfig)
    medium: MediumConfig = field(default_factory=MediumConfig)
    hashnode: HashnodeConfig = field(default_factory=HashnodeConfig)
    wordpress: WordPressConfig = field(default_factory=WordPressConfig)
    linkedin: LinkedInConfig = field(default_factory=LinkedInConfig)
    ghost: GhostConfig = field(default_factory=GhostConfig)
    universal_webhook: UniversalWebhookConfig = field(default_factory=UniversalWebhookConfig)

class SyntaxPreset(Enum):
    NONE = "none"
    ADMONITIONS = "admonitions"
    CONTAINERS = "containers"
    LEGACY = "legacy"

@dataclass
class MetadataMapping:
    key: str = ""
    style: str = "plain"
    datetime_format: Optional[str] = None  # 🚀 [GGP] 新增：支持自定义日期输出格式 (如 ISO 8601)

@dataclass
class ThemeSettings:
    syntax_engine: str = "generic"
    syntax_preset: SyntaxPreset = SyntaxPreset.ADMONITIONS
    output_paths: Dict[str, str] = field(default_factory=dict)
    callout_template: Optional[str] = None
    type_mapping: Dict[str, str] = field(default_factory=dict)
    metadata_mapping: Dict[str, MetadataMapping] = field(default_factory=dict)
    lang_mapping: Dict[str, str] = field(default_factory=dict)
    component_mappings: Dict[str, str] = field(default_factory=dict)
    shortcode_mappings: Dict[str, str] = field(default_factory=dict)  # 🚀 [GGP] 新增：通用短代码正则映射表

@dataclass
class I18nSource:
    lang_code: str = "zh"
    name: str = "Chinese"
    dir: str = "src/content/docs"

@dataclass
class I18nTarget:
    lang_code: str = "en"
    name: str = "English"
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
    multilingual_alt: bool = False  # 🚀 [Resonance] 开启后，ADMI 将同步生成多语言描述
    deduplication: bool = False
    enabled: bool = True
    format: str = "webp"
    max_width: int = 1400
    quality: int = 80

@dataclass
class Configuration:
    vault_root: str = "./vault"
    metadata_db: str = ".plenipes/ledger.json"
    active_theme: str = "starlight"
    route_matrix: List[Dict[str, Any]] = field(default_factory=list)
    output_paths: Dict[str, str] = field(default_factory=dict)
    theme_options: Dict[str, ThemeSettings] = field(default_factory=dict)
    system: SystemSettings = field(default_factory=SystemSettings)
    translation: TranslationSettings = field(default_factory=TranslationSettings)
    ingress_settings: IngressSettings = field(default_factory=IngressSettings)
    seo_settings: SEOSettings = field(default_factory=SEOSettings)
    i18n_settings: I18nSettings = field(default_factory=I18nSettings)
    syndication: SyndicationSettings = field(default_factory=SyndicationSettings)
    publish_control: PublishControl = field(default_factory=PublishControl)
    image_settings: ImageSettings = field(default_factory=ImageSettings)
    timeline: TimelineSettings = field(default_factory=TimelineSettings)
    site_url: str = ""
    framework_adapters: Dict[str, Any] = field(default_factory=dict)
    frontmatter_order: List[str] = field(default_factory=list)
    frontmatter_defaults: Dict[str, Any] = field(default_factory=dict)
    lang_mapping: Dict[str, str] = field(default_factory=dict)

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._raw_config = self._load_and_merge()
        self.config = self._build_typed_config()
        self._post_process()

    def _load_and_merge(self) -> Dict[str, Any]:
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, collections.abc.Mapping):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d

        abs_base = os.path.abspath(os.path.expanduser(self.config_path))
        with open(abs_base, 'r', encoding='utf-8') as f:
            base_cfg = yaml.safe_load(f) or {}

        local_path = os.path.join(os.path.dirname(abs_base), 'config.local.yaml')
        if os.path.exists(local_path):
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    local_cfg = yaml.safe_load(f) or {}
                base_cfg = deep_update(base_cfg, local_cfg)
                print("⚙️ [系统] 已激活【本地沙盒覆盖】配置 (config.local.yaml)")
            except Exception as e:
                logger.warning(f"⚠️ 加载本地配置失败: {e}")
        
        return base_cfg

    def _build_typed_config(self) -> Configuration:
        def from_dict(cls, data):
            if not isinstance(data, dict): return data
            field_names = {f.name for f in fields(cls)}
            init_data = {}
            for name, val in data.items():
                if name in field_names:
                    f = [f for f in fields(cls) if f.name == name][0]
                    if hasattr(f.type, '__dataclass_fields__'):
                        init_data[name] = from_dict(f.type, val)
                    elif hasattr(f.type, '__origin__') and f.type.__origin__ is list:
                        child_type = f.type.__args__[0]
                        if hasattr(child_type, '__dataclass_fields__'):
                            init_data[name] = [from_dict(child_type, i) for i in val]
                        else:
                            init_data[name] = val
                    elif hasattr(f.type, '__origin__') and f.type.__origin__ is dict:
                        child_type = f.type.__args__[1]
                        if hasattr(child_type, '__dataclass_fields__'):
                            init_data[name] = {k: from_dict(child_type, v) for k, v in val.items()}
                        else:
                            init_data[name] = val
                    elif inspect.isclass(f.type) and issubclass(f.type, Enum):
                        try: init_data[name] = f.type(val)
                        except (ValueError, TypeError): init_data[name] = list(f.type)[0]
                    else:
                        init_data[name] = val
            return cls(**init_data)

        # 🚀 兼容性逻辑复归 [AEL-Iter-013] SAFE-INDEX 豁免标记注入
        if 'system' in self._raw_config:
            s = self._raw_config['system']  # SAFE-INDEX: guarded by 'in' check above
            if 'system_tuning' in self._raw_config:
                tuning = self._raw_config['system_tuning']  # SAFE-INDEX: guarded by 'in' check above
                if 'max_concurrent_workers' in tuning: s['max_workers'] = tuning['max_concurrent_workers']
            if 'network_settings' in self._raw_config:
                s['network_settings'] = self._raw_config['network_settings']  # SAFE-INDEX: guarded by 'in' check above

        return from_dict(Configuration, self._raw_config)

    def _post_process(self):
        theme = self.config.active_theme
        paths = self.config.output_paths
        defaults = {
            'markdown_dir': "./themes/{theme}/src/content/docs",
            'assets_dir': "./themes/{theme}/public/assets",
            'graph_json_dir': "./themes/{theme}/public"
        }
        theme_opts = self.config.theme_options.get(theme, ThemeSettings())
        theme_overrides = theme_opts.output_paths
        for k, v in defaults.items():
            raw_v = theme_overrides.get(k) or paths.get(k) or v
            paths[k] = raw_v.replace('{theme}', theme)
        self.config.lang_mapping = theme_opts.lang_mapping
        self._validate_paths()
        self._audit_ai_services()

    def _validate_paths(self):
        abs_vault = os.path.abspath(os.path.expanduser(self.config.vault_root))
        if not os.path.exists(abs_vault):
            logger.error(f"🛑 笔记库路径不存在: {abs_vault}")
            sys.exit(1)

    def _audit_ai_services(self):
        t = self.config.translation
        for name, p in t.providers.items():
            if p.api_key and "HERE" in p.api_key:
                logger.warning(f"⚠️ [配置风险] AI 节点 '{name}' 的 API_KEY 包含默认占位符。")

def load_config(path: str = "config.yaml") -> Configuration:
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    
    manager = ConfigManager(path)
    _config_cache = manager.config
    return _config_cache
