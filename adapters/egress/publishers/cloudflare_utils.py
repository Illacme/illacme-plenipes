#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Cloudflare Pages Publisher Utils
🚀 [V48.3]：Cloudflare Pages 插件工具分片，提供命令构建、代理对齐、Token脱敏及 API 自愈中枢。
"""

import os
import re
import shutil
import urllib.request
import json
import ssl
from typing import Optional, List
from core.utils.tracing import tlog


def mask_token(text: str, token: str = "") -> str:
    """
    🔒 抹除文本中可能夹带的明文 Cloudflare Token。
    """
    if not text:
        return text
    active_token = token or os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if active_token and len(active_token) > 4:
        return text.replace(active_token, "***")
    return text


def align_proxy(proxy_str: str, for_python: bool = False) -> Optional[str]:
    """
    🔌 [代理协议自愈中枢]：针对 v2rayn 常见的 Socks5(10808) 与 HTTP(10809) 端口进行物理自动对齐，
    将不被 Node/Python 原生 HTTP 代理模块支持的 socks 端口自动路由至标准的 10809 HTTP 代理通道。
    """
    if not proxy_str:
        return proxy_str

    p_str = proxy_str.strip()

    # 如果端口配置为 10808（V2RayN 的 Socks 端口）
    if "10808" in p_str:
        p_aligned = (
            p_str.replace("10808", "10809")
            .replace("socks5://", "http://")
            .replace("socks4://", "http://")
            .replace("socks://", "http://")
            .replace("https://", "http://")
        )
        tlog.info(f"🔌 [代理中枢自愈] 自动将 10808 (Socks) 物理重定向对齐至标准的 10809 HTTP 代理通道: {p_aligned}")
        return p_aligned

    return p_str


def extract_deploy_url(stdout: str) -> Optional[str]:
    """
    从 Wrangler stdout 中解析部署 URL。
    Wrangler 输出通常包含形如 "https://xxx.pages.dev" 的 URL。
    """
    if not stdout:
        return None

    # 匹配 Wrangler 输出中的 pages.dev URL
    url_pattern = re.compile(r'(https://[\w\-]+\.pages\.dev\S*)', re.IGNORECASE)
    match = url_pattern.search(stdout)
    if match:
        return match.group(1)

    # 兜底：匹配 any https URL
    fallback_pattern = re.compile(r'(https://\S+)')
    match = fallback_pattern.search(stdout)
    return match.group(1) if match else None


def build_wrangler_command(
    bundle_path: str,
    project_name: str,
    branch: str = "production",
    account_id: str = "",
    wrangler_path: str = "wrangler"
) -> List[str]:
    """组装 wrangler pages deploy 命令参数（含智能路径自愈与 npx 降级）"""
    actual_path = wrangler_path

    # 如果是默认 of "wrangler" 命令，且系统 PATH 中找不到它
    if actual_path == "wrangler" and not shutil.which("wrangler"):
        # 1. 尝试探测本地 node_modules
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        local_wrangler = os.path.join(project_root, "node_modules", ".bin", "wrangler")
        if os.path.exists(local_wrangler):
            actual_path = local_wrangler
            tlog.info(f"🟢 [Cloudflare Pages] 检测到本地项目 node_modules 里的 wrangler，已自动切换为: {actual_path}")
        else:
            # 2. 尝试探测 npx 可用性，若可用则降级为以 npx wrangler 执行
            if shutil.which("npx"):
                tlog.info("🟢 [Cloudflare Pages] 系统未检测到全局 wrangler，但发现 npx，已自动降级为以 npx wrangler 运行。")
                cmd = [
                    "npx", "-y", "wrangler",
                    "pages", "deploy",
                    bundle_path,
                    "--project-name", project_name,
                    "--branch", branch
                ]
                if account_id:
                    cmd.extend(["--account-id", account_id])
                return cmd

    cmd = [
        actual_path,
        "pages", "deploy",
        bundle_path,
        "--project-name", project_name,
        "--branch", branch
    ]

    if account_id:
        cmd.extend(["--account-id", account_id])

    return cmd


def auto_fetch_account_id(token: str, custom_proxy: Optional[str] = None, timeout: int = 8) -> Optional[str]:
    """
    🚀 [V100.0] 物理自愈：利用 Cloudflare Token 自动获取当前用户账号 ID。
    """
    # 🔌 [V89.9] 智能配置 Python 网络代理并利用自愈对齐中枢消除 10808 端口混淆
    aligned_proxy = align_proxy(custom_proxy or "", for_python=True)
    if aligned_proxy:
        proxy_support = urllib.request.ProxyHandler({'http': aligned_proxy, 'https': aligned_proxy})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)

    url = "https://api.cloudflare.com/client/v4/accounts"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Illacme-Plenipes-Sovereignty-Bot"
        },
        method="GET"
    )

    try:
        # 🔌 [TLS自愈] 忽略 TLS 证书验证以适配特定的局域网代理
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                result = data.get("result", [])
                if result:
                    return result[0].get("id")
    except Exception as e:
        tlog.warning(f"⚠️ [Cloudflare Pages] 自动拉取账户 ID 因网络受限未闭环 (已自动降级为使用 Wrangler 本地内置会话探测): {e}")
    return None


def emit_cloudflare_error_diagnostics(error_msg: str) -> None:
    """针对特定的代理混淆和网络连接错误输出诊断建议"""
    err_low = error_msg.lower()
    if "invalid url" in err_low or "bad request" in err_low or "malformed response" in err_low:
        tlog.warning("💡 [代理自愈建议] 检测到 API 接口返回 400 Bad Request/Invalid URL。")
        tlog.warning("   这通常是由于在全局配置中误将 Socks 代理端口（如 10808）的前缀指定为 http://，")
        tlog.warning("   或者将 HTTP 代理端口（如 10809）指定为了 socks:// 协议所致。")
        tlog.warning("   虽然本次系统已自动为您尝试进行协议对齐，但建议您在发布卡片配置中，")
        tlog.warning("   将代理地址规范修改为 http://127.0.0.1:10809（HTTP）或 socks5://127.0.0.1:10808（Socks5）！")
    elif any(kw in err_low for kw in ["fetch failed", "timeout", "connectivity", "connection refused"]):
        tlog.warning("💡 [自愈建议] 检测到本地网络在直连 Cloudflare API 时超时。")
        tlog.warning("   由于刚才系统已经成功把网站推送至 GitHub Pages，")
        tlog.warning("   强烈建议您登录 Cloudflare 控制台，直接将项目绑定 to GitHub 仓库。")
        tlog.warning("   此后只要本地成功推送到 GitHub，Cloudflare 将在云端完成自动部署，100% 避开本地网络物理拦截！")


def emit_cloudflare_timeout_diagnostics(custom_proxy: Optional[str] = None) -> None:
    """针对部署超时给出代理及 API 状态排查提示"""
    tlog.warning("💡 [超时排查建议] 检测到部署发生超时。推荐进行以下自检：")
    tlog.warning(f"   1. 检查当前注入的网络代理: {custom_proxy or '未配置(直连)'}。若该代理端口未开启，Node.js 握手会无限期卡死。")
    tlog.warning("      建议在卡片配置中设置 proxy: 'direct' 强制使用物理网络直连测试。")
    tlog.warning("   2. 检查 Cloudflare API 令牌是否具有编辑与部署该 Pages 项目的完整权限。")
