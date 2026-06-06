#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V48.3] Vercel Publisher 插件测试
"""
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath('.'))


class TestVercelPublisher:
    """Vercel 发布插件单元测试"""

    def test_import_and_instantiate(self):
        """验证 VercelPublisher 可正常导入和实例化"""
        from adapters.egress.publishers.vercel import VercelPublisher
        pub = VercelPublisher(config={
            "enabled": True,
            "token": "token-123",
            "project_name": "my-vercel-site",
            "org_id": "org-123",
            "prod": False,
            "vercel_path": "/usr/local/bin/vercel"
        })
        assert pub.PLUGIN_ID == "vercel"
        assert pub.token == "token-123"
        assert pub.project_name == "my-vercel-site"
        assert pub.org_id == "org-123"
        assert pub.prod is False
        assert pub.vercel_path == "/usr/local/bin/vercel"
        assert pub.enabled is True

    def test_default_config_values(self):
        """验证默认配置值正确"""
        from adapters.egress.publishers.vercel import VercelPublisher
        pub = VercelPublisher(config={})
        assert pub.token == ""
        assert pub.project_name == ""
        assert pub.org_id == ""
        assert pub.prod is True
        assert pub.vercel_path == "vercel"

    def test_push_skips_when_no_token(self):
        """未配置 token 时 push 应直接跳过"""
        from adapters.egress.publishers.vercel import VercelPublisher
        pub = VercelPublisher(config={})
        result = pub.push("/tmp/fake_bundle", {})
        assert result["status"] == "skipped"
        assert "token" in result["message"]

    def test_push_errors_when_bundle_missing(self):
        """bundle_path 不存在时 push 应返回 error"""
        from adapters.egress.publishers.vercel import VercelPublisher
        pub = VercelPublisher(config={
            "token": "token-123"
        })
        result = pub.push("/nonexistent/path", {})
        assert result["status"] == "error"
        assert "does not exist" in result["message"]

    def test_validate_config(self):
        """验证配置校验逻辑"""
        from adapters.egress.publishers.vercel import VercelPublisher
        pub_invalid = VercelPublisher(config={})
        assert len(pub_invalid.validate_config()) == 1

        pub_valid = VercelPublisher(config={"token": "token-123"})
        assert len(pub_valid.validate_config()) == 0

    def test_get_deploy_url(self):
        """验证部署 URL 推导"""
        from adapters.egress.publishers.vercel import VercelPublisher
        pub = VercelPublisher(config={"project_name": "my-site"})
        assert pub.get_deploy_url() == "https://my-site.vercel.app"

        pub_none = VercelPublisher(config={})
        assert pub_none.get_deploy_url() is None

    @patch("subprocess.run")
    def test_push_success(self, mock_run):
        """模拟部署成功的过程"""
        from adapters.egress.publishers.vercel import VercelPublisher
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = "https://my-site.vercel.app\n"
        mock_res.stderr = ""
        mock_run.return_value = mock_res

        pub = VercelPublisher(config={
            "token": "token-123",
            "project_name": "my-site",
            "org_id": "org-123"
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert result["project"] == "my-site"
            assert result["url"] == "https://my-site.vercel.app"
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert "deploy" in cmd
            assert "--token=token-123" in cmd
            assert "--prod" in cmd
            assert "--name" in cmd
            env = mock_run.call_args[1]["env"]
            assert env["CI"] == "1"
            assert env["VERCEL_ORG_ID"] == "org-123"
