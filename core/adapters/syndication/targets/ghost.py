#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ghost Syndicator
模块职责：负责将内容分发至 Ghost CMS 平台。
🛡️ [AEL-Iter-v5.3]：全自治插件实现。
"""
import json
import logging
import requests
from datetime import datetime
from ..base import BaseSyndicator

logger = logging.getLogger("Illacme.plenipes")

try:
    import jwt
    HAS_JWT = True
except ImportError:
    HAS_JWT = False

class GhostSyndicator(BaseSyndicator):
    def format_payload(self, title, body, tags, url, desc=""):
        mobiledoc = json.dumps({
            "version": "0.3.1",
            "markups": [], "atoms": [], "sections": [[10, 0]],
            "cards": [["markdown", {"cardName": "markdown", "markdown": body}]]
        })
        return {
            "posts": [{
                "title": title,
                "status": "draft",
                "mobiledoc": mobiledoc,
                "tags": [{"name": t} for t in tags],
                "canonical_url": url
            }]
        }

    def push(self, payload: dict):
        if not self.is_enabled() or not self.config.url or not self.config.admin_api_key:
            return
        if not HAS_JWT:
            logger.error("🛑 [Ghost 分发拦截] 缺少 PyJWT 依赖。")
            return
            
        try:
            api_key = self.config.admin_api_key
            key_id, secret = api_key.split(':')
            iat = int(datetime.now().timestamp())
            header = {'alg': 'HS256', 'typ': 'JWT', 'kid': key_id}
            jwt_payload = {'iat': iat, 'exp': iat + 5 * 60, 'aud': '/admin/'}
            token = jwt.encode(jwt_payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
            
            url = f"{self.config.url.rstrip('/')}/ghost/api/admin/posts/"
            headers = {"Authorization": f"Ghost {token}", "Content-Type": "application/json"}
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code == 201:
                logger.info("🚀 [Ghost 分发成功] 文章已落入草稿箱！")
            else:
                logger.warning(f"⚠️ [Ghost 分发异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"🛑 [Ghost 投递失败]: {e}")
