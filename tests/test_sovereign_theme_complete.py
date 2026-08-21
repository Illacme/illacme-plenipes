#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Sovereign Theme Complete Capabilities & Multi-Language Test Suite
验证主权原生默认主题全页面类型、全息多语言切换、面包屑、代码块复制与离线搜索索引能力。
"""

import unittest
from types import SimpleNamespace
from themes.sovereign.adapters.sovereign import SovereignSSGAdapter
from themes.sovereign.adapters.sovereign_i18n import get_ui_i18n, get_language_display_names
from themes.sovereign.adapters.sovereign_ui import (
    calculate_reading_meta,
    build_breadcrumbs,
    build_doc_pagination
)


class TestSovereignThemeComplete(unittest.TestCase):

    def setUp(self):
        self.theme_settings = SimpleNamespace(
            name="sovereign",
            site_name="Illacme Sovereign Press",
            accent_color="#00f5ff",
            enable_glassmorphism=True,
            footer_copyright="© 2026 Sovereign. All Rights Reserved.",
            github_repo="https://github.com/Illacme/illacme-plenipes",
            nav_links=[
                {"text": "📚 Blog", "url": "/blog/", "external": False},
                {"text": "📚 Docs", "url": "/docs/", "external": False}
            ]
        )
        self.adapter = SovereignSSGAdapter(self.theme_settings)

    def test_i18n_dictionary_completeness(self):
        """测试全息多语言字典支持度"""
        supported_langs = ["zh", "zh-Hans", "zh-Hant", "en", "ja", "ko", "fr", "de", "es", "ru"]
        for lang in supported_langs:
            t = get_ui_i18n(lang)
            self.assertIn("nav_home", t)
            self.assertIn("nav_docs", t)
            self.assertIn("nav_blog", t)
            self.assertIn("search_placeholder", t)
            self.assertIn("reading_time", t)
            self.assertIn("copy_code", t)

        display_names = get_language_display_names()
        self.assertIn("zh", display_names)
        self.assertIn("en", display_names)
        self.assertIn("ja", display_names)

    def test_reading_meta_and_breadcrumbs(self):
        """测试阅读时间计算与面包屑生成"""
        content = "<p>这是一段用于测试阅读时间和字数统计的中文内容，同时包含 English keywords 和技术术语。</p>"
        meta = calculate_reading_meta(content)
        self.assertGreaterEqual(meta["words"], 20)
        self.assertGreaterEqual(meta["minutes"], 1)

        bc = build_breadcrumbs("zh", "docs", "guide/intro.html", "入门指南", "./")
        self.assertIn("breadcrumb-container", bc)
        self.assertIn("入门指南", bc)
        self.assertIn("guide", bc)

    def test_render_docs_page(self):
        """测试文档页面完整渲染（含侧边栏、TOC、面包屑与元数据）"""
        markdown_body = """---
title: 主权出版入门指南
layout: docs
route_prefix: docs
author: Sovereign Author
date: 2026-08-16
tags: [architecture, ssg, i18n]
---

# 欢迎使用主权出版引擎

> [!TIP] 核心提示
> 这是主权原生渲染引擎的 Obsidian 呼号演示。

```python
def publish():
    print("Sovereign Published!")
```
"""
        fm = {
            "title": "主权出版入门指南",
            "slug": "intro",
            "route_prefix": "docs",
            "layout": "docs",
            "author": "Sovereign Author",
            "date": "2026-08-16",
            "tags": ["architecture", "ssg", "i18n"]
        }

        html, out_fm = self.adapter.render(markdown_body, fm, target_lang="zh", sub_path="docs/intro.html")
        self.assertIn("layout-docs", html)
        self.assertIn("主权出版入门指南", html)
        self.assertIn("callout-tip", html)
        self.assertIn("prose-container", html)
        self.assertIn("tag-pill", html)
        self.assertNotIn("{{ language_switcher }}", html)
        self.assertIn('<select class="control-select"', html)

    def test_render_blog_page(self):
        """测试博客文章页面渲染"""
        markdown_body = "# 我的第一篇主权博客\n\n欢迎来到去中心化出版时代。"
        fm = {
            "title": "我的第一篇主权博客",
            "slug": "first-post",
            "route_prefix": "blog",
            "layout": "blog",
            "author": "Eason",
            "date": "2026-08-16",
            "tags": ["release", "blog"]
        }
        html, out_fm = self.adapter.render(markdown_body, fm, target_lang="en", sub_path="en/blog/first-post.html")
        self.assertIn("layout-blog", html)
        self.assertIn("Eason", html)
        self.assertIn("2026-08-16", html)

    def test_render_showcase_and_home_page(self):
        """测试 Showcase 案例页与首页形态渲染"""
        fm_home = {
            "title": "首页",
            "slug": "index",
            "route_prefix": "page",
            "layout": "page"
        }
        html_home, _ = self.adapter.render("# 首页展示内容", fm_home, target_lang="zh", sub_path="index.html")
        self.assertIn("layout-page", html_home)

        fm_showcase = {
            "title": "主权案例墙",
            "slug": "showcase-index",
            "route_prefix": "showcase",
            "layout": "showcase"
        }
        html_showcase, _ = self.adapter.render("# 案例展示", fm_showcase, target_lang="zh", sub_path="showcase/index.html")
        self.assertIn("layout-showcase", html_showcase)

    def test_doc_pagination_rendering(self):
        """测试上下篇文档翻页器渲染"""
        prev_doc = {"title": "前置架构设计", "url": "/docs/arch.html"}
        next_doc = {"title": "后续分发部署", "url": "/docs/deploy.html"}
        pag_html = build_doc_pagination(prev_doc, next_doc, "zh")
        self.assertIn("前置架构设计", pag_html)
        self.assertIn("后续分发部署", pag_html)
        self.assertIn("doc-pagination-wrapper", pag_html)


if __name__ == '__main__':
    unittest.main()
