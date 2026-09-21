# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EBook Bindery Test Suite
模块职责：验证电子书出口插件体系、原生 EPUB 3.0 装订驱动与全卷编排器的契约与输出完整性。
"""

import os
import zipfile
import tempfile
import pytest

from core.adapters.egress.ebook import EBookRegistry, BaseEBookAdapter
from core.adapters.egress.ebook.epub import EpubAdapter
from core.bindery.book_assembler import BookAssembler


def test_ebook_registry_discovery():
    """验证电子书注册中心能够自发现并加载内置驱动"""
    all_names = EBookRegistry.get_all_names()
    assert "epub" in all_names
    adapter_cls = EBookRegistry.get_adapter("epub")
    assert adapter_cls is EpubAdapter
    assert issubclass(adapter_cls, BaseEBookAdapter)
    assert adapter_cls.OUTPUT_EXTENSION == ".epub"


def test_epub_adapter_standard_container_integrity():
    """验证生成的 EPUB 符合 W3C / IDPF 规范容器结构"""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "test_book.epub")
        adapter = EpubAdapter()

        manuscript = [
            {"order": 1, "title": "第一章：数字主权", "slug": "chapter-1", "html_body": "<p>这是第一章正文，探讨出版主权。</p>"},
            {"order": 2, "title": "第二章：全网分发", "slug": "chapter-2", "html_body": "<p>这是第二章正文，探讨多渠道发布。</p>"},
        ]
        meta = {
            "title": "数字出版主权实践指南",
            "author": "Illacme 架构团队",
            "publisher": "Illacme Plenipes Press",
            "description": "一本关于主权化数字出版的测试书籍。",
            "date": "2026-09-21"
        }

        success = adapter.bind_book(
            manuscript_tree=manuscript,
            book_metadata=meta,
            target_lang="zh",
            output_file_path=out_file
        )
        assert success is True
        assert os.path.exists(out_file)

        # 解包物理断言
        with zipfile.ZipFile(out_file, "r") as zf:
            namelist = zf.namelist()

            # 1. 规范断言：首文件必须是 mimetype 且未压缩
            first_info = zf.infolist()[0]
            assert first_info.filename == "mimetype"
            assert first_info.compress_type == zipfile.ZIP_STORED
            assert zf.read("mimetype").decode("utf-8").strip() == "application/epub+zip"

            # 2. 规范断言：container.xml
            assert "META-INF/container.xml" in namelist
            container_str = zf.read("META-INF/container.xml").decode("utf-8")
            assert "OEBPS/content.opf" in container_str

            # 3. 规范断言：content.opf 清单与元数据
            assert "OEBPS/content.opf" in namelist
            opf_str = zf.read("OEBPS/content.opf").decode("utf-8")
            assert "数字出版主权实践指南" in opf_str
            assert "Illacme 架构团队" in opf_str
            assert 'id="ch_1"' in opf_str
            assert 'id="ch_2"' in opf_str

            # 4. 规范断言：双目录 (nav.xhtml + toc.ncx)
            assert "OEBPS/nav.xhtml" in namelist
            assert "OEBPS/toc.ncx" in namelist
            nav_str = zf.read("OEBPS/nav.xhtml").decode("utf-8")
            assert "第一章：数字主权" in nav_str

            # 5. 规范断言：样式与章节 XHTML
            assert "OEBPS/styles/epub.css" in namelist
            assert "OEBPS/text/ch_1.xhtml" in namelist
            assert "OEBPS/text/ch_2.xhtml" in namelist
            ch1_str = zf.read("OEBPS/text/ch_1.xhtml").decode("utf-8")
            assert "这是第一章正文" in ch1_str


def test_epub_adapter_with_cover_image():
    """验证携带封面图片时封面 XHTML 与清单属性生成正确"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cover_path = os.path.join(tmpdir, "mock_cover.jpg")
        with open(cover_path, "wb") as f:
            f.write(b"\xFF\xD8\xFF\xE0MockJPEGBinary")

        out_file = os.path.join(tmpdir, "covered_book.epub")
        adapter = EpubAdapter()

        success = adapter.bind_book(
            manuscript_tree=[{"order": 1, "title": "引言", "slug": "intro", "html_body": "<p>Hello</p>"}],
            book_metadata={"title": "带封面书籍"},
            cover_image_path=cover_path,
            target_lang="en",
            output_file_path=out_file
        )
        assert success is True

        with zipfile.ZipFile(out_file, "r") as zf:
            namelist = zf.namelist()
            assert "OEBPS/images/cover.jpg" in namelist
            assert "OEBPS/text/cover.xhtml" in namelist
            opf_str = zf.read("OEBPS/content.opf").decode("utf-8")
            assert 'properties="cover-image"' in opf_str


