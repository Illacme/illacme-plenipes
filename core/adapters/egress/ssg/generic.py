#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter
模块职责：通用模板渲染器，作为兜底或标准 Markdown 转换使用。
🛡️ [AEL-Iter-v5.3]：基于模板驱动的柔性处理器。
"""

import re
from typing import Dict, Any, Tuple
from .base import BaseSSGAdapter

class GenericSSGAdapter(BaseSSGAdapter):
    """🚀 通用模板渲染引擎"""
    
    def render_callout(self, g_type: str, title: str, body: str) -> str:
        body_quoted = '\n> '.join(body.split('\n'))
        # 默认使用 Markdown 增强语法 (Admonitions style)
        return f"\n> [!{g_type.upper()}] {title}\n> {body_quoted}\n\n"

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        return fm
