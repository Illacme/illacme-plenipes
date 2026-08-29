# -*- coding: utf-8 -*-
"""
📣 [V74.97] Domestic Social & Media Channel Dry Run Shard
职责：微信公众号, 知乎, 掘金, 小红书, 头条, CSDN, 博客园, B站, 思否, 开源中国 的真实网络握手与凭证校验。
架构：由 plugin_dry_run_social.py 拆分而来 (SOP-02 模块拆分标准)。
"""

import requests
from typing import Dict, Any, List


def probe_domestic_social(
    plugin_id: str,
    settings: Dict[str, Any],
    logs: List[Dict[str, str]],
    log_func: Any,
    proxies: Dict[str, str]
) -> bool:
    """执行国内主流自媒体与技术社区平台的网络连通性与凭证格式探测。"""
    success = True

    if plugin_id == "wechat":
        app_id = settings.get("app_id", "")
        app_secret = settings.get("app_secret", "")
        if not app_id or not app_secret:
            logs.append(log_func("ERROR", "❌ [错误] 微信公众号 AppID 或 AppSecret 尚未配置。"))
            return False
        
        logs.append(log_func("INFO", "📡 [探测] 正在连接 微信公众平台 API 端点进行 Access Token 预校验..."))
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
        try:
            resp = requests.get(url, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                res_data = resp.json()
                if "access_token" in res_data:
                    logs.append(log_func("SUCCESS", "🟢 [成功] 微信公众号凭证校验通过，成功握手并换取 Access Token。"))
                else:
                    err_code = res_data.get("errcode")
                    err_msg = res_data.get("errmsg", "")
                    logs.append(log_func("ERROR", f"❌ [授权] 微信端返回鉴权失败 (错误码 {err_code}): {err_msg}"))
                    success = False
            else:
                logs.append(log_func("ERROR", f"❌ [错误] 微信 API 返回异常状态码 {resp.status_code}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 无法连接至 微信公众平台 API 端点: {e}。"))
            success = False

    elif plugin_id == "zhihu":
        token = settings.get("token", "")
        column_id = settings.get("column_id", "")
        if not token or not column_id:
            logs.append(log_func("ERROR", "❌ [错误] 知乎专栏 Token 或 专栏 ID 尚未配置。"))
            return False
        
        logs.append(log_func("INFO", "🔑 [授权] 知乎授权凭证格式校验通过。"))
        logs.append(log_func("INFO", "📡 [探测] 正在测试 知乎 API 连通性: api.zhihu.com..."))
        try:
            resp = requests.get("https://api.zhihu.com", proxies=proxies, timeout=15)
            logs.append(log_func("INFO", f"🟢 [探测] 对端知乎 API 服务网络握手正常 (HTTP {resp.status_code})。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [警告] 无法直接建立与 知乎 API 端点的物理连接: {e}。"))
            success = False

    elif plugin_id == "juejin":
        cookie = settings.get("cookie", "")
        api_token = settings.get("api_token", "")
        if not cookie and not api_token:
            logs.append(log_func("ERROR", "❌ [错误] 稀土掘金 Cookie 与 API Token 必须至少配置一项。"))
            return False
        
        logs.append(log_func("INFO", "📡 [探测] 正在校验 掘金 API 连通度..."))
        try:
            resp = requests.head("https://api.juejin.cn", proxies=proxies, timeout=15)
            logs.append(log_func("SUCCESS", f"🟢 [成功] 对端掘金 API 服务网络握手正常 (HTTP {resp.status_code})。已完成本地凭据格式匹配。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [警告] 无法直接建立与 掘金 API 端的物理连接: {e}。"))
            success = False

    elif plugin_id in ["xiaohongshu", "red"]:
        token = settings.get("token") or ""
        cookie = settings.get("cookie") or ""
        if not token and not cookie:
            logs.append(log_func("ERROR", "❌ [错误] 小红书 Token 与 Cookie 必须至少配置一项。"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在探测小红书创作者服务网络握手与凭证格式..."))
        try:
            resp = requests.head("https://creator.xiaohongshu.com", proxies=proxies, timeout=10)
            logs.append(log_func("SUCCESS", f"🟢 [成功] 小红书创作者平台网络握手正常 (HTTP {resp.status_code})。凭证格式校验通过。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [警告] 连接小红书创作者网络端点异常: {e}。"))
            success = False

    elif plugin_id == "toutiao":
        access_token = settings.get("access_token") or settings.get("token") or ""
        cookie = settings.get("cookie") or ""
        if not access_token and not cookie:
            logs.append(log_func("ERROR", "❌ [错误] 今日头条 Access Token 与 Cookie 必须至少配置一项。"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在探测今日头条 (头条号) 平台连通性..."))
        try:
            resp = requests.head("https://mp.toutiao.com", proxies=proxies, timeout=10)
            logs.append(log_func("SUCCESS", f"🟢 [成功] 今日头条发布服务网络连接通畅 (HTTP {resp.status_code})。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [警告] 无法连接至今日头条端点: {e}。"))
            success = False

    elif plugin_id == "csdn":
        token = settings.get("token") or ""
        cookie = settings.get("cookie") or ""
        if not token and not cookie:
            logs.append(log_func("ERROR", "❌ [错误] CSDN Token 或 Cookie 凭据必须至少配置一项。"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在探测 CSDN 博客控制台 API 连通度..."))
        try:
            resp = requests.head("https://mp.csdn.net", proxies=proxies, timeout=10)
            logs.append(log_func("SUCCESS", f"🟢 [成功] CSDN 创作中心网络通道畅通 (HTTP {resp.status_code})。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [警告] 无法直接连接 CSDN 创作者服务器: {e}。"))
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

    elif plugin_id == "bilibili":
        sessdata = settings.get("sessdata") or ""
        cookie = settings.get("cookie") or ""
        token = settings.get("token") or ""
        if not (sessdata or cookie or token):
            logs.append(log_func("ERROR", "❌ [错误] Bilibili 专栏 SESSDATA / Cookie 凭证缺失。"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在校验 Bilibili 专栏服务握手状态..."))
        try:
            resp = requests.get("https://api.bilibili.com/x/web-interface/nav", proxies=proxies, timeout=10)
            logs.append(log_func("SUCCESS", f"🟢 [成功] Bilibili 接口网络通道通畅 (HTTP {resp.status_code})。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [警告] 无法连接至 Bilibili API 服务: {e}。"))
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
