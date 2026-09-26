# -*- coding: utf-8 -*-
"""
📱 tests/test_epub_reader_prefs.py
EPUB 阅读器沉浸全屏手势、Aa 排版定制抽屉与五色护眼主题自动化回归套件。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import subprocess
import pytest
from core.adapters.egress.ebook.epub_reader import render_epub_reader_html
from core.adapters.egress.ebook.epub_reader_prefs_css import get_epub_prefs_css
from core.adapters.egress.ebook.epub_reader_prefs_js import get_epub_prefs_js


def test_prefs_css_and_template_injection():
    """验证排版与沉浸 CSS 样式及 HTML 抽屉注入完备性"""
    css = get_epub_prefs_css()
    assert '[data-theme="mint"]' in css
    assert '[data-theme="oled"]' in css
    assert 'body.er-immersive' in css
    assert '.er-prefs-drawer' in css
    assert '.er-resume-toast' in css

    # 验证真实样例渲染包含新组件
    sample_epub = "imprints/default/books/illacme-press-数字出版集_zh.epub"
    if os.path.exists(sample_epub):
        html_out = render_epub_reader_html(sample_epub)
        assert 'id="er-btn-prefs"' in html_out
        assert 'id="er-prefs-drawer"' in html_out
        assert 'data-th="mint"' in html_out
        assert 'data-th="oled"' in html_out
        assert 'er-immersive-indicator' in html_out


def test_prefs_js_in_node_sandbox():
    """在 Node 沙箱中运行 epub_reader_prefs_js.py 确保 0 语法与运行时错误"""
    js_code = get_epub_prefs_js()
    runner = f"""
    const mockStorage = {{}};
    const mockDoc = {{
        body: {{
            classList: {{
                _set: new Set(),
                add: function(c) {{ this._set.add(c); }},
                remove: function(c) {{ this._set.delete(c); }},
                toggle: function(c, force) {{
                    if (typeof force === 'boolean') {{
                        if (force) this._set.add(c); else this._set.delete(c);
                        return force;
                    }}
                    if (this._set.has(c)) {{ this._set.delete(c); return false; }}
                    this._set.add(c); return true;
                }},
                contains: function(c) {{ return this._set.has(c); }}
            }},
            appendChild: () => {{}}
        }},
        documentElement: {{
            setAttribute: () => {{}},
            getAttribute: () => 'dark',
            style: {{ setProperty: () => {{}} }}
        }},
        getElementById: (id) => ({{
            id: id,
            classList: {{
                add: () => {{}},
                remove: () => {{}},
                toggle: () => true,
                contains: () => false
            }},
            addEventListener: () => {{}},
            style: {{}}
        }}),
        querySelectorAll: () => [],
        querySelector: () => null,
        createElement: () => ({{
            style: {{}},
            classList: {{ add: () => {{}}, remove: () => {{}} }},
            textContent: '',
            remove: () => {{}}
        }}),
        addEventListener: () => {{}},
        title: '测试典籍'
    }};

    global.document = mockDoc;
    global.window = {{
        addEventListener: () => {{}},
        scrollTo: () => {{}},
        scrollY: 0,
        innerWidth: 800,
        innerHeight: 600
    }};
    global.localStorage = {{
        getItem: (k) => mockStorage[k] || null,
        setItem: (k, v) => {{ mockStorage[k] = String(v); }}
    }};
    global.MutationObserver = function(cb) {{ this.observe = () => {{}}; }};

    {js_code}

    if (typeof window.toggleImmersive !== 'function') throw new Error('缺少 toggleImmersive 全局方法');
    window.toggleImmersive(true);
    if (!mockDoc.body.classList.contains('er-immersive')) throw new Error('未能正确激活 er-immersive 类名');

    window.toggleImmersive(false);
    if (mockDoc.body.classList.contains('er-immersive')) throw new Error('未能正确解除 er-immersive 类名');

    console.log('PASS');
    """

    res = subprocess.run(["node", "-e", runner], capture_output=True, text=True)
    assert res.returncode == 0, f"Node 执行错误: {res.stderr}"
    assert "PASS" in res.stdout
