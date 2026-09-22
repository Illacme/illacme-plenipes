# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Single-File WebBook EBook Test Suite
模块职责：验证单文件交互式 WebBook 驱动的自发现、Base64 离线资源封包、侧边栏交互、三模主题与端到端装订。
"""

import os
import tempfile
import base64
import pytest
from fastapi.testclient import TestClient

from core.adapters.egress.ebook import EBookRegistry, BaseEBookAdapter
from core.adapters.egress.ebook.webbook import WebBookAdapter
from core.bindery.book_assembler import BookAssembler


def test_webbook_adapter_discovery():
    """验证 WebBook 驱动已成功接入注册中心契约"""
    all_names = EBookRegistry.get_all_names()
    assert "webbook" in all_names
    adapter_cls = EBookRegistry.get_adapter("webbook")
    assert adapter_cls is WebBookAdapter
    assert issubclass(adapter_cls, BaseEBookAdapter)
    assert adapter_cls.OUTPUT_EXTENSION == ".html"
    assert "text/html" in adapter_cls.MIME_TYPE


def test_webbook_adapter_self_contained_packaging():
    """验证生成的 WebBook 具备完整的自包含离线能力（Base64插图/封面、TOC、即时搜索与三模主题）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. 构造测试封面与物理图片
        cover_path = os.path.join(tmpdir, "cover.png")
        with open(cover_path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\nFakeCoverData")

        img_path = os.path.join(tmpdir, "diagram.png")
        with open(img_path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\nFakeDiagramData")

        out_file = os.path.join(tmpdir, "handbook.html")
        adapter = WebBookAdapter()

        manuscript = [
            {
                "order": 1,
                "title": "第一章：数字出版主权",
                "slug": "chapter-1",
                "html_body": f'<p>正文内容如下：</p><p><img src="../images/img_test_diagram.png" alt="图示" /></p>',
                "assets": [
                    {
                        "target_name": "img_test_diagram.png",
                        "src_path": img_path,
                        "mime_type": "image/png"
                    }
                ]
            },
            {
                "order": 2,
                "title": "第二章：全网分发协议",
                "slug": "chapter-2",
                "html_body": '<p>本章探讨多渠道分发架构。</p>',
                "assets": []
            }
        ]

        meta = {
            "title": "主权出版全息实战指南",
            "author": "Illacme 架构组",
            "publisher": "Illacme Plenipes Press",
            "date": "2026-09-22"
        }

        success = adapter.bind_book(
            manuscript_tree=manuscript,
            book_metadata=meta,
            cover_image_path=cover_path,
            target_lang="zh",
            output_file_path=out_file
        )

        assert success is True
        assert os.path.exists(out_file)

        with open(out_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # 2. 离线自包含断言：封面与正文插图均已 Base64 内联
        assert "data:image/png;base64," in html_content
        assert base64.b64encode(b"\x89PNG\r\n\x1a\nFakeCoverData").decode('utf-8') in html_content
        assert base64.b64encode(b"\x89PNG\r\n\x1a\nFakeDiagramData").decode('utf-8') in html_content

        # 3. 沉浸式阅读器 UI 组件断言
        assert 'id="wb-sidebar"' in html_content
        assert 'id="wb-search"' in html_content
        assert 'class="wb-toc"' in html_content
        assert 'data-theme="light"' in html_content
        assert 'data-theme="dark"' in html_content
        assert 'data-theme="sepia"' in html_content
        assert 'id="wb-font-inc"' in html_content
        assert 'id="wb-font-dec"' in html_content
        assert 'id="wb-progress"' in html_content

        # 4. 内容与目录断言
        assert "第一章：数字出版主权" in html_content
        assert "第二章：全网分发协议" in html_content
        assert 'id="ch_1"' in html_content
        assert 'id="ch_2"' in html_content

        # 5. 版记断言
        assert 'id="colophon"' in html_content
        assert "Colophon" in html_content
        assert "Illacme 架构组" in html_content


def test_book_assembler_webbook_end_to_end():
    """验证 BookAssembler 调度 webbook 驱动导出完整流程"""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_dir = os.path.join(tmpdir, "vault")
        docs_dir = os.path.join(vault_dir, "guide")
        os.makedirs(docs_dir, exist_ok=True)

        with open(os.path.join(docs_dir, "start.md"), "w", encoding="utf-8") as f:
            f.write("---\ntitle: 极速开始\norder: 1\n---\n# 极速开始\n欢迎阅读单文件电子书。")

        assembler = BookAssembler(vault_dir=vault_dir)
        result_path = assembler.assemble_and_bind(
            category="guide",
            format_type="webbook",
            target_lang="zh",
            custom_title="WebBook 实战篇",
            output_dir=os.path.join(tmpdir, "dist")
        )

        assert result_path is not None
        assert result_path.endswith(".html")
        assert os.path.exists(result_path)

        with open(result_path, "r", encoding="utf-8") as rf:
            c = rf.read()
            assert "极速开始" in c
            assert "wb-layout" in c
