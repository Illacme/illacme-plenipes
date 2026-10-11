#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [V123.0] Tests for Dispatch Stale Content Detection & Hash Diff
"""

import hashlib
import pytest
from fastapi.testclient import TestClient
from services.api.server import app
import core.runtime.engine_singleton as singleton


class MockConfig:
    def __init__(self, vault_root: str):
        self.syndication = {"devto": {"enabled": True, "api_token": "test_tok"}}
        self.site_url = "https://example.com"
        self.vault_root = vault_root


class MockMeta:
    def __init__(self):
        self.records = []

    def list_all_syndication_tasks(self):
        return []

    def list_all_syndication_records(self, limit=100, offset=0):
        return self.records

    def list_hosting_deploy_batches(self, imprint_id=None, limit=50, offset=0):
        return []

    def get_documents_snapshot(self):
        return {}


class MockEngine:
    def __init__(self, vault_root: str):
        self.config = MockConfig(vault_root)
        self.meta = MockMeta()
        self.vault_root = vault_root


client = TestClient(app)


def test_dispatch_stale_content_detection(tmp_path):
    """测试当本地文库原稿 MD5 与记录保存的 content_hash 不一致时，输出 is_stale=True"""
    doc_path = tmp_path / "article.md"
    doc_path.write_text("# Updated Article Content\n\nNew edits.", encoding="utf-8")
    cur_hash = hashlib.md5(doc_path.read_bytes()).hexdigest()
    old_hash = "deadbeef1234567890abcdef"

    old_engine = singleton.get_global_engine()
    mock_eng = MockEngine(str(tmp_path))
    singleton.set_global_engine(mock_eng)

    try:
        mock_eng.meta.records = [
            {
                "id": 1,
                "rel_path": "article.md",
                "lang_code": "zh-CN",
                "target_id": "devto",
                "remote_article_id": "999",
                "remote_url": "https://dev.to/test",
                "content_hash": old_hash,
                "updated_at": "2026-10-10 10:00:00"
            }
        ]

        res = client.get("/api/dispatch/overview")
        assert res.status_code == 200
        data = res.json()
        recs = data.get("recent_records", [])
        assert len(recs) == 1
        rec = recs[0]
        assert rec["content_hash"] == old_hash
        assert rec["current_hash"] == cur_hash
        assert rec["is_stale"] is True

        # 如果文库内容哈希一致，则 is_stale 为 False
        mock_eng.meta.records = [
            {
                "id": 1,
                "rel_path": "article.md",
                "lang_code": "zh-CN",
                "target_id": "devto",
                "remote_article_id": "999",
                "content_hash": cur_hash,
                "updated_at": "2026-10-10 10:00:00"
            }
        ]
        res2 = client.get("/api/dispatch/overview")
        assert res2.status_code == 200
        rec2 = res2.json()["recent_records"][0]
        assert rec2["is_stale"] is False
    finally:
        singleton.set_global_engine(old_engine)
