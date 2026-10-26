# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Shards Package
"""

from .syntax_resolver import resolve_wikilinks, resolve_callouts, resolve_mermaids, resolve_videos
from .navigation_builder import build_docs_sidebar, get_doc_slug_map, build_language_switcher
from .assets_bundle import get_universal_css, get_universal_client_js
from .page_renderer import render_html_page
from .blog_archiver import generate_dynamic_blog_archive

__all__ = [
    "resolve_wikilinks",
    "resolve_callouts",
    "resolve_mermaids",
    "resolve_videos",
    "build_docs_sidebar",
    "get_doc_slug_map",
    "build_language_switcher",
    "get_universal_css",
    "get_universal_client_js",
    "render_html_page",
    "generate_dynamic_blog_archive",
]
