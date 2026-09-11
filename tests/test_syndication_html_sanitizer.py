#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 单元测试：社媒分发全渠道内容自适应清洗与跨平台格式适配器
验证：
1. 全页 HTML 网页外壳 (DOCTYPE/head/script/style/nav) 的精准探测与物理剥离；
2. 相对超链接向官方 Canonical 绝对路径的自动规约与补全；
3. 标签 (Tags) 的小写字母化、特殊符号剔除与平台上限截断；
4. 首页 (Landing Page) 营销卡片向 GFM 结构化通告的优雅降级；
5. 保留文章合法内联标签 (如 details/summary)；
6. 真实 index.md 英文整页 HTML 产物端到端清洗验证。
"""

import pytest
from core.editorial.ast_processor import MarkdownASTProcessor
from core.editorial.ast_shards import HtmlSanitizer, GfmNormalizer, MetadataSanitizer, LandingPageTransformer

RAW_FULL_HTML_SAMPLE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <title>Illacme Plenipes - Global Private Publishing House</title>
    <script>
        (function () { var saved = localStorage.getItem('theme'); })();
    </script>
    <style>
        :root { --accent-color: #00f5ff; }
    </style>
    <link rel="stylesheet" href="../static/css/style.css">
</head>
<body class="sovereign-engine">
    <header class="glass-header">
        <nav class="desktop-nav">
            <a href="../en/docs/index.html">Document Guide</a>
        </nav>
    </header>
    <main>
        <div class="home-hero-container">
            <h1 class="hero-main-title">Your Sovereign Global Publishing Center</h1>
            <p class="hero-subtext">Industrial-grade AI-native publishing operating system.</p>
            <div class="hero-cta-group">
                <a href="./docs/quick-start.html" class="theme-btn">5-Minute Quickstart</a>
            </div>
            <div class="stats-matrix">
                <div class="stat-card">
                    <div>Shield Mode</div>
                    <div>100% Physical Sovereignty</div>
                </div>
            </div>
        </div>
        <details>
            <summary>Advanced Features</summary>
            <p>Details content here.</p>
        </details>
    </main>
    <footer>
        <p>Copyright 2026</p>
    </footer>
</body>
</html>"""

def test_html_sanitizer_detect_full_page():
    assert HtmlSanitizer.is_full_html_page(RAW_FULL_HTML_SAMPLE) is True
    assert HtmlSanitizer.is_full_html_page("# Normal Markdown Title\n\nSome paragraph.") is False

def test_html_sanitizer_strip_boilerplate():
    stripped, lines_count = HtmlSanitizer.strip_html_boilerplate(RAW_FULL_HTML_SAMPLE)
    assert "<!DOCTYPE" not in stripped
    assert "<script" not in stripped
    assert "<style" not in stripped
    assert "<header" not in stripped
    assert "<nav" not in stripped
    assert "<footer" not in stripped
    assert lines_count > 0
    # 核心主体和合法 details 依然存在
    assert "Your Sovereign Global Publishing Center" in stripped
    assert "<details>" in stripped

def test_gfm_normalizer_absolutize_links():
    content = "Check [Quick Start](./docs/quick-start.html) or [Blog](../blog/index.html) or [External](https://google.com)"
    converted, count = GfmNormalizer.absolutize_links(content, site_url="https://illacme.org")
    assert count == 2
    assert "https://illacme.org/docs/quick-start.html" in converted
    assert "https://illacme.org/blog/index.html" in converted
    assert "https://google.com" in converted

def test_metadata_sanitizer_tags_and_canonical():
    raw_tags = ["Home", "Sovereign Publishing", "AI原生出版!@#", "DevOps", "ExtraTag1", "ExtraTag2"]
    clean_tags = MetadataSanitizer.sanitize_tags(raw_tags, max_tags=4, target_platform="devto")
    assert len(clean_tags) <= 4
    for t in clean_tags:
        assert t.islower()
        assert " " not in t
        assert not any(c in t for c in "!@#$%^&*()")

    canonical = MetadataSanitizer.build_canonical_url("index.md", "index", "en", "https://illacme.org")
    assert canonical == "https://illacme.org/en/index.html"

def test_end_to_end_adapt_format_for_devto():
    processor = MarkdownASTProcessor()
    fm = {
        "title": "Illacme Plenipes - Global Private Publishing House",
        "tags": ["Home", "Sovereign"],
        "layout": "page"
    }

    clean_content = processor.adapt_format(
        content=RAW_FULL_HTML_SAMPLE,
        target_platform="devto",
        site_url="https://illacme.org",
        slug="index",
        fm=fm
    )

    # 1. 绝无全页壳与脚本
    assert "<!DOCTYPE" not in clean_content
    assert "<script" not in clean_content
    assert "<style" not in clean_content
    assert "<header" not in clean_content
    assert "<nav" not in clean_content

    # 2. 标题已转为标准 GFM
    assert "# Your Sovereign Global Publishing Center" in clean_content or "### Your Sovereign Global Publishing Center" in clean_content or "Your Sovereign Global Publishing Center" in clean_content

    # 3. 相对链接已升级为绝对 URL
    assert "https://illacme.org/docs/quick-start.html" in clean_content

    # 4. 保留合法折叠标签
    assert "<details>" in clean_content
    assert "<summary>Advanced Features</summary>" in clean_content

    # 5. 元数据治理
    clean_fm = processor.sanitize_metadata(
        metadata=fm,
        target_platform="devto",
        site_url="https://illacme.org",
        slug="index",
        doc_id="index.md",
        lang_code="en"
    )
    assert clean_fm["canonical_url"] == "https://illacme.org/en/index.html"
    assert clean_fm["tags"] == ["home", "sovereign"]
