#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Gitee Pages Publisher Plugin
🚀 [V24.0]：将静态站点产物推送至 Gitee pages 分支，支持 API Rebuild 触发。
"""

import os
import shutil
import subprocess
import tempfile
import requests
import re
from datetime import datetime
from typing import Dict, Any, Tuple, List

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog


class GiteePagesPublisher(BasePublisher):
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

    def _get_authenticated_repo_url(self) -> str:
        """
        🚀 动态组装带有 OAuth Token 的 HTTPS 克隆/推送 URL。
        若无 Token，或 URL 格式不符合要求，则原样返回 repo_url。
        """
        url = self.repo_url
        token = self.token or os.environ.get("GITEE_TOKEN", "")
        if not token or not url:
            return url

        # 针对 Gitee HTTPS/HTTP 地址进行 Token 注入
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
        """
        🔒 抹除文本中可能夹带的明文 Token 凭证（用 *** 代替）。
        """
        if not text:
            return text
        return re.sub(r'(https?://oauth2:)([^@\s]+)(@)', r'\1***\3', text)

    def _add_autotherapy_suggestion(self, err_msg: str) -> str:
        """
        💡 为网络连接或 SSL 握手失败的报错信息注入高情商物理自愈提示。
        """
        if not err_msg:
            return err_msg

        network_keywords = ["unable to access", "ssl_error", "ssl_connect", "timed out", "could not resolve host", "connection refused"]
        if any(kw in err_msg.lower() for kw in network_keywords):
            tlog.warning("💡 [自愈建议] 检测到本地网络在直连 gitee.com 时超时或 SSL 握手失败。")
            tlog.warning("   1. 检查本地代理：如果使用了代理工具，请确保已正确配置 git 全局代理，例如：")
            tlog.warning("      git config --global http.proxy http://127.0.0.1:您的代理端口")
            tlog.warning("   2. 切换 SSH 协议：如果您已配置 Gitee SSH Key，强烈建议在后台配置中将仓库 URL 更改为 SSH 格式：")
            tlog.warning("      git@gitee.com:您的用户名/您的仓库名.git")

            return (
                f"{err_msg}\n\n"
                "💡 [自愈建议] 检测到本地网络在直连 gitee.com 时超时或 SSL 握手失败。\n"
                "1. 检查本地代理：如果使用了代理工具，请在终端尝试配置 Git 代理，例如：\n"
                "   git config --global http.proxy http://127.0.0.1:您的代理端口\n"
                "2. 切换 SSH 协议：如果您已配置 Gitee SSH Key，强烈建议将仓库 URL 更改为 SSH 格式：\n"
                "   git@gitee.com:您的用户名/您的仓库名.git\n"
                "   SSH 协议通常比 HTTPS 更加稳定，能有效避开 SSL 握手错误！"
            )
        return err_msg

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布：将 bundle_path 下的全部产物推送至指定分支。
        """
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
                if item == ".git": continue
                item_path = os.path.join(work_dir, item)
                if os.path.isdir(item_path): shutil.rmtree(item_path)
                else: os.remove(item_path)
            return

        for root, dirs, files in os.walk(work_dir, topdown=False):
            if ".git" in root.split(os.sep): continue
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
                    try: os.remove(abs_work)
                    except: pass
            for d in dirs:
                abs_dir = os.path.join(root, d)
                if not os.listdir(abs_dir):
                    try: os.rmdir(abs_dir)
                    except: pass

    def _copy_bundle(self, bundle_path: str, work_dir: str) -> Tuple[int, int]:
        copied_count = 0
        skipped_count = 0
        tlog.info(f"🔍 [Gitee Pages] 正在从 {bundle_path} 拷贝文件至临时区 {work_dir}...")
        for root, dirs, files in os.walk(bundle_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'): continue
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

    def _trigger_gitee_pages_rebuild(self):
        """
        🚀 利用 Gitee Token 自动通过 API 触发 Gitee Pages 自动编译服务。
        """
        token = self.token or os.environ.get("GITEE_TOKEN", "")
        if not self.trigger_build or not token or not self.repo_url:
            return

        # 解析 owner 和 repo
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
