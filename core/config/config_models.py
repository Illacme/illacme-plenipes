#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Models (Facade)
职责：聚合系统、AI、主题等模块化配置模型，提供统一的数据结构。
🛡️ [V24.0] Pydantic 严格校验体系：工业级配置审计根模型。
"""

import os
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Dict, Optional, Any

# 🚀 导入模块化后的子配置
from .models.base import LogFormat, ProviderType, StrategyType
from .models.system import SystemSettings, ConcurrencySettings, ResilienceSettings, WatchdogSettings
from .models.ai import TranslationSettings, AIProviderLimits, PromptTemplates
from .models.theme import ThemeSettings, ImageSettings
from .models.plugins import PluginSettings
from .models.governance import GovernanceSettings, PublishingMode, SeoStrategy
from .models.publishing import (
    I18nSource,
    InjectionSettings,
    I18nTarget,
    I18nSettings,
    IngressSettings,
    TimelineSettings,
    WebhookDefinition,
    WebhookEndpoint,
    PublishControl,
    SeoSettings,
    RouteItem,
)
from .models.paths_mixin import ConfigurationPathsMixin

# 保持对外统一导出
__all__ = [
    "LogFormat",
    "ProviderType",
    "StrategyType",
    "SystemSettings",
    "ConcurrencySettings",
    "ResilienceSettings",
    "WatchdogSettings",
    "TranslationSettings",
    "AIProviderLimits",
    "PromptTemplates",
    "ThemeSettings",
    "ImageSettings",
    "PluginSettings",
    "GovernanceSettings",
    "PublishingMode",
    "SeoStrategy",
    "I18nSource",
    "InjectionSettings",
    "I18nTarget",
    "I18nSettings",
    "IngressSettings",
    "TimelineSettings",
    "WebhookDefinition",
    "WebhookEndpoint",
    "PublishControl",
    "SeoSettings",
    "RouteItem",
    "ConfigurationPathsMixin",
    "Configuration",
]


class Configuration(ConfigurationPathsMixin, BaseModel):
    """💎 [Illacme Plenipes] 全局配置模型总纲"""

    version: str = "24.0"

    # 核心物理基础设施
    imprint_name: str = Field(default="Illacme Press", alias="press_name")
    imprint_description: str = Field(default="在此输入品牌介绍/格言...", alias="press_description")
    active_imprint: Optional[str] = None  # 🚀 [V52.10] 当前激活的物理品牌 ID
    vault_root: str = ""
    metadata_dir: str = "metadata"
    active_theme: str = "sovereign"
    site_url: str = ""
    lang_mapping: Dict[str, str] = Field(default_factory=dict)
    block_cache_dir: Optional[str] = None  # 🚀 [V100.4] 自定义段落缓存物理路径
    block_cache_shard_levels: int = Field(default=1, ge=0, le=3, description="🚀 [V100.4] 段落缓存哈希路径分级层数")
    enable_cache_eviction: bool = False  # 🚀 是否启用算力缓存垃圾回收
    cache_eviction_days: int = Field(default=30, ge=1, description="缓存保留天数")
    cache_max_size_mb: int = Field(default=512, ge=10, description="缓存容量上限 (MB)")

    # 🎨 Sovereign Global Branding & Compliance (Promoted settings)
    site_name: Optional[str] = Field(default=None, description="全局网站展示标题 (多主题共享)")
    site_description: Optional[str] = Field(default=None, description="网站全局描述与 SEO Slogan")
    favicon_path: Optional[str] = Field(default=None, description="全站 Favicon 图标物理/相对路径")
    logo_path: Optional[str] = Field(default=None, description="通用品牌视觉 Logo 物理/相对路径")

    # 全局出站映射 (Optional 零配设计)
    output_paths: Optional[Dict[str, str]] = None

    # 路由矩阵
    route_matrix: List[RouteItem] = Field(default_factory=list)

    # 子配置组合
    system: SystemSettings = Field(default_factory=SystemSettings)
    ingress_settings: IngressSettings = Field(default_factory=IngressSettings)
    i18n_settings: I18nSettings = Field(default_factory=I18nSettings)
    translation: TranslationSettings = Field(default_factory=TranslationSettings)
    theme_options: Dict[str, ThemeSettings] = Field(default_factory=dict)
    framework_adapters: Dict[str, Any] = Field(default_factory=dict)
    seo_settings: SeoSettings = Field(default_factory=SeoSettings)
    image_settings: ImageSettings = Field(default_factory=ImageSettings)
    image_hosting: Dict[str, Any] = Field(default_factory=dict)
    publish_control: PublishControl = Field(default_factory=PublishControl)
    syndication: Dict[str, Any] = Field(default_factory=dict)
    timeline: TimelineSettings = Field(default_factory=TimelineSettings)
    plugins: PluginSettings = Field(default_factory=PluginSettings)
    governance: GovernanceSettings = Field(default_factory=GovernanceSettings)

    # 🚀 [V24.0] 增强审计字段
    frontmatter_defaults: Dict[str, Any] = Field(default_factory=dict)
    frontmatter_order: List[str] = Field(default_factory=lambda: ['title', 'description', 'keywords', 'author', 'date', 'tags', 'categories'])

    model_config = ConfigDict(
        populate_by_name=True,
        protected_namespaces=(),
        extra='ignore'
    )

    def model_post_init(self, __context: Any) -> None:
        if self.translation and self.system:
            self.translation.resilience = self.system.resilience

    @model_validator(mode='after')
    def validate_publishing_mode_and_ai(self) -> 'Configuration':
        """🚀 [V74.96] 出版模式自动降级与自愈保护机制"""
        local_types = ["ollama", "lmstudio", "local"]
        has_node = False
        if self.translation and self.translation.compute_nodes:
            for node in self.translation.compute_nodes.values():
                if not node.enabled:
                    continue
                node_type = (node.type or "").lower()
                api_key = node.api_key or ""
                if any(t in node_type for t in local_types):
                    has_node = True
                    break
                if len(str(api_key)) > 10 and "your" not in str(api_key).lower():
                    has_node = True
                    break

        ai_enabled = bool(self.translation and self.translation.enable_ai)
        ai_available = ai_enabled and has_node

        if not self.governance:
            return self
        mode = self.governance.publishing_mode
        i18n_enabled = self.i18n_settings.enabled if self.i18n_settings else False

        if not ai_available:
            if mode in (PublishingMode.ENHANCED, PublishingMode.GLOBAL) or i18n_enabled:
                from core.utils.tracing import tlog
                tlog.warning(f"⚠️ [自动降级] AI 算力总控关闭或无可用节点，出版模式降级为 {PublishingMode.BASIC.value}，多语言矩阵重置为关闭")
                self.governance.publishing_mode = PublishingMode.BASIC
                if self.i18n_settings:
                    self.i18n_settings.enabled = False
                if self.translation:
                    self.translation.enable_ai = False
        else:
            if i18n_enabled:
                if mode != PublishingMode.GLOBAL:
                    from core.utils.tracing import tlog
                    tlog.info(f"⚖️ [模式对齐] AI 算力与多语言矩阵均激活，出版模式对齐升阶为 {PublishingMode.GLOBAL.value}")
                    self.governance.publishing_mode = PublishingMode.GLOBAL
            else:
                if mode == PublishingMode.GLOBAL:
                    from core.utils.tracing import tlog
                    tlog.info(f"⚖️ [模式对齐] 多语言矩阵处于关闭状态，出版模式对齐为 {PublishingMode.ENHANCED.value}")
                    self.governance.publishing_mode = PublishingMode.ENHANCED

        from .models.governance import validate_mode_strategy, get_default_strategy
        new_mode = self.governance.publishing_mode
        if not validate_mode_strategy(new_mode, self.governance.seo_strategy):
            old_strategy = self.governance.seo_strategy
            self.governance.seo_strategy = get_default_strategy(new_mode)
            from core.utils.tracing import tlog
            tlog.info(f"⚖️ [策略自愈对正] 出版模式变更为 {new_mode.value}，SEO策略从 {old_strategy.value} 自动对齐重置为默认值 {self.governance.seo_strategy.value}")

        return self

    def dump_to_disk(self, path: str):
        """🚀 [V66.5] 主权分流持久化：智能感应物理与策略层级"""
        import yaml

        data = self.model_dump(exclude_unset=True, mode='json')
        data['governance'] = self.governance.model_dump(mode='json')

        if 'translation' in data and 'resilience' in data['translation']:
            del data['translation']['resilience']

        filename = os.path.basename(path)
        if "imprint" in filename:
            if 'translation' in data and 'compute_nodes' in data['translation']:
                del data['translation']['compute_nodes']

        from core.governance.secret_manager import secrets
        should_encrypt = getattr(getattr(self, "system", None), "encrypt_secrets", True)
        if should_encrypt:
            data = secrets.encrypt_tree(data)
        else:
            data = secrets.decrypt_tree(data)

        from core.utils.common import promote_config_keys
        data = promote_config_keys(data)

        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
