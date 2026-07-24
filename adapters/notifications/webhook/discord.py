from core.adapters.egress.webhook.base import BaseWebhookDriver

class DiscordNoticeDriver(BaseWebhookDriver):
    DISPLAY_NAME = "Discord Notice 适配器"
    VERSION = "V1.0"
    DESCRIPTION = "对接 Discord 频道 Webhook，支持富文本 Embeds 卡片及 Bot 属性自定义 Override。"

    def match(self, url: str) -> bool:
        return 'discord.com/api/webhooks' in url or 'discordapp.com/api/webhooks' in url

    def build_payload(self, title: str, url_path: str, lang_code: str, ael_tag: str) -> dict:
        username = self.config.get("username")
        avatar_url = self.config.get("avatar_url")

        payload = {
            "embeds": [
                {
                    "title": f"✨ Illacme 同步就绪: {title}",
                    "color": 65534,
                    "fields": [
                        {"name": "📚 标题", "value": title, "inline": True},
                        {"name": "🌐 语种", "value": lang_code.upper(), "inline": True},
                        {"name": "🔗 预测路由", "value": url_path, "inline": False},
                        {"name": "🧬 溯源 ID", "value": f"`{ael_tag}`", "inline": True}
                    ],
                    "footer": {"text": "⚡️ 状态: SSG 增量更新已触发。"}
                }
            ]
        }
        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url

        return payload
