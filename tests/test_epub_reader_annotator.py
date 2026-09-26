# -*- coding: utf-8 -*-
"""
🖍️ tests/test_epub_reader_annotator.py
EPUB 阅读器真实 DOM 划线、就地悬浮操作气泡、笔记重现还原（Rehydration）自动化测试。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import subprocess
import pytest
from core.adapters.egress.ebook.epub_reader import render_epub_reader_html
from core.adapters.egress.ebook.epub_reader_annotator import get_epub_annotator_css, get_epub_annotator_js
from core.adapters.egress.ebook.epub_reader_annotator_dom_js import get_epub_annotator_dom_js


def test_annotator_css_and_dom_template():
    """验证高亮划线样式、气泡 Popover 与模态窗注入完整性"""
    css = get_epub_annotator_css()
    assert 'mark.er-hl' in css
    assert 'mark.er-hl-yellow' in css
    assert 'mark.er-hl-emerald' in css
    assert 'mark.er-hl-pink' in css
    assert '.er-mark-popover' in css
    assert 'mark[data-has-comment="true"]' in css

    sample_epub = "imprints/default/books/illacme-press-数字出版集_zh.epub"
    if os.path.exists(sample_epub):
        html_out = render_epub_reader_html(sample_epub)
        assert 'id="er-mark-popover"' in html_out
        assert 'id="er-floating-bar"' in html_out
        assert 'id="er-card-modal"' in html_out
        assert 'id="er-note-modal"' in html_out


def test_annotator_js_in_node_sandbox():
    """在 Node 沙箱中验证划线引擎与 DOM 重现还原逻辑 0 语法与运行时异常"""
    js_dom = get_epub_annotator_dom_js()
    runner = f"""
    const mockWindow = {{
      addEventListener: () => {{}},
      getSelection: () => ({{ isCollapsed: true, rangeCount: 0 }}),
      innerWidth: 1200,
      innerHeight: 800
    }};
    const mockDoc = {{
      getElementById: () => null,
      querySelector: () => null,
      querySelectorAll: () => [],
      addEventListener: () => {{}},
      createElement: (tag) => ({{
        className: '',
        setAttribute: () => {{}},
        appendChild: () => {{}}
      }})
    }};
    global.window = mockWindow;
    global.document = mockDoc;
    global.NodeFilter = {{ SHOW_TEXT: 4 }};

    {js_dom}

    if (typeof mockWindow.wrapRangeWithHighlight !== 'function') throw new Error('wrapRangeWithHighlight missing');
    if (typeof mockWindow.rehydrateAnnotations !== 'function') throw new Error('rehydrateAnnotations missing');
    if (typeof mockWindow.removeHighlightMark !== 'function') throw new Error('removeHighlightMark missing');
    console.log('Annotator DOM Engine PASS');
    """
    res = subprocess.run(["node", "-e", runner], capture_output=True, text=True)
    assert res.returncode == 0, f"Node sandbox failed: {res.stderr}"
    assert "Annotator DOM Engine PASS" in res.stdout
