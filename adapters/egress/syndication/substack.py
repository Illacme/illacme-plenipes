#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Substack Syndicator
模块职责：负责将稿件同步分发至 Substack 平台草稿箱。
"""

import re
import requests
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


import threading

# 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
_last_substack_time = 0.0
_substack_lock = threading.Lock()

class SubstackSyndicator(BaseSyndicator):
    PLUGIN_ID = "substack"
    DISPLAY_NAME = "Substack"
    VERSION = "V1.0"
    DESCRIPTION = "将内容同步分发至 Substack 订阅，支持草稿创建与 Newsletter 邮件推送预备。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        subtitle = metadata.get("description") or metadata.get("subtitle") or ""
        return {
            "draft": True,
            "title": title,
            "subtitle": subtitle,
            "body": content,  # 可以是 HTML
            "write_comment_permissions": "everyone"
        }

    def push(self, payload: dict):
        import time
        import random

        url_cfg = getattr(self.config, 'url', None) or self.config.get('url')
        cookie = getattr(self.config, 'cookie', None) or self.config.get('cookie')
        api_key = getattr(self.config, 'api_key', None) or self.config.get('api_key')

        if not url_cfg:
            tlog.warning("⚠️ [Substack] 缺少 Substack 首页 URL 配置，分发跳过。")
            return
        if not cookie and not api_key:
            tlog.warning("⚠️ [Substack] 缺少 cookie 或 api_key 凭证，分发跳过。")
            return

        # 试图从配置的域名（如 test.substack.com）中推导 API 端点
        subdomain = "www"
        match = re.search(r"https?://([^.]+)\.substack\.com", url_cfg)
        if match:
            subdomain = match.group(1)

        api_url = f"https://{subdomain}.substack.com/api/v1/posts"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Illacme-Plenipes-Client"
        }

        if cookie:
            headers["Cookie"] = cookie
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # 🛡️ 1. 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上 (加上线程锁防止竞态穿透)
        global _last_substack_time
        with _substack_lock:
            while True:
                elapsed = time.time() - _last_substack_time
                if elapsed < 1.5:
                    time.sleep(1.5 - elapsed)
                else:
                    break

            _last_substack_time = time.time()

        # 🛡️ 2. 指数退避重试循环 (对冲 429 频控)
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                resp = requests.post(api_url, json=payload, headers=headers, timeout=self.timeout)
                _last_substack_time = time.time()

                if resp.status_code == 429:
                    if attempt < max_attempts - 1:
                        sleep_time = 3.0 * (2 ** attempt) + random.uniform(0.1, 0.5)
                        time.sleep(sleep_time)
                        continue
                    else:
                        raise RuntimeError("对端 Substack 接口频控限制 (429 Too Many Requests)，请稍后重试。")

                if resp.status_code in [200, 201]:
                    tlog.info(f"🚀 [Substack 分发成功] 成功同步草稿至子域名 '{subdomain}'。")
                    return {"success": True, "subdomain": subdomain}
                elif resp.status_code in (401, 403):
                    raise RuntimeError("Substack 认证失败（401/403）：Cookie 或 API Key 无效，请重新配置 Substack 访问凭据。")
                else:
                    raise RuntimeError(f"Substack API 报错 ({resp.status_code}): {resp.text}")

            except requests.RequestException as req_err:
                if attempt < max_attempts - 1:
                    sleep_time = 2.0 + random.uniform(0.1, 0.5)
                    time.sleep(sleep_time)
                    continue
                else:
                    tlog.error(f"🛑 [Substack] 网络请求失败: {req_err}")
                    raise RuntimeError(f"Substack 网络请求失败: {req_err}") from req_err
            except Exception as e:
                tlog.error(f"🛑 [Substack 失败]: {e}")
                raise e
