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
            "cloudflare_pages": {"enabled": True, "custom_domain": "docs.example.com"},
            "github_pages": {"enabled": True, "site_url": "https://example.github.io"}
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
        return self.batches

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
    assert len(data["fleet"]) == 11
    assert data["total_channels"] == 11
    assert data["ready_channels"] >= 1
    assert len(data["batches"]) == 1
    assert data["batches"][0]["batch_id"] == "deploy_test_001"


def test_trigger_hosting_deploy():
    client = TestClient(app)
    # 当 bundle_path 不存在时，端点会拦截并友好返回 400
    resp = client.post(
        "/api/dispatch/hosting/deploy",
        json={"target_channel": "cloudflare_pages", "trigger_source": "workbench"},
        headers={"Authorization": "Bearer plenipes-dev-token"}
    )
    # 静态发布包未构建时返回 400
    assert resp.status_code in (200, 400)
