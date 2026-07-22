#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Discord Webhook Syndicator
模块职责：通过 Discord Webhook 向指定的 Discord 频道频道推送新文章卡片广播。
"""

import requests
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


import threading

# 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
_last_discord_time = 0.0
_discord_lock = threading.Lock()

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
        import time
        import random

        webhook_url = getattr(self.config, 'webhook_url', None) or self.config.get('webhook_url')

        if not webhook_url:
            tlog.warning("⚠️ [Discord 广播] 缺少 webhook_url 配置，分发跳过。")
            return

        if not (webhook_url.startswith("http://") or webhook_url.startswith("https://")):
            tlog.warning(f"⚠️ [Discord 广播] webhook_url 格式不合法: '{webhook_url}'")
            return

        # 🛡️ 1. 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上 (加上线程锁防止竞态穿透)
        global _last_discord_time
        with _discord_lock:
            while True:
                elapsed = time.time() - _last_discord_time
                if elapsed < 1.5:
                    time.sleep(1.5 - elapsed)
                else:
                    break

            _last_discord_time = time.time()

        # 🛡️ 2. 指数退避重试循环 (对冲 429 频控，且支持 Discord Webhook 特有的 retry_after 响应)
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                resp = requests.post(webhook_url, json=payload, headers={"Content-Type": "application/json"}, timeout=self.timeout)
                _last_discord_time = time.time()

                if resp.status_code == 429:
                    # 探测对端 retry_after 指示
                    retry_sec = 3.0 * (2 ** attempt)
                    try:
                        resp_json = resp.json()
                        # Discord Webhook 返回的 retry_after 有时是秒，有时是毫秒。若大于 100，通常认为是毫秒，自动除以 1000 换算
                        retry_after_val = resp_json.get("retry_after")
                        if retry_after_val:
                            val = float(retry_after_val)
                            if val > 100:
                                retry_sec = val / 1000.0 + random.uniform(0.1, 0.3)
                            else:
                                retry_sec = val + random.uniform(0.1, 0.3)
                    except Exception:
                        pass

                    if attempt < max_attempts - 1:
                        tlog.warning(f"⚠️ [Discord Rate Limit] 触发 Webhook 频控限制，休眠 {retry_sec:.2f} 秒后重试...")
                        time.sleep(retry_sec)
                        continue
                    else:
                        raise RuntimeError(f"对端 Discord Webhook 频控超限 (429 Too Many Requests)，需等待超过 {retry_sec:.1f} 秒。")

                if resp.status_code in [200, 204]:
                    tlog.info("🚀 [Discord 广播成功] Webhook 消息推送成功。")
                    return {"success": True}
                elif resp.status_code in (401, 403, 404):
                    raise RuntimeError(f"Discord 广播推送失败：Webhook URL 无效、已失效或频道不存在 (HTTP {resp.status_code})。")
                else:
                    raise RuntimeError(f"Discord Webhook API 报错 ({resp.status_code}): {resp.text}")

            except requests.RequestException as req_err:
                if attempt < max_attempts - 1:
                    sleep_time = 2.0 + random.uniform(0.1, 0.5)
                    time.sleep(sleep_time)
                    continue
                else:
                    tlog.error(f"🛑 [Discord 广播] 网络请求失败: {req_err}")
                    raise RuntimeError(f"Discord 网络请求失败: {req_err}") from req_err
            except Exception as e:
                tlog.error(f"🛑 [Discord 广播失败]: {e}")
                raise e
