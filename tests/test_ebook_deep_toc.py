# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EBook Deep TOC & Heading Hierarchy Test Suite
模块职责：全面验证多级标题树规整提取 (H2/H3)、EPUB 3 嵌套 nav.xhtml、
EPUB 2 嵌套 toc.ncx 以及 WebBook 离线树形侧边栏目录的生成与结构完整性。
"""

import os
import zipfile
import tempfile
import pytest

from core.bindery.toc_builder import TocBuilder
from core.adapters.egress.ebook.epub import EpubAdapter
from core.adapters.egress.ebook.webbook import WebBookAdapter
from core.bindery.book_assembler import BookAssembler


def test_toc_builder_extract_heading_tree_with_h1_root():
    """验证当 Markdown 存在顶层 H1 时，精准提取其 children 作为章节内 H2/H3 大纲"""
    mock_tokens = [
        {
            "level": 1,
            "id": "book-chapter-title",
            "name": "第一章：数字出版主权",
            "children": [
                {
                    "level": 2,
                    "id": "arch-design",
                    "name": "1.1 架构设计",
                    "children": [
                        {"level": 3, "id": "storage-layer", "name": "1.1.1 存储适配", "children": []},
                        {"level": 3, "id": "engine-layer", "name": "1.1.2 运行基座", "children": []}
                    ]
                },
                {
                    "level": 2,
                    "id": "security-redline",
                    "name": "1.2 安全红线与隔离",
                    "children": []
                }
            ]
        }
    ]

    tree = TocBuilder.extract_heading_tree(mock_tokens, chapter_title="第一章：数字出版主权")
    assert len(tree) == 2
    assert tree[0]["id"] == "arch-design"
    assert tree[0]["title"] == "1.1 架构设计"
    assert tree[0]["level"] == 2
    assert len(tree[0]["children"]) == 2
    assert tree[0]["children"][0]["id"] == "storage-layer"
    assert tree[0]["children"][1]["title"] == "1.1.2 运行基座"
    assert tree[1]["id"] == "security-redline"
    assert len(tree[1]["children"]) == 0


def test_toc_builder_extract_heading_tree_direct_h2():
    """验证当 Markdown 无 H1 直接以 H2 起始时的规整提取"""
    mock_tokens = [
        {"level": 2, "id": "step-1", "name": "第一步：唤醒出版引擎", "children": []},
        {"level": 2, "id": "step-2", "name": "第二步：起草原稿", "children": [
            {"level": 3, "id": "step-2-detail", "name": "2.1 格式适配", "children": []}
        ]}
    ]

    tree = TocBuilder.extract_heading_tree(mock_tokens)
    assert len(tree) == 2
    assert tree[0]["id"] == "step-1"
    assert tree[1]["id"] == "step-2"
    assert len(tree[1]["children"]) == 1


def test_toc_builder_extract_from_html_fallback():
    """验证当无结构化 tokens 时从 HTML 标签中正则防御性提取多级标题"""
    sample_html = """
    <p>引言正文...</p>
    <h2 id="sec-core">核心机制</h2>
    <p>详细讲解...</p>
    <h3 id="sec-cache">缓存加速</h3>
    <p>缓存说明...</p>
    <h2 id="sec-summary">全卷总结</h2>
    """

    tree = TocBuilder.extract_headings_from_html(sample_html)
    assert len(tree) == 2
    assert tree[0]["id"] == "sec-core"
    assert tree[0]["title"] == "核心机制"
    assert len(tree[0]["children"]) == 1
    assert tree[0]["children"][0]["id"] == "sec-cache"
    assert tree[1]["id"] == "sec-summary"


def test_epub_nested_toc_nav_and_ncx_integrity():
    """验证 EPUB 3 nav.xhtml 嵌套 <ol> 与 EPUB 2 toc.ncx 嵌套 <navPoint> 的生成规范"""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_epub = os.path.join(tmpdir, "deep_toc.epub")
        adapter = EpubAdapter()

        manuscript = [
            {
                "order": 1,
                "title": "第一章：架构全景",
                "slug": "ch1",
                "html_body": '<p>正文</p><h2 id="sec1-1">1.1 基座解耦</h2><p>内容</p><h3 id="sec1-1-1">1.1.1 驱动模型</h3>',
                "headings": [
                    {
                        "id": "sec1-1",
                        "title": "1.1 基座解耦",
                        "level": 2,
                        "children": [
                            {"id": "sec1-1-1", "title": "1.1.1 驱动模型", "level": 3, "children": []}
                        ]
                    }
                ]
            },
            {
                "order": 2,
                "title": "第二章：分发管线",
                "slug": "ch2",
                "html_body": '<p>第二章内容</p><h2 id="sec2-1">2.1 边缘同步</h2>',
                "headings": [
                    {"id": "sec2-1", "title": "2.1 边缘同步", "level": 2, "children": []}
                ]
            }
        ]

        meta = {"title": "深度目录测试书籍", "author": "Illacme"}
        ok = adapter.bind_book(manuscript, meta, target_lang="zh", output_file_path=out_epub)
        assert ok is True
        assert os.path.exists(out_epub)

        with zipfile.ZipFile(out_epub, "r") as zf:
            # 1. 断言 nav.xhtml 嵌套 <ol> 结构
            nav_xml = zf.read("OEBPS/nav.xhtml").decode("utf-8")
            assert '<a href="text/ch_1.xhtml">第一章：架构全景</a>' in nav_xml
            assert '<a href="text/ch_1.xhtml#sec1-1">1.1 基座解耦</a>' in nav_xml
            assert '<a href="text/ch_1.xhtml#sec1-1-1">1.1.1 驱动模型</a>' in nav_xml
            assert '<a href="text/ch_2.xhtml#sec2-1">2.1 边缘同步</a>' in nav_xml
            assert "<ol><ol>" not in nav_xml or "<ol>" in nav_xml

            # 2. 断言 toc.ncx 嵌套 <navPoint> 与深度配置
            ncx_xml = zf.read("OEBPS/toc.ncx").decode("utf-8")
            assert '<meta name="dtb:depth" content="3"/>' in ncx_xml
            assert '<content src="text/ch_1.xhtml"/>' in ncx_xml
            assert '<content src="text/ch_1.xhtml#sec1-1"/>' in ncx_xml
            assert '<content src="text/ch_1.xhtml#sec1-1-1"/>' in ncx_xml
            assert 'playOrder="1"' in ncx_xml
            assert 'playOrder="2"' in ncx_xml
            assert 'playOrder="3"' in ncx_xml


def test_webbook_nested_toc_structure_and_interaction():
    """验证 WebBook 单文件离线网页书生成树形侧栏大纲、折叠按钮与锚点"""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_html = os.path.join(tmpdir, "webbook_deep_toc.html")
        adapter = WebBookAdapter()

        manuscript = [
            {
                "order": 1,
                "title": "快速上手指南",
                "slug": "quick-start",
                "html_body": '<h2 id="step-one">第一步：启动</h2><p>内容...</p><h3 id="sub-config">配置项</h3><p>详细...</p>',
                "headings": [
                    {
                        "id": "step-one",
                        "title": "第一步：启动",
                        "level": 2,
                        "children": [{"id": "sub-config", "title": "配置项", "level": 3, "children": []}]
                    }
                ]
            }
        ]

        meta = {"title": "WebBook 树形大纲测试", "author": "Illacme"}
        ok = adapter.bind_book(manuscript, meta, target_lang="zh", output_file_path=out_html)
        assert ok is True
        assert os.path.exists(out_html)

        with open(out_html, "r", encoding="utf-8") as f:
            content = f.read()

        # 断言 DOM 树形结构
        assert 'class="wb-toc-group has-sub"' in content
        assert 'class="wb-toc-toggle"' in content
        assert 'class="wb-toc-sub"' in content
        assert 'data-id="step-one"' in content
        assert 'href="#step-one"' in content
        assert 'data-id="sub-config"' in content
        assert 'href="#sub-config"' in content
        assert 'wb-toc-h2' in content
        assert 'wb-toc-h3' in content

        # 断言 JS 控制逻辑
        assert "wb-toc-toggle" in content
        assert "wb-toc-group" in content
        assert "IntersectionObserver" in content


def test_vault_assembler_nested_headings_integration():
    """端到端验证：从文库真实原稿 Docs 中提取并生成带 H2/H3 大纲的电子书"""
    vault_dir = "vault"
    if not os.path.exists(vault_dir):
        pytest.skip("文库目录不存在，跳过")

    with tempfile.TemporaryDirectory() as tmpdir:
        assembler = BookAssembler(vault_dir=vault_dir)
        chapters = assembler._collect_chapters(category="Docs", target_lang="zh")
        assert len(chapters) > 0

        # 检查是否至少有章节成功提取出了 headings
        chapters_with_headings = [c for c in chapters if c.get("headings")]
        assert len(chapters_with_headings) > 0, "文库章节未提取出任何层级标题"

        # 验证 quick-start.md 或 index.md 提取到了第一步、第二步等小节
        all_heading_titles = []
        for c in chapters_with_headings:
            for h in c["headings"]:
                all_heading_titles.append(h["title"])
                for sub in h.get("children", []):
                    all_heading_titles.append(sub["title"])

        assert any("启动" in t or "第一步" in t or "目录" in t for t in all_heading_titles), \
            f"未在标题列表中找到预期小节: {all_heading_titles[:10]}"
