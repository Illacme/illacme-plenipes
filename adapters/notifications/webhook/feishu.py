import time
import hmac
import hashlib
import base64
from core.adapters.egress.webhook.base import BaseWebhookDriver

class FeishuDriver(BaseWebhookDriver):
    DISPLAY_NAME = "飞书 Notice 适配器"
    VERSION = "V1.0"
    DESCRIPTION = "自动构造飞书 Post/Interactive 富文本卡片，支持签名校验密钥。"

    def match(self, url: str) -> bool:
        return 'feishu.cn' in url or 'larksuite.com' in url

    def build_payload(self, title: str, url_path: str, lang_code: str, ael_tag: str) -> dict:
        secret = self.config.get("secret") or ""
        msg_type = self.config.get("msg_type") or "post"

        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "✨ Illacme 引擎：新文章编译就绪",
                        "content": [
                            [{"tag": "text", "text": f"📚 标题: {title}"}],
                            [{"tag": "text", "text": f"🌐 语种: {lang_code.upper()}"}],
                            [{"tag": "text", "text": f"🔗 预测路由: {url_path}"}],
                            [{"tag": "text", "text": f"🧬 溯源 ID: {ael_tag}"}]
                        ]
                    }
                }
            }
        }

        if secret:
            timestamp = str(int(time.time()))
            string_to_sign = f"{timestamp}\n{secret}"
            hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
            sign = base64.b64encode(hmac_code).decode("utf-8")
            payload["timestamp"] = timestamp
            payload["sign"] = sign

        return payload
