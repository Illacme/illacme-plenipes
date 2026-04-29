#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Starlight SSG Adapter
模块职责：负责 Astro Starlight 语法的标准化转换。
🛡️ [AEL-Iter-v5.3]：物理隔离的渲染插件实现。
"""

from core.adapters.egress.ssg.base import BaseSSGAdapter

class StarlightAdapter(BaseSSGAdapter):
    """🚀 Starlight 专属渲染引擎"""
    
    _GENERIC_MAP = {
        'info': 'note', 'abstract': 'note', 'note': 'note', 'question': 'note',
        'warning': 'caution', 'attention': 'caution',
        'error': 'danger', 'bug': 'danger', 'danger': 'danger',
        'success': 'tip', 'check': 'tip', 'tip': 'tip'
    }

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
        return LanguageHub.get_physical_path(iso_code, "starlight")

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        """
        [Sovereignty] Starlight 特有的多语言路径规范 (通常是根目录下的语言前缀)
        """
        return "{lang}/{sub_dir}"
