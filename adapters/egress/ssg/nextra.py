#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Nextra SSG Adapter
模块职责：负责 Nextra MDX 语法的物理转换与默认路径映射。
🛡️ [V76.0]：高自治适配器，支持 React 组件化 Callout。
"""

from typing import Dict, Any, Tuple
from core.adapters.egress.ssg.base import BaseSSGAdapter

class NextraAdapter(BaseSSGAdapter):
    """🚀 Nextra 专属渲染引擎"""
    PLUGIN_ID = "nextra"
    DISPLAY_NAME = "Nextra Engine"
    VERSION = "V1.0"
    DESCRIPTION = "驱动 Next.js + MDX 的 Nextra 架构排版渲染，支持 React 组件式 Callout 与 Meta 结构。"

    _GENERIC_MAP = {
        'info': ('info', 'ℹ️'), 'abstract': ('info', 'ℹ️'), 'note': ('info', 'ℹ️'), 'question': ('info', 'ℹ️'),
        'warning': ('warning', '⚠️'), 'attention': ('warning', '⚠️'), 'caution': ('warning', '⚠️'),
        'error': ('error', '🚨'), 'bug': ('error', '🚨'), 'danger': ('error', '🚨'),
        'success': ('default', '💡'), 'check': ('default', '💡'), 'tip': ('default', '💡')
    }

    @classmethod
    def get_default_path_mappings(cls) -> Dict[str, str]:
        """🚀 [V76.0] Nextra 推荐的原生默认物理寻址映射"""
        return {
            'source_dir': "pages",
            'static_dir': "out",
            'assets_dir': "public/assets",
            'graph_json_dir': "public"
        }

    def get_feature_slots(self) -> dict:
        """🚀 [V56.0] Nextra 标准布局声明 (对齐 Next.js pages)"""
        return {
            "docs": {
                "label": "文档中心",
                "single": "pages",
                "multi": "pages/{lang}"
            },
            "blog": {
                "label": "博客文章",
                "single": "pages/blog",
                "multi": "pages/{lang}/blog"
            },
            "pages": {
                "label": "展示页面",
                "single": "pages/custom",
                "multi": "pages/{lang}/custom"
            },
            "static": {
                "label": "静态资产",
                "single": "public",
                "multi": "public"
            }
        }

    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """Nextra MDX 渲染：注入 SEO 数据并将 Callout 组件导入引入进来"""
        new_fm = fm.copy()
        if seo_data:
            new_fm = self.inject_seo(new_fm, seo_data.get('description'), seo_data.get('keywords'))
        
        # 智能兼容落地页模板 (Nextra 使用 layout: 'raw')
        if new_fm.get('template') == 'splash':
            new_fm['layout'] = 'raw'
            new_fm.pop('template', None)

        # 确保 Nextra 页面顶部导入了 Callout 组件 (如果文本中包含 <Callout)
        if "<Callout" in body and "import { Callout }" not in body:
            body = "import { Callout } from 'nextra/components'\n\n" + body
            
        return body, new_fm

    def render_callout(self, g_type: str, title: str, body: str) -> str:
        """Nextra 专有的 React <Callout> 标签组件渲染"""
        target_type, emoji = self._GENERIC_MAP.get(g_type.lower(), ('info', 'ℹ️'))
        res = f'\n<Callout type="{target_type}" emoji="{emoji}">\n'
        if title:
            res += f"  **{title}**\n\n"
        # 换行缩进处理，使其在 React Component 内部良好格式化
        body_indented = '\n'.join([f"  {line}" for line in body.split('\n')])
        res += f"{body_indented}\n</Callout>\n\n"
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
