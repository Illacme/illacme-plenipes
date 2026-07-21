#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Git Publishing Helper Mixin
🚀 [V48.5]：提供通用的 Git 推送及凭证注入、克隆、差分对齐辅助方法。
"""

import os
import re
import shutil
import subprocess
from datetime import datetime
from typing import Dict, Any, Tuple
from core.utils.tracing import tlog


class GitPushMixin:
    """
    🚀 通用的 Git 推送混入类
    为 Render, Railway, Zeabur 等全站托管平台提供独立的 Git 推送自包含能力。
    """

    def _get_authenticated_repo_url(self, repo_url: str, token: str) -> str:
        """
        🚀 动态组装带有 OAuth Token 的 HTTPS 克隆/推送 URL。
        """
        if not token or not repo_url:
            return repo_url

        url = repo_url
        if "github.com" in url:
            prefix = "x-access-token"
        elif "gitee.com" in url:
            prefix = "oauth2"
        elif "gitlab.com" in url:
            prefix = "oauth2"
        else:
            prefix = "oauth2"

        if url.startswith("https://"):
            clean_url = url.replace("https://", "")
            if "@" in clean_url:
                clean_url = clean_url.split("@", 1)[1]
            return f"https://{prefix}:{token}@{clean_url}"
        elif url.startswith("http://"):
            clean_url = url.replace("http://", "")
            if "@" in clean_url:
                clean_url = clean_url.split("@", 1)[1]
            return f"http://{prefix}:{token}@{clean_url}"

        return url

    def _mask_url_credentials(self, text: str, token: str) -> str:
        """
        🔒 抹除文本中可能夹带的明文 Token 凭证（用 *** 代替）。
        """
        if not text:
            return text
        if token:
            text = text.replace(token, "***")
        return re.sub(r'(https?://[^:]+:[^@]+@)', r'\1***@', text)

    def _add_autotherapy_suggestion(self, err_msg: str) -> str:
        """
        💡 为网络连接或 SSL 握手失败的报错信息注入高情商物理自愈提示。
        """
        if not err_msg:
            return err_msg

        network_keywords = ["unable to access", "ssl_error", "ssl_connect", "timed out", "could not resolve host", "connection refused"]
        if any(kw in err_msg.lower() for kw in network_keywords):
            return (
                f"{err_msg}\n\n"
                "💡 [自愈建议] 检测到本地网络在直连 Git 托管服务时超时或 SSL 握手失败。\n"
                "1. 检查本地代理：如果使用了代理工具，请在终端尝试配置 Git 代理，例如：\n"
                "   git config --global http.proxy http://127.0.0.1:您的代理端口\n"
                "2. 切换 SSH 协议：如果您已配置 SSH Key，强烈建议将仓库 URL 更改为 SSH 格式：\n"
                "   git@github.com:您的用户名/您的仓库名.git 或 git@gitee.com:您的用户名/您的仓库名.git\n"
                "   SSH 协议通常比 HTTPS 更加稳定，能有效避开 SSL 握手错误！"
            )
        return err_msg

    def _run_git(self, work_dir: str, args: list, check: bool = True, timeout: int = 30) -> subprocess.CompletedProcess:
        """执行 Git 命令的统一入口"""
        cmd = ["git", "-C", work_dir] + args
        env = os.environ.copy()
        if hasattr(self, "get_proxy"):
            proxy = self.get_proxy()
            if proxy:
                env["HTTP_PROXY"] = proxy
                env["HTTPS_PROXY"] = proxy
                env["http_proxy"] = proxy
                env["https_proxy"] = proxy
        return subprocess.run(
            cmd, env=env, capture_output=True, text=True,
            timeout=timeout, check=check
        )

    def _clone_target_branch(self, work_dir: str, repo_url: str, token: str, branch: str, git_user_name: str, git_user_email: str) -> bool:
        """
        尝试浅克隆目标分支到工作区。
        """
        auth_url = self._get_authenticated_repo_url(repo_url, token)
        env = os.environ.copy()
        if hasattr(self, "get_proxy"):
            proxy = self.get_proxy()
            if proxy:
                env["HTTP_PROXY"] = proxy
                env["HTTPS_PROXY"] = proxy
                env["http_proxy"] = proxy
                env["https_proxy"] = proxy
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch",
             "--branch", branch, auth_url, work_dir],
            env=env, capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            self._configure_git_identity(work_dir, git_user_name, git_user_email)
            return True

        stderr = result.stderr.lower()
        if "not found" in stderr or "remote branch" in stderr or "does not exist" in stderr:
            return False

        safe_args = [self._mask_url_credentials(arg, token) for arg in result.args]
        safe_stderr = self._mask_url_credentials(result.stderr, token)
        safe_stdout = self._mask_url_credentials(result.stdout, token)
        raise subprocess.CalledProcessError(
            result.returncode, safe_args,
            output=safe_stdout, stderr=safe_stderr
        )

    def _init_orphan_branch(self, work_dir: str, repo_url: str, token: str, branch: str, git_user_name: str, git_user_email: str):
        """创建孤儿分支"""
        tlog.info(f"📦 [Git 辅助] 目标分支 '{branch}' 不存在，正在创建孤儿分支...")
        auth_url = self._get_authenticated_repo_url(repo_url, token)
        env = os.environ.copy()
        if hasattr(self, "get_proxy"):
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
            safe_args = [self._mask_url_credentials(arg, token) for arg in e.cmd]
            safe_stderr = self._mask_url_credentials(e.stderr, token) if e.stderr else None
            safe_stdout = self._mask_url_credentials(e.stdout, token) if e.stdout else None
            raise subprocess.CalledProcessError(
                e.returncode, safe_args,
                output=safe_stdout, stderr=safe_stderr
            )

        self._run_git(work_dir, ["checkout", "--orphan", branch])
        self._run_git(work_dir, ["rm", "-rf", "."], check=False)
        self._configure_git_identity(work_dir, git_user_name, git_user_email)

    def _configure_git_identity(self, work_dir: str, git_user_name: str, git_user_email: str):
        """配置 Git 用户身份"""
        self._run_git(work_dir, ["config", "user.name", git_user_name])
        self._run_git(work_dir, ["config", "user.email", git_user_email])

    def _clean_work_dir(self, work_dir: str, bundle_path: str = None):
        """清空工作区内容，保留 .git 目录及对应文件"""
        if not bundle_path:
            for item in os.listdir(work_dir):
                if item == ".git":
                    continue
                item_path = os.path.join(work_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            return

        for root, dirs, files in os.walk(work_dir, topdown=False):
            if ".git" in root.split(os.sep):
                continue
            for file in files:
                abs_work = os.path.join(root, file)
                rel = os.path.relpath(abs_work, work_dir)
                abs_bundle = os.path.join(bundle_path, rel)
                
                keep = False
                if os.path.exists(abs_bundle) and os.path.isfile(abs_bundle):
                    if os.path.getsize(abs_bundle) == os.path.getsize(abs_work):
                        if os.path.getmtime(abs_bundle) <= os.path.getmtime(abs_work):
                            keep = True
                if not keep:
                    try:
                        os.remove(abs_work)
                    except:
                        pass
            for d in dirs:
                abs_dir = os.path.join(root, d)
                if not os.listdir(abs_dir):
                    try:
                        os.rmdir(abs_dir)
                    except:
                        pass

    def _copy_bundle(self, bundle_path: str, work_dir: str, verbose_copy: bool = False) -> Tuple[int, int]:
        """将构建产物差分复制到工作区"""
        copied_count = 0
        skipped_count = 0
        copied_files = []
        for root, dirs, files in os.walk(bundle_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'):
                    continue
                # 禁止 Markdown 原稿文件拷贝
                if file.endswith('.md') or file.endswith('.mdx') or file.endswith('.markdown') or file.endswith('.mdown'):
                    continue
                src = os.path.join(root, file)
                rel_path = os.path.relpath(src, bundle_path)
                dst = os.path.join(work_dir, rel_path)
                
                need_copy = True
                if os.path.exists(dst):
                    if os.path.getsize(src) == os.path.getsize(dst):
                        need_copy = False
                if need_copy:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
                    copied_files.append(rel_path)
                    copied_count += 1
                else:
                    skipped_count += 1
        return copied_count, skipped_count

    def _commit_and_push(self, work_dir: str, commit_msg: str, branch: str, repo_url: str, token: str, force_push: bool = False) -> bool:
        """暂存、提交并推送"""
        self._run_git(work_dir, ["add", "-A"])
        status_result = self._run_git(work_dir, ["status", "--porcelain"])
        if not status_result.stdout.strip():
            return False  # 无变更

        self._run_git(work_dir, ["commit", "-m", commit_msg])
        push_cmd = ["push", "origin", branch]
        if force_push:
            push_cmd.insert(1, "--force")
        self._run_git(work_dir, push_cmd, timeout=120)
        return True
