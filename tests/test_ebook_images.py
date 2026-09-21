# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EBook Images & Offline Assets Test Suite
模块职责：验证 Obsidian ![[...]] 图像语法转译、本地多层级物理寻址探测、HTML 路径自愈及 EPUB 离线资源打包封包。
"""

import os
import zipfile
import tempfile
import xml.etree.ElementTree as ET
import pytest

from core.bindery.image_packager import ImagePackager
from core.bindery.book_assembler import BookAssembler
from core.adapters.egress.ebook.epub import EpubAdapter


def test_obsidian_image_syntax_healing():
    """验证 Obsidian 图片语法转译为标准图像标签与尺寸约束"""
    # 1. 基础图片转译
    md_1 = "正文前段\n\n![[screenshot.png]]\n\n正文后段"
    healed_1 = ImagePackager.heal_obsidian_embedded_images(md_1)
    assert '<img src="screenshot.png" alt="screenshot" />' in healed_1

    # 2. 带宽度限制转译
    md_2 = "![[diagram.jpg|500]]"
    healed_2 = ImagePackager.heal_obsidian_embedded_images(md_2)
    assert '<img src="diagram.jpg" alt="diagram" style="max-width: 500px;" />' in healed_2

    # 3. 带宽高限制转译 (300x200 提取宽度)
    md_3 = "![[logo.svg|300x200]]"
    healed_3 = ImagePackager.heal_obsidian_embedded_images(md_3)
    assert '<img src="logo.svg" alt="logo" style="max-width: 300px;" />' in healed_3

    # 4. 非图片双链不受影响 (不被转为 img)
    md_4 = "[[some-other-document]]"
    healed_4 = ImagePackager.heal_obsidian_embedded_images(md_4)
    assert healed_4 == md_4


def test_local_image_multi_level_location():
    """验证多层级本地物理图片寻址算法"""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_dir = os.path.join(tmpdir, "vault")
        os.makedirs(os.path.join(vault_dir, "docs", "assets"), exist_ok=True)
        os.makedirs(os.path.join(vault_dir, "attachments"), exist_ok=True)

        doc_path = os.path.join(vault_dir, "docs", "index.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("# Doc")

        # 在 doc 级 assets 放置图片 1
        img1_path = os.path.join(vault_dir, "docs", "assets", "fig1.png")
        with open(img1_path, "wb") as f:
            f.write(b"PNG1")

        # 在文库全局 attachments 放置图片 2
        img2_path = os.path.join(vault_dir, "attachments", "fig2.jpg")
        with open(img2_path, "wb") as f:
            f.write(b"JPG2")

        # 寻址测试 1：通过相对路径引用 assets/fig1.png
        loc1 = ImagePackager.locate_local_image("assets/fig1.png", doc_path, vault_dir)
        assert loc1 is not None
        assert os.path.samefile(loc1, img1_path)

        # 寻址测试 2：仅凭纯文件名 fig1.png 自动探测同级 assets
        loc1_auto = ImagePackager.locate_local_image("fig1.png", doc_path, vault_dir)
        assert loc1_auto is not None
        assert os.path.samefile(loc1_auto, img1_path)

        # 寻址测试 3：仅凭文件名 fig2.jpg 自动探测全局 attachments
        loc2 = ImagePackager.locate_local_image("fig2.jpg", doc_path, vault_dir)
        assert loc2 is not None
        assert os.path.samefile(loc2, img2_path)

        # 寻址测试 4：网络图片与非法路径安全返回 None
        assert ImagePackager.locate_local_image("https://example.com/logo.png", doc_path, vault_dir) is None
        assert ImagePackager.locate_local_image("non_existent_img.png", doc_path, vault_dir) is None


def test_html_extract_and_heal_images():
    """验证 HTML 中图片的抽取、路径重写与资产收集"""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_dir = os.path.join(tmpdir, "vault")
        doc_dir = os.path.join(vault_dir, "guide")
        os.makedirs(doc_dir, exist_ok=True)

        doc_path = os.path.join(doc_dir, "hello.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("guide")

        img_file = os.path.join(doc_dir, "architecture.png")
        with open(img_file, "wb") as f:
            f.write(b"PNG_DATA")

        html_in = f'<p>架构设计图如下：</p><p><img src="architecture.png" alt="Arch" /></p>'
        healed_html, assets = ImagePackager.extract_and_heal_images(html_in, doc_path, vault_dir)

        assert len(assets) == 1
        asset = assets[0]
        assert asset["mime_type"] == "image/png"
        assert asset["target_name"].endswith("_architecture.png")
        assert f'src="../images/{asset["target_name"]}"' in healed_html


def test_end_to_end_epub_offline_image_packaging():
    """验证全卷装订时端到端本地插图打包入 EPUB 并在阅读器中路径自愈"""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_dir = os.path.join(tmpdir, "vault")
        docs_dir = os.path.join(vault_dir, "docs")
        assets_dir = os.path.join(docs_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        # 创建两张物理测试图片
        img1_file = os.path.join(assets_dir, "diagram_1.png")
        with open(img1_file, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\nMockImageData1")

        img2_file = os.path.join(assets_dir, "photo_2.jpg")
        with open(img2_file, "wb") as f:
            f.write(b"\xFF\xD8\xFF\xE0MockImageData2")

        # 创建包含两种图片语法的文档
        doc_1 = os.path.join(docs_dir, "01-start.md")
        with open(doc_1, "w", encoding="utf-8") as f:
            f.write("""---
