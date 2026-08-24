# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Templates & UI Engine (Facade)
模块职责：提供 Universal 主题与兜底渲染器的标准 HTML5 骨架、导航栏、Docs 侧边栏、多语言切换、Showcase 栅格与 Blog 交互引擎。
本文件作为顶层门面（Facade），按 SOP-02 精益物理拆分架构统一对外导出子分片原子能力。
"""

from .generic_shards import (
    resolve_wikilinks,
    resolve_callouts,
    resolve_mermaids,
    build_docs_sidebar,
    get_doc_slug_map,
    build_language_switcher,
    get_universal_css,
    get_universal_client_js,
    render_html_page,
    generate_dynamic_blog_archive,
)

__all__ = [
    "resolve_wikilinks",
    "resolve_callouts",
    "resolve_mermaids",
    "build_docs_sidebar",
    "get_doc_slug_map",
    "build_language_switcher",
    "get_universal_css",
    "get_universal_client_js",
    "render_html_page",
    "generate_dynamic_blog_archive",
]
