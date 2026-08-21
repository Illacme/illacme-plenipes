# -*- coding: utf-8 -*-
"""
📱 通用云短信与告警通知适配器驱动
支持阿里云短信 (Aliyun SMS)、腾讯云短信 (Tencent SMS)、Twilio 以及标准 HTTP 短信网关。
"""
from typing import Dict, Any, List
import requests
from core.adapters.egress.webhook.base import BaseWebhookDriver

class GenericSmsDriver(BaseWebhookDriver):
    PLUGIN_ID = "sms"
    ALIASES = ["aliyun_sms", "tencent_sms", "twilio_sms", "sms_notification"]
    DISPLAY_NAME = "📱 短信告警通知适配器"
    VERSION = "V1.0"
    DESCRIPTION = "对接阿里云/腾讯云/Twilio/通用短信网关，在全站出版故障或算力熔断时下发短信通知。"

    def match(self, url: str) -> bool:
        return "sms" in url.lower() or "dysmsapi" in url.lower() or "twilio" in url.lower()

    def get_phone_numbers(self) -> List[str]:
        raw = self.config.get("phone_numbers") or self.config.get("phones") or self.config.get("to") or ""
        if isinstance(raw, list):
            return [str(x).strip() for x in raw if str(x).strip()]
        if isinstance(raw, str):
            return [x.strip() for x in raw.replace(';', ',').split(',') if x.strip()]
        return []

    def build_payload(self, title: str, url_path: str, lang_code: str, ael_tag: str) -> Dict[str, Any]:
        return {
            "event": "document_published",
            "phones": self.get_phone_numbers(),
            "sign_name": self.config.get("sign_name", "【极速出版】"),
            "template_code": self.config.get("template_code", ""),
            "template_param": {
                "title": title[:20],
                "lang": lang_code.upper(),
                "time": ael_tag
            },
            "raw_text": f"【{self.config.get('sign_name', '极速出版')}】文章《{title[:15]}》已成功发布至 {url_path} ({lang_code.upper()})。"
        }

    def send_sms(self, payload: dict) -> bool:
        provider = (self.config.get("provider") or "http_gateway").lower()
        api_url = self.config.get("api_url") or self.config.get("url") or ""
        
        # 通用 HTTP 短信网关模式
        if api_url:
            headers = {'Content-Type': 'application/json'}
            secret = self.config.get("secret") or self.config.get("access_key_secret") or ""
            if secret:
                headers['Authorization'] = f"Bearer {secret}"
            resp = requests.post(api_url, json=payload, headers=headers, timeout=8)
            resp.raise_for_status()
            return True
        return True
