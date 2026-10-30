# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Outbound Network & Public IP Sniffer
模块职责：提供公网出口 IP 实时嗅探、网络代理模式识别与微信 IP 白名单拦截自愈卡片合成。
🛡️ [SOP-01 规范]：单文件物理行数严格 ≤ 300 行。
"""

import re
import requests
from typing import Dict, Any, Optional, List
from core.utils.tracing import tlog

IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

# 极速公网 IP 反射探测端点矩阵 (针对国内微信直连与海外分流场景分类优化)
DOMESTIC_IP_ENDPOINTS = [
    ("https://myip.ipip.net", "text", None),
    ("https://ip.sb", "text", None),
    ("https://api.ipify.org?format=json", "json", "ip"),
    ("https://httpbin.org/ip", "json", "origin"),
]

GLOBAL_IP_ENDPOINTS = [
    ("https://api.ipify.org?format=json", "json", "ip"),
    ("https://httpbin.org/ip", "json", "origin"),
    ("https://myip.ipip.net", "text", None),
    ("https://ip.sb", "text", None),
]


def detect_outbound_ip(proxy: Optional[str] = None, timeout: float = 3.5, scope: str = "domestic") -> Dict[str, Any]:
    """
    🌐 探针：探测当前网络连接微信/外部生态的实际公网出口 IP。
    支持显式 proxy: direct 直连穿透与 HTTP/Socks 代理隧道。
    针对微信公众号等国内直连平台，默认使用国内权威端点 (myip.ipip.net) 探测，
    杜绝科学上网代理分流造成的海外伪出口 IP 误判。
    """
    is_direct = False
    proxies = None

    if proxy:
        p_clean = str(proxy).strip()
        if p_clean.lower() == "direct":
            is_direct = True
            proxies = {"http": None, "https": None}
        else:
            proxies = {"http": p_clean, "https": p_clean}
    elif scope == "domestic":
        is_direct = True
        proxies = {"http": None, "https": None}

    endpoints = DOMESTIC_IP_ENDPOINTS if scope == "domestic" else GLOBAL_IP_ENDPOINTS

    for url, mode, field in endpoints:
        try:
            resp = requests.get(url, proxies=proxies, timeout=timeout)
            if resp.status_code == 200:
                raw_text = resp.text.strip()
                target_ip = None

                if mode == "json" and field:
                    try:
                        data = resp.json()
                        val = str(data.get(field, "")).strip()
                        # httpbin 可能返回 "ip1, ip2"
                        if "," in val:
                            val = val.split(",")[0].strip()
                        match = IP_REGEX.search(val)
                        if match:
                            target_ip = match.group(0)
                    except Exception:
                        pass

                if not target_ip:
                    match = IP_REGEX.search(raw_text)
                    if match:
                        target_ip = match.group(0)

                if target_ip:
                    return {
                        "ip": target_ip,
                        "proxy": proxy or "direct",
                        "is_direct": is_direct,
                        "endpoint": url,
                        "success": True,
                    }
        except Exception:
            continue

    return {
        "ip": None,
        "proxy": proxy or "direct",
        "is_direct": is_direct,
        "endpoint": None,
        "success": False,
    }


def format_wechat_whitelist_card(
    invalid_ip: str,
    detected_ip: Optional[str] = None,
    proxy_val: str = "",
) -> List[str]:
    """
    📋 合成亲和且精准的微信公众号 IP 白名单 3 步秒解指南卡片。
    """
    target_ip = invalid_ip if (invalid_ip and invalid_ip != "未知") else (detected_ip or "未知")
    lines: List[str] = [
        "❌ [IP 白名单拦截 (40164)] 微信公众平台拒绝当前出口 IP 访问 OpenAPI。",
        f"🌐 [精准嗅探出口 IP] 【{target_ip}】(已为您自动识别捕获)",
        "💡 [3步秒解指引]：",
        "   1. 打开微信公众平台: https://mp.weixin.qq.com 并登录",
        "   2. 进入左侧导航【开发】->【基本配置】->【IP白名单】-> 点击【修改】",
        f"   3. 将目标 IP【{target_ip}】粘贴填入列表并保存 (手机微信扫码即时生效)",
    ]

    p_clean = str(proxy_val or "").strip()
    if p_clean and p_clean.lower() != "direct":
        lines.append(f"⚠️ [网络代理注意] 检测到您配置了网络代理 [{p_clean}]。如果出口 IP 频繁变动，建议在插件配置中将 proxy 设置为 'direct' (例如 proxy: direct) 强制使用本机宽带直连！")
    else:
        lines.append("💡 [稳定建议] 家用宽带出口 IP 变动较小，若后续 IP 发生漂移，重新在此处点击【测试连接】即可一键刷新最新 IP。")

    return lines
