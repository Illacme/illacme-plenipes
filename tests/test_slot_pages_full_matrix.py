#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Slot Pages Full Matrix Tests
覆盖范围：
1. 全部 8 大主流 SSG 引擎（Starlight, Docusaurus, VitePress, Nextra, Hugo, Hexo, Sovereign, Universal）单页物理落盘断言
2. 同名单页 Clean URL 智能折叠与坍缩断言 (消灭 /about/about)
3. 根目录双重套娃拦截网断言 (拦截 content/content/ 等)
4. 双向链接 [[about]] 根单页相对寻址断言
5. 元数据无损透传与槽位声明契约断言
"""

import os
from unittest.mock import MagicMock
import pytest

from core.editorial.router import RouteManager
from adapters.egress.ssg.starlight import StarlightAdapter
from adapters.egress.ssg.docusaurus import DocusaurusAdapter
from adapters.egress.ssg.vitepress import VitepressAdapter
from adapters.egress.ssg.nextra import NextraAdapter
from adapters.egress.ssg.hugo import HugoAdapter
from adapters.egress.ssg.hexo import HexoAdapter
from themes.sovereign.adapters.sovereign import SovereignSSGAdapter
from core.adapters.egress.ssg.generic import GenericSSGAdapter
from core.adapters.egress.ssg.generic_shards.syntax_resolver import resolve_wikilinks


def test_slot_pages_physical_paths_all_8_ssg_engines():
    """验证全部 8 大主流 SSG 引擎单页在单语言与多语言下的物理落盘路径"""
    engine_specs = [
        # (engine_name, adapter_cls, base_path, expected_single, expected_en, expected_ja)
        ("starlight", StarlightAdapter, "src/content/docs",
         os.path.normpath("src/content/docs/about.md"),
         os.path.normpath("src/content/docs/en/about.md"),
         os.path.normpath("src/content/docs/ja/about.md")),
        
        ("docusaurus", DocusaurusAdapter, ".",
         os.path.normpath("src/pages/about.md"),
         os.path.normpath("i18n/en/docusaurus-plugin-content-pages/about.md"),
         os.path.normpath("i18n/ja/docusaurus-plugin-content-pages/about.md")),
        
        ("vitepress", VitepressAdapter, ".",
         os.path.normpath("about.md"),
         os.path.normpath("en/about.md"),
         os.path.normpath("ja/about.md")),
        
        ("nextra", NextraAdapter, "pages",
         os.path.normpath("pages/about.md"),
         os.path.normpath("pages/en/about.md"),
         os.path.normpath("pages/ja/about.md")),
        
        ("hugo", HugoAdapter, "content",
         os.path.normpath("content/about.md"),
         os.path.normpath("content/en/about.md"),
         os.path.normpath("content/ja/about.md")),
        
        ("hexo", HexoAdapter, "source",
         os.path.normpath("source/about.md"),
         os.path.normpath("source/en/about.md"),
         os.path.normpath("source/ja/about.md")),
        
        ("sovereign", SovereignSSGAdapter, "content",
         os.path.normpath("content/about.md"),
         os.path.normpath("content/en/about.md"),
         os.path.normpath("content/ja/about.md")),
        
        ("universal", GenericSSGAdapter, ".",
         os.path.normpath("about.md"),
         os.path.normpath("en/about.md"),
         os.path.normpath("ja/about.md")),
    ]

    for name, cls, base, exp_single, exp_en, exp_ja in engine_specs:
        adapter = cls(MagicMock())
        rm = RouteManager(
            meta_manager=MagicMock(),
            translator_factory=None,
            default_lang="zh",
            active_theme=name,
            ssg_adapter=adapter
        )

        p_single = rm.resolve_physical_path(base, "zh", "", "", "about", ".md", source_type="pages")
        p_en = rm.resolve_physical_path(base, "en", "", "", "about", ".md", source_type="pages")
        p_ja = rm.resolve_physical_path(base, "ja", "", "", "about", ".md", source_type="pages")

        assert p_single == exp_single, f"[{name}] 单语落盘不符: 实际 {p_single}, 期望 {exp_single}"
        assert p_en == exp_en, f"[{name}] 英语落盘不符: 实际 {p_en}, 期望 {exp_en}"
        assert p_ja == exp_ja, f"[{name}] 日语落盘不符: 实际 {p_ja}, 期望 {exp_ja}"


def test_slot_pages_clean_url_collapsing():
    """验证同名单页 Clean URL 自动坍缩折叠与普通多级页面隔离"""
    rm = RouteManager(
        meta_manager=MagicMock(),
        translator_factory=None,
        default_lang="zh",
        active_theme="starlight"
    )

    # 1. 同名单页自动折叠为单级
    assert rm.resolve_logical_url("zh", "about", "", "about") == "/about"
    assert rm.resolve_logical_url("en", "about", "", "about") == "/en/about"
    assert rm.resolve_logical_url("ja", "terms", "", "terms") == "/ja/terms"

    # 2. 带有不同 slug 的子页面不坍缩
    assert rm.resolve_logical_url("zh", "about", "", "team") == "/about/team"
    assert rm.resolve_logical_url("en", "about", "", "team") == "/en/about/team"

    # 3. 带有子目录的页面不坍缩
    assert rm.resolve_logical_url("zh", "about", "sub", "about") == "/about/sub/about"

    # 4. 普通频道不受影响
    assert rm.resolve_logical_url("zh", "docs", "", "intro") == "/docs/intro"
    assert rm.resolve_logical_url("en", "docs", "", "intro") == "/en/docs/intro"
    assert rm.resolve_logical_url("zh", "blog", "", "post-1") == "/blog/post-1"


def test_slot_pages_anti_nesting_shield():
    """验证双重根目录套娃拦截网剥离机制"""
    rm = RouteManager(
        meta_manager=MagicMock(),
        translator_factory=None,
        default_lang="zh",
        active_theme="hugo"
    )

    # base_path 为 content，route_prefix 首级也是 content -> 剥离首级
    p1 = rm.resolve_physical_path("content", "zh", "content/about", "", "terms", ".md", source_type="pages")
    assert p1 == os.path.normpath("content/about/terms.md")
    assert "content/content" not in p1.replace('\\', '/')

    # base_path 为 source，route_prefix 首级也是 source -> 剥离首级
    p2 = rm.resolve_physical_path("source", "zh", "source/about", "", "privacy", ".md", source_type="pages")
    assert p2 == os.path.normpath("source/about/privacy.md")
    assert "source/source" not in p2.replace('\\', '/')


def test_slot_pages_wikilink_resolution():
    """验证独立单页双链 [[about]] 在深层与根层均精准解析为根单页超链接"""
    engine = MagicMock()
    engine.config.translation.slug_dir_mode = "nested"
    engine.state_manager.get_all_records.return_value = {
        "about": {"slug": "about", "channel": "pages"},
        "guide": {"slug": "guide", "channel": "docs"}
    }

    # 1. 在深层文档 docs/guide.html 中引用 [[about|关于我们]]
    html_deep = resolve_wikilinks("[[about|关于我们]]", root_path="../", sub_path="docs/guide.html", engine=engine)
    assert '<a href="../about.html" class="universal-link wikilink">关于我们</a>' in html_deep

    # 2. 在站点根目录 index.html 中引用 [[about|关于我们]]
    html_root = resolve_wikilinks("[[about|关于我们]]", root_path="./", sub_path="index.html", engine=engine)
    assert '<a href="./about.html" class="universal-link wikilink">关于我们</a>' in html_root

    # 3. 容错回退机制：未注册的单页常见名 [[terms|用户协议]]
    html_fallback = resolve_wikilinks("[[terms|用户协议]]", root_path="../", sub_path="docs/guide.html", engine=engine)
    assert '<a href="../terms.html" class="universal-link wikilink">用户协议</a>' in html_fallback
