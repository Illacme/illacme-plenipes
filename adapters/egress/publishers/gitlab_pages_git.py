#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — GitLab Pages Git Operations Shard
模块职责：负责 GitLab Pages 的 Git 仓库克隆、分支切换、孤儿分支初始化、产物同步与推送。
🛡️ [SOP-01 & SOP-02]：从 gitlab_pages.py 物理拆解出的 Git 操作能力 Mixin。
"""

import os
import shutil
import subprocess
import re
from typing import Tuple
from core.utils.tracing import tlog


class GitLabPagesGitOpsMixin:
    """GitLab Pages Git 物理操作与 CI 生成 Mixin"""

    def _get_authenticated_repo_url(self) -> str:
        """🚀 动态组装带有 OAuth / Personal Access Token 的 HTTPS 克隆/推送 URL。"""
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
        """🔒 抹除文本中可能夹带的明文 Token 凭证（用 *** 代替）。"""
        if not text:
            return text
        return re.sub(r'(https?://oauth2:)([^@\s]+)(@)', r'\1***\3', text)

    def _add_autotherapy_suggestion(self, err_msg: str) -> str:
        """💡 为网络连接或 SSL 握手失败的报错信息注入物理自愈提示。"""
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
        """🛡️ 清空目标目录中的旧网页文件，保留 .git 及 .gitlab-ci.yml"""
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
                dst_public = os.path.join(target_public_dir, file)
                shutil.copy2(src_file, dst_public)
                dst_root = os.path.join(target_root_dir, file)
                shutil.copy2(src_file, dst_root)
                copied += 1

        return copied, skipped

    def _inject_meta_files(self, work_dir: str):
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
