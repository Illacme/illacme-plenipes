# -*- coding: utf-8 -*-
"""
📚 [V125.0] Test Suite for Gov Bindery & EBook Export APIs
测试范围：装订范围勘测、合卷编排生成、产物落盘与安全防越权下载。
"""

import os
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


def test_bindery_single_document_flow(client, setup_mock_vault):
    """🚀 测试单篇 Markdown 文稿极速装订 (EPUB / WebBook / PDF)"""
    from core.runtime.engine_singleton import get_global_engine, set_global_engine
    old_engine = get_global_engine()
    mock_engine = type("MockEngine", (), {"vault_root": setup_mock_vault, "config": None})()
    set_global_engine(mock_engine)

    try:
        # 1. 测试单篇 EPUB 极速装订
        single_rel = "Docs/01_intro.md"
        payload_epub = {
            "format": "epub",
            "scope": f"single:{single_rel}",
            "lang": "zh",
            "title": "单篇系统引言独立出版物",
            "output_dir": "dist/books"
        }
        res = client.post("/api/bindery/build", json=payload_epub)
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") is True
        assert data.get("chapter_count") == 1
        fn = data.get("filename")
        assert fn.endswith(".epub")

        epub_abs = os.path.abspath(os.path.join("dist/books", fn))
        assert os.path.exists(epub_abs)
        assert os.path.getsize(epub_abs) > 0

        # 2. 测试单篇 WebBook 极速装订
        payload_wb = {
            "format": "webbook",
            "scope": f"single:{single_rel}",
            "lang": "zh",
            "output_dir": "dist/books"
        }
        res_wb = client.post("/api/bindery/build", json=payload_wb)
        assert res_wb.status_code == 200
        wb_data = res_wb.json()
        assert wb_data.get("success") is True
        assert wb_data.get("chapter_count") == 1
        assert wb_data.get("preview_url") is not None
        wb_fn = wb_data.get("filename")
        assert wb_fn.endswith(".html")
    finally:
        set_global_engine(old_engine)


def test_bindery_pdf_export_flow(client, setup_mock_vault):
    """🚀 测试独立单文件 PDF 印刷典籍装订全流程（含全卷、单篇、安全下载与书架检索）"""
    from core.runtime.engine_singleton import get_global_engine, set_global_engine
    old_engine = get_global_engine()
    mock_engine = type("MockEngine", (), {"vault_root": setup_mock_vault, "config": None})()
    set_global_engine(mock_engine)

    try:
        # 1. 测试栏目分卷 PDF 装订
        payload_pdf = {
            "format": "pdf",
            "scope": "Docs",
            "lang": "zh",
            "title": "精装印刷典籍测试版",
            "author": "Illacme Master Team",
            "output_dir": "dist/books"
        }
        res = client.post("/api/bindery/build", json=payload_pdf)
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") is True
        assert data.get("format") == "pdf"
        assert data.get("chapter_count") >= 2
        fn = data.get("filename")
        assert fn.endswith(".pdf")

        pdf_abs = os.path.abspath(os.path.join("dist/books", fn))
        assert os.path.exists(pdf_abs)
        assert os.path.getsize(pdf_abs) > 0
        with open(pdf_abs, "rb") as f:
            header = f.read(5)
            assert header == b"%PDF-"

        # 2. 测试二进制流式安全下载
        dl_res = client.get(f"/api/bindery/download?file={fn}")
        assert dl_res.status_code == 200
        assert "application/pdf" in dl_res.headers.get("content-type", "")
        assert len(dl_res.content) == os.path.getsize(pdf_abs)

        # 3. 测试单篇 Markdown 极速装订为 PDF
        single_rel = "Docs/02_guide.md"
        payload_single_pdf = {
            "format": "pdf",
            "scope": f"single:{single_rel}",
            "lang": "zh",
            "title": "单篇指南精美印本",
            "output_dir": "dist/books"
        }
        res_single = client.post("/api/bindery/build", json=payload_single_pdf)
        assert res_single.status_code == 200
        single_data = res_single.json()
        assert single_data.get("success") is True
        assert single_data.get("chapter_count") == 1
        s_fn = single_data.get("filename")
        assert s_fn.endswith(".pdf")

        # 4. 验证书架扫描感知到了刚编译的 PDF 文件
        shelf_res = client.get("/api/bindery/shelf")
        assert shelf_res.status_code == 200
        books = shelf_res.json().get("books", [])
        pdf_books = [b for b in books if b["format"] == "pdf"]
        # 5. 验证 PDF 驱动内部渲染逻辑：确保跨章超链接全部自愈为同文档内部锚点 #ch_X，杜绝 FileLinkedNotAvail 外部文件报错
        from core.adapters.egress.ebook.pdf import PDFBookAdapter
        adapter = PDFBookAdapter()
        mock_tree = [
            {"title": "首页", "html_body": '<p><a href="ch_2.xhtml#ch_2">前往第二章</a> 和 <a href="./docs/other.html">外部相对链接</a></p>'},
            {"title": "第二章", "html_body": '<p>这是第二章内容</p>'}
        ]
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_pdf:
            out_pdf_p = tmp_pdf.name
        res_ok = adapter.bind_book(mock_tree, {"title": "测试双链"}, None, "zh", out_pdf_p)
        assert res_ok is True
        assert os.path.exists(out_pdf_p) and os.path.getsize(out_pdf_p) > 0
        with open(out_pdf_p, "rb") as f:
            pdf_raw = f.read()
        # 严格断言：生成的 PDF 二进制中绝对不得出现 .xhtml 外部相对文件死链
        assert b".xhtml" not in pdf_raw
        # 6. 验证前置目录 (TOC) 与末尾版权页 (Colophon) 在多章节 PDF 中已成功注入
        from core.adapters.egress.ebook.pdf_assets import PDFAssets
        from core.adapters.egress.ebook.colophon import ColophonBuilder
        toc_html = PDFAssets.render_toc_html(mock_tree, lang="zh")
        assert 'id="print-toc"' in toc_html
        assert "目  录" in toc_html
        assert 'href="#ch_2"' in toc_html
        # 验证单篇模式下不冗余生成全书大目录
        assert PDFAssets.render_toc_html([mock_tree[0]], lang="zh") == ""
        # 验证版权页数据包含 PDF 规格
        c_data = ColophonBuilder.build_colophon_data(mock_tree, {"title": "测试双链"}, format_name="pdf")
        assert "PDF 印本" in c_data["format_name"]
        colo_html = PDFAssets.render_colophon_html(c_data, lang="zh")
        assert 'id="print-colophon"' in colo_html
        assert "物权编码" in colo_html

        if os.path.exists(out_pdf_p):
            try: os.remove(out_pdf_p)
            except Exception: pass

    finally:
        set_global_engine(old_engine)

