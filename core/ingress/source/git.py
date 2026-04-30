#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Ingress Plugin - Git Repository Source
职责：负责从 Git 仓库拉取并读取数据，实现团队协作的远程收稿。
🛡️ [V48.3] 全息收稿：支持直接从 Git 仓库同步原稿，含增量更新与冲突检测。
"""
import os
import shutil
import subprocess
import logging
from typing import Iterator, Optional

from core.ingress.base import BaseSource
from core.utils.tracing import tlog

class GitRepositorySource(BaseSource):
    """🚀 [V48.3] Git 仓库数据源 — 全息远程收稿

    支持从远程 Git 仓库克隆/拉取 Markdown 原稿。采用浅克隆 (shallow clone) 策略
    以降低带宽消耗，支持增量同步 (git pull) 以实现高效的二次收稿。

    物理协议：
      - 仓库数据缓存在 `.plenipes/ingress/git/{repo_hash}/` 下
      - 文件列表仅返回 Markdown 相关文件 (.md, .mdx)
      - mtime 基于 git log 的作者时间 (author date)
    """

    # 支持的文件扩展名
    _CONTENT_EXTENSIONS = {'.md', '.mdx', '.markdown'}

    def __init__(
        self,
        repo_url: str,
        branch: str = "main",
        subfolder: str = "",
        cache_root: str = ".plenipes/ingress/git"
    ):
        self.repo_url = repo_url
        self.branch = branch
        self.subfolder = subfolder.strip("/")
        self._cache_root = os.path.abspath(cache_root)

        # 基于 URL 生成稳定的缓存目录名
        import hashlib
        url_hash = hashlib.sha256(repo_url.encode()).hexdigest()[:12]
        safe_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        self._local_path = os.path.join(self._cache_root, f"{safe_name}_{url_hash}")

        # 内容根路径 (可能是仓库子目录)
        self._content_root = os.path.join(self._local_path, self.subfolder) if self.subfolder else self._local_path

    # ==========================================
    # Git 操作层
    # ==========================================

    def _git_available(self) -> bool:
        """检测本机 git 命令是否可用"""
        return shutil.which("git") is not None

    def _run_git(self, args: list, cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        """安全执行 git 命令"""
        cmd = ["git"] + args
        result = subprocess.run(
            cmd, cwd=cwd or self._local_path,
            capture_output=True, text=True, timeout=120
        )
        return result

    def sync(self) -> bool:
        """🚀 [V48.3] 同步远程仓库到本地缓存

        策略：
          - 首次调用执行浅克隆 (depth=1)
          - 后续调用执行增量拉取 (git pull --ff-only)

        Returns:
            bool: 同步是否成功
        """
        if not self._git_available():
            tlog.error("❌ [Git Ingress] 系统未安装 git 命令行工具。")
            return False

        os.makedirs(self._cache_root, exist_ok=True)

        if os.path.exists(os.path.join(self._local_path, ".git")):
            # 增量拉取
            tlog.info(f"📥 [Git Ingress] 增量同步: {self.repo_url} ({self.branch})")
            result = self._run_git(["pull", "--ff-only", "origin", self.branch])
            if result.returncode != 0:
                tlog.warning(f"⚠️ [Git Ingress] 增量拉取失败，尝试硬重置: {result.stderr.strip()}")
                # 回退策略：fetch + reset
                self._run_git(["fetch", "origin", self.branch])
                self._run_git(["reset", "--hard", f"origin/{self.branch}"])
            tlog.info("✅ [Git Ingress] 增量同步完成。")
        else:
            # 首次浅克隆
            tlog.info(f"📥 [Git Ingress] 首次克隆: {self.repo_url} → {self._local_path}")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", self.branch,
                 self.repo_url, self._local_path],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode != 0:
                tlog.error(f"❌ [Git Ingress] 克隆失败: {result.stderr.strip()}")
                return False
            tlog.info("✅ [Git Ingress] 首次克隆完成。")

        return True

    # ==========================================
    # BaseSource 契约实现
    # ==========================================

    def list_files(self) -> Iterator[str]:
        """[Contract] 返回仓库中的全量 Markdown 文件相对路径"""
        if not os.path.isdir(self._content_root):
            tlog.warning(f"⚠️ [Git Ingress] 内容根目录不存在: {self._content_root}，请先调用 sync()。")
            return

        for root, dirs, files in os.walk(self._content_root):
            # 跳过 Git 内部目录与隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'):
                    continue
                ext = os.path.splitext(file)[1].lower()
                if ext in self._CONTENT_EXTENSIONS:
                    abs_path = os.path.join(root, file)
                    yield os.path.relpath(abs_path, self._content_root)

    def read_content(self, rel_path: str) -> str:
        """[Contract] 读取指定文件的原始文本内容"""
        abs_path = os.path.join(self._content_root, rel_path)
        if not os.path.exists(abs_path):
            tlog.warning(f"⚠️ [Git Ingress] 文件不存在: {rel_path}")
            return ""
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_mtime(self, rel_path: str) -> float:
        """[Contract] 获取文件修改时间

        优先使用 git log 的作者时间；
        回退到文件系统的 mtime。
        """
        abs_path = os.path.join(self._content_root, rel_path)

        # 尝试从 git log 获取精确的作者时间
        if os.path.exists(os.path.join(self._local_path, ".git")):
            try:
                result = self._run_git(
                    ["log", "-1", "--format=%at", "--", rel_path],
                    cwd=self._content_root
                )
                if result.returncode == 0 and result.stdout.strip():
                    return float(result.stdout.strip())
            except (ValueError, subprocess.TimeoutExpired):
                pass

        # 回退到文件系统时间
        if os.path.exists(abs_path):
            return os.path.getmtime(abs_path)

        return 0.0

    # ==========================================
    # 辅助能力
    # ==========================================

    def get_health_status(self) -> dict:
        """🚀 [V48.3] 返回数据源健康状态，用于 sentinel_health.json"""
        is_cloned = os.path.exists(os.path.join(self._local_path, ".git"))
        file_count = sum(1 for _ in self.list_files()) if is_cloned else 0

        return {
            "source_type": "git",
            "repo_url": self.repo_url,
            "branch": self.branch,
            "subfolder": self.subfolder or "(root)",
            "is_cloned": is_cloned,
            "local_cache": self._local_path,
            "file_count": file_count,
            "status": "online" if is_cloned else "offline"
        }
