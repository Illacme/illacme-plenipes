# -*- coding: utf-8 -*-
"""
📚 [V125.0] Test Suite for Custom Cover Upload & Reader 'M' Shortcut
验证自定义封面上传接口、解码注入电子书管线，以及阅读器 M 快捷键展开/收起目录导航树。
"""

import base64
import os
import pytest
from fastapi.testclient import TestClient

from services.api.server import app
from services.api.routes.system import verify_token


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


def test_cover_preview_custom_mode(client):
    """测试自定义封面预览模式接口响应"""
    # 1. 待上传状态（无图片）
    res = client.post("/api/bindery/cover-preview", json={
        "title": "测试文集",
        "author": "测试作者",
        "cover_mode": "custom"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["mode"] == "custom"
    assert data["data_uri"] is None

    # 2. 携带自定义图片 DataURI
    tiny_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    data_uri = f"data:image/png;base64,{tiny_png_b64}"
    res2 = client.post("/api/bindery/cover-preview", json={
        "title": "测试文集",
        "author": "测试作者",
        "cover_mode": "custom",
        "custom_cover_image": data_uri
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["success"] is True
    assert data2["mode"] == "custom"
    assert data2["data_uri"] == data_uri


def test_custom_cover_build_pipeline(client, tmp_path, monkeypatch):
    """测试通过 API 提交自定义封面并完成电子书装订全流程"""
    from core.runtime.engine_singleton import get_global_engine, set_global_engine
    old_engine = get_global_engine()
    
    # 构造极简文库
    vault_dir = tmp_path / "vault"
    docs_dir = vault_dir / "Docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "01_test.md").write_text("---\ntitle: 测试手稿\n---\n# 测试手稿\n正文内容\n", encoding="utf-8")

    class MockEngine:
        def __init__(self, v_path):
            self.vault_root = str(v_path)
            self.config = type("Config", (), {"site_name": "测试站点", "author": "测试作者"})()

    mock_engine = MockEngine(vault_dir)
    set_global_engine(mock_engine)

    try:
        tiny_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        data_uri = f"data:image/png;base64,{tiny_png_b64}"

        res = client.post("/api/bindery/build", json={
            "format": "epub",
            "scope": "Docs",
            "title": "自定义封面测试全书",
            "author": "测试作者",
            "cover_mode": "custom",
            "custom_cover_image": data_uri
        })
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") is True
        filename = data.get("filename")
        assert filename.endswith(".epub")

        # 验证落盘文件存在且大小大于 0
        book_path = os.path.join("dist/books", filename)
        assert os.path.exists(book_path)
        assert os.path.getsize(book_path) > 0

        # 清理
        try: os.remove(book_path)
        except Exception: pass
    finally:
        set_global_engine(old_engine)


def test_epub_reader_m_shortcut_sovereignty():
    """测试 EPUB 阅读器底层代码包含 M 键快捷键支持与 toggleSidebar 暴露"""
    from core.adapters.egress.ebook.epub_reader_js import get_epub_reader_js
    from core.adapters.egress.ebook.epub_reader_prefs_js import get_epub_prefs_js
    from core.adapters.egress.ebook.epub_reader_template import build_epub_reader_shell

    client_js = get_epub_reader_js()
    prefs_js = get_epub_prefs_js()
    shell_html = build_epub_reader_shell("test", "test", "test", "test")

    # 检查 epub_reader_js 暴露与监听
    assert "window.toggleSidebar = toggleSidebar" in client_js
    assert "KeyM" in client_js

    # 检查按钮 tooltip
    assert "快捷键 M" in shell_html


def test_multilingual_custom_book_title_preservation():
    """验证多语对照装订时，用户自定义标题被完整保留并形成地道的多语言版本，严禁自造标题替换用户书名"""
    from core.bindery.translation_resolver import TranslationResolver

    custom_t = "多语艺术双封面典籍"
    en_t = TranslationResolver.resolve_book_title(custom_t, "en")
    ja_t = TranslationResolver.resolve_book_title(custom_t, "ja")
    zh_t = TranslationResolver.resolve_book_title(custom_t, "zh")

    assert zh_t == custom_t
    # 验证英文与日文版均基于用户自定义书名生成
    assert "Polyglot" in en_t and "Dual-Cover" in en_t
    assert "多言語" in ja_t and "ダブル表紙" in ja_t
    # 验证绝无凭空自造的硬编码模板覆盖
    assert "Illacme · Polyglot Concordance" not in en_t
    assert "Illacme · 多言語対照典籍" not in ja_t


def test_bindery_custom_cover_syncs_to_media_assets(tmp_path):
    """验证装订中心自定义上传封面全自动同步落盘至设计中心媒体资产库并登记 SQLite 账本"""
    import sqlite3
    from core.bindery.bindery_asset_syncer import BinderyAssetSyncer

    # 创建测试用 SQLite 账本
    db_file = tmp_path / "metadata.sqlite"
    conn = sqlite3.connect(str(db_file))
    with conn:
        conn.execute("""
            CREATE TABLE visual_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rel_path TEXT NOT NULL,
                asset_type TEXT NOT NULL DEFAULT 'cover',
                strategy TEXT NOT NULL,
                source_url TEXT,
                cdn_url TEXT,
                media_id TEXT,
                prompt TEXT,
                width INTEGER DEFAULT 0,
                height INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

    class MockSqlite:
        def get_connection(self):
            return sqlite3.connect(str(db_file))

    class MockEngine:
        def __init__(self, root):
            self.vault_root = str(root)
            self.meta = type("Meta", (), {"sqlite": MockSqlite()})()

    mock_engine = MockEngine(tmp_path)
    tiny_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    data_uri = f"data:image/png;base64,{tiny_png_b64}"

    out_books_dir = str(tmp_path / "dist_books")
    cover_res = BinderyAssetSyncer.sync_custom_cover(
        custom_cover_data=data_uri,
        vault_dir=str(tmp_path),
        slug_prefix="test-book",
        out_dir=out_books_dir,
        engine=mock_engine,
        book_title="测试全书"
    )

    # 1. 验证装订产物封面落盘
    assert cover_res is not None
    assert os.path.exists(cover_res)
    assert "cover_test-book_custom.png" in cover_res

    # 2. 验证设计中心媒体资产目录落盘 (.plenipes/cache/covers/)
    covers_cache_dir = tmp_path / ".plenipes" / "cache" / "covers"
    assert covers_cache_dir.exists()
    cached_files = list(covers_cache_dir.glob("upload_bindery_test-book_*.png"))
    assert len(cached_files) == 1
    assert cached_files[0].stat().st_size > 0

    # 3. 验证 SQLite visual_assets 物权账本登记
    check_conn = sqlite3.connect(str(db_file))
    cur = check_conn.cursor()
    cur.execute("SELECT rel_path, asset_type, strategy, source_url, prompt FROM visual_assets")
    row = cur.fetchone()
    assert row is not None
    assert row[0].startswith(".plenipes/cache/covers/upload_bindery_test-book_")
    assert row[1] == "cover"
    assert row[2] == "bindery_upload"
    assert row[3].startswith("/api/design/assets/covers/upload_bindery_test-book_")
    assert "测试全书" in row[4]

    # 4. 验证防重复插入
    BinderyAssetSyncer.sync_custom_cover(
        custom_cover_data=data_uri,
        vault_dir=str(tmp_path),
        slug_prefix="test-book",
        out_dir=out_books_dir,
        engine=mock_engine,
        book_title="测试全书"
    )
    cur.execute("SELECT COUNT(*) FROM visual_assets")
    assert cur.fetchone()[0] == 1


