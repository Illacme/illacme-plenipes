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

    def list_hosting_deploy_batches(self, imprint_id=None, limit=50, offset=0):
        return [
            {
                "batch_id": "deploy_1791550990_test",
                "trigger_source": "vault_drawer:Showcase/test-doc.md",
                "doc_title": "测试托管文档",
                "overall_status": "SUCCESS",
                "started_at": "2026-10-09 21:03:10",
                "targets": {
                    "github_pages": {
                        "status": "SUCCESS",
                        "url": "https://example.github.io/test-doc.html",
                        "deployed_at": "2026-10-09 21:04:17"
                    }
                }
            }
        ]

    def get_documents_snapshot(self):
        return {
            "published.md": {"title": "主权出版之光", "slug": "published"}
        }

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
    """测试 /api/dispatch/overview 能够防御性返回大盘数据，并正确聚合托管与分发成果"""
    response = client.get("/api/dispatch/overview")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "success"
    assert "summary" in data
    assert "channel_health" in data
    assert len(data["recent_records"]) == 2
    assert len(data["dead_letter_tasks"]) == 1

    # 第 1 条应为最新的托管成果 (2026-10-09)
    assert data["recent_records"][0]["title"] == "测试托管文档"
    assert data["recent_records"][0]["target_id"] == "github_pages"
    assert data["recent_records"][0]["target_type"] == "hosting"
    assert data["recent_records"][0]["remote_url"] == "https://example.github.io/test-doc.html"

    # 第 2 条为历史社媒成果 (2026-09-17)
    assert data["recent_records"][1]["title"] == "主权出版之光"
    assert data["recent_records"][1]["remote_url"] == "https://dev.to/article/12345"

    task = data["dead_letter_tasks"][0]
    assert "diagnostic" in task
    assert "badge" in task["diagnostic"]
    assert "suggestion" in task["diagnostic"]
    assert "friendly_message" in task["diagnostic"]


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


def test_dispatch_overview_with_hosting_failure():
    """测试当网站托管发布失败时，/api/dispatch/overview 能够自动将其纳入死信任务并降低成功率"""
    mock_eng = singleton.get_global_engine()
    # 模拟新增一次 github_pages 部署失败批次
    mock_eng.meta.list_hosting_deploy_batches = lambda imprint_id=None, limit=50, offset=0: [
        {
            "batch_id": "deploy_failed_999",
            "trigger_source": "workbench",
            "doc_title": "全站静态站点",
            "overall_status": "FAILED",
            "started_at": "2026-10-10 21:18:27",
            "targets": {
                "github_pages": {
                    "status": "FAILED",
                    "error": "Authentication failed for git push",
                    "deployed_at": "2026-10-10 21:19:00"
                }
            }
        }
    ]

    response = client.get("/api/dispatch/overview")
    assert response.status_code == 200
    data = response.json()

    # 死信任务应包含原社媒失败 1 个 + 托管失败 1 个 = 2 个
    dead_targets = [t["target_id"] for t in data["dead_letter_tasks"]]
    assert "github_pages" in dead_targets
    assert "devto" in dead_targets

    # 找到 github_pages 死信任务并验证字段与诊断
    gh_task = next(t for t in data["dead_letter_tasks"] if t["target_id"] == "github_pages")
    assert gh_task["target_type"] == "hosting"
    assert gh_task["status"] == "FAILED"
    assert "Authentication failed" in gh_task["last_error"]
    assert gh_task["diagnostic"]["action"] == "redeploy"

    # 渠道健康度矩阵中 github_pages 状态应由 healthy 变为 error
    gh_health = next(c for c in data["channel_health"] if c["id"] == "github_pages")
    assert gh_health["status"] == "error"
    assert "存在推送失败任务" in gh_health["status_msg"]

    # 成功率计算应真实下降（非 100%）
    assert data["summary"]["total_failed"] >= 2
    assert data["summary"]["success_rate"] != "100.0%"


def test_dispatch_deadletter_retry_with_hosting_failure(monkeypatch):
    """测试当存在托管失败任务时，调用 /api/dispatch/deadletter/retry 能够自动触发托管重试"""
    from services.api.routes.dispatch_shards import hosting_routes

    mock_eng = singleton.get_global_engine()
    mock_eng.meta.list_hosting_deploy_batches = lambda imprint_id=None, limit=50, offset=0: [
        {
            "batch_id": "deploy_failed_999",
            "trigger_source": "workbench",
            "doc_title": "全站静态站点",
            "overall_status": "FAILED",
            "started_at": "2026-10-10 21:18:27",
            "targets": {
                "github_pages": {
                    "status": "FAILED",
                    "error": "Authentication failed for git push",
                    "deployed_at": "2026-10-10 21:19:00"
                }
            }
        }
    ]

    called_channels = []
    def mock_launch_hosting(eng, target_channel=None, target_channels=None, doc_id=None, trigger_source="workbench"):
        if target_channels:
            called_channels.extend(target_channels)
        elif target_channel:
            called_channels.append(target_channel)
        return {"status": "success", "batch_id": "deploy_mock_retry"}

    monkeypatch.setattr(hosting_routes, "launch_hosting_deploy_job", mock_launch_hosting)

    retry_res = client.post("/api/dispatch/deadletter/retry", json={})
    assert retry_res.status_code == 200
    res_data = retry_res.json()
    assert res_data.get("status") == "success"
    assert "github_pages" in res_data.get("message", "").lower()
    assert "github_pages" in called_channels
