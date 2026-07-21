#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V48.3] Cloudflare Pages Publisher 插件测试
"""
import os
import sys
import tempfile
import pytest
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
            "wrangler_path": "/usr/local/bin/wrangler",
            "deploy_timeout": 120,
            "api_timeout": 10,
            "health_check_timeout": 5
        })
        assert pub.PLUGIN_ID == "cloudflare_pages"
        assert pub.project_name == "my-docs-site"
        assert pub.branch == "production"
        assert pub.account_id == "acc-123"
        assert pub.wrangler_path == "/usr/local/bin/wrangler"
        assert pub.enabled is True
        assert pub.deploy_timeout == 120
        assert pub.api_timeout == 10
        assert pub.health_check_timeout == 5

    def test_default_config_values(self):
        """验证默认配置值正确"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        pub = CloudflarePagesPublisher(config={})
        assert pub.project_name == ""
        assert pub.branch == "production"
        assert pub.account_id == ""
        assert pub.wrangler_path == "wrangler"
        assert pub.deploy_timeout == 300
        assert pub.api_timeout == 8
        assert pub.health_check_timeout == 15

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

    @patch("subprocess.run")
    def test_cloudflare_pages_token_env_injection_and_masking(self, mock_run):
        """验证 Wrangler deploy 运行时会注入 CLOUDFLARE_API_TOKEN 环境变量，且会对其进行错误脱敏"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = "✨ Success! Uploaded 12 files\nDeployment URL: https://my-site.pages.dev\n"
        mock_res.stderr = ""
        mock_run.return_value = mock_res
        
        pub = CloudflarePagesPublisher(config={
            "project_name": "my-site",
            "token": "cf_securetoken123"
        })
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            
            # 验证环境变量中确实含有 Token
            called_env = mock_run.call_args[1].get("env", {})
            assert called_env.get("CLOUDFLARE_API_TOKEN") == "cf_securetoken123"
            
        # 验证错误信息脱敏
        raw_error_message = "Failed to authenticate with token cf_securetoken123 on api.cloudflare.com"
        masked_message = pub._mask_token(raw_error_message)
        assert "cf_securetoken123" not in masked_message
        assert masked_message == "Failed to authenticate with token *** on api.cloudflare.com"

    def test_auto_fetch_account_id_success(self):
        """验证使用 Cloudflare API Token 能自动探测并拉取 account_id"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        from unittest.mock import patch, MagicMock
        import json

        pub = CloudflarePagesPublisher(config={
            "project_name": "test-project",
            "token": "cf_valid_token"
        })

        # 模拟 API 响应数据
        api_response_data = {
            "result": [
                {
                    "id": "mock_cf_account_id_5678",
                    "name": "My CF Account"
                }
            ],
            "success": True
        }

        mock_ctx = MagicMock()
        mock_ctx.status = 200
        mock_ctx.read.return_value = json.dumps(api_response_data).encode("utf-8")
        
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_ctx

        with patch("urllib.request.urlopen", return_value=mock_response):
            account_id = pub._auto_fetch_account_id("cf_valid_token")
            assert account_id == "mock_cf_account_id_5678"

    @pytest.mark.anyio
    async def test_install_npm_dependencies_success(self):
        """验证 install_plugin_deps_impl 能够正确调用 npm 并安装 wrangler 物理依赖"""
        from services.api.routes.gov.context_shards.plugin_ops_deps import install_plugin_deps_impl
        from unittest.mock import patch, MagicMock

        # 模拟 shutil.which 发现 npm 存在
        # 模拟 subprocess.run 返回成功
        mock_process = MagicMock()
        mock_process.returncode = 0

        with patch("shutil.which", return_value="/usr/local/bin/npm"), \
             patch("subprocess.run", return_value=mock_process):
            result = await install_plugin_deps_impl({"id": "cloudflare_pages"})
            assert result["success"] is True
            assert any("wrangle" in log["message"] or "npm" in log["message"] for log in result["logs"])

    def test_custom_timeouts_and_timeout_exception(self):
        """验证自定义超时属性被正确传递给 subprocess 并在超时异常时进行友好提示"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        import subprocess

        pub = CloudflarePagesPublisher(config={
            "project_name": "test-timeout-project",
            "deploy_timeout": 42
        })

        # 模拟 subprocess.run 抛出 TimeoutExpired
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=["wrangler"], timeout=42)), \
             tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {})
            assert result["status"] == "error"
            assert "timed out after 42 seconds" in result["message"]

    def test_get_proxy_with_pydantic_settings(self):
        """验证 BasePublisher 能够同时兼容字典和 Pydantic Model 对象的代理读取"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        
        # 1. 模拟 SystemSettings 实例化对象
        class MockSystemSettings:
            def __init__(self, global_proxy):
                self.global_proxy = global_proxy

        sys_settings_obj = MockSystemSettings("http://127.0.0.1:8888")
        pub1 = CloudflarePagesPublisher(config={"enabled": True}, sys_config=sys_settings_obj)
        assert pub1.get_proxy() == "http://127.0.0.1:8888"

        # 2. 模拟普通 dict
        sys_settings_dict = {"global_proxy": "http://127.0.0.1:9999"}
        pub2 = CloudflarePagesPublisher(config={"enabled": True}, sys_config=sys_settings_dict)
        assert pub2.get_proxy() == "http://127.0.0.1:9999"

        # 3. 优先读取插件局部的 proxy
        pub3 = CloudflarePagesPublisher(config={"enabled": True, "proxy": "http://127.0.0.1:7777"}, sys_config=sys_settings_dict)
        assert pub3.get_proxy() == "http://127.0.0.1:7777"

    def test_build_wrangler_command_npx_fallback(self):
        """验证当系统找不到全局 wrangler 时，自动降级为以 npx -y wrangler 运行"""
        from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
        from unittest.mock import patch

        pub = CloudflarePagesPublisher(config={
            "project_name": "my-site",
            "account_id": "acc-123"
        })

        # 模拟 shutil.which("wrangler") 返回 None（系统无全局 wrangler）
        # 模拟 os.path.exists 本地 node_modules 下的 wrangler 返回 False
        # 模拟 shutil.which("npx") 返回 "/usr/local/bin/npx" (系统有 npx)
        with patch("shutil.which", side_effect=lambda name: "/usr/local/bin/npx" if name == "npx" else None), \
             patch("os.path.exists", return_value=False):
            cmd = pub._build_wrangler_command("/fake/bundle")
            assert cmd[0] == "npx"
            assert cmd[1] == "-y"
            assert cmd[2] == "wrangler"
            assert "--project-name" in cmd
            assert "my-site" in cmd
            assert "--account-id" in cmd
            assert "acc-123" in cmd
