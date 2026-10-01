# -*- coding: utf-8 -*-
"""
Tests for PDF Running Footer & Folio Stamp Engine (PDFFolioStamp)
验证：封面 0 污染、前置目录小写罗马页码、正文居中短横线物理页码与异常自愈。
"""

import os
import tempfile
import pytest
from core.adapters.egress.ebook.pdf_folio_stamp import PDFFolioStamp


def test_pdf_folio_stamp_non_existent():
    """验证文件不存在时优雅返回 False"""
    assert PDFFolioStamp.stamp_folios("/tmp/non_existent_file_123.pdf") is False


def test_pdf_folio_stamp_pipeline():
    """验证多页 PDF 物理页码注入机制"""
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
    except ImportError:
        pytest.skip("fitz/pymupdf not installed in this environment")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
        tmp_pdf = tf.name

    try:
        # 构建一个包含封面、目录、两个正文章节的测试 PDF
        doc = fitz.open()

        # Page 0: 封面
        p0 = doc.new_page(width=595, height=842)
        p0.insert_text((100, 200), "Cover Title: Global Sovereign Book", fontsize=18)

        # Page 1: 目录
        p1 = doc.new_page(width=595, height=842)
        p1.insert_text((100, 100), "TABLE OF CONTENTS", fontsize=16)
        p1.insert_text((100, 150), "01. First Chapter ...... CH 1 ->", fontsize=10)

        # Page 2: 第 1 章
        p2 = doc.new_page(width=595, height=842)
        p2.insert_text((100, 100), "Chapter 1: Publishing Core Principles", fontsize=16)
        p2.insert_text((100, 150), "This is the content of chapter 1.", fontsize=10)

        # Page 3: 第 1 章续页
        p3 = doc.new_page(width=595, height=842)
        p3.insert_text((100, 150), "This is the continuation of chapter 1.", fontsize=10)

        # Page 4: 第 2 章
        p4 = doc.new_page(width=595, height=842)
        p4.insert_text((100, 100), "Chapter 2: Syndication Matrix", fontsize=16)
        p4.insert_text((100, 150), "This is the content of chapter 2.", fontsize=10)

        doc.save(tmp_pdf)
        doc.close()

        # 执行页码印章注入
        res = PDFFolioStamp.stamp_folios(tmp_pdf, has_cover=True)
        assert res is True

        # 读取验证
        doc_injected = fitz.open(tmp_pdf)
        assert len(doc_injected) == 5

        # 1. 验证封面页 (Page 0) 无任何页码
        t0 = doc_injected[0].get_text()
        assert "- 1 -" not in t0
        assert " - " not in t0

        # 2. 验证目录页 (Page 1) 具有小写罗马页码 i
        t1 = doc_injected[1].get_text()
        assert "i" in t1

        # 3. 验证正文第 1 页 (Page 2) 具有正文起始页码 - 1 -
        t2 = doc_injected[2].get_text()
        assert "- 1 -" in t2

        # 4. 验证正文第 2 页续页 (Page 3) 具有页码 - 2 -
        t3 = doc_injected[3].get_text()
        assert "- 2 -" in t3

        # 5. 验证正文第 3 页 (Page 4) 具有页码 - 3 -
        t4 = doc_injected[4].get_text()
        assert "- 3 -" in t4

        doc_injected.close()

    finally:
        if os.path.exists(tmp_pdf):
            os.remove(tmp_pdf)


def test_pdf_folio_detect_chapter_pages():
    """验证从物理 PDF 中自动探测各章节起始逻辑页码（Two-Pass 核心）"""
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
    except ImportError:
        pytest.skip("fitz/pymupdf not installed in this environment")

    # 1. 验证不存在的文件
    assert PDFFolioStamp.detect_chapter_pages("/tmp/non_existent.pdf", chapter_count=2) == {}

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
        tmp_pdf = tf.name

    try:
        doc = fitz.open()
        # Page 0: 封面
        p0 = doc.new_page(width=595, height=842)
        p0.insert_text((100, 200), "Cover Title", fontsize=18)

        # Page 1: 目录
        p1 = doc.new_page(width=595, height=842)
        p1.insert_text((100, 100), "TABLE OF CONTENTS", fontsize=16)

        # Page 2: 第 1 章（正文逻辑第 1 页）
        p2 = doc.new_page(width=595, height=842)
        p2.insert_text((100, 100), "Chapter 1: Core Principles", fontsize=16)

        # Page 3: 第 1 章续页（正文逻辑第 2 页）
        p3 = doc.new_page(width=595, height=842)
        p3.insert_text((100, 100), "Chapter 1 Continuation", fontsize=12)

        # Page 4: 第 2 章（正文逻辑第 3 页）
        p4 = doc.new_page(width=595, height=842)
        p4.insert_text((100, 100), "Chapter 2: Syndication Matrix", fontsize=16)

        doc.save(tmp_pdf)
        doc.close()

        # 探测章节物理页码
        page_map = PDFFolioStamp.detect_chapter_pages(
            tmp_pdf,
            chapter_count=2,
            has_cover=True,
            chapter_titles=["Core Principles", "Syndication Matrix"]
        )

        assert page_map == {0: 1, 1: 3}

        # 验证回填至 PDFAssets.render_toc_html 生成带有精确印厂物理页码的 HTML
        from core.adapters.egress.ebook.pdf_assets import PDFAssets
        manuscripts = [
            {"title": "Core Principles", "html_body": "<p>ch1</p>"},
            {"title": "Syndication Matrix", "html_body": "<p>ch2</p>"}
        ]
        toc_html = PDFAssets.render_toc_html(manuscripts, page_map=page_map)
        assert '<span class="toc-target">P. 1</span>' in toc_html
        assert '<span class="toc-target">P. 3</span>' in toc_html
        assert 'CH 1 &rarr;' not in toc_html

    finally:
        if os.path.exists(tmp_pdf):
            os.remove(tmp_pdf)

