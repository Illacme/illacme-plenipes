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


def test_webbook_mobile_immersive_interactions():
    """验证移动端 WebBook 沉浸式阅读交互体验：手势翻页、遮罩抽屉、章节卡片与安全区适配"""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "mobile_test.html")
        adapter = WebBookAdapter()
        manuscript = [
            {"order": 1, "title": "第一节：移动端交互设计", "html_body": "<p>移动端手势流畅度优化。</p>"},
            {"order": 2, "title": "第二节：沉浸式触控翻页", "html_body": "<p>左右滑动手势翻章。</p>"},
            {"order": 3, "title": "第三节：全屏无扰阅读", "html_body": "<p>目录自愈收拢遮罩体验。</p>"}
        ]
        meta = {"title": "移动端交互手册", "author": "Illacme 移动端体验组"}

        success = adapter.bind_book(
            manuscript_tree=manuscript,
            book_metadata=meta,
            target_lang="zh",
            output_file_path=out_file
        )
        assert success is True
        assert os.path.exists(out_file)

        with open(out_file, "r", encoding="utf-8") as f:
            html = f.read()

        # 1. 移动端毛玻璃半透明遮罩与底部手势胶囊 DOM 断言
        assert 'id="wb-backdrop"' in html
        assert 'class="wb-backdrop"' in html
        assert 'id="wb-toast-capsule"' in html
        assert 'class="wb-toast-capsule"' in html

        # 2. 章节末尾上一节 / 下一节宽幅磁吸导航卡片断言
        assert 'class="wb-chapter-footer"' in html
        assert 'class="wb-nav-card prev"' in html
        assert 'class="wb-nav-card next"' in html
        assert 'href="#ch_1"' in html
        assert 'href="#ch_2"' in html
        assert 'href="#ch_3"' in html
        assert "第一节：移动端交互设计" in html
        assert "第二节：沉浸式触控翻页" in html
        assert "第三节：全屏无扰阅读" in html

        # 3. 触屏手势翻页与遮罩自愈脚本契约断言
        assert "touchstart" in html
        assert "touchend" in html
        assert "wb-toast-capsule" in html
        assert "bDrop.classList.remove('active')" in html
        assert "closeSidebar()" in html

        # 4. 移动端响应式样式与 iPhone 安全区契约断言
        assert "@media (max-width: 900px)" in html
        assert "#wb-print-btn { display: none !important; }" in html
        assert "safe-area-inset-bottom" in html

        # 5. 移动端章节导航防挤压与全宽磁吸契约断言
        assert ".wb-ch-nav { flex-direction: column;" in html
        assert ".wb-nav-card { width: 100%; box-sizing: border-box; }" in html
        assert ".wb-nav-card.next { margin-left: 0; text-align: right; }" in html

        # 6. 移动端目录切换按钮触控优化与抽屉绝对层级契约断言
        assert "#wb-toggle-sidebar { min-width: 38px; min-height: 38px;" in html
        assert "touch-action: manipulation" in html
        assert ".wb-backdrop { z-index: 950 !important; }" in html
        assert "z-index: 960 !important;" in html
        assert "onToggleTrigger" in html


def test_webbook_multi_viewport_overflow_prevention():
    """验证 WebBook 全局及多分辨率下无横向溢出规则契约（手机/平板/桌面三端防溢出）"""
    from core.adapters.egress.ebook.webbook_css import get_webbook_css
    css = get_webbook_css()

    # 1. 全局视口防溢出断言
    assert "html, body { overflow-x: hidden; max-width: 100vw; }" in css
    assert "width: 100%; max-width: 100vw; overflow-x: hidden;" in css

    # 2. 桌面/平板断点计算主屏宽度防右侧挤压溢出
    assert "min-width: 0;" in css
    assert "width: calc(100% - 290px);" in css
    assert "max-width: calc(100% - 290px);" in css

    # 3. 模板 Hero/网格容器弹性收缩约束
    assert ".home-hero-container, [class*=\"hero\"] { max-width: 100% !important;" in css
    assert "box-sizing: border-box !important;" in css

    # 4. 移动端媒体查询覆写
    assert "grid-template-columns: 1fr !important;" in css
    assert ".wb-main { margin-left: 0 !important; width: 100% !important; max-width: 100% !important;" in css


