#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V48.3] Git Ingress 数据源测试
验证 GitRepositorySource 的核心契约：list_files / read_content / get_mtime / sync / health
"""
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.abspath('.'))

import pytest

class TestGitIngressSource:
    """Git 数据源核心契约测试"""

    def test_import_and_instantiate(self):
        """验证 GitRepositorySource 可正常导入和实例化"""
        from core.ingress.source.git import GitRepositorySource
        source = GitRepositorySource(
            repo_url="https://github.com/example/test-repo.git",
            branch="main"
        )
        assert source.repo_url == "https://github.com/example/test-repo.git"
        assert source.branch == "main"
        assert source.subfolder == ""

    def test_cache_path_deterministic(self):
        """验证相同 URL 生成相同的缓存路径（幂等性）"""
        from core.ingress.source.git import GitRepositorySource
        s1 = GitRepositorySource(repo_url="https://github.com/a/b.git", branch="main")
        s2 = GitRepositorySource(repo_url="https://github.com/a/b.git", branch="main")
        assert s1._local_path == s2._local_path

    def test_different_urls_different_cache(self):
        """验证不同 URL 生成不同的缓存路径"""
        from core.ingress.source.git import GitRepositorySource
        s1 = GitRepositorySource(repo_url="https://github.com/a/b.git", branch="main")
        s2 = GitRepositorySource(repo_url="https://github.com/c/d.git", branch="main")
        assert s1._local_path != s2._local_path

    def test_list_files_empty_when_not_cloned(self):
        """未克隆时 list_files 应返回空迭代器"""
        from core.ingress.source.git import GitRepositorySource
        source = GitRepositorySource(
            repo_url="https://github.com/nonexistent/repo.git",
            cache_root=tempfile.mkdtemp()
        )
        result = list(source.list_files())
        assert result == []
        # 清理
        shutil.rmtree(source._cache_root, ignore_errors=True)

    def test_read_content_returns_empty_for_missing(self):
        """文件不存在时 read_content 返回空字符串"""
        from core.ingress.source.git import GitRepositorySource
        source = GitRepositorySource(
            repo_url="https://github.com/test/test.git",
            cache_root=tempfile.mkdtemp()
        )
        content = source.read_content("nonexistent.md")
        assert content == ""
        shutil.rmtree(source._cache_root, ignore_errors=True)

    def test_get_mtime_returns_zero_for_missing(self):
        """文件不存在时 get_mtime 返回 0.0"""
        from core.ingress.source.git import GitRepositorySource
        source = GitRepositorySource(
            repo_url="https://github.com/test/test.git",
            cache_root=tempfile.mkdtemp()
        )
        mtime = source.get_mtime("nonexistent.md")
        assert mtime == 0.0
        shutil.rmtree(source._cache_root, ignore_errors=True)

    def test_health_status_offline_when_not_cloned(self):
        """未克隆时健康状态应为 offline"""
        from core.ingress.source.git import GitRepositorySource
        source = GitRepositorySource(
            repo_url="https://github.com/test/repo.git",
            branch="main",
            cache_root=tempfile.mkdtemp()
        )
        health = source.get_health_status()
        assert health["status"] == "offline"
        assert health["is_cloned"] is False
        assert health["source_type"] == "git"
        assert health["file_count"] == 0
        shutil.rmtree(source._cache_root, ignore_errors=True)

    def test_list_files_with_simulated_cache(self):
        """模拟已克隆的缓存目录，验证 list_files 只返回 .md/.mdx 文件"""
        from core.ingress.source.git import GitRepositorySource
        cache_root = tempfile.mkdtemp()
        source = GitRepositorySource(
            repo_url="https://github.com/sim/repo.git",
            cache_root=cache_root
        )

        # 创建模拟的仓库缓存结构
        os.makedirs(source._local_path, exist_ok=True)
        # 模拟 .git 目录
        os.makedirs(os.path.join(source._local_path, ".git"), exist_ok=True)
        # 创建测试文件
        for name in ["readme.md", "guide.mdx", "data.json", "image.png", ".hidden.md"]:
            with open(os.path.join(source._local_path, name), 'w') as f:
                f.write(f"content of {name}")
        # 子目录
        subdir = os.path.join(source._local_path, "docs")
        os.makedirs(subdir, exist_ok=True)
        with open(os.path.join(subdir, "nested.md"), 'w') as f:
            f.write("nested content")

        files = sorted(list(source.list_files()))
        assert "readme.md" in files
        assert "guide.mdx" in files
        assert "docs/nested.md" in files
        # 非 Markdown 文件不应出现
        assert "data.json" not in files
        assert "image.png" not in files
        # 隐藏文件不应出现
        assert ".hidden.md" not in files

        shutil.rmtree(cache_root, ignore_errors=True)

    def test_read_content_with_simulated_cache(self):
        """模拟已克隆缓存，验证 read_content 能正确读取"""
        from core.ingress.source.git import GitRepositorySource
        cache_root = tempfile.mkdtemp()
        source = GitRepositorySource(
            repo_url="https://github.com/sim/repo2.git",
            cache_root=cache_root
        )
        os.makedirs(source._local_path, exist_ok=True)
        test_content = "# Hello World\nThis is a test."
        with open(os.path.join(source._local_path, "test.md"), 'w', encoding='utf-8') as f:
            f.write(test_content)

        result = source.read_content("test.md")
        assert result == test_content
        shutil.rmtree(cache_root, ignore_errors=True)

    def test_subfolder_isolation(self):
        """验证 subfolder 参数正确限制文件扫描范围"""
        from core.ingress.source.git import GitRepositorySource
        cache_root = tempfile.mkdtemp()
        source = GitRepositorySource(
            repo_url="https://github.com/sim/mono.git",
            subfolder="packages/docs",
            cache_root=cache_root
        )

        os.makedirs(source._local_path, exist_ok=True)
        # 创建仓库根文件 (不应被扫描到)
        with open(os.path.join(source._local_path, "root.md"), 'w') as f:
            f.write("root")
        # 创建子目录文件 (应被扫描到)
        target = os.path.join(source._local_path, "packages", "docs")
        os.makedirs(target, exist_ok=True)
        with open(os.path.join(target, "guide.md"), 'w') as f:
            f.write("guide")

        files = list(source.list_files())
        assert "guide.md" in files
        # root.md 不在 subfolder 范围内
        assert "root.md" not in files
        shutil.rmtree(cache_root, ignore_errors=True)

    def test_auto_registration_in_ingress_registry(self):
        """验证 Git 源被 IngressManager 自动发现并注册"""
        # IngressManager.initialize() 在 import manager 模块时自动触发
        from core.ingress.manager import IngressManager  # noqa: F401 — 触发自动发现
        from core.ingress.registry import ingress_registry
        sources = ingress_registry.list_sources()
        assert "git" in sources, f"Git source not registered. Available: {sources}"
        assert "local" in sources, f"Local source not registered. Available: {sources}"
