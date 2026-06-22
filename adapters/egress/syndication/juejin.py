#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Juejin Syndicator
模块职责：负责将稿件同步分发至稀土掘金平台草稿箱。
"""

import requests
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


class JuejinSyndicator(BaseSyndicator):
    PLUGIN_ID = "juejin"
    DISPLAY_NAME = "稀土掘金"
    VERSION = "V1.0"
    DESCRIPTION = "将文章同步保存至稀土掘金的草稿箱，支持 Cookie 或 API Token 验证。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        digest = metadata.get("description") or metadata.get("digest") or (content[:100] + "...")
        return {
            "title": title,
            "brief_content": digest,
            "mark_content": content,  # Markdown 源码内容
            "category_id": metadata.get("juejin_category_id") or "6809637767543259144",  # 默认分类：后端/开发
            "tag_ids": metadata.get("juejin_tag_ids") or [],
            "html_content": ""
        }

    def push(self, payload: dict):
        cookie = getattr(self.config, 'cookie', None) or self.config.get('cookie')
        api_token = getattr(self.config, 'api_token', None) or self.config.get('api_token')

        if not cookie and not api_token:
            tlog.warning("⚠️ [稀土掘金] 缺少 cookie 或 api_token 凭据，分发跳过。")
            return

        url = "https://api.juejin.cn/content_api/v1/article_draft/create"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        if cookie:
            headers["Cookie"] = cookie
        if api_token:
            headers["X-Juejin-Token"] = api_token

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code == 200:
                resp_data = resp.json()
                if resp_data.get("err_no") == 0:
                    tlog.info(f"🚀 [稀土掘金分发成功] 成功保存草稿，Draft ID: {resp_data.get('data', {}).get('draft_id')}")
                else:
                    tlog.warning(f"⚠️ [稀土掘金异常] 返回错误码 {resp_data.get('err_no')}: {resp_data.get('err_msg')}")
            else:
                tlog.warning(f"⚠️ [稀土掘金异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e:
            tlog.error(f"🛑 [稀土掘金失败]: {e}")
