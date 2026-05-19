#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Vitepress SSG Adapter
模块职责：负责 Vitepress 语法的物理转换与默认路径映射。
🛡️ [V76.0]：高自治适配器，独立于核心解耦。
"""

from typing import Dict, Any, Tuple
from core.adapters.egress.ssg.base import BaseSSGAdapter

class VitepressAdapter(BaseSSGAdapter):
    """🚀 Vitepress 专属渲染引擎"""
    PLUGIN_ID = "vitepress"
    DISPLAY_NAME = "Vitepress Engine"
    VERSION = "V1.0"
    DESCRIPTION = "驱动 Vue 驱动的 Vitepress 架构排版渲染，支持 Markdown 增强、Vue 组件与插值感知。"

    _GENERIC_MAP = {
        'info': 'info', 'abstract': 'info', 'note': 'info', 'question': 'info',
        'warning': 'warning', 'attention': 'warning', 'caution': 'warning',
        'error': 'danger', 'bug': 'danger', 'danger': 'danger',
        'success': 'tip', 'check': 'tip', 'tip': 'tip'
    }

    @classmethod
    def get_default_path_mappings(cls) -> Dict[str, str]:
        """🚀 [V76.0] Vitepress 推荐的原生默认物理寻址映射"""
        return {
            'source_dir': "docs",
            'static_dir': ".vitepress/dist",
            'assets_dir': "public/assets",
            'graph_json_dir': "public"
        }

    def get_feature_slots(self) -> dict:
        """🚀 [V56.0] Vitepress 标准布局声明"""
        return {
            "docs": {
                "label": "文档中心",
                "single": "docs",
                "multi": "docs/{lang}"
            },
            "blog": {
                "label": "博客文章",
                "single": "blog",
                "multi": "blog/{lang}"
            },
            "pages": {
                "label": "展示页面",
                "single": "pages",
                "multi": "pages/{lang}"
            },
            "static": {
                "label": "静态资产",
                "single": "public",
                "multi": "public"
            }
        }

    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """Vitepress 渲染逻辑：直接透传内容并注入 SEO 字段"""
        new_fm = fm.copy()
        if seo_data:
            new_fm = self.inject_seo(new_fm, seo_data.get('description'), seo_data.get('keywords'))
        
        # 智能兼容落地页模板 (Vitepress 使用 layout: home)
        if new_fm.get('template') == 'splash':
            new_fm['layout'] = 'home'
            new_fm.pop('template', None)
            
        return body, new_fm

    def render_callout(self, g_type: str, title: str, body: str) -> str:
        """Vitepress 特有的 Native 自定义标题容器渲染"""
        target_type = self._GENERIC_MAP.get(g_type.lower(), 'info')
        res = f"\n::: {target_type}"
        if title:
            res += f" {title}"
        res += f"\n{body}\n:::\n\n"
        return res

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        return fm

    def get_language_code(self, logic_code: str) -> str:
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logic_code)
        
        source_lang = "zh"
        force_prefix = False
        if self.engine and hasattr(self.engine, "config"):
            source_lang = self.engine.config.i18n_settings.source.lang_code
            force_prefix = self.engine.config.i18n_settings.force_source_prefix
            
        return LanguageHub.get_physical_path(
            iso_code,
            theme="generic",
            source_lang=source_lang,
            force_prefix=force_prefix
        )

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        return "{lang}/{sub_dir}"
