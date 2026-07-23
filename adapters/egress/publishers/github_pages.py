#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — GitHub Pages Publisher Plugin (Facade Hub)
🚀 [V48.3]：将静态站点产物推送至 gh-pages 分支，支持懒卸载与增量对齐。
职责：主 Publisher 部署门面类，聚合物理分片逻辑并零破坏代理导出。
"""

import os
import shutil
import tempfile
import subprocess
from datetime import datetime
from typing import Dict, Any, Tuple

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog

# 引入分片逻辑实现
from .github_pages_shards.security_ops import (
    get_authenticated_repo_url_impl,
    mask_url_credentials_impl,
    add_autotherapy_suggestion_impl
)
from .github_pages_shards.cloud_api_ops import (
    auto_create_github_repo_impl,
    parse_owner_repo_impl,
    auto_enable_github_pages_impl
)
from .github_pages_shards.git_workspace_ops import (
    run_git_impl,
    configure_git_identity_impl,
    clone_target_branch_impl,
    init_orphan_branch_impl,
    clean_work_dir_impl,
    copy_bundle_impl,
    inject_meta_files_impl,
    commit_and_push_impl
)


class GitHubPagesPublisher(BasePublisher):
    """
    🚀 [V48.3] GitHub Pages 发布插件
    将静态站点产物推送至 gh-pages 分支，实现零配置 GitHub Pages 部署。
    """
    PLUGIN_ID = "github_pages"
    DISPLAY_NAME = "GitHub Pages"
    VERSION = "V3.5"
    DESCRIPTION = "自动将渲染后的静态站点推送至指定 GitHub 仓库的 gh-pages 分支。"

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
        self.token = config.get("token", "") or config.get("git_token", "")
        self.verbose_copy = config.get("verbose_copy", False)

    # ── 安全与凭据辅助方法 ─────────────────────────────────
    def _get_authenticated_repo_url(self) -> str:
        return get_authenticated_repo_url_impl(self.repo_url, self.token)

    def _mask_url_credentials(self, text: str) -> str:
        return mask_url_credentials_impl(text)

    def _add_autotherapy_suggestion(self, err_msg: str) -> str:
        return add_autotherapy_suggestion_impl(err_msg)

    # ── 云端 API 自愈方法 ─────────────────────────────────
    def _auto_create_github_repo(self) -> bool:
        return auto_create_github_repo_impl(self)

    def _parse_owner_repo(self) -> tuple[str, str]:
        return parse_owner_repo_impl(self.repo_url, self.token)

    def _auto_enable_github_pages(self) -> str:
        return auto_enable_github_pages_impl(self)

    # ── Git 物理工作区操作 ────────────────────────────────
    def _run_git(self, work_dir: str, args: list, check: bool = True, timeout: int = 30) -> subprocess.CompletedProcess:
        return run_git_impl(self, work_dir, args, check, timeout)

    def _configure_git_identity(self, work_dir: str):
        return configure_git_identity_impl(self, work_dir)

    def _clone_target_branch(self, work_dir: str) -> bool:
        return clone_target_branch_impl(self, work_dir)

    def _init_orphan_branch(self, work_dir: str):
        return init_orphan_branch_impl(self, work_dir)

    def _clean_work_dir(self, work_dir: str, bundle_path: str = None):
        return clean_work_dir_impl(self, work_dir, bundle_path)

    def _copy_bundle(self, bundle_path: str, work_dir: str) -> Tuple[int, int]:
        return copy_bundle_impl(self, bundle_path, work_dir)

    def _inject_meta_files(self, work_dir: str):
        return inject_meta_files_impl(self, work_dir)

    def _commit_and_push(self, work_dir: str, commit_msg: str) -> bool:
        return commit_and_push_impl(self, work_dir, commit_msg)

    # ── BasePublisher 核心契约 ─────────────────────────────
    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布：将 bundle_path 下的全部产物推送至 gh-pages 分支。
        """
        if not self.repo_url:
            return {"status": "skipped", "message": "GitHub Pages repo_url not configured."}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path does not exist: {bundle_path}"}

        tlog.info(f"🚀 [GitHub Pages] 正在部署至 {self.repo_url} ({self.branch})...")

        work_dir = tempfile.mkdtemp(prefix="plenipes_ghpages_")
        try:
            clone_ok = self._clone_target_branch(work_dir)
            if not clone_ok:
                self._init_orphan_branch(work_dir)

            self._clean_work_dir(work_dir, bundle_path)
            copied_count, skipped_count = self._copy_bundle(bundle_path, work_dir)
            self._inject_meta_files(work_dir)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = self.commit_message_template.format(
                timestamp=timestamp,
                files=copied_count,
                branch=self.branch
            )

            pushed = self._commit_and_push(work_dir, commit_msg)

            if pushed:
                pages_url = self._auto_enable_github_pages()
                tlog.success(f"✅ [GitHub Pages] 部署成功！{copied_count} 个文件已推送至 {self.branch} 分支。")
                return {
                    "status": "success",
                    "files": copied_count,
                    "branch": self.branch,
                    "repo": self.repo_url,
                    "url": pages_url,
                    "pages_base_url": pages_url,
                    "timestamp": timestamp
                }
            else:
                pages_url = self._auto_enable_github_pages()
                tlog.info("ℹ️ [GitHub Pages] 无变更需要推送 (内容已同步)。")
                return {
                    "status": "success",
                    "files": copied_count,
                    "url": pages_url,
                    "pages_base_url": pages_url,
                    "message": "No changes to deploy."
                }

        except subprocess.CalledProcessError as e:
            err_msg = e.stderr or e.stdout or str(e)
            masked_err = self._mask_url_credentials(err_msg)
            suggested_err = self._add_autotherapy_suggestion(masked_err)
            tlog.error(f"❌ [GitHub Pages] Git 操作失败: {masked_err}")
            return {"status": "error", "message": f"Git operation failed: {suggested_err}"}
        except Exception as e:
            err_msg = str(e)
            masked_err = self._mask_url_credentials(err_msg)
            suggested_err = self._add_autotherapy_suggestion(masked_err)
            tlog.error(f"❌ [GitHub Pages] 部署异常: {masked_err}")
            return {"status": "error", "message": suggested_err}
        finally:
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
