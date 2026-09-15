# -*- coding: utf-8 -*-
"""
🧪 Test Design Asset Batch Delete & Document Unbind
"""
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from core.api.server import app
from core.runtime.engine_singleton import set_global_engine

@pytest.fixture
def mock_engine_with_assets(tmp_path):
    vault_root = tmp_path / "vault"
    vault_root.mkdir()
    covers_dir = vault_root / ".plenipes" / "cache" / "covers"
    covers_dir.mkdir(parents=True)

    # 创建测试原稿
    doc_path = vault_root / "test-doc.md"
    doc_path.write_text(
        "---\ntitle: 测试文章\ncover: /api/design/assets/covers/test-cover.jpg\n---\n正文内容\n",
        encoding="utf-8"
    )

    # 创建测试封面物理文件
    img_file = covers_dir / "test-cover.jpg"
    img_file.write_bytes(b"fake image bytes")

    # 创建 Mock SQLite 与 Engine
    import sqlite3
    db_path = str(tmp_path / "metadata.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE visual_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rel_path TEXT,
            asset_type TEXT,
            strategy TEXT,
            source_url TEXT,
            cdn_url TEXT,
            media_id TEXT,
            prompt TEXT,
            created_at TEXT
        )
    """)
    cur.execute("""
        INSERT INTO visual_assets (id, rel_path, asset_type, strategy, source_url, created_at)
        VALUES (101, 'covers/test-cover.jpg', 'cover', 'og_card', '/api/design/assets/covers/test-cover.jpg', '2026-09-13 00:00:00')
    """)
    conn.commit()

    mock_sqlite = MagicMock()
    mock_sqlite.get_connection = MagicMock(return_value=conn)
    mock_sqlite.update_document_metadata = MagicMock()

    mock_engine = MagicMock()
    mock_engine.vault_root = str(vault_root)
    mock_engine.meta.sqlite = mock_sqlite
    mock_engine.config.system.api_token = None

    set_global_engine(mock_engine)
    yield mock_engine, conn, doc_path, img_file
    set_global_engine(None)

def test_batch_delete_assets_with_doc_unbinding(mock_engine_with_assets):
    engine, conn, doc_path, img_file = mock_engine_with_assets
    client = TestClient(app)

    # 1. 验证删除前：物理图片存在，文档有 cover 属性，DB 有记录
    assert img_file.exists()
    assert "cover:" in doc_path.read_text(encoding="utf-8")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM visual_assets WHERE id = 101")
    assert cur.fetchone()[0] == 1

    # 2. 调用批量删除端点
    resp = client.post("/api/design/assets/batch-delete", json={
        "asset_ids": [101],
        "remove_from_docs": True
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["deleted_count"] == 1
    assert data["unbound_docs_count"] == 1

    # 3. 验证删除后：物理文件已删除，DB 记录已清理，文档 cover 属性已清空
    assert not img_file.exists()
    cur.execute("SELECT COUNT(*) FROM visual_assets WHERE id = 101")
    assert cur.fetchone()[0] == 0

    new_doc_content = doc_path.read_text(encoding="utf-8")
    assert "cover: ''" in new_doc_content or "cover:" not in new_doc_content
    engine.meta.sqlite.update_document_metadata.assert_called_with("test-doc.md", {"cover": ""})
