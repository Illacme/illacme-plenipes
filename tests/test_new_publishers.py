#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V24.0] 单元测试 — 5大全新分发渠道插件 (Gitee Pages, Firebase, Render, Railway, Zeabur)
"""

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch
import subprocess

sys.path.insert(0, os.path.abspath('.'))


class TestGiteePagesPublisher:
    """Gitee Pages 发布器插件测试"""

    def test_init_and_default_values(self):
        from adapters.egress.publishers.gitee_pages import GiteePagesPublisher
        pub = GiteePagesPublisher(config={
            "enabled": True,
            "repo_url": "https://gitee.com/owner/repo.git",
            "branch": "master",
            "token": "gitee_pat_token_123"
        })
        assert pub.PLUGIN_ID == "gitee_pages"
        assert pub.repo_url == "https://gitee.com/owner/repo.git"
        assert pub.branch == "master"
        assert pub.token == "gitee_pat_token_123"
        assert pub.trigger_build is True

    def test_get_authenticated_repo_url(self):
        from adapters.egress.publishers.gitee_pages import GiteePagesPublisher
        pub = GiteePagesPublisher(config={
            "repo_url": "https://gitee.com/owner/repo.git",
            "token": "mytoken"
        })
        auth_url = pub._get_authenticated_repo_url()
        assert auth_url == "https://oauth2:mytoken@gitee.com/owner/repo.git"

        # 原样返回非 Gitee URL
        pub_other = GiteePagesPublisher(config={
            "repo_url": "https://github.com/owner/repo.git",
            "token": "mytoken"
        })
        assert pub_other._get_authenticated_repo_url() == "https://github.com/owner/repo.git"

    def test_mask_url_credentials(self):
        from adapters.egress.publishers.gitee_pages import GiteePagesPublisher
        pub = GiteePagesPublisher(config={})
        text = "error cloning https://oauth2:secret_token_abc@gitee.com/owner/repo.git"
        masked = pub._mask_url_credentials(text)
        assert "secret_token_abc" not in masked
        assert masked == "error cloning https://oauth2:***@gitee.com/owner/repo.git"

    @patch("subprocess.run")
    @patch("requests.post")
    def test_push_success(self, mock_post, mock_run):
        from adapters.egress.publishers.gitee_pages import GiteePagesPublisher
        pub = GiteePagesPublisher(config={
            "repo_url": "https://gitee.com/owner/repo.git",
            "token": "gitee_token_123",
            "trigger_build": True
        })

        # 模拟 git clone & git status & git push
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "modified file.txt"
        mock_run.return_value = mock_process

        # 模拟 Gitee Pages rebuild API 响应
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {"timestamp": "2026-07-07 12:00:00"})
            assert result["status"] == "success"
            assert result["repo"] == "https://gitee.com/owner/repo.git"

            # 验证 API Rebuild 触发了 requests.post
            mock_post.assert_called_once()
            called_url = mock_post.call_args[0][0]
            assert "gitee.com/api/v5/repos/owner/repo/pages/builds" in called_url


class TestFirebaseHostingPublisher:
    """Firebase Hosting 发布器插件测试"""

    def test_init_and_defaults(self):
        from adapters.egress.publishers.firebase import FirebaseHostingPublisher
        pub = FirebaseHostingPublisher(config={
            "project": "my-firebase-project",
            "token": "cf_token_abc",
            "site": "my-custom-site"
        })
        assert pub.PLUGIN_ID == "firebase"
        assert pub.project == "my-firebase-project"
        assert pub.token == "cf_token_abc"
        assert pub.site == "my-custom-site"
        assert pub.deploy_timeout == 300

    @patch("subprocess.run")
    def test_push_success(self, mock_run):
        from adapters.egress.publishers.firebase import FirebaseHostingPublisher
        pub = FirebaseHostingPublisher(config={
            "project": "my-firebase-project",
            "token": "fb_token_123",
            "site": "my-custom-site",
            "deploy_timeout": 150
        })
        pub.ensure_npm_dependency = MagicMock()

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Hosting URL: https://my-custom-site.web.app"
        mock_run.return_value = mock_process

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert result["project"] == "my-firebase-project"
            assert result["url"] == "https://my-custom-site.web.app"

            # 验证 npx firebase deploy 执行了，并且传入了正确的超时和 project 参数
            mock_run.assert_called_once()
            called_args = mock_run.call_args[0][0]
            assert "firebase" in called_args
            assert "--project" in called_args
            assert "my-firebase-project" in called_args
            assert mock_run.call_args[1].get("timeout") == 150
            assert mock_run.call_args[1].get("env", {}).get("FIREBASE_TOKEN") == "fb_token_123"

    @patch("subprocess.run")
    def test_deploy_timeout(self, mock_run):
        from adapters.egress.publishers.firebase import FirebaseHostingPublisher
        pub = FirebaseHostingPublisher(config={
            "project": "my-firebase-project",
            "deploy_timeout": 50
        })

        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["firebase"], timeout=50)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {})
            assert result["status"] == "error"
            assert "timed out after 50 seconds" in result["message"]


class TestRenderPublisher:
    """Render Webhook Deploy Hook 发布器测试"""

    def test_init_and_git_defaults(self):
        from adapters.egress.publishers.render import RenderPublisher
        pub = RenderPublisher(config={
            "deploy_hook_url": "https://api.render.com/deploy/srv-12345",
            "repo_url": "https://github.com/owner/repo.git",
            "token": "my_pat_token",
            "branch": "prod"
        })
        assert pub.PLUGIN_ID == "render"
        assert pub.deploy_hook_url == "https://api.render.com/deploy/srv-12345"
        assert pub.repo_url == "https://github.com/owner/repo.git"
        assert pub.token == "my_pat_token"
        assert pub.branch == "prod"

    @patch("requests.post")
    def test_push_success_trigger_only(self, mock_post):
        from adapters.egress.publishers.render import RenderPublisher
        pub = RenderPublisher(config={
            "deploy_hook_url": "https://api.render.com/deploy/srv-12345"
        })

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert "triggered" in result["message"]
            mock_post.assert_called_once_with("https://api.render.com/deploy/srv-12345", proxies=None, timeout=10)

    @patch("subprocess.run")
    @patch("requests.post")
    def test_push_success_with_git(self, mock_post, mock_run):
        from adapters.egress.publishers.render import RenderPublisher
        pub = RenderPublisher(config={
            "deploy_hook_url": "https://api.render.com/deploy/srv-12345",
            "repo_url": "https://github.com/owner/repo.git",
            "token": "my_pat_token",
            "branch": "prod"
        })

        # 模拟 git clone, git status, git commit & push
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "modified file.txt"
        mock_run.return_value = mock_process

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            # 建立一个虚拟的静态包子目录，并写入临时文件以触发拷贝和 git push
            with open(os.path.join(tmpdir, "index.html"), "w") as f:
                f.write("test html")
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert result["files"] > 0
            mock_post.assert_called_once_with("https://api.render.com/deploy/srv-12345", proxies=None, timeout=10)
            mock_run.assert_called()


class TestRailwayPublisher:
    """Railway Webhook Deploy Hook 发布器测试"""

    def test_init_and_git_defaults(self):
        from adapters.egress.publishers.railway import RailwayPublisher
        pub = RailwayPublisher(config={
            "deploy_hook_url": "https://backboard.railway.app/webhook/deploy/srv-123",
            "repo_url": "https://github.com/owner/railway-repo.git",
            "token": "rw_token"
        })
        assert pub.PLUGIN_ID == "railway"
        assert pub.deploy_hook_url == "https://backboard.railway.app/webhook/deploy/srv-123"
        assert pub.repo_url == "https://github.com/owner/railway-repo.git"
        assert pub.token == "rw_token"

    @patch("adapters.egress.publishers.railway.requests.post")
    def test_push_success_trigger_only(self, mock_post):
        from adapters.egress.publishers.railway import RailwayPublisher
        pub = RailwayPublisher(config={
            "deploy_hook_url": "https://backboard.railway.app/webhook/deploy/srv-123"
        })

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert "triggered" in result["message"]
            mock_post.assert_called_once_with("https://backboard.railway.app/webhook/deploy/srv-123", proxies=None, timeout=10)

    @patch("subprocess.run")
    @patch("adapters.egress.publishers.railway.requests.post")
    def test_push_success_with_git(self, mock_post, mock_run):
        from adapters.egress.publishers.railway import RailwayPublisher
        pub = RailwayPublisher(config={
            "deploy_hook_url": "https://backboard.railway.app/webhook/deploy/srv-123",
            "repo_url": "https://github.com/owner/railway-repo.git",
            "token": "rw_token"
        })

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "modified file.txt"
        mock_run.return_value = mock_process

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "index.html"), "w") as f:
                f.write("test html")
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert result["files"] > 0
            mock_post.assert_called_once_with("https://backboard.railway.app/webhook/deploy/srv-123", proxies=None, timeout=10)
            mock_run.assert_called()


class TestZeaburPublisher:
    """Zeabur Webhook Deploy Hook 发布器测试"""

    def test_init_and_git_defaults(self):
        from adapters.egress.publishers.zeabur import ZeaburPublisher
        pub = ZeaburPublisher(config={
            "deploy_hook_url": "https://api.zeabur.com/deploy/srv-123",
            "repo_url": "https://github.com/owner/zeabur-repo.git",
            "token": "zb_token"
        })
        assert pub.PLUGIN_ID == "zeabur"
        assert pub.deploy_hook_url == "https://api.zeabur.com/deploy/srv-123"
        assert pub.repo_url == "https://github.com/owner/zeabur-repo.git"
        assert pub.token == "zb_token"

    @patch("adapters.egress.publishers.zeabur.requests.post")
    def test_push_success_trigger_only(self, mock_post):
        from adapters.egress.publishers.zeabur import ZeaburPublisher
        pub = ZeaburPublisher(config={
            "deploy_hook_url": "https://api.zeabur.com/deploy/srv-123"
        })

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert "triggered" in result["message"]
            mock_post.assert_called_once_with("https://api.zeabur.com/deploy/srv-123", proxies=None, timeout=10)

    @patch("subprocess.run")
    @patch("adapters.egress.publishers.zeabur.requests.post")
    def test_push_success_with_git(self, mock_post, mock_run):
        from adapters.egress.publishers.zeabur import ZeaburPublisher
        pub = ZeaburPublisher(config={
            "deploy_hook_url": "https://api.zeabur.com/deploy/srv-123",
            "repo_url": "https://github.com/owner/zeabur-repo.git",
            "token": "zb_token"
        })

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "modified file.txt"
        mock_run.return_value = mock_process

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "index.html"), "w") as f:
                f.write("test html")
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert result["files"] > 0
            mock_post.assert_called_once_with("https://api.zeabur.com/deploy/srv-123", proxies=None, timeout=10)
            mock_run.assert_called()
