#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Config - Publishing & Routing Models
职责：定义多语言 (i18n)、入口 (Ingress)、时间轴 (Timeline)、发布控制 (PublishControl)、SEO 及路由矩阵 (RouteItem) 数据模型。
🛡️ [V24.0] Pydantic 严格校验体系。
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Dict, Optional, Any


class I18nSource(BaseModel):
    lang_code: str = "auto"
    name: str = "智能检测 (Auto Detect)"
    prompt_lang: str = "Auto"


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
    enabled: bool = True
    force_source_prefix: bool = False  # 🚀 [V57.0] 强制原稿使用语言前缀 (默认 false，即发布至 SSG 根目录)
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
    json_path: str = "timeline_{theme}.json"
    markdown_path: str = "timeline_{theme}.md"
    max_entries: int = 1000


class WebhookDefinition(BaseModel):
    """🚀 全局 Webhook 通道定义 (蓝图层)"""
    id: str = ""
    name: str = ""
    description: Optional[str] = None


class WebhookEndpoint(BaseModel):
    """🚀 本地 Webhook 物理端点 (授权层)"""
    url: str = ""
    secret: Optional[str] = None
    enabled: bool = True


class PublishControl(BaseModel):
    model_config = ConfigDict(extra='allow')
    exclude_patterns: List[str] = Field(default_factory=list)

    # 🔗 Webhook 三层治理矩阵
    webhook_enabled: bool = False
    webhook_registry: Dict[str, WebhookDefinition] = Field(default_factory=dict)  # 全局/本地：能力清单
    webhook_endpoints: Dict[str, WebhookEndpoint] = Field(default_factory=dict)    # 本地：物理授权
    active_webhook_ids: List[str] = Field(default_factory=list)                   # 品牌：业务点火

    webhook_timeout: float = Field(10.0, ge=1)
    append_credit: bool = False
    credit_text: str = ""
    direct_upload: Dict[str, Any] = Field(default_factory=dict)


class SeoSettings(BaseModel):
    enabled: bool = True
    generate_description: bool = True
    generate_keywords: bool = True


class RouteItem(BaseModel):
    """🚀 [V55.26 / V100.9] 路由矩阵与全景导航项：支持频道级方言绑定与统一跨 SSG 导航呈现"""
    source: str = ""
    prefix: str = ""
    target_slot: str = "docs"  # 🚀 [V56.0] 意图感知：docs, blog, pages 等
    style: Optional[str] = None  # 🔗 频道级方言映射，优先级高于全局 active_style

    # 🧭 [全新全景导航呈现扩展字段 (100% 向后兼容)]
    nav_label: Optional[str] = None  # 导航栏展示名称（如“文档中心”、“博客资讯”），若为空则自动自愈
    nav_label_i18n: Optional[Dict[str, str]] = None  # 🌐 多语言导航名称定制字典: {"en": "Docs", "ja": "ドキュメント"}
    show_in_nav: bool = True  # 是否在顶部主导航栏展示
    nav_icon: Optional[str] = None  # 导航图标（如 📚, 📰, 🌐 或 emoji）
    nav_position: str = "left"  # 导航位置: 'left' | 'right'
    nav_order: int = 0  # 排序权重 (数字越小越靠前)
    external_url: Optional[str] = None  # 外部链接 (若是纯外部菜单项)

    @field_validator('source', 'prefix', mode='before')
    @classmethod
    def sanitize_null_strings(cls, v: Any) -> str:
        if v is None:
            return ""
        return str(v)
