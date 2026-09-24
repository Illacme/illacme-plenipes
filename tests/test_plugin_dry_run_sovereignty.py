# -*- coding: utf-8 -*-
"""
🛡️ [V74.92] Test Suite for Plugin Dry Run Sovereignty & Sandbox Defense
验证 plugin_dry_run.py 的类型防御解包 (Rule 8) 与原始异常透传 (Rule 16)。
"""

import asyncio
from unittest.mock import patch, MagicMock
from services.api.routes.gov.context_shards.plugin_dry_run import dry_run_plugin_impl


def test_dry_run_dirty_payload_sandbox_defense():
    """验证非法、空值或畸形 payload 时的沙箱防御，确保 0 崩溃且返回友好错误。"""
    # 1. payload 为 None
    res = asyncio.run(dry_run_plugin_impl(None))
    assert isinstance(res, dict)
    assert res.get("success") is False
    assert any("Plugin ID is required" in log.get("message", "") or "缺少有效的插件标识" in log.get("message", "") for log in res.get("logs", []))

    # 2. payload 为非字典类型
    res = asyncio.run(dry_run_plugin_impl("invalid_string_payload"))
    assert isinstance(res, dict)
    assert res.get("success") is False

    # 3. settings 为 None 或非字典
    res = asyncio.run(dry_run_plugin_impl({"id": "custom_webhook", "settings": None}))
    assert isinstance(res, dict)
    assert res.get("success") is False

    # 4. settings 包含占位符
    res = asyncio.run(dry_run_plugin_impl({"id": "custom_webhook", "settings": {"url": "https://example.com", "token": "your_token_here"}}))
    assert isinstance(res, dict)
    assert res.get("success") is False
    assert any("占位符" in log.get("message", "") for log in res.get("logs", []))


def test_dry_run_raw_exception_transparency_http_error():
    """验证当分片抛出 HTTP 异常时，真实状态码与错误现场无损透传至 logs (Rule 16)。"""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = '{"error": "Too Many Requests, rate limit exceeded"}'
    
    import requests
    http_err = requests.exceptions.HTTPError("429 Client Error", response=mock_resp)

    with patch("services.api.routes.gov.context_shards.plugin_dry_run_social.run_social_plugin_dry_run", side_effect=http_err):
        res = asyncio.run(dry_run_plugin_impl({
            "id": "zhihu",
            "settings": {"token": "valid_token", "column_id": "test_col"}
        }))
        assert isinstance(res, dict)
        assert res.get("success") is False
        logs = res.get("logs", [])
        
        # 断言错误日志中穿透了 HTTP 状态码 429 和原始异常现场
        err_logs = [l.get("message", "") for l in logs if l.get("level") == "ERROR"]
        assert any("429" in msg for msg in err_logs)
        assert any("HTTPError" in msg or "HTTP 状态码: 429" in msg for msg in err_logs)
        assert any("Too Many Requests" in msg for msg in err_logs)


def test_dry_run_ai_protocol_connectivity_and_error():
    """验证 AI Protocol 的正常连通与异常透传。"""
    # 模拟连通成功
    with patch("core.logic.diagnostics.component_monitor.ComponentMonitor.validate_ai_connectivity") as mock_val:
        mock_val.return_value = {"status": "success", "message": "OK", "models": ["gpt-4o", "claude-3-5"]}
        res = asyncio.run(dry_run_plugin_impl({
            "id": "openai",
            "settings": {"api_key": "test-mock-api-key-safe", "base_url": "https://api.openai.com/v1"}
        }))
        assert res.get("success") is True
        logs_text = " ".join(l.get("message", "") for l in res.get("logs", []))
        assert "已探测到模型资产: gpt-4o, claude-3-5" in logs_text

    # 模拟对端返回 HTTP 503 业务错误
    with patch("core.logic.diagnostics.component_monitor.ComponentMonitor.validate_ai_connectivity") as mock_val:
        mock_val.return_value = {"status": "error", "message": "No capacity available", "status_code": 503}
        res = asyncio.run(dry_run_plugin_impl({
            "id": "openai",
            "settings": {"api_key": "test-mock-api-key-safe", "base_url": "https://api.openai.com/v1"}
        }))
        assert res.get("success") is False
        logs_text = " ".join(l.get("message", "") for l in res.get("logs", []))
        assert "HTTP 503" in logs_text
        assert "No capacity available" in logs_text


def test_dry_run_tunnel_probe_and_exception_handling():
    """验证 Tunnel 穿透探针的健康与异常沙箱。"""
    # 模拟未知 ID
    res = asyncio.run(dry_run_plugin_impl({"id": "non_existent_tunnel", "parentId": "tunnel"}))
    assert res.get("success") is False
    assert any("穿透驱动注册表中未发现" in l.get("message", "") for l in res.get("logs", []))

    # 模拟探针抛出异常时沙箱防御与透传
    mock_adapter = MagicMock()
    mock_adapter.DISPLAY_NAME = "MockTunnel"
    mock_adapter.probe.side_effect = RuntimeError("SSH agent unreachable")
    with patch("core.adapters.tunnel.TunnelRegistry.get", return_value=MagicMock(return_value=mock_adapter)):
        res = asyncio.run(dry_run_plugin_impl({"id": "localhost_run", "parentId": "tunnel"}))
        assert res.get("success") is False
        logs_text = " ".join(l.get("message", "") for l in res.get("logs", []))
        assert "SSH agent unreachable" in logs_text


def test_dry_run_notice_business_error_code_transparency():
    """验证钉钉/飞书在 HTTP 200 下返回非 0 业务错误码时的透传与失败标记。"""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"code": 19001, "msg": "sign match fail or timestamp is invalid"}

    with patch("requests.post", return_value=mock_resp):
        res = asyncio.run(dry_run_plugin_impl({
            "id": "feishu",
            "settings": {"url": "https://open.feishu.cn/open-apis/bot/v2/hook/test-token", "secret": "bad-secret"}
        }))
        assert res.get("success") is False
        logs_text = " ".join(l.get("message", "") for l in res.get("logs", []))
        assert "19001" in logs_text
        assert "sign match fail" in logs_text


def test_dry_run_hosting_shard_exception_transparency():
    """验证全站托管插件（如 GitHub Pages）在异常时的透传。"""
    import requests
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.text = "Resource not accessible by personal access token"
    http_err = requests.exceptions.HTTPError("403 Forbidden", response=mock_resp)

    with patch("services.api.routes.gov.context_shards.plugin_dry_run_hosting.run_hosting_plugin_dry_run", side_effect=http_err):
        res = asyncio.run(dry_run_plugin_impl({
            "id": "github_pages",
            "settings": {"token": "ghp_invalid", "repo": "user/repo"}
        }))
        assert res.get("success") is False
        logs = res.get("logs", [])
        err_logs = [l.get("message", "") for l in logs if l.get("level") == "ERROR"]
        assert any("403" in msg for msg in err_logs)
        assert any("Resource not accessible" in msg for msg in err_logs)
