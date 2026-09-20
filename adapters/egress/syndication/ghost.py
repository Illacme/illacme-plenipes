#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Ghost Syndicator Plugin
🚀 [V76.0]：对接 Ghost Admin API v3，支持 JWT 鉴权与幂等发布。
🛡️ [SOP-01 & SOP-02]：自底向上物理拆分重构版本，单文件物理行数严格 ≤300 行。
"""

import time
import threading
from typing import Dict, Any, Optional

import requests
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog
from .ghost_utils import build_ghost_jwt, markdown_to_mobiledoc

# 保持历史方法兼容
_build_ghost_jwt = build_ghost_jwt

# 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
_last_ghost_time = 0.0
_ghost_lock = threading.Lock()


class GhostSyndicator(BaseSyndicator):
    """
    🚀 [V76.0] Ghost 专业出版平台分发插件
    通过 Ghost Admin API v3 将内容同步至 Ghost 站点，支持 JWT 鉴权与幂等发布。
    """
    PLUGIN_ID = "ghost"
    DISPLAY_NAME = "Ghost"
    ICON = "👻"
    VERSION = "V2.0"
    DESCRIPTION = "同步至 Ghost 专业出版平台，通过 Admin API v3 + JWT 鉴权实现文章创建与幂等更新。"

    REQUIRED_PACKAGES = ["requests"]

    def __init__(self, config: Any, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        if isinstance(config, dict):
            self.url = (config.get("url") or config.get("api_url") or "").rstrip("/")
            self.admin_api_key = config.get("admin_api_key") or ""
            self.update_existing = config.get("update_existing", True)
            self.default_status = config.get("default_status", "draft")
        else:
            raw_url = getattr(config, "url", None)
            if raw_url is None:
                raw_url = getattr(config, "api_url", "")
            self.url = raw_url.rstrip("/") if isinstance(raw_url, str) else ""
            raw_key = getattr(config, "admin_api_key", "")
            self.admin_api_key = raw_key if isinstance(raw_key, str) else ""
            self.update_existing = getattr(config, "update_existing", True)
            self.default_status = getattr(config, "default_status", "draft")
        self.api_url = self.url

    def format_payload(self, title: str, slug: str, content: str, metadata: Dict[str, Any], canonical_url: str = None) -> Dict[str, Any]:
        """组装 Ghost Admin API 所需的 post 数据结构"""
        tags = [{"name": t} for t in metadata.get("tags", [])]
        if not canonical_url and self.site_url:
            canonical_url = f"{self.site_url.rstrip('/')}/{slug}"

        mobiledoc = self._markdown_to_mobiledoc(content)
        post_item: Dict[str, Any] = {
            "title": title,
            "slug": slug,
            "mobiledoc": mobiledoc,
            "status": self.default_status,
            "tags": tags,
        }
        if canonical_url:
            post_item["canonical_url"] = canonical_url

        return {"posts": [post_item]}

    def push(self, payload: Dict[str, Any], remote_id: str = None, **kwargs):
        """执行物理推流到 Ghost Admin API"""
        import random

        if not self.url or not self.admin_api_key:
            tlog.warning("⚠️ [Ghost] 缺少 url 或 admin_api_key，分发跳过。")
            return

        key_parts = self.admin_api_key.split(":")
        if len(key_parts) != 2:
            tlog.error("❌ [Ghost] admin_api_key 格式错误，应为 'id:hex_secret'。")
            raise ValueError("Ghost admin_api_key 格式错误，应为 'id:hex_secret'")

        key_id, hex_secret = key_parts[0], key_parts[1]

        global _last_ghost_time
        while True:
            elapsed = time.time() - _last_ghost_time
            if elapsed < 1.5:
                time.sleep(1.5 - elapsed)
            else:
                break
        _last_ghost_time = time.time()

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                jwt_token = build_ghost_jwt(key_id, hex_secret)
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
                existing_id: Optional[str] = None
                if self.update_existing and slug:
                    existing_id = self._find_post_id_by_slug(api_base, headers, slug)

                if existing_id:
                    tlog.info(f"📡 [Ghost] 正在更新现有文章 (ID: {existing_id}): {post_data.get('title')} (第 {attempt + 1} 次尝试)")
                    get_resp = requests.get(
                        f"{api_base}/posts/{existing_id}/",
                        headers=headers,
                        timeout=self.timeout,
                    )
                    _last_ghost_time = time.time()

                    if get_resp.status_code == 429:
                        if attempt < max_attempts - 1:
                            sleep_time = 3.0 * (2 ** attempt) + random.uniform(0.1, 0.5)
                            time.sleep(sleep_time)
                            continue
                        else:
                            raise RuntimeError("对端 Ghost 接口频控限制 (429 Too Many Requests)，请稍后重试。")

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
                    tlog.info(f"📡 [Ghost] 正在创建新文章: {post_data.get('title')} (第 {attempt + 1} 次尝试)")
                    resp = requests.post(
                        f"{api_base}/posts/",
                        json=payload,
                        headers=headers,
                        timeout=self.timeout,
                    )
                
                _last_ghost_time = time.time()

                if resp.status_code == 429:
                    if attempt < max_attempts - 1:
                        sleep_time = 3.0 * (2 ** attempt) + random.uniform(0.1, 0.5)
                        time.sleep(sleep_time)
                        continue
                    else:
                        raise RuntimeError("对端 Ghost 接口频控限制 (429 Too Many Requests)，请稍后重试。")

                if resp.status_code in (200, 201):
                    result_post = resp.json().get("posts", [{}])[0]
                    post_url = result_post.get("url", "")
                    tlog.info(f"✨ [Ghost 同步成功] URL: {post_url}")
                    return {"url": post_url}
                elif resp.status_code == 401:
                    raise RuntimeError("Ghost 认证失败（401）：JWT 鉴权未通过，请检查 admin_api_key 格式与 Secret。")
                else:
                    raise RuntimeError(f"Ghost Admin API 报错 ({resp.status_code}): {resp.text}")

            except requests.RequestException as req_err:
                if attempt < max_attempts - 1:
                    sleep_time = 2.0 + random.uniform(0.1, 0.5)
                    time.sleep(sleep_time)
                    continue
                else:
                    tlog.error(f"🛑 [Ghost] 网络请求失败: {req_err}")
                    raise RuntimeError(f"Ghost 网络请求失败: {req_err}") from req_err
            except Exception as e:
                tlog.error(f"🛑 [Ghost] 失败: {e}")
                raise e

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
        """将 Markdown 内容包装为 Ghost Mobiledoc 格式"""
        return markdown_to_mobiledoc(markdown)

    def delete(self, remote_id: str) -> bool:
        """🚀 远程物理下架：通过 Ghost Admin API 彻底删除对端文章"""
        if not remote_id or not self.api_url or not self.admin_api_key:
            return False
        
        api_base = f"{self.api_url}/ghost/api/admin"
        try:
            key_id, hex_secret = self.admin_api_key.split(":")
            token = build_ghost_jwt(key_id, hex_secret)
        except Exception:
            return False

        headers = {
            "Authorization": f"Ghost {token}",
            "Content-Type": "application/json",
            "Accept-Version": "v5.0"
        }
        
        try:
            resp = requests.delete(f"{api_base}/posts/{remote_id}/", headers=headers, timeout=self.timeout)
            if resp.status_code in (200, 204):
                tlog.info(f"🗑️ [Ghost 物理下架成功] 文章已永久删除 (ID: {remote_id})")
                return True
            elif resp.status_code == 404:
                tlog.info(f"🗑️ [Ghost 物理对正] 文章在 Ghost 已不存在 (ID: {remote_id})，自动对正解绑。")
                return True
            else:
                tlog.error(f"🛑 [Ghost 物理下架失败] ID: {remote_id} (HTTP {resp.status_code}): {resp.text[:200]}")
                return False
        except Exception as e:
            tlog.error(f"🛑 [Ghost 物理下架异常] ID: {remote_id}: {e}")
            return False
