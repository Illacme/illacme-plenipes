#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Models (Facade)
职责：聚合系统、AI、主题等模块化配置模型，提供统一的数据结构。
🛡️ [V24.0] Pydantic 严格校验体系：工业级配置审计根模型。
"""
import os
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import List, Dict, Optional, Any

# 🚀 导入模块化后的子配置
from .models.base import LogFormat, ProviderType, StrategyType
from .models.system import SystemSettings, ConcurrencySettings, ResilienceSettings, WatchdogSettings
from .models.ai import TranslationSettings, AIProviderLimits, PromptTemplates
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

class RouteItem(BaseModel):
    """🚀 [V55.26 / V100.9] 路由矩阵与全景导航项：支持频道级方言绑定与统一跨 SSG 导航呈现"""
    source: str = ""
    prefix: str = ""
    target_slot: str = "docs" # 🚀 [V56.0] 意图感知：docs, blog, pages 等
    style: Optional[str] = None # 🔗 频道级方言映射，优先级高于全局 active_style
    
    # 🧭 [全新全景导航呈现扩展字段 (100% 向后兼容)]
    nav_label: Optional[str] = None # 导航栏展示名称（如“文档中心”、“博客资讯”），若为空则自动自愈
    nav_label_i18n: Optional[Dict[str, str]] = None # 🌐 多语言导航名称定制字典: {"en": "Docs", "ja": "ドキュメント"}
    show_in_nav: bool = True # 是否在顶部主导航栏展示
    nav_icon: Optional[str] = None # 导航图标（如 📚, 📰, 🌐 或 emoji）
    nav_position: str = "left" # 导航位置: 'left' | 'right'
    nav_order: int = 0 # 排序权重 (数字越小越靠前)
    external_url: Optional[str] = None # 外部链接 (若是纯外部菜单项)

    @field_validator('source', 'prefix', mode='before')
    @classmethod
    def sanitize_null_strings(cls, v: Any) -> str:
        if v is None:
            return ""
        return str(v)
    
class Configuration(BaseModel):
    """💎 [Illacme Plenipes] 全局配置模型总纲"""
    
    version: str = "24.0"
    
    # 核心物理基础设施
    imprint_name: str = Field(default="Illacme Press", alias="press_name")
    imprint_description: str = Field(default="在此输入品牌介绍/格言...", alias="press_description")
    active_imprint: Optional[str] = None # 🚀 [V52.10] 当前激活的物理品牌 ID
    vault_root: str = ""
    metadata_dir: str = "metadata"
    active_theme: str = "sovereign"
    site_url: str = ""
    lang_mapping: Dict[str, str] = Field(default_factory=dict)
    block_cache_dir: Optional[str] = None # 🚀 [V100.4] 自定义段落缓存物理路径，默认为项目根目录下的 .plenipes/blocks
    block_cache_shard_levels: int = Field(default=1, ge=0, le=3, description="🚀 [V100.4] 段落缓存哈希路径分级层数，0为不分级，1为取前两位（如 ab/），2为取前四位（如 ab/cd/），3为取前六位（如 ab/cd/ef/）")
    enable_cache_eviction: bool = False # 🚀 是否启用算力缓存垃圾回收
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

    def get_theme_metadata_dir(self) -> str:
        """🎨 获取品牌/主题专属元数据目录 (主权对正)"""
        theme = self.active_theme or "sovereign"
        if theme == "default": theme = "sovereign"
        return os.path.join(self.metadata_dir, "themes", theme)

    def get_vault_cache_dir(self) -> str:
        """🚀 获取原稿文库公共缓存根目录，若不可用则优雅降级为本地缓存路径"""
        if self.vault_root and os.path.exists(self.vault_root):
            return os.path.abspath(os.path.join(self.vault_root, ".plenipes", "cache"))
        # 优雅降级到本地 imprints/borealis_realm/metadata/runtime/cache
        return os.path.abspath(os.path.join(self.metadata_dir, "runtime", "cache"))

    def get_theme_source_cache_dir(self, theme: str = None) -> str:
        """🚀 获取当前主题在原稿文库公共缓存下的专属源文件缓存路径"""
        theme = theme or self.active_theme or "sovereign"
        if theme == "default": theme = "sovereign"
        return os.path.join(self.get_vault_cache_dir(), "sources", theme)

    def get_ledger_path(self) -> str:
        """🚀 [V55.26] 主权账本路径对正：使用原稿文库全局唯一账本，以跨主题共享元数据"""
        return os.path.join(self.get_vault_cache_dir(), "ledger.db")

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

    def get_knowledge_graph_path(self) -> str:
        """🌌 获取版图全局唯一的知识图谱路径 (脱耦主题)"""
        filename = self.system.data_paths.get("knowledge_graph", "knowledge_graph.json")
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
            from core.config.models.governance import PublishingMode
            is_multi = self.i18n_settings.enabled and self.governance.publishing_mode == PublishingMode.GLOBAL
            
            # 🛡️ [V56.1] 默认语言主权对齐：在全球发布模式下，若传入的 lang 是默认源语种且未开启强制前缀，
            # 则该语种的文档应落在站点根目录（使用 single 模板），而非带语种前缀的多语目录（multi 模板）。
            # 防止 route_prefix 被错误写入 zh/docs 等含语种段的路径，导致 hreflangs 和导航链接全部错误。
            if is_multi:
                from core.utils.language_hub import LanguageHub as _LH
                _src_lang = getattr(self.i18n_settings, 'source', None)
                _src_code = getattr(_src_lang, 'lang_code', 'zh') if _src_lang else 'zh'
                if not _src_code or _src_code == 'auto':
                    _src_code = 'zh'
                _force_prefix = getattr(self.i18n_settings, 'force_source_prefix', False)
                if _LH.resolve_to_iso(lang) == _LH.resolve_to_iso(_src_code) and not _force_prefix:
                    is_multi = False  # 默认语言降级为 single 模板，落在站点根目录
            
            # 根据多语言状态选择模版
            path_tmpl = slot.get("multi" if is_multi else "single", "")
            
            # 🛡️ 安全回退：如果适配器未定义多语言模版，则降级使用单语言
            if is_multi and not path_tmpl:
                path_tmpl = slot.get("single", "")
                
            # 2. 渲染语种占位符
            from core.utils.language_hub import LanguageHub
            physical_lang = LanguageHub.resolve_to_iso(lang)
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

    # 兼容性属性映射逻辑 (V24.0 纯化)
    def model_post_init(self, __context: Any) -> None:
        # 运行时动态同步
        if self.translation and self.system:
            self.translation.resilience = self.system.resilience

    @model_validator(mode='after')
    def validate_publishing_mode_and_ai(self) -> 'Configuration':
        """🚀 [V74.96] 出版模式自动降级与自愈保护机制"""
        # 1. 检查 AI 算力可用性：以算力中心 AI 算力总控开关 (enable_ai) 为准，并探查物理节点
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

        # 2. 获取当前出版模式和多语言矩阵状态
        if not self.governance:
            return self
        mode = self.governance.publishing_mode
        i18n_enabled = self.i18n_settings.enabled if self.i18n_settings else False

        # 3. 校验并自动降级
        # 3.1 AI 算力总控关闭或无可用节点 -> 出版模式强制重置为基础物理出版 (BASIC)，多语言矩阵关闭
        if not ai_available:
            if mode in (PublishingMode.ENHANCED, PublishingMode.GLOBAL) or i18n_enabled:
                from core.utils.tracing import tlog
                tlog.warning(f"⚠️ [自动降级] AI 算力总控关闭或无可用节点，出版模式降级为 {PublishingMode.BASIC.value}，多语言矩阵重置为关闭")
                self.governance.publishing_mode = PublishingMode.BASIC
                if self.i18n_settings:
                    self.i18n_settings.enabled = False
                if self.translation:
                    self.translation.enable_ai = False
        # 3.2 AI 算力开启且节点可用 -> 根据多语言矩阵开关自愈升降阶出版模式
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

        # 4. 降级后，自动对齐重置 SEO 策略
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
        
        # 1. 提取全量数据镜像
        data = self.model_dump(exclude_unset=True, mode='json')
        data['governance'] = self.governance.model_dump(mode='json')
        
        # 🛡️ 架构纯化：剔除冗余的 translation.resilience，强行规定使用全局 system.resilience
        if 'translation' in data and 'resilience' in data['translation']:
            del data['translation']['resilience']
            
        # 🛡️ [V66.5] 物理-策略解耦分流
        filename = os.path.basename(path)
        if "imprint" in filename:
            # 品牌主权层：仅保留策略（选哪个节点、用哪个模型），强制剔除物理节点底座
            if 'translation' in data and 'compute_nodes' in data['translation']:
                del data['translation']['compute_nodes']
        
        # 🚀 [V66.6] “头部键强力提升 (Key Promotion)”协议
        from core.utils.common import promote_config_keys
        data = promote_config_keys(data)

        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
