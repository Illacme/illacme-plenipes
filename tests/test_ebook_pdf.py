# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EBook PDF Adapter & Print Assets Test Suite
模块职责：全面验证印刷级 PDF 电子书适配器契约、CSS Paged Media 样式规范、
前置目录生成、双引擎调度（无头 Chrome 探测与 ReportLab 兜底自愈）及全链路装订。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import tempfile
from unittest.mock import patch, MagicMock
import pytest

from core.adapters.egress.ebook.base import EBookRegistry
from core.adapters.egress.ebook.pdf import PDFBookAdapter
from core.adapters.egress.ebook.pdf_assets import PDFAssets


def test_pdf_adapter_registry_contract():
    """验证 PDF 适配器正确注册并满足 BaseEBookAdapter 契约"""
    adapter_cls = EBookRegistry.get_adapter("pdf")
    assert adapter_cls is PDFBookAdapter
    assert PDFBookAdapter.PLUGIN_ID == "pdf"
    assert PDFBookAdapter.OUTPUT_EXTENSION == ".pdf"
    assert PDFBookAdapter.MIME_TYPE == "application/pdf"
    assert "PDF" in PDFBookAdapter.DISPLAY_NAME


def test_pdf_assets_print_css():
    """验证 PDF 印刷级 CSS 包含关键 Paged Media 规则与防死锁设计"""
    css = PDFAssets.get_print_css()
    assert "@page" in css
    assert "size: A4 portrait" in css
    assert ".cover-page" in css
    assert ".toc-page" in css
    assert ".chapter-page" in css
    assert ".colophon-section" in css
    # 防死锁设计断言
    assert "-webkit-text-fill-color: initial !important" in css
    assert "border-collapse: collapse !important" in css


def test_pdf_assets_render_toc_html():
    """验证前置目录 (Print TOC) 的生成与多语种标题适配"""
    tree = [
        {"title": "第一章 初始启航"},
        {"title": "第二章 架构主权"},
        {"title": "第三章 落地实操"},
    ]
    # 中文目录
    zh_toc = PDFAssets.render_toc_html(tree, lang="zh")
    assert 'id="print-toc"' in zh_toc
    assert "目  录" in zh_toc
    assert "第一章 初始启航" in zh_toc
    assert 'href="#ch_1"' in zh_toc
    assert "01." in zh_toc
    assert "03." in zh_toc

    # 英文目录
    en_toc = PDFAssets.render_toc_html(tree, lang="en")
    assert "TABLE OF CONTENTS" in en_toc

    # 单章节时不生成冗余目录
    single_tree = [{"title": "唯一章节"}]
    assert PDFAssets.render_toc_html(single_tree, lang="zh") == ""


def test_pdf_assets_render_colophon_html():
    """验证出版版权页 (Colophon) HTML 包装结构"""
    colophon_data = {
        "title": "测试全集",
        "author": "测试作者",
        "publisher": "Illacme Press",
        "year": "2026",
        "format_name": "pdf",
    }
    html = PDFAssets.render_colophon_html(colophon_data, lang="zh")
    assert 'id="print-colophon"' in html
    assert "测试全集" in html
    assert "测试作者" in html


def test_pdf_find_chrome_detection():
    """验证 Chrome 二进制路径探测函数在候选存在与不存在时的行为"""
    with patch("os.path.exists", return_value=True), \
         patch("os.access", return_value=True):
        chrome = PDFBookAdapter._find_chrome()
        assert chrome is not None

    with patch("shutil.which", return_value=None), \
         patch("os.path.exists", return_value=False):
        chrome = PDFBookAdapter._find_chrome()
        assert chrome is None


def test_pdf_render_via_headless_mock():
    """验证无头浏览器调用流程与命令参数拼装"""
    adapter = PDFBookAdapter()
    manuscript_tree = [
        {
            "title": "导言",
            "html_body": '<p>这是内容，内含链接 <a href="ch_2.xhtml#sec1">第二章</a></p>',
            "assets": []
        },
        {
            "title": "第二章",
            "html_body": '<p>这是第二章内容</p>',
            "assets": []
        }
    ]
    meta = {
        "title": "主权印本",
        "author": "测试专家",
        "publisher": "Sovereign Press"
    }

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
        out_pdf = tf.name

    try:
        with patch("subprocess.run") as mock_run, \
             patch("os.path.exists", return_value=True), \
             patch("os.path.getsize", return_value=5000):
            mock_run.return_value = MagicMock(returncode=0)
            res = adapter._render_via_headless(
                chrome_bin="/usr/bin/mock-chrome",
                manuscript_tree=manuscript_tree,
                meta=meta,
                cover_path=None,
                lang="zh",
                out_pdf=out_pdf
            )
            assert res is True
            assert mock_run.called
            args, kwargs = mock_run.call_args
            cmd = args[0]
            assert cmd[0] == "/usr/bin/mock-chrome"
            assert "--headless" in cmd
            assert f"--print-to-pdf={out_pdf}" in cmd
    finally:
        if os.path.exists(out_pdf):
            try: os.remove(out_pdf)
            except Exception: pass


def test_pdf_render_fallback_behavior():
    """验证当 Chrome 探测失败时，bind_book 能平稳触发自愈降级分支"""
    adapter = PDFBookAdapter()
    manuscript_tree = [{"title": "章节一", "html_body": "<p>测试内容</p>", "assets": []}]
    meta = {"title": "自愈测试", "author": "作者"}

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
        out_pdf = tf.name

    try:
        with patch.object(adapter, "_find_chrome", return_value=None), \
             patch.object(adapter, "_render_via_reportlab", return_value=True) as mock_rl:
            success = adapter.bind_book(
                manuscript_tree=manuscript_tree,
                book_metadata=meta,
                cover_image_path=None,
                target_lang="zh",
                output_file_path=out_pdf
            )
            assert success is True
            assert mock_rl.called
    finally:
        if os.path.exists(out_pdf):
            try: os.remove(out_pdf)
            except Exception: pass
