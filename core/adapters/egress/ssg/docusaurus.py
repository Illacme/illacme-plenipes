#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Docusaurus SSG Adapter
模块职责：负责 Docusaurus v2/v3 语法的标准化转换。
🛡️ [AEL-Iter-v5.3]：物理隔离的渲染插件实现。
"""

from typing import Dict, Any, Tuple
from .base import BaseSSGAdapter

class DocusaurusAdapter(BaseSSGAdapter):
    """🚀 Docusaurus 专属渲染引擎"""
    
    _GENERIC_MAP = {
        'info': 'info', 'note': 'info', 'warning': 'warning',
        'danger': 'danger', 'error': 'danger', 'success': 'success', 'tip': 'tip'
    }

    def render_callout(self, g_type: str, title: str, body: str) -> str:
        target_type = self._GENERIC_MAP.get(g_type.lower(), 'info')
        # Docusaurus 使用 ::: 容器语法 (无方括号)
        res = f"\n:::{target_type}"
        if title: res += f"{{{title}}}"
        res += f"\n{body}\n:::\n\n"
        return res

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        new_fm = fm.copy()
        # Docusaurus 特有的最后修改时间格式
        if hasattr(date_obj, 'strftime'):
            new_fm['last_update'] = {'date': date_obj.strftime('%Y-%m-%d')}
        return new_fm
