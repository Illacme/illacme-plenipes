#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Vercel Publisher Plugin Utilities
模块职责：Vercel CLI 执行辅助、URL 提取、代理环境变量注入与异常自愈建议。
🛡️ [SOP-01 & SOP-02]：从 vercel.py 拆解的独立辅助分片。
"""

import os
import re
import base64
import subprocess
import requests
from typing import Optional, Dict, Any
from core.utils.tracing import tlog


def add_autotherapy_suggestion(err_msg: str) -> str:
    """💡 为 Vercel 错误注入友好免密授权物理自愈提示。"""
    if not err_msg:
        return err_msg

    auth_keywords = ["unauthorized", "forbidden", "token", "login", "expired", "invalid token"]
    if any(kw in err_msg.lower() for kw in auth_keywords):
        return (
            f"{err_msg}\n\n"
            "💡 [自愈建议] Vercel 授权 Token 无效或已过期。\n"
            "推荐操作：请在治理中心配置中，点击「🔑 本地一键免密授权」，系统将后台唤醒授权浏览器并自动回填密钥，免去手动获取的麻烦！"
        )
    return err_msg


def resolve_proxy_env(proxy: str, env: dict) -> dict:
    """注入代理环境变量，确保国内环境发布至全球边缘节点网络链路高可用"""
    effective_proxy = proxy or env.get("HTTPS_PROXY") or env.get("HTTP_PROXY") or env.get("https_proxy") or env.get("http_proxy")
    if not effective_proxy:
        import socket
        for port in [10809, 7890, 7897, 1087, 8889]:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.15)
                if s.connect_ex(('127.0.0.1', port)) == 0:
                    effective_proxy = f"http://127.0.0.1:{port}"
                    break
    if effective_proxy:
        for k in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
            env[k] = effective_proxy
    return env


def sanitize_cmd_for_log(cmd: list) -> str:
    """脱敏命令行日志（隐藏 Token）"""
    sanitized = []
    for arg in cmd:
        if arg.startswith("--token="):
            sanitized.append("--token=***")
        else:
            sanitized.append(arg)
    return " ".join(sanitized)


def extract_deploy_url(stdout: str) -> Optional[str]:
    """
    从 Vercel CLI stdout 中解析部署 URL。
    Vercel CLI 成功部署后通常直接输出 URL (如 https://xxx.vercel.app)。
    """
    if not stdout:
        return None

    lines = stdout.strip().split('\n')
    for line in reversed(lines):
        line = line.strip().rstrip('",\';')
        if line.startswith("https://"):
            return line

    url_pattern = re.compile(r'(https://[a-zA-Z0-9\-\.]+\.vercel\.app)', re.IGNORECASE)
    match = url_pattern.search(stdout)
    if match:
        return match.group(1).rstrip('",\';')

    fallback_pattern = re.compile(r'(https://[^\s",\';]+)')
    match = fallback_pattern.search(stdout)
    return match.group(1).rstrip('",\';') if match else None


def auto_create_project(executable: list, project_name: str, token: str, org_id: str = "") -> bool:
    """🚀 [V48.4] 远端项目自动创建自愈：若项目未创建，全自动调用 vercel project add 创建"""
    if not project_name:
        return False
    cmd = executable + [
        "project", "add", project_name,
        f"--token={token}"
    ]
    if org_id:
        cmd.extend(["--scope", org_id])
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode == 0:
            tlog.info(f"✨ [Vercel] 远端项目自愈创建成功: {project_name}")
            return True
    except Exception as e:
        tlog.warning(f"⚠️ [Vercel] 远端项目自动创建异常: {e}")
    return False


def deploy_via_direct_api(publisher_inst, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    🚀 Vercel 原生零 CLI (Zero-CLI) Direct Deploy REST API 直传引擎。
    将本地静态构建目录转译为多文件载荷，通过官方 OpenAPI 直接部署至 Vercel Edge Network。
    彻底摆脱对 Node.js、npm 及 vercel CLI 外部宿主依赖。
    """
    token = publisher_inst.token
    project_name = publisher_inst.project_name or "sovereign-press"
    mode_label = "生产" if publisher_inst.prod else "预览"

    tlog.info(f"🛸 [Vercel Direct API] 正在以 {mode_label} 模式执行原生纯 HTTP 直传部署...")

    # 1. 扫描并打包文件清单
    text_exts = {".html", ".css", ".js", ".mjs", ".json", ".svg", ".xml", ".txt", ".md", ".map"}
    files_payload = []
    file_count = 0
    total_bytes = 0

    try:
        for root, _, files in os.walk(bundle_path):
            for f in files:
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, bundle_path).replace("\\", "/")
                ext = os.path.splitext(f)[1].lower()
                is_text = ext in text_exts

                with open(full_p, "rb") as fp:
                    raw_bytes = fp.read()
                total_bytes += len(raw_bytes)
                file_count += 1

                if is_text:
                    try:
                        content_str = raw_bytes.decode("utf-8")
                        files_payload.append({
                            "file": rel_p,
                            "data": content_str,
                            "encoding": "utf-8"
                        })
                    except UnicodeDecodeError:
                        files_payload.append({
                            "file": rel_p,
                            "data": base64.b64encode(raw_bytes).decode("ascii"),
                            "encoding": "base64"
                        })
                else:
                    files_payload.append({
                        "file": rel_p,
                        "data": base64.b64encode(raw_bytes).decode("ascii"),
                        "encoding": "base64"
                    })

        tlog.info(f"📦 [Vercel Direct API] 文件载荷就绪：共 {file_count} 个文件 ({total_bytes / 1024:.1f} KB)")
    except Exception as pe:
        err = f"产物读取转译异常: {pe}"
        tlog.error(f"❌ [Vercel Direct API] {err}")
        return {"status": "error", "message": err}

    # 2. 构造 REST API 请求
    api_url = "https://api.vercel.com/v13/deployments"
    if publisher_inst.org_id:
        api_url += f"?teamId={publisher_inst.org_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "name": project_name,
        "projectSettings": {"framework": None},
        "files": files_payload
    }
    if publisher_inst.prod:
        body["target"] = "production"

    proxy = publisher_inst.get_proxy()
    proxies = {"http": proxy, "https": proxy} if proxy else None
    timeout = publisher_inst.get_timeout(default_timeout=180)

    try:
        resp = requests.post(
            api_url,
            json=body,
            headers=headers,
            proxies=proxies,
            timeout=timeout
        )

        if resp.status_code not in (200, 201):
            err_text = resp.text.strip()
            healed = add_autotherapy_suggestion(err_text)
            tlog.error(f"❌ [Vercel Direct API] 部署失败 ({resp.status_code}): {healed[:200]}")
            return {
                "status": "error",
                "message": f"Vercel API deploy failed ({resp.status_code}): {healed}"
            }

        data = resp.json()
        deploy_url = f"https://{data.get('url')}" if data.get("url") else None
        canonical_url = f"https://{project_name}.vercel.app" if project_name else ""
        live_url = canonical_url if (publisher_inst.prod and canonical_url) else (deploy_url or canonical_url)

        tlog.success(f"✅ [Vercel Direct API] 零依赖部署成功！访问地址: {live_url}")
        return {
            "status": "success",
            "project": project_name,
            "mode": "production" if publisher_inst.prod else "preview",
            "url": live_url,
            "deployment_url": deploy_url,
            "message": "Deployed via Vercel Native Direct HTTP API (Zero-CLI 自闭环)"
        }

    except requests.exceptions.Timeout:
        tlog.error("❌ [Vercel Direct API] 部署请求超时 (>180s)")
        return {"status": "error", "message": "Vercel API deployment timed out after 180 seconds"}
    except Exception as e:
        healed = add_autotherapy_suggestion(str(e))
        tlog.error(f"❌ [Vercel Direct API] 网络通信异常: {healed}")
        return {"status": "error", "message": healed}
