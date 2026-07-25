# -*- coding: utf-8 -*-
"""
⚙️ Health Check API Contract Test — 校验全站健康检查接口响应强契约规范。
"""

from fastapi.testclient import TestClient
from services.api.server import app
from services.api.schemas import HealthCheckResponse, SystemHealthResponse, HealthMatrixResponse

client = TestClient(app)

def test_liveness_health_contract():
    """验证 GET /health 接口强契约格式与字段"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    # 校验 Pydantic 解析是否正常
    health_obj = HealthCheckResponse(**data)
    assert health_obj.status == "ok"
    assert health_obj.engine == "Illacme-plenipes"
    assert "active_imprint" not in data  # 强契约断言：已彻底移除 active_imprint
    assert "imprint" in data
    assert isinstance(health_obj.timestamp, float)

def test_system_health_contract():
    """验证 GET /api/system/health 接口强契约格式与字典对象数据类型"""
    response = client.get("/api/system/health")
    assert response.status_code == 200
    data = response.json()
    
    health_obj = SystemHealthResponse(**data)
    assert health_obj.status in ["online", "starting", "degraded", "error"]
    assert health_obj.engine == "Illacme-plenipes"
    assert isinstance(health_obj.services, dict)  # 强契约断言：services 必须为 Dict 类型而非 str
    assert isinstance(health_obj.timestamp, float)

def test_health_matrix_contract():
    """验证 GET /api/system/health/matrix 接口强契约与统一数据模型"""
    response = client.get("/api/system/health/matrix")
    assert response.status_code == 200
    data = response.json()
    
    matrix_obj = HealthMatrixResponse(**data)
    assert matrix_obj.engine.status in ["online", "starting", "offline"]
    assert matrix_obj.onboarding.status in ["active", "standby", "offline"]
    assert matrix_obj.preview.status in ["online", "running", "offline"]
    assert 0 <= matrix_obj.engine.health <= 100
