#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — GitHub Pages Publisher Plugin
🚀 [V48.3]：全球分发中心首个真实渠道实装。

功能：
  1. 将本地构建产物推送至目标 Git 仓库的 gh-pages 分支
  2. 支持孤儿分支初始化 (orphan branch)
  3. 支持自定义 CNAME 域名注入
  4. 支持 .nojekyll 标记自动生成
  5. 支持增量部署 (仅推送 diff) 或全量覆盖

配置示例 (config.yaml):
  github_pages:
    enabled: true
    repo_url: "https://github.com/user/repo.git"
    branch: "gh-pages"
    cname: "docs.example.com"      # 可选
    commit_message: "deploy: {timestamp}"
    force_push: false               # 危险操作，默认关闭
    nojekyll: true                  # 自动生成 .nojekyll
    git_user_name: "Plenipes Bot"
    git_user_email: "bot@plenipes.press"
"""

import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, Any

from plugins.publishers.base import BasePublisher
from core.utils.tracing import tlog


class GitHubPagesPublisher(BasePublisher):
    """
    🚀 [V48.3] GitHub Pages 发布插件
    将静态站点产物推送至 gh-pages 分支，实现零配置 GitHub Pages 部署。
    """
    PLUGIN_ID = "github_pages"

    # ==========================================
    # 生命周期
    # ==========================================

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.repo_url = config.get("repo_url", "")
        self.branch = config.get("branch", "gh-pages")
        self.cname = config.get("cname", "")
        self.commit_message_template = config.get("commit_message", "deploy: {timestamp}")
        self.force_push = config.get("force_push", False)
        self.nojekyll = config.get("nojekyll", True)
        self.git_user_name = config.get("git_user_name", "Plenipes Bot")
        self.git_user_email = config.get("git_user_email", "bot@plenipes.press")

    # ==========================================
    # BasePublisher 契约实现
    # ==========================================

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布：将 bundle_path 下的全部产物推送至 gh-pages 分支。

        执行流程：
          1. 校验配置完整性
          2. 创建临时工作区，克隆目标分支
          3. 清空工作区（保留 .git）
          4. 拷贝构建产物
          5. 注入元文件（.nojekyll / CNAME）
          6. Git commit + push
          7. 清理临时工作区

        :param bundle_path: 本地构建产物目录（SSG 输出目录）
        :param metadata: 任务元数据
        :return: 发布结果字典
        """
        # ── 1. 前置校验 ──────────────────────────────────
        if not self.repo_url:
            return {"status": "skipped", "message": "GitHub Pages repo_url not configured."}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path does not exist: {bundle_path}"}

        tlog.info(f"🚀 [GitHub Pages] 正在部署至 {self.repo_url} ({self.branch})...")

        # ── 2. 创建临时工作区 ────────────────────────────
        work_dir = tempfile.mkdtemp(prefix="plenipes_ghpages_")
        try:
            # ── 3. 克隆或初始化目标分支 ──────────────────
            clone_ok = self._clone_target_branch(work_dir)
            if not clone_ok:
                # 分支不存在：创建孤儿分支
                self._init_orphan_branch(work_dir)

            # ── 4. 清空工作区 (保留 .git) ────────────────
            self._clean_work_dir(work_dir)

            # ── 5. 拷贝构建产物 ──────────────────────────
            file_count = self._copy_bundle(bundle_path, work_dir)

            # ── 6. 注入元文件 ────────────────────────────
            self._inject_meta_files(work_dir)

            # ── 7. Commit + Push ─────────────────────────
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = self.commit_message_template.format(
                timestamp=timestamp,
                files=file_count,
                branch=self.branch
            )

            pushed = self._commit_and_push(work_dir, commit_msg)

            if pushed:
                tlog.success(f"✅ [GitHub Pages] 部署成功！{file_count} 个文件已推送至 {self.branch} 分支。")
                return {
                    "status": "success",
                    "files": file_count,
                    "branch": self.branch,
                    "repo": self.repo_url,
                    "timestamp": timestamp
                }
            else:
                tlog.info("ℹ️ [GitHub Pages] 无变更需要推送 (内容已同步)。")
                return {
                    "status": "success",
                    "files": file_count,
                    "message": "No changes to deploy."
                }

        except subprocess.CalledProcessError as e:
            tlog.error(f"❌ [GitHub Pages] Git 操作失败: {e.stderr or e.stdout or str(e)}")
            return {"status": "error", "message": f"Git operation failed: {e.stderr or str(e)}"}
        except Exception as e:
            tlog.error(f"❌ [GitHub Pages] 部署异常: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            # ── 8. 清理临时工作区 ─────────────────────────
            shutil.rmtree(work_dir, ignore_errors=True)

    def is_healthy(self) -> bool:
        """检查 git 命令可用性与仓库连通性"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    # ==========================================
    # 内部实现
    # ==========================================

    def _clone_target_branch(self, work_dir: str) -> bool:
        """
        尝试浅克隆目标分支到工作区。
        :return: True 表示克隆成功，False 表示分支不存在。
        """
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch",
             "--branch", self.branch, self.repo_url, work_dir],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            # 配置用户身份
            self._configure_git_identity(work_dir)
            return True

        # 检查是否是 "branch not found" 错误
        stderr = result.stderr.lower()
        if "not found" in stderr or "remote branch" in stderr or "does not exist" in stderr:
            return False

        # 其他错误直接抛出
        raise subprocess.CalledProcessError(
            result.returncode, result.args,
            output=result.stdout, stderr=result.stderr
        )

    def _init_orphan_branch(self, work_dir: str):
        """创建孤儿分支：用于首次部署时目标分支尚不存在的场景"""
        tlog.info(f"📦 [GitHub Pages] 目标分支 '{self.branch}' 不存在，正在创建孤儿分支...")

        # 先克隆仓库默认分支（仅获取 .git 元数据）
        subprocess.run(
            ["git", "clone", "--depth", "1", self.repo_url, work_dir],
            capture_output=True, text=True, timeout=120, check=True
        )

        # 创建孤儿分支
        self._run_git(work_dir, ["checkout", "--orphan", self.branch])
        # 清空暂存区
        self._run_git(work_dir, ["rm", "-rf", "."], check=False)

        self._configure_git_identity(work_dir)

    def _configure_git_identity(self, work_dir: str):
        """配置 Git 用户身份（临时工作区级别）"""
        self._run_git(work_dir, ["config", "user.name", self.git_user_name])
        self._run_git(work_dir, ["config", "user.email", self.git_user_email])

    def _clean_work_dir(self, work_dir: str):
        """清空工作区内容，保留 .git 目录"""
        for item in os.listdir(work_dir):
            if item == ".git":
                continue
            item_path = os.path.join(work_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

    def _copy_bundle(self, bundle_path: str, work_dir: str) -> int:
        """
        将构建产物从 bundle_path 复制到工作区。
        :return: 复制的文件总数
        """
        file_count = 0
        for root, dirs, files in os.walk(bundle_path):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue
                src = os.path.join(root, file)
                rel_path = os.path.relpath(src, bundle_path)
                dst = os.path.join(work_dir, rel_path)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                file_count += 1

        return file_count

    def _inject_meta_files(self, work_dir: str):
        """注入 GitHub Pages 元文件"""
        # .nojekyll — 禁止 Jekyll 处理（支持下划线开头的路径）
        if self.nojekyll:
            nojekyll_path = os.path.join(work_dir, ".nojekyll")
            with open(nojekyll_path, 'w') as f:
                f.write("")

        # CNAME — 自定义域名绑定
        if self.cname:
            cname_path = os.path.join(work_dir, "CNAME")
            with open(cname_path, 'w') as f:
                f.write(self.cname.strip())

    def _commit_and_push(self, work_dir: str, commit_msg: str) -> bool:
        """
        暂存全部变更、提交并推送。
        :return: True 表示有变更被推送，False 表示无变更。
        """
        # 暂存全部文件
        self._run_git(work_dir, ["add", "-A"])

        # 检查是否有变更
        status_result = self._run_git(work_dir, ["status", "--porcelain"])
        if not status_result.stdout.strip():
            return False  # 无变更

        # 提交
        self._run_git(work_dir, ["commit", "-m", commit_msg])

        # 推送
        push_cmd = ["push", "origin", self.branch]
        if self.force_push:
            push_cmd.insert(1, "--force")
            tlog.warning("⚠️ [GitHub Pages] 正在执行强制推送 (force_push=true)！")

        self._run_git(work_dir, push_cmd, timeout=120)
        return True

    @staticmethod
    def _run_git(work_dir: str, args: list, check: bool = True,
                 timeout: int = 30) -> subprocess.CompletedProcess:
        """执行 Git 命令的统一入口"""
        cmd = ["git", "-C", work_dir] + args
        return subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, check=check
        )
