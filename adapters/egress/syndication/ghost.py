#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Ghost Syndicator Plugin
🚀 [V76.0]：对接 Ghost Admin API v3，支持 JWT 鉴权与幂等发布。

配置示例 (config.yaml):
  syndication:
    ghost:
      enabled: true
      url: "https://your-ghost-site.com"         # Ghost 站点根 URL（无尾斜杠）
      admin_api_key: "your_key_id:your_hex_secret" # Admin API Key（格式: id:secret）
      update_existing: true                         # 可选，对同 Slug 文章执行更新，默认 true
      default_status: "draft"                       # 可选，"draft" 或 "published"，默认 draft
"""

import hmac
import hashlib
import base64
import json
import time
from typing import Dict, Any, Optional

import requests
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


# ---------------------------------------------------------------------------
# JWT 工具函数（基于 Python 标准库，无需 PyJWT）
# Ghost Admin API JWT 规范：
#   Header: {"alg": "HS256", "kid": <key_id>, "typ": "JWT"}
#   Payload: {"iat": <now>, "exp": <now + 5min>, "aud": "/admin/"}
#   签名密钥：bytes.fromhex(hex_secret)
# ---------------------------------------------------------------------------

def _b64url_encode(data: bytes) -> str:
    """URL-safe Base64 编码，无填充符"""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _build_ghost_jwt(key_id: str, hex_secret: str) -> str:
    """
    生成符合 Ghost Admin API 规范的 JWT Token。

    :param key_id: Admin API Key 的 ID 部分（冒号前）
    :param hex_secret: Admin API Key 的 Secret 部分（冒号后，十六进制字符串）
    :return: JWT Token 字符串
    """
    now = int(time.time())
    header = {"alg": "HS256", "kid": key_id, "typ": "JWT"}
    payload = {"iat": now, "exp": now + 300, "aud": "/admin/"}

    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signing_key = bytes.fromhex(hex_secret)

    signature = hmac.new(signing_key, signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


class GhostSyndicator(BaseSyndicator):
    """
    🚀 [V76.0] Ghost 专业出版平台分发插件
    通过 Ghost Admin API v3 将内容同步至 Ghost 站点，支持 JWT 鉴权与幂等发布。
    """
    PLUGIN_ID = "ghost"
    DISPLAY_NAME = "Ghost"
    VERSION = "V2.0"
    DESCRIPTION = "同步至 Ghost 专业出版平台，通过 Admin API v3 + JWT 鉴权实现文章创建与幂等更新。"

    REQUIRED_PACKAGES = ["requests"]

    def __init__(self, config: Any, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.url = getattr(config, "url", "").rstrip("/")
        self.admin_api_key = getattr(config, "admin_api_key", "")
        self.update_existing = getattr(config, "update_existing", True)
        self.default_status = getattr(config, "default_status", "draft")

    # ------------------------------------------------------------------
    # BaseSyndicator 契约实现
    # ------------------------------------------------------------------

    def format_payload(self, title: str, slug: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """组装 Ghost Admin API 所需的 post 数据结构"""
        tags = [{"name": t} for t in metadata.get("tags", [])]
        canonical_url = f"{self.site_url.rstrip('/')}/{slug}" if self.site_url else ""

        post: Dict[str, Any] = {
            "title": title,
            "slug": slug,
            "mobiledoc": self._markdown_to_mobiledoc(content),
            "status": self.default_status,
            "tags": tags,
        }
        if canonical_url:
            post["canonical_url"] = canonical_url

        return {"posts": [post]}

    def push(self, payload: Dict[str, Any]):
        """执行物理推流到 Ghost Admin API"""
        if not self.url or not self.admin_api_key:
            tlog.warning("⚠️ [Ghost] 缺少 url 或 admin_api_key，分发跳过。")
            return

        # 解析 Admin API Key
        key_parts = self.admin_api_key.split(":")
        if len(key_parts) != 2:
            tlog.error("❌ [Ghost] admin_api_key 格式错误，应为 'id:hex_secret'。")
            raise ValueError("Ghost admin_api_key 格式错误，应为 'id:hex_secret'")

        key_id, hex_secret = key_parts[0], key_parts[1]

        try:
            jwt_token = _build_ghost_jwt(key_id, hex_secret)
        except ValueError as e:
            tlog.error(f"❌ [Ghost] JWT 生成失败，请检查 admin_api_key 的 secret 是否为合法十六进制: {e}")
            raise

        headers = {
            "Authorization": f"Ghost {jwt_token}",
            "Content-Type": "application/json",
            "Accept-Version": "v3.0",
        }

        post_data = payload.get("posts", [{}])[0]
        slug = post_data.get("slug", "")
        api_base = f"{self.url}/ghost/api/admin"

        try:
            # 幂等检查：查询同 Slug 是否已存在
            existing_id: Optional[str] = None
            if self.update_existing and slug:
                existing_id = self._find_post_id_by_slug(api_base, headers, slug)

            if existing_id:
                # 更新现有文章（PUT 需要附带 updated_at 做乐观锁）
                tlog.info(f"📡 [Ghost] 正在更新现有文章 (ID: {existing_id}): {post_data.get('title')}")
                # 获取当前 updated_at
                get_resp = requests.get(
                    f"{api_base}/posts/{existing_id}/",
                    headers=headers,
                    timeout=self.timeout,
                )
                get_resp.raise_for_status()
                current_updated_at = get_resp.json().get("posts", [{}])[0].get("updated_at")
                post_data["updated_at"] = current_updated_at

                resp = requests.put(
                    f"{api_base}/posts/{existing_id}/",
                    json={"posts": [post_data]},
                    headers=headers,
                    timeout=self.timeout,
                )
            else:
                # 创建新文章
                tlog.info(f"📡 [Ghost] 正在创建新文章: {post_data.get('title')}")
                resp = requests.post(
                    f"{api_base}/posts/",
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )

            if resp.status_code in (200, 201):
                result_post = resp.json().get("posts", [{}])[0]
                post_url = result_post.get("url", "")
                tlog.info(f"✨ [Ghost 同步成功] URL: {post_url}")
            else:
                raise RuntimeError(f"Ghost Admin API 报错 ({resp.status_code}): {resp.text}")

        except requests.RequestException as e:
            tlog.error(f"🛑 [Ghost] 网络请求失败: {e}")
            raise RuntimeError(f"Ghost 网络请求失败: {e}") from e

    # ------------------------------------------------------------------
    # 内部辅助方法
    # ------------------------------------------------------------------

    def _find_post_id_by_slug(self, api_base: str, headers: dict, slug: str) -> Optional[str]:
        """通过 Slug 查询文章 ID，用于幂等更新"""
        try:
            resp = requests.get(
                f"{api_base}/posts/slug/{slug}/",
                headers=headers,
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                posts = resp.json().get("posts", [])
                if posts:
                    return posts[0].get("id")
        except requests.RequestException:
            pass
        return None

    @staticmethod
    def _markdown_to_mobiledoc(markdown: str) -> str:
        """
        将 Markdown 内容包装为 Ghost Mobiledoc 格式（Markdown Card）。
        Ghost Admin API 接受 Mobiledoc JSON 字符串作为内容载体。
        """
        mobiledoc = {
            "version": "0.3.1",
            "markups": [],
            "atoms": [],
            "cards": [["markdown", {"markdown": markdown}]],
            "sections": [[10, 0]],
        }
        return json.dumps(mobiledoc, ensure_ascii=False)
