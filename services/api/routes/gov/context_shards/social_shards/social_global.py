# -*- coding: utf-8 -*-
"""
📣 [V74.97] Global Social & Syndication Channel Dry Run Shard
职责：Dev.to, Hashnode, Medium, WordPress, Ghost, Substack, Telegram, Discord 的真实 API 握手与凭证探测。
架构：由 plugin_dry_run_social.py 拆分而来 (SOP-02 模块拆分标准)。
"""

import requests
from typing import Dict, Any, List
from requests.auth import HTTPBasicAuth


def probe_global_social(
    plugin_id: str,
    settings: Dict[str, Any],
    logs: List[Dict[str, str]],
    log_func: Any,
    proxies: Dict[str, str]
) -> bool:
    """执行海外社交、独立博客与即时通讯分发平台的真实 API 握手与凭证探测。"""
    success = True

    if plugin_id == "substack":
        home_url = settings.get("url", "")
        if not home_url:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 Substack 首页 URL。"))
            return False
        
        logs.append(log_func("INFO", f"📡 [探测] 正在测试 Substack 网络端点连通性: {home_url}..."))
        try:
            resp = requests.head(home_url, proxies=proxies, timeout=8)
            logs.append(log_func("SUCCESS", f"🟢 [成功] 对端 Substack 页面访问正常 (HTTP {resp.status_code})。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [警告] 无法直接连接至 Substack 端点: {e}。"))
            success = False

    elif plugin_id == "telegram":
        bot_token = settings.get("bot_token", "")
        chat_id = settings.get("chat_id", "")
        if not bot_token or not chat_id:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 Telegram Bot Token 或 目标 Chat ID。"))
            return False
        elif ":" not in bot_token:
            logs.append(log_func("ERROR", "❌ [错误] Telegram Bot Token 格式不合法 (应包含冒号 ':')。"))
            return False
        
        logs.append(log_func("INFO", "📡 [探测] 正在验证 Telegram Bot Token 的有效性..."))
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        try:
            resp = requests.get(url, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                res_data = resp.json()
                if res_data.get("ok"):
                    bot_name = res_data["result"].get("username", "")
                    logs.append(log_func("SUCCESS", f"🟢 [成功] Telegram 凭证有效！成功匹配机器人: @{bot_name}。"))
                else:
                    logs.append(log_func("ERROR", "❌ [授权] Telegram 返回 Token 无效。"))
                    success = False
            else:
                logs.append(log_func("ERROR", f"❌ [错误] Telegram API 返回错误状态码 {resp.status_code}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 无法连接到 Telegram API: {e}。若在中国大陆，请配置代理地址。"))
            success = False

    elif plugin_id == "discord":
        webhook_url = settings.get("webhook_url", "")
        if not webhook_url:
            logs.append(log_func("ERROR", "❌ [错误] Discord Webhook URL 尚未配置。"))
            return False
        elif not any(wh in webhook_url for wh in ["discord.com/api/webhooks/", "discordapp.com/api/webhooks/"]):
            logs.append(log_func("ERROR", "❌ [错误] Discord Webhook URL 格式不正确。"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在校验 Discord Webhook 的真实有效性..."))
        try:
            resp = requests.get(webhook_url, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                logs.append(log_func("SUCCESS", "🟢 [成功] Discord Webhook 验证成功，物理端点状态正常。"))
            else:
                logs.append(log_func("ERROR", f"❌ [错误] Discord 返回异常状态码 {resp.status_code}，Webhook 可能已失效。"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 无法建立与 Discord Webhook 端点的物理连接: {e}。"))
            success = False

    elif plugin_id in ["dev_to", "devto"]:
        api_key = settings.get("api_key") or settings.get("token") or ""
        if not api_key:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 Dev.to API Key (可在极简向导中获取)。"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在连接 Dev.to API 校验凭证有效性..."))
        url = "https://dev.to/api/users/me"
        headers = {"api-key": api_key}
        try:
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                user_data = resp.json()
                username = user_data.get("username", "")
                logs.append(log_func("SUCCESS", f"🟢 [成功] Dev.to 凭证校验通过！成功对接用户: {username}。"))
            elif resp.status_code in [401, 403]:
                logs.append(log_func("ERROR", "❌ [错误] Dev.to API Key 无效或已失效，请核对权限。"))
                success = False
            else:
                logs.append(log_func("ERROR", f"❌ [错误] Dev.to API 返回异常状态码 {resp.status_code}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 无法连接到 Dev.to API: {e}。建议配置代理。"))
            success = False

    elif plugin_id == "hashnode":
        api_key = settings.get("token") or settings.get("api_key") or settings.get("integration_token") or ""
        if not api_key:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 Hashnode 个人访问令牌 (PAT)。"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在通过 GraphQL API 校验 Hashnode 凭证..."))
        url = "https://gql.hashnode.com"
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        payload = {"query": "query { me { id username name } }"}
        try:
            resp = requests.post(url, headers=headers, json=payload, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                res_data = resp.json()
                errors = res_data.get("errors")
                if errors:
                    logs.append(log_func("ERROR", f"❌ [授权] Hashnode API 校验失败: {errors[0].get('message')}"))
                    success = False
                else:
                    me = res_data.get("data", {}).get("me") or {}
                    logs.append(log_func("SUCCESS", f"🟢 [成功] Hashnode 凭证有效！成功匹配作者: {me.get('name')} (@{me.get('username')})。"))
            else:
                logs.append(log_func("ERROR", f"❌ [错误] Hashnode GraphQL API 返回异常状态码 {resp.status_code}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 连接 Hashnode API 超时或出错: {e}。"))
            success = False

    elif plugin_id == "medium":
        token = settings.get("token") or settings.get("api_key") or settings.get("integration_token") or ""
        if not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 Medium 集成令牌 (Integration Token)。"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在连接 Medium API 校验凭证有效性..."))
        url = "https://api.medium.com/v1/me"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                user_data = resp.json().get("data", {})
                name = user_data.get("name", "")
                logs.append(log_func("SUCCESS", f"🟢 [成功] Medium 凭证校验通过！成功匹配作家: {name}。"))
            elif resp.status_code in [401, 403]:
                logs.append(log_func("ERROR", "❌ [错误] Medium 访问令牌无效或已过期。"))
                success = False
            else:
                logs.append(log_func("ERROR", f"❌ [错误] Medium API 返回异常状态码 {resp.status_code}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 连接 Medium API 出错: {e}。"))
            success = False

    elif plugin_id == "wordpress":
        url = settings.get("url") or ""
        username = settings.get("username") or ""
        app_password = settings.get("app_password") or settings.get("api_key") or ""

        if not url or not username or not app_password:
            logs.append(log_func("ERROR", "❌ [错误] WordPress 配置不完整：需要填写站点 URL、用户名与应用密码。"))
            return False

        logs.append(log_func("INFO", f"📡 [探测] 正在通过 REST API 校验 WordPress 凭证 ({url})..."))
        wp_api_url = url.rstrip("/") + "/wp-json/wp/v2/users/me"
        try:
            auth = HTTPBasicAuth(username, app_password)
            resp = requests.get(wp_api_url, auth=auth, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                logs.append(log_func("SUCCESS", "🟢 [成功] WordPress 账号与应用密码鉴权通过！"))
            elif resp.status_code in [401, 403]:
                check_root = requests.get(url.rstrip("/") + "/wp-json", proxies=proxies, timeout=6)
                if check_root.status_code == 200:
                    logs.append(log_func("ERROR", "❌ [错误] WordPress 鉴权失败：用户名或应用密码 (Application Password) 错误。"))
                else:
                    logs.append(log_func("ERROR", f"❌ [错误] 无法定位 WordPress API 服务，请确认您的站点地址 '{url}' 是否正确配置，或是否启用了伪静态/REST API。"))
                success = False
            else:
                logs.append(log_func("ERROR", f"❌ [错误] WordPress API 返回异常状态码 {resp.status_code}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 连接 WordPress 站点超时或出错: {e}。"))
            success = False

    elif plugin_id == "ghost":
        url = settings.get("url") or ""
        content_key = settings.get("content_api_key") or settings.get("api_key") or ""
        if not url or not content_key:
            logs.append(log_func("ERROR", "❌ [错误] Ghost 配置不完整：站点 URL 或 API Key 缺失。"))
            return False

        if not (url.startswith("http://") or url.startswith("https://")):
            logs.append(log_func("ERROR", f"❌ [错误] 物理端点 URL 格式不合法 (缺少 http:// 或 https://): '{url}'"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在校验 Ghost 站点可达性与 API Key..."))
        ghost_api = f"{url.rstrip('/')}/ghost/api/content/posts/?key={content_key}&limit=1"
        try:
            resp = requests.get(ghost_api, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                logs.append(log_func("SUCCESS", "🟢 [成功] Ghost 访问凭证及 API Key 校验通过！"))
            elif resp.status_code == 401:
                logs.append(log_func("ERROR", "❌ [错误] Ghost API 鉴权失败：API Key 无效。"))
                success = False
            else:
                logs.append(log_func("ERROR", f"❌ [错误] Ghost 接口返回异常 HTTP {resp.status_code}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 无法连接 Ghost 站点: {e}。"))
            success = False

    return success
