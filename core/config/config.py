#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Manager (强类型配置中枢)
🛡️ [AEL-Iter-v5.3]：基于分层架构的 TDR 复健版本。
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

from .config_models import (
    SystemSettings, TranslationSettings, IngressSettings, SEOSettings,
    I18nSettings, SyndicationSettings, PublishControl, ImageSettings,
    TimelineSettings, ThemeSettings, TranslationProvider, SyntaxPreset
)

logger = logging.getLogger("Illacme.plenipes")

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
                else: d[k] = v
            return d

        abs_base = os.path.abspath(os.path.expanduser(self.config_path))
        with open(abs_base, 'r', encoding='utf-8') as f:
            base_cfg = yaml.safe_load(f) or {}
        
        # 🚀 [Rule 11.5] 支持递归配置文件包含
        base_cfg = self._resolve_includes(base_cfg, os.path.dirname(abs_base))

        local_path = os.path.join(os.path.dirname(abs_base), 'config.local.yaml')
        if os.path.exists(local_path):
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    local_cfg = yaml.safe_load(f) or {}
                # 同时也为 local 配置文件支持 include
                local_cfg = self._resolve_includes(local_cfg, os.path.dirname(abs_base))
                base_cfg = deep_update(base_cfg, local_cfg)
            except Exception: pass
        return base_cfg

    def _resolve_includes(self, data: Any, base_dir: str) -> Any:
        """递归解析 YAML 中的 include 指令"""
        if isinstance(data, dict):
            # 处理当前层级的 include
            if "include" in data:
                include_target = data.pop("include")
                targets = [include_target] if isinstance(include_target, str) else include_target
                if isinstance(targets, list):
                    for t in targets:
                        abs_include = os.path.join(base_dir, t)
                        if os.path.exists(abs_include):
                            try:
                                with open(abs_include, 'r', encoding='utf-8') as f:
                                    included_data = yaml.safe_load(f) or {}
                                # 递归解析子文件中的 include
                                included_data = self._resolve_includes(included_data, os.path.dirname(abs_include))
                                # 执行深度合并
                                def deep_update(d, u):
                                    for k, v in u.items():
                                        if isinstance(v, collections.abc.Mapping):
                                            d[k] = deep_update(d.get(k, {}), v)
                                        else: d[k] = v
                                    return d
                                data = deep_update(data, included_data)
                            except Exception as e:
                                logger.warning(f"⚠️ 配置文件包含失败 [{t}]: {e}")
            
            # 递归处理所有子项
            for k, v in data.items():
                data[k] = self._resolve_includes(v, base_dir)
        elif isinstance(data, list):
            return [self._resolve_includes(item, base_dir) for item in data]
        return data

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
                        else: init_data[name] = val
                    elif hasattr(f.type, '__origin__') and f.type.__origin__ is dict:
                        child_type = f.type.__args__[1]
                        if hasattr(child_type, '__dataclass_fields__'):
                            init_data[name] = {k: from_dict(child_type, v) for k, v in val.items()}
                        else: init_data[name] = val
                    else: init_data[name] = val
            return cls(**init_data)

        # 🚀 兼容性修复
        if 'system' in self._raw_config:
            s = self._raw_config.get('system')
            if 'system_tuning' in self._raw_config:
                tuning = self._raw_config.get('system_tuning')
                if tuning and 'max_concurrent_workers' in tuning: 
                    s['max_workers'] = tuning.get('max_concurrent_workers')
        
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
            logger.error(f"🛑 路径不存在: {abs_vault}")
            sys.exit(1)

    def _audit_ai_services(self):
        t = self.config.translation
        for name, p in t.providers.items():
            key = getattr(p, 'api_key', '')
            if key and "HERE" in key:
                logger.warning(f"⚠️ [配置风险] AI 节点 '{name}' 的 API_KEY 包含默认占位符。")

def load_config(path: str = "config.yaml") -> Configuration:
    manager = ConfigManager(path)
    return manager.config
