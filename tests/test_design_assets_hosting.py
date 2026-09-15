# -*- coding: utf-8 -*-
"""
🛡️ [V1.0] 媒体资产公网图床托管与外链同步自动化测试
职责：验证图床目标探测、物理委托上传、SQLite cdn_url 回填及文库文档外链同步替换。
🛡️ [SOP-01] 物理行数保持在 300 行以内。
"""

import os
import sqlite3
import tempfile
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from core.api.server import app
from core.runtime.engine_singleton import get_global_engine

@pytest.fixture
def mock_design_env():
    """构造临时 SQLite 数据库与文库原稿测试沙箱"""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_dir = os.path.join(tmpdir, "vault")
        covers_dir = os.path.join(vault_dir, ".plenipes", "cache", "covers")
        os.makedirs(covers_dir, exist_ok=True)

        # 1. 创建测试图片物理文件
        fake_img_filename = "gen_test_sample_123.jpg"
        fake_img_path = os.path.join(covers_dir, fake_img_filename)
        with open(fake_img_path, "wb") as f:
            f.write(b"FAKE_JPEG_DATA_FOR_TESTING")

        # 2. 创建引用的测试 Markdown 原稿
        sample_doc_path = os.path.join(vault_dir, "sample.md")
        local_cover_url = f"/api/design/assets/covers/{fake_img_filename}"
        doc_content = f"""---
title: 测试文章
cover: {local_cover_url}
---
这是测试正文内容。
"""
        with open(sample_doc_path, "w", encoding="utf-8") as f:
            f.write(doc_content)

        # 3. 创建 SQLite 临时元数据库
        db_path = os.path.join(tmpdir, "meta.db")
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
            CREATE TABLE documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rel_path TEXT,
                title TEXT,
                cover TEXT
            )
        """)
        cur.execute("""
            INSERT INTO visual_assets (id, rel_path, asset_type, strategy, source_url, cdn_url, prompt)
            VALUES (1, 'covers/gen_test_sample_123.jpg', 'cover', 'ai_picsum', ?, NULL, '赛博朋克都市')
        """, (local_cover_url,))
        cur.execute("""
            INSERT INTO documents (rel_path, title, cover)
            VALUES ('sample.md', '测试文章', ?)
        """, (local_cover_url,))
        conn.commit()

        # 4. Mock 全局引擎
        from core.runtime.engine_singleton import set_global_engine
        orig_engine = get_global_engine()
        engine = MagicMock()

        mock_sqlite = MagicMock()
        mock_sqlite.get_connection.return_value = conn
        mock_meta = MagicMock()
        mock_meta.sqlite = mock_sqlite

        engine.meta = mock_meta
        engine.vault_root = vault_dir
        engine.config = MagicMock()
        engine.config.system.api_token = None
        engine.config.plugins = {}

        set_global_engine(engine)

        try:
            yield {
                "client": TestClient(app),
                "conn": conn,
                "vault_dir": vault_dir,
                "sample_doc_path": sample_doc_path,
                "local_cover_url": local_cover_url
            }
        finally:
            set_global_engine(orig_engine)
            conn.close()

def test_get_hosting_targets(mock_design_env):
    """测试获取图床目标列表接口"""
    client = mock_design_env["client"]
    res = client.get("/api/design/assets/hosting-targets")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "targets" in data
    targets = data["targets"]
    assert len(targets) > 0

    # 验证 ImgBB 驱动存在并正确包含在 targets 列表中
    target_ids = [t["id"] for t in targets]
    assert "imgbb" in target_ids
    tele_target = next(t for t in targets if t["id"] == "imgbb")
    assert "name" in tele_target
    assert "status_label" in tele_target

def test_upload_asset_to_hosting_success(mock_design_env):
    """测试将本地资产上传至图床并自动同步原稿 Frontmatter"""
    client = mock_design_env["client"]
    conn = mock_design_env["conn"]
    sample_doc_path = mock_design_env["sample_doc_path"]

    mock_cdn_url = "https://i.ibb.co/mocked_remote_image_456.jpg"

    # Mock ImgBBImageHost.upload 方法
    with patch("adapters.egress.image_hosting.imgbb.ImgBBImageHost.upload", return_value=mock_cdn_url):
        payload = {
            "asset_id": 1,
            "provider_id": "imgbb",
            "sync_references": True
        }
        res = client.post("/api/design/assets/upload-hosting", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["cdn_url"] == mock_cdn_url
        assert data["synced_docs_count"] == 1

        # 1. 验证 SQLite visual_assets 表中的 cdn_url 已更新
        cur = conn.cursor()
        cur.execute("SELECT cdn_url FROM visual_assets WHERE id = 1")
        row = cur.fetchone()
        assert row[0] == mock_cdn_url

        # 2. 验证 SQLite documents 表中的 cover 已更新
        cur.execute("SELECT cover FROM documents WHERE rel_path = 'sample.md'")
        doc_row = cur.fetchone()
        assert doc_row[0] == mock_cdn_url

        # 3. 验证原稿 Markdown 物理文件中的 Frontmatter 已替换为 CDN 外链
        with open(sample_doc_path, "r", encoding="utf-8") as f:
            updated_md = f.read()
        assert f"cover: {mock_cdn_url}" in updated_md

def test_upload_asset_not_found(mock_design_env):
    """测试上传不存在的资产 ID"""
    client = mock_design_env["client"]
    res = client.post("/api/design/assets/upload-hosting", json={"asset_id": 999, "provider_id": "imgbb"})
    assert res.status_code == 404
