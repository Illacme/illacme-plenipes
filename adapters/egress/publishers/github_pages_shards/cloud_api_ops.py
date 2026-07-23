# -*- coding: utf-8 -*-
"""
☁️ GitHub Pages Publisher Shard - Cloud API Ops
职责：承载利用 GitHub REST API 物理自愈建仓、解析 Owner/Repo 以及一键激活 Pages 服务与权限 PATCH 修正。
"""

import os
import json
import urllib.request
from core.utils.tracing import tlog


def parse_owner_repo_impl(repo_url: str, token: str = "") -> tuple[str, str]:
    """解析 GitHub 仓库的 Owner 与 Name (支持完整的 HTTPS/SSH 链接、'owner/repo' 简写及 Token 自动解析)"""
    url = (repo_url or "").strip()
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
    elif url and token:
        # 仅填了仓库名且有 Token，尝试自动通过 API 获取当前登录用户名
        try:
            req = urllib.request.Request("https://api.github.com/user", headers={
                "Authorization": f"token {token}",
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


def auto_create_github_repo_impl(publisher_inst) -> bool:
    """
    🚀 [V100.0] 物理自愈：利用配置的 Token 自动在云端创建缺失的 GitHub 仓库。
    """
    token = publisher_inst.token or os.environ.get("GITHUB_TOKEN", "")
    if not token or not publisher_inst.repo_url:
        return False

    owner, repo = parse_owner_repo_impl(publisher_inst.repo_url, token)
    if not owner or not repo:
        return False

    tlog.info(f"🧬 [GitHub Pages] 物理自愈：检测到仓库 '{owner}/{repo}' 不存在，正在尝试利用 Token 自动为您在 GitHub 创建仓库...")

    custom_proxy = publisher_inst.get_proxy()
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


def auto_enable_github_pages_impl(publisher_inst) -> str:
    """
    🚀 [V105.0] 物理全自动化：自动调用 GitHub API 激活该仓库的 GitHub Pages 服务，
    并提取官方 html_url 站点分配地址。若仓库当前为 Private，自动全自动 PATCH 升级为 Public。
    """
    token = publisher_inst.token or os.environ.get("GITHUB_TOKEN", "")
    owner, repo = parse_owner_repo_impl(publisher_inst.repo_url, token)
    if not token or not owner or not repo:
        if owner and repo:
            tlog.info(f"💡 [GitHub Pages] 提示：当前未配置 Token（采用 SSH 免密通道推送成功）。若为首次部署，请确保前往 GitHub 仓库 (Settings -> Pages) 将 Build Source 分支指定为 '{publisher_inst.branch}'。若已设置，请等待 1~3 分钟待 GitHub 云端完成构建部署。")
            return f"https://{owner}.github.io/{repo}/"
        return ""

    custom_proxy = publisher_inst.get_proxy()
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
            "branch": publisher_inst.branch,
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
                if curr_branch == publisher_inst.branch:
                    tlog.info(f"🌐 [GitHub Pages] 云端 Pages 已激活，构建分支已对准 '{publisher_inst.branch}': {html_url}")
                    return html_url
                
                # 分支不匹配，通过 PUT 强制修正分支绑定为 publisher_inst.branch
                tlog.info(f"⚡ [GitHub Pages] 云端 Pages 分支为 '{curr_branch}'，正在通过 API 自动调整为 '{publisher_inst.branch}'...")
                put_req = urllib.request.Request(pages_url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
                with urllib.request.urlopen(put_req, timeout=10) as put_resp:
                    if put_resp.status in (200, 204):
                        tlog.success(f"🟢 [GitHub Pages] 物理自愈：成功将 Pages 构建分支绑定升级为 '{publisher_inst.branch}'！")
                        return html_url
    except Exception:
        pass

    # 2. 若未激活 Pages，尝试 POST 调用 API 一键全自动激活并绑定 publisher_inst.branch
    tlog.info(f"⚡ [GitHub Pages] 云端物理自愈：正在调用 API 自动激活 '{owner}/{repo}' 的 GitHub Pages 服务 (分支: {publisher_inst.branch})...")
    try:
        req = urllib.request.Request(pages_url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status in (201, 202, 200):
                data = json.loads(resp.read().decode("utf-8"))
                html_url = data.get("html_url") or f"https://{owner}.github.io/{repo}/"
                tlog.success(f"🟢 [GitHub Pages] 一键全自动激活并成功绑定 '{publisher_inst.branch}' 分支！分配域名: {html_url}")
                return html_url
    except Exception as e:
        tlog.warning(f"ℹ️ [GitHub Pages] 尝试自动激活 Pages API 反馈: {e}")

    # Fallback 默认预测 GitHub Pages 官方 URL 规范
    return f"https://{owner}.github.io/{repo}/"
