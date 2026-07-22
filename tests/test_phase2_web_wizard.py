#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Phase 2 Web Wizard Verification
职责：验证引导服务器 API 的连通性与逻辑正确性。
"""

import pytest
from fastapi.testclient import TestClient
from core.ui.web.wizard_server import app

client = TestClient(app)

def test_probe_endpoint():
    """验证算力探测接口"""
    response = client.get("/api/probe")
    assert response.status_code == 200
    data = response.json()
    assert "fingerprint" in data
    assert "nodes" in data
    assert isinstance(data["nodes"], list)

def test_static_access():
    """验证前端静态资源访问"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Illacme Plenipes" in response.text

def test_init_validation():
    """验证初始化接口的参数校验"""
    # 缺少参数
    response = client.post("/api/init", json={"press_name": "Test"})
    assert response.status_code == 422 # FastAPI 自动校验失败

def test_auth_callback_endpoint():
    """验证新增的 OAuth 本地回调接口"""
    response = client.get("/api/auth/callback?token=test_token_abc&provider=github&extra=test_repo_url")
    assert response.status_code == 200
    assert "test_token_abc" in response.text
    assert "github" in response.text
    assert "test_repo_url" in response.text
    assert "window.opener.postMessage" in response.text

def test_init_press_enable_ai_injection(tmp_path, monkeypatch):
    """验证向导初始化时 enable_ai 为 True 能成功写入配置字典"""
    monkeypatch.chdir(tmp_path)
    from services.wizard.wizard_ops_shards.init_ops import init_press_logic
    from services.wizard.wizard_server import InitRequest
    import yaml, os

    # 模拟输入请求
    req = InitRequest(
        imprint_id="test_ai_imp",
        imprint_name="Test AI Press",
        manuscripts_path=str(tmp_path),
        enable_ai=True,
        ai_provider="lmstudio",
        ai_model="qwen/qwen3.5-9b",
        ai_base_url="http://localhost:1234/v1"
    )
    init_press_logic(req)

    # 校验 config.local.yaml
    local_cfg_p = tmp_path / "config.local.yaml"
    assert local_cfg_p.exists()
    with open(local_cfg_p, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["translation"]["enable_ai"] is True
    assert data["translation"]["primary_node"] == "lmstudio_local"
    assert data["translation"]["primary_model"] == "qwen/qwen3.5-9b"
    assert data["translation"]["compute_nodes"]["lmstudio_local"]["enabled"] is True

if __name__ == "__main__":
    pytest.main([__file__])
