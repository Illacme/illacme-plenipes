#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - WordPress Syndicator
模块职责：负责将内容分发至 WordPress 平台。
🛡️ [AEL-Iter-v5.3]：全自治插件实现。
"""
import logging
import requests
from requests.auth import HTTPBasicAuth
from ..base import BaseSyndicator

logger = logging.getLogger("Illacme.plenipes")

class WordPressSyndicator(BaseSyndicator):
    def format_payload(self, title, body, tags, url, desc=""):
        return {
            "title": title,
            "content": body,
            "status": "draft",
            "format": "standard"
        }

    def push(self, payload: dict):
        if not self.is_enabled() or not self.config.url or not self.config.username or not self.config.app_password:
            return
        endpoint = f"{self.config.url.rstrip('/')}/wp-json/wp/v2/posts"
        try:
            resp = requests.post(endpoint, json=payload, auth=HTTPBasicAuth(self.config.username, self.config.app_password), timeout=self.timeout)
            if resp.status_code == 201:
                logger.info(f"🚀 [WordPress 分发成功] 预览: {resp.json().get('link')}")
            else:
                logger.warning(f"⚠️ [WordPress 异常] {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"🛑 [WordPress 失败]: {e}")
