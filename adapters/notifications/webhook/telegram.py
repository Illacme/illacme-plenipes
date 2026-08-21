from core.adapters.egress.webhook.base import BaseWebhookDriver

class TelegramDriver(BaseWebhookDriver):
    DISPLAY_NAME = "Telegram 运维事件通知"
    VERSION = "V1.0"
    DESCRIPTION = "面向站长与运维的系统监控通道：利用 Telegram Bot API 实时接收全站编译就绪、AI 算力熔断等系统事件推送。"

    def match(self, url: str) -> bool:
        return 'api.telegram.org' in url or not url

    def build_payload(self, title: str, url_path: str, lang_code: str, ael_tag: str) -> dict:
        chat_id = self.config.get("chat_id") or ""
        parse_mode = self.config.get("parse_mode") or "HTML"
        thread_id = self.config.get("message_thread_id") or None

        payload = {
            "chat_id": chat_id,
            "text": f"✨ <b>Illacme 同步就绪</b>\n\n📚 <b>标题</b>: {title}\n🌐 <b>语种</b>: {lang_code.upper()}\n🔗 <b>路由</b>: {url_path}\n🧬 <b>溯源 ID</b>: <code>{ael_tag}</code>",
            "parse_mode": parse_mode
        }
        if thread_id:
            try:
                payload["message_thread_id"] = int(thread_id)
            except ValueError:
                pass
        return payload
