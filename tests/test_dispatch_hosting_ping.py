#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [V125.1] Tests for Hosting Channel Connectivity Ping API
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
            "cloudflare_pages": {
                "enabled": True,
                "project_name": "my-cf-site",
                "token": "valid_cf_token",
                "account_id": "cf_acc_123"
            },
            "github_pages": {
                "enabled": True,
                "repo_url": "https://github.com/myorg/myrepo.git",
                "token": "ghp_validtoken"
            },
            "netlify": {
                "enabled": True,
                "site_id": "net-site-123",
                "token": "net_tok_xyz"
            }
        }


class MockEngine:
    def __init__(self):
        self.config = MockConfig()
        self.vault_root = "/tmp"


@pytest.fixture(autouse=True)
def setup_engine(monkeypatch):
    mock = MockEngine()
    monkeypatch.setattr(singleton, "_GLOBAL_ENGINE", mock)
    yield


def test_ping_missing_channel():
    client = TestClient(app)
    resp = client.post(
        "/api/dispatch/hosting/ping",
        json={"channel": ""},
        headers={"Authorization": "Bearer plenipes-dev-token"}
    )
    assert resp.status_code == 400


def test_ping_github_pages_success(monkeypatch):
    client = TestClient(app)

    def mock_dry_run(plugin_id, settings, logs, log_fn):
        log_fn("INFO", "📡 [探测] 正在校验 GitHub Token 访问令牌有效性...")
        log_fn("SUCCESS", "🟢 [成功] GitHub Token 鉴权有效，识别当前用户身份: 'octocat'。")
        return True

    monkeypatch.setattr(
        "services.api.routes.dispatch_shards.hosting_diagnostic_routes.run_hosting_plugin_dry_run",
        mock_dry_run
    )

    resp = client.post(
        "/api/dispatch/hosting/ping",
        json={"channel": "github_pages"},
        headers={"Authorization": "Bearer plenipes-dev-token"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["channel"] == "github_pages"
    assert data["healthy"] is True
    assert data["latency_ms"] >= 1
    assert "octocat" in data["identity"]
    assert "GitHub Token" in data["summary"]
    assert len(data["logs"]) >= 2


def test_ping_cloudflare_pages_failed(monkeypatch):
    client = TestClient(app)

    def mock_dry_run(plugin_id, settings, logs, log_fn):
        log_fn("INFO", "📡 [探测] 正在连接 Cloudflare API 校验项目...")
        log_fn("ERROR", "❌ [错误] Cloudflare 拒绝连接：API Token 无效或权限不足。")
        return False

    monkeypatch.setattr(
        "services.api.routes.dispatch_shards.hosting_diagnostic_routes.run_hosting_plugin_dry_run",
        mock_dry_run
    )

    resp = client.post(
        "/api/dispatch/hosting/ping",
        json={"channel": "cloudflare_pages"},
        headers={"Authorization": "Bearer plenipes-dev-token"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["channel"] == "cloudflare_pages"
    assert data["healthy"] is False
    assert "拒绝连接" in data["summary"]


def test_ping_with_settings_override(monkeypatch):
    client = TestClient(app)
    received_settings = {}

    def mock_dry_run(plugin_id, settings, logs, log_fn):
        nonlocal received_settings
        received_settings = settings
        log_fn("SUCCESS", "🟢 [成功] 临时测试凭证校验通过。")
        return True

    monkeypatch.setattr(
        "services.api.routes.dispatch_shards.hosting_diagnostic_routes.run_hosting_plugin_dry_run",
        mock_dry_run
    )

    resp = client.post(
        "/api/dispatch/hosting/ping",
        json={
            "channel": "netlify",
            "settings_override": {"token": "override_token_test"}
        },
        headers={"Authorization": "Bearer plenipes-dev-token"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["healthy"] is True
    assert received_settings.get("token") == "override_token_test"


def test_get_hosting_batch_detail_success(monkeypatch):
    client = TestClient(app)
    mock_batch = {
        "batch_id": "deploy_test_123",
        "theme": "sovereign",
        "pages_count": 121,
        "bundle_size_kb": 7039.0,
        "overall_status": "SUCCESS",
        "started_at": "2026-10-08 11:39:13",
        "completed_at": "2026-10-08 11:39:27",
        "duration_sec": 14.2,
        "targets": {
            "github_pages": {"status": "SUCCESS", "url": "https://test.github.io/site/", "deployed_at": "2026-10-08 11:39:20"}
        },
        "logs_excerpt": ""
    }

    class MockMeta:
        def get_hosting_deploy_batch(self, batch_id):
            if batch_id == "deploy_test_123":
                return dict(mock_batch)
            return None

    mock_engine = singleton._GLOBAL_ENGINE
    mock_engine.meta = MockMeta()

    resp = client.get(
        "/api/dispatch/hosting/batch/deploy_test_123",
        headers={"Authorization": "Bearer plenipes-dev-token"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    batch = data["batch"]
    assert batch["batch_id"] == "deploy_test_123"
    assert "github_pages" in batch["targets"]
    assert "[SUCCESS] 平台 [github_pages]" in batch["logs_excerpt"]


def test_get_hosting_batch_detail_not_found():
    client = TestClient(app)
    resp = client.get(
        "/api/dispatch/hosting/batch/deploy_non_existent",
        headers={"Authorization": "Bearer plenipes-dev-token"}
    )
    assert resp.status_code == 404

