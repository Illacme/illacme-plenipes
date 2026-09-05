#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试：原稿文库路径已有品牌绑定检测接口与逻辑验证
验证 /api/imprints/check-vault 在输入相对路径、绝对路径及全新未绑定路径时的精准感知能力。
"""

import os
import pytest
from fastapi.testclient import TestClient
from services.api.server import app
from core.governance.imprint_manager import im

@pytest.fixture
def client():
    return TestClient(app)

def test_check_vault_binding_for_default_brand(client):
    """验证检测系统默认文库路径能够正确识别出绑定的品牌"""
    # 相对路径 ./vault
    res_rel = client.get("/api/imprints/check-vault?path=./vault")
    assert res_rel.status_code == 200
    data_rel = res_rel.json()
    assert data_rel["bound"] is True
    assert any(imp["id"] == "default" for imp in data_rel["imprints"])

    # 绝对物理路径
    abs_vault = os.path.abspath("./vault")
    res_abs = client.get(f"/api/imprints/check-vault?path={abs_vault}")
    assert res_abs.status_code == 200
    data_abs = res_abs.json()
    assert data_abs["bound"] is True
    assert any(imp["id"] == "default" for imp in data_abs["imprints"])

def test_check_vault_binding_for_unbound_path(client):
    """验证全新未绑定的文库路径返回 bound=False"""
    unbound_path = "/tmp/test_completely_unbound_vault_12345"
    res = client.get(f"/api/imprints/check-vault?path={unbound_path}")
    assert res.status_code == 200
    data = res.json()
    assert data["bound"] is False
    assert len(data["imprints"]) == 0

def test_check_vault_binding_for_empty_path(client):
    """验证空路径或空白路径返回 bound=False"""
    res = client.get("/api/imprints/check-vault?path=")
    assert res.status_code == 200
    data = res.json()
    assert data["bound"] is False
    assert len(data["imprints"]) == 0
