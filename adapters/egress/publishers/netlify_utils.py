# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Netlify Publisher Plugin Utilities
模块职责：Netlify 原生 Direct REST API 直传 (Zero-CLI 纯 Python 自闭环)、URL 解析与凭据探针。
🛡️ [SOP-01 & SOP-02]：单文件物理行数严格 ≤ 300 行。
"""

import os
import io
import zipfile
import requests
from typing import Dict, Any, Optional
from core.utils.tracing import tlog


def add_autotherapy_suggestion(err_msg: str) -> str:
    """💡 为 Netlify 错误注入友好免密授权物理自愈提示"""
    if not err_msg:
        return err_msg

    auth_keywords = ["unauthorized", "authentication", "expired", "token", "unrecognized token", "forbidden"]
    if any(kw in err_msg.lower() for kw in auth_keywords):
        return (
            f"{err_msg}\n\n"
            "💡 [自愈建议] Netlify 授权 Token 无效或已过期。\n"
            "推荐操作：请在治理中心配置中，点击「🔑 本地一键免密授权」，系统将后台唤醒授权浏览器并自动回填密钥，免去手动获取的麻烦！"
        )
    return err_msg


def probe_site_api(site_id: str, auth_token: str, proxy: Optional[str] = None, timeout: int = 15) -> bool:
    """
    🟢 探针：通过 Netlify REST API 校验站点与凭据有效性（无需 Netlify CLI）
    """
    if not site_id or not auth_token:
        return False
    url = f"https://api.netlify.com/api/v1/sites/{site_id}"
    headers = {"Authorization": f"Bearer {auth_token}"}
    proxies = {"http": proxy, "https": proxy} if proxy else None
    try:
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False


def deploy_via_direct_api(publisher_inst, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    🚀 Netlify 原生零 CLI (Zero-CLI) Direct Deploy API 直传引擎。
    将本地构建目录打包为内存 ZIP 流，通过官方 OpenAPI 直接部署至 Netlify CDN。
    彻底摆脱对 Node.js、npm 及 netlify-cli 外部宿主依赖。
    """
    site_id = publisher_inst.site_id
    auth_token = publisher_inst.auth_token
    mode_label = "生产" if publisher_inst.prod else "草稿"

    tlog.info(f"🛸 [Netlify Direct API] 正在以 {mode_label} 模式执行原生纯 HTTP 直传部署...")

    # 1. 在内存中打包静态产物目录
    try:
        zip_buffer = io.BytesIO()
        file_count = 0
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(bundle_path):
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, bundle_path)
                    zf.write(full_p, rel_p)
                    file_count += 1
        zip_bytes = zip_buffer.getvalue()
        tlog.info(f"📦 [Netlify Direct API] 产物包已就绪：共 {file_count} 个文件 ({len(zip_bytes) / 1024:.1f} KB)")
    except Exception as ze:
        err = f"产物打包异常: {ze}"
        tlog.error(f"❌ [Netlify Direct API] {err}")
        return {"status": "error", "message": err}

    # 2. 调用 Netlify Direct ZIP Deploy API
    api_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/zip",
    }
    proxy = publisher_inst.get_proxy()
    proxies = {"http": proxy, "https": proxy} if proxy else None
    timeout = publisher_inst.get_timeout(default_timeout=180)

    try:
        resp = requests.post(
            api_url,
            data=zip_bytes,
            headers=headers,
            proxies=proxies,
            timeout=timeout
        )

        if resp.status_code not in (200, 201):
            err_text = resp.text.strip()
            healed = add_autotherapy_suggestion(err_text)
            tlog.error(f"❌ [Netlify Direct API] 部署失败 ({resp.status_code}): {healed[:200]}")
            return {
                "status": "error",
                "message": f"Netlify API deploy failed ({resp.status_code}): {healed}"
            }

        data = resp.json()
        deploy_url = data.get("deploy_ssl_url") or data.get("deploy_url") or data.get("url")
        ssl_url = data.get("ssl_url") or data.get("url")
        live_url = ssl_url if publisher_inst.prod else deploy_url

        tlog.success(f"✅ [Netlify Direct API] 零依赖部署成功！访问地址: {live_url}")
        return {
            "status": "success",
            "site_id": site_id,
            "mode": "production" if publisher_inst.prod else "draft",
            "url": live_url,
            "deploy_url": deploy_url,
            "message": "Deployed via Netlify Native Direct HTTP API (Zero-CLI 自闭环)"
        }

    except requests.exceptions.Timeout:
        tlog.error("❌ [Netlify Direct API] 部署请求超时 (>180s)")
        return {"status": "error", "message": "Netlify API deployment timed out"}
    except Exception as e:
        healed = add_autotherapy_suggestion(str(e))
        tlog.error(f"❌ [Netlify Direct API] 网络通信异常: {healed}")
        return {"status": "error", "message": healed}

