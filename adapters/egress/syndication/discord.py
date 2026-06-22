#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Discord Webhook Syndicator
模块职责：通过 Discord Webhook 向指定的 Discord 频道频道推送新文章卡片广播。
"""

import requests
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


class DiscordSyndicator(BaseSyndicator):
    PLUGIN_ID = "discord"
    DISPLAY_NAME = "Discord Webhook"
    VERSION = "V1.0"
    DESCRIPTION = "通过 Discord Webhook 安全可靠地向频道内推送带有图文排版、阅读链接的 Embed 富文本广播。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        digest = metadata.get("description") or metadata.get("digest") or (content[:150] + "...")

        # 构造符合 Discord 格式的 embeds 图文卡片
        return {
            "embeds": [
                {
                    "title": f"📝 新文章发布: {title}",
                    "description": digest,
                    "url": canonical_url,
                    "color": 3447003,  # Discord 经典皇家蓝 (HEX: #3498db)
                    "fields": [
                        {
                            "name": "🔗 永久标识符 (Slug)",
                            "value": f"`{slug}`",
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": "Illacme Plenipes Syndication Engine"
                    }
                }
            ]
        }

    def push(self, payload: dict):
        webhook_url = getattr(self.config, 'webhook_url', None) or self.config.get('webhook_url')

        if not webhook_url:
            tlog.warning("⚠️ [Discord 广播] 缺少 webhook_url 配置，分发跳过。")
            return

        if not (webhook_url.startswith("http://") or webhook_url.startswith("https://")):
            tlog.warning(f"⚠️ [Discord 广播] webhook_url 格式不合法: '{webhook_url}'")
            return

        try:
            resp = requests.post(webhook_url, json=payload, headers={"Content-Type": "application/json"}, timeout=self.timeout)
            if resp.status_code in [200, 204]:
                tlog.info("🚀 [Discord 广播成功] Webhook 消息推送成功。")
            else:
                tlog.warning(f"⚠️ [Discord 广播异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e:
            tlog.error(f"🛑 [Discord 广播失败]: {e}")
