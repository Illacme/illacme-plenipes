#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG Rendering Base
模块职责：定义 SSG 输出端渲染器的基类协议。
🛡️ [AEL-Iter-v5.3]：全链路解耦的渲染基座。
"""
import abc
from typing import Tuple, Dict, Any, List

class BaseSSGAdapter(abc.ABC):
    PLUGIN_ID = "generic"
    """所有 SSG 渲染插件的抽象基类"""
    def __init__(self, theme_settings: Any = None):
        self.theme_settings = theme_settings
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

    @abc.abstractmethod
    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """
        [Contract] 执行特定 SSG 的语法转换与元数据增强。
        """
        pass

    def supports_frontmatter(self, ext: str) -> bool:
        """🚀 [V15.6] 判定特定扩展名是否支持元数据头"""
        if not ext: return False
        return ext.lower() in self.frontmatter_extensions

    def get_output_schema(self) -> List[str]:
        """
        🚀 [V11.2] 获取该适配器支持的输出出口列表。
        默认为 ['source']，如果支持静态渲染则返回 ['source', 'static']。
        """
        schema = ["source"]
        if hasattr(self, 'active_renderer') and self.active_renderer:
            schema.append("static")
        return schema

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        """[Sovereignty] 物理元数据方言适配"""
        return fm

    def inject_seo(self, fm: dict, description: str, keywords: list) -> dict:
        """[SEO] 框架感知的 SEO 字段映射协议"""
        if description: fm['description'] = description
        if keywords: fm['keywords'] = keywords
        return fm

    def get_language_code(self, logic_code: str) -> str:
        """
        [Sovereignty] 物理路径语种对齐。
        """
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logic_code)
        # 🛡️ 如果不强制前缀且为默认语言，返回空字符串以匹配根路径
        if not self.force_default_lang_prefix and iso_code == LanguageHub.resolve_to_iso(self.default_lang):
            return ""
        return LanguageHub.get_physical_path(iso_code, "generic")

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        """
        [Sovereignty] 获取当前 SSG 的多语言路径模版。
        """
        return "{lang}/{sub_dir}"
