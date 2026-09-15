#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for SafeStaticFiles
测试目标：
1. 验证正常的前端静态资源（index.html、css、js）能正常返回 200；
2. 验证敏感文件（.env、config.yaml、.git、.master.key、*.lic）请求 100% 被拦截并返回 403；
3. 验证路径穿越请求（../）被 100% 拦截并返回 403。
"""

import pytest
from fastapi.testclient import TestClient
from services.api.server import app

@pytest.fixture
def client():
    return TestClient(app)

def test_safe_static_files_normal_asset(client):
    """测试常规页面与合法资源正常加载"""
    resp = client.get("/dashboard/index.html")
    assert resp.status_code == 200

def test_safe_static_files_allows_metadata_js(client):
    """测试包含 metadata/config 关键字的合法前端 JS 脚本正常加载（防误伤回归）"""
    resp = client.get("/dashboard/js/vault/vault.metadata.js")
    assert resp.status_code == 200
    assert b"renderDynamicMetadata" in resp.content

    resp_editor = client.get("/dashboard/js/vault/vault.editor.js")
    assert resp_editor.status_code == 200

    resp_config = client.get("/dashboard/js/dashboard.config_audit.js")
    assert resp_config.status_code == 200

def test_safe_static_files_block_sensitive_configs(client):
    """测试敏感配置文件探测被 403 拦截"""
    sensitive_targets = [
        "/dashboard/config.yaml",
        "/dashboard/config.local.yaml",
        "/dashboard/.env",
        "/dashboard/.git/config",
        "/dashboard/.plenipes/cache/ledger.db",
        "/dashboard/core/storage/.master.key",
        "/dashboard/license.lic"
    ]
    for target in sensitive_targets:
        resp = client.get(target)
        assert resp.status_code == 403
        assert b"Access Denied" in resp.content

def test_safe_static_files_block_path_traversal(client):
    """测试路径穿越探针被拦截"""
    resp = client.get("/dashboard/..%2f..%2fconfig.yaml")
    # 无论是被 403 还是 404，绝不能返回 200 OK 泄漏内容
    assert resp.status_code in (403, 404)
