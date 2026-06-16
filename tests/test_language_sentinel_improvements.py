# -*- coding: utf-8 -*-
"""
Illacme-plenipes Tests - Language Sentinel & Hub Improvements Test Case
职责：验证语种识别中的噪声清洗、标题中文优先加权判别等优化机制。
"""

from core.utils.language_hub import LanguageHub
from core.ingress.language_sentinel import LanguageSentinel

def test_language_hub_clean_noise() -> None:
    """验证 LanguageHub 物理降噪过滤代码块、HTML 及 URL 链接"""
    raw_text = (
        "Hello world. Check this URL: https://example.com/some/path. "
        "Also, here is a code block:\n"
        "```python\n"
        "def hello():\n"
        "    print('world')\n"
        "```\n"
        "And Obsidian link: [[another-link]]."
    )
    # 清洗后的文本中不应存在代码块、Obsidian 双链、链接及 URL
    clean = LanguageHub._clean_noise(raw_text)
    assert "https://example" not in clean
    assert "def hello" not in clean
    assert "another-link" not in clean
    assert "Hello world" in clean

def test_language_hub_detect_chinese_title_with_english_body() -> None:
    """验证当标题为纯中文，但正文富含高密度英文噪声时，智能判定为中文"""
    raw_md = (
        "---\n"
        "title: 竞品分析\n"
        "language: auto\n"
        "---\n"
        "Langbly Translate: https://github.com/Langbly/translate\n"
        "Crowdin SASS & CLI: https://store.crowdin.com/readme-io-proxy-translator\n"
        "Hugo Translator: https://github.com/rico00121/hugo-translator\n"
        "mdxlate: https://github.com/Softoft-Orga/markdown-automatic-translation\n"
        "Some details in english, but should be marked as zh because title is chinese."
    )
    detected = LanguageHub.detect_source_lang(raw_md)
    assert detected == "zh-Hans"

def test_language_sentinel_detect_chinese_title() -> None:
    """验证 Ingress 静态哨兵中对标题优先的语种判定机制"""
    content = (
        "# 竞品分析与发版策略指南\n\n"
        "Langbly Translate: https://github.com/Langbly/translate\n"
        "Crowdin SASS & CLI: https://store.crowdin.com/readme-io-proxy-translator\n"
    )
    detected = LanguageSentinel.detect_language(content)
    assert detected == "zh"
