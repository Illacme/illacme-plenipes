# -*- coding: utf-8 -*-
"""
🌐 [V74.96] Git-based Hosting Dry Run Shard
职责：GitHub Pages, Gitee Pages, GitLab Pages 的 REST API 校验、私有/公开仓库识别、SSH 免密探针与网络重试。
架构：由 plugin_dry_run_hosting.py 拆分而来 (SOP-02 模块拆分标准)。
"""

import os
import subprocess
import requests
from typing import Dict, Any, List


def probe_git_hosting(
    plugin_id: str,
    settings: Dict[str, Any],
    logs: List[Dict[str, str]],
    log_func: Any,
    proxies: Dict[str, str],
    net_timeout: int
) -> bool:
    """执行 Git 类全站托管平台的网络连通性与鉴权探测。"""
    success = True

    if plugin_id == "github_pages":
        raw_repo = (settings.get("repo", "") or settings.get("repo_url", "") or settings.get("repository", "") or "").strip()
        repo = raw_repo
        
        # 兼容规范化提取 owner/repo
        if "github.com/" in raw_repo:
            repo = raw_repo.split("github.com/")[1]
        elif "github.com:" in raw_repo:
            repo = raw_repo.split("github.com:")[1]
        repo = repo.replace(".git", "").strip().strip("/")

        token = settings.get("token", "")

        if not repo:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 GitHub 仓库 (格式应为 'owner/repo' 或 'git@github.com:owner/repo.git')。"))
            return False

        if token:
            logs.append(log_func("INFO", f"📡 [探测] 正在校验 GitHub Repository '{repo}' API 连通性..."))
            url = f"https://api.github.com/repos/{repo}"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            try:
                resp = requests.get(url, headers=headers, proxies=proxies, timeout=net_timeout)
                if resp.status_code == 200:
                    data = resp.json() if hasattr(resp, "json") else {}
                    is_private = data.get("private", False)
                    if is_private:
                        logs.append(log_func("SUCCESS", f"🟢 [成功] API 鉴权通过！成功探测到私有仓库 '{repo}' (🔒 私有仓库在主页公开列表中隐私隐藏)。"))
                        logs.append(log_func("INFO", "💡 [提示] GitHub 免费版的私有仓库默认无法挂载 Pages。若访问网页报 404，请前往 GitHub 仓库 (Settings -> Change visibility) 设为 Public (公开仓库)。"))
                    else:
                        logs.append(log_func("SUCCESS", f"🟢 [成功] GitHub API 鉴权校验通过，成功探测到公开仓库 '{repo}'。"))
                elif resp.status_code in [401, 403]:
                    logs.append(log_func("ERROR", "❌ [错误] GitHub Token 校验失败：访问令牌无效或已过期，请核对权限。"))
                    success = False
                elif resp.status_code == 404:
                    logs.append(log_func("ERROR", f"❌ [错误] 未在 GitHub 上发现仓库 '{repo}'，请确认仓库是否正确创建，或 Token 具备 Repo 访问权限。"))
                    success = False
                else:
                    logs.append(log_func("ERROR", f"❌ [错误] GitHub API 返回异常状态码 {resp.status_code}: {resp.text[:100]}"))
                    success = False
            except Exception:
                # 🛡️ 物理自动重试 1 次（防止瞬时网络波动）
                try:
                    logs.append(log_func("INFO", "📡 [重试] 正在通过本地代理尝试第 2 次连接 GitHub API..."))
                    resp = requests.get(url, headers=headers, proxies=proxies, timeout=net_timeout)
                    if resp.status_code == 200:
                        data = resp.json() if hasattr(resp, "json") else {}
                        is_private = data.get("private", False)
                        if is_private:
                            logs.append(log_func("SUCCESS", f"🟢 [成功] 重试成功！API 鉴权通过，探测到私有仓库 '{repo}' (🔒 主页公开列表隐身)。"))
                        else:
                            logs.append(log_func("SUCCESS", f"🟢 [成功] 重试成功！GitHub API 鉴权校验通过，探测到仓库 '{repo}'。"))
                        success = True
                    else:
                        logs.append(log_func("ERROR", f"❌ [错误] GitHub API 重试返回异常状态码 {resp.status_code}"))
                        success = False
                except Exception as retry_err:
                    logs.append(log_func("WARN", f"⚠️ [网络] 连接 GitHub API 超时或出错: {retry_err}。"))
                    logs.append(log_func("INFO", "💡 [自愈建议] 1. 请核对本地代理节点连接性；2. 若仅部署网页，亦可使用 SSH 格式 (git@github.com:owner/repo.git) 避开 API 限频。"))
                    success = False
        else:
            # 🚀 [多因子免密探测] 优先使用本地 Git / SSH 探针直接握手远程仓库
            full_repo_url = raw_repo if ("github.com" in raw_repo or raw_repo.startswith("git@")) else f"git@github.com:{repo}.git"
            logs.append(log_func("INFO", f"🔑 [免密探测] 当前未配置 Token，正在通过本地 Git / SSH 协议握手 '{full_repo_url}'..."))
            
            ssh_probe_passed = False
            try:
                probe_env = dict(os.environ)
                probe_env["GIT_TERMINAL_PROMPT"] = "0"
                probe_env["GIT_SSH_COMMAND"] = "ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no"
                probe_proc = subprocess.run(
                    ["git", "ls-remote", "--heads", full_repo_url],
                    capture_output=True,
                    text=True,
                    timeout=8,
                    env=probe_env
                )
                if probe_proc.returncode == 0:
                    ssh_probe_passed = True
                    logs.append(log_func("SUCCESS", f"🟢 [成功] 本地 SSH 密钥连通极佳！已成功免密握手远程仓库 '{repo}'，无需填写 Token 即可直接实现全自动打包发布！"))
                    success = True
            except Exception:
                pass

            if not ssh_probe_passed:
                # 降级尝试公开仓库 API 探针
                logs.append(log_func("INFO", f"📡 [公开探测] 正在测试公开仓库 '{repo}' 的可达性..."))
                url = f"https://api.github.com/repos/{repo}"
                try:
                    resp = requests.get(url, proxies=proxies, timeout=10)
                    if resp.status_code == 200:
                        logs.append(log_func("SUCCESS", f"🟢 [成功] 成功检测到公开仓库 '{repo}'。若本地已配置 SSH Key 即可直接免密推送。"))
                        success = True
                    elif resp.status_code == 404:
                        logs.append(log_func("WARN", f"⚠️ [提示] 未能在公开列表找到仓库 '{repo}' (若为私有仓库，请确保本地 SSH Key 具备访问权限或填入 Personal Access Token)。"))
                        success = False
                    else:
                        logs.append(log_func("ERROR", f"❌ [错误] 无法获取仓库 '{repo}' 的状态 (HTTP {resp.status_code})。"))
                        success = False
                except Exception as e:
                    logs.append(log_func("WARN", f"⚠️ [网络] 无法连接到 GitHub: {e}。建议检查网络或配置代理。"))
                    success = False

    elif plugin_id == "gitee_pages":
        raw_repo = (settings.get("repo", "") or settings.get("repo_url", "") or settings.get("repository", "") or "").strip()
        repo = raw_repo
        if "gitee.com/" in raw_repo:
            repo = raw_repo.split("gitee.com/")[1]
        elif "gitee.com:" in raw_repo:
            repo = raw_repo.split("gitee.com:")[1]
        repo = repo.replace(".git", "").strip().strip("/")

        token = settings.get("token", "") or settings.get("access_token", "")

        if not repo:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 Gitee 仓库 (格式应为 'owner/repo' 或 'git@gitee.com:owner/repo.git')。"))
            return False

        if token:
            logs.append(log_func("INFO", f"📡 [探测] 正在校验 Gitee 仓库 '{repo}' API 连通性..."))
            url = f"https://gitee.com/api/v5/repos/{repo}"
            params = {"access_token": token}
            try:
                resp = requests.get(url, params=params, proxies=proxies, timeout=net_timeout)
                if resp.status_code == 200:
                    logs.append(log_func("SUCCESS", f"🟢 [成功] Gitee API 鉴权校验通过，成功探测到仓库 '{repo}'。"))
                elif resp.status_code in [401, 403]:
                    logs.append(log_func("ERROR", "❌ [错误] Gitee Token 校验失败：访问令牌无效或已过期。"))
                    success = False
                elif resp.status_code == 404:
                    logs.append(log_func("ERROR", f"❌ [错误] 未在 Gitee 上发现仓库 '{repo}'，请确认仓库路径。"))
                    success = False
                else:
                    logs.append(log_func("ERROR", f"❌ [错误] Gitee API 返回异常状态码 {resp.status_code}"))
                    success = False
            except Exception as e:
                logs.append(log_func("WARN", f"⚠️ [网络] 无法连接到 Gitee API: {e}。"))
                success = False
        else:
            full_repo_url = raw_repo if ("gitee.com" in raw_repo or raw_repo.startswith("git@")) else f"git@gitee.com:{repo}.git"
            logs.append(log_func("INFO", f"🔑 [免密探测] 当前未配置 Token，正在通过本地 Git / SSH 协议握手 '{full_repo_url}'..."))
            try:
                probe_env = dict(os.environ)
                probe_env["GIT_TERMINAL_PROMPT"] = "0"
                probe_env["GIT_SSH_COMMAND"] = "ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no"
                probe_proc = subprocess.run(
                    ["git", "ls-remote", "--heads", full_repo_url],
                    capture_output=True, text=True, timeout=8, env=probe_env
                )
                if probe_proc.returncode == 0:
                    logs.append(log_func("SUCCESS", f"🟢 [成功] 本地 SSH 密钥连通极佳！已成功免密握手远程仓库 '{repo}'。"))
                    success = True
                else:
                    logs.append(log_func("WARN", "⚠️ [提示] SSH 免密探测未通过，请配置 Access Token 或检查 SSH Key 授权。"))
                    success = False
            except Exception as e:
                logs.append(log_func("WARN", f"⚠️ [探测异常] SSH 握手失败: {e}"))
                success = False

    elif plugin_id == "gitlab_pages":
        raw_repo = (settings.get("repo", "") or settings.get("repo_url", "") or settings.get("repository", "") or "").strip()
        repo = raw_repo
        if "gitlab.com/" in raw_repo:
            repo = raw_repo.split("gitlab.com/")[1]
        elif "gitlab.com:" in raw_repo:
            repo = raw_repo.split("gitlab.com:")[1]
        repo = repo.replace(".git", "").strip().strip("/")

        token = settings.get("token", "") or settings.get("access_token", "")

        if not repo:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 GitLab 仓库 (格式应为 'owner/repo' 或 'git@gitlab.com:owner/repo.git')。"))
            return False

        if token:
            logs.append(log_func("INFO", f"📡 [探测] 正在校验 GitLab 仓库 '{repo}' API 连通性..."))
            import urllib.parse
            encoded_project = urllib.parse.quote(repo, safe="")
            url = f"https://gitlab.com/api/v4/projects/{encoded_project}"
            headers = {"PRIVATE-TOKEN": token}
            try:
                resp = requests.get(url, headers=headers, proxies=proxies, timeout=net_timeout)
                if resp.status_code == 200:
                    logs.append(log_func("SUCCESS", f"🟢 [成功] GitLab API 鉴权校验通过，成功探测到仓库 '{repo}'。"))
                elif resp.status_code in [401, 403]:
                    logs.append(log_func("ERROR", "❌ [错误] GitLab Token 校验失败：访问令牌无效或缺少 api/read_repository 权限。"))
                    success = False
                elif resp.status_code == 404:
                    logs.append(log_func("ERROR", f"❌ [错误] 未在 GitLab 上发现项目 '{repo}'，请核对路径。"))
                    success = False
                else:
                    logs.append(log_func("ERROR", f"❌ [错误] GitLab API 返回异常状态码 {resp.status_code}"))
                    success = False
            except Exception as e:
                logs.append(log_func("WARN", f"⚠️ [网络] 无法连接到 GitLab API: {e}。建议配置代理。"))
                success = False
        else:
            full_repo_url = raw_repo if ("gitlab.com" in raw_repo or raw_repo.startswith("git@")) else f"git@gitlab.com:{repo}.git"
            logs.append(log_func("INFO", f"🔑 [免密探测] 当前未配置 Token，正在通过本地 Git / SSH 协议握手 '{full_repo_url}'..."))
            try:
                probe_env = dict(os.environ)
                probe_env["GIT_TERMINAL_PROMPT"] = "0"
                probe_env["GIT_SSH_COMMAND"] = "ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no"
                probe_proc = subprocess.run(
                    ["git", "ls-remote", "--heads", full_repo_url],
                    capture_output=True, text=True, timeout=8, env=probe_env
                )
                if probe_proc.returncode == 0:
                    logs.append(log_func("SUCCESS", f"🟢 [成功] 本地 SSH 密钥连通极佳！已成功免密握手远程仓库 '{repo}'。"))
                    success = True
                else:
                    logs.append(log_func("WARN", "⚠️ [提示] SSH 免密探测未通过，请配置 Personal Access Token 或检查 SSH Key 授权。"))
                    success = False
            except Exception as e:
                logs.append(log_func("WARN", f"⚠️ [探测异常] SSH 握手失败: {e}"))
                success = False

    return success