def test_book_assembler_vault_end_to_end():
    """验证全卷编排器从真实文库聚合章节并导出完整电子书"""
    vault_dir = "vault"
    if not os.path.exists(vault_dir):
        pytest.skip("文库目录不存在，跳过端到端测试")

    with tempfile.TemporaryDirectory() as tmpdir:
        assembler = BookAssembler(vault_dir=vault_dir)

        # 1. 导出 Docs 栏目中文版
        zh_book = assembler.assemble_and_bind(
            category="Docs",
            format_type="epub",
            target_lang="zh",
            custom_title="Illacme 官方技术手册",
            output_dir=tmpdir
        )
        assert zh_book is not None
        assert os.path.exists(zh_book)
        assert zh_book.endswith(".epub")

        # 验证生成的章节数量与内容
        with zipfile.ZipFile(zh_book, "r") as zf:
            namelist = zf.namelist()
            chapter_files = [n for n in namelist if n.startswith("OEBPS/text/ch_")]
            assert len(chapter_files) >= 5, f"章节数量过少: {len(chapter_files)}"

        # 2. 导出 Docs 栏目英文版 (利用已有 en 翻译)
        en_book = assembler.assemble_and_bind(
            category="Docs",
            format_type="epub",
            target_lang="en",
            custom_title="Illacme Technical Manual",
            output_dir=tmpdir
        )
        assert en_book is not None
        assert os.path.exists(en_book)


def test_epub_colophon_injection():
    """验证电子书装订时自动注入末尾版权页 (Colophon) 与物权指纹"""
    from core.adapters.egress.ebook import ColophonBuilder

    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "colophon_test.epub")
        adapter = EpubAdapter()

        manuscripts = [
            {
                "order": 1,
                "title": "第 1 章 架构总览",
                "slug": "ch1",
                "html_body": "<p>这里是架构解析，包含 100 个核心要点与架构设计图。</p>"
            },
            {
                "order": 2,
                "title": "第 2 章 实战案例",
                "slug": "ch2",
                "html_body": "<p>Deep learning and sovereign publishing workflow.</p>"
            }
        ]

        book_meta = {
            "title": "版记验证典籍",
            "author": "架构委员会",
            "publisher": "Illacme Press",
            "license": "CC BY-NC-SA 4.0 国际知识共享协议"
        }

        success = adapter.bind_book(
            manuscript_tree=manuscripts,
            book_metadata=book_meta,
            target_lang="zh",
            output_file_path=out_file
        )
        assert success is True

        with zipfile.ZipFile(out_file, "r") as zf:
            namelist = zf.namelist()
            # 1. 验证版记独立 XHTML 落盘
            assert "OEBPS/text/colophon.xhtml" in namelist

            # 2. 验证版记内容准确包含各项元数据
            colophon_html = zf.read("OEBPS/text/colophon.xhtml").decode("utf-8")
            assert "出版物版记 · COLOPHON" in colophon_html
            assert "版记验证典籍" in colophon_html
            assert "架构委员会" in colophon_html
            assert "CC BY-NC-SA 4.0" in colophon_html
            assert "篇章节" in colophon_html

            # 3. 验证 nav.xhtml 与 toc.ncx 均包含版记导航
            nav_html = zf.read("OEBPS/nav.xhtml").decode("utf-8")
            assert "text/colophon.xhtml" in nav_html
            assert "版记 · Colophon" in nav_html

            ncx_xml = zf.read("OEBPS/toc.ncx").decode("utf-8")
            assert "text/colophon.xhtml" in ncx_xml
            assert "版记 · Colophon" in ncx_xml


