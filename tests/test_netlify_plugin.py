#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V48.3] Netlify Publisher 插件测试
"""
import os
import sys
import tempfile
import json
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath('.'))


class TestNetlifyPublisher:
    """Netlify 发布插件单元测试"""

    def test_import_and_instantiate(self):
        """验证 NetlifyPublisher 可正常导入和实例化"""
        from adapters.egress.publishers.netlify import NetlifyPublisher
        pub = NetlifyPublisher(config={
            "enabled": True,
            "site_id": "site-123",
            "auth_token": "token-123",
            "prod": False,
            "message": "test msg",
            "netlify_path": "/usr/local/bin/netlify"
        })
        assert pub.PLUGIN_ID == "netlify"
        assert pub.site_id == "site-123"
        assert pub.auth_token == "token-123"
        assert pub.prod is False
        assert pub.message == "test msg"
        assert pub.netlify_path == "/usr/local/bin/netlify"
        assert pub.enabled is True

    def test_default_config_values(self):
        """验证默认配置值正确"""
        from adapters.egress.publishers.netlify import NetlifyPublisher
        pub = NetlifyPublisher(config={})
        assert pub.site_id == ""
        assert pub.auth_token == ""
        assert pub.prod is True
        assert pub.message == ""
        assert pub.netlify_path == "netlify"

    def test_push_skips_when_missing_config(self):
        """未配置 site_id 或 auth_token 时 push 应直接跳过"""
        from adapters.egress.publishers.netlify import NetlifyPublisher
        pub = NetlifyPublisher(config={})
        result = pub.push("/tmp/fake_bundle", {})
        assert result["status"] == "skipped"
        assert "site_id" in result["message"]

        pub_no_token = NetlifyPublisher(config={"site_id": "site-123"})
        result = pub_no_token.push("/tmp/fake_bundle", {})
        assert result["status"] == "skipped"
        assert "auth_token" in result["message"]

    def test_push_errors_when_bundle_missing(self):
        """bundle_path 不存在时 push 应返回 error"""
        from adapters.egress.publishers.netlify import NetlifyPublisher
        pub = NetlifyPublisher(config={
            "site_id": "site-123",
            "auth_token": "token-123"
        })
        result = pub.push("/nonexistent/path", {})
        assert result["status"] == "error"
        assert "does not exist" in result["message"]

    def test_validate_config(self):
        """验证配置校验逻辑"""
        from adapters.egress.publishers.netlify import NetlifyPublisher
        pub_invalid = NetlifyPublisher(config={})
        assert len(pub_invalid.validate_config()) == 2

        pub_valid = NetlifyPublisher(config={
            "site_id": "site-123",
            "auth_token": "token-123"
        })
        assert len(pub_valid.validate_config()) == 0

    def test_get_deploy_url(self):
        """验证部署 URL 推导"""
        from adapters.egress.publishers.netlify import NetlifyPublisher
        pub = NetlifyPublisher(config={"site_id": "site-123"})
        assert pub.get_deploy_url() == "https://site-123.netlify.app"

        pub_none = NetlifyPublisher(config={})
        assert pub_none.get_deploy_url() is None

    @patch("subprocess.run")
    def test_push_success_json(self, mock_run):
        """模拟部署成功的过程 (JSON 模式)"""
        from adapters.egress.publishers.netlify import NetlifyPublisher
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = json.dumps({
            "url": "https://site-123.netlify.app",
            "deploy_url": "https://deploy-123.netlify.app"
        })
        mock_res.stderr = ""
        mock_run.return_value = mock_res

        pub = NetlifyPublisher(config={
            "site_id": "site-123",
            "auth_token": "token-123",
            "message": "msg-{timestamp}"
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {"timestamp": 12345678})
            assert result["status"] == "success"
            assert result["site_id"] == "site-123"
            assert result["url"] == "https://site-123.netlify.app"
            assert result["deploy_url"] == "https://deploy-123.netlify.app"
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert "--json" in cmd
            assert "--message=msg-12345678" in cmd
            env = mock_run.call_args[1]["env"]
            assert env["NETLIFY_AUTH_TOKEN"] == "token-123"

    @patch("subprocess.run")
    def test_push_success_text(self, mock_run):
        """模拟部署成功的过程 (文本兜底模式)"""
        from adapters.egress.publishers.netlify import NetlifyPublisher
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = "Website URL: https://text-site.netlify.app\nUnique Deploy URL: https://text-deploy.netlify.app"
        mock_res.stderr = ""
        mock_run.return_value = mock_res

        pub = NetlifyPublisher(config={
            "site_id": "site-123",
            "auth_token": "token-123"
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert result["url"] == "https://text-site.netlify.app"
            assert result["deploy_url"] == "https://text-deploy.netlify.app"
