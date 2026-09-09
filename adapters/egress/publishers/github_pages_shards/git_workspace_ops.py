# -*- coding: utf-8 -*-
"""
📦 GitHub Pages Publisher Shard - Git Workspace Ops
职责：承载 Git 分支克隆、孤儿分支初始化、工作区智感清理、Markdown 源稿防泄密拦截拷贝及 Commit/Push 执行。
"""

import os
import shutil
import subprocess
from typing import Tuple
from core.utils.tracing import tlog
from .security_ops import get_authenticated_repo_url_impl, mask_url_credentials_impl
from .cloud_api_ops import auto_create_github_repo_impl


def run_git_impl(publisher_inst, work_dir: str, args: list, check: bool = True, timeout: int = 60) -> subprocess.CompletedProcess:
    """执行 Git 命令的统一入口，强力覆盖宿主机残留的失效代理配置"""
    proxy = publisher_inst.get_proxy()
    cmd = ["git", "-C", work_dir]
    if proxy:
        cmd.extend(["-c", f"http.proxy={proxy}", "-c", f"https.proxy={proxy}"])
    else:
        cmd.extend(["-c", "http.proxy=", "-c", "https.proxy="])
    cmd.extend(args)

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = "echo"
    if proxy:
        env["HTTP_PROXY"] = proxy
        env["HTTPS_PROXY"] = proxy
        env["http_proxy"] = proxy
        env["https_proxy"] = proxy
    else:
        env.pop("HTTP_PROXY", None)
        env.pop("HTTPS_PROXY", None)
        env.pop("http_proxy", None)
        env.pop("https_proxy", None)

    return subprocess.run(
        cmd, env=env, capture_output=True, text=True,
        timeout=timeout, check=check
    )


def configure_git_identity_impl(publisher_inst, work_dir: str):
    """配置 Git 用户身份（临时工作区级别）"""
    run_git_impl(publisher_inst, work_dir, ["config", "user.name", publisher_inst.git_user_name])
    run_git_impl(publisher_inst, work_dir, ["config", "user.email", publisher_inst.git_user_email])


def clone_target_branch_impl(publisher_inst, work_dir: str) -> bool:
    """
    尝试浅克隆目标分支到工作区。
    :return: True 表示克隆成功，False 表示分支不存在。
    """
    auth_url = get_authenticated_repo_url_impl(publisher_inst.repo_url, publisher_inst.token)
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = "echo"
    proxy = publisher_inst.get_proxy()
    clone_cmd = ["git"]
    if proxy:
        clone_cmd.extend(["-c", f"http.proxy={proxy}", "-c", f"https.proxy={proxy}"])
        env["HTTP_PROXY"] = proxy
        env["HTTPS_PROXY"] = proxy
        env["http_proxy"] = proxy
        env["https_proxy"] = proxy
    else:
        clone_cmd.extend(["-c", "http.proxy=", "-c", "https.proxy="])
        env.pop("HTTP_PROXY", None)
        env.pop("HTTPS_PROXY", None)
        env.pop("http_proxy", None)
        env.pop("https_proxy", None)

    clone_cmd.extend([
        "clone", "--depth", "1", "--single-branch",
        "--branch", publisher_inst.branch, auth_url, work_dir
    ])
    result = subprocess.run(
        clone_cmd,
        env=env, capture_output=True, text=True, timeout=120
    )
    if result.returncode == 0:
        # 配置用户身份
        configure_git_identity_impl(publisher_inst, work_dir)
        return True

    # 检查是否是 "branch not found" 错误
    stderr = result.stderr.lower()
    
    # 🛡️ 物理自愈：如果是仓库本身不存在（Repository not found），尝试利用 Token 一键自动建仓
    if "repository not found" in stderr or "fatal: repository" in stderr:
        if auto_create_github_repo_impl(publisher_inst):
            # 建仓成功后，分支显然不存在，返回 False 走 _init_orphan_branch 建立新分支
            return False

    if "not found" in stderr or "remote branch" in stderr or "does not exist" in stderr:
        return False

    # 其他错误直接抛出（过滤 args/stderr 中的敏感 Token）
    safe_args = [mask_url_credentials_impl(arg) for arg in result.args]
    safe_stderr = mask_url_credentials_impl(result.stderr)
    safe_stdout = mask_url_credentials_impl(result.stdout)
    raise subprocess.CalledProcessError(
        result.returncode, safe_args,
        output=safe_stdout, stderr=safe_stderr
    )


def init_orphan_branch_impl(publisher_inst, work_dir: str):
    """创建孤儿分支：用于首次部署时目标分支尚不存在的场景"""
    tlog.info(f"📦 [GitHub Pages] 目标分支 '{publisher_inst.branch}' 不存在，正在初始化本地独立发布工作区...")

    auth_url = get_authenticated_repo_url_impl(publisher_inst.repo_url, publisher_inst.token)
    run_git_impl(publisher_inst, work_dir, ["init"])
    run_git_impl(publisher_inst, work_dir, ["remote", "add", "origin", auth_url])
    run_git_impl(publisher_inst, work_dir, ["checkout", "-b", publisher_inst.branch])
    configure_git_identity_impl(publisher_inst, work_dir)


def clean_work_dir_impl(publisher_inst, work_dir: str, bundle_path: str = None):
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


def copy_bundle_impl(publisher_inst, bundle_path: str, work_dir: str) -> Tuple[int, int]:
    """将构建产物从 bundle_path 差分复制到工作区。
    返回 (copied_count, skipped_count)。
    """
    copied_count = 0
    skipped_count = 0
    copied_files: list[str] = []
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
            
            log_fn = tlog.info if publisher_inst.verbose_copy else tlog.debug
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

    if copied_files:
        tlog.info("✅ 实际复制的文件:\n" + "\n".join(f" - {p}" for p in copied_files))
    else:
        tlog.info("✅ 实际复制的文件: 无（全部已同步）")
    tlog.info(f"✨ [GitHub Pages] 拷贝完成。共复制 {copied_count} 个文件，跳过 {skipped_count} 个已同步资产。")
    return copied_count, skipped_count


def inject_meta_files_impl(publisher_inst, work_dir: str):
    """注入 GitHub Pages 元文件"""
    # .nojekyll — 禁止 Jekyll 处理（支持下划线开头的路径）
    if publisher_inst.nojekyll:
        nojekyll_path = os.path.join(work_dir, ".nojekyll")
        with open(nojekyll_path, 'w') as f:
            f.write("")

    # CNAME — 自定义域名绑定
    if publisher_inst.cname:
        cname_path = os.path.join(work_dir, "CNAME")
        with open(cname_path, 'w') as f:
            f.write(publisher_inst.cname.strip())


def commit_and_push_impl(publisher_inst, work_dir: str, commit_msg: str) -> bool:
    """
    暂存全部变更、提交并推送。
    :return: True 表示有变更被推送，False 表示无变更。
    """
    # 暂存全部文件
    run_git_impl(publisher_inst, work_dir, ["add", "-A"])

    # 检查是否有变更
    status_result = run_git_impl(publisher_inst, work_dir, ["status", "--porcelain"])
    if not status_result.stdout.strip():
        return False  # 无变更

    # 提交
    run_git_impl(publisher_inst, work_dir, ["commit", "-m", commit_msg])

    # 推送
    push_cmd = ["push", "origin", publisher_inst.branch]
    if publisher_inst.force_push:
        push_cmd.insert(1, "--force")
        tlog.warning("⚠️ [GitHub Pages] 正在执行强制推送 (force_push=true)！")

    run_git_impl(publisher_inst, work_dir, push_cmd, timeout=120)
    return True