def test_wikilinks_and_anchor_healing():
    """验证 Obsidian 双链内链与章节锚点的全场景自愈重写"""
    route_map = {
        "chapter-1": "ch_1",
        "chapter-2": "ch_2",
        "核心架构篇": "ch_2",
        "deep-guide": "ch_3"
    }

    # 1. 跨章节基础跳转（自动追加 #ch_2 锚点以兼容 Apple Books 等阅读器翻章）
    t1 = BookAssembler._rewrite_wikilinks_to_chapters("[[chapter-2]]", route_map, curr_ch_id="ch_1")
    assert t1 == "[chapter-2](ch_2.xhtml#ch_2)"

    # 2. 跨章节带别名
    t2 = BookAssembler._rewrite_wikilinks_to_chapters("[[chapter-2|第二章 实战]]", route_map, curr_ch_id="ch_1")
    assert t2 == "[第二章 实战](ch_2.xhtml#ch_2)"

    # 2.1 容错匹配：带 Emoji 的双链精准命中章节
    t2_emoji = BookAssembler._rewrite_wikilinks_to_chapters("[[⚡ 核心架构篇]]", route_map, curr_ch_id="ch_1")
    assert t2_emoji == "[⚡ 核心架构篇](ch_2.xhtml#ch_2)"

    # 3. 跨章节带锚点跳转
    t3 = BookAssembler._rewrite_wikilinks_to_chapters("[[chapter-2#核心架构]]", route_map, curr_ch_id="ch_1")
    assert t3 == "[chapter-2 · 核心架构](ch_2.xhtml#核心架构)"

    # 4. 跨章节带别名与锚点
    t4 = BookAssembler._rewrite_wikilinks_to_chapters("[[chapter-2#核心架构|查看架构图]]", route_map, curr_ch_id="ch_1")
    assert t4 == "[查看架构图](ch_2.xhtml#核心架构)"

    # 5. 基于 Frontmatter 中文标题匹配跨章节锚点
    t5 = BookAssembler._rewrite_wikilinks_to_chapters("[[核心架构篇#2. 原生主权|主权机制]]", route_map, curr_ch_id="ch_1")
    assert t5 == "[主权机制](ch_2.xhtml#2-原生主权)"

    # 6. 本章内部小节锚点
    t6 = BookAssembler._rewrite_wikilinks_to_chapters("[[#本章小结]]", route_map, curr_ch_id="ch_1")
    assert t6 == "[本章小结](#本章小结)"

    t7 = BookAssembler._rewrite_wikilinks_to_chapters("[[#本章小结|快速回顾]]", route_map, curr_ch_id="ch_1")
    assert t7 == "[快速回顾](#本章小结)"

    # 7. 当前章节自指跨链自动转为页内锚点
    t8 = BookAssembler._rewrite_wikilinks_to_chapters("[[chapter-1#引言背景|背景说明]]", route_map, curr_ch_id="ch_1")
    assert t8 == "[背景说明](#引言背景)"

    # 8. 外部不存在的文档优雅降级，防止死链
    t9 = BookAssembler._rewrite_wikilinks_to_chapters("[[NonExistentDoc|暂未公开文稿]]", route_map, curr_ch_id="ch_1")
    assert t9 == "暂未公开文稿"

    # 9. 端到端 Markdown 编译断言
    import markdown
    from markdown.extensions.toc import slugify_unicode
    md_converter = markdown.Markdown(
        extensions=['extra', 'codehilite', 'tables', 'toc'],
        extension_configs={'toc': {'slugify': slugify_unicode}}
    )
    test_md = """
# 第一章 引言

参考 [[chapter-2#2. 原生主权|第二章主权架构]]，更多请参见 [[#本章小结|文末总结]]。

## 本章小结
这里是引言小结。
"""
    healed = BookAssembler._rewrite_wikilinks_to_chapters(test_md, route_map, curr_ch_id="ch_1")
    html = md_converter.convert(healed)
    assert '<a href="ch_2.xhtml#2-原生主权">第二章主权架构</a>' in html
    assert '<a href="#本章小结">文末总结</a>' in html

    # 10. 原生 HTML 标签与静态相对路径自愈断言 (如首页按钮 ./docs/quick-start.html)
    raw_btn_html = '<div class="btn-group"><a href="./docs/chapter-2.html" class="theme-btn"><span>⚡ 5 分钟上手</span></a></div>'
    healed_btn = BookAssembler._heal_html_hrefs(raw_btn_html, route_map, curr_ch_id="ch_1")
    assert 'href="ch_2.xhtml#ch_2"' in healed_btn
    assert 'class="theme-btn"' in healed_btn
