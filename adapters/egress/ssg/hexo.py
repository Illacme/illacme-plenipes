#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Hexo SSG Adapter
模块职责：负责 Hexo 语法的物理转换与默认路径映射。
🛡️ [V76.0]：高自治适配器，支持 Hexo Tag Plugins 标签渲染。
"""

from typing import Dict, Any, Tuple
from core.adapters.egress.ssg.base import BaseSSGAdapter

class HexoAdapter(BaseSSGAdapter):
    """🚀 Hexo 专属渲染引擎"""
    PLUGIN_ID = "hexo"
    DISPLAY_NAME = "Hexo Engine"
    VERSION = "V1.0"
    DESCRIPTION = "驱动 Node.js 驱动的 Hexo 排版渲染，完美支持 Hexo Tag Plugins 标签块语法。"

    _GENERIC_MAP = {
        'info': 'info', 'abstract': 'info', 'note': 'info', 'question': 'info',
        'warning': 'warning', 'attention': 'warning', 'caution': 'warning',
        'error': 'danger', 'bug': 'danger', 'danger': 'danger',
        'success': 'success', 'check': 'success', 'tip': 'tip'
    }

    @classmethod
    def get_default_path_mappings(cls) -> Dict[str, str]:
        """🚀 [V76.0] Hexo 推荐的原生默认物理寻址映射"""
        return {
            'source_dir': "source",
            'site_dir': "public",
            'assets_dir': "source/assets",
            'graph_json_dir': "source"
        }

    def get_feature_slots(self) -> dict:
        """🚀 [V56.0] Hexo 标准布局声明 (对齐 Hexo source)"""
        return {
            "docs": {
                "label": "文档中心",
                "single": "source",
                "multi": "source/{lang}"
            },
            "blog": {
                "label": "博客文章",
                "single": "source/_posts",
                "multi": "source/_posts/{lang}"
            },
            "pages": {
                "label": "展示页面",
                "single": "source/custom",
                "multi": "source/{lang}/custom"
            },
            "static": {
                "label": "静态资产",
                "single": "source/assets",
                "multi": "source/assets"
            }
        }

    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """Hexo 渲染逻辑：支持标准 Frontmatter 与 SEO 字段注入"""
        new_fm = fm.copy()
        if seo_data:
            new_fm = self.inject_seo(new_fm, seo_data.get('description'), seo_data.get('keywords'))
        
        # 智能兼容落地页模板 (Hexo 使用 layout: splash)
        if new_fm.get('template') == 'splash':
            new_fm['layout'] = 'splash'
            new_fm.pop('template', None)
            
        return body, new_fm

    def render_callout(self, g_type: str, title: str, body: str) -> str:
        """Hexo Tag Plugins 专属 `{% note class [title] %}` 标签块渲染"""
        target_type = self._GENERIC_MAP.get(g_type.lower(), 'info')
        res = f"\n{{% note {target_type}"
        if title:
            res += f" {title}"
        res += f" %}}\n{body}\n{{% endnote %}}\n\n"
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

    @classmethod
    def get_build_command(cls) -> str:
        """🚀 [V78.0] 返回 Hexo 的标准构建命令"""
        return "npx hexo generate"
