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
import hashlib
import requests
from typing import Optional, List, Dict, Any
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


def deploy_via_direct_api(publisher_inst, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    🚀 Cloudflare Pages 原生零 CLI (Zero-CLI) Direct Deploy REST API 直传引擎。
    通过官方 OpenAPI 直接部署静态资产至 Cloudflare Edge 网络。
    彻底摆脱对 Node.js、npm 及 wrangler CLI 外部宿主依赖。
    """
    account_id = publisher_inst.account_id
    project_name = publisher_inst.project_name
    token = publisher_inst.token or os.environ.get("CLOUDFLARE_API_TOKEN", "")
    branch = publisher_inst.branch or "production"

    tlog.info(f"🛸 [Cloudflare Direct API] 正在以分支 '{branch}' 执行原生纯 HTTP 直传部署...")

    # 1. 扫描计算资产哈希清单与二进制载荷
    manifest = {}
    file_map = {}
    file_count = 0
    total_bytes = 0

    try:
        for root, _, files in os.walk(bundle_path):
            for f in files:
                full_p = os.path.join(root, f)
                rel_p = "/" + os.path.relpath(full_p, bundle_path).replace("\\", "/").lstrip("/")
                with open(full_p, "rb") as fp:
                    content = fp.read()
                file_hash = hashlib.sha1(content).hexdigest()
                manifest[rel_p] = file_hash
                file_map[file_hash] = content
                file_count += 1
                total_bytes += len(content)

        tlog.info(f"📦 [Cloudflare Direct API] 资产哈希清单就绪：共 {file_count} 个文件 ({total_bytes / 1024:.1f} KB)")
    except Exception as pe:
        err = f"资产哈希计算异常: {pe}"
        tlog.error(f"❌ [Cloudflare Direct API] {err}")
        return {"status": "error", "message": err}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    proxy = publisher_inst.get_proxy()
    proxies = {"http": proxy, "https": proxy} if proxy else None
    timeout = publisher_inst.get_timeout(default_timeout=180)

    try:
        # 2. 探查并上传缺失资产 (Check missing assets)
        check_url = "https://api.cloudflare.com/client/v4/pages/assets/check-missing"
        check_resp = requests.post(check_url, json={"hashes": list(file_map.keys())}, headers=headers, proxies=proxies, timeout=timeout)
        jwt = ""
        missing_hashes = []
        if check_resp.status_code == 200:
            cdata = check_resp.json()
            missing_hashes = cdata.get("result", [])
            jwt = cdata.get("jwt") or check_resp.headers.get("x-amz-cf-jwt") or ""
        else:
            missing_hashes = list(file_map.keys())

        if missing_hashes:
            upload_url = "https://api.cloudflare.com/client/v4/pages/assets/upload"
            up_headers = {"Authorization": f"Bearer {token}"}
            if jwt:
                up_headers["jwt"] = jwt
            for h in missing_hashes:
                if h in file_map:
                    requests.post(upload_url, data=file_map[h], headers=up_headers, proxies=proxies, timeout=timeout)

        # 3. 创建部署 (Create Deployment via Manifest)
        deploy_url_api = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{project_name}/deployments"
        deploy_payload = {"manifest": manifest, "branch": branch}
        deploy_resp = requests.post(deploy_url_api, json=deploy_payload, headers=headers, proxies=proxies, timeout=timeout)

        if deploy_resp.status_code not in (200, 201):
            err_text = deploy_resp.text.strip()
            emit_cloudflare_error_diagnostics(err_text)
            return {"status": "error", "message": f"Cloudflare API deploy failed ({deploy_resp.status_code}): {err_text[:200]}"}

        ddata = deploy_resp.json().get("result", {})
        live_url = ddata.get("url") or f"https://{project_name}.pages.dev"
        tlog.success(f"✅ [Cloudflare Direct API] 零依赖部署成功！访问地址: {live_url}")
        return {
            "status": "success",
            "project": project_name,
            "branch": branch,
            "url": live_url,
            "message": "Deployed via Cloudflare Native Direct HTTP API (Zero-CLI 自闭环)"
        }
    except Exception as e:
        err_msg = str(e)
        emit_cloudflare_error_diagnostics(err_msg)
        return {"status": "error", "message": err_msg}
