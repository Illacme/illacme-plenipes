# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Test PDF Chunked Printer & Instant Merger
验证：长篇章节与多语对照分批切片打印、PyMuPDF/PyPDF2 极速合并与异常自愈降级。
"""

import os
import tempfile
import pytest
from core.adapters.egress.ebook.pdf_chunk_printer import PDFChunkPrinter


def test_chunk_printer_empty_sections():
    """验证空节时返回 False"""
    res = PDFChunkPrinter.render_and_merge("dummy_chrome", "<html>", [], "</html>", "/tmp/out.pdf")
    assert res is False


def test_chunk_printer_merge_logic():
    """验证 _merge_pdfs 能够有效利用 pypdf / fitz 完成多 PDF 缝合"""
    # 创建两个临时小 PDF
    p1 = "/tmp/test_chunk_p1.pdf"
    p2 = "/tmp/test_chunk_p2.pdf"
    out_pdf = "/tmp/test_chunk_out.pdf"

    # 兼容 pymupdf / fitz 或 pypdf
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        for p in [p1, p2]:
            d = fitz.open()
            d.new_page(width=200, height=200)
            d.save(p)
            d.close()
    except ImportError:
        from pypdf import PdfWriter
        for p in [p1, p2]:
            w = PdfWriter()
            w.add_blank_page(width=200, height=200)
            with open(p, "wb") as f:
                w.write(f)

    try:
        success = PDFChunkPrinter._merge_pdfs([p1, p2], out_pdf)
        assert success is True
        assert os.path.exists(out_pdf)

        # 验证合并后的页数为 2
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open(out_pdf)
            assert len(doc) == 2
            doc.close()
        except ImportError:
            from pypdf import PdfReader
            reader = PdfReader(out_pdf)
            assert len(reader.pages) == 2
    finally:
        for f in [p1, p2, out_pdf]:
            if os.path.exists(f):
                os.remove(f)
