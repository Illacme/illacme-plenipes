#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — GitLab Pages Publisher Plugin
🚀 [V24.0]：将静态站点产物推送至 GitLab 仓库，支持 GitLab Pages 自动流水线部署。
"""

import os
import shutil
import subprocess
import tempfile
import re
from datetime import datetime
from typing import Dict, Any, Tuple

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog


class GitLabPagesPublisher(BasePublisher):
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

    def _get_authenticated_repo_url(self) -> str:
        """
        🚀 动态组装带有 OAuth / Personal Access Token 的 HTTPS 克隆/推送 URL。
        """
        url = self.repo_url
        token = self.token or os.environ.get("GITLAB_TOKEN", "")
        if not token or not url:
            return url

        if url.startswith("https://") and "gitlab.com" in url:
            clean_url = url.replace("https://", "")
            if "@" in clean_url:
                clean_url = clean_url.split("@", 1)[1]
            return f"https://oauth2:{token}@{clean_url}"
        elif url.startswith("http://") and "gitlab.com" in url:
            clean_url = url.replace("http://", "")
            if "@" in clean_url:
                clean_url = clean_url.split("@", 1)[1]
            return f"http://oauth2:{token}@{clean_url}"

        return url

    def _mask_url_credentials(self, text: str) -> str:
        """
        🔒 抹除文本中可能夹带的明文 Token 凭证（用 *** 代替）。
        """
        if not text:
            return text
        return re.sub(r'(https?://oauth2:)([^@\s]+)(@)', r'\1***\3', text)

    def _add_autotherapy_suggestion(self, err_msg: str) -> str:
        """
        💡 为网络连接或 SSL 握手失败的报错信息注入物理自愈提示。
        """
        if not err_msg:
            return err_msg

        network_keywords = ["unable to access", "ssl_error", "ssl_connect", "timed out", "could not resolve host", "connection refused"]
        if any(kw in err_msg.lower() for kw in network_keywords):
            return (
                f"{err_msg}\n\n"
                "💡 [自愈建议] 检测到本地网络在直连 gitlab.com 时超时或 SSL 握手失败。\n"
                "1. 检查本地代理：如果使用了代理工具，请在当前渠道配置代理或设置 Git 代理。\n"
                "2. 切换 SSH 协议：如果您已配置 GitLab SSH Key，建议将仓库 URL 更改为 SSH 格式 (git@gitlab.com:owner/repo.git)。"
            )
        return err_msg

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布：将 bundle_path 下的全部产物推送至指定分支。
        """
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

    def _clone_target_branch(self, work_dir: str) -> bool:
        auth_url = self._get_authenticated_repo_url()
        env = os.environ.copy()
        proxy = self.get_proxy()
        if proxy:
            env["HTTP_PROXY"] = proxy
            env["HTTPS_PROXY"] = proxy
            env["http_proxy"] = proxy
            env["https_proxy"] = proxy
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch",
             "--branch", self.branch, auth_url, work_dir],
            env=env, capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            self._configure_git_identity(work_dir)
            return True

        stderr = result.stderr.lower()
        if "not found" in stderr or "remote branch" in stderr or "does not exist" in stderr:
            return False

        safe_args = [self._mask_url_credentials(arg) for arg in result.args]
        safe_stderr = self._mask_url_credentials(result.stderr)
        safe_stdout = self._mask_url_credentials(result.stdout)
        raise subprocess.CalledProcessError(
            result.returncode, safe_args,
            output=safe_stdout, stderr=safe_stderr
        )

    def _init_orphan_branch(self, work_dir: str):
        tlog.info(f"📦 [GitLab Pages] 目标分支 '{self.branch}' 不存在，正在创建孤儿分支...")
        auth_url = self._get_authenticated_repo_url()
        env = os.environ.copy()
        proxy = self.get_proxy()
        if proxy:
            env["HTTP_PROXY"] = proxy
            env["HTTPS_PROXY"] = proxy
            env["http_proxy"] = proxy
            env["https_proxy"] = proxy
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", auth_url, work_dir],
                env=env, capture_output=True, text=True, timeout=120, check=True
            )
        except subprocess.CalledProcessError as e:
            safe_args = [self._mask_url_credentials(arg) for arg in e.cmd]
            safe_stderr = self._mask_url_credentials(e.stderr or "")
            tlog.warning(f"⚠️ [GitLab Pages] 仓库可能为空仓库，正在执行本地初始化: {safe_stderr}")
            os.makedirs(work_dir, exist_ok=True)
            subprocess.run(["git", "init"], cwd=work_dir, check=True, capture_output=True)
            subprocess.run(["git", "remote", "add", "origin", auth_url], cwd=work_dir, check=True, capture_output=True)

        self._configure_git_identity(work_dir)

        # 切换或创建指定分支
        try:
            subprocess.run(
                ["git", "checkout", "--orphan", self.branch],
                cwd=work_dir, check=True, capture_output=True, text=True
            )
        except subprocess.CalledProcessError:
            subprocess.run(
                ["git", "checkout", "-b", self.branch],
                cwd=work_dir, check=True, capture_output=True, text=True
            )

    def _configure_git_identity(self, work_dir: str):
        subprocess.run(["git", "config", "user.name", self.git_user_name], cwd=work_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", self.git_user_email], cwd=work_dir, check=True, capture_output=True)

    def _clean_work_dir(self, work_dir: str, bundle_path: str = None):
        """
        🛡️ 清空目标目录中的旧网页文件，保留 .git 及 .gitlab-ci.yml
        """
        for item in os.listdir(work_dir):
            if item in [".git", ".gitlab-ci.yml"]:
                continue
            item_path = os.path.join(work_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path, ignore_errors=True)
            else:
                try:
                    os.remove(item_path)
                except OSError:
                    pass

    def _copy_bundle(self, bundle_path: str, work_dir: str) -> Tuple[int, int]:
        copied = 0
        skipped = 0

        # GitLab Pages 支持将文件直接放置在 public 目录或根目录（配合 Pages CI）
        # 默认将文件部署至 public 目录，同时在根目录保留 index.html
        public_dir = os.path.join(work_dir, "public")
        os.makedirs(public_dir, exist_ok=True)

        for root, dirs, files in os.walk(bundle_path):
            rel_dir = os.path.relpath(root, bundle_path)
            target_public_dir = os.path.join(public_dir, rel_dir) if rel_dir != "." else public_dir
            target_root_dir = os.path.join(work_dir, rel_dir) if rel_dir != "." else work_dir
            os.makedirs(target_public_dir, exist_ok=True)
            os.makedirs(target_root_dir, exist_ok=True)

            for file in files:
                src_file = os.path.join(root, file)
                # 写入 public 目录
                dst_public = os.path.join(target_public_dir, file)
                shutil.copy2(src_file, dst_public)
                # 根目录也写入一份以兼容各类 GitLab Pages 设置
                dst_root = os.path.join(target_root_dir, file)
                shutil.copy2(src_file, dst_root)
                copied += 1

        return copied, skipped

    def _inject_meta_files(self, work_dir: str):
        # 自动注入标准 GitLab Pages CI 脚本（若不存在）
        ci_path = os.path.join(work_dir, ".gitlab-ci.yml")
        if not os.path.exists(ci_path):
            ci_content = """# GitLab Pages Auto Deployment by Illacme Plenipes
pages:
  stage: deploy
  script:
    - mkdir -p public
    - cp -r * public/ 2>/dev/null || true
  artifacts:
    paths:
      - public
  rules:
    - if: $CI_COMMIT_BRANCH
"""
            try:
                with open(ci_path, "w", encoding="utf-8") as f:
                    f.write(ci_content)
            except Exception:
                pass

    def _commit_and_push(self, work_dir: str, commit_msg: str) -> bool:
        subprocess.run(["git", "add", "-A"], cwd=work_dir, check=True, capture_output=True)

        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=work_dir, capture_output=True, text=True, check=True
        )
        if not status_result.stdout.strip():
            return False

        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=work_dir, check=True, capture_output=True, text=True
        )

        push_cmd = ["git", "push", "origin", self.branch]
        if self.force_push:
            push_cmd.insert(2, "--force")

        env = os.environ.copy()
        proxy = self.get_proxy()
        if proxy:
            env["HTTP_PROXY"] = proxy
            env["HTTPS_PROXY"] = proxy
            env["http_proxy"] = proxy
            env["https_proxy"] = proxy

        result = subprocess.run(
            push_cmd, cwd=work_dir, capture_output=True, text=True, env=env, timeout=180
        )
        if result.returncode != 0:
            safe_args = [self._mask_url_credentials(arg) for arg in result.args]
            safe_stderr = self._mask_url_credentials(result.stderr)
            safe_stdout = self._mask_url_credentials(result.stdout)
            raise subprocess.CalledProcessError(
                result.returncode, safe_args,
                output=safe_stdout, stderr=safe_stderr
            )
        return True
