# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Test Suite for Bindery HTML Sanitizer & Container Unwrapper
测试目标：
1. HtmlSanitizer.sanitize_to_markdown 能够对容器标签 (div, span, section) 彻底脱壳
2. HTML 标题 (h1-h6) 正确转换为 Markdown 标题
3. HTML 链接与粗斜体正确转译为 Markdown 语法
4. HtmlSanitizer.sanitize_to_plain_text 彻底剔除标签，输出纯自然语言
5. 混排 HTML 原稿经 DocxBookAdapter 导出后不含任何 HTML 标签噪音
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import pytest
from core.bindery.html_sanitizer import HtmlSanitizer
from core.adapters.egress.ebook.docx import DocxBookAdapter


def test_html_sanitizer_container_unwrapping():
    """验证复杂嵌套的前端容器标签被彻底脱壳并保留内容"""
    raw_html = '''
    <div class="home-hero-container" style="text-align: center; margin: 0 auto;">
        <div class="hero-badge" style="color: var(--accent);">
            <span>🚀</span> V50.3 主权中枢已就绪
        </div>
        <h1 class="hero-title" style="font-size: 3rem;">全球出版发行中心</h1>
        <p class="hero-desc" style="color: #666;">让灵感在起草室点燃，在文库中沉淀。</p>
        <a href="https://example.com/guide" class="btn">⚡ 快速上手</a>
    </div>
    '''
    cleaned = HtmlSanitizer.sanitize_to_markdown(raw_html)

    # 1. 断言没有任何 HTML 容器或样式残留
    assert "<div" not in cleaned
    assert "</div>" not in cleaned
    assert "<span" not in cleaned
    assert "style=" not in cleaned
    assert "class=" not in cleaned

    # 2. 断言关键业务文本完整保留
    assert "V50.3 主权中枢已就绪" in cleaned
    assert "# 全球出版发行中心" in cleaned
    assert "让灵感在起草室点燃，在文库中沉淀。" in cleaned
    assert "[⚡ 快速上手](https://example.com/guide)" in cleaned


def test_html_sanitizer_to_plain_text():
    """验证纯文本模式下 100% 剥离 HTML 与 Markdown 语法标签"""
    raw_mixed = '''
    <div class="box">
        <h2>第二章 核心原则</h2>
        <p>正文内容包含 <strong>粗体强调</strong> 与 <a href="/docs">超链接</a>。</p>
    </div>
    '''
    plain = HtmlSanitizer.sanitize_to_plain_text(raw_mixed)

    assert "<" not in plain
    assert ">" not in plain
    assert "##" not in plain
    assert "**" not in plain
    assert "[" not in plain and "]" not in plain
    assert "第二章 核心原则" in plain
    assert "粗体强调" in plain
    assert "超链接" in plain


def test_docx_export_without_html_noise(tmp_path):
    """验证 DocxBookAdapter 导出包含 HTML 混排的章节时，Word 实体中 0 HTML 标签"""
    out_docx = str(tmp_path / "sanitized_test.docx")
    chapters = [
        {
            "id": "ch_1",
            "title": "测试章节",
            "slug": "test-ch",
            "raw_body": '<div class="alert-box" style="padding:10px;">\n<h1>主权出版</h1>\n<p>这是被 div 包裹的正文。</p>\n</div>',
            "headings": [],
            "assets": []
        }
    ]
    meta = {
        "title": "测试审校本",
        "author": "测试组",
        "publisher": "测试出版社"
    }

    adapter = DocxBookAdapter()
    success = adapter.bind_book(
        manuscript_tree=chapters,
        book_metadata=meta,
        output_file_path=out_docx
    )
    assert success is True
    assert os.path.exists(out_docx)

    import docx
    d = docx.Document(out_docx)
    all_texts = [p.text for p in d.paragraphs if p.text.strip()]
    
    # 断言没有任何 HTML 标签进入段落
    for t in all_texts:
        assert "<div" not in t
        assert "style=" not in t
        assert "class=" not in t
        assert "</" not in t

    # 断言内容被转换为 Word 标题和段落
    assert any("主权出版" in t for t in all_texts)
    assert any("这是被 div 包裹的正文。" in t for t in all_texts)
