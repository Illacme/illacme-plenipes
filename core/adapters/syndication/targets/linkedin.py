#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - LinkedIn Syndicator
模块职责：负责将内容分发至 LinkedIn 平台。
🛡️ [AEL-Iter-v5.3]：全自治插件实现。
"""
import logging
import requests
from ..base import BaseSyndicator

logger = logging.getLogger("Illacme.plenipes")

class LinkedInSyndicator(BaseSyndicator):
    def format_payload(self, title, body, tags, url, desc=""):
        return {
            "author": f"urn:li:person:{self.config.person_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": f"✨ 新技术文章发布：{title}\n\n{desc[:100]}...\n\n点击阅读全文 👇"},
                    "shareMediaCategory": "ARTICLE",
                    "media": [{
                        "status": "READY",
                        "originalUrl": url,
                        "title": {"text": title},
                        "description": {"text": desc[:100]}
                    }]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

    def push(self, payload: dict):
        if not self.is_enabled() or not self.config.access_token or not self.config.person_urn:
            return
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {"Authorization": f"Bearer {self.config.access_token}", "X-Restli-Protocol-Version": "2.0.0", "Content-Type": "application/json"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code == 201:
                logger.info("🚀 [LinkedIn 分发成功] 动态已发布至您的 LinkedIn 时间线！")
            else:
                logger.warning(f"⚠️ [LinkedIn 分发异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"🛑 [LinkedIn 投递失败]: {e}")
