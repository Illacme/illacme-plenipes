#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — LinkedIn Syndicator Plugin
🚀 [V76.0]：对接 LinkedIn UGC Posts API v2，支持文章摘要与 Canonical 链接分享。

配置示例 (config.yaml):
  syndication:
    linkedin:
      enabled: true
      token: "your_oauth2_access_token"      # LinkedIn OAuth 2.0 Access Token（必填）
      person_urn: "urn:li:person:XXXXXX"     # 你的 LinkedIn Person URN（必填）
      # 或组织主页发布：
      # organization_urn: "urn:li:organization:XXXXXX"

注意：LinkedIn API 需要应用具有 w_member_social 权限范围（scope）。
      Access Token 的有效期通常为 60 天，需定期刷新。
"""

import requests
from typing import Dict, Any

from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

import threading

# 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
_last_linkedin_time = 0.0
_linkedin_lock = threading.Lock()

# ---------------------------------------------------------------------------
# LinkedIn API 端点
# ---------------------------------------------------------------------------
LINKEDIN_UGC_POSTS_URL = "https://api.linkedin.com/v2/ugcPosts"
LINKEDIN_API_VERSION_HEADER = "202304"  # LinkedIn API 版本标头


class LinkedInSyndicator(BaseSyndicator):
    """
    🚀 [V76.0] LinkedIn 职场社交平台分发插件
    通过 LinkedIn UGC Posts API v2 将文章摘要与链接分享至个人动态或组织主页。

    发布形式：外部文章链接分享（ARTICLE 类型），包含标题、摘要与 Canonical URL。
    """
    PLUGIN_ID = "linkedin"
    DISPLAY_NAME = "LinkedIn"
    VERSION = "V2.0"
    DESCRIPTION = "同步至 LinkedIn 职场社交平台，通过 UGC Posts API v2 将文章链接分享至个人动态，支持 Person/Organization 双模式。"

    REQUIRED_PACKAGES = ["requests"]

    def __init__(self, config: Any, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.token = getattr(config, "token", "")
        # 支持个人（person_urn）或组织主页（organization_urn）两种发布模式
        self.person_urn = getattr(config, "person_urn", "")
        self.organization_urn = getattr(config, "organization_urn", "")
        # 帖子可见性：PUBLIC 或 CONNECTIONS
        self.visibility = getattr(config, "visibility", "PUBLIC")

    # ------------------------------------------------------------------
    # BaseSyndicator 契约实现
    # ------------------------------------------------------------------

    def format_payload(self, title: str, slug: str, content: str, metadata: Dict[str, Any], canonical_url: str = None) -> Dict[str, Any]:
        """
        组装 LinkedIn UGC Post 数据结构（ARTICLE 类型分享）。
        文档：https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
        """
        # 确定发布者 URN（个人优先，其次组织）
        author_urn = self.person_urn or self.organization_urn
        if not author_urn:
            author_urn = "urn:li:person:unknown"

        # Canonical 文章 URL，优先使用传入值，否则 Fallback 推导
        article_url = canonical_url
        if not article_url and self.site_url:
            article_url = f"{self.site_url.rstrip('/')}/{slug}"

        # 摘要：取 metadata description，或截取正文前 200 字
        description = metadata.get("description", "")
        if not description and content:
            # 去掉 Markdown 标记后截取
            plain = content.replace("#", "").replace("*", "").replace("`", "").strip()
            description = plain[:200].rstrip() + ("..." if len(plain) > 200 else "")

        payload: Dict[str, Any] = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": f"{title}\n\n{description}"
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [],
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": self.visibility
            },
        }

        # 注入文章媒体卡片（含 URL、标题、描述）
        if article_url:
            media_entry: Dict[str, Any] = {
                "status": "READY",
                "originalUrl": article_url,
                "title": {"text": title},
            }
            if description:
                media_entry["description"] = {"text": description}
            payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"].append(media_entry)

        return payload

    def push(self, payload: Dict[str, Any]):
        """执行物理推流到 LinkedIn UGC Posts API"""
        import time
        import random

        if not self.token:
            tlog.warning("⚠️ [LinkedIn] 缺少 Access Token，分发跳过。")
            return

        author_urn = self.person_urn or self.organization_urn
        if not author_urn:
            tlog.warning("⚠️ [LinkedIn] 缺少 person_urn 或 organization_urn，分发跳过。")
            return

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": LINKEDIN_API_VERSION_HEADER,
        }

        title = (
            payload.get("specificContent", {})
            .get("com.linkedin.ugc.ShareContent", {})
            .get("shareCommentary", {})
            .get("text", "")[:40]
        )

        # 🛡️ 1. 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上 (加上线程锁防止竞态穿透)
        global _last_linkedin_time
        with _linkedin_lock:
            while True:
                elapsed = time.time() - _last_linkedin_time
                if elapsed < 1.5:
                    time.sleep(1.5 - elapsed)
                else:
                    break

            _last_linkedin_time = time.time()

        # 🛡️ 2. 指数退避重试循环 (对冲 429 频控)
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                tlog.info(f"📡 [LinkedIn] 正在发布帖子: {title}...")
                resp = requests.post(
                    LINKEDIN_UGC_POSTS_URL,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                _last_linkedin_time = time.time()

                if resp.status_code == 429:
                    if attempt < max_attempts - 1:
                        sleep_time = 3.0 * (2 ** attempt) + random.uniform(0.1, 0.5)
                        tlog.warning(f"⚠️ [LinkedIn Rate Limit] 频率超限，正在休眠 {sleep_time:.2f} 秒后重试...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        raise RuntimeError("对端 LinkedIn 接口频控限制 (429 Too Many Requests)，请稍后重试。")

                if resp.status_code == 201:
                    post_id = resp.headers.get("x-restli-id", resp.headers.get("X-RestLi-Id", ""))
                    tlog.info(f"✨ [LinkedIn 同步成功] Post ID: {post_id}")
                    return {"url": f"https://www.linkedin.com/feed/update/{post_id}" if post_id else ""}
                elif resp.status_code == 401:
                    raise RuntimeError("LinkedIn 认证失败（401）：Access Token 无效或已过期，请重新进行 OAuth2 授权绑定。")
                elif resp.status_code == 403:
                    raise RuntimeError("LinkedIn 权限不足（403）：请确认您的 App 拥有 w_member_social 权限，且 URN 与授权账户相符。")
                else:
                    raise RuntimeError(f"LinkedIn API 报错 ({resp.status_code}): {resp.text}")

            except requests.RequestException as req_err:
                if attempt < max_attempts - 1:
                    sleep_time = 2.0 + random.uniform(0.1, 0.5)
                    time.sleep(sleep_time)
                    continue
                else:
                    tlog.error(f"🛑 [LinkedIn] 网络请求失败: {req_err}")
                    raise RuntimeError(f"LinkedIn 网络请求失败: {req_err}") from req_err
            except Exception as e:
                tlog.error(f"🛑 [LinkedIn] 失败: {e}")
                raise e
