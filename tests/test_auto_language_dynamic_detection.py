#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 单元测试：自动语种 (auto) 基于文章内容的动态检测与反模式彻底规避门禁
验证：
1. 任何 auto 设置绝不能被指定为固定值 (如 "zh")。
2. 纯英文文章自动探测为 en，纯中文文章自动探测为 zh-Hans。
3. Frontmatter 显式语言优于内容探测。
4. load_syndication_content_and_metadata 正确动态解析实际母语并绑定至目标槽。
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock
from core.utils.language_hub import LanguageHub
from services.api.logic.dispatch_ops_shards.pipeline_shards.pipeline_syndicate_loader import (
    load_syndication_content_and_metadata
)

def test_resolve_document_language_frontmatter_priority():
    content = "---\ntitle: Sample\nlang: ja\n---\nHello world this is an english text"
    fm = {"lang": "ja", "title": "Sample"}
    res = LanguageHub.resolve_document_language(content=content, fm=fm)
    assert res == "ja"

def test_resolve_document_language_english_content():
    content = "# Welcome to Illacme Plenipes\n\nThis is a complete architectural documentation written in pure English without any Chinese characters."
    res = LanguageHub.resolve_document_language(content=content, doc_info={"source_lang": "auto"})
    assert res == "en", f"Expected 'en', got '{res}'"

def test_resolve_document_language_chinese_content():
    content = "# 欢迎使用 Illacme Plenipes\n\n这是一个完全用中文书写的工程架构说明文档，包含充足的汉字内容。"
    res = LanguageHub.resolve_document_language(content=content, doc_info={"source_lang": "auto"})
    assert res == "zh-Hans", f"Expected 'zh-Hans', got '{res}'"

def test_resolve_to_name_auto():
    # 彻底杜绝 auto 解析为 "Chinese (Simplified)"
    res = LanguageHub.resolve_to_name("auto")
    assert "Chinese" not in res
    assert "Auto" in res

def test_loader_dynamic_detection_for_english_file():
    with tempfile.TemporaryDirectory() as tmp_vault:
        doc_filename = "quickstart.md"
        doc_path = os.path.join(tmp_vault, doc_filename)
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("# Quickstart Guide\n\nFollow these simple steps to deploy your modern documentation website.")

        mock_engine = MagicMock()
        mock_engine.vault_root = tmp_vault
        mock_engine.translator = None

        doc_info = {
            "source_lang": "auto",
            "title": "Quickstart Guide",
            "translations": {}
        }

        # 当 target_slot 为 auto 时，应当动态探测出真实母语为 en，且不应寻找翻译
        title, body, fm = load_syndication_content_and_metadata(
            mock_engine, doc_filename, doc_info, target_slot="auto"
        )

        assert title == "Quickstart Guide"
        assert fm.get("_detected_source_lang") == "en"
        assert "Quickstart Guide" in body
