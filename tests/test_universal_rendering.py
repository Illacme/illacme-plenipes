# -*- coding: utf-8 -*-
"""
Tests for Universal Theme / GenericSSGAdapter Markdown Enhancement & Full UI Layout
"""

from core.adapters.egress.ssg.generic import GenericSSGAdapter

def test_generic_ssg_adapter_wikilinks_and_callouts():
    adapter = GenericSSGAdapter()
    raw_md = """
# 📚 出版指南与文档中心

- **[[quick-start|⚡ 5 分钟极速上手指南]]**
- **[[authoring-and-vault-guide|✍️ 原稿文库组织与写作指引]]**

> [!TIP]
> 这是一个测试提示框！

```mermaid
graph TD
    A[原稿] --> B[分发]
```
"""
    fm = {"title": "出版指南与文档中心", "layout": "docs"}
    html, out_fm = adapter.render(raw_md, fm, target_lang="zh", sub_path="docs/index.html")

    # 1. 验证双链被正确解析为超链接
    assert '<a href="./quick-start.html" class="universal-link wikilink">⚡ 5 分钟极速上手指南</a>' in html
    assert '<a href="./authoring-and-vault-guide.html" class="universal-link wikilink">✍️ 原稿文库组织与写作指引</a>' in html

    # 2. 验证 Callout 被转换为提示卡片
    assert 'universal-callout callout-tip' in html
    assert '这是一个测试提示框！' in html

    # 3. 验证 Mermaid 图表被封装
    assert 'class="universal-mermaid"' in html
    assert 'class="mermaid"' in html

    # 4. 验证 Docs 页面包含侧边栏
    assert 'universal-docs-sidebar' in html
    assert '5 分钟上手指南' in html

    # 5. 验证顶部全局导航栏
    assert 'class="universal-header"' in html
    assert '官方文档' in html
    assert '官方博客' in html
    assert '案例展示' in html
    assert '关于我们' in html

def test_generic_ssg_adapter_multilingual_sidebar():
    adapter = GenericSSGAdapter()
    raw_md = "# Documentation\nWelcome"
    fm = {"title": "Docs Index", "layout": "docs"}
    
    # 英文 Docs 侧边栏
    html_en, _ = adapter.render(raw_md, fm, target_lang="en", sub_path="en/docs/index.html")
    assert "Core Onboarding Guide" in html_en
    assert "5-Minute Quick Start" in html_en
    assert "Governance & Operations" in html_en
    
    # 日文 Docs 侧边栏
    html_ja, _ = adapter.render(raw_md, fm, target_lang="ja", sub_path="ja/docs/index.html")
    assert "コア入門ガイド" in html_ja
    assert "5分でサクッと始める" in html_ja
    assert "ガバナンスセンターと運用" in html_ja

def test_ai_logic_hub_japanese_artifact_cleaning():
    from core.logic.ai.ai_logic_hub import AILogicHub
    
    sample1 = """翻訳

Illacme Press は、中央集権的なコンテンツプラットフォームによるデジタルの壁を打ち破ります。"""
    cleaned1 = AILogicHub.clean_translation_response(sample1)
    assert not cleaned1.startswith("翻訳")
    assert "Illacme Press は" in cleaned1

    sample2 = """## ✨ なぜ Illacme Plenipes を選ぶのか？

### 翻訳 ###"""
    cleaned2 = AILogicHub.clean_translation_response(sample2)
    assert "### 翻訳 ###" not in cleaned2
    assert "なぜ Illacme Plenipes を選ぶのか？" in cleaned2

    sample3 = """【翻訳】
1. 物理主権優先 (Physical Sovereignty First)"""
    cleaned3 = AILogicHub.clean_translation_response(sample3)
    assert "【翻訳】" not in cleaned3
    assert "1. 物理主権優先" in cleaned3

