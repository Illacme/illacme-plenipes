# -*- coding: utf-8 -*-
"""
🛰️ [V90.0] Health Radar Operations
职责：并发探测已分发线上站点的连通性、RTT 延迟、HTTP 状态码与 CDN 节点特征。
遵循 SOP-01 核心工程标准与 Rule 8 防御性类型防护。
"""

import time
import socket
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, Field
from core.runtime.engine_singleton import get_global_engine


class HealthRadarRequest(BaseModel):
    urls: List[str] = Field(default_factory=list, description="待探测的公网 URL 列表")


def _resolve_effective_proxy(proxy_arg: Optional[str] = None) -> Optional[str]:
    """解析全局或本机的代理配置，保障全球 CDN 边缘节点探测连通性"""
    if proxy_arg:
        return proxy_arg

    engine = get_global_engine()
    if engine and hasattr(engine, "config"):
        sys_cfg = getattr(engine.config, "system", {})
        if isinstance(sys_cfg, dict) and sys_cfg.get("global_proxy"):
            return sys_cfg["global_proxy"]

    # 嗅探本机常见科学加速端口
    for port in [10809, 7890, 7897, 1087, 8889]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.08)
                if s.connect_ex(('127.0.0.1', port)) == 0:
                    return f"http://127.0.0.1:{port}"
        except Exception:
            continue
    return None


def probe_single_url(url: str, proxy: Optional[str] = None, timeout: float = 4.0) -> Dict[str, Any]:
    """微秒级探测单个线上 URL，提取 HTTP 状态、延迟与 CDN 厂商指纹"""
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return {
            "url": url,
            "status_code": 0,
            "latency_ms": 0,
            "server": "Invalid",
            "is_healthy": False,
            "message": "无效的 URL 协议"
        }

    opener = urllib.request.build_opener()
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
        opener = urllib.request.build_opener(proxy_handler)

    headers = {
        "User-Agent": "Illacme-Plenipes-HealthRadar/1.0 (+https://github.com/Illacme/illacme-press)",
        "Accept": "*/*"
    }

    t0 = time.perf_counter()
    status_code = 0
    server_fingerprint = "Unknown"
    is_healthy = False
    message = ""

    def _inspect_headers(resp_headers) -> str:
        h_dict = {k.lower(): v for k, v in resp_headers.items()}
        if "x-vercel-id" in h_dict:
            return "Vercel"
        if "server" in h_dict and "github.com" in h_dict["server"].lower():
            return "GitHub Pages"
        if "x-github-request-id" in h_dict:
            return "GitHub Pages"
        if "cf-ray" in h_dict or ("server" in h_dict and "cloudflare" in h_dict["server"].lower()):
            return "Cloudflare Pages"
        if "x-nf-request-id" in h_dict:
            return "Netlify"
        if "server" in h_dict:
            return h_dict["server"]
        return "Edge CDN"

    try:
        # 首选 HEAD 请求节约带宽
        req = urllib.request.Request(url, headers=headers, method="HEAD")
        with opener.open(req, timeout=timeout) as resp:
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            status_code = resp.status
            server_fingerprint = _inspect_headers(resp.headers)
            is_healthy = (200 <= status_code < 400)
            message = "OK" if is_healthy else f"HTTP {status_code}"

    except urllib.error.HTTPError as he:
        # 若 405 Method Not Allowed，降级为 GET 只取头部
        if he.code == 405:
            try:
                t_get = time.perf_counter()
                req_get = urllib.request.Request(url, headers=headers, method="GET")
                with opener.open(req_get, timeout=timeout) as resp_get:
                    latency_ms = max(1, int((time.perf_counter() - t_get) * 1000))
                    status_code = resp_get.status
                    server_fingerprint = _inspect_headers(resp_get.headers)
                    is_healthy = (200 <= status_code < 400)
                    message = "OK" if is_healthy else f"HTTP {status_code}"
            except Exception as e_get:
                latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
                status_code = getattr(e_get, "code", 0)
                is_healthy = False
                message = f"HTTP {status_code}" if status_code else str(e_get)
        else:
            latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
            status_code = he.code
            server_fingerprint = _inspect_headers(he.headers) if hasattr(he, "headers") else "Unknown"
            if status_code == 404:
                message = "边缘部署同步中 (HTTP 404)"
            else:
                message = f"HTTP {status_code}"
            is_healthy = False

    except urllib.error.URLError as ue:
        latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
        is_healthy = False
        err_str = str(ue.reason) if hasattr(ue, "reason") else str(ue)
        if "timed out" in err_str.lower():
            message = "探测超时 (Timeout)"
        elif "nodename nor servname" in err_str.lower():
            message = "DNS 域名未解析"
        else:
            message = "网络连通异常"

    except Exception as e:
        latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
        is_healthy = False
        message = str(e)

    return {
        "url": url,
        "status_code": status_code,
        "latency_ms": latency_ms,
        "server": server_fingerprint,
        "is_healthy": is_healthy,
        "message": message
    }


def probe_all_urls_impl(urls: List[str], proxy_arg: Optional[str] = None) -> List[Dict[str, Any]]:
    """并发多路探测给定的 URL 列表"""
    if not urls:
        return []

    effective_proxy = _resolve_effective_proxy(proxy_arg)
    results = []

    # 限制最大并发量为 6
    max_workers = min(len(urls), 6)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(probe_single_url, u, effective_proxy) for u in urls]
        for f in futures:
            try:
                results.append(f.result(timeout=6.0))
            except Exception as e:
                results.append({
                    "url": "unknown",
                    "status_code": 0,
                    "latency_ms": 0,
                    "server": "Unknown",
                    "is_healthy": False,
                    "message": f"探测调度异常: {e}"
                })

    return results
