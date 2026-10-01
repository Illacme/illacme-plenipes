# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Test Suite for Additional Bindery Formats (Markdown & DOCX)
测试目标：
1. MarkdownBundleAdapter 真实编译生成长篇合并 Markdown 文件
2. DocxBookAdapter 真实编译生成出版级 Word .docx 文件
3. /api/bindery/scopes 动态注册包含 markdown 和 docx
4. /api/bindery/build 支持多格式输出
5. /api/bindery/shelf 货架扫描、统计与安全下载
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import pytest
from fastapi.testclient import TestClient

from services.api.server import app
from services.api.routes.system import verify_token
from core.adapters.egress.ebook.markdown_bundle import MarkdownBundleAdapter
from core.adapters.egress.ebook.docx import DocxBookAdapter


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


@pytest.fixture
def sample_manuscript_tree():
    return [
        {
            "id": "ch_1",
            "title": "第一章 典籍绪论",
            "slug": "intro",
            "raw_body": "# 绪论\n\n欢迎阅读数字典籍合卷。\n\n## 核心宗旨\n\n建立自主出版主权。\n\n- 自由流式\n- 离线网页\n- Word 审校\n- Markdown 合卷\n",
            "headings": [{"title": "核心宗旨", "level": 2}],
            "assets": []
        },
        {
            "id": "ch_2",
            "title": "第二章 架构原理",
            "slug": "architecture",
            "raw_body": "# 架构原理\n\n系统采用纯插件化驱动插槽设计。\n\n> [!NOTE]\n> 所有电子书格式遵循 BaseEBookAdapter 统一契约。\n",
            "headings": [],
            "assets": []
        }
    ]


@pytest.fixture
def sample_book_meta():
    return {
        "title": "数字主权出版实践典籍",
        "author": "Illacme 架构研造组",
        "publisher": "Illacme Plenipes Global Press",
        "description": "探讨数字出版主权与多格式导出实践。",
        "license": "保留所有权利 · All Rights Reserved",
        "isbn": "978-7-00-000000-0"
    }


