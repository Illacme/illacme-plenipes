# -*- coding: utf-8 -*-
"""
📲 移动端与桌面极速推送适配器驱动
支持 Bark (iOS 极速推送)、Gotify (自建推送服务器)、Server酱 (微信消息推送) 与 Pushover。
"""
from typing import Dict, Any
import requests
from core.adapters.egress.webhook.base import BaseWebhookDriver

class AppPushDriver(BaseWebhookDriver):
    PLUGIN_ID = "app_push"
    ALIASES = ["bark", "gotify", "serverchan", "pushover", "mobile_push"]
    DISPLAY_NAME = "📲 移动与桌面推送中枢"
    VERSION = "V1.0"
    DESCRIPTION = "支持 Bark (iOS)、Gotify (私有化)、Server酱 (微信通知) 与 Pushover 极速推送。"

    def match(self, url: str) -> bool:
        return any(k in url.lower() for k in ["bark", "gotify", "sctapi", "ftqq", "pushover", "push"])

    def build_push_request(self, title: str, body: str, url_path: str = "") -> Dict[str, Any]:
        provider = (self.config.get("push_provider") or "bark").lower()
        device_key = self.config.get("device_key") or self.config.get("token") or self.config.get("key") or ""
        server_url = self.config.get("server_url") or ""
        sound = self.config.get("sound") or "glass"
        group = self.config.get("group") or "Illacme-Plenipes"

        if provider == "bark":
            base = server_url.rstrip('/') if server_url else "https://api.day.app"
            target_url = f"{base}/{device_key}" if device_key else base
            payload = {
                "title": title,
                "body": body,
                "sound": sound,
                "group": group,
                "url": url_path
            }
            return {"url": target_url, "json": payload, "headers": {'Content-Type': 'application/json'}}

        elif provider in ("serverchan", "server_chan", "wechat"):
            target_url = f"https://sctapi.ftqq.com/{device_key}.send"
            payload = {
                "title": title,
                "desp": f"{body}\n\n[点击查看出版文档]({url_path})" if url_path else body
            }
            return {"url": target_url, "data": payload, "headers": {}}

        elif provider == "gotify":
            base = server_url.rstrip('/') if server_url else "http://localhost:80"
            target_url = f"{base}/message?token={device_key}"
            payload = {
                "title": title,
                "message": f"{body} ({url_path})",
                "priority": 5
            }
            return {"url": target_url, "json": payload, "headers": {'Content-Type': 'application/json'}}

        elif provider == "pushover":
            target_url = "https://api.pushover.net/1/messages.json"
            app_token = self.config.get("app_token") or ""
            payload = {
                "token": app_token,
                "user": device_key,
                "title": title,
                "message": body,
                "url": url_path,
                "sound": sound
            }
            return {"url": target_url, "data": payload, "headers": {}}

        # 自定义通用 Push 终端
        target_url = server_url or f"https://api.day.app/{device_key}"
        return {"url": target_url, "json": {"title": title, "body": body, "url": url_path}, "headers": {'Content-Type': 'application/json'}}

    def build_payload(self, title: str, url_path: str, lang_code: str, ael_tag: str) -> Dict[str, Any]:
        return {
            "title": f"📚 文章出版完成 ({lang_code.upper()})",
            "body": f"《{title}》已成功生成并分发上线。\nAEL 溯源: {ael_tag}",
            "url_path": url_path,
            "lang": lang_code
        }

    def push(self, title: str, body: str, url_path: str = "") -> bool:
        req = self.build_push_request(title, body, url_path)
        if not req.get("url"):
            raise ValueError("推送目标 URL 或设备 Key 未配置。")
        kwargs = {"timeout": 8}
        if "headers" in req: kwargs["headers"] = req["headers"]
        if "json" in req: kwargs["json"] = req["json"]
        if "data" in req: kwargs["data"] = req["data"]
        
        resp = requests.post(req["url"], **kwargs)
        resp.raise_for_status()
        return True
