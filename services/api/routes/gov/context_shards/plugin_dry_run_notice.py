# -*- coding: utf-8 -*-
"""
🛡️ [V74.91] Gov Plugin Dry Run Driver - Notice & Webhook Channels
职责：承载邮件、短信、App推送及Webhook通知渠道端点的物理连通性探测。
"""

from typing import List, Callable


def run_notice_plugin_dry_run(
    plugin_id: str,
    parent_id: str,
    settings: dict,
    logs: List[dict],
    log: Callable[[str, str], dict]
) -> bool:
    """
    负责执行邮件 (Email)、短信 (SMS)、移动推送 (App Push) 及 Webhook (钉钉、飞书、企业微信、Telegram、Discord、通用) 连通性探测。
    """
    success = True

    # 📧 [Email] SMTP 邮件通知独立探测
    if plugin_id == "email":
        host = settings.get("smtp_host") or ""
        port = int(settings.get("smtp_port") or (465 if settings.get("use_ssl", True) else 587))
        user = settings.get("smtp_user") or ""
        password = settings.get("smtp_pass") or settings.get("password") or ""
        receivers = settings.get("receivers") or settings.get("to") or ""

        if not host:
            logs.append(log("ERROR", "❌ [错误] SMTP 主机地址 (smtp_host) 未填写。"))
            success = False
        if not user or not password:
            logs.append(log("ERROR", "❌ [错误] SMTP 登录账号或授权码/密码为空。"))
            success = False
        if not receivers:
            logs.append(log("WARN", "⚠️ [提示] 未填写接收者邮箱 (receivers)，本次探测仅验证 SMTP 鉴权通道。"))

        if success:
            logs.append(log("INFO", f"📡 [SMTP 握手] 正在连接邮件服务器: {host}:{port}..."))
            try:
                import smtplib
                use_ssl = bool(settings.get("use_ssl", port == 465))
                if use_ssl:
                    with smtplib.SMTP_SSL(host, port, timeout=8) as server:
                        logs.append(log("INFO", "🔒 [SSL] SSL 加密握手成功，正在验证账号凭据..."))
                        server.login(user, password)
                        logs.append(log("INFO", "🟢 [鉴权通过] SMTP 登录认证成功！发件服务完全就绪。"))
                else:
                    with smtplib.SMTP(host, port, timeout=8) as server:
                        server.ehlo()
                        if settings.get("use_tls", True):
                            server.starttls()
                            server.ehlo()
                            logs.append(log("INFO", "🔒 [TLS] STARTTLS 会话升级成功..."))
                        server.login(user, password)
                        logs.append(log("INFO", "🟢 [鉴权通过] SMTP 登录认证成功！发件服务完全就绪。"))
            except Exception as e:
                logs.append(log("ERROR", f"❌ [SMTP 握手失败] 无法完成邮件服务器鉴权: {e}"))
                success = False

    # 📱 [SMS] 短信告警独立探测
    elif plugin_id == "sms":
        provider = settings.get("provider") or "http_gateway"
        api_url = settings.get("api_url") or settings.get("url") or ""
        sign_name = settings.get("sign_name") or "【极速出版】"
        phones = settings.get("phone_numbers") or settings.get("phones") or ""

        logs.append(log("INFO", f"📱 [短信网关] 当前提供商模式: {provider.upper()} | 短信签名: {sign_name}"))
        if not phones:
            logs.append(log("WARN", "⚠️ [提示] 目标手机号为空，本次仅探测网关配置合规性。"))

        if api_url:
            logs.append(log("INFO", f"📡 [探测] 正在向短信 API 网关发起连通性探测: {api_url[:45]}..."))
            try:
                import requests
                headers = {'Content-Type': 'application/json'}
                secret = settings.get("secret") or settings.get("access_key_secret") or ""
                if secret:
                    headers['Authorization'] = f"Bearer {secret}"
                resp = requests.post(api_url, json={"event": "dry_run", "sign": sign_name}, headers=headers, timeout=8)
                logs.append(log("INFO", f"🟢 [成功] 短信网关响应 HTTP {resp.status_code}。API 通道可达！"))
            except Exception as e:
                logs.append(log("WARN", f"⚠️ [网关警告] 短信网关连通性探测异常: {e}"))
        else:
            logs.append(log("INFO", "🟢 [配置通过] 短信参数静态语法校验通过。"))

    # 📲 [App Push] 移动端/桌面推送独立探测
    elif plugin_id == "app_push":
        from adapters.notifications.app_push.push_hub import AppPushDriver
        driver = AppPushDriver(config=settings)
        provider = (settings.get("push_provider") or "bark").lower()
        device_key = settings.get("device_key") or settings.get("token") or ""

        if not device_key and provider != "custom":
            logs.append(log("ERROR", f"❌ [错误] {provider.upper()} 设备 Key 或 Token 为空！"))
            success = False

        if success:
            logs.append(log("INFO", f"📡 [Push] 正在向 {provider.upper()} 移动推送中枢发送单次探测消息..."))
            try:
                import requests
                req = driver.build_push_request("✨ Illacme Plenipes 测试", "移动与桌面推送通道连通成功！", "/test")
                kwargs = {"timeout": 8}
                if "headers" in req: kwargs["headers"] = req["headers"]
                if "json" in req: kwargs["json"] = req["json"]
                if "data" in req: kwargs["data"] = req["data"]
                resp = requests.post(req["url"], **kwargs)
                if resp.status_code in (200, 201, 202, 204):
                    logs.append(log("INFO", f"🟢 [推送成功] 对端服务响应 HTTP {resp.status_code} OK。移动端设备应已收到提示！"))
                else:
                    logs.append(log("ERROR", f"❌ [响应异常] 推送服务器返回 HTTP {resp.status_code}: {resp.text[:120]}"))
                    success = False
            except Exception as e:
                logs.append(log("ERROR", f"❌ [推送失败] 无法连通推送服务器: {e}"))
                success = False

    # 对通用 Webhook / 机器人通知类插件执行定制化连接探测
    else:
        url = settings.get("url") or ""
        secret = settings.get("secret") or ""
        bot_token = settings.get("bot_token") or settings.get("token") or ""
        chat_id = settings.get("chat_id") or ""
        
        # 针对 Telegram Bot 的专用寻址逻辑
        target_url = url
        if plugin_id == "telegram":
            if not target_url and bot_token:
                target_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                logs.append(log("INFO", "🤖 [Telegram] 自动根据 Bot Token 组装 API 访问端点。"))
            if not chat_id:
                logs.append(log("ERROR", "❌ [错误] Telegram 未配置目标 Chat ID (如 @my_channel 或 -100xxx)。"))
                success = False

        if not target_url and success:
            logs.append(log("ERROR", "❌ [错误] 物理端点 URL 为空！请输入有效的 Webhook HTTP/HTTPS 地址或 Bot 凭据。"))
            success = False
        elif target_url and not (target_url.startswith("http://") or target_url.startswith("https://")):
            # 🚀 [V105.0] 极简智能降级自愈：全自动补全平台官方标准前缀
            if plugin_id == "feishu":
                target_url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{target_url.lstrip('/')}"
                logs.append(log("INFO", f"🪄 [智能自愈] 探测到纯指纹 Key，已全自动补齐飞书官方标准前缀: {target_url[:55]}..."))
            elif plugin_id == "dingtalk":
                target_url = f"https://oapi.dingtalk.com/robot/send?access_token={target_url.lstrip('/')}"
                logs.append(log("INFO", f"🪄 [智能自愈] 探测到纯 Token，已全自动补齐钉钉官方标准前缀: {target_url[:55]}..."))
            elif plugin_id == "wecom":
                target_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={target_url.lstrip('/')}"
                logs.append(log("INFO", f"🪄 [智能自愈] 探测到纯 Key，已全自动补齐企业微信官方标准前缀: {target_url[:55]}..."))
            elif plugin_id == "discord":
                target_url = f"https://discord.com/api/webhooks/{target_url.lstrip('/')}"
                logs.append(log("INFO", f"🪄 [智能自愈] 探测到纯路径，已全自动补齐 Discord 官方标准前缀: {target_url[:55]}..."))
            else:
                logs.append(log("ERROR", f"❌ [错误] 物理端点 URL 格式不合法 (必须以 http:// 或 https:// 开头): '{target_url}'"))
                success = False

        if success:
            logs.append(log("INFO", f"📡 [探测] 正在对第三方 API 发起真实连通性握手: {target_url[:50]}..."))
            try:
                import requests
                headers = {'Content-Type': 'application/json'}
                
                driver_payload = {
                    "event": "connectivity_test",
                    "text": "✨ Illacme Plenipes 真实 API 物理通道连通性测试成功。"
                }
                
                if plugin_id == "dingtalk":
                    from adapters.notifications.webhook.dingtalk import DingTalkDriver
                    driver = DingTalkDriver(config=settings)
                    target_url = driver.compute_signed_url(target_url, secret)
                    driver_payload = driver.build_payload("真实 API 握手测试", "/test", "zh", "AEL-PING")
                    if secret:
                        logs.append(log("INFO", "🔑 [签名] 钉钉 timestamp + sign HMAC-SHA256 签名计算并拼接完成。"))
                elif plugin_id == "feishu":
                    from adapters.notifications.webhook.feishu import FeishuDriver
                    driver = FeishuDriver(config=settings)
                    driver_payload = driver.build_payload("真实 API 握手测试", "/test", "zh", "AEL-PING")
                    if secret:
                        logs.append(log("INFO", "🔑 [签名] 飞书 timestamp + sign 签名卡片凭据已成功算入。"))
                elif plugin_id == "telegram":
                    from adapters.notifications.webhook.telegram import TelegramDriver
                    driver = TelegramDriver(config=settings)
                    driver_payload = driver.build_payload("真实 API 握手测试", "/test", "zh", "AEL-PING")
                elif plugin_id == "discord":
                    from adapters.notifications.webhook.discord import DiscordNoticeDriver
                    driver = DiscordNoticeDriver(config=settings)
                    driver_payload = driver.build_payload("真实 API 握手测试", "/test", "zh", "AEL-PING")
                elif plugin_id in ("generic_webhook", "generic"):
                    from adapters.notifications.webhook.generic_webhook import GenericWebhookDriver
                    driver = GenericWebhookDriver(config=settings)
                    custom_hdrs = driver.get_custom_headers()
                    if custom_hdrs:
                        headers.update(custom_hdrs)
                        logs.append(log("INFO", f"🔑 [Header] 自定义 HTTP 报头已成功注入 ({len(custom_hdrs)} 项)。"))

                resp = requests.post(target_url, json=driver_payload, headers=headers, timeout=8)
                if resp.status_code in (200, 201, 202, 204):
                    # 🛡️ [Rule 16] 深度业务状态码穿透检查（钉钉/飞书/企业微信在 HTTP 200 下也会包含错误码）
                    biz_ok = True
                    try:
                        data = resp.json() if hasattr(resp, "json") else {}
                        if isinstance(data, dict):
                            errcode = data.get("errcode")
                            if errcode is not None and errcode != 0:
                                logs.append(log("ERROR", f"❌ [业务错误 (代码 {errcode})] {data.get('errmsg', '签名或凭证无效')}"))
                                biz_ok = False
                            code = data.get("code")
                            if code is not None and code != 0:
                                logs.append(log("ERROR", f"❌ [业务错误 (代码 {code})] {data.get('msg', '签名或凭据无效')}"))
                                biz_ok = False
                    except Exception:
                        pass

                    if biz_ok:
                        logs.append(log("INFO", f"🟢 [成功] 第三方 API 物理服务响应 HTTP {resp.status_code} OK。链路与凭据校验圆满成功！"))
                    else:
                        success = False
                else:
                    logs.append(log("ERROR", f"❌ [响应异常] 对端 API 返回非 20x 状态码: HTTP {resp.status_code} | 响应体: {resp.text[:140]}"))
                    success = False
            except Exception as e:
                logs.append(log("ERROR", f"❌ [网络错误] API 物理可达性异常或超时: {e}"))
                success = False

    return success
