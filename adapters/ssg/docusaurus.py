#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Docusaurus SSG Adapter
模块职责：负责 Docusaurus v2/v3 语法的标准化转换。
🛡️ [AEL-Iter-v5.3]：物理隔离的渲染插件实现。
"""

from typing import Tuple, Dict, Any
from core.adapters.egress.ssg.base import BaseSSGAdapter

class DocusaurusAdapter(BaseSSGAdapter):
    """🚀 Docusaurus 专属渲染引擎"""
    
    _GENERIC_MAP = {
        'info': 'info', 'note': 'info', 'warning': 'warning',
        'danger': 'danger', 'error': 'danger', 'success': 'success', 'tip': 'tip'
    }

    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """🚀 [V10.3] Docusaurus 深度渲染：SEO 注入与链接自愈"""
        new_fm = fm.copy()
        
        # 1. 注入 AI 生成的 SEO 元数据
        if seo_data:
            new_fm = self.inject_seo(new_fm, seo_data.get('description'), seo_data.get('keywords'))
            
        # 2. 链接自愈 (Link Healing)
        # 将 [text](V9_Child.md) 转换为语种感知的路径
        import re
        def heal_link(match):
            text, path = match.groups()
            if path.endswith('.md') and not path.startswith('http'):
                # Docusaurus 内部链接通常保持相对或根据 Slug 转换
                # 这里我们确保链接格式符合 Starlight/Docusaurus 混编要求
                return f"[{text}]({path})"
            return match.group(0)
            
        healed_body = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', heal_link, body)
        
        return healed_body, new_fm

    def render_callout(self, g_type: str, title: str, body: str) -> str:
        target_type = self._GENERIC_MAP.get(g_type.lower(), 'info')
        # Docusaurus 使用 ::: 容器语法
        res = f"\n:::{target_type}"
        if title: res += f" {title}"
        res += f"\n{body}\n:::\n\n"
        return res

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        new_fm = fm.copy()
        if hasattr(date_obj, 'strftime'):
            new_fm['last_update'] = {'date': date_obj.strftime('%Y-%m-%d')}
        return new_fm

    def get_language_code(self, logic_code: str) -> str:
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logic_code)
        return LanguageHub.get_physical_path(iso_code, "docusaurus")

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        plugin_map = {
            "docs": "docusaurus-plugin-content-docs/current",
            "blog": "docusaurus-plugin-content-blog",
            "pages": "docusaurus-plugin-content-pages"
        }
        plugin_path = plugin_map.get(source_type.lower(), plugin_map["docs"])
        return f"i18n/{{lang}}/{plugin_path}/{{sub_dir}}"
