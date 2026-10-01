# -*- coding: utf-8 -*-
"""
Tests for PDF Facing Pages Concordance (洛布古典丛书级双开面对照 PDF 排版自动化测试)
"""

import os
import pytest
from core.adapters.egress.ebook.pdf import PDFBookAdapter
from core.adapters.egress.ebook.pdf_facing_pages import PDFFacingPagesBuilder


def test_pdf_facing_pages_builder_structure():
    """验证 PDFFacingPagesBuilder 生成的对称 Verso/Recto 对开面结构"""
    manuscript_tree = [
        {
            "title": "多品牌主权矩阵",
            "chapter_by_lang": {
                "zh": {
                    "title": "多品牌主权矩阵",
                    "raw_body": "# 🏷️ 多品牌主权矩阵\n\n> [!TIP]\n> 一次起草，多元矩阵独立发行。\n\n## 架构全景\n\n物理隔离出版。"
                },
                "en": {
                    "title": "Multi-Brand Sovereign Matrix",
                    "raw_body": "> [!TIP]\n> Draft Once, Publish Independently Across a Diverse Matrix.\n\n## Architecture Overview\n\nPhysically isolated publishing."
                }
            }
        }
    ]

    sections = PDFFacingPagesBuilder.render_facing_chapters(
        manuscript_tree=manuscript_tree,
        polyglot_langs=["zh", "en"],
        asset_map={},
        publisher="Illacme Press",
        author="Editorial Team",
        is_single=False
    )

    assert len(sections) == 2, "每个章节必须生成一对对开面 (Verso + Recto)"

    # 1. 验证左页 (Verso / 原稿)
    verso_html = sections[0]
    assert "facing-verso" in verso_html
    assert "ZH 原稿 (VERSO)" in verso_html
    assert "第 1 章" in verso_html
    assert "多品牌主权矩阵" in verso_html
    assert "一次起草，多元矩阵独立发行" in verso_html
    # 验证首行重复 H1 被成功剥离，避免正文重复大标题
    assert not verso_html.startswith("<h1>🏷️ 多品牌主权矩阵</h1>")

    # 2. 验证右页 (Recto / 译稿)
    recto_html = sections[1]
    assert "facing-recto" in recto_html
    assert "EN CONCORDANCE (RECTO)" in recto_html
    assert "Chapter 1" in recto_html
    assert "Multi-Brand Sovereign Matrix" in recto_html
    assert "Draft Once, Publish Independently" in recto_html


def test_pdf_facing_pages_end_to_end_bind(tmp_path):
    """端到端验证 PDFBookAdapter 双语对照导出双开面 PDF"""
    adapter = PDFBookAdapter()
    out_pdf = str(tmp_path / "test_polyglot_facing.pdf")

    manuscript_tree = [
        {
            "title": "主权出版哲学",
            "chapter_by_lang": {
                "zh": {
                    "title": "主权出版哲学",
                    "raw_body": "思想的自由取决于出版载体的主权控制。"
                },
                "en": {
                    "title": "Philosophy of Sovereign Publishing",
                    "raw_body": "Freedom of thought relies on sovereign control over publishing mediums."
                }
            }
        }
    ]

    book_meta = {
        "title": "主权出版典籍",
        "author": "Illacme Authors",
        "publisher": "Illacme Press",
        "language": "mul",
        "polyglot_langs": ["zh", "en"],
        "is_single_article": False,
        "cover_mode": "none"
    }

    success = adapter.bind_book(
        manuscript_tree=manuscript_tree,
        book_metadata=book_meta,
        cover_image_path=None,
        target_lang="zh",
        output_file_path=out_pdf
    )

    assert success is True
    assert os.path.exists(out_pdf)
    assert os.path.getsize(out_pdf) > 1000
