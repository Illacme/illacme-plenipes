# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Polyglot Matrix WebBook Test Suite
模块职责：验证多语平行对照矩阵 (Multilingual Polyglot Matrix) 的块级对齐、WebBook 导出与离线交互完整性。
"""

import os
import tempfile
import pytest

from core.bindery.polyglot_aligner import PolyglotAligner
from core.bindery.book_assembler import BookAssembler
from core.adapters.egress.ebook.webbook import WebBookAdapter


def test_polyglot_aligner_block_split():
    """验证 HTML 能够被准确切分为语义块"""
    html = "<h2>Title</h2><p>Paragraph 1</p><blockquote>Quote</blockquote><pre><code>code</code></pre>"
    blocks = PolyglotAligner.split_into_blocks(html)
    assert len(blocks) == 4
    assert blocks[0] == "<h2>Title</h2>"
    assert blocks[1] == "<p>Paragraph 1</p>"
    assert blocks[2] == "<blockquote>Quote</blockquote>"


def test_polyglot_aligner_synthesis():
    """验证多语种块级合成与标签注入"""
    ch_by_lang = {
        "zh": {"title": "计算架构", "html_body": "<p>第一段中文原稿。</p><p>第二段中文内容。</p>"},
        "en": {"title": "Compute Architecture", "html_body": "<p>First English paragraph.</p><p>Second English paragraph.</p>"},
        "ja": {"title": "計算アーキテクチャ", "html_body": "<p>最初の日本語段落。</p><p>二番目の日本語段落。</p>"}
    }
    aligned = PolyglotAligner.align_chapter_polyglot(ch_by_lang, primary_lang="zh", ordered_langs=["zh", "en", "ja"])
    assert aligned["block_count"] == 1
    body = aligned["html_body"]

    assert 'class="wb-polyglot-block wb-polyglot-columns"' in body
    assert 'class="wb-poly-item wb-poly-column" data-lang="zh"' in body
    assert 'class="wb-poly-item wb-poly-column" data-lang="en"' in body
    assert 'class="wb-poly-item wb-poly-column" data-lang="ja"' in body
    assert '<span class="wb-lang-badge">ZH</span>' in body
    assert '<span class="wb-lang-badge">EN</span>' in body
    assert '<span class="wb-lang-badge">JA</span>' in body
    assert "第一段中文原稿" in body
    assert "First English paragraph" in body
    assert "最初の日本語段落" in body


def test_polyglot_webbook_export_and_dom_integrity():
    """验证多语平行对照 WebBook 真实落盘与 DOM 完整性"""
    with tempfile.TemporaryDirectory() as tmpdir:
        assembler = BookAssembler(vault_dir="vault")
        out_html = assembler.assemble_and_bind(
            category="",
            format_type="webbook",
            target_lang="zh",
            output_dir=tmpdir,
            polyglot_langs=["zh", "en", "ja"]
        )
        assert out_html is not None
        assert os.path.exists(out_html)

        with open(out_html, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. 顶栏主语言选择与多栏对照控制条
        assert '<div class="wb-polyglot-bar">' in content
        assert 'class="wb-primary-group"' in content
        assert 'id="wb-compare-chips"' in content
        assert 'data-lang="zh"' in content
        assert 'data-lang="en"' in content
        assert 'data-lang="ja"' in content

        # 2. 块级多语容器与徽标
        assert 'class="wb-polyglot-block wb-polyglot-columns"' in content
        assert 'wb-poly-item' in content
        assert 'class="wb-lang-badge"' in content

        # 3. 版记数字物权标识
        assert "urn:uuid:" in content
        assert "N/A" not in content[content.find("urn:uuid:"):content.find("urn:uuid:") + 100]


def test_webbook_reading_preferences_and_keyboard_shortcuts():
    """验证 WebBook 沉浸翻阅全套偏好记忆与键盘快捷翻章运行时"""
    from core.adapters.egress.ebook.webbook_assets import WebBookAssets
    js = WebBookAssets.get_embedded_js()
    css = WebBookAssets.get_embedded_css()

    # 1. 主题与字号偏好
    assert "wb_theme" in js
    assert "wb_fs" in js
    assert "wb-theme-btn" in js

    # 2. 侧边栏折叠与阅读进度滚动恢复
    assert "wb_sb_collapsed" in js
    assert "wb_scroll_pos" in js

    # 3. 主语言与多栏对照矩阵记忆
    assert "wb_primary_lang" in js
    assert "wb_compare_langs" in js

    # 4. 键盘左右方向键与 J/K 平滑翻章
    assert "ArrowLeft" in js
    assert "ArrowRight" in js
    assert "window.scrollTo" in js

    # 5. CSS 主题变量完备性
    assert '[data-theme="light"]' in css
    assert '[data-theme="sepia"]' in css

    # 6. 出版级 @media print 印刷排版与打印控制
    assert "@media print" in css
    assert "break-before: page" in css
    assert "orphans: 3" in css
    assert "widows: 3" in css
    assert "wb-print-btn" in js
    assert "window.print" in js


