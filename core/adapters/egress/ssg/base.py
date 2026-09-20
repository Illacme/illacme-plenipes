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
from .base_shards.ssg_link_healer import SSGLinkHealer

__all__ = ["BaseSSGAdapter", "SLOT_I18N_FALLBACK", "SSGLinkHealer"]


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
        self.output_extensions = {
            "source": None,
            "static": ".html"
        }
        self.force_default_lang_prefix = False
        self.frontmatter_extensions = [".md", ".mdx", ".markdown"]
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
            g_site_name = getattr(cfg, "site_name", None) or getattr(cfg, "imprint_name", None)
            g_site_desc = getattr(cfg, "site_description", None) or getattr(cfg, "imprint_description", None)

            fm_defaults = getattr(cfg, "frontmatter_defaults", {}) or {}
            g_copyright = fm_defaults.get("copyright", None)
            g_license = fm_defaults.get("license", None)
            g_author = fm_defaults.get("author", None)
            g_icp = fm_defaults.get("icp_license") or getattr(cfg, "icp_license", None)
            g_police = fm_defaults.get("police_license") or getattr(cfg, "police_license", None)

            global_promotions = {
                "site_name": g_site_name,
                "site_description": g_site_desc,
                "favicon_path": getattr(cfg, "favicon_path", None),
                "logo_path": getattr(cfg, "logo_path", None),
                "footer_copyright": g_copyright,
                "license": g_license,
                "author": g_author,
                "icp_license": g_icp,
                "police_license": g_police
            }

            for g_key, g_val in global_promotions.items():
                if g_val is not None and str(g_val).strip() != "":
                    options[g_key] = g_val

        if self.theme_settings and hasattr(self.theme_settings, 'options') and self.theme_settings.options:
            for key, val in self.theme_settings.options.items():
                if val is not None:
                    options[key] = val

        # 🧭 [Universal Navigation Injection] 将 route_matrix 动态合成的导航项注入 options
        try:
            nav_synthesis = self.generate_navigation_items()
            if nav_synthesis and isinstance(nav_synthesis, dict):
                if nav_synthesis.get('nav_links'):
                    options['nav_links'] = nav_synthesis['nav_links']
                if nav_synthesis.get('nav_links_i18n'):
                    options['nav_links_i18n'] = nav_synthesis['nav_links_i18n']
        except Exception:
            pass

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
        """🚀 [V56.0/V80.0] 意图感知协议：声明该适配器支持的功能槽及其物理路径映射。"""
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

    def normalize_markdown_content(self, body: str, sub_path: str = "", target_lang: str = "zh", clean_url: bool = None) -> str:
        """
        🚀 [Universal Link Healing & Parity] 通用 Markdown/MDX 链接清洗与语法规范化：
        委派至 SSGLinkHealer 执行。
        """
        return SSGLinkHealer.normalize_markdown_content(self, body, sub_path, target_lang, clean_url)

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
        """🧭 [V100.9 Universal Navigation Synthesis] 自动合成全景导航结构"""
        return SSGNavSynthesizer.generate_navigation_items(self)

    def compile_theme_options(self) -> bool:
        """🎯 [SSG 热对齐] 将用户最新的自定义主题选项编译并输出为物理层样式"""
        return SSGThemeCompiler.compile_theme_options(self)

    def get_theme_root(self) -> str:
        """🚀 获取当前主题的物理根目录路径"""
        if self.engine and hasattr(self.engine, 'paths') and self.engine.paths:
            themes_root = self.engine.paths.get("themes", "themes")
        else:
            from core.config.config import THEMES_DIR
            themes_root = THEMES_DIR
        theme_name = getattr(self.theme_settings, 'name', 'generic') if self.theme_settings else 'generic'
        if theme_name in ('default', ''):
            theme_name = 'sovereign'
        return os.path.join(themes_root, theme_name)

    def has_autonomous_blog_engine(self) -> bool:
        """🎨 博客自治能力契约声明"""
        if hasattr(self, 'theme_settings') and getattr(self.theme_settings, 'autonomous_blog', None) is not None:
            return bool(self.theme_settings.autonomous_blog)
        theme_root = self.get_theme_root()
        if theme_root and os.path.exists(theme_root):
            if os.path.exists(os.path.join(theme_root, "scripts", "blog_synthesizer.py")):
                return True
            if os.path.exists(os.path.join(theme_root, "hooks.py")):
                try:
                    with open(os.path.join(theme_root, "hooks.py"), 'r', encoding='utf-8') as f:
                        h_content = f.read()
                        if "BlogSynthesizer" in h_content or "blog" in h_content:
                            return True
                except Exception:
                    pass
        return False

    def is_framework_engine(self) -> bool:
        """🚀 外部框架 SSG 构建能力声明"""
        theme_root = self.get_theme_root()
        if not theme_root or not os.path.exists(theme_root):
            return False
        has_pkg = os.path.exists(os.path.join(theme_root, "package.json"))
        has_cfg = any(os.path.exists(os.path.join(theme_root, f)) for f in (
            "astro.config.mjs", "docusaurus.config.js", "theme.config.jsx",
            ".vitepress", "config.toml", "hugo.toml"
        ))
        return bool(has_pkg or has_cfg)
