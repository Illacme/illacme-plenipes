#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [V126.0] Tests for Dispatch Ledger Doc Diff API
"""

import os
from fastapi.testclient import TestClient
from services.api.server import app
import core.runtime.engine_singleton as singleton


class MockConfig:
    def __init__(self, vault_root: str):
        self.vault_root = vault_root


class MockMeta:
    def __init__(self):
        self.records = [
            {
                "id": 1,
                "rel_path": "article.md",
                "target_id": "devto",
                "updated_at": "2026-09-14 12:00:00",
                "remote_url": "https://dev.to/test"
            }
        ]

    def list_all_syndication_records(self, limit=100, offset=0):
        return self.records


class MockEngine:
    def __init__(self, vault_root: str):
        self.config = MockConfig(vault_root)
        self.meta = MockMeta()
        self.vault_root = vault_root


client = TestClient(app)


def test_dispatch_diff_api_file_not_found(tmp_path):
    """测试请求不存在的文档时返回 404"""
    old_engine = singleton.get_global_engine()
    singleton.set_global_engine(MockEngine(str(tmp_path)))
    try:
        res = client.get("/api/dispatch/ledger/diff?rel_path=nonexistent.md")
        assert res.status_code == 404
    finally:
        singleton.set_global_engine(old_engine)


def test_dispatch_diff_api_success(tmp_path):
    """测试正常请求文档返回差异数据结构"""
    doc_path = tmp_path / "article.md"
    doc_path.write_text("# Test Title\n\nContent body.\n", encoding="utf-8")

    old_engine = singleton.get_global_engine()
    singleton.set_global_engine(MockEngine(str(tmp_path)))
    try:
        res = client.get("/api/dispatch/ledger/diff?rel_path=article.md&target_id=devto")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        info = data["data"]
        assert info["rel_path"] == "article.md"
        assert info["target_id"] == "devto"
        assert "published_at" in info
        assert "modified_at" in info
        assert "has_diff" in info
        assert "additions" in info
        assert "deletions" in info
    finally:
        singleton.set_global_engine(old_engine)
