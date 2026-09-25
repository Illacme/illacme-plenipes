# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Search Engine Facade
模块职责：提供全书即时全文检索、上下文 Snippet 提取与正文穿透聚焦门面调度。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

from core.adapters.egress.ebook.epub_reader_search_css import get_epub_search_css
from core.adapters.egress.ebook.epub_reader_search_js import get_epub_search_js

__all__ = ["get_epub_search_css", "get_epub_search_js"]
