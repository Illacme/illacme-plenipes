import time
import hmac
import hashlib
import urllib.parse
from core.adapters.egress.webhook.base import BaseWebhookDriver

class DingTalkDriver(BaseWebhookDriver):
    DISPLAY_NAME = "钉钉 Notice 适配器"
    VERSION = "V1.0"
    DESCRIPTION = "自动构造钉钉 Markdown 消息卡片，支持加签验证与指定 @提醒。"

    def match(self, url: str) -> bool:
        return 'dingtalk.com' in url or 'oapi.dingtalk.com' in url

    def compute_signed_url(self, url: str, secret: str) -> str:
        if not secret:
            return url
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        import base64
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}timestamp={timestamp}&sign={sign}"

    def build_payload(self, title: str, url_path: str, lang_code: str, ael_tag: str) -> dict:
        at_mobiles_str = self.config.get("at_mobiles") or ""
        is_at_all = bool(self.config.get("is_at_all", False))

        mobiles = [m.strip() for m in at_mobiles_str.split(",") if m.strip()] if isinstance(at_mobiles_str, str) else []

        return {
            "msgtype": "markdown",
            "markdown": {
                "title": f"Illacme 同步就绪: {title}",
                "text": f"### ✨ Illacme 引擎编译就绪\n- **标题**: {title}\n- **语种**: {lang_code.upper()}\n- **路由**: {url_path}\n- **溯源 ID**: `{ael_tag}`\n> ⚡️ 状态: SSG 增量更新已触发。"
            },
            "at": {
                "atMobiles": mobiles,
                "isAtAll": is_at_all
            }
        }
