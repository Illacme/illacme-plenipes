#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Telegram Channel Syndicator
模块职责：通过 Telegram Bot API 将新发布文章以卡片消息形式推送至指定 Channel/Group。
"""

import requests
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


class TelegramSyndicator(BaseSyndicator):
    PLUGIN_ID = "telegram"
    DISPLAY_NAME = "Telegram Channel"
    VERSION = "V1.0"
    DESCRIPTION = "使用 Telegram Bot 将文章的标题、摘要与阅读全文链接自动推送至指定的 Telegram 频道或群组。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        digest = metadata.get("description") or metadata.get("digest") or ""
        if digest:
            digest = digest[:200] + "..." if len(digest) > 200 else digest
            digest = f"\n\n_{digest}_"

        # 构造 Markdown 格式的快讯卡片消息
        text = f"📢 *【文章发布推送】*\n\n*标题*: {title}{digest}\n\n🔗 [阅读全文]({canonical_url})"
        
        chat_id = getattr(self.config, 'chat_id', None) or self.config.get('chat_id')

        return {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }

    def push(self, payload: dict):
        bot_token = getattr(self.config, 'bot_token', None) or self.config.get('bot_token')
        chat_id = payload.get("chat_id")

        if not bot_token:
            tlog.warning("⚠️ [Telegram 推送] 缺少 bot_token 配置，分发跳过。")
            return
        if not chat_id:
            tlog.warning("⚠️ [Telegram 推送] 缺少 chat_id 配置，分发跳过。")
            return

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        try:
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=self.timeout)
            if resp.status_code == 200:
                tlog.info(f"🚀 [Telegram 推送成功] 消息已发送至频道 '{chat_id}'。")
            else:
                tlog.warning(f"⚠️ [Telegram 推送异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e:
            tlog.error(f"🛑 [Telegram 推送失败]: {e}")
