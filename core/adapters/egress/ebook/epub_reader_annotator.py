# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Annotator & Quote Card Facade
模块职责：划词高亮、随笔批注管理、Markdown 笔记导出及金句卡片生成门面调度模块。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

from core.adapters.egress.ebook.epub_reader_annotator_css import get_epub_annotator_css
from core.adapters.egress.ebook.epub_reader_annotator_js import get_epub_annotator_js as _get_core_js
from core.adapters.egress.ebook.epub_reader_poster_js import get_epub_poster_js


def get_epub_annotator_js() -> str:
    """获取整合了纯客户端高清金句卡片海报生成器与划词批注管理器的完整 JavaScript"""
    return f"{get_epub_poster_js()}\n{_get_core_js()}"


__all__ = ["get_epub_annotator_css", "get_epub_annotator_js"]
