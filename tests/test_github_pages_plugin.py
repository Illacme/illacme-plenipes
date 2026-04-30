#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V48.3] GitHub Pages Publisher 插件测试
验证 GitHubPagesPublisher 的核心契约与内部逻辑。
所有测试均在本地模拟环境中运行，不涉及真实网络请求。
"""
import os
import sys
import tempfile
import shutil
import subprocess

sys.path.insert(0, os.path.abspath('.'))

import pytest


class TestGitHubPagesPublisher:
    """GitHub Pages 发布插件单元测试"""

    def test_import_and_instantiate(self):
        """验证 GitHubPagesPublisher 可正常导入和实例化"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        pub = GitHubPagesPublisher(config={
            "enabled": True,
            "repo_url": "https://github.com/test/test.git",
            "branch": "gh-pages"
        })
        assert pub.PLUGIN_ID == "github_pages"
        assert pub.repo_url == "https://github.com/test/test.git"
        assert pub.branch == "gh-pages"
        assert pub.enabled is True

    def test_default_config_values(self):
        """验证默认配置值正确"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        pub = GitHubPagesPublisher(config={})
        assert pub.repo_url == ""
        assert pub.branch == "gh-pages"
        assert pub.cname == ""
        assert pub.force_push is False
        assert pub.nojekyll is True
        assert pub.git_user_name == "Plenipes Bot"
        assert pub.git_user_email == "bot@plenipes.press"

    def test_push_skips_when_no_repo_url(self):
        """未配置 repo_url 时 push 应直接跳过"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        pub = GitHubPagesPublisher(config={})
        result = pub.push("/tmp/fake_bundle", {})
        assert result["status"] == "skipped"
        assert "repo_url" in result["message"]

    def test_push_errors_when_bundle_missing(self):
        """bundle_path 不存在时 push 应返回 error"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        pub = GitHubPagesPublisher(config={
            "repo_url": "https://github.com/test/test.git"
        })
        result = pub.push("/nonexistent/path", {})
        assert result["status"] == "error"
        assert "does not exist" in result["message"]

    def test_is_healthy_checks_git(self):
        """验证 is_healthy 通过检测 git 命令可用性"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        pub = GitHubPagesPublisher(config={})
        # 在大多数开发环境中 git 应该已安装
        assert pub.is_healthy() is True

    def test_inherits_base_publisher(self):
        """验证正确继承 BasePublisher"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        from plugins.publishers.base import BasePublisher
        assert issubclass(GitHubPagesPublisher, BasePublisher)

    def test_clean_work_dir_preserves_git(self):
        """验证 _clean_work_dir 保留 .git 目录但清除其他文件"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        pub = GitHubPagesPublisher(config={})

        work_dir = tempfile.mkdtemp()
        try:
            # 模拟已克隆的仓库结构
            os.makedirs(os.path.join(work_dir, ".git", "objects"), exist_ok=True)
            os.makedirs(os.path.join(work_dir, "old_content"), exist_ok=True)
            with open(os.path.join(work_dir, "index.html"), 'w') as f:
                f.write("<html>old</html>")
            with open(os.path.join(work_dir, "old_content", "page.html"), 'w') as f:
                f.write("<html>old page</html>")

            pub._clean_work_dir(work_dir)

            # .git 应该保留
            assert os.path.isdir(os.path.join(work_dir, ".git"))
            assert os.path.isdir(os.path.join(work_dir, ".git", "objects"))
            # 其他内容应被清除
            assert not os.path.exists(os.path.join(work_dir, "index.html"))
            assert not os.path.exists(os.path.join(work_dir, "old_content"))
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def test_copy_bundle_counts_files(self):
        """验证 _copy_bundle 正确复制文件并返回计数"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        pub = GitHubPagesPublisher(config={})

        bundle_dir = tempfile.mkdtemp()
        work_dir = tempfile.mkdtemp()
        try:
            # 创建模拟构建产物
            with open(os.path.join(bundle_dir, "index.html"), 'w') as f:
                f.write("<html>test</html>")
            os.makedirs(os.path.join(bundle_dir, "assets"))
            with open(os.path.join(bundle_dir, "assets", "style.css"), 'w') as f:
                f.write("body { margin: 0; }")
            # 隐藏文件不应被复制
            with open(os.path.join(bundle_dir, ".DS_Store"), 'w') as f:
                f.write("")

            count = pub._copy_bundle(bundle_dir, work_dir)

            assert count == 2  # index.html + style.css
            assert os.path.isfile(os.path.join(work_dir, "index.html"))
            assert os.path.isfile(os.path.join(work_dir, "assets", "style.css"))
            assert not os.path.exists(os.path.join(work_dir, ".DS_Store"))
        finally:
            shutil.rmtree(bundle_dir, ignore_errors=True)
            shutil.rmtree(work_dir, ignore_errors=True)

    def test_inject_nojekyll(self):
        """验证 .nojekyll 文件注入"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        pub = GitHubPagesPublisher(config={"nojekyll": True})

        work_dir = tempfile.mkdtemp()
        try:
            pub._inject_meta_files(work_dir)
            assert os.path.isfile(os.path.join(work_dir, ".nojekyll"))
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def test_inject_cname(self):
        """验证 CNAME 文件注入"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        pub = GitHubPagesPublisher(config={
            "cname": "docs.example.com"
        })

        work_dir = tempfile.mkdtemp()
        try:
            pub._inject_meta_files(work_dir)
            cname_path = os.path.join(work_dir, "CNAME")
            assert os.path.isfile(cname_path)
            with open(cname_path, 'r') as f:
                assert f.read() == "docs.example.com"
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def test_no_cname_when_not_configured(self):
        """未配置 cname 时不应生成 CNAME 文件"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        pub = GitHubPagesPublisher(config={})

        work_dir = tempfile.mkdtemp()
        try:
            pub._inject_meta_files(work_dir)
            assert not os.path.exists(os.path.join(work_dir, "CNAME"))
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def test_no_nojekyll_when_disabled(self):
        """nojekyll=false 时不应生成 .nojekyll 文件"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        pub = GitHubPagesPublisher(config={"nojekyll": False})

        work_dir = tempfile.mkdtemp()
        try:
            pub._inject_meta_files(work_dir)
            assert not os.path.exists(os.path.join(work_dir, ".nojekyll"))
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def test_plugin_auto_discovery_by_loader(self):
        """验证 PluginLoader 能自动发现 GitHubPagesPublisher"""
        from core.utils.plugin_loader import PluginLoader
        from plugins.publishers.base import BasePublisher

        plugin_dir = os.path.join("plugins", "publishers")
        classes = PluginLoader.load_plugins(plugin_dir, BasePublisher, package_name="plugins.publishers")

        plugin_ids = [getattr(cls, "PLUGIN_ID", "") for cls in classes]
        assert "github_pages" in plugin_ids, f"github_pages not found in discovered plugins: {plugin_ids}"

    def test_commit_message_template_formatting(self):
        """验证 commit message 模板变量替换"""
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher
        pub = GitHubPagesPublisher(config={
            "commit_message": "Deploy {files} files to {branch} at {timestamp}"
        })
        msg = pub.commit_message_template.format(
            timestamp="2026-04-30 09:00:00",
            files=42,
            branch="gh-pages"
        )
        assert "42" in msg
        assert "gh-pages" in msg
        assert "2026-04-30" in msg

    def test_full_local_deploy_simulation(self):
        """
        模拟完整部署流程（本地 Git 仓库作为 remote）。
        这是一个端到端集成测试，验证 clone → clean → copy → commit → push 全流程。
        """
        from plugins.publishers.github_pages_plugin import GitHubPagesPublisher

        # ── 准备：创建一个本地 bare 仓库作为 remote ──
        remote_dir = tempfile.mkdtemp(prefix="plenipes_test_remote_")
        bundle_dir = tempfile.mkdtemp(prefix="plenipes_test_bundle_")

        try:
            # 初始化 bare repo
            subprocess.run(["git", "init", "--bare", remote_dir],
                           capture_output=True, check=True)

            # 在 bare repo 中创建一个初始提交（否则无法克隆）
            init_dir = tempfile.mkdtemp()
            subprocess.run(["git", "clone", remote_dir, init_dir],
                           capture_output=True, check=True)
            subprocess.run(["git", "-C", init_dir, "config", "user.name", "test"],
                           capture_output=True, check=True)
            subprocess.run(["git", "-C", init_dir, "config", "user.email", "test@test.com"],
                           capture_output=True, check=True)
            with open(os.path.join(init_dir, "README.md"), 'w') as f:
                f.write("init")
            subprocess.run(["git", "-C", init_dir, "add", "."],
                           capture_output=True, check=True)
            subprocess.run(["git", "-C", init_dir, "commit", "-m", "init"],
                           capture_output=True, check=True)
            subprocess.run(["git", "-C", init_dir, "push", "origin", "main"],
                           capture_output=True, check=True)
            shutil.rmtree(init_dir, ignore_errors=True)

            # 创建模拟构建产物
            with open(os.path.join(bundle_dir, "index.html"), 'w') as f:
                f.write("<!DOCTYPE html><html><body>Hello Plenipes!</body></html>")
            os.makedirs(os.path.join(bundle_dir, "assets"))
            with open(os.path.join(bundle_dir, "assets", "app.js"), 'w') as f:
                f.write("console.log('deployed');")

            # ── 执行部署 ──
            pub = GitHubPagesPublisher(config={
                "enabled": True,
                "repo_url": remote_dir,  # 使用本地路径作为 remote
                "branch": "gh-pages",
                "cname": "test.plenipes.press",
                "nojekyll": True,
                "git_user_name": "Test Bot",
                "git_user_email": "test@plenipes.press"
            })

            result = pub.push(bundle_dir, {"timestamp": "2026-04-30T09:00:00"})

            # ── 验证结果 ──
            assert result["status"] == "success", f"Deploy failed: {result}"
            assert result["files"] == 2  # index.html + app.js
            assert result["branch"] == "gh-pages"

            # ── 验证远程仓库 ──
            verify_dir = tempfile.mkdtemp()
            subprocess.run(
                ["git", "clone", "--branch", "gh-pages", remote_dir, verify_dir],
                capture_output=True, check=True
            )
            # 验证文件存在
            assert os.path.isfile(os.path.join(verify_dir, "index.html"))
            assert os.path.isfile(os.path.join(verify_dir, "assets", "app.js"))
            assert os.path.isfile(os.path.join(verify_dir, ".nojekyll"))
            assert os.path.isfile(os.path.join(verify_dir, "CNAME"))
            # 验证 CNAME 内容
            with open(os.path.join(verify_dir, "CNAME"), 'r') as f:
                assert f.read() == "test.plenipes.press"
            shutil.rmtree(verify_dir, ignore_errors=True)

            # ── 验证二次部署（幂等性）──
            result2 = pub.push(bundle_dir, {})
            assert result2["status"] == "success"
            assert result2.get("message") == "No changes to deploy."

        finally:
            shutil.rmtree(remote_dir, ignore_errors=True)
            shutil.rmtree(bundle_dir, ignore_errors=True)
