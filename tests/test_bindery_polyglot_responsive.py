# -*- coding: utf-8 -*-
"""
📱 [V125.3] 多语言对照移动端响应式与段落联动测试套件
测试重点：
1. 移动端/窄屏媒体查询对齐：顶栏多语胶囊在窄屏下不被隐藏，翻页模式保持分栏防截断；
2. 跨语种段落级索引与微光高亮联动在 Node.js 环境下的拓扑完备性；
3. 阅读器完整模版包含多语同步控制器脚本。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""
import subprocess
import pytest

from core.adapters.egress.ebook.epub_reader_polyglot_css import get_epub_polyglot_css
from core.adapters.egress.ebook.epub_reader_polyglot_sync_js import get_epub_reader_polyglot_sync_js
from core.adapters.egress.ebook.epub_reader_template import build_epub_reader_shell


def test_polyglot_responsive_css_integrity():
    """验证移动端窄屏 CSS 规则完备性"""
    css = get_epub_polyglot_css()
    # 1. 窄屏顶栏不被隐藏
    assert ".er-topbar-polyglot { display: flex !important;" in css
    # 2. 翻页模式下移动端保持 row 布局防截断
    assert '[data-read-mode="paginated"] body.wb-concordance .wb-polyglot-block' in css
    assert "display: flex !important; flex-direction: row !important;" in css
    # 3. 卷轴模式下支持紧凑纵向堆叠
    assert '[data-read-mode="scroll"] body.wb-concordance .wb-polyglot-block' in css
    assert "flex-direction: column !important;" in css
    # 4. 段落高亮微光样式
    assert ".wb-para-active" in css
    assert "var(--accent-glow" in css


def test_polyglot_template_embeds_sync_script():
    """验证阅读器模版正确注入了段落联动同步脚本"""
    shell = build_epub_reader_shell(
        book_title="多语测试典籍",
        toc_html="<nav>toc</nav>",
        content_html="<div class='er-chapter-card'>content</div>"
    )
    assert "initPolyglotParaSync" in shell
    assert "wb-para-target" in shell


def test_polyglot_sync_in_node_sandbox():
    """在 Node.js 沙箱中验证多语段落自动索引标注与点击联动高亮"""
    sync_js = get_epub_reader_polyglot_sync_js()
    runner = f"""
    global.window = global;
    global.window.innerWidth = 400;
    global.window.innerHeight = 800;

    let clickHandler = null;
    const mockElements = [];

    function createMockElement(tag, text) {{
      const el = {{
        tagName: tag.toUpperCase(),
        textContent: text,
        _attrs: {{}},
        classList: {{
          _classes: new Set(),
          add(c) {{ this._classes.add(c); }},
          remove(c) {{ this._classes.delete(c); }},
          contains(c) {{ return this._classes.has(c); }}
        }},
        hasAttribute(a) {{ return a in this._attrs; }},
        getAttribute(a) {{ return this._attrs[a] || null; }},
        setAttribute(a, v) {{ this._attrs[a] = String(v); }},
        closest(sel) {{
          if (sel === '.wb-para-target' && this.classList.contains('wb-para-target')) return this;
          if (sel === '.wb-polyglot-block') return mockBlock;
          return null;
        }},
        getBoundingClientRect() {{ return {{ top: 100, bottom: 200 }}; }},
        scrollIntoView() {{}}
      }};
      mockElements.push(el);
      return el;
    }}

    const pZh1 = createMockElement('p', '第一段中文');
    const pZh2 = createMockElement('p', '第二段中文');
    const colZh = {{
      children: [pZh1, pZh2]
    }};

    const pEn1 = createMockElement('p', 'First English para');
    const pEn2 = createMockElement('p', 'Second English para');
    const colEn = {{
      children: [pEn1, pEn2]
    }};

    const mockBlock = {{
      _indexed: false,
      querySelectorAll(sel) {{
        if (sel === '.wb-poly-content') return [colZh, colEn];
        if (sel.startsWith('.wb-para-target[data-para-idx=')) {{
          const match = sel.match(/data-para-idx="([^"]+)"/);
          if (match) {{
            const idx = match[1];
            return mockElements.filter(e => e.getAttribute('data-para-idx') === idx);
          }}
        }}
        return [];
      }}
    }};

    global.document = {{
      readyState: 'complete',
      body: {{
        classList: {{ contains: (c) => c === 'wb-concordance' }}
      }},
      documentElement: {{
        getAttribute: (a) => a === 'data-read-mode' ? 'scroll' : ''
      }},
      addEventListener(event, fn) {{
        if (event === 'click') clickHandler = fn;
      }},
      querySelectorAll(sel) {{
        if (sel === '.wb-polyglot-block') return [mockBlock];
        if (sel === '.wb-para-active') return mockElements.filter(e => e.classList.contains('wb-para-active'));
        return [];
      }}
    }};

    {sync_js}

    // 1. 验证初始化标注
    if (typeof window.initPolyglotParaSync !== 'function') throw new Error('initPolyglotParaSync 未挂载');
    window.initPolyglotParaSync();

    if (pZh1.getAttribute('data-para-idx') !== '0') throw new Error('pZh1 未正确标注索引 0');
    if (pEn1.getAttribute('data-para-idx') !== '0') throw new Error('pEn1 未正确标注索引 0');
    if (pZh2.getAttribute('data-para-idx') !== '1') throw new Error('pZh2 未正确标注索引 1');
    if (pEn2.getAttribute('data-para-idx') !== '1') throw new Error('pEn2 未正确标注索引 1');

    // 2. 模拟点击中文第一段
    if (!clickHandler) throw new Error('点击事件委托未挂载');
    clickHandler({{
      target: pZh1
    }});

    // 验证 pZh1 和 pEn1 同时进入高亮状态
    if (!pZh1.classList.contains('wb-para-active')) throw new Error('pZh1 未进入激活高亮状态');
    if (!pEn1.classList.contains('wb-para-active')) throw new Error('pEn1 跨语种对应段落未同步激活高亮');
    if (pZh2.classList.contains('wb-para-active')) throw new Error('无关段落 pZh2 不应被高亮');

    console.log('POLYGLOT_RESPONSIVE_SYNC_OK');
    """
    res = subprocess.run(["node", "-e", runner], capture_output=True, text=True)
    assert res.returncode == 0, f"Node 执行失败: {res.stderr}"
    assert "POLYGLOT_RESPONSIVE_SYNC_OK" in res.stdout
