#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Gitee Pages Git Operations Shard
模块职责：负责 Gitee Pages 的 Git 克隆、分支初始化、产物同步与凭据脱敏。
🛡️ [SOP-01 & SOP-02]：从 gitee_pages.py 物理拆解出的 Git 操作能力 Mixin。
"""

import os
import shutil
import subprocess
import re
from typing import Tuple, List
from core.utils.tracing import tlog


class GiteePagesGitOpsMixin:
    """Gitee Pages Git 物理操作能力 Mixin"""

    def _get_authenticated_repo_url(self) -> str:
        """动态组装带有 OAuth Token 的 HTTPS 克隆/推送 URL。"""
        url = self.repo_url
        token = self.token or os.environ.get("GITEE_TOKEN", "")
        if not token or not url:
            return url

        if url.startswith("https://") and "gitee.com/" in url:
            clean_url = url.replace("https://", "")
            if "@" in clean_url:
                clean_url = clean_url.split("@", 1)[1]
            return f"https://oauth2:{token}@{clean_url}"
        elif url.startswith("http://") and "gitee.com/" in url:
            clean_url = url.replace("http://", "")
            if "@" in clean_url:
                clean_url = clean_url.split("@", 1)[1]
            return f"http://oauth2:{token}@{clean_url}"

        return url

    def _mask_url_credentials(self, text: str) -> str:
        """抹除文本中可能夹带的明文 Token 凭证（用 *** 代替）。"""
        if not text:
            return text
        return re.sub(r'(https?://oauth2:)([^@\s]+)(@)', r'\1***\3', text)

    def _add_autotherapy_suggestion(self, err_msg: str) -> str:
        """为网络连接或 SSL 握手失败的报错信息注入高情商物理自愈提示。"""
        if not err_msg:
            return err_msg

        network_keywords = ["unable to access", "ssl_error", "ssl_connect", "timed out", "could not resolve host", "connection refused"]
        if any(kw in err_msg.lower() for kw in network_keywords):
            return (
                f"{err_msg}\n\n"
                "💡 [自愈建议] 检测到本地网络在直连 gitee.com 时超时或 SSL 握手失败。\n"
                "1. 检查本地代理：如果使用了代理工具，请在终端尝试配置 Git 代理。\n"
                "2. 切换 SSH 协议：如果您已配置 Gitee SSH Key，强烈建议将仓库 URL 更改为 SSH 格式 (git@gitee.com:owner/repo.git)。"
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
        tlog.info(f"📦 [Gitee Pages] 目标分支 '{self.branch}' 不存在，正在创建孤儿分支...")
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
            safe_stderr = self._mask_url_credentials(e.stderr) if e.stderr else None
            safe_stdout = self._mask_url_credentials(e.stdout) if e.stdout else None
            raise subprocess.CalledProcessError(
                e.returncode, safe_args,
                output=safe_stdout, stderr=safe_stderr
            )

        self._run_git(work_dir, ["checkout", "--orphan", self.branch])
        self._run_git(work_dir, ["rm", "-rf", "."], check=False)
        self._configure_git_identity(work_dir)

    def _configure_git_identity(self, work_dir: str):
        self._run_git(work_dir, ["config", "user.name", self.git_user_name])
        self._run_git(work_dir, ["config", "user.email", self.git_user_email])

    def _clean_work_dir(self, work_dir: str, bundle_path: str = None):
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
                    except Exception:
                        pass
            for d in dirs:
                abs_dir = os.path.join(root, d)
                if not os.listdir(abs_dir):
                    try:
                        os.rmdir(abs_dir)
                    except Exception:
                        pass

    def _copy_bundle(self, bundle_path: str, work_dir: str) -> Tuple[int, int]:
        copied_count = 0
        skipped_count = 0
        tlog.info(f"🔍 [Gitee Pages] 正在从 {bundle_path} 拷贝文件至临时区 {work_dir}...")
        for root, dirs, files in os.walk(bundle_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'):
                    continue
                if file.endswith('.md') or file.endswith('.mdx') or file.endswith('.markdown') or file.endswith('.mdown'):
                    tlog.warning(f"🛡️ [安全拦截] 过滤丢弃源 Markdown 文件: {file}")
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
                    copied_count += 1
                else:
                    skipped_count += 1
        return copied_count, skipped_count

    def _inject_meta_files(self, work_dir: str):
        if self.cname:
            cname_path = os.path.join(work_dir, "CNAME")
            with open(cname_path, "w", encoding="utf-8") as f:
                f.write(self.cname.strip())

    def _commit_and_push(self, work_dir: str, commit_msg: str) -> bool:
        self._run_git(work_dir, ["add", "-A"])
        
        status_res = self._run_git(work_dir, ["status", "--porcelain"])
        if not status_res.strip():
            return False

        self._run_git(work_dir, ["commit", "-m", commit_msg])

        push_args = ["push"]
        if self.force_push:
            push_args.append("-f")
        push_args.extend(["origin", self.branch])

        self._run_git(work_dir, push_args)
        return True

    def _run_git(self, work_dir: str, args: List[str], check: bool = True) -> str:
        cmd = ["git"] + args
        env = os.environ.copy()
        proxy = self.get_proxy()
        if proxy:
            env["HTTP_PROXY"] = proxy
            env["HTTPS_PROXY"] = proxy
            env["http_proxy"] = proxy
            env["https_proxy"] = proxy
        result = subprocess.run(
            cmd, cwd=work_dir, env=env,
            capture_output=True, text=True, timeout=120
        )
        if check and result.returncode != 0:
            safe_args = [self._mask_url_credentials(arg) for arg in cmd]
            safe_stderr = self._mask_url_credentials(result.stderr)
            safe_stdout = self._mask_url_credentials(result.stdout)
            raise subprocess.CalledProcessError(
                result.returncode, safe_args,
                output=safe_stdout, stderr=safe_stderr
            )
        return result.stdout
