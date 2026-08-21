# -*- coding: utf-8 -*-
"""
tests/test_reactive_security.py
🛡️ [V75.9] 动态实时安全警报器测试
验证当发生接口认证越权、功能准入受限、资源物理过载等安全事件时，系统能够通过事件总线实时、白盒化地发射警报。
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from core.utils.event_bus import bus
from core.governance.license_guard import LicenseGuard
from services.api.routes.system import verify_token
from core.governance.resource_guard import ResourceGuard

def test_token_verification_failure_emits_security_alert():
    """测试 API Token 校验失败时成功向事件总线广播 SECURITY_ALERT 事件"""
    alerts = []
    
    @bus.on("SECURITY_ALERT")
    def _on_alert(category, message, **kwargs):
        alerts.append((category, message))
        
    mock_engine = MagicMock()
    mock_engine.config.system.api_token = "correct-token"
    
    with patch("services.api.routes.system.get_global_engine", return_value=mock_engine):
        with pytest.raises(HTTPException) as excinfo:
            verify_token(x_token="wrong-token")
            
        assert excinfo.value.status_code == 403
        assert len(alerts) == 1
        assert alerts[0][0] == "API_TOKEN_EXPIRED"
        assert "接口访问认证失败" in alerts[0][1]

def test_license_guard_interception_emits_security_alert():
    """测试功能准入拦截时成功向事件总线广播 SECURITY_ALERT 事件"""
    alerts = []
    
    @bus.on("SECURITY_ALERT")
    def _on_alert(category, message, **kwargs):
        alerts.append((category, message))
        
    # 模拟未激活授权版且切换至自定义品牌 (清空全局警告缓存以避免测试污染)
    LicenseGuard._warned_features.clear()
    from core.governance.imprint_manager import im
    old_imp = im.active_imprint
    try:
        im.active_imprint = "custom_press"
        with patch.object(LicenseGuard, "is_licensed", return_value=False):
            # 拦截多语言矩阵功能调用
            allowed = LicenseGuard.is_pro_feature_allowed("multi_language")
            
            assert allowed is False
            assert len(alerts) == 1
            assert alerts[0][0] == "LICENSE_LIMIT"
            assert "系统已拦截对未授权专业版功能" in alerts[0][1]
    finally:
        im.active_imprint = old_imp

def test_resource_guard_overload_emits_throttle_event():
    """测试物理过载紧急削峰和负载恢复时能够发射 UI_RESOURCE_THROTTLE 事件"""
    throttles = []
    
    @bus.on("UI_RESOURCE_THROTTLE")
    def _on_throttle(active, cpu=None, ram=None, **kwargs):
        throttles.append((active, cpu, ram))
        
    mock_engine = MagicMock()
    mock_engine.config.system.concurrency.global_workers = 4
    mock_engine.config.system.concurrency.ai_workers = 4
    
    guard = ResourceGuard(mock_engine)
    guard.original_concurrency = {"global": 4, "ai": 4}
    
    # 模拟执行紧急削峰
    with patch("core.logic.orchestration.task_orchestrator.global_executor.update_concurrency") as mock_global_update, \
         patch("core.logic.orchestration.task_orchestrator.ai_executor.update_concurrency") as mock_ai_update, \
         patch("core.logic.orchestration.task_orchestrator.global_executor.get_stats", return_value={"queue_size": 1, "active_workers": 1}):
         
         guard._apply_throttle(cpu=95.0, ram=88.0, compute_ram=25.0)
         
         assert len(throttles) == 1
         assert throttles[0] == (True, 95.0, 88.0)
         assert guard.is_throttled is True
         
         # 模拟负载回落恢复满血
         guard._release_throttle()
         
         assert len(throttles) == 2
         assert throttles[1] == (False, None, None)
         assert guard.is_throttled is False
