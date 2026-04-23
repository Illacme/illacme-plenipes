#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Medium Syndicator
模块职责：负责将内容分发至 Medium 平台。
🛡️ [AEL-Iter-v5.3]：全自治插件实现。
"""
import logging
import requests
from ..base import BaseSyndicator

logger = logging.getLogger("Illacme.plenipes")

class MediumSyndicator(BaseSyndicator):
    def format_payload(self, title, body, tags, url, desc=""):
        return {
            "title": title,
            "contentFormat": "markdown",
            "content": body,
            "tags": tags[:5],
            "publishStatus": "draft",
            "canonicalUrl": url
        }

    def push(self, payload: dict):
        if not self.is_enabled() or not self.config.token or not self.config.author_id:
            return
        url = f"https://api.medium.com/v1/users/{self.config.author_id}/posts"
        headers = {"Authorization": f"Bearer {self.config.token}", "Content-Type": "application/json"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code in [200, 201]:
                logger.info(f"🚀 [Medium 分发成功] 预览: {resp.json().get('data', {}).get('url')}")
            else:
                logger.warning(f"⚠️ [Medium 异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"🛑 [Medium 失败]: {e}")
