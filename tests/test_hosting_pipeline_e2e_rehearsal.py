#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Full-Site Static Hosting Deploy Pipeline E2E Rehearsal
模块职责：全站静态托管发布流水线端到端演练（GitHub Pages / Vercel / Netlify / 批次流水账本）。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from core.adapters.egress.publishers.base import PublisherRegistry
from adapters.egress.publishers.github_pages import GitHubPagesPublisher
from adapters.egress.publishers.vercel import VercelPublisher
from adapters.egress.publishers.netlify import NetlifyPublisher
from services.api.routes.dispatch_shards.hosting_diagnostic_routes import (
    resolve_hosting_site_url, get_bundle_stats, format_deploy_process_logs
)
from services.api.routes.dispatch_shards.hosting_routes import (
    _resolve_ordered_hosting_channels, _collect_fleet_status, launch_hosting_deploy_job
)


class TestHostingPipelineE2ERehearsal(unittest.TestCase):
    """🌐 全站静态托管发布流水线端到端演练测试套件"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="illacme_hosting_e2e_")
        self.bundle_dir = os.path.join(self.temp_dir, "dist", "site")
        os.makedirs(os.path.join(self.bundle_dir, "assets"), exist_ok=True)
        os.makedirs(os.path.join(self.bundle_dir, "posts"), exist_ok=True)

        # 写入模拟静态站点资产
        with open(os.path.join(self.bundle_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html><html><head><title>主权书站</title></head><body><h1>首页</h1></body></html>")
        with open(os.path.join(self.bundle_dir, "404.html"), "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html><html><body><h1>404 Not Found</h1></body></html>")
        with open(os.path.join(self.bundle_dir, "posts", "hello.html"), "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html><html><body><p>正文内容</p></body></html>")
        with open(os.path.join(self.bundle_dir, "assets", "style.css"), "w", encoding="utf-8") as f:
            f.write("body { margin: 0; background: #000; color: #fff; }")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bundle_stats_and_fleet_resolution(self):
        """阶段 1：验证静态发布包态势感知与多平台 URL 智能推导"""
        mock_engine = MagicMock()
        mock_engine.config.active_imprint = "sovereign_press"
        mock_engine.config.active_theme = "default"
        mock_engine.ssg_adapter.get_site_dir.return_value = self.bundle_dir

        stats = get_bundle_stats(mock_engine)
        self.assertTrue(stats["bundle_exists"])
        self.assertGreaterEqual(stats["pages_count"], 3)
        self.assertGreater(stats["bundle_size_kb"], 0.0)

        # 校验 11 大平台 URL 智能推导契约
        gh_url = resolve_hosting_site_url("github_pages", {"repo_url": "https://github.com/myorg/myrepo"}, {})
        self.assertEqual(gh_url, "https://myorg.github.io/myrepo/")

        vercel_url = resolve_hosting_site_url("vercel", {"project_name": "my-press"}, {})
        self.assertEqual(vercel_url, "https://my-press.vercel.app")

        netlify_url = resolve_hosting_site_url("netlify", {"site_name": "my-press-site"}, {})
        self.assertEqual(netlify_url, "https://my-press-site.netlify.app")

        # 校验主站优先排序契约 (Rule #5 主站率先投递)
        direct_upload = {
            "github_pages": {"enabled": True},
            "vercel": {"enabled": True},
            "netlify": {"enabled": True}
        }
        mock_engine.config.publish_control.primary_hosting_id = "vercel"
        ordered = _resolve_ordered_hosting_channels(mock_engine, direct_upload)
        self.assertEqual(ordered[0], "vercel", "官方主站必须在流水线中首个率先投递")

    def test_github_pages_e2e_rehearsal_flow(self):
        """阶段 2：端到端真实演练 GitHub Pages 静态站点部署与元文件注入"""
        remote_repo = os.path.join(self.temp_dir, "remote_git")
        os.makedirs(remote_repo, exist_ok=True)
        # 初始化远程裸仓库
        import subprocess
        subprocess.run(["git", "init", "--bare", remote_repo], check=True, capture_output=True)

        config = {
            "repo_url": remote_repo,
            "branch": "gh-pages",
            "cname": "press.mycustomdomain.org",
            "nojekyll": True,
            "commit_message": "rehearsal: static deploy {timestamp}"
        }
        pub = GitHubPagesPublisher(config=config, sys_config={})
        res = pub.push(self.bundle_dir, {"timestamp": "2026-10-27 06:00:00", "imprint": "test"})

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["branch"], "gh-pages")

        # 验证远端 gh-pages 分支中确实注入了 .nojekyll 与 CNAME
        verify_clone = os.path.join(self.temp_dir, "verify_clone")
        subprocess.run(["git", "clone", "-b", "gh-pages", remote_repo, verify_clone], check=True, capture_output=True)
        self.assertTrue(os.path.isfile(os.path.join(verify_clone, ".nojekyll")))
        self.assertTrue(os.path.isfile(os.path.join(verify_clone, "CNAME")))
        with open(os.path.join(verify_clone, "CNAME"), "r") as f:
            self.assertEqual(f.read().strip(), "press.mycustomdomain.org")
        self.assertTrue(os.path.isfile(os.path.join(verify_clone, "index.html")))

    @patch("subprocess.run")
    def test_vercel_e2e_rehearsal_flow(self, mock_run):
        """阶段 3：端到端模拟演练 Vercel CLI 部署与 cleanUrls 注入"""
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = "Vercel CLI 34.2.0\nUploaded 4 files\nhttps://my-press-inst123.vercel.app\nDone"
        mock_run.return_value = mock_res

        config = {
            "token": "mock-vercel-token-secret",
            "project_name": "my-press-live",
            "prod": True
        }
        pub = VercelPublisher(config=config, sys_config={})
        res = pub.push(self.bundle_dir, {"is_primary": True})

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["project"], "my-press-live")
        self.assertEqual(res["url"], "https://my-press-live.vercel.app")

        # 校验 vercel.json 友好路由注入
        vercel_json = os.path.join(self.bundle_dir, "vercel.json")
        self.assertTrue(os.path.isfile(vercel_json))

        # 校验执行命令附带了 --yes 与非阻塞参数 (遵循 Rule #4)
        call_args = mock_run.call_args[0][0]
        self.assertIn("--yes", call_args)
        self.assertIn("--prod", call_args)

    @patch("subprocess.run")
    def test_netlify_e2e_rehearsal_flow(self, mock_run):
        """阶段 4：端到端模拟演练 Netlify CLI 部署与 npx 降级回填"""
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = '{"site_id": "site-xyz", "deploy_url": "https://xyz-deploy.netlify.app", "url": "https://site-xyz.netlify.app"}'
        mock_run.return_value = mock_res

        config = {
            "site_id": "site-xyz",
            "auth_token": "mock-netlify-token",
            "prod": True
        }
        pub = NetlifyPublisher(config=config, sys_config={})
        res = pub.push(self.bundle_dir, {})

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["site_id"], "site-xyz")
        self.assertEqual(res["url"], "https://site-xyz.netlify.app")

        # 校验命令包含 --dir, --site 与 --json
        call_args = mock_run.call_args[0][0]
        self.assertTrue(any(arg.startswith("--dir=") for arg in call_args))
        self.assertTrue(any(arg.startswith("--site=") for arg in call_args))
        self.assertIn("--json", call_args)

    def test_full_pipeline_orchestration_and_ledger(self):
        """阶段 5：验证流水线总调度与控制台批次流水格式化"""
        logs = format_deploy_process_logs(
            batch_id="deploy_test_123",
            theme="default",
            pages_count=42,
            bundle_size_formatted="2.5 MB",
            channels=["github_pages", "vercel"],
            targets_result={
                "github_pages": {"status": "SUCCESS", "url": "https://user.github.io/repo/", "duration_sec": 1.5},
                "vercel": {"status": "SUCCESS", "url": "https://press.vercel.app", "duration_sec": 2.1}
            },
            overall_status="SUCCESS",
            duration=3.6,
            start_time_str="06:30:00"
        )
        self.assertIn("#123", logs)
        self.assertIn("github_pages", logs)
        self.assertIn("vercel", logs)
        self.assertIn("SUCCESS", logs)


if __name__ == "__main__":
    unittest.main()
