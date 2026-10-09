#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [V125.0] Tests for Dispatch Hosting Management API
"""

import pytest
from fastapi.testclient import TestClient
from services.api.server import app
import core.runtime.engine_singleton as singleton


class MockConfig:
    def __init__(self):
        self.active_imprint = "default"
        self.active_theme = "default"
        self.direct_upload = {
            "cloudflare_pages": {"enabled": True, "project_name": "my-cf-site"},
            "netlify": {"enabled": True, "site_name": "my-net-site"},
            "github_pages": {"enabled": True, "repo_url": "https://github.com/myorg/myrepo.git"},
            "gitlab_pages": {"enabled": True, "repo_url": "https://gitlab.com/gluser/glrepo.git"},
            "gitee_pages": {"enabled": True, "repo_url": "https://gitee.com/gtuser/gtrepo.git"},
            "render": {"enabled": True, "project_name": "my-render-app"},
            "vercel": {"enabled": True, "project_name": "my-vercel-app"}
        }


class MockMeta:
    def __init__(self):
        self.batches = [
            {
                "id": 1,
                "batch_id": "deploy_test_001",
                "trigger_source": "workbench",
                "imprint_id": "default",
                "theme": "default",
                "pages_count": 42,
                "bundle_size_kb": 1280.5,
                "targets_json": '{"cloudflare_pages": {"status": "SUCCESS"}}',
                "targets": {"cloudflare_pages": {"status": "SUCCESS"}},
                "overall_status": "SUCCESS",
                "started_at": "2026-10-04 09:00:00",
                "completed_at": "2026-10-04 09:00:05",
                "duration_sec": 5.2
            }
        ]

    def list_hosting_deploy_batches(self, imprint_id=None, limit=50, offset=0):
        return self.batches[offset:offset + limit]

    def count_hosting_deploy_batches(self, imprint_id=None):
        return len(self.batches)

    def create_hosting_deploy_batch(self, **kwargs):
        self.batches.append(kwargs)
        return kwargs["batch_id"]

    def update_hosting_deploy_batch(self, **kwargs):
        pass


class MockEngine:
    def __init__(self):
        self.config = MockConfig()
        self.meta = MockMeta()
        self.vault_root = "/tmp"


@pytest.fixture(autouse=True)
def setup_engine(monkeypatch):
    mock = MockEngine()
    monkeypatch.setattr(singleton, "_GLOBAL_ENGINE", mock)
    yield


def test_get_hosting_overview():
    client = TestClient(app)
    resp = client.get("/api/dispatch/hosting/overview", headers={"Authorization": "Bearer plenipes-dev-token"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "bundle" in data
    assert "fleet" in data
    assert "pagination" in data
    assert data["pagination"]["total"] == 1
    assert data["pagination"]["page"] == 1
    assert len(data["fleet"]) == 11
    assert data["total_channels"] == 11
    assert data["ready_channels"] >= 1
    assert len(data["batches"]) == 1
    assert data["batches"][0]["batch_id"] == "deploy_test_001"

    fleet_dict = {f["id"]: f for f in data["fleet"]}
    assert fleet_dict["cloudflare_pages"]["site_url"] == "https://my-cf-site.pages.dev"
    assert fleet_dict["netlify"]["site_url"] == "https://my-net-site.netlify.app"
    assert fleet_dict["github_pages"]["site_url"] == "https://myorg.github.io/myrepo/"
    assert fleet_dict["gitlab_pages"]["site_url"] == "https://gluser.gitlab.io/glrepo/"
    assert fleet_dict["gitee_pages"]["site_url"] == "https://gtuser.gitee.io/gtrepo/"
    assert fleet_dict["render"]["site_url"] == "https://my-render-app.onrender.com"
    assert fleet_dict["vercel"]["site_url"] == "https://my-vercel-app.vercel.app"


def test_list_hosting_batches_pagination():
    client = TestClient(app)
    resp = client.get("/api/dispatch/hosting/batches?page=1&page_size=5", headers={"Authorization": "Bearer plenipes-dev-token"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["batches"]) == 1
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 5
    assert data["pagination"]["total"] == 1
    assert data["pagination"]["total_pages"] == 1


def test_trigger_hosting_deploy():
    client = TestClient(app)
    resp = client.post(
        "/api/dispatch/hosting/deploy",
        json={"target_channel": "cloudflare_pages", "trigger_source": "workbench"},
        headers={"Authorization": "Bearer plenipes-dev-token"}
    )
    assert resp.status_code in (200, 400)


def test_record_global_deploy_batch_bridge():
    from core.bindery.hosting_record_bridge import record_global_deploy_batch
    mock = singleton._GLOBAL_ENGINE
    deploy_results = {
        "status": "success",
        "summary": {
            "total_channels": 2,
            "success_count": 2,
            "fail_count": 0,
            "channels": [
                {"id": "github_pages", "status": "success", "url": "https://test.github.io/repo/"},
                {"id": "vercel", "status": "success", "url": "https://test.vercel.app"}
            ]
        }
    }
    batch_id = record_global_deploy_batch(mock, "/tmp", deploy_results, duration_sec=12.5)
    assert batch_id is not None
    assert batch_id.startswith("deploy_")
    created = [b for b in mock.meta.batches if b.get("batch_id") == batch_id]
    assert len(created) == 1
    assert created[0]["overall_status"] == "SUCCESS"
    assert created[0]["trigger_source"] == "global_publish"
    assert "github_pages" in created[0]["targets_json"]


def test_record_global_deploy_batch_bridge_with_process_logs():
    from core.bindery.hosting_record_bridge import record_global_deploy_batch
    mock = singleton._GLOBAL_ENGINE
    deploy_results = {
        "status": "success",
        "process_logs": [
            "[18:00:01] [INIT] 全域发布驱动整站部署任务启动...",
            "[18:00:01] [ROUTING] 目标平台队列: github_pages, vercel",
            "[18:00:02] [PUSH] 正在向平台 [github_pages] 推送静态网站产物...",
            "[18:00:06] [SUCCESS] 平台 [github_pages] 部署完成 -> 线上地址: https://test.github.io/repo/ (耗时 4.12s)",
            "[18:00:06] [PUSH] 正在向平台 [vercel] 推送静态网站产物...",
            "[18:00:10] [SUCCESS] 平台 [vercel] 部署完成 -> 线上地址: https://test.vercel.app (耗时 3.88s)",
            "[18:00:10] [FINISH] 全域部署完成，总状态: SUCCESS，总耗时: 8.95s"
        ],
        "summary": {
            "total_channels": 2,
            "success_count": 2,
            "fail_count": 0,
            "channels": [
                {"id": "github_pages", "status": "success", "url": "https://test.github.io/repo/", "duration_sec": 4.12},
                {"id": "vercel", "status": "success", "url": "https://test.vercel.app", "duration_sec": 3.88}
            ]
        }
    }
    batch_id = record_global_deploy_batch(mock, "/tmp", deploy_results, duration_sec=8.95)
    assert batch_id is not None
    created = [b for b in mock.meta.batches if b.get("batch_id") == batch_id]
    assert len(created) == 1
    log = created[0]["logs_excerpt"]
    assert "[18:00:01] [INIT]" in log
    assert "[18:00:01] [BUNDLE]" in log
    assert "[18:00:06] [SUCCESS] 平台 [github_pages] 部署完成" in log
    assert "(耗时 4.12s)" in log
    assert "(耗时 3.88s)" in log
    assert "[18:00:10] [FINISH]" in log
    targets = created[0]["targets_json"]
    assert targets["github_pages"]["duration_sec"] == 4.12
    assert targets["vercel"]["duration_sec"] == 3.88


def test_trigger_hosting_deploy_from_vault_drawer(tmp_path):
    mock = singleton._GLOBAL_ENGINE
    bundle_dir = tmp_path / "mock_dist"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "showcase").mkdir(parents=True, exist_ok=True)
    (bundle_dir / "en" / "showcase").mkdir(parents=True, exist_ok=True)
    (bundle_dir / "showcase" / "multi-channel-syndication.html").write_text("<html>Chinese</html>", encoding="utf-8")
    (bundle_dir / "en" / "showcase" / "multi-channel-syndication.html").write_text("<html>English</html>", encoding="utf-8")
    
    # 模拟 engine 的输出路径指向该真实测试产物包
    mock.config.output_paths = {"site_dir": str(bundle_dir)}

    client = TestClient(app)
    resp = client.post(
        "/api/dispatch/hosting/deploy",
        json={
            "target_channels": ["github_pages", "vercel"],
            "trigger_source": "vault_drawer",
            "doc_id": "Showcase/multi-channel-syndication.md"
        },
        headers={"Authorization": "Bearer plenipes-dev-token"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "batch_id" in data
    created = [b for b in mock.meta.batches if b.get("batch_id") == data["batch_id"]]
    assert len(created) == 1
    assert created[0]["trigger_source"] == "vault_drawer:Showcase/multi-channel-syndication.md"
    # 真实扫描包含主语言和英文共 2 个页面
    assert created[0]["pages_count"] == 2
    assert created[0]["bundle_size_kb"] > 0
    assert "Showcase/multi-channel-syndication.md" in created[0]["logs_excerpt"]
    assert "[SOURCE] 触发原稿: [Showcase/multi-channel-syndication.md]" in created[0]["logs_excerpt"]
    targets = created[0]["targets_json"]
    assert targets.get("_trigger_doc") == "Showcase/multi-channel-syndication.md"
    assert "github_pages" in targets
    assert "vercel" in targets


