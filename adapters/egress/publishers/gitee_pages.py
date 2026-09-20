#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Gitee Pages Publisher Plugin
🚀 [V24.0]：将静态站点产物推送至 Gitee pages 分支，支持 API Rebuild 触发。
🛡️ [SOP-01 & SOP-02]：自底向上物理拆分重构版本，单文件物理行数严格 ≤300 行。
"""

import os
import shutil
import subprocess
import tempfile
import re
import requests
from datetime import datetime
from typing import Dict, Any

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog
from .gitee_pages_git import GiteePagesGitOpsMixin


class GiteePagesPublisher(BasePublisher, GiteePagesGitOpsMixin):
    """
    🚀 [V24.0] Gitee Pages 发布插件
    将静态站点产物推送至 Gitee，实现零配置 Gitee Pages 部署。
    """
    PLUGIN_ID = "gitee_pages"
    DISPLAY_NAME = "Gitee Pages"
    VERSION = "V1.0"
    DESCRIPTION = "自动将渲染后的静态站点推送至指定 Gitee 仓库的 pages 分支，并可选调用 API 触发重新编译。"

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.repo_url = config.get("repo_url", "")
        self.branch = config.get("branch", "master")
        self.cname = config.get("cname", "")
        self.commit_message_template = config.get("commit_message", "deploy: {timestamp}")
        self.force_push = config.get("force_push", False)
        self.git_user_name = config.get("git_user_name", "Plenipes Bot")
        self.git_user_email = config.get("git_user_email", "bot@plenipes.press")
        self.token = config.get("token", "") or config.get("gitee_token", "")
        self.trigger_build = config.get("trigger_build", True)
        self.verbose_copy = config.get("verbose_copy", False)

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """🚀 执行物理发布：将 bundle_path 下的全部产物推送至指定分支。"""
        if not self.repo_url:
            return {"status": "skipped", "message": "Gitee Pages repo_url not configured."}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path does not exist: {bundle_path}"}

        tlog.info(f"🚀 [Gitee Pages] 正在部署至 {self.repo_url} ({self.branch})...")

        work_dir = tempfile.mkdtemp(prefix="plenipes_giteepages_")
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
                tlog.success(f"✅ [Gitee Pages] 部署成功！{copied_count} 个文件已推送至 {self.branch} 分支。")
            else:
                tlog.info("ℹ️ [Gitee Pages] 无变更需要推送 (内容已同步)。")

            # 触发 Gitee Pages 自动编译服务 API
            self._trigger_gitee_pages_rebuild()

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
            tlog.error(f"❌ [Gitee Pages] Git 操作失败: {masked_err}")
            return {"status": "error", "message": f"Git operation failed: {suggested_err}"}
        except Exception as e:
            err_msg = str(e)
            masked_err = self._mask_url_credentials(err_msg)
            suggested_err = self._add_autotherapy_suggestion(masked_err)
            tlog.error(f"❌ [Gitee Pages] 部署异常: {masked_err}")
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

    def _trigger_gitee_pages_rebuild(self):
        """利用 Gitee Token 自动通过 API 触发 Gitee Pages 自动编译服务。"""
        token = self.token or os.environ.get("GITEE_TOKEN", "")
        if not self.trigger_build or not token or not self.repo_url:
            return

        match = re.search(r'gitee\.com/([^/]+)/([^/\.]+)', self.repo_url)
        if not match:
            tlog.warning(f"⚠️ [Gitee Pages] 无法从仓库 URL '{self.repo_url}' 中解析出所有者和仓库名，跳过 API 编译触发。")
            return

        owner = match.group(1)
        repo = match.group(2)
        build_url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/pages/builds"

        tlog.info("📡 [Gitee Pages] 正在尝试通过 API 触发云端 Pages 编译...")
        try:
            proxy = self.get_proxy()
            proxies = {"http": proxy, "https": proxy} if proxy else None
            resp = requests.post(build_url, data={"access_token": token}, proxies=proxies, timeout=10)
            if resp.status_code in (200, 201):
                tlog.success("✅ [Gitee Pages] API 重新编译请求成功触发！云端正在构建最新部署。")
            else:
                tlog.warning(f"⚠️ [Gitee Pages] 触发 API 编译失败，状态码: {resp.status_code}，响应: {resp.text}")
        except Exception as e:
            tlog.warning(f"⚠️ [Gitee Pages] 触发 API 编译异常: {e}")
