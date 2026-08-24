#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG Rendering Base (Central Hub)
模块职责：定义 SSG 输出端渲染器的抽象基类协议与全局导航/主题参数分发门面。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
"""
import abc
import os
import json
from typing import Tuple, Dict, Any, List

from .mixins import CITemplateMixin
from .base_shards.ssg_nav_synthesizer import SSGNavSynthesizer, SLOT_I18N_FALLBACK
from .base_shards.ssg_theme_compiler import SSGThemeCompiler

__all__ = ["BaseSSGAdapter", "SLOT_I18N_FALLBACK"]


class BaseSSGAdapter(CITemplateMixin, abc.ABC):
    PLUGIN_ID = "generic"
    """所有 SSG 渲染插件的抽象基类"""

    @classmethod
    def get_default_path_mappings(cls) -> Dict[str, str]:
        """🚀 [V76.0] 声明该适配器推荐的原生默认物理寻址映射"""
        return {
            'source_dir': "src/content",
            'site_dir': "dist",
            'assets_dir': "public/assets",
            'graph_json_dir': "public"
        }

    @classmethod
    def get_build_command(cls) -> str:
        """🚀 [V105.0] 默认 SSG 静态构建命令"""
        return "python plenipes.py --sync"

    def __init__(self, theme_settings: Any = None, engine=None):
        self.theme_settings = theme_settings
        self.engine = engine
        self.default_lang = "zh"
        # 🚀 [V11.2] 双相出口扩展名定义
        self.output_extensions = {
            "source": None,  # 🚀 [V12.0] None 表示跟随原文件后缀
            "static": ".html"
        }
        # 🚀 [V11.2] 默认语言路径契约：是否强制在物理路径中包含语言前缀
        self.force_default_lang_prefix = False
        # 🚀 [V15.6] 元数据主权：定义哪些输出后缀支持 Frontmatter
        self.frontmatter_extensions = [".md", ".mdx", ".markdown"]
        # 🚀 [V80.0] 自动物理探测并加载主题自描述 JSON Schema 协议
        self.theme_schema = {}
        if self.theme_settings:
            theme_name = getattr(self.theme_settings, 'name', 'sovereign')
            if theme_name == 'default':
                theme_name = 'sovereign'
            if self.engine and hasattr(self.engine, 'paths') and self.engine.paths:
                themes_root = self.engine.paths.get("themes", "themes")
            elif self.engine and hasattr(self.engine, '_resolve_path'):
                themes_root = self.engine._resolve_path("themes")
            else:
                themes_root = "themes"
            schema_path = os.path.join(themes_root, theme_name, "theme.schema.json")
            if os.path.exists(schema_path):
                try:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        self.theme_schema = json.load(f)
                except Exception:
                    pass

    def get_custom_options(self) -> Dict[str, Any]:
        """
        🚀 [V80.0] 获取并合并强校验的主题自定义选项映射。
        自动将用户填写的 theme_settings.options 与主题 schema 默认值进行深层合并，实现自愈降级。
        """
        options = {}
        properties = self.theme_schema.get("properties", {})
        for key, prop in properties.items():
            if "default" in prop:
                options[key] = prop["default"]

        # 🚀 [Unified Promotion Architecture] 引入全局基础信息继承层 (I&O Engine)
        if hasattr(self, 'engine') and self.engine and hasattr(self.engine, 'config'):
            cfg = self.engine.config

            # 自愈逻辑：site_name Fallback 为 imprint_name/press_name; site_description Fallback 为 imprint_description
            g_site_name = getattr(cfg, "site_name", None) or getattr(cfg, "imprint_name", None)
            g_site_desc = getattr(cfg, "site_description", None) or getattr(cfg, "imprint_description", None)

            # 版权声明自愈逻辑：彻底合并为单数据源，直接继承自全域默认版权设置 frontmatter_defaults.copyright
            fm_defaults = getattr(cfg, "frontmatter_defaults", {}) or {}
            g_copyright = fm_defaults.get("copyright", None)

            global_promotions = {
                "site_name": g_site_name,
                "site_description": g_site_desc,
                "favicon_path": getattr(cfg, "favicon_path", None),
                "logo_path": getattr(cfg, "logo_path", None),
                "footer_copyright": g_copyright
            }

            for g_key, g_val in global_promotions.items():
                if g_val is not None and str(g_val).strip() != "":
                    options[g_key] = g_val

        if self.theme_settings and hasattr(self.theme_settings, 'options') and self.theme_settings.options:
            for key, val in self.theme_settings.options.items():
                if val is not None and str(val).strip() != "":
                    options[key] = val
        return options

    @abc.abstractmethod
    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """[Contract] 执行特定 SSG 的语法转换与元数据增强。"""
        pass

    def supports_frontmatter(self, ext: str) -> bool:
        """🚀 [V15.6] 判定特定扩展名是否支持元数据头"""
        if not ext:
            return False
        return ext.lower() in self.frontmatter_extensions

    def get_output_schema(self) -> List[str]:
        """🚀 [V11.2] 获取该适配器支持的输出出口列表。"""
        schema = ["source"]
        if hasattr(self, 'active_renderer') and self.active_renderer:
            schema.append("static")
        return schema

    def get_feature_slots(self) -> Dict[str, Dict[str, str]]:
        """🚀 [V56.0/V80.0] 意图感知协议：声明该适配器支持的功能槽及其物理路径映射。
        优先从 theme.schema.json 中动态读取，实现数据驱动的零代码适配。"""
        if hasattr(self, 'theme_schema') and self.theme_schema and 'slots' in self.theme_schema:
            return self.theme_schema['slots']

        return {
            "docs": {"label": "文档中心", "single": "docs", "multi": "i18n/{lang}/docs"},
            "blog": {"label": "博客文章", "single": "blog", "multi": "i18n/{lang}/blog"},
            "pages": {"label": "独立页面", "single": "pages", "multi": "i18n/{lang}/pages"},
            "static": {"label": "静态资产", "single": "static", "multi": "static"}
        }

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        """[Sovereignty] 物理元数据方言适配"""
        return fm

    def inject_seo(self, fm: dict, desc_or_data: Any, keywords: list = None) -> dict:
        """[SEO] 框架感知的 SEO 字段映射协议"""
        from .seo_helper import inject_seo_helper
        return inject_seo_helper(fm, desc_or_data, keywords)

    def get_language_code(self, logic_code: str) -> str:
        """[Sovereignty] 物理路径语种对齐。"""
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logic_code)
        if not self.force_default_lang_prefix and iso_code == LanguageHub.resolve_to_iso(self.default_lang):
            return ""
        return LanguageHub.get_physical_path(iso_code, "generic")

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        """[Sovereignty] 获取当前 SSG 的多语言路径模版。"""
        return "{lang}/{sub_dir}"

    def generate_navigation_items(self) -> Dict[str, Any]:
        """
        🧭 [V100.9 Universal Navigation Synthesis]
        根据引擎配置的 route_matrix 自动合成适配各 SSG 主题的全景导航结构。
        委派至 SSGNavSynthesizer 执行。
        """
        return SSGNavSynthesizer.generate_navigation_items(self)

    def compile_theme_options(self) -> bool:
        """
        🎯 [SSG 热对齐] 将用户最新的自定义主题选项编译并输出为物理层样式，
        委派至 SSGThemeCompiler 执行。
        """
        return SSGThemeCompiler.compile_theme_options(self)
