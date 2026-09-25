# -*- coding: utf-8 -*-
"""
📚 [V126.0] Test Suite for EPUB Embedded Web Reader
测试范围：EPUB 容器与 OPF 解析、章节提取、图片 Base64 嵌入及 /api/bindery/view 在线阅读全流程。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import zipfile
import pytest
from fastapi.testclient import TestClient

from services.api.server import app
from services.api.routes.system import verify_token
from core.adapters.egress.ebook.epub_reader import render_epub_reader_html


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


@pytest.fixture
def mock_epub_file(tmp_path):
    """动态构建符合 EPUB 3.0 标准的测试压缩包"""
    epub_file = tmp_path / "test_fiction_novel.epub"
    with zipfile.ZipFile(epub_file, "w") as z:
        z.writestr("mimetype", "application/epub+zip")
        z.writestr(
            "META-INF/container.xml",
            '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
        )
        z.writestr(
            "OEBPS/content.opf",
            """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>微型幻想典籍</dc:title>
    <dc:creator>测试创作者</dc:creator>
    <dc:description>EPUB 原生翻阅测试手稿</dc:description>
  </metadata>
  <manifest>
    <item id="cover-img" href="images/cover.png" media-type="image/png" properties="cover-image"/>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ch1" href="text/ch1.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch2" href="text/ch2.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="ch1"/>
    <itemref idref="ch2"/>
  </spine>
</package>"""
        )
        z.writestr("OEBPS/images/cover.png", b"\x89PNG\r\n\x1a\n\x00mock_image_bytes")
        z.writestr(
            "OEBPS/nav.xhtml",
            """<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>导航目录</title></head>
<body>
<nav epub:type="toc">
  <h1>目录</h1>
  <ol>
    <li><a href="text/ch1.xhtml">第一章 觉醒</a>
      <ol>
        <li><a href="text/ch1.xhtml#sec-1">1.1 星辰之光</a></li>
        <li><a href="text/ch1.xhtml#sec-2">1.2 虚空行者</a></li>
      </ol>
    </li>
    <li><a href="text/ch2.xhtml">第二章 远征</a></li>
  </ol>
</nav>
</body></html>"""
        )
        z.writestr(
            "OEBPS/text/ch1.xhtml",
            """<!DOCTYPE html><html><head><title>第一章 觉醒</title></head><body>
<div class="chap"><img src="../images/cover.png" alt="Cover"/><h1>第一章 觉醒</h1><p>星辰在大地之上闪烁，微型装订器启动中。<a href="text/ch2.xhtml">前往下一章</a></p><h2 id="sec-1">1.1 星辰之光</h2><p>第一节详情</p></div>
</body></html>"""
        )
        z.writestr(
            "OEBPS/text/ch2.xhtml",
            """<!DOCTYPE html><html><head><title>第二章 远征</title></head><body>
<div class="chap"><h1>第二章 远征</h1><p>穿越光年的跋涉。<a href="ch1.xhtml#sec-1">返回第一节</a></p></div>
</body></html>"""
        )
    return str(epub_file)


def test_render_epub_reader_html_core(mock_epub_file):
    """测试 EPUB 解析引擎直接输出完整的自包含阅读器 HTML"""
    html_output = render_epub_reader_html(mock_epub_file)
    assert "<title>微型幻想典籍 - EPUB 在线翻阅</title>" in html_output
    assert "er-chapter-card" in html_output
    assert "第一章 觉醒" in html_output
    assert "星辰在大地之上闪烁" in html_output
    # 验证内部相对图片路径已成功内联转换为 Base64
    assert 'data:image/png;base64,' in html_output
    assert "../images/cover.png" not in html_output
    # 验证多级目录结构解析与生成
    assert 'class="er-toc-tree"' in html_output
    assert '1.1 星辰之光' in html_output
    assert '1.2 虚空行者' in html_output
    # 验证正文内部跨章节/节超链接已重写为页内锚点，不再是相对路径
    assert 'href="#er-doc-ch2_xhtml"' in html_output
    assert 'er-toggle-sidebar' in html_output
    # 验证翻页仿真模式与双模切换组件
    assert 'id="er-mode-toggle"' in html_output
    assert 'id="er-spread-toggle"' in html_output
    assert 'id="er-font-family"' in html_output
    assert 'id="er-fullscreen"' in html_output
    assert 'id="er-viewport"' in html_output
    assert 'id="er-page-prev"' in html_output
    assert 'id="er-page-next"' in html_output
    assert 'id="er-paginated-footer"' in html_output
    assert 'data-read-mode="paginated"' in html_output
    assert 'data-spread="auto"' in html_output
    assert 'data-font="sans"' in html_output

    # 验证划词高亮、侧边栏双 Tab、笔记面板与金句卡片
    assert 'id="er-floating-bar"' in html_output
    assert 'id="er-stab-toc"' in html_output
    assert 'id="er-stab-notes"' in html_output
    assert 'id="er-pane-notes"' in html_output
    assert 'id="er-export-notes-btn"' in html_output
    assert 'id="er-card-modal"' in html_output
    assert 'id="er-note-modal"' in html_output
    assert 'er-quote-card' in html_output

    # 验证全书全文检索与关键词穿透聚焦组件
    assert 'id="er-stab-search"' in html_output
    assert 'id="er-pane-search"' in html_output
    assert 'id="er-search-input"' in html_output
    assert 'id="er-search-results"' in html_output
    assert 'er-search-box' in html_output




def test_api_bindery_view_epub(client, mock_epub_file):
    """测试通过 /api/bindery/view 路由发起在线翻阅请求"""
    books_dir = os.path.abspath("dist/books")
    os.makedirs(books_dir, exist_ok=True)
    dst_name = "test_auto_read_sample.epub"
    dst_path = os.path.join(books_dir, dst_name)

    import shutil
    shutil.copyfile(mock_epub_file, dst_path)

    try:
        # 1. 验证书架扫描接口能够为 EPUB 提供 preview_url
        shelf_res = client.get("/api/bindery/shelf")
        assert shelf_res.status_code == 200
        shelf_data = shelf_res.json()
        assert shelf_data.get("success") is True
        epub_item = next((b for b in shelf_data.get("books", []) if b["filename"] == dst_name), None)
        assert epub_item is not None
        assert epub_item["format"] == "epub"
        assert f"/api/bindery/view?file={dst_name}" in epub_item["preview_url"]

        # 2. 验证 /api/bindery/view?file=... 正确以 HTML 视界响应
        view_res = client.get(f"/api/bindery/view?file={dst_name}")
        assert view_res.status_code == 200
        assert "text/html" in view_res.headers.get("content-type", "")
        assert "微型幻想典籍" in view_res.text
        assert "data:image/png;base64," in view_res.text

        # 3. 验证未找到文件时的安全 404
        assert client.get("/api/bindery/view?file=ghost_file.epub").status_code == 404
    finally:
        if os.path.exists(dst_path):
            os.remove(dst_path)
