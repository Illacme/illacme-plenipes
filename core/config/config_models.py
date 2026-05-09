#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Models (Facade)
职责：聚合系统、AI、主题等模块化配置模型，提供统一的数据结构。
🛡️ [V24.0] Pydantic 严格校验体系：工业级配置审计根模型。
"""
import os
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Dict, Optional, Any

# 🚀 导入模块化后的子配置
from .models.base import LogFormat, ProviderType, StrategyType
from .models.system import SystemSettings, ConcurrencySettings, ResilienceSettings, WatchdogSettings
from .models.ai import TranslationSettings, TranslationProvider, AIProviderLimits, PromptTemplates
from .models.theme import ThemeSettings, ImageSettings
from .models.plugins import PluginSettings
from .models.governance import GovernanceSettings, PublishingMode, SeoStrategy

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
    enable_multilingual: bool = True
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
    id: str
    name: str
    description: Optional[str] = None

class WebhookEndpoint(BaseModel):
    """🚀 本地 Webhook 物理端点 (授权层)"""
    url: str
    secret: Optional[str] = None
    enabled: bool = True

class PublishControl(BaseModel):
    model_config = ConfigDict(extra='allow')
    exclude_patterns: List[str] = Field(default_factory=list)

    # 🔗 Webhook 三层治理矩阵
    webhook_enabled: bool = False
    webhook_registry: Dict[str, WebhookDefinition] = Field(default_factory=dict) # 全局/本地：能力清单
    webhook_endpoints: Dict[str, WebhookEndpoint] = Field(default_factory=dict) # 本地：物理授权
    active_webhook_ids: List[str] = Field(default_factory=list)                # 品牌：业务点火
    
    webhook_timeout: float = Field(10.0, ge=1)
    append_credit: bool = False
    credit_text: str = ""
    direct_upload: Dict[str, Any] = Field(default_factory=dict)

class SeoSettings(BaseModel):
    enabled: bool = True
    generate_description: bool = True
    generate_keywords: bool = True
    autopilot_enabled: bool = True

class RouteItem(BaseModel):
    """🚀 [V55.26] 路由矩阵项：支持频道级的方言与风格绑定"""
    source: str
    prefix: str
    target_slot: str = "docs" # 🚀 [V56.0] 意图感知：docs, blog, pages 等
    style: Optional[str] = None # 🔗 频道级方言映射，优先级高于全局 active_style
    
class Configuration(BaseModel):
    """💎 [Illacme Plenipes] 全局配置模型总纲"""
    
    version: str = "24.0"
    
    # 核心物理基础设施
    imprint_name: str = Field(default="Illacme Press", alias="press_name")
    imprint_description: str = Field(default="在此输入品牌介绍/格言...", alias="press_description")
    active_imprint: Optional[str] = None # 🚀 [V52.10] 当前激活的物理品牌 ID
    vault_root: str = "./content-vault"
    metadata_dir: str = "metadata"
    active_theme: str = "default"
    site_url: str = ""
    lang_mapping: Dict[str, str] = Field(default_factory=dict)
    
    # 全局出站映射
    output_paths: Dict[str, str] = Field(default_factory=lambda: {
        "markdown_dir": "./themes/{theme}/src/content/docs",
        "assets_dir": "./themes/{theme}/public/assets",
        "graph_json_dir": "./themes/{theme}/public"
    })
    
    # 路由矩阵
    route_matrix: List[RouteItem] = Field(default_factory=list)

    def get_theme_metadata_dir(self) -> str:
        """🎨 获取主题专属元数据目录"""
        return os.path.join(self.metadata_dir, "themes", self.active_theme)

    def get_ledger_path(self) -> str:
        """🚀 [V55.26] 主权账本路径对正：强制执行主题子目录隔离"""
        return os.path.join(self.get_theme_metadata_dir(), "ledger.db")

    def get_ai_metadata_dir(self) -> str:
        """🧠 获取 AI 算力与语义知识目录"""
        return os.path.join(self.metadata_dir, "ai")

    def get_core_metadata_dir(self) -> str:
        """🛡️ 获取品牌核心治理与审计目录"""
        return os.path.join(self.metadata_dir, "core")

    def get_runtime_metadata_dir(self) -> str:
        """⚡ 获取运行时态缓存与日志目录"""
        return os.path.join(self.metadata_dir, "runtime")

    def get_audit_db_path(self) -> str:
        """🛡️ 获取全量审计账本路径"""
        filename = self.system.data_paths.get("audit_db", "audit.db")
        return os.path.join(self.get_core_metadata_dir(), filename)

    def get_lessons_learned_path(self) -> str:
        """🧠 获取 AI 教训流路径"""
        filename = self.system.data_paths.get("lessons_learned", "lessons_learned.json")
        return os.path.join(self.get_ai_metadata_dir(), "brain", filename)

    def get_ai_features_path(self) -> str:
        """🧠 获取 AI 算力特性路径"""
        filename = self.system.data_paths.get("ai_features", "features.json")
        return os.path.join(self.get_ai_metadata_dir(), filename)

    def get_health_report_path(self) -> str:
        """🛰️ 获取哨兵健康报告路径"""
        filename = self.system.data_paths.get("health_log", "sentinel_health.json")
        return os.path.join(self.get_core_metadata_dir(), filename)

    def get_sync_stats_path(self) -> str:
        """📊 获取当前主题的同步统计路径"""
        filename = self.system.data_paths.get("sync_stats", "sync_stats_{theme}.json")
        filename = filename.replace("{theme}", self.active_theme)
        return os.path.join(self.get_theme_metadata_dir(), filename)

    def get_link_graph_path(self) -> str:
        """🕸️ 获取当前主题的关系图谱路径"""
        filename = self.system.data_paths.get("link_graph", "link_graph_{theme}.json")
        filename = filename.replace("{theme}", self.active_theme)
        return os.path.join(self.get_theme_metadata_dir(), filename)

    def get_search_index_path(self) -> str:
        """🔍 获取当前主题的搜索索引路径"""
        filename = self.system.data_paths.get("search_index", "search_index_{theme}.json")
        filename = filename.replace("{theme}", self.active_theme)
        return os.path.join(self.get_theme_metadata_dir(), filename)

    def get_vectors_path(self) -> str:
        """🧠 获取向量数据库路径"""
        filename = self.system.data_paths.get("vectors_json", "vectors.json")
        filename = filename.replace("{theme}", self.active_theme)
        return os.path.join(self.get_ai_metadata_dir(), "vectors", filename)

    def get_pulse_path(self) -> str:
        """💓 获取系统心跳路径"""
        filename = self.system.data_paths.get("pulse_json", "pulse_{theme}.json")
        filename = filename.replace("{theme}", self.active_theme)
        return os.path.join(self.get_core_metadata_dir(), filename)

    def get_history_dir(self) -> str:
        """📜 获取系统迭代历史目录"""
        return os.path.join(self.get_core_metadata_dir(), "history")

    def get_timeline_json_path(self) -> str:
        """📝 获取时间轴 JSON 路径"""
        filename = self.timeline.json_path or "timeline_{theme}.json"
        filename = filename.replace("{theme}", self.active_theme)
        return os.path.join(self.get_theme_metadata_dir(), filename)

    def get_timeline_markdown_path(self) -> str:
        """📝 获取时间轴 Markdown 路径"""
        filename = self.timeline.markdown_path or "timeline_{theme}.md"
        filename = filename.replace("{theme}", self.active_theme)
        return os.path.join(self.get_theme_metadata_dir(), filename)
    
    def resolve_output_path(self, item: RouteItem, adapter: Any, lang: str = "zh") -> str:
        """🚀 [V56.0] 意图路径解析：根据适配器槽位声明计算物理路径"""
        # 1. 优先尝试从适配器获取功能槽定义
        slots = adapter.get_feature_slots() if hasattr(adapter, 'get_feature_slots') else {}
        
        if item.target_slot in slots:
            slot = slots[item.target_slot]
            is_multi = self.i18n_settings.enable_multilingual
            
            # 根据多语言状态选择模版
            path_tmpl = slot.get("multi" if is_multi else "single", "")
            
            # 🛡️ 安全回退：如果适配器未定义多语言模版，则降级使用单语言
            if is_multi and not path_tmpl:
                path_tmpl = slot.get("single", "")
                
            # 2. 渲染语种占位符
            from core.utils.language_hub import LanguageHub
            physical_lang = LanguageHub.resolve_to_iso(lang)
            # 如果是默认语言且未强制前缀，路径中可能不需要 lang 段（取决于适配器实现，此处先简单替换）
            res_path = path_tmpl.replace("{lang}", physical_lang)
            return res_path
            
        # 3. 如果槽位不存在，回退到 prefix 原始逻辑（保持向后兼容）
        return item.prefix
    
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
        populate_by_name=True,
        protected_namespaces=(),
        extra='ignore'
    )

    # 兼容性属性映射逻辑 (V24.0 纯化)
    def model_post_init(self, __context: Any) -> None:
        # 运行时动态同步
        if self.translation and self.system:
            self.translation.resilience = self.system.resilience

    def dump_to_disk(self, path: str):
        """🚀 [V50.3] 物理持久化：将当前配置状态回写至磁盘"""
        import yaml
        # 🚀 [修复] 使用 mode='json' 确保枚举等对象被序列化为纯文本，防止 yaml.safe_dump 报错
        data = self.model_dump(exclude_unset=True, mode='json')
        # 🚀 [V53.0] 治理字段强制持久化：确保运行时修改的出版模式不被 exclude_unset 丢弃
        data['governance'] = self.governance.model_dump(mode='json')
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
