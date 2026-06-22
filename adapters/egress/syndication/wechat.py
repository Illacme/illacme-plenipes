#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - WeChat Official Account Syndicator
模块职责：负责将稿件作为草稿同步分发至微信公众号平台。
"""

import requests
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


class WeChatSyndicator(BaseSyndicator):
    PLUGIN_ID = "wechat"
    DISPLAY_NAME = "微信公众号"
    VERSION = "V1.0"
    DESCRIPTION = "将文章作为草稿同步至微信公众号素材库，支持自动授权与原文链接回溯。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        # 提取摘要
        digest = metadata.get("description") or metadata.get("digest") or (content[:120] + "...")
        author = metadata.get("author") or "Plenipes Bot"

        # 微信公众号要求图片封面 thumb_media_id 字段。此处测试时提供占位符，若有需要用户可在微信后台替换
        thumb_media_id = metadata.get("wechat_thumb_media_id") or "media_id_placeholder"

        return {
            "articles": [
                {
                    "title": title,
                    "author": author,
                    "digest": digest,
                    "content": content,  # 支持富文本 HTML 排版
                    "content_source_url": canonical_url,
                    "thumb_media_id": thumb_media_id,
                    "need_open_comment": 1,
                    "only_fans_can_comment": 0
                }
            ]
        }

    def push(self, payload: dict):
        app_id = getattr(self.config, 'app_id', None) or self.config.get('app_id')
        app_secret = getattr(self.config, 'app_secret', None) or self.config.get('app_secret')

        if not app_id or not app_secret:
            tlog.warning("⚠️ [微信公众号] 缺少 app_id 或 app_secret 配置，分发跳过。")
            return

        try:
            # ── 1. 获取全局 Access Token ──────────────────
            token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
            token_resp = requests.get(token_url, timeout=self.timeout)
            if token_resp.status_code != 200:
                tlog.error(f"❌ [微信公众号] 获取 Access Token 失败，HTTP 状态码: {token_resp.status_code}")
                return

            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                tlog.error(f"❌ [微信公众号] 获取 Access Token 接口返回异常: {token_data}")
                return

            # ── 2. 将图文推送至草稿箱 ────────────────────
            draft_url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
            resp = requests.post(draft_url, json=payload, headers={"Content-Type": "application/json"}, timeout=self.timeout)
            
            if resp.status_code == 200:
                resp_data = resp.json()
                if "media_id" in resp_data:
                    tlog.info(f"🚀 [微信公众号分发成功] 草稿 Media ID: {resp_data.get('media_id')}")
                else:
                    tlog.warning(f"⚠️ [微信公众号异常] 接口返回非预期结果: {resp_data}")
            else:
                tlog.warning(f"⚠️ [微信公众号异常] 状态码 {resp.status_code}: {resp.text}")

        except Exception as e:
            tlog.error(f"🛑 [微信公众号分发失败]: {e}")