title: 快速入门
order: 1
---

# 极速上手

系统架构图展示如下：

![[diagram_1.png|400]]

标准 Markdown 图片语法：

![实拍照片](assets/photo_2.jpg)
""")

        out_epub = os.path.join(tmpdir, "output.epub")
        assembler = BookAssembler(vault_dir=vault_dir)

        result_path = assembler.assemble_and_bind(
            category="docs",
            format_type="epub",
            target_lang="zh",
            custom_title="图文电子书实战典籍",
            custom_author="Illacme 架构组",
            cover_mode="none",
            output_dir=os.path.join(tmpdir, "dist")
        )

        assert result_path is not None
        assert os.path.exists(result_path)

        # 解包并深入断言 EPUB 容器与内部结构
        with zipfile.ZipFile(result_path, "r") as zf:
            namelist = zf.namelist()

            # 1. 断言 OEBPS/images 目录下存在两张物理打包图片
            image_files = [f for f in namelist if f.startswith("OEBPS/images/")]
            assert len(image_files) == 2
            for img_name in image_files:
                assert img_name.endswith(".png") or img_name.endswith(".jpg")
                # 验证图片内容非空且未损坏
                data = zf.read(img_name)
                assert len(data) > 0

            # 2. 断言 content.opf 中注册了每张图片的 manifest item 与 MIME
            opf_content = zf.read("OEBPS/content.opf").decode("utf-8")
            assert 'media-type="image/png"' in opf_content
            assert 'media-type="image/jpeg"' in opf_content
            for img_name in image_files:
                rel_href = img_name.replace("OEBPS/", "")
                assert f'href="{rel_href}"' in opf_content

            # 3. 断言章节 XHTML 中的 <img> 标签 src 均已自愈为 ../images/xxx
            ch1_xhtml = zf.read("OEBPS/text/ch_1.xhtml").decode("utf-8")
            assert 'src="../images/' in ch1_xhtml
            assert 'diagram_1' in ch1_xhtml
            assert 'photo_2' in ch1_xhtml
            assert 'style="max-width: 400px;"' in ch1_xhtml

            # 4. XML 严格解析断言：确保 XHTML 格式合法无残缺标签
            root = ET.fromstring(ch1_xhtml)
            assert root.tag.endswith("html")
