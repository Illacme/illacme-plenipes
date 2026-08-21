import json
from core.adapters.egress.webhook.base import BaseWebhookDriver

class GenericWebhookDriver(BaseWebhookDriver):
    PLUGIN_ID = "generic_webhook"
    ALIASES = ["generic", "http_webhook", "custom_webhook"]
    DISPLAY_NAME = "通用 HTTP Webhook 适配器"
    VERSION = "V1.0"
    DESCRIPTION = "向任意自定义 HTTP API 发送 JSON 事件报文，支持自定义 Headers 与签名验证。"

    def match(self, url: str) -> bool:
        return True

    def get_custom_headers(self) -> dict:
        raw_headers = self.config.get("custom_headers") or ""
        if isinstance(raw_headers, dict):
            return raw_headers
        if isinstance(raw_headers, str) and raw_headers.strip():
            try:
                parsed = json.loads(raw_headers)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
        return {}

    def build_payload(self, title: str, url_path: str, lang_code: str, ael_tag: str) -> dict:
        return {
            "event": "document_published",
            "ael_iter_id": ael_tag,
            "data": {
                "title": title, "lang": lang_code, "url_path": url_path
            }
        }
