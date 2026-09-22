# -*- coding: utf-8 -*-
"""
📚 [V125.0] Test Suite for Gov Bindery & EBook Export APIs
测试范围：装订范围勘测、合卷编排生成、产物落盘与安全防越权下载。
"""

import os
import shutil
import pytest
from fastapi.testclient import TestClient

from services.api.server import app
from services.api.routes.system import verify_token


@pytest.fixture(scope="module")
def client():
    # 注入依赖重载以隔离其他测试设置的 API Token 保护干扰
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


@pytest.fixture(scope="module")
def setup_mock_vault(tmp_path_factory):
    """构建临时文库沙箱以供测试合卷装订"""
    base_dir = tmp_path_factory.mktemp("bindery_test_vault")
    docs_dir = base_dir / "Docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # 写入两篇测试手稿
    (docs_dir / "01_intro.md").write_text(
        "---\ntitle: 系统引言\norder: 1\n---\n# 系统引言\n这是第一章内容，包含 [[02_guide|进阶指南]] 的双链引用。\n",
        encoding="utf-8"
    )
    (docs_dir / "02_guide.md").write_text(
        "---\ntitle: 进阶指南\norder: 2\n---\n# 进阶指南\n这是第二章内容，回跳到 [[01_intro|引言]]。\n",
        encoding="utf-8"
    )
    return str(base_dir)


def test_bindery_scopes_api(client):
    """测试获取装订范围与元数据"""
    res = client.get("/api/bindery/scopes")
    assert res.status_code == 200
    data = res.json()
    assert data.get("success") is True
    assert "categories" in data
    assert any(c["id"] == "all" for c in data["categories"])
    assert "formats" in data
    assert any(f["id"] == "epub" for f in data["formats"])


def test_bindery_build_and_download_flow(client, setup_mock_vault, monkeypatch):
    """测试电子书合卷装订及后续流式二进制下载全流程"""
    from core.runtime.engine_singleton import get_global_engine
    engine = get_global_engine()
    
    # 将文库根目录临时指向沙箱目录
    if engine:
        monkeypatch.setattr(engine, "vault_root", setup_mock_vault)

    out_books_dir = os.path.abspath("dist/books")
    os.makedirs(out_books_dir, exist_ok=True)

    payload = {
        "format": "epub",
        "scope": "Docs",
        "lang": "zh",
        "title": "单元测试专属出版物",
        "author": "Test Author",
        "output_dir": "dist/books"
    }

    res = client.post("/api/bindery/build", json=payload)
    assert res.status_code == 200
    build_data = res.json()
    assert build_data.get("success") is True
    assert build_data.get("format") == "epub"
    assert build_data.get("chapter_count") >= 2
    filename = build_data.get("filename")
    assert filename.endswith(".epub")

    # 验证物理文件真实存在
    target_path = os.path.join(out_books_dir, filename)
    assert os.path.exists(target_path)
    assert os.path.getsize(target_path) > 0

    # 测试安全下载
    dl_res = client.get(f"/api/bindery/download?file={filename}")
    assert dl_res.status_code == 200
    assert "application/epub+zip" in dl_res.headers.get("content-type", "")
    assert len(dl_res.content) == os.path.getsize(target_path)


def test_bindery_download_security_defense(client):
    """测试 SOP-04 安全红线：目录穿越 (Directory Traversal) 与越权拦截"""
    # 1. 非法包含路径斜杠
    res_slash = client.get("/api/bindery/download?file=../../etc/passwd")
    assert res_slash.status_code == 400

    # 2. 尝试伪造不存在的文件
    res_404 = client.get("/api/bindery/download?file=ghost_file_not_exist.epub")
    assert res_404.status_code == 404

    # 3. 空参数
    res_empty = client.get("/api/bindery/download?file=")
    assert res_empty.status_code == 400


def test_bindery_cover_preview_api(client):
    """测试封面实时预览接口返回 DataURL 与状态"""
    # 1. 自动/生成模式
    res = client.post("/api/bindery/cover-preview", json={
        "title": "封面测试书",
        "author": "测试作者",
        "scope": "all",
        "style": "dark_emerald",
        "lang": "zh",
        "cover_mode": "generated"
    })
    assert res.status_code == 200
    data = res.json()
    assert data.get("success") is True
    assert data.get("mode") == "generated"
    assert data.get("data_uri", "").startswith("data:image/svg+xml;base64,")

    # 2. 禁用封面模式
    res_none = client.post("/api/bindery/cover-preview", json={
        "title": "无封面书",
        "cover_mode": "none"
    })
    assert res_none.status_code == 200
    assert res_none.json().get("mode") == "none"
    assert res_none.json().get("data_uri") is None


