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
    <item id="ch1" href="text/ch1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="ch1"/>
  </spine>
</package>"""
        )
        z.writestr("OEBPS/images/cover.png", b"\x89PNG\r\n\x1a\n\x00mock_image_bytes")
        z.writestr(
            "OEBPS/text/ch1.xhtml",
            """<!DOCTYPE html><html><head><title>第一章 觉醒</title></head><body>
<div class="chap"><img src="../images/cover.png" alt="Cover"/><h1>第一章 觉醒</h1><p>星辰在大地之上闪烁，微型装订器启动中。</p></div>
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
    # 验证目录项生成
    assert '📖 第一章 觉醒' in html_output
    # 验证交互脚本注入
    assert 'er-toggle-sidebar' in html_output


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
