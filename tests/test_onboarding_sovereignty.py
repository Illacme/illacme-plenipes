#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [V74.9] Onboarding Sovereignty Unit Test
职责：测试当 vault_root 为空或不存在时，治理层契约守护的降级警告自愈能力，以及主引擎的 Onboarding 状态属性。
"""
import tempfile
import pytest

from core.governance.contract_guard import ContractGuard

class MockConfig:
    def __init__(self, vault_root=""):
        self.vault_root = vault_root
        self.translation = type('MockTranslation', (), {'enable_ai': False})()
        self.config_path = "config.yaml"

def test_contract_guard_vault_root_missing():
    # 1. 测试 vault_root 为空
    cfg_empty = MockConfig(vault_root="")
    violations = ContractGuard.verify_config(cfg_empty)
    # 应该返回警告 (以 ⚠️ 开头) 且没有致命错误 (以 ❌ 开头)
    warnings = [v for v in violations if "⚠️" in v]
    errors = [v for v in violations if "❌" in v]
    assert len(warnings) > 0, "应该包含金库未就绪的警告"
    assert len(errors) == 0, "不应该包含致命错误"

    # 2. 测试 vault_root 路径不存在
    cfg_invalid = MockConfig(vault_root="/nonexistent/path/here")
    violations = ContractGuard.verify_config(cfg_invalid)
    warnings = [v for v in violations if "⚠️" in v]
    errors = [v for v in violations if "❌" in v]
    assert len(warnings) > 0, "应该包含物理路径不存在的警告"
    assert len(errors) == 0, "不应该包含致命错误"

    # 3. 测试正规存在的物理路径
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_valid = MockConfig(vault_root=tmpdir)
        violations = ContractGuard.verify_config(cfg_valid)
        warnings = [v for v in violations if "[原稿金库未就绪]" in v]
        assert len(warnings) == 0, "合法的物理路径不应该触发警告"

def test_ingress_sovereignty_routing():
    """🧪 测试输入端 Ingress 凭据与战略的物理双轨路由正确性"""
    from core.config.governance_map import resolve_governance_level
    # 1. 物理配置/密钥凭据路径 -> 物理本地 (local)
    assert resolve_governance_level("ingress_settings.source_options.notion.token") == "local"
    assert resolve_governance_level("ingress_settings.source_options.obsidian.vault_path") == "local"
    assert resolve_governance_level("ingress_settings.source_options.git.ssh_key") == "local"

    # 2. 战略策略/非机密属性 -> 品牌主权 (imprint)
    assert resolve_governance_level("ingress_settings.source_type") == "imprint"
    assert resolve_governance_level("ingress_settings.active_dialects") == "imprint"
    assert resolve_governance_level("ingress_settings.staticize_components") == "imprint"

@pytest.mark.anyio
async def test_dry_run_backend_engine():
    """🧪 测试物理沙盒出版干跑引擎的验证校验与流日志生成"""
    from services.api.routes.gov.context import dry_run_plugin
    from unittest.mock import patch, MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"posts": [], "data": {"name": "Test Writer"}, "username": "test_user"}

    with patch("requests.get", return_value=mock_resp):
        # 1. 测试凭据缺失情况
        payload_no_key = {
            "id": "medium",
            "settings": {
                "enabled": True,
                "url": "https://api.medium.com/v1"
            }
        }
        res_no_key = await dry_run_plugin(payload_no_key)
        assert res_no_key["success"] is False
        assert any("未配置 Medium 集成令牌" in log["message"] for log in res_no_key["logs"])

        # 2. 测试 URL 格式非法情况
        payload_bad_url = {
            "id": "ghost",
            "settings": {
                "enabled": True,
                "url": "api.ghost.org",
                "api_key": "valid_token_here"
            }
        }
        res_bad_url = await dry_run_plugin(payload_bad_url)
        assert res_bad_url["success"] is False
        assert any("物理端点 URL 格式不合法" in log["message"] for log in res_bad_url["logs"])

        # 3. 测试完全配置正确的成功场景
        payload_success = {
            "id": "ghost",
            "settings": {
                "enabled": True,
                "url": "https://api.ghost.org",
                "api_key": "valid_token_here"
            }
        }
        res_success = await dry_run_plugin(payload_success)
        assert res_success["success"] is True
        assert any("物理访问凭证及 API Key 校验通过" in log["message"] or "校验通过" in log["message"] or "验证成功" in log["message"] for log in res_success["logs"])

        # 4. 测试 WordPress 专属字段成功场景 (url, username, app_password)
        payload_wp = {
            "id": "wordpress",
            "settings": {
                "enabled": True,
                "url": "https://yoursite.com",
                "username": "admin",
                "app_password": "wp_app_pwd_here"
            }
        }
        res_wp = await dry_run_plugin(payload_wp)
        assert res_wp["success"] is True
        assert any("WordPress 账号与应用密码鉴权通过" in log["message"] for log in res_wp["logs"])

        # 5. 测试 Medium 专属字段成功场景 (integration_token)
        payload_medium = {
            "id": "medium",
            "settings": {
                "enabled": True,
                "integration_token": "medium_token_here"
            }
        }
        res_medium = await dry_run_plugin(payload_medium)
        assert res_medium["success"] is True
        assert any("Medium 凭证校验通过" in log["message"] for log in res_medium["logs"])



