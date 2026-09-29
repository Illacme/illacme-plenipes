# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Test Suite for Bindery Archive & Batch ZIP Export
测试目标：
1. 非法路径与遍历攻击阻断验证（防越权）
2. 不支持的文件格式与缺失文件安全防御
3. POST /api/bindery/export-zip 批量导出 ZIP（含 MANIFEST.txt 出版清单断言）
4. GET /api/bindery/export-zip 直链打包下载
5. scope="all" 全书架打包归档
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import io
import zipfile
import pytest
from fastapi.testclient import TestClient

from services.api.server import app
from services.api.routes.system import verify_token


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


@pytest.fixture
def mock_books_env(tmp_path, monkeypatch):
    """构建安全的临时 dist/books 物理目录环境"""
    books_dir = tmp_path / "dist" / "books"
    books_dir.mkdir(parents=True, exist_ok=True)

    # 写入若干测试电子书
    epub_file = books_dir / "illacme-press-test-vol1.epub"
    epub_file.write_bytes(b"PK\x03\x04mock_epub_content")

    pdf_file = books_dir / "illacme-press-test-vol1.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 mock_pdf_content")

    md_file = books_dir / "illacme-press-test-bundle.md"
    md_file.write_text("# Test Bundle\n\nSample content.\n", encoding="utf-8")

    docx_file = books_dir / "illacme-press-test-review.docx"
    docx_file.write_bytes(b"PK\x03\x04mock_docx_content")

    # monkeypatch 切换工作目录或模拟 dist/books
    original_cwd = os.getcwd()
    os.chdir(str(tmp_path))
    yield books_dir
    os.chdir(original_cwd)


def test_export_zip_security_traversal_blocked(client, mock_books_env):
    """测试防路径遍历与越权攻击防护"""
    # 试图跳出目录访问外部文件
    res = client.post("/api/bindery/export-zip", json={"filenames": ["../../etc/passwd"]})
    assert res.status_code == 400

    # 包含斜杠的文件名
    res = client.post("/api/bindery/export-zip", json={"filenames": ["sub/folder/file.epub"]})
    assert res.status_code == 400

    # 不存在的书籍
    res = client.post("/api/bindery/export-zip", json={"filenames": ["non_existent_book.epub"]})
    assert res.status_code == 404

    # 非法后缀（例如试图打包 .env 或 .py）
    secret_file = mock_books_env / "secret.env"
    secret_file.write_text("API_KEY=123456", encoding="utf-8")
    res = client.post("/api/bindery/export-zip", json={"filenames": ["secret.env"]})
    assert res.status_code == 400


def test_export_zip_post_batch_success(client, mock_books_env):
    """测试 POST 批量打包已选出版物及 MANIFEST.txt 完整性"""
    target_files = ["illacme-press-test-vol1.epub", "illacme-press-test-bundle.md"]
    res = client.post("/api/bindery/export-zip", json={"filenames": target_files})
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    assert "illacme-books-bundle-" in res.headers["content-disposition"]
    assert res.headers["x-bundle-count"] == "2"

    # 内存解压 ZIP 并验证内容
    zf = zipfile.ZipFile(io.BytesIO(res.content))
    names = zf.namelist()
    assert "MANIFEST.txt" in names
    assert "illacme-press-test-vol1.epub" in names
    assert "illacme-press-test-bundle.md" in names

    # 校验 MANIFEST.txt 包含出版级元数据
    manifest_text = zf.read("MANIFEST.txt").decode("utf-8")
    assert "ILLACME PLENIPES · DIGITAL PUBLICATION ARCHIVE BUNDLE" in manifest_text
    assert "illacme-press-test-vol1.epub" in manifest_text
    assert "illacme-press-test-bundle.md" in manifest_text
    assert "Total Books : 2 item(s)" in manifest_text


def test_export_zip_get_direct_download(client, mock_books_env):
    """测试 GET 请求逗号分隔直传下载"""
    target = "illacme-press-test-vol1.pdf,illacme-press-test-review.docx"
    res = client.get(f"/api/bindery/export-zip?files={target}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"

    zf = zipfile.ZipFile(io.BytesIO(res.content))
    names = zf.namelist()
    assert "MANIFEST.txt" in names
    assert "illacme-press-test-vol1.pdf" in names
    assert "illacme-press-test-review.docx" in names


def test_export_zip_scope_all(client, mock_books_env):
    """测试 scope=all 一键全书架打包归档"""
    res = client.get("/api/bindery/export-zip?scope=all")
    assert res.status_code == 200
    zf = zipfile.ZipFile(io.BytesIO(res.content))
    names = zf.namelist()
    assert "MANIFEST.txt" in names
    # 4 本测试书均应被打包
    assert "illacme-press-test-vol1.epub" in names
    assert "illacme-press-test-vol1.pdf" in names
    assert "illacme-press-test-bundle.md" in names
    assert "illacme-press-test-review.docx" in names

    manifest_text = zf.read("MANIFEST.txt").decode("utf-8")
    assert "Total Books : 4 item(s)" in manifest_text