def test_markdown_bundle_adapter_generation(tmp_path, sample_manuscript_tree, sample_book_meta):
    """验证 MarkdownBundleAdapter 能自愈生成标准合并 Markdown"""
    out_file = str(tmp_path / "test_bundle.md")
    adapter = MarkdownBundleAdapter()
    success = adapter.bind_book(
        manuscript_tree=sample_manuscript_tree,
        book_metadata=sample_book_meta,
        target_lang="zh",
        output_file_path=out_file
    )
    assert success is True
    assert os.path.isfile(out_file)
    assert os.path.getsize(out_file) > 0

    with open(out_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 验证 Frontmatter
    assert "---" in content
    assert "title: 数字主权出版实践典籍" in content
    assert "chapters_count: 2" in content

    # 验证 TOC 目录大纲
    assert "## 📖 目录大纲 (Contents)" in content
    assert "[1. 第一章 典籍绪论]" in content
    assert "[2. 第二章 架构原理]" in content

    # 验证正文章节与标题顺延降级 (原一级标题 # 绪论 降级为 ### 绪论)
    assert "## 1. 第一章 典籍绪论" in content
    assert "### 绪论" in content
    assert "## 2. 第二章 架构原理" in content

    # 验证版权声明
    assert "## 📜 版权声明 (Colophon)" in content
    assert "Illacme Plenipes Sovereign Digital Bindery Hub" in content


def test_docx_book_adapter_generation(tmp_path, sample_manuscript_tree, sample_book_meta):
    """验证 DocxBookAdapter 能生成标准出版级 Word 审校文档"""
    out_file = str(tmp_path / "test_review.docx")
    adapter = DocxBookAdapter()
    success = adapter.bind_book(
        manuscript_tree=sample_manuscript_tree,
        book_metadata=sample_book_meta,
        target_lang="zh",
        output_file_path=out_file
    )
    assert success is True
    assert os.path.isfile(out_file)
    assert os.path.getsize(out_file) > 1000

    # 读取 docx 验证结构
    import docx
    doc = docx.Document(out_file)
    all_text = " ".join([p.text for p in doc.paragraphs])
    assert "数字主权出版实践典籍" in all_text
    assert "Illacme 架构研造组" in all_text
    assert "第一章 典籍绪论" in all_text
    assert "第二章 架构原理" in all_text
    assert "版权声明" in all_text


def test_scopes_returns_all_five_formats(client):
    """验证 /api/bindery/scopes 接口动态返回所有 5 种装订格式"""
    res = client.get("/api/bindery/scopes")
    assert res.status_code == 200
    data = res.json()
    assert data.get("success") is True
    format_ids = [f["id"] for f in data.get("formats", [])]
    assert "epub" in format_ids
    assert "webbook" in format_ids
    assert "pdf" in format_ids
    assert "markdown" in format_ids
    assert "docx" in format_ids


def test_build_and_shelf_markdown_and_docx(client, tmp_path, monkeypatch):
    """测试 /api/bindery/build 装订 Markdown 与 Docx，并验证货架识别"""
    # 构造模拟文库
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    doc_file = vault_dir / "01_intro.md"
    doc_file.write_text("# 介绍\n\n这是合卷测试稿件。\n", encoding="utf-8")

    mock_engine = type("MockEngine", (), {
        "vault_root": str(vault_dir),
        "site_name": "Test Formats Press",
        "author": "Tester"
    })()
    monkeypatch.setattr("services.api.routes.gov.bindery.get_global_engine", lambda: mock_engine)

    out_dir = os.path.abspath("dist/books")
    os.makedirs(out_dir, exist_ok=True)

    # 1. 装订 Markdown 合卷
    res_md = client.post("/api/bindery/build", json={
        "format": "markdown",
        "scope": "all",
        "lang": "zh",
        "title": "Auto Test MD Book",
        "cover_mode": "none"
    })
    assert res_md.status_code == 200
    md_data = res_md.json()
    assert md_data.get("success") is True
    md_filename = md_data.get("filename")
    assert md_filename.endswith(".md")
    md_real_p = os.path.join(out_dir, md_filename)
    assert os.path.isfile(md_real_p)
    with open(md_real_p, "r", encoding="utf-8") as f:
        md_text = f.read()
        assert "这是合卷测试稿件" in md_text, "Markdown 合卷必须包含真实章节正文！"

    # 2. 装订 Docx 审校本
    res_docx = client.post("/api/bindery/build", json={
        "format": "docx",
        "scope": "all",
        "lang": "zh",
        "title": "Auto Test Docx Book",
        "cover_mode": "none"
    })
    assert res_docx.status_code == 200
    docx_data = res_docx.json()
    assert docx_data.get("success") is True
    docx_filename = docx_data.get("filename")
    assert docx_filename.endswith(".docx")
    docx_real_p = os.path.join(out_dir, docx_filename)
    assert os.path.isfile(docx_real_p)
    import docx
    d = docx.Document(docx_real_p)
    all_paras = [p.text for p in d.paragraphs if p.text.strip()]
    assert any("这是合卷测试稿件" in p for p in all_paras), "Docx 必须包含真实章节正文！"

    # 3. 装订 TXT 便携文本
    res_txt = client.post("/api/bindery/build", json={
        "format": "txt",
        "scope": "all",
        "lang": "zh",
        "title": "Auto Test TXT Book",
        "cover_mode": "none"
    })
    assert res_txt.status_code == 200
    txt_data = res_txt.json()
    assert txt_data.get("success") is True
    txt_filename = txt_data.get("filename")
    txt_real_p = os.path.join(out_dir, txt_filename)
    assert os.path.isfile(txt_real_p)
    with open(txt_real_p, "r", encoding="utf-8") as f:
        txt_text = f.read()
        assert "这是合卷测试稿件" in txt_text, "TXT 便携本必须包含真实章节正文！"

    # 4. 验证货架接口正确识别 formats
    res_shelf = client.get("/api/bindery/shelf")
    assert res_shelf.status_code == 200
    shelf_data = res_shelf.json()
    book_items = {b["filename"]: b for b in shelf_data.get("books", [])}
    assert md_filename in book_items
    assert book_items[md_filename]["format"] == "markdown"
    assert docx_filename in book_items
    assert book_items[docx_filename]["format"] == "docx"
    assert txt_filename in book_items
    assert book_items[txt_filename]["format"] == "txt"

    # 5. 验证在线查看 / 下载
    res_view_md = client.get(f"/api/bindery/view?file={md_filename}")
    assert res_view_md.status_code == 200
    assert "text/plain" in res_view_md.headers.get("content-type", "")

    res_dl_docx = client.get(f"/api/bindery/download?file={docx_filename}")
    assert res_dl_docx.status_code == 200

    # 清理测试产物
    for fn in (md_filename, docx_filename, txt_filename):
        p = os.path.join(out_dir, fn)
        if os.path.exists(p):
            os.remove(p)


def test_polyglot_build_more_formats(client, tmp_path, monkeypatch):
    """测试多语对照模式 (polyglot_mode) 下装订 Docx 与 Markdown 并验证双语对齐正文写入"""
    vault_dir = tmp_path / "poly_vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    (vault_dir / "01_guide.md").write_text("# 研造指南\n\n主语言正文内容段落。\n", encoding="utf-8")
    (vault_dir / "01_guide.en.md").write_text("# Guide\n\nEnglish translation body content.\n", encoding="utf-8")

    mock_engine = type("MockEngine", (), {
        "vault_root": str(vault_dir),
        "site_name": "Polyglot Formats Press",
        "author": "Polyglot Team"
    })()
    monkeypatch.setattr("services.api.routes.gov.bindery.get_global_engine", lambda: mock_engine)

    out_dir = os.path.abspath("dist/books")
    os.makedirs(out_dir, exist_ok=True)

    # 1. 多语 Markdown
    res_md = client.post("/api/bindery/build", json={
        "format": "markdown", "scope": "all", "polyglot_mode": True,
        "languages": ["zh", "en"], "title": "Bilingual MD", "cover_mode": "none"
    })
    assert res_md.status_code == 200
    fn_md = res_md.json().get("filename")
    with open(os.path.join(out_dir, fn_md), encoding="utf-8") as f:
        c = f.read()
        assert "主语言正文内容段落" in c
        assert "ZH)" in c and "EN)" in c

    # 2. 多语 Docx
    res_docx = client.post("/api/bindery/build", json={
        "format": "docx", "scope": "all", "polyglot_mode": True,
        "languages": ["zh", "en"], "title": "Bilingual Docx", "cover_mode": "none"
    })
    assert res_docx.status_code == 200
    fn_docx = res_docx.json().get("filename")
    import docx
    d = docx.Document(os.path.join(out_dir, fn_docx))
    all_texts = [p.text for p in d.paragraphs if p.text.strip()]
    for tbl in d.tables:
        for row in tbl.rows:
            for cell in row.cells:
                all_texts.extend([p.text for p in cell.paragraphs if p.text.strip()])
    assert any("主语言正文内容段落" in t for t in all_texts)
    assert len(d.tables) >= 1

    # 清理
    for fn in (fn_md, fn_docx):
        p = os.path.join(out_dir, fn)
        if os.path.exists(p): os.remove(p)

