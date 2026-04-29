#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Models (Facade)
职责：聚合系统、AI、主题等模块化配置模型，提供统一的数据结构。
🛡️ [V24.0] Pydantic 严格校验体系：工业级配置审计根模型。
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Dict, Optional, Any

# 🚀 导入模块化后的子配置
from .models.base import LogFormat, ProviderType, StrategyType
from .models.system import SystemSettings, ConcurrencySettings, ResilienceSettings, WatchdogSettings
from .models.ai import TranslationSettings, TranslationProvider, AIProviderLimits, PromptTemplates
from .models.theme import ThemeSettings, ImageSettings
from .models.plugins import PluginSettings
from .models.governance import GovernanceSettings

class I18nSource(BaseModel):
    lang_code: str = "zh"
    name: str = "简体中文"
    prompt_lang: str = "Chinese"

class InjectionSettings(BaseModel):
    replace_placeholders: Dict[str, str] = Field(default_factory=dict)
    prepend_body: Optional[str] = None
    append_body: Optional[str] = None
    imports: List[str] = Field(default_factory=list)

class I18nTarget(BaseModel):
    lang_code: str = "en"
    name: str = "English"
    prompt_lang: str = "English"
    translate_body: bool = True
    translate_title: bool = True
    output_sub_dir: Optional[str] = None

class I18nSettings(BaseModel):
    enable_multilingual: bool = True
    source: I18nSource = Field(default_factory=I18nSource)
    targets: List[I18nTarget] = Field(default_factory=list)
    injection_matrix: Dict[str, InjectionSettings] = Field(default_factory=dict)

class IngressSettings(BaseModel):
    source_type: str = "local"
    source_options: Dict[str, Any] = Field(default_factory=dict)
    active_dialects: List[str] = Field(default_factory=lambda: ["auto"])
    staticize_components: bool = True
    hard_line_break: bool = False
    custom_sanitizers: Dict[str, Any] = Field(default_factory=dict)


    @field_validator('custom_sanitizers', mode='before')
    @classmethod
    def validate_custom_sanitizers(cls, v):
        """🚀 [V24.0] 容错处理：将 YAML 解析出的 None 自动映射为字典"""
        return v or {}

class TimelineSettings(BaseModel):
    enabled: bool = True
    json_path: str = "plenipes_timeline.json"
    markdown_path: str = "timeline.md"
    max_entries: int = 1000

class PublishControl(BaseModel):
    exclude_patterns: List[str] = Field(default_factory=list)
    webhook_enabled: bool = False
    webhook_urls: List[str] = Field(default_factory=list)
    webhook_timeout: float = Field(10.0, ge=1)
    append_credit: bool = False
    credit_text: str = ""
    direct_upload: Dict[str, Any] = Field(default_factory=dict)

class SeoSettings(BaseModel):
    enabled: bool = True
    generate_description: bool = True
    generate_keywords: bool = True
    autopilot_enabled: bool = True

class Configuration(BaseModel):
    """💎 [Omni-Hub] 全局配置模型总纲"""
    model_config = ConfigDict(populate_by_name=True, extra='ignore')
    
    version: str = "24.0"
    
    # 核心物理基础设施
    vault_root: str = "./content-vault"
    metadata_db: str = "metadata"
    active_theme: str = "default"
    site_url: str = ""
    lang_mapping: Dict[str, str] = Field(default_factory=dict)
    
    # 全局出站映射
    output_paths: Dict[str, str] = Field(default_factory=lambda: {
        "markdown_dir": "./themes/{theme}/src/content/docs",
        "assets_dir": "./themes/{theme}/dist/static",
        "graph_json_dir": "./themes/{theme}/public"
    })
    
    # 路由矩阵
    route_matrix: List[Dict[str, str]] = Field(default_factory=list)
    
    # 子配置组合
    system: SystemSettings = Field(default_factory=SystemSettings)
    ingress_settings: IngressSettings = Field(default_factory=IngressSettings)
    i18n_settings: I18nSettings = Field(default_factory=I18nSettings)
    translation: TranslationSettings = Field(default_factory=TranslationSettings)
    theme_options: Dict[str, ThemeSettings] = Field(default_factory=dict)
    framework_adapters: Dict[str, Any] = Field(default_factory=dict)
    seo_settings: SeoSettings = Field(default_factory=SeoSettings)
    image_settings: ImageSettings = Field(default_factory=ImageSettings)
    publish_control: PublishControl = Field(default_factory=PublishControl)
    syndication: Dict[str, Any] = Field(default_factory=dict)
    timeline: TimelineSettings = Field(default_factory=TimelineSettings)
    plugins: PluginSettings = Field(default_factory=PluginSettings)
    governance: GovernanceSettings = Field(default_factory=GovernanceSettings)
    
    # 🚀 [V24.0] 增强审计字段
    frontmatter_defaults: Dict[str, Any] = Field(default_factory=dict)
    frontmatter_order: List[str] = Field(default_factory=lambda: ['title', 'description', 'keywords', 'author', 'date', 'tags', 'categories'])

    model_config = ConfigDict(
        protected_namespaces=(),
        extra='ignore'
    )

    # 兼容性属性映射逻辑 (V24.0 纯化)
    def model_post_init(self, __context: Any) -> None:
        # 运行时动态同步
        if self.translation and self.system:
            self.translation.resilience = self.system.resilience
