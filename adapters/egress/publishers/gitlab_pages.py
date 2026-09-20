#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — GitLab Pages Publisher Plugin
🚀 [V24.0]：将静态站点产物推送至 GitLab 仓库，支持 GitLab Pages 自动流水线部署。
🛡️ [SOP-01 & SOP-02]：自底向上物理拆分重构版本，单文件物理行数严格 ≤300 行。
"""

import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, Any

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog
from .gitlab_pages_git import GitLabPagesGitOpsMixin


class GitLabPagesPublisher(BasePublisher, GitLabPagesGitOpsMixin):
    """
    🚀 [V24.0] GitLab Pages 发布插件
    将静态站点产物推送至 GitLab，实现零配置 GitLab Pages 部署。
    """
    PLUGIN_ID = "gitlab_pages"
    DISPLAY_NAME = "GitLab Pages"
    VERSION = "V1.0"
    DESCRIPTION = "自动将渲染后的静态站点推送至指定 GitLab 仓库，支持自动生成 pages 流水线。"

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.repo_url = config.get("repo_url", "")
        self.branch = config.get("branch", "main")
        self.commit_message_template = config.get("commit_message", "deploy: {timestamp}")
        self.force_push = config.get("force_push", False)
        self.git_user_name = config.get("git_user_name", "Plenipes Bot")
        self.git_user_email = config.get("git_user_email", "bot@plenipes.press")
        self.token = config.get("token", "") or config.get("access_token", "")
        self.verbose_copy = config.get("verbose_copy", False)

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """🚀 执行物理发布：将 bundle_path 下的全部产物推送至指定分支。"""
        if not self.repo_url:
            return {"status": "skipped", "message": "GitLab Pages repo_url not configured."}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path does not exist: {bundle_path}"}

        tlog.info(f"🚀 [GitLab Pages] 正在部署至 {self.repo_url} ({self.branch})...")

        work_dir = tempfile.mkdtemp(prefix="plenipes_gitlabpages_")
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
                tlog.success(f"✅ [GitLab Pages] 部署成功！{copied_count} 个文件已推送至 {self.branch} 分支。")
            else:
                tlog.info("ℹ️ [GitLab Pages] 无变更需要推送 (内容已同步)。")

            return {
                "status": "success",
                "files": copied_count,
                "branch": self.branch,
                "repo": self.repo_url,
                "timestamp": timestamp
            }

        except subprocess.CalledProcessError as e:
            err_msg = e.stderr or e.stdout or str(e)
            masked_err = self._mask_url_credentials(err_msg)
            suggested_err = self._add_autotherapy_suggestion(masked_err)
            tlog.error(f"❌ [GitLab Pages] Git 操作失败: {masked_err}")
            return {"status": "error", "message": f"Git operation failed: {suggested_err}"}
        except Exception as e:
            err_msg = str(e)
            masked_err = self._mask_url_credentials(err_msg)
            suggested_err = self._add_autotherapy_suggestion(masked_err)
            tlog.error(f"❌ [GitLab Pages] 部署异常: {masked_err}")
            return {"status": "error", "message": suggested_err}
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def is_healthy(self) -> bool:
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
