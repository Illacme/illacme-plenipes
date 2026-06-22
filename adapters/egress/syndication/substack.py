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

        try:
            resp = requests.post(api_url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code in [200, 201]:
                tlog.info(f"🚀 [Substack 分发成功] 成功同步草稿至子域名 '{subdomain}'。")
            else:
                tlog.warning(f"⚠️ [Substack 异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e:
            tlog.error(f"🛑 [Substack 失败]: {e}")
