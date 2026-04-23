#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Hashnode Syndicator
模块职责：负责将内容分发至 Hashnode 平台。
🛡️ [AEL-Iter-v5.3]：全自治插件实现。
"""
import logging
import requests
from ..base import BaseSyndicator

logger = logging.getLogger("Illacme.plenipes")

class HashnodeSyndicator(BaseSyndicator):
    def format_payload(self, title, body, tags, url, desc=""):
        query = "mutation PublishPost($input: PublishPostInput!) { publishPost(input: $input) { post { url } } }"
        return {
            "query": query,
            "variables": {
                "input": {
                    "title": title,
                    "contentMarkdown": body,
                    "publicationId": self.config.publication_id,
                    "originalArticleUrl": url
                }
            }
        }

    def push(self, payload: dict):
        if not self.is_enabled() or not self.config.token or not self.config.publication_id:
            return
        url = "https://gql.hashnode.com/"
        headers = {"Authorization": self.config.token, "Content-Type": "application/json"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code == 200 and "errors" not in resp.json():
                logger.info("🚀 [Hashnode 分发成功] (请前往草稿箱查看)")
            else:
                logger.warning(f"⚠️ [Hashnode 异常]: {resp.text}")
        except Exception as e:
            logger.error(f"🛑 [Hashnode 失败]: {e}")
