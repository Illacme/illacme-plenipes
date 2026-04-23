#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Dev.to Syndicator
模块职责：负责将内容分发至 Dev.to 平台。
🛡️ [AEL-Iter-v5.3]：全自治插件实现。
"""
import logging
import requests
from ..base import BaseSyndicator

logger = logging.getLogger("Illacme.plenipes")

class DevToSyndicator(BaseSyndicator):
    def format_payload(self, title, body, tags, url, desc=""):
        return {
            "article": {
                "title": title,
                "body_markdown": body,
                "published": False,
                "tags": tags[:4],
                "canonical_url": url
            }
        }

    def push(self, payload: dict):
        if not self.is_enabled() or not self.config.api_key:
            return
        url = "https://dev.to/api/articles"
        headers = {"api-key": self.config.api_key, "Content-Type": "application/json"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code == 201:
                logger.info(f"🚀 [Dev.to 分发成功] 预览: {resp.json().get('url')}")
            else:
                logger.warning(f"⚠️ [Dev.to 异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"🛑 [Dev.to 失败]: {e}")
