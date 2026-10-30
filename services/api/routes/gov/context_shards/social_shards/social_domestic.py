# -*- coding: utf-8 -*-
"""
📣 [V74.98] Domestic Social & Media Channel Dry Run Shard
职责：微信公众号, 知乎, 掘金, 小红书, 头条, CSDN, 博客园, B站, 思否, 开源中国 的真实网络握手与凭证健康校验。
架构：由 plugin_dry_run_social.py 拆分而来 (SOP-02 模块拆分标准)，深度集成 cookie_prober 与 network_sniffer。
🛡️ [SOP-01 规范]：单文件物理行数严格 ≤ 300 行。
"""

import re
import requests
from typing import Dict, Any, List
from core.config.assembler import resolve_secrets
from core.utils.network_sniffer import detect_outbound_ip, format_wechat_whitelist_card
from .cookie_prober import (
    probe_xiaohongshu,
    probe_zhihu,
    probe_bilibili,
    probe_toutiao,
    probe_csdn,
)


def probe_domestic_social(
    plugin_id: str,
    settings: Dict[str, Any],
    logs: List[Dict[str, str]],
    log_func: Any,
    proxies: Dict[str, str]
) -> bool:
    """执行国内主流自媒体与技术社区平台的网络连通性、Cookie 深度健康与出口 IP 嗅探。"""
    success = True

    if plugin_id == "wechat":
        resolved_settings = resolve_secrets(settings) if isinstance(settings, dict) else settings
        app_id = str(resolved_settings.get("app_id", "") or "").strip()
        app_secret = str(resolved_settings.get("app_secret", "") or "").strip()
        if not app_id or not app_secret:
            logs.append(log_func("ERROR", "❌ [错误] 微信公众号 AppID 或 AppSecret 尚未配置。"))
            return False
        
        proxy_val = str(resolved_settings.get("proxy", "") or "").strip()
        effective_proxies = {"http": None, "https": None} if proxy_val.lower() == "direct" else proxies

        logs.append(log_func("INFO", "📡 [探测] 正在连接 微信公众平台 API 端点进行 Access Token 预校验..."))
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
        try:
            resp = requests.get(url, proxies=effective_proxies, timeout=8)
            if resp.status_code == 200:
                res_data = resp.json()
                if "access_token" in res_data:
                    logs.append(log_func("SUCCESS", "🟢 [成功] 微信公众号凭证校验通过，成功握手并换取 Access Token。草稿箱通道就绪。"))
                else:
                    err_code = res_data.get("errcode")
                    err_msg = res_data.get("errmsg", "")
                    if err_code == 40164:
                        ip_match = re.search(r"invalid ip\s+([0-9\.]+)", err_msg)
                        invalid_ip = ip_match.group(1) if ip_match else "未知"
                        detected_info = detect_outbound_ip(proxy=proxy_val, timeout=2.5)
                        detected_ip = detected_info.get("ip")
                        card_lines = format_wechat_whitelist_card(invalid_ip, detected_ip, proxy_val=proxy_val)
                        for line in card_lines:
                            level = "ERROR" if line.startswith("❌") else ("WARN" if line.startswith("⚠️") else "INFO")
                            logs.append(log_func(level, line))
                    elif err_code in (40001, 40013):
                        logs.append(log_func("ERROR", f"❌ [凭证无效 (错误码 {err_code})] 微信 AppID 与 AppSecret 不匹配，请核对公众平台基本配置。"))
                    else:
                        logs.append(log_func("ERROR", f"❌ [授权] 微信端返回鉴权失败 (错误码 {err_code}): {err_msg}"))
                    success = False
            else:
                logs.append(log_func("ERROR", f"❌ [错误] 微信 API 返回异常状态码 {resp.status_code}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 无法连接至 微信公众平台 API 端点: {e}。"))
            success = False

    elif plugin_id == "zhihu":
        return probe_zhihu(settings, logs, log_func, proxies)

    elif plugin_id in ["xiaohongshu", "red"]:
        return probe_xiaohongshu(settings, logs, log_func, proxies)

    elif plugin_id == "bilibili":
        return probe_bilibili(settings, logs, log_func, proxies)

    elif plugin_id == "toutiao":
        return probe_toutiao(settings, logs, log_func, proxies)

    elif plugin_id == "csdn":
        return probe_csdn(settings, logs, log_func, proxies)

    elif plugin_id == "juejin":
        cookie = settings.get("cookie", "")
        api_token = settings.get("api_token", "")
        if not cookie and not api_token:
            logs.append(log_func("ERROR", "❌ [错误] 稀土掘金 Cookie 与 API Token 必须至少配置一项。"))
            return False
        
        logs.append(log_func("INFO", "📡 [探测] 正在校验 掘金 API 连通度与登录身份凭证..."))
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if cookie:
            clean_cookie = cookie.strip()
            if "sessionid" not in clean_cookie and "=" not in clean_cookie and len(clean_cookie) >= 16:
                clean_cookie = f"sessionid={clean_cookie}"
            headers["Cookie"] = clean_cookie
        if api_token:
            headers["X-Juejin-Token"] = api_token

        try:
            user_resp = requests.get(
                "https://api.juejin.cn/user_api/v1/user/get",
                headers=headers,
                proxies=proxies,
                timeout=12
            )
            if user_resp.status_code == 200:
                res_data = user_resp.json()
                err_no = res_data.get("err_no")
                if err_no == 0:
                    user_info = res_data.get("data") or {}
                    u_name = user_info.get("user_name") or "创作者"
                    u_id = user_info.get("user_id") or ""
                    logs.append(log_func("SUCCESS", f"🟢 [成功] 稀土掘金身份探测通过！已连接创作者: {u_name} (UID: {u_id})。草稿箱就绪。"))
                elif err_no in (401, 403, 3000):
                    logs.append(log_func("ERROR", f"❌ [错误] 掘金凭证校验失败 (err_no {err_no}): 登录凭据已过期或无效，请重新提取 Cookie。"))
                    success = False
                else:
                    logs.append(log_func("WARN", f"⚠️ [掘金响应] 接口已连通，凭证返回: {res_data.get('err_msg')} (err_no {err_no})。"))
            else:
                logs.append(log_func("WARN", f"⚠️ [网络握手] 掘金接口返回 HTTP {user_resp.status_code}。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [警告] 无法直接建立与 掘金 API 端的物理连接: {e}。"))
            success = False

    elif plugin_id == "cnblogs":
        token = settings.get("token") or settings.get("bearer_token") or ""
        if not token:
            logs.append(log_func("ERROR", "❌ [错误] 博客园 Personal Access Token / Bearer Token 尚未配置。"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在向 博客园 API 端点发起握手探测..."))
        try:
            resp = requests.head("https://api.cnblogs.com", proxies=proxies, timeout=10)
            logs.append(log_func("SUCCESS", f"🟢 [成功] 博客园 API 服务端点连接正常 (HTTP {resp.status_code})。已装载授权令牌。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [警告] 无法连接至博客园 API 服务: {e}。"))
            success = False

    elif plugin_id == "segmentfault":
        token = settings.get("token") or ""
        cookie = settings.get("cookie") or ""
        if not token and not cookie:
            logs.append(log_func("ERROR", "❌ [错误] SegmentFault 思否 Token 与 Cookie 必须至少配置一项。"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在探测 SegmentFault 思否服务连通性..."))
        try:
            resp = requests.head("https://segmentfault.com", proxies=proxies, timeout=10)
            logs.append(log_func("SUCCESS", f"🟢 [成功] SegmentFault 思否网络握手正常 (HTTP {resp.status_code})。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [警告] 无法连接 SegmentFault 服务器: {e}。"))
            success = False

    elif plugin_id == "oschina":
        access_token = settings.get("access_token") or settings.get("token") or ""
        if not access_token:
            logs.append(log_func("ERROR", "❌ [错误] 开源中国 (OSChina) OpenAPI Access Token 尚未配置。"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在向 开源中国 OpenAPI 端点发起握手..."))
        try:
            resp = requests.head("https://www.oschina.net", proxies=proxies, timeout=10)
            logs.append(log_func("SUCCESS", f"🟢 [成功] 开源中国网络通道正常 (HTTP {resp.status_code})。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [警告] 连接开源中国 OpenAPI 异常: {e}。"))
            success = False

    return success
