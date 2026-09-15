# -*- coding: utf-8 -*-
"""
Unit tests for Design Studio Batch Cover Operations Routes.
"""
import os
import tempfile
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from core.api.server import app
from core.runtime.engine_singleton import get_global_engine, set_global_engine

@pytest.fixture
def mock_batch_env():
    """构造临时文库测试沙箱与 Mock 引擎"""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_dir = os.path.join(tmpdir, "vault")
        covers_dir = os.path.join(vault_dir, ".plenipes", "cache", "covers")
        os.makedirs(covers_dir, exist_ok=True)

        # 1. 包含封面的文章
        with open(os.path.join(vault_dir, "doc_with_cover.md"), "w", encoding="utf-8") as f:
            f.write("---\ntitle: 已有封面\ncover: /api/design/assets/covers/test.jpg\n---\n正文")

        # 2. 缺少封面的文章
        with open(os.path.join(vault_dir, "doc_no_cover.md"), "w", encoding="utf-8") as f:
            f.write("---\ntitle: 待配图文章\ncategory: Tech\n---\n这是一篇需要配图的原稿。")

        orig_engine = get_global_engine()
        engine = MagicMock()
        mock_sqlite = MagicMock()
        mock_meta = MagicMock()
        mock_meta.sqlite = mock_sqlite

        engine.meta = mock_meta
        engine.vault_root = vault_dir
        engine.imprint_id = "default"
        engine.brand_name = "TEST_BRAND"
        engine.config = MagicMock()
        engine.config.system.api_token = None

        set_global_engine(engine)

        try:
            yield {
                "client": TestClient(app),
                "vault_dir": vault_dir
            }
        finally:
            set_global_engine(orig_engine)

def test_uncovered_docs_report(mock_batch_env):
    client = mock_batch_env["client"]
    response = client.get("/api/design/batch/uncovered-docs")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 2
    assert data["covered_count"] == 1
    assert data["uncovered_count"] == 1
    assert len(data["uncovered_docs"]) == 1
    assert data["uncovered_docs"][0]["title"] == "待配图文章"

def test_batch_generate_and_apply(mock_batch_env):
    client = mock_batch_env["client"]
    response = client.post("/api/design/batch/generate-and-apply", json={
        "doc_ids": ["doc_no_cover.md"],
        "strategy": "og_card"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["applied_count"] == 1

    # 验证原稿文件的 Frontmatter 已被成功注入 cover
    vault_dir = mock_batch_env["vault_dir"]
    doc_path = os.path.join(vault_dir, "doc_no_cover.md")
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "cover:" in content
    assert "/api/design/assets/covers/" in content
