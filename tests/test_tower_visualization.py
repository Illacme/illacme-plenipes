#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [Test] 总编室控制塔可视化面板 RESTful API 单元测试
职责：全面覆盖 /api/governance/pulse 端点的可访问性、身份验证拦截与 JSON 脉搏数据格式完整性。
"""

import sys
import os
import tempfile
import json
from fastapi.testclient import TestClient

# 将项目根目录加入 python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.api.server import app

class MockSystemConfig:
    def __init__(self):
        self.api_token = None  # 初始无 token，便于测试免密

class MockConfig:
    def __init__(self, pulse_path: str):
        self.system = MockSystemConfig()
        self._pulse_path = pulse_path

    def get_pulse_path(self) -> str:
        return self._pulse_path

class MockEngine:
    def __init__(self, pulse_path: str):
        self.config = MockConfig(pulse_path)

    def _resolve_path(self, path: str) -> str:
        # 简单直接返回，避开复杂的路径对齐
        return path

def test_pulse_api_flow():
    print("🧪 [Test] 启动控制塔可视化 Pulse 遥测 API 单元测试...")

    with tempfile.TemporaryDirectory() as temp_dir:
        # 建立测试用 pulse json 物理文件
        test_pulse_file = os.path.join(temp_dir, "pulse_universal.json")
        
        # 模拟心跳服务聚合的遥测数据
        mock_telemetry_data = {
            "version": "V24.0",
            "timestamp": "2026-06-05T22:00:00.000000",
            "uptime": 120,
            "status": "RUNNING",
            "progress": {
                "current": 10,
                "total": 100,
                "percentage": 10.0
            },
            "pools": {
                "global": {
                    "queue_size": 2,
                    "max_workers": 4,
                    "active_workers": 1
                },
                "ai": {
                    "queue_size": 0,
                    "max_workers": 2,
                    "active_workers": 0
                },
                "asset": {
                    "queue_size": 1,
                    "max_workers": 2,
                    "active_workers": 2
                },
                "total_queue": 3
            },
            "load": {
                "cpu_percent": 25.5,
                "memory_percent": 60.1
            },
            "usage": {
                "tokens": 10500,
                "cost": 0.0525
            }
        }
        
        # 写入物理磁盘文件
        with open(test_pulse_file, 'w', encoding='utf-8') as f:
            json.dump(mock_telemetry_data, f)

        # 实例化 Mock 引擎并注入单例
        mock_engine = MockEngine(test_pulse_file)
        
        import core.runtime.engine_singleton as singleton
        original_engine = singleton.get_global_engine()
        singleton.set_global_engine(mock_engine)
        
        client = TestClient(app)
        
        try:
            # 1. 正常免密场景：直接请求 pulse 数据
            res = client.get("/api/governance/pulse")
            assert res.status_code == 200, f"API 返回非 200: {res.status_code}"
            
            data = res.json()
            assert data.get("version") == "V24.0", "Pulse 版本校验失败"
            assert data.get("status") == "RUNNING", "运行状态校验失败"
            assert data["progress"]["percentage"] == 10.0, "进度校验失败"
            assert data["pools"]["global"]["queue_size"] == 2, "全局池队列校验失败"
            assert data["load"]["cpu_percent"] == 25.5, "CPU 负载校验失败"
            assert data["usage"]["cost"] == 0.0525, "Token 累计成本校验失败"
            print("  ✅ [测试] 免密场景下脉搏 JSON 数据格式及完整性校验 100% 通过！")
            
            # 2. 身份验证：设置 api_token 开启拦截
            mock_engine.config.system.api_token = "secure-tower-secret"
            
            # 2.1 拦截测试：不带 X-Token 请求
            res_forbidden = client.get("/api/governance/pulse")
            assert res_forbidden.status_code == 403, "未授权请求未被成功拦截"
            assert res_forbidden.json().get("detail") == "Unauthorized", "未授权报错信息不符"
            
            # 2.2 拦截测试：带有错误 X-Token 请求
            res_bad_token = client.get("/api/governance/pulse", headers={"X-Token": "wrong-secret"})
            assert res_bad_token.status_code == 403, "错误 Token 未被成功拦截"
            
            # 2.3 放行测试：带有正确 X-Token 请求
            res_authorized = client.get("/api/governance/pulse", headers={"X-Token": "secure-tower-secret"})
            assert res_authorized.status_code == 200, "合法 Token 遭遇误报拦截"
            
            data_auth = res_authorized.json()
            assert data_auth.get("version") == "V24.0", "认证后数据响应损坏"
            print("  ✅ [测试] 物理主权 API 访问令牌校验与边界防御拦截完美通过！")
            
        finally:
            # 恢复单例原物
            singleton.set_global_engine(original_engine)

if __name__ == "__main__":
    test_pulse_api_flow()
