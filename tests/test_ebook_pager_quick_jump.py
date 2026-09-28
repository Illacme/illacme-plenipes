# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Reader Pager & Quick Jump Tests
测试职责：验证 EPUB 阅读器底部翻页控制器、首页/尾页快捷按钮、指定页码跳转与键盘快捷键。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import pytest
from core.adapters.egress.ebook.epub_reader_template import build_epub_reader_shell
from core.adapters.egress.ebook.epub_reader_pager_css import get_epub_pager_css
from core.adapters.egress.ebook.epub_reader_pager_js import get_epub_pager_js
from core.adapters.egress.ebook.epub_reader_js import get_epub_reader_js


def test_epub_pager_css_integrity():
    """验证底部快速跳转与页码导航 CSS 规则完备性"""
    css = get_epub_pager_css()
    assert ".er-footer-nav" in css
    assert ".er-footer-btn" in css
    assert ".er-footer-page-box" in css
    assert ".er-page-jump-input" in css
    assert "user-select: none" in css


def test_epub_pager_js_integrity():
    """验证底部快速跳转与页码导航 JS 逻辑完备性"""
    js = get_epub_pager_js()
    assert "initPagerControls" in js
    assert "er-nav-first" in js
    assert "er-nav-last" in js
    assert "er-footer-page-box" in js
    assert "er-page-jump-input" in js
    assert "activateJumpInput" in js
    assert "commitJump" in js
    assert "cancelJump" in js
    assert "goToFirstPage" in js
    assert "goToLastPage" in js
    assert "goToPage" in js
    # 快捷键 G
    assert "e.key === 'g' || e.key === 'G'" in js


def test_epub_reader_core_js_pager_support():
    """验证 core reader js 支持 goToPage / goToFirstPage / goToLastPage"""
    core_js = get_epub_reader_js()
    assert "window.goToPage = goToPage" in core_js
    assert "window.goToFirstPage = () =>" in core_js
    assert "window.goToLastPage = () =>" in core_js
    assert "window.selectChapterByIndex = (idx) =>" in core_js
    assert "window.getReaderTotalPages = () =>" in core_js
    # 快捷键 Home / End
    assert "e.key === 'Home'" in core_js
    assert "e.key === 'End'" in core_js


def test_epub_reader_shell_contains_pager_dom():
    """验证生成的完整阅读器 HTML 骨架包含翻页与跳转 DOM 元素"""
    html_output = build_epub_reader_shell(
        book_title="测试全景典籍",
        toc_html="<div class='toc'></div>",
        content_html="<div class='chapter'><h1>第一卷</h1><p>正文内容</p></div>"
    )

    # 验证样式与脚本注入
    assert ".er-footer-nav" in html_output
    assert "initPagerControls" in html_output
    assert "window.goToPage" in html_output

    # 验证 DOM 拓扑
    assert 'class="er-footer-nav"' in html_output
    assert 'id="er-nav-first"' in html_output
    assert 'id="er-nav-last"' in html_output
    assert 'id="er-nav-prev-footer"' in html_output
    assert 'id="er-nav-next-footer"' in html_output
    assert 'id="er-footer-page-box"' in html_output
    assert 'id="er-footer-page"' in html_output
    assert 'id="er-page-jump-input"' in html_output
