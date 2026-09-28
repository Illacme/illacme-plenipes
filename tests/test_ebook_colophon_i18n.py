# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Colophon Multilingual & Property Rights Test Suite
模块职责：验证电子书出版物末尾版记 (Colophon / 奥付) 的多语言国际化渲染与物权编码 (UUID) 自动自愈注入。
"""

import os
import re
import zipfile
import tempfile
import pytest

from core.adapters.egress.ebook.colophon import ColophonBuilder
from core.adapters.egress.ebook.epub import EpubAdapter
from core.adapters.egress.ebook.webbook import WebBookAdapter
from core.bindery.book_assembler import BookAssembler


def test_colophon_uuid_auto_healing():
    """验证物权编码在缺失或为 N/A 时自动自愈为合规的 urn:uuid"""
    # 情况 1: 空 uuid
    meta_empty = {"title": "Test Book", "language": "en"}
    data1 = ColophonBuilder.build_colophon_data([], meta_empty, "epub")
    assert data1["uuid"].startswith("urn:uuid:")
    assert len(data1["uuid"]) > 20

    # 情况 2: N/A 脏值
    meta_na = {"title": "Test Book", "language": "en", "uuid": "N/A"}
    data2 = ColophonBuilder.build_colophon_data([], meta_na, "webbook")
    assert data2["uuid"].startswith("urn:uuid:")
    assert "N/A" not in data2["uuid"]


def test_colophon_multilingual_dictionary_and_rendering():
    """验证英、日、中多语种版记渲染无语言污染"""
    dummy_tree = [
        {"title": "Chapter 1", "html_body": "<p>Hello world of digital sovereignty.</p>"},
        {"title": "Chapter 2", "html_body": "<p>Another chapter with high quality text.</p>"}
    ]

    # 1. 英文版记测试
    en_meta = {
        "title": "Illacme Press · Digital Publication Collection (EN Edition)",
        "author": "Illacme Editorial Team",
        "publisher": "Illacme Plenipes Global Private Press",
        "language": "en"
    }
    en_data = ColophonBuilder.build_colophon_data(dummy_tree, en_meta, "webbook")
    en_xhtml = ColophonBuilder.render_xhtml(en_data, iso_lang="en")

    assert "📖 COLOPHON" in en_xhtml
    assert "Title" in en_xhtml
    assert "Author" in en_xhtml
    assert "Publisher" in en_xhtml
    assert "Edition Format" in en_xhtml
    assert "Contents" in en_xhtml
    assert "Digital Identifier (UUID)" in en_xhtml
    assert "urn:uuid:" in en_xhtml
    assert "N/A" not in en_xhtml
    assert "作品名称" not in en_xhtml
    assert "保留所有权利" not in en_xhtml

    # 2. 日文版记测试
    ja_meta = {
        "title": "Illacme Press · デジタル出版全集 (JA Edition)",
        "author": "Illacme Editorial Team",
        "publisher": "Illacme Plenipes Global Private Press",
        "language": "ja"
    }
    ja_data = ColophonBuilder.build_colophon_data(dummy_tree, ja_meta, "epub")
    ja_xhtml = ColophonBuilder.render_xhtml(ja_data, iso_lang="ja")

    assert "奥付" in ja_xhtml
    assert "作品名" in ja_xhtml
    assert "著者" in ja_xhtml
    assert "発行元" in ja_xhtml
    assert "装丁仕様" in ja_xhtml
    assert "デジタル物権コード (UUID)" in ja_xhtml
    assert "urn:uuid:" in ja_xhtml
    assert "N/A" not in ja_xhtml
    assert "作品名称" not in ja_xhtml


def test_epub_and_webbook_colophon_integration():
    """验证 EPUB 与 WebBook 导出真实包含多语种版记与合规物权编码"""
    with tempfile.TemporaryDirectory() as tmpdir:
        manuscripts = [
            {"title": "Section 1", "slug": "sec-1", "html_body": "<p>First section content.</p>"},
            {"title": "Section 2", "slug": "sec-2", "html_body": "<p>Second section content.</p>"}
        ]
        meta = {
            "title": "Universal Sovereignty",
            "author": "Eason & Claude",
            "publisher": "Illacme Global",
            "language": "en"
        }

        # 1. 验证 EPUB
        epub_path = os.path.join(tmpdir, "test_en.epub")
        epub_adapter = EpubAdapter()
        ok = epub_adapter.bind_book(manuscripts, meta, target_lang="en", output_file_path=epub_path)
        assert ok is True
        with zipfile.ZipFile(epub_path, "r") as zf:
            colophon_raw = zf.read("OEBPS/text/colophon.xhtml").decode("utf-8")
            assert "Digital Identifier (UUID)" in colophon_raw
            assert "urn:uuid:" in colophon_raw
            assert "N/A" not in colophon_raw
            assert "Title" in colophon_raw

        # 2. 验证 WebBook
        wb_path = os.path.join(tmpdir, "test_en.html")
        wb_adapter = WebBookAdapter()
        ok = wb_adapter.bind_book(manuscripts, meta, target_lang="en", output_file_path=wb_path)
        assert ok is True
        with open(wb_path, "r", encoding="utf-8") as f:
            wb_raw = f.read()
            assert "Digital Identifier (UUID)" in wb_raw
            assert "urn:uuid:" in wb_raw
            assert "N/A" not in wb_raw[wb_raw.find("Digital Identifier"):wb_raw.find("Digital Identifier")+150]


def test_epub_polyglot_colophon_parallel_columns():
    """验证多语对照模式下，EPUB 版记页生成包含各语言平行分栏与译本，杜绝单语缺失"""
    with tempfile.TemporaryDirectory() as tmpdir:
        manuscripts = [
            {
                "title": "第 1 卷 哲学纲领",
                "slug": "ch-1",
                "html_body": "<div class=\"wb-polyglot-block wb-polyglot-columns\"><div class=\"wb-poly-column\" data-lang=\"zh\"><p>中文内容</p></div><div class=\"wb-poly-column\" data-lang=\"en\"><p>English Content</p></div><div class=\"wb-poly-column\" data-lang=\"ja\"><p>日本語内容</p></div></div>",
                "titles_by_lang": {"zh": "第 1 卷 哲学纲领", "en": "Vol 1 Philosophy", "ja": "第 1 巻 哲学綱領"}
            },
            {
                "title": "第 2 卷 实践规范",
                "slug": "ch-2",
                "html_body": "<div class=\"wb-polyglot-block wb-polyglot-columns\"><div class=\"wb-poly-column\" data-lang=\"zh\"><p>中文内容2</p></div><div class=\"wb-poly-column\" data-lang=\"en\"><p>English Content 2</p></div><div class=\"wb-poly-column\" data-lang=\"ja\"><p>日本語内容2</p></div></div>",
                "titles_by_lang": {"zh": "第 2 卷 实践规范", "en": "Vol 2 Practice", "ja": "第 2 巻 実践規範"}
            }
        ]
        meta = {
            "title": "多语艺术双封面典籍",
            "author": "Illacme Master",
            "publisher": "Illacme Press",
            "language": "zh",
            "polyglot_langs": ["zh", "en", "ja"]
        }

        epub_path = os.path.join(tmpdir, "polyglot_test.epub")
        epub_adapter = EpubAdapter()
        ok = epub_adapter.bind_book(
            manuscripts,
            meta,
            target_lang="polyglot",
            output_file_path=epub_path
        )
        assert ok is True
        assert os.path.exists(epub_path)

        with zipfile.ZipFile(epub_path, "r") as zf:
            colophon_raw = zf.read("OEBPS/text/colophon.xhtml").decode("utf-8")
            # 1. 验证外层多语对照分栏容器
            assert "wb-polyglot-columns" in colophon_raw
            # 2. 验证包含全部三种语言的分栏
            assert '<div class="wb-poly-column" data-lang="zh">' in colophon_raw
            assert '<div class="wb-poly-column" data-lang="en">' in colophon_raw
            assert '<div class="wb-poly-column" data-lang="ja">' in colophon_raw
            # 3. 验证各自分栏中呈现的地道译本标题与版权字段
            assert "出版物版记" in colophon_raw
            assert "COLOPHON" in colophon_raw
            assert "奥付" in colophon_raw
            assert "Title" in colophon_raw
            assert "作品名" in colophon_raw
            assert "Digital Identifier (UUID)" in colophon_raw
