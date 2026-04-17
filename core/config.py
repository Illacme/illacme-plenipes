#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Manager (强类型配置中枢)
模块职责：提供统一、强类型、具备自愈能力的配置访问接口。
🚀 [V32 架构重构]：彻底从 raw dict 转向属性化访问，解决命名歧义与配置遗失问题。
"""

import os
import sys
import yaml
import logging
import collections.abc
from dataclasses import dataclass, field, fields
from typing import Dict, List, Any, Optional

logger = logging.getLogger("Illacme.plenipes")

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

@dataclass
class TranslationSettings:
    strategy: str = "single"
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
class SyndicationSettings:
    enabled: bool = False
    timeout: float = 15.0
    platforms: Dict[str, Any] = field(default_factory=dict)

@dataclass
class I18nSettings:
    enabled: bool = False
    source: Dict[str, Any] = field(default_factory=dict)
    targets: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ThemeSettings:
    """
    🎨 SSG 主题专用适配配置
    支持 Starlight, Docusaurus, VitePress, Nextra, Hugo, Hexo 等全域框架。
    """
    syntax_engine: str = "default"
    output_paths: Dict[str, str] = field(default_factory=dict)
    lang_mapping: Dict[str, str] = field(default_factory=dict)
    callout_template: str = "\n> **{title}**\n> {body_quoted}\n\n"
    type_mapping: Dict[str, str] = field(default_factory=dict)
    metadata_mapping: Dict[str, Any] = field(default_factory=dict)
    component_mappings: Dict[str, str] = field(default_factory=dict)

@dataclass
class PublishControl:
    exclude_patterns: List[str] = field(default_factory=list)
    webhook_enabled: bool = False
    webhook_urls: List[str] = field(default_factory=list)
    webhook_timeout: float = 3.0
    append_credit: bool = False
    credit_text: str = ""

@dataclass
class ImageSettings:
    base_url: str = "/assets/"
    process_images: bool = True
    generate_alt: bool = True
    deduplication: bool = False
    enabled: bool = True
    format: str = "webp"
    max_width: int = 1400
    quality: int = 80

@dataclass
class Configuration:
    vault_root: str = "./vault"
    metadata_db: str = "metadata.db"
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
    site_url: str = ""
    framework_adapters: Dict[str, Any] = field(default_factory=dict)
    frontmatter_order: List[str] = field(default_factory=list)
    frontmatter_defaults: Dict[str, Any] = field(default_factory=dict)
    lang_mapping: Dict[str, str] = field(default_factory=dict)

class ConfigManager:
    """
    🚀 工业级配置管理器
    职责：加载、合并、归一化并校验全量配置。
    """
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._raw_config = self._load_and_merge()
        self.config = self._build_typed_config()
        self._post_process()

    def _load_and_merge(self) -> Dict[str, Any]:
        """合并 config.yaml 与 config.local.yaml"""
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, collections.abc.Mapping):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d

        abs_base = os.path.abspath(os.path.expanduser(self.config_path))
        try:
            with open(abs_base, 'r', encoding='utf-8') as f:
                base_cfg = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"🛑 无法读取主配置 {abs_base}: {e}")
            sys.exit(1)

        local_path = os.path.join(os.path.dirname(abs_base), 'config.local.yaml')
        if os.path.exists(local_path):
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    local_cfg = yaml.safe_load(f) or {}
                base_cfg = deep_update(base_cfg, local_cfg)
                logger.info("⚙️ 已激活【本地沙盒覆盖】配置。")
            except Exception as e:
                logger.warning(f"⚠️ 加载本地配置失败: {e}")
        
        return base_cfg

    def _build_typed_config(self) -> Configuration:
        """将原始嵌套字典转换为强类型 DataClass 对象"""
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
                        # 处理 List[SubDataclass]
                        child_type = f.type.__args__[0]
                        if hasattr(child_type, '__dataclass_fields__'):
                            init_data[name] = [from_dict(child_type, i) for i in val]
                        else:
                            init_data[name] = val
                    elif hasattr(f.type, '__origin__') and f.type.__origin__ is dict:
                        # 🚀 [V32] 处理 Dict[str, SubDataclass]
                        child_type = f.type.__args__[1]
                        if hasattr(child_type, '__dataclass_fields__'):
                            init_data[name] = {k: from_dict(child_type, v) for k, v in val.items()}
                        else:
                            init_data[name] = val
                    else:
                        init_data[name] = val
            return cls(**init_data)

        # 🚀 [语义对齐] 在转换前执行紧急纠偏
        # 针对审计中发现的命名/位置不一致问题
        if 'system' in self._raw_config:
            s = self._raw_config['system']
            # 解决 system_tuning 冗余提取
            if 'system_tuning' in self._raw_config:
                tuning = self._raw_config['system_tuning']
                # 合并 max_concurrent_workers 到 max_workers
                if 'max_concurrent_workers' in tuning:
                    s['max_workers'] = tuning['max_concurrent_workers']
                # 合并 max_transclusion_depth 到 max_depth
                if 'max_transclusion_depth' in tuning:
                    s['max_depth'] = tuning['max_transclusion_depth']

            # 解决 network_settings 顶级映射到 system 节点
            if 'network_settings' in self._raw_config:
                s['network_settings'] = self._raw_config['network_settings']

        if 'translation' in self._raw_config:
            t = self._raw_config['translation']
            if 'system' in self._raw_config and 'ai_concurrency' in self._raw_config['system']:
                t['llm_concurrency'] = self._raw_config['system']['ai_concurrency']

        return from_dict(Configuration, self._raw_config)

    def _post_process(self):
        """物理路径推导与占位符替换"""
        theme = self.config.active_theme
        paths = self.config.output_paths
        
        # 1. 默认路径推导
        defaults = {
            'markdown_dir': "./themes/{theme}/src/content/docs",
            'assets_dir': "./themes/{theme}/public/assets",
            'graph_json_dir': "./themes/{theme}/public"
        }
        
        # 2. 允许主题覆盖全局路径
        theme_opts = self.config.theme_options.get(theme, ThemeSettings())
        theme_overrides = theme_opts.output_paths
        
        for k, v in defaults.items():
            raw_v = theme_overrides.get(k) or paths.get(k) or v
            paths[k] = raw_v.replace('{theme}', theme)
            
        # 3. 提取语种映射
        self.config.lang_mapping = theme_opts.lang_mapping
        
        # 4. 强制物理路径核验
        self._validate_paths()

    def _validate_paths(self):
        """执行基础存活性核验"""
        abs_vault = os.path.abspath(os.path.expanduser(self.config.vault_root))
        if not os.path.exists(abs_vault):
            logger.error(f"🛑 笔记库路径不存在: {abs_vault}")
            sys.exit(1)
        logger.info("🛡️ 配置审计完成：核心物理路径已锁定。")

def load_config(path: str = "config.yaml") -> Configuration:
    manager = ConfigManager(path)
    return manager.config
