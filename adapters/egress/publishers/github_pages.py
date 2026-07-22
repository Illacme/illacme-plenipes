#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — GitHub Pages Publisher Plugin
🚀 [V48.3]：将静态站点产物推送至 gh-pages 分支，支持懒卸载与增量对齐。
"""

import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, Any, Tuple

from core.adapters.egress.publishers.base import BasePublisher
from core.utils.tracing import tlog


class GitHubPagesPublisher(BasePublisher):
    """
    🚀 [V48.3] GitHub Pages 发布插件
    将静态站点产物推送至 gh-pages 分支，实现零配置 GitHub Pages 部署。
    """
    PLUGIN_ID = "github_pages"
    DISPLAY_NAME = "GitHub Pages"
    VERSION = "V3.5"
    DESCRIPTION = "自动将渲染后的静态站点推送至指定 GitHub 仓库的 gh-pages 分支。"

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
        self.token = config.get("token", "") or config.get("git_token", "")
        self.verbose_copy = config.get("verbose_copy", False)

    def _get_authenticated_repo_url(self) -> str:
        """
        🚀 动态组装带有 OAuth Token 的 HTTPS 克隆/推送 URL。
        若无 Token，或 URL 格式不符合要求，则原样返回 repo_url。
        """
        url = self.repo_url
        token = self.token or os.environ.get("GITHUB_TOKEN", "")
        if not token or not url:
            return url

        # 针对 GitHub HTTPS/HTTP 地址进行 Token 注入
        if url.startswith("https://") and "github.com/" in url:
            clean_url = url.replace("https://", "")
            if "@" in clean_url:
                clean_url = clean_url.split("@", 1)[1]
            return f"https://x-access-token:{token}@{clean_url}"
        elif url.startswith("http://") and "github.com/" in url:
            clean_url = url.replace("http://", "")
            if "@" in clean_url:
                clean_url = clean_url.split("@", 1)[1]
            return f"http://x-access-token:{token}@{clean_url}"

        return url

    def _mask_url_credentials(self, text: str) -> str:
        """
        🔒 抹除文本中可能夹带的明文 Token 凭证（用 *** 代替）。
        """
        if not text:
            return text
        import re
        return re.sub(r'(https?://x-access-token:)([^@\s]+)(@)', r'\1***\3', text)

    def _add_autotherapy_suggestion(self, err_msg: str) -> str:
        """
        💡 为网络连接或 SSL 握手失败的报错信息注入高情商物理自愈提示。
        """
        if not err_msg:
            return err_msg

        network_keywords = ["unable to access", "ssl_error", "ssl_connect", "timed out", "could not resolve host", "connection refused"]
        if any(kw in err_msg.lower() for kw in network_keywords):
            tlog.warning("💡 [自愈建议] 检测到本地网络在直连 github.com 时超时或 SSL 握手失败。")
            tlog.warning("   1. 检查本地代理：如果使用了代理工具，请确保已正确配置 git 全局代理，例如：")
            tlog.warning("      git config --global http.proxy http://127.0.0.1:您的代理端口")
            tlog.warning("   2. 切换 SSH 协议：如果您已配置 GitHub SSH Key，强烈建议在后台配置中将仓库 URL 更改为 SSH 格式：")
            tlog.warning("      git@github.com:您的用户名/您的仓库名.git")
            tlog.warning("      SSH 协议相比 HTTPS 更加稳定，能有效避开 SSL 握手错误！")

            return (
                f"{err_msg}\n\n"
                "💡 [自愈建议] 检测到本地网络在直连 github.com 时超时或 SSL 握手失败。\n"
                "1. 检查本地代理：如果使用了代理工具，请在终端尝试配置 Git 代理，例如：\n"
                "   git config --global http.proxy http://127.0.0.1:您的代理端口\n"
                "2. 切换 SSH 协议：如果您已配置 GitHub SSH Key，强烈建议将仓库 URL 更改为 SSH 格式：\n"
                "   git@github.com:您的用户名/您的仓库名.git\n"
                "   SSH 协议通常比 HTTPS 更加稳定，能有效避开 SSL 握手错误！"
            )
        return err_msg


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

            # ── 4. 清空工作区 (保留 .git 及对应一致资产) ────────
            self._clean_work_dir(work_dir, bundle_path)

            # ── 5. 拷贝构建产物 ──────────────────────────
            copied_count, skipped_count = self._copy_bundle(bundle_path, work_dir)

            # ── 6. 注入元文件 ────────────────────────────
            self._inject_meta_files(work_dir)

            # ── 7. Commit + Push ─────────────────────────
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
            # 配置用户身份
            self._configure_git_identity(work_dir)
            return True

        # 检查是否是 "branch not found" 错误
        stderr = result.stderr.lower()
        
        # 🛡️ 物理自愈：如果是仓库本身不存在（Repository not found），尝试利用 Token 一键自动建仓
        if "repository not found" in stderr or "fatal: repository" in stderr:
            if self._auto_create_github_repo():
                # 建仓成功后，分支显然不存在，返回 False 走 _init_orphan_branch 建立新分支
                return False

        if "not found" in stderr or "remote branch" in stderr or "does not exist" in stderr:
            return False

        # 其他错误直接抛出（过滤 args/stderr 中的敏感 Token）
        safe_args = [self._mask_url_credentials(arg) for arg in result.args]
        safe_stderr = self._mask_url_credentials(result.stderr)
        safe_stdout = self._mask_url_credentials(result.stdout)
        raise subprocess.CalledProcessError(
            result.returncode, safe_args,
            output=safe_stdout, stderr=safe_stderr
        )

    def _init_orphan_branch(self, work_dir: str):
        """创建孤儿分支：用于首次部署时目标分支尚不存在的场景"""
        tlog.info(f"📦 [GitHub Pages] 目标分支 '{self.branch}' 不存在，正在创建孤儿分支...")

        auth_url = self._get_authenticated_repo_url()
        env = os.environ.copy()
        proxy = self.get_proxy()
        if proxy:
            env["HTTP_PROXY"] = proxy
            env["HTTPS_PROXY"] = proxy
            env["http_proxy"] = proxy
            env["https_proxy"] = proxy
        try:
            # 先克隆仓库默认分支（仅获取 .git 元数据）
            subprocess.run(
                ["git", "clone", "--depth", "1", auth_url, work_dir],
                env=env, capture_output=True, text=True, timeout=120, check=True
            )
        except subprocess.CalledProcessError as e:
            # 过滤异常参数以防泄露 Token
            safe_args = [self._mask_url_credentials(arg) for arg in e.cmd]
            safe_stderr = self._mask_url_credentials(e.stderr) if e.stderr else None
            safe_stdout = self._mask_url_credentials(e.stdout) if e.stdout else None
            raise subprocess.CalledProcessError(
                e.returncode, safe_args,
                output=safe_stdout, stderr=safe_stderr
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

    def _clean_work_dir(self, work_dir: str, bundle_path: str = None):
        """清空工作区内容，保留 .git 目录及与 bundle_path 对应一致的文件"""
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
        """将构建产物从 bundle_path 差分复制到工作区。
        返回 (copied_count, skipped_count)。
        """
        copied_count = 0
        skipped_count = 0
        copied_files: list[str] = []
        # removed duplicate initialization
        tlog.info(f"🔍 [GitHub Pages] 正在从 {bundle_path} 拷贝文件至临时区 {work_dir}...")
        for root, dirs, files in os.walk(bundle_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'): continue
                # 🛡️ 静态纯净化防泄密：绝对禁止将原始未经编译的 Markdown 源稿文件拷贝到 gh-pages 发布分支中
                if file.endswith('.md') or file.endswith('.mdx') or file.endswith('.markdown') or file.endswith('.mdown'):
                    tlog.warning(f"🛡️ [安全拦截] 过滤丢弃源 Markdown 文件: {file}")
                    continue
                src = os.path.join(root, file)
                rel_path = os.path.relpath(src, bundle_path)
                dst = os.path.join(work_dir, rel_path)
                
                log_fn = tlog.info if self.verbose_copy else tlog.debug
                log_fn(f"📂 [拷贝中] {rel_path} -> {dst}")
                # Determine if copy needed
                need_copy = True
                if os.path.exists(dst):
                    if os.path.getsize(src) == os.path.getsize(dst):
                        # Files are identical in size; consider them unchanged and skip copying
                        need_copy = False
                if need_copy:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
                    copied_files.append(rel_path)
                    copied_count += 1
                else:
                    skipped_count += 1
        # 汇总实际复制的文件路径（相对路径）
        # 使用列表收集，在复制时已添加到 copied_files
        if copied_files:
            tlog.info("✅ 实际复制的文件:\n" + "\n".join(f" - {p}" for p in copied_files))
        else:
            tlog.info("✅ 实际复制的文件: 无（全部已同步）")
        tlog.info(f"✨ [GitHub Pages] 拷贝完成。共复制 {copied_count} 个文件，跳过 {skipped_count} 个已同步资产。")
        return copied_count, skipped_count

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

    def _run_git(self, work_dir: str, args: list, check: bool = True,
                 timeout: int = 30) -> subprocess.CompletedProcess:
        """执行 Git 命令的统一入口"""
        cmd = ["git", "-C", work_dir] + args
        env = os.environ.copy()
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

    def _auto_create_github_repo(self) -> bool:
        """
        🚀 [V100.0] 物理自愈：利用配置的 Token 自动在云端创建缺失的 GitHub 仓库。
        """
        token = self.token or os.environ.get("GITHUB_TOKEN", "")
        if not token or not self.repo_url:
            return False

        owner, repo = self._parse_owner_repo()
        if not owner or not repo:
            return False

        tlog.info(f"🧬 [GitHub Pages] 物理自愈：检测到仓库 '{owner}/{repo}' 不存在，正在尝试利用 Token 自动为您在 GitHub 创建仓库...")

        import urllib.request
        import json

        custom_proxy = self.get_proxy()
        if custom_proxy:
            proxy_support = urllib.request.ProxyHandler({'http': custom_proxy, 'https': custom_proxy})
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)

        # 1. 尝试直接在用户账号下建仓
        user_url = "https://api.github.com/user/repos"
        payload = {
            "name": repo,
            "private": False, # 🚀 [V105.0] 物理修正：对于 GitHub Pages 托管，建仓默认即为 Public 公开仓库
            "description": "Auto-created by Illacme Plenipes for GitHub Pages",
            "auto_init": False
        }
        
        req = urllib.request.Request(
            user_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
                "User-Agent": "Illacme-Plenipes-Sovereignty-Bot"
            },
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status in [201, 200]:
                    tlog.success(f"🟢 [GitHub Pages] 物理自愈：已成功在 GitHub 上一键创建公开仓库 '{owner}/{repo}'！")
                    return True
        except Exception as e:
            tlog.debug(f"ℹ️ [GitHub Pages] 个人账号建仓尝试未闭环: {e}，正在尝试向组织仓库建仓...")
            
            org_url = f"https://api.github.com/orgs/{owner}/repos"
            org_req = urllib.request.Request(
                org_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json",
                    "User-Agent": "Illacme-Plenipes-Sovereignty-Bot"
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(org_req, timeout=15) as org_response:
                    if org_response.status in [201, 200]:
                        tlog.success(f"🟢 [GitHub Pages] 物理自愈：已成功在组织 '{owner}' 下一键创建公开仓库 '{repo}'！")
                        return True
            except Exception as org_err:
                tlog.error(f"❌ [GitHub Pages] 云端一键自动建仓彻底失败: {org_err}")
                
        return False

    def _parse_owner_repo(self) -> tuple[str, str]:
        """解析 GitHub 仓库的 Owner 与 Name (支持完整的 HTTPS/SSH 链接、'owner/repo' 简写及 Token 自动解析)"""
        url = (self.repo_url or "").strip()
        if url.endswith(".git"):
            url = url[:-4]
            
        if "github.com/" in url:
            parts = url.split("github.com/")[1].split("/")
            if len(parts) >= 2:
                return parts[0], parts[1]
        elif "github.com:" in url:
            parts = url.split("github.com:")[1].split("/")
            if len(parts) >= 2:
                return parts[0], parts[1]
        elif "/" in url:
            parts = url.split("/")
            if len(parts) == 2 and parts[0] and parts[1]:
                return parts[0], parts[1]
        elif url and self.token:
            # 仅填了仓库名且有 Token，尝试自动通过 API 获取当前登录用户名
            try:
                import urllib.request
                import json
                req = urllib.request.Request("https://api.github.com/user", headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "Illacme-Plenipes-Sovereignty-Bot"
                })
                with urllib.request.urlopen(req, timeout=8) as resp:
                    if resp.status == 200:
                        user_login = json.loads(resp.read().decode("utf-8")).get("login", "")
                        if user_login:
                            return user_login, url
            except Exception:
                pass
        return "", ""

    def _auto_enable_github_pages(self) -> str:
        """
        🚀 [V105.0] 物理全自动化：自动调用 GitHub API 激活该仓库的 GitHub Pages 服务，
        并提取官方 html_url 站点分配地址。若仓库当前为 Private，自动全自动 PATCH 升级为 Public。
        """
        token = self.token or os.environ.get("GITHUB_TOKEN", "")
        owner, repo = self._parse_owner_repo()
        if not token or not owner or not repo:
            if owner and repo:
                tlog.info(f"💡 [GitHub Pages] 提示：当前未配置 Token（采用 SSH 免密通道推送成功）。若为首次部署，请确保前往 GitHub 仓库 (Settings -> Pages) 将 Build Source 分支指定为 '{self.branch}'。若已设置，请等待 1~3 分钟待 GitHub 云端完成构建部署。")
                return f"https://{owner}.github.io/{repo}/"
            return ""

        import urllib.request
        import json

        custom_proxy = self.get_proxy()
        if custom_proxy:
            proxy_support = urllib.request.ProxyHandler({'http': custom_proxy, 'https': custom_proxy})
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "Illacme-Plenipes-Sovereignty-Bot"
        }

        # 0. 检查仓库可见性，若为 Private 自动全自动修正为 Public (适配 GitHub Pages 免费部署规则)
        try:
            repo_info_url = f"https://api.github.com/repos/{owner}/{repo}"
            req_info = urllib.request.Request(repo_info_url, headers=headers, method="GET")
            with urllib.request.urlopen(req_info, timeout=10) as r_info:
                if r_info.status == 200:
                    info_data = json.loads(r_info.read().decode("utf-8"))
                    if info_data.get("private") is True:
                        tlog.info(f"⚡ [GitHub Pages] 物理自愈：检测到仓库 '{owner}/{repo}' 为私有仓库，正在自动调整为 Public 以满足免费 Pages 部署规则...")
                        patch_req = urllib.request.Request(repo_info_url, data=json.dumps({"private": False}).encode("utf-8"), headers=headers, method="PATCH")
                        urllib.request.urlopen(patch_req, timeout=10)
                        tlog.success(f"🟢 [GitHub Pages] 物理自愈：成功将仓库 '{owner}/{repo}' 升级为 Public (公开)！")
        except Exception as e_patch:
            tlog.debug(f"ℹ️ [GitHub Pages] 物理检测仓库可见性退避: {e_patch}")

        pages_url = f"https://api.github.com/repos/{owner}/{repo}/pages"
        payload = {
            "source": {
                "branch": self.branch,
                "path": "/"
            }
        }

        # 1. 尝试 GET 查询当前云端 Pages 配置状态
        try:
            req = urllib.request.Request(pages_url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    curr_branch = data.get("source", {}).get("branch")
                    html_url = data.get("html_url") or f"https://{owner}.github.io/{repo}/"
                    
                    # 若已绑定正确的 target 分支，直接返还
                    if curr_branch == self.branch:
                        tlog.info(f"🌐 [GitHub Pages] 云端 Pages 已激活，构建分支已对准 '{self.branch}': {html_url}")
                        return html_url
                    
                    # 分支不匹配，通过 PUT 强制修正分支绑定为 self.branch
                    tlog.info(f"⚡ [GitHub Pages] 云端 Pages 分支为 '{curr_branch}'，正在通过 API 自动调整为 '{self.branch}'...")
                    put_req = urllib.request.Request(pages_url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
                    with urllib.request.urlopen(put_req, timeout=10) as put_resp:
                        if put_resp.status in (200, 204):
                            tlog.success(f"🟢 [GitHub Pages] 物理自愈：成功将 Pages 构建分支绑定升级为 '{self.branch}'！")
                            return html_url
        except Exception:
            pass

        # 2. 若未激活 Pages，尝试 POST 调用 API 一键全自动激活并绑定 self.branch
        tlog.info(f"⚡ [GitHub Pages] 云端物理自愈：正在调用 API 自动激活 '{owner}/{repo}' 的 GitHub Pages 服务 (分支: {self.branch})...")
        try:
            req = urllib.request.Request(pages_url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status in (201, 202, 200):
                    data = json.loads(resp.read().decode("utf-8"))
                    html_url = data.get("html_url") or f"https://{owner}.github.io/{repo}/"
                    tlog.success(f"🟢 [GitHub Pages] 一键全自动激活并成功绑定 '{self.branch}' 分支！分配域名: {html_url}")
                    return html_url
        except Exception as e:
            tlog.warning(f"ℹ️ [GitHub Pages] 尝试自动激活 Pages API 反馈: {e}")

        # Fallback 默认预测 GitHub Pages 官方 URL 规范
        return f"https://{owner}.github.io/{repo}/"
