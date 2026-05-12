from core.adapters.egress.webhook.base import BaseWebhookDriver
class GenericWebhookDriver(BaseWebhookDriver):
    def match(self, url): return True
    def build_payload(self, title, url_path, lang_code, ael_tag):
        return {
            "event": "document_published",
            "ael_iter_id": ael_tag,
            "data": {
                "title": title, "lang": lang_code, "url_path": url_path
            }
        }
