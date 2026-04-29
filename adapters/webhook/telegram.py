from core.adapters.egress.webhook.base import BaseWebhookDriver
class TelegramDriver(BaseWebhookDriver):
    def match(self, url): return 'api.telegram.org' in url
    def build_payload(self, title, url_path, lang_code, ael_tag):
        return {
            "text": f"✨ <b>Illacme 同步就绪</b>\n\n📚 <b>标题</b>: {title}\n🌐 <b>语种</b>: {lang_code.upper()}\n🔗 <b>路由</b>: {url_path}\n🧬 <b>溯源 ID</b>: <code>{ael_tag}</code>",
            "parse_mode": "HTML"
        }
