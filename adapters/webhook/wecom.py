from core.adapters.egress.webhook.base import BaseWebhookDriver
class WeComDriver(BaseWebhookDriver):
    def match(self, url): return 'qyapi.weixin.qq.com' in url
    def build_payload(self, title, url_path, lang_code, ael_tag):
        return {
            "msgtype": "markdown",
            "markdown": {
                "content": f"### ✨ Illacme 引擎编译就绪\n> **标题**: {title}\n> **语种**: {lang_code.upper()}\n> **路由**: {url_path}\n> **溯源 ID**: `{ael_tag}`\n> ⚡️ 状态: SSG 增量更新已触发。"
            }
        }
