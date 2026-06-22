#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Hashnode Syndicator Plugin
🚀 [V76.0]：对接 Hashnode GraphQL API，支持 Bearer Token 鉴权与文章发布。

配置示例 (config.yaml):
  syndication:
    hashnode:
      enabled: true
      token: "your_hashnode_personal_access_token"
      publication_id: "your_publication_id"   # 必填，Hashnode Publication ID
      hide_from_feed: false                    # 可选，是否隐藏自个人动态，默认 false
"""

import requests
from typing import Dict, Any

from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


# ---------------------------------------------------------------------------
# Hashnode GraphQL 端点
# ---------------------------------------------------------------------------
HASHNODE_GQL_URL = "https://gql.hashnode.com/"

# GraphQL Mutation：发布文章
PUBLISH_POST_MUTATION = """
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post {
      id
      slug
      url
      title
    }
  }
}
"""


class HashnodeSyndicator(BaseSyndicator):
    """
    🚀 [V76.0] Hashnode 全球博客社区分发插件
    通过 Hashnode GraphQL API 将内容发布至指定 Publication，支持标签映射。
    """
    PLUGIN_ID = "hashnode"
    DISPLAY_NAME = "Hashnode"
    VERSION = "V2.0"
    DESCRIPTION = "同步至 Hashnode 全球博客社区，通过 GraphQL API 实现文章发布，支持 Publication 绑定与标签映射。"

    REQUIRED_PACKAGES = ["requests"]

    def __init__(self, config: Any, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.token = getattr(config, "token", "")
        self.publication_id = getattr(config, "publication_id", "")
        self.hide_from_feed = getattr(config, "hide_from_feed", False)

    # ------------------------------------------------------------------
    # BaseSyndicator 契约实现
    # ------------------------------------------------------------------

    def format_payload(self, title: str, slug: str, content: str, metadata: Dict[str, Any], canonical_url: str = None) -> Dict[str, Any]:
        """
        组装 Hashnode PublishPost GraphQL 变量。
        文档：https://apidocs.hashnode.com/#mutation-publishPost
        """
        # 标签列表（Hashnode 接受 slug 格式标签）
        tags_raw = metadata.get("tags", [])
        tags = [{"slug": t.lower().replace(" ", "-"), "name": t} for t in tags_raw[:5]]

        # Canonical URL 优先使用传入值，否则 Fallback 推导
        if not canonical_url and self.site_url:
            canonical_url = f"{self.site_url.rstrip('/')}/{slug}"

        variables: Dict[str, Any] = {
            "input": {
                "title": title,
                "slug": slug,
                "contentMarkdown": content,
                "publicationId": self.publication_id,
                "tags": tags,
                "hideFromHashnodeFeed": self.hide_from_feed,
            }
        }

        if canonical_url:
            variables["input"]["originalArticleURL"] = canonical_url

        return {
            "query": PUBLISH_POST_MUTATION,
            "variables": variables,
        }

    def push(self, payload: Dict[str, Any]):
        """执行物理推流到 Hashnode GraphQL API"""
        if not self.token:
            tlog.warning("⚠️ [Hashnode] 缺少 token，分发跳过。")
            return

        if not self.publication_id:
            tlog.warning("⚠️ [Hashnode] 缺少 publication_id，分发跳过。")
            return

        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
        }

        input_data = payload.get("variables", {}).get("input", {})
        title = input_data.get("title", "")

        try:
            tlog.info(f"📡 [Hashnode] 正在发布文章: {title}")
            resp = requests.post(
                HASHNODE_GQL_URL,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            resp.raise_for_status()

            result = resp.json()

            # GraphQL 错误检查（HTTP 200 但含 errors 字段）
            gql_errors = result.get("errors")
            if gql_errors:
                error_msg = "; ".join(e.get("message", str(e)) for e in gql_errors)
                raise RuntimeError(f"Hashnode GraphQL 错误: {error_msg}")

            post_data = result.get("data", {}).get("publishPost", {}).get("post", {})
            post_url = post_data.get("url", "")
            post_slug = post_data.get("slug", "")
            tlog.info(f"✨ [Hashnode 同步成功] Slug: {post_slug} | URL: {post_url}")

        except requests.RequestException as e:
            tlog.error(f"🛑 [Hashnode] 网络请求失败: {e}")
            raise RuntimeError(f"Hashnode 网络请求失败: {e}") from e
