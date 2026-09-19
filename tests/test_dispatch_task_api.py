#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [V122.0] Tests for Dispatch Task Management API
"""

import pytest
from fastapi.testclient import TestClient
from services.api.server import app
import core.runtime.engine_singleton as singleton


class MockConfig:
    def __init__(self):
        self.syndication = {"devto": {"enabled": True, "api_token": "test_tok"}}
        self.site_url = "https://example.com"


class MockMeta:
    def __init__(self):
        self.tasks = [
            {
                "id": 1,
                "rel_path": "test.md",
                "target_id": "devto",
                "title": "测试文章",
                "slug": "test-slug",
                "lang_code": "zh-CN",
                "status": "FAILED",
                "last_error": "Token expired",
                "retry_count": 2,
                "next_retry_time": 0
            }
        ]
        self.records = [
            {
                "id": 1,
                "rel_path": "published.md",
                "lang_code": "zh-CN",
                "target_id": "devto",
                "remote_article_id": "12345",
                "remote_url": "https://dev.to/article/12345",
                "updated_at": "2026-09-17 12:00:00"
            }
        ]

    def list_all_syndication_tasks(self):
        return self.tasks

    def list_all_syndication_records(self, limit=100, offset=0):
        return self.records

    def retry_syndication_task(self, rel_path=None, target_id=None):
        for t in self.tasks:
            if t["rel_path"] == rel_path and t["target_id"] == target_id:
                t["status"] = "PENDING"

    def delete_syndication_task(self, rel_path=None, target_id=None):
        self.tasks = [t for t in self.tasks if not (t["rel_path"] == rel_path and t["target_id"] == target_id)]


class MockEngine:
    def __init__(self):
        self.config = MockConfig()
        self.meta = MockMeta()
        self.vault_root = "/tmp"


@pytest.fixture(autouse=True)
def setup_mock_engine():
    old = singleton.get_global_engine()
    singleton.set_global_engine(MockEngine())
    yield
    singleton.set_global_engine(old)


client = TestClient(app)


def test_dispatch_overview_api():
    """测试 /api/dispatch/overview 能够防御性返回大盘数据"""
    response = client.get("/api/dispatch/overview")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "success"
    assert "summary" in data
    assert "channel_health" in data
    assert "dead_letter_tasks" in data
    assert "recent_records" in data
    assert len(data["recent_records"]) == 1
    assert len(data["dead_letter_tasks"]) == 1
    assert data["recent_records"][0]["remote_url"] == "https://dev.to/article/12345"


def test_dispatch_active_tasks_api():
    """测试 /api/dispatch/tasks/active 返回活跃状态与队列"""
    response = client.get("/api/dispatch/tasks/active")
    assert response.status_code == 200
    data = response.json()
    assert "is_publishing" in data
    assert "active_pipeline" in data
    assert "pending_queue" in data
    assert isinstance(data["pending_queue"], list)


def test_dispatch_deadletter_actions():
    """测试死信任务重试与清理接口"""
    # 1. 重试
    retry_res = client.post("/api/dispatch/deadletter/retry", json={"rel_path": "test.md", "target_id": "devto"})
    assert retry_res.status_code == 200
    assert retry_res.json().get("status") == "success"

    # 2. 清理
    clear_res = client.request("DELETE", "/api/dispatch/deadletter/clear", json={"rel_path": "test.md", "target_id": "devto"})
    assert clear_res.status_code == 200
    assert clear_res.json().get("status") == "success"
