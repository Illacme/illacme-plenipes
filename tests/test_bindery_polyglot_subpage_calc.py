# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Polyglot Reader Subpage & Volume Semantics Tests
测试范围：
1. 验证多语言阅读器分页目标点算法 (getPolyglotTargets) 严格单调递增，无相邻重复页，末尾差值 >= 48px。
2. 验证卡片语义识别 (getCardMeta) 正确识别封面、目录、版记，不将其计为正文卷数，正文从第 1 卷准确计数。
"""

import json
import subprocess
from core.adapters.egress.ebook.epub_reader_polyglot_js import get_epub_reader_polyglot_js


def test_get_polyglot_targets_no_duplicate_pages():
    """验证各种不同高度下，绝不出现末尾重复或两页相同的 bug"""
    poly_js = get_epub_reader_polyglot_js()
    payload = json.dumps(poly_js)
    node_script = f"""
    const polyCode = {payload};
    const testCases = [
      {{ vh: 600, sh: 600 }},
      {{ vh: 600, sh: 620 }},
      {{ vh: 600, sh: 800 }},
      {{ vh: 600, sh: 1180 }},
      {{ vh: 600, sh: 1200 }},
      {{ vh: 600, sh: 1205 }},
      {{ vh: 600, sh: 1250 }},
      {{ vh: 600, sh: 1800 }},
      {{ vh: 800, sh: 2400 }}
    ];

    const fnPrimaryMatch = polyCode.match(/function getPrimaryCol\\([^\\)]*\\)\\s*\\{{[\\s\\S]*?\\n  \\}}/);
    const fnMatch = polyCode.match(/function getPolyglotTargets\\([^\\)]*\\)\\s*\\{{[\\s\\S]*?\\n  \\}}/);
    if (!fnMatch) throw new Error('未找到 getPolyglotTargets 函数定义');
    const primaryLang = 'zh';
    const getPolyglotTargets = new Function('cols', 'card', (fnPrimaryMatch ? fnPrimaryMatch[0] : '') + '; ' + fnMatch[0] + '; return getPolyglotTargets(cols, card);');

    for (const tc of testCases) {{
      const cols = [{{ clientHeight: tc.vh, scrollHeight: tc.sh }}];
      const targets = getPolyglotTargets(cols);
      if (!targets || targets.length === 0) throw new Error(`空 targets: ${{JSON.stringify(tc)}}`);
      for (let i = 1; i < targets.length; i++) {{
        if (targets[i] <= targets[i - 1]) {{
          throw new Error(`发现重复或递减分页点: ${{JSON.stringify(targets)}} for ${{JSON.stringify(tc)}}`);
        }}
        if (targets[i] - targets[i - 1] < 48) {{
          throw new Error(`相邻页位移差过小 (<48px): ${{targets[i] - targets[i-1]}}px in ${{JSON.stringify(targets)}}`);
        }}
      }}
    }}
    console.log('TARGETS_NO_DUPLICATE_PASS');
    """
    res = subprocess.run(['node', '-e', node_script], capture_output=True, text=True)
    assert res.returncode == 0, f"Node 执行失败: {res.stderr}"
    assert "TARGETS_NO_DUPLICATE_PASS" in res.stdout


def test_card_meta_distinguishes_auxiliary_pages():
    """验证封面、目录、版记不被作为卷呈现，正文卷号准确"""
    poly_js = get_epub_reader_polyglot_js()
    payload = json.dumps(poly_js)
    node_script = f"""
    const polyCode = {payload};
    const fnMetaMatch = polyCode.match(/function getCardMeta\\([^\\)]*\\)\\s*\\{{[\\s\\S]*?\\n  \\}}/);
    if (!fnMetaMatch) throw new Error('未找到 getCardMeta 函数定义');
    const getCardMeta = new Function('card', 'allCards', fnMetaMatch[0] + '; return getCardMeta(card, allCards);');

    const mockCover = {{ id: 'er-doc-cover_xhtml', classList: {{ contains: (c) => c === 'er-cover-card' }} }};
    const mockNav = {{ id: 'er-doc-nav_xhtml', classList: {{ contains: () => false }} }};
    const mockCh1 = {{ id: 'er-doc-ch_1_xhtml', classList: {{ contains: () => false }} }};
    const mockCh2 = {{ id: 'er-doc-ch_2_xhtml', classList: {{ contains: () => false }} }};
    const mockCh3 = {{ id: 'er-doc-ch_3_xhtml', classList: {{ contains: () => false }} }};
    const mockColophon = {{ id: 'er-doc-colophon_xhtml', classList: {{ contains: () => false }} }};

    const allCards = [mockCover, mockNav, mockCh1, mockCh2, mockCh3, mockColophon];

    const metaCover = getCardMeta(mockCover, allCards);
    if (metaCover.type !== 'cover') throw new Error('封面类型错误: ' + JSON.stringify(metaCover));

    const metaNav = getCardMeta(mockNav, allCards);
    if (metaNav.type !== 'nav') throw new Error('目录类型错误: ' + JSON.stringify(metaNav));

    const metaCh1 = getCardMeta(mockCh1, allCards);
    if (metaCh1.type !== 'chapter' || metaCh1.chapterNum !== 1 || metaCh1.totalChapters !== 3) {{
      throw new Error('正文第一卷元数据错误: ' + JSON.stringify(metaCh1));
    }}

    const metaCh3 = getCardMeta(mockCh3, allCards);
    if (metaCh3.type !== 'chapter' || metaCh3.chapterNum !== 3 || metaCh3.totalChapters !== 3) {{
      throw new Error('正文第三卷元数据错误: ' + JSON.stringify(metaCh3));
    }}

    const metaColophon = getCardMeta(mockColophon, allCards);
    if (metaColophon.type !== 'colophon') throw new Error('版记类型错误: ' + JSON.stringify(metaColophon));

    console.log('CARD_META_SEMANTICS_PASS');
    """
    res = subprocess.run(['node', '-e', node_script], capture_output=True, text=True)
    assert res.returncode == 0, f"Node 执行失败: {res.stderr}"
    assert "CARD_META_SEMANTICS_PASS" in res.stdout
