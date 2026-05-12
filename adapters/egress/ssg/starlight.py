#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Starlight SSG Adapter
模块职责：负责 Astro Starlight 语法的标准化转换。
🛡️ [AEL-Iter-v5.3]：物理隔离的渲染插件实现。
"""

from typing import Dict, Any, Tuple
from core.adapters.egress.ssg.base import BaseSSGAdapter

class StarlightAdapter(BaseSSGAdapter):
    """🚀 Starlight 专属渲染引擎"""
    PLUGIN_ID = "starlight"
    DISPLAY_NAME = "Starlight Engine"
    DESCRIPTION = "驱动 Astro Starlight 架构的文档渲染，完美支持 Asides 容器语法与物理路径投影。"
    
    _GENERIC_MAP = {
        'info': 'note', 'abstract': 'note', 'note': 'note', 'question': 'note',
        'warning': 'caution', 'attention': 'caution',
        'error': 'danger', 'bug': 'danger', 'danger': 'danger',
        'success': 'tip', 'check': 'tip', 'tip': 'tip'
    }
    def get_feature_slots(self) -> dict:
        """🚀 [V56.0] Starlight 标准布局声明：需对齐主题 sidebar 自动生成规则"""
        return {
            "docs": {
                "label": "文档中心",
                "single": "src/content/docs/docs",
                "multi": "src/content/docs/{lang}/docs"
            },
            "blog": {
                "label": "博客文章",
                "single": "src/content/docs/blog",
                "multi": "src/content/docs/{lang}/blog"
            },
            "pages": {
                "label": "展示页面",
                "single": "src/pages",
                "multi": "src/pages/{lang}"
            },
            "static": {
                "label": "静态资产",
                "single": "public",
                "multi": "public"
            }
        }
    
    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """🚀 [V10.3] Starlight 深度渲染：SEO 注入与元数据对齐"""
        from typing import Tuple
        new_fm = fm.copy()
        
        # 1. 注入 AI 生成的 SEO 元数据
        if seo_data:
            # Starlight 允许直接在 Frontmatter 中使用 description
            if seo_data.get('description'):
                new_fm['description'] = seo_data.get('description')
            
        return body, new_fm

    def render_callout(self, g_type: str, title: str, body: str) -> str:
        target_type = self._GENERIC_MAP.get(g_type.lower(), 'note')
        # Starlight 使用 ::: 容器语法
        res = f"\n:::{target_type}"
        if title: res += f" [{title}]"
        res += f"\n{body}\n:::\n\n"
        return res

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        # Starlight 默认元数据映射
        new_fm = fm.copy()
        if hasattr(date_obj, 'strftime'):
            new_fm['lastUpdated'] = date_obj
        return new_fm

    def get_language_code(self, logic_code: str) -> str:
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logic_code)
        
        # 🚀 [V57.0] 注入主权配置参数
        source_lang = "zh"
        force_prefix = False
        if self.engine and hasattr(self.engine, "config"):
            source_lang = self.engine.config.i18n_settings.source.lang_code
            force_prefix = self.engine.config.i18n_settings.force_source_prefix
            
        return LanguageHub.get_physical_path(
            iso_code, 
            theme="starlight", 
            source_lang=source_lang, 
            force_prefix=force_prefix
        )

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        """
        [Sovereignty] Starlight 特有的多语言路径规范 (通常是根目录下的语言前缀)
        """
        return "{lang}/{sub_dir}"
