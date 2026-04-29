#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter
模块职责：通用模板渲染器，作为兜底或标准 Markdown 转换使用。
🛡️ [AEL-Iter-v5.3]：基于模板驱动的柔性处理器。
"""

from .base import BaseSSGAdapter

class GenericSSGAdapter(BaseSSGAdapter):
    PLUGIN_ID = "generic"
    """🚀 通用模板渲染引擎"""
    def get_output_schema(self) -> list:
        """🚀 [V11.2] 通用适配器默认开启双相分发 (源码 + 静态渲染)"""
        return ["source", "static"]

    def render(self, body: str, fm: dict, seo_data: dict = None, target_lang: str = "en", sub_path: str = "") -> tuple:
        """通用渲染逻辑：直接透传内容并应用 SEO 注入"""
        if seo_data:
            fm = self.inject_seo(fm, seo_data.get('description'), seo_data.get('keywords'))
        return body, fm

    def render_callout(self, g_type: str, title: str, body: str) -> str:
        body_quoted = '\n> '.join(body.split('\n'))
        # 默认使用 Markdown 增强语法 (Admonitions style)
        return f"\n> [!{g_type.upper()}] {title}\n> {body_quoted}\n\n"

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        return fm
