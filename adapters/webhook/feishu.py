from core.adapters.egress.webhook.base import BaseWebhookDriver
class FeishuDriver(BaseWebhookDriver):
    def match(self, url): return 'feishu.cn' in url
    def build_payload(self, title, url_path, lang_code, ael_tag):
        return {
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
