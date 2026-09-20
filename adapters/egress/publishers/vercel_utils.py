#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Vercel Publisher Plugin Utilities
模块职责：Vercel CLI 执行辅助、URL 提取、代理环境变量注入与异常自愈建议。
🛡️ [SOP-01 & SOP-02]：从 vercel.py 拆解的独立辅助分片。
"""

import re
import subprocess
from typing import Optional
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
