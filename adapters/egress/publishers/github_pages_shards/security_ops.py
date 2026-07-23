# -*- coding: utf-8 -*-
"""
🔒 GitHub Pages Publisher Shard - Security & Autotherapy Ops
职责：承载 OAuth Token 明文脱敏、带鉴权克隆 URL 组装以及网络握手报错高情商自愈建议。
"""

import os
import re
from core.utils.tracing import tlog


def get_authenticated_repo_url_impl(repo_url: str, token: str) -> str:
    """
    🚀 动态组装带有 OAuth Token 的 HTTPS 克隆/推送 URL。
    若无 Token，或 URL 格式不符合要求，则原样返回 repo_url。
    """
    url = repo_url or ""
    auth_token = token or os.environ.get("GITHUB_TOKEN", "")
    if not auth_token or not url:
        return url

    # 针对 GitHub HTTPS/HTTP 地址进行 Token 注入
    if url.startswith("https://") and "github.com/" in url:
        clean_url = url.replace("https://", "")
        if "@" in clean_url:
            clean_url = clean_url.split("@", 1)[1]
        return f"https://x-access-token:{auth_token}@{clean_url}"
    elif url.startswith("http://") and "github.com/" in url:
        clean_url = url.replace("http://", "")
        if "@" in clean_url:
            clean_url = clean_url.split("@", 1)[1]
        return f"http://x-access-token:{auth_token}@{clean_url}"

    return url


def mask_url_credentials_impl(text: str) -> str:
    """
    🔒 抹除文本中可能夹带的明文 Token 凭证（用 *** 代替）。
    """
    if not text:
        return text
    return re.sub(r'(https?://x-access-token:)([^@\s]+)(@)', r'\1***\3', text)


def add_autotherapy_suggestion_impl(err_msg: str) -> str:
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
