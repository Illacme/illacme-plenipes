# -*- coding: utf-8 -*-
"""
📖 [V125.3] Test Suite for Single Article Colophon Suppression
测试目标：
1. 单篇独立文章导出时，EPUB 适配器自动抑制版记页 (colophon.xhtml) 生成与目录索引
2. 单篇独立文章导出时，WebBook 适配器自动跳过版记卡片与大纲导航项
3. 单篇独立文章导出时，PDF 适配器自动剔除末尾 print-colophon 章节
4. 多章节合集或全书装订时，正常保留出版版记与物权指纹
"""

import os
import zipfile
import pytest

from core.adapters.egress.ebook.epub import EpubAdapter
from core.adapters.egress.ebook.webbook import WebBookAdapter
from core.adapters.egress.ebook.pdf import PDFBookAdapter
from core.bindery.book_assembler import BookAssembler


@pytest.fixture
def sample_single_manuscript():
    """单篇章节原稿树"""
    return [
        {
            "filename": "ch_1.xhtml",
            "title": "深度学习实战指南",
            "html_body": "<h1>深度学习实战指南</h1><p>这是单篇独立文章的正文内容。</p>",
            "assets": []
        }
    ]


@pytest.fixture
def sample_multi_manuscript():
    """多篇章节原稿树"""
    return [
        {
            "filename": "ch_1.xhtml",
            "title": "第一章：基础",
            "html_body": "<h1>第一章：基础</h1><p>第一章内容。</p>",
            "assets": []
        },
        {
            "filename": "ch_2.xhtml",
            "title": "第二章：进阶",
            "html_body": "<h1>第二章：进阶</h1><p>第二章内容。</p>",
            "assets": []
        }
    ]


def test_epub_colophon_suppression(tmp_path, sample_single_manuscript, sample_multi_manuscript):
    """验证 EPUB 导出：单篇无版记，多章保留版记"""
    adapter = EpubAdapter()

    # 1. 单篇导出测试
    single_out = str(tmp_path / "single_test.epub")
    adapter.bind_book(
        manuscript_tree=sample_single_manuscript,
        book_metadata={"title": "单篇测试", "author": "作者", "is_single_article": True},
        output_file_path=single_out
    )
    with zipfile.ZipFile(single_out, 'r') as zf:
        namelist = zf.namelist()
        assert "OEBPS/text/colophon.xhtml" not in namelist
        toc_ncx = zf.read("OEBPS/toc.ncx").decode("utf-8")
        assert "colophon.xhtml" not in toc_ncx

    # 2. 多章导出测试
    multi_out = str(tmp_path / "multi_test.epub")
    adapter.bind_book(
        manuscript_tree=sample_multi_manuscript,
        book_metadata={"title": "多章合集", "author": "作者", "is_single_article": False},
        output_file_path=multi_out
    )
    with zipfile.ZipFile(multi_out, 'r') as zf:
        namelist = zf.namelist()
        assert "OEBPS/text/colophon.xhtml" in namelist
        toc_ncx = zf.read("OEBPS/toc.ncx").decode("utf-8")
        assert "colophon.xhtml" in toc_ncx


def test_webbook_colophon_suppression(tmp_path, sample_single_manuscript, sample_multi_manuscript):
    """验证 WebBook 导出：单篇无版记卡片与大纲，多章正常保留"""
    adapter = WebBookAdapter()

    # 1. 单篇导出测试
    single_out = str(tmp_path / "single_test.html")
    adapter.bind_book(
        manuscript_tree=sample_single_manuscript,
        book_metadata={"title": "单篇测试", "author": "作者", "is_single_article": True},
        output_file_path=single_out
    )
    with open(single_out, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'id="colophon"' not in content
        assert '✦ 版记' not in content
        assert 'wb-poly-item wb-colophon-card' not in content

    # 2. 多章导出测试
    multi_out = str(tmp_path / "multi_test.html")
    adapter.bind_book(
        manuscript_tree=sample_multi_manuscript,
        book_metadata={"title": "多章合集", "author": "作者", "is_single_article": False},
        output_file_path=multi_out
    )
    with open(multi_out, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'id="colophon"' in content
        assert 'wb-poly-item wb-colophon-card' in content


def test_pdf_colophon_suppression(monkeypatch, tmp_path, sample_single_manuscript, sample_multi_manuscript):
    """验证 PDF 导出：单篇无 print-colophon 章节，多章正常保留"""
    adapter = PDFBookAdapter()

    captured_htmls = []

    import subprocess
    def mock_subprocess_run(cmd, *args, **kwargs):
        # cmd[-1] 是 tmp_html 路径，cmd[-2] 是 --print-to-pdf=out_pdf
        tmp_html = cmd[-1]
        out_pdf = cmd[-2].split("=", 1)[1]
        if os.path.exists(tmp_html):
            with open(tmp_html, "r", encoding="utf-8") as f:
                captured_htmls.append(f.read())
        with open(out_pdf, "wb") as pf:
            pf.write(b"%PDF-1.4 mock print bytes " * 20)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr("subprocess.run", mock_subprocess_run)
    monkeypatch.setattr(PDFBookAdapter, "_find_chrome", staticmethod(lambda: "/usr/bin/mock-chrome"))

    # 1. 单篇导出测试
    single_out = str(tmp_path / "single_test.pdf")
    adapter.bind_book(
        manuscript_tree=sample_single_manuscript,
        book_metadata={"title": "单篇测试", "author": "作者", "is_single_article": True},
        output_file_path=single_out
    )
    assert len(captured_htmls) == 1
    assert 'id="print-colophon"' not in captured_htmls[0]

    # 2. 多章导出测试
    multi_out = str(tmp_path / "multi_test.pdf")
    adapter.bind_book(
        manuscript_tree=sample_multi_manuscript,
        book_metadata={"title": "多章合集", "author": "作者", "is_single_article": False},
        output_file_path=multi_out
    )
    assert len(captured_htmls) == 2
    assert 'id="print-colophon"' in captured_htmls[1]


def test_assembler_single_article_flag(tmp_path):
    """验证 BookAssembler 在 single_file 或 len(chapters)<=1 时自动注入 is_single_article"""
    doc = tmp_path / "test.md"
    doc.write_text("# 测试文章\n这是内容", encoding="utf-8")

    assembler = BookAssembler(engine=None, vault_dir=str(tmp_path))
    out = assembler.assemble_and_bind(
        category="",
        format_type="webbook",
        single_file="test.md",
        output_dir=str(tmp_path / "out")
    )
    assert out and os.path.exists(out)
    with open(out, 'r', encoding='utf-8') as f:
        html = f.read()
        assert 'id="colophon"' not in html
