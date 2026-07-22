#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Telegram Channel Syndicator
模块职责：通过 Telegram Bot API 将新发布文章以卡片消息形式推送至指定 Channel/Group。
"""

import requests
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


import threading

# 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
_last_telegram_time = 0.0
_telegram_lock = threading.Lock()

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
        import time
        import random

        bot_token = getattr(self.config, 'bot_token', None) or self.config.get('bot_token')
        chat_id = payload.get("chat_id")

        if not bot_token:
            tlog.warning("⚠️ [Telegram 推送] 缺少 bot_token 配置，分发跳过。")
            return
        if not chat_id:
            tlog.warning("⚠️ [Telegram 推送] 缺少 chat_id 配置，分发跳过。")
            return

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        # 🛡️ 1. 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上 (加上线程锁防止竞态穿透)
        global _last_telegram_time
        with _telegram_lock:
            while True:
                elapsed = time.time() - _last_telegram_time
                if elapsed < 1.5:
                    time.sleep(1.5 - elapsed)
                else:
                    break

            _last_telegram_time = time.time()

        # 🛡️ 2. 指数退避重试循环 (对冲 429 频控，且兼容 Telegram 的 retry_after 指示)
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=self.timeout)
                _last_telegram_time = time.time()

                if resp.status_code == 429:
                    # 探测对端 retry_after 指示
                    retry_sec = 3.0 * (2 ** attempt)
                    try:
                        retry_after_val = resp.json().get("parameters", {}).get("retry_after")
                        if retry_after_val:
                            retry_sec = float(retry_after_val) + random.uniform(0.1, 0.5)
                    except Exception:
                        pass

                    if attempt < max_attempts - 1:
                        tlog.warning(f"⚠️ [Telegram Rate Limit] 触发频控，休眠 {retry_sec:.2f} 秒后重试...")
                        time.sleep(retry_sec)
                        continue
                    else:
                        raise RuntimeError(f"对端 Telegram 频控限制 (429 Too Many Requests)，需等待超过 {retry_sec:.1f} 秒。")

                if resp.status_code == 200:
                    tlog.info(f"🚀 [Telegram 推送成功] 消息已发送至频道 '{chat_id}'。")
                    return {"success": True}
                elif resp.status_code in (401, 403):
                    raise RuntimeError("Telegram 推送失败：Bot Token 无效，或该 Bot 没有被加入此频道且赋予管理员发布消息权限。")
                else:
                    raise RuntimeError(f"Telegram API 报错 ({resp.status_code}): {resp.text}")

            except requests.RequestException as req_err:
                if attempt < max_attempts - 1:
                    sleep_time = 2.0 + random.uniform(0.1, 0.5)
                    time.sleep(sleep_time)
                    continue
                else:
                    tlog.error(f"🛑 [Telegram 推送] 网络请求失败: {req_err}")
                    raise RuntimeError(f"Telegram 网络请求失败: {req_err}") from req_err
            except Exception as e:
                tlog.error(f"🛑 [Telegram 推送失败]: {e}")
                raise e
