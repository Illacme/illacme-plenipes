#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [V123.0] Tests for Dispatch Stale Content Detection
"""

import os
from datetime import datetime
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
    """测试原稿在发布后被编辑修改时输出 is_stale=True，未被修改时输出 is_stale=False"""
    doc_path = tmp_path / "article.md"
    doc_path.write_text("# Article Content\n\nInitial version.", encoding="utf-8")
    
    # 模拟文件物理 mtime 设为 2026-10-10 12:00:00
    file_ts = datetime.fromisoformat("2026-10-10T12:00:00").timestamp()
    os.utime(str(doc_path), (file_ts, file_ts))

    old_engine = singleton.get_global_engine()
    mock_eng = MockEngine(str(tmp_path))
    singleton.set_global_engine(mock_eng)

    try:
        # 1. 模拟早于修改时间的发布记录（2026-10-10 10:00:00 < 12:00:00），原稿已发生新修改 -> is_stale=True
        mock_eng.meta.records = [
            {
                "id": 1,
                "rel_path": "article.md",
                "lang_code": "zh-CN",
                "target_id": "devto",
                "remote_article_id": "999",
                "remote_url": "https://dev.to/test",
                "content_hash": "dummy_hash",
                "updated_at": "2026-10-10 10:00:00"
            }
        ]

        res = client.get("/api/dispatch/overview")
        assert res.status_code == 200
        data = res.json()
        recs = data.get("recent_records", [])
        assert len(recs) == 1
        assert recs[0]["is_stale"] is True

        # 2. 模拟晚于修改时间的发布记录（2026-10-10 14:00:00 > 12:00:00），刚刚推流最新 -> is_stale=False
        mock_eng.meta.records = [
            {
                "id": 1,
                "rel_path": "article.md",
                "lang_code": "zh-CN",
                "target_id": "devto",
                "remote_article_id": "999",
                "remote_url": "https://dev.to/test",
                "content_hash": "dummy_hash",
                "updated_at": "2026-10-10 14:00:00"
            }
        ]
        res2 = client.get("/api/dispatch/overview")
        assert res2.status_code == 200
        assert res2.json()["recent_records"][0]["is_stale"] is False
    finally:
        singleton.set_global_engine(old_engine)
