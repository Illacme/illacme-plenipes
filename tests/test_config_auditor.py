# -*- coding: utf-8 -*-
"""
🧪 [Test] 三层配置层级安全继承与拓扑审计单元测试
"""
import sys
import os
import unittest
from fastapi.testclient import TestClient

# 将项目根目录加入 python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.api.server import app
from core.config.auditor import flatten_dict, audit_config_layers

class MockConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.imprint_id = "test_imprint"

class TestConfigAuditor(unittest.TestCase):
    def test_flatten_dict(self):
        """测试递归展平字典功能"""
        d = {
            "a": 1,
            "b": {
                "c": 2,
                "d": [3, {"e": 4}]
            }
        }
        flat = flatten_dict(d)
        self.assertEqual(flat.get("a"), 1)
        self.assertEqual(flat.get("b.c"), 2)
        self.assertEqual(flat.get("b.d.0"), 3)
        self.assertEqual(flat.get("b.d.1.e"), 4)

    def test_audit_config_layers(self):
        """测试审计决策与敏感值脱敏"""
        from unittest.mock import patch
        
        mock_layers = {
            "global": {
                "version": "V50.3",
                "system": {
                    "serve_port": 8080
                }
            },
            "local": {
                "system": {
                    "serve_port": 9090,
                    "api_token": "my-plain-token-1234567890"
                }
            },
            "imprint": {
                "imprint_name": "Test Brand",
                "vault_root": "/path/to/vault"
            }
        }
        
        with patch('core.config.auditor.load_raw_layers', return_value=mock_layers):
            mgr = MockConfigManager("config.yaml")
            report = audit_config_layers(mgr, imprint_id="test_imprint")
            
            items = {item["key"]: item for item in report["items"]}
            
            # 1. 验证常规 Local 覆盖 Global 生效
            serve_port_item = items.get("system.serve_port")
            self.assertIsNotNone(serve_port_item)
            self.assertEqual(serve_port_item["merged_val"], "9090")
            self.assertEqual(serve_port_item["source"], "local")
            
            # 2. 验证 Imprint 级别生效 (imprint_name 是 imprint 级)
            name_item = items.get("imprint_name")
            self.assertIsNotNone(name_item)
            self.assertEqual(name_item["merged_val"], "Test Brand")
            self.assertEqual(name_item["source"], "imprint")
            
            # 3. 验证明文密钥安全检测与 mask_plain_value 遮蔽脱敏
            token_item = items.get("system.api_token")
            self.assertIsNotNone(token_item)
            self.assertEqual(token_item["security_status"], "cleartext")
            self.assertIn("****", token_item["merged_val"])
            self.assertNotIn("1234567890", token_item["merged_val"])
            
            # 4. 验证统计结果
            self.assertEqual(report["summary"]["cleartext_issues"], 1)
            self.assertTrue(report["summary"]["has_warnings"])

    def test_api_config_audit(self):
        """测试 /api/config/audit API 路由可用性"""
        client = TestClient(app)
        from unittest.mock import patch
        mock_report = {
            "imprint_id": "default",
            "items": [],
            "summary": {
                "total_keys": 0,
                "cleartext_issues": 0,
                "has_warnings": False
            }
        }
        
        with patch('core.config.auditor.audit_config_layers', return_value=mock_report):
            response = client.get("/api/config/audit?imprint_id=default")
            self.assertNotEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
