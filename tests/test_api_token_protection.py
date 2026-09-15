#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for API Gateway Token Protection
测试目标：
1. 本地回环 (127.0.0.1 / testclient) 在未配置 Token 时免密放行，保证创作者本地出版零摩擦；
2. 跨网络/非本地回环在未配 Token 时强制 401 拦截；
3. 配置 system.api_token 后，未携带或携带错误 Token 强制 401 拦截，携带正确 X-Token 或 ?token= 正常放行；
4. 验证 /api/agent/model_info 同样受到守卫保护。
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from services.api.server import app
from core.runtime.engine_singleton import set_global_engine

@pytest.fixture
def mock_engine():
    engine = MagicMock()
    engine.config = MagicMock()
    engine.config.system = MagicMock()
    engine.config.system.api_token = None
    engine.config.system.strict_security = False
    engine.config.translation = MagicMock()
    engine.config.translation.enable_ai = False
    engine.translator = None
    engine.no_ai = True
    set_global_engine(engine)
    return engine


def test_localhost_unauthenticated_allowed(mock_engine):
    """测试本地客户端在未配 Token 时免密放行"""
    mock_engine.config.system.api_token = None
    client = TestClient(app)
    # TestClient 默认 host 为 testclient，属于本地白名单
    resp = client.get("/api/agent/model_info")
    assert resp.status_code == 200

def test_non_localhost_blocked_without_token(mock_engine):
    """测试非本地回环客户端在未配 Token 时被 401 拦截"""
    mock_engine.config.system.api_token = None
    client = TestClient(app, client=("192.168.1.105", 54321))
    resp = client.get("/api/agent/model_info")
    assert resp.status_code == 401
    assert "requires system.api_token" in resp.json()["detail"]

def test_token_configured_requires_matching_token(mock_engine):
    """测试配置了 api_token 后的认证流程"""
    mock_engine.config.system.api_token = "SOVEREIGN_SECRET_TOKEN_123"
    client = TestClient(app)
    
    # 1. 未携带 Token
    resp_no_token = client.get("/api/agent/model_info")
    assert resp_no_token.status_code == 401
    
    # 2. 携带错误 Token
    resp_bad_token = client.get("/api/agent/model_info", headers={"X-Token": "WRONG_TOKEN"})
    assert resp_bad_token.status_code == 401
    
    # 3. 携带正确 Header X-Token
    resp_ok = client.get("/api/agent/model_info", headers={"X-Token": "SOVEREIGN_SECRET_TOKEN_123"})
    assert resp_ok.status_code == 200
    
    # 4. 携带正确 Query Param ?token=
    resp_query = client.get("/api/agent/model_info?token=SOVEREIGN_SECRET_TOKEN_123")
    assert resp_query.status_code == 200

def test_strict_security_forces_token_even_on_localhost(mock_engine):
    """测试开启 strict_security 时本地回环也强制要求 Token"""
    mock_engine.config.system.api_token = None
    mock_engine.config.system.strict_security = True
    client = TestClient(app)
    resp = client.get("/api/agent/model_info")
    assert resp.status_code == 401