def test_bindery_build_with_cover_options(client, setup_mock_vault, monkeypatch):
    """测试携带装帧封面策略执行 EPUB 编译落盘"""
    from core.runtime.engine_singleton import get_global_engine
    engine = get_global_engine()
    if engine:
        monkeypatch.setattr(engine, "vault_root", setup_mock_vault)

    payload = {
        "format": "epub",
        "scope": "Docs",
        "lang": "zh",
        "title": "装帧艺术封面版",
        "author": "测试作者",
        "cover_mode": "generated",
        "cover_style": "obsidian_gold",
        "output_dir": "dist/books"
    }
    res = client.post("/api/bindery/build", json=payload)
    assert res.status_code == 200
    b_data = res.json()
    assert b_data.get("success") is True
    fn = b_data.get("filename")
    
    # 检查 EPUB 内部是否成功封装了 cover
    import zipfile
    epub_abs = os.path.abspath(os.path.join("dist/books", fn))
    with zipfile.ZipFile(epub_abs, "r") as z:
        namelist = z.namelist()
        assert "OEBPS/text/cover.xhtml" in namelist
        assert any(n.startswith("OEBPS/images/cover") for n in namelist)


def test_bindery_shelf_view_and_delete(client):
    """测试典籍货架扫描、WebBook 在线即时翻阅以及归档删除全流程"""
    books_dir = os.path.abspath("dist/books")
    os.makedirs(books_dir, exist_ok=True)

    # 准备测试书籍文件
    test_html = os.path.join(books_dir, "test_webbook_sample.html")
    with open(test_html, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html><body><h1>WebBook Test</h1></body></html>")

    test_epub = os.path.join(books_dir, "test_dummy_shelf.epub")
    with open(test_epub, "wb") as f:
        f.write(b"PK\x03\x04test_epub_binary")

    try:
        # 1. 测试货架扫描
        shelf_res = client.get("/api/bindery/shelf")
        assert shelf_res.status_code == 200
        shelf_data = shelf_res.json()
        assert shelf_data.get("success") is True
        books = shelf_data.get("books", [])
        assert any(b["filename"] == "test_webbook_sample.html" for b in books)
        assert any(b["filename"] == "test_dummy_shelf.epub" for b in books)

        sample_webbook = next(b for b in books if b["filename"] == "test_webbook_sample.html")
        assert sample_webbook["format"] == "webbook"
        assert "/api/bindery/view" in sample_webbook["preview_url"]

        # 2. 测试 WebBook 在线流式翻阅
        view_res = client.get("/api/bindery/view?file=test_webbook_sample.html")
        assert view_res.status_code == 200
        assert "text/html" in view_res.headers.get("content-type", "")
        assert "WebBook Test" in view_res.text

        # 3. 测试 view 安全防御与格式校验
        # 目录穿越
        assert client.get("/api/bindery/view?file=../../etc/passwd").status_code == 400
        # 非 html 格式禁止作为网页翻阅
        assert client.get("/api/bindery/view?file=test_dummy_shelf.epub").status_code == 400
        # 不存在文件
        assert client.get("/api/bindery/view?file=not_exist.html").status_code == 404

        # 4. 测试删除文件
        del_res = client.post("/api/bindery/delete", json={"filename": "test_webbook_sample.html"})
        assert del_res.status_code == 200
        assert del_res.json().get("success") is True
        assert not os.path.exists(test_html)

        # 5. 测试删除安全校验
        # 穿越拦截
        assert client.post("/api/bindery/delete", json={"filename": "../../etc/hosts"}).status_code == 400
        # 不存在文件
        assert client.post("/api/bindery/delete", json={"filename": "not_exist.epub"}).status_code == 404

    finally:
        if os.path.exists(test_html):
            os.remove(test_html)
        if os.path.exists(test_epub):
            os.remove(test_epub)

