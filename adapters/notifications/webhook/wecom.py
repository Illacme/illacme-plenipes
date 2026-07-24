from core.adapters.egress.webhook.base import BaseWebhookDriver

class WeComDriver(BaseWebhookDriver):
    DISPLAY_NAME = "企业微信 Notice 适配器"
    VERSION = "V1.0"
    DESCRIPTION = "对接企业微信群机器人，提供高颜值出版告警与状态提醒卡片。"

    def match(self, url): return 'qyapi.weixin.qq.com' in url
    def build_payload(self, title, url_path, lang_code, ael_tag):
        return {
            "msgtype": "markdown",
            "markdown": {
                "content": f"✨ <font color=\"info\">Illacme 引擎编译就绪</font>\n> **标题**: {title}\n> **语种**: {lang_code.upper()}\n> **预测路由**: {url_path}\n> **溯源 ID**: `<font color=\"comment\">{ael_tag}</font>`"
            }
        }
