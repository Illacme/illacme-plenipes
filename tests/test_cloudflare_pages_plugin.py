#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V48.3] Cloudflare Pages Publisher 插件测试
"""
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath('.'))


class TestCloudflarePagesPublisher:
    """Cloudflare Pages 发布插件单元测试"""

    def test_import_and_instantiate(self):
        """验证 CloudflarePagesPublisher 可正常导入和实例化"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        pub = CloudflarePagesPublisher(config={
            "enabled": True,
            "project_name": "my-docs-site",
            "branch": "production",
            "account_id": "acc-123",
            "wrangler_path": "/usr/local/bin/wrangler"
        })
        assert pub.PLUGIN_ID == "cloudflare_pages"
        assert pub.project_name == "my-docs-site"
        assert pub.branch == "production"
        assert pub.account_id == "acc-123"
        assert pub.wrangler_path == "/usr/local/bin/wrangler"
        assert pub.enabled is True

    def test_default_config_values(self):
        """验证默认配置值正确"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        pub = CloudflarePagesPublisher(config={})
        assert pub.project_name == ""
        assert pub.branch == "production"
        assert pub.account_id == ""
        assert pub.wrangler_path == "wrangler"

    def test_push_skips_when_no_project_name(self):
        """未配置 project_name 时 push 应直接跳过"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        pub = CloudflarePagesPublisher(config={})
        result = pub.push("/tmp/fake_bundle", {})
        assert result["status"] == "skipped"
        assert "project_name" in result["message"]

    def test_push_errors_when_bundle_missing(self):
        """bundle_path 不存在时 push 应返回 error"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        pub = CloudflarePagesPublisher(config={
            "project_name": "my-site"
        })
        result = pub.push("/nonexistent/path", {})
        assert result["status"] == "error"
        assert "does not exist" in result["message"]

    def test_validate_config(self):
        """验证配置校验逻辑"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        pub_invalid = CloudflarePagesPublisher(config={})
        assert len(pub_invalid.validate_config()) > 0

        pub_valid = CloudflarePagesPublisher(config={"project_name": "my-site"})
        assert len(pub_valid.validate_config()) == 0

    def test_get_deploy_url(self):
        """验证部署 URL 推导"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        pub = CloudflarePagesPublisher(config={"project_name": "my-site"})
        assert pub.get_deploy_url() == "https://my-site.pages.dev"

        pub_none = CloudflarePagesPublisher(config={})
        assert pub_none.get_deploy_url() is None

    @patch("subprocess.run")
    def test_push_success(self, mock_run):
        """模拟部署成功的过程"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = "✨ Success! Uploaded 12 files\nDeployment URL: https://my-site.pages.dev\n"
        mock_res.stderr = ""
        mock_run.return_value = mock_res

        pub = CloudflarePagesPublisher(config={
            "project_name": "my-site",
            "account_id": "acc-123"
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert result["project"] == "my-site"
            assert result["url"] == "https://my-site.pages.dev"
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert "pages" in cmd
            assert "deploy" in cmd
            assert "--account-id" in cmd
            assert "acc-123" in cmd

    @patch("subprocess.run")
    def test_push_failure(self, mock_run):
        """模拟部署失败的过程"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        mock_res = MagicMock()
        mock_res.returncode = 1
        mock_res.stdout = ""
        mock_res.stderr = "Authentication Error"
        mock_run.return_value = mock_res

        pub = CloudflarePagesPublisher(config={
            "project_name": "my-site"
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {})
            assert result["status"] == "error"
            assert "Authentication Error" in result["message"]
