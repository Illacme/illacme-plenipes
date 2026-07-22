#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Medium Syndicator Plugin
🚀 [V75.1]：全面对齐 BaseSyndicator 物理契约，彻底清扫零散碎片。
"""

import requests
from typing import Dict, Any
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

import threading

# 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
_last_medium_time = 0.0
_medium_lock = threading.Lock()

class MediumSyndicator(BaseSyndicator):
    PLUGIN_ID = "medium"
    DISPLAY_NAME = "Medium"
    VERSION = "V1.1"
    DESCRIPTION = "同步至 Medium 全球创作平台，支持 Markdown 格式化与 Canonical URL 溯源。"

    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: Dict[str, Any], canonical_url: str = None) -> Dict[str, Any]:
        """对齐 BaseSyndicator 抽象接口契约"""
        tags = metadata.get('tags', [])
        # Canonical URL 优先使用传入值，否则 Fallback 推导
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        return {
            "title": title,
            "contentFormat": "markdown",
            "content": content,
            "canonicalUrl": canonical_url,
            "tags": tags[:5],
            "publishStatus": getattr(self.config, 'publish_status', 'draft') # 默认为草稿模式，安全防呆
        }

    def push(self, payload: Dict[str, Any]):
        """执行物理推流到 Medium"""
        import time
        import random

        token = getattr(self.config, 'integration_token', None)
        if not token:
            tlog.warning("⚠️ [Medium] 缺少 integration_token，分发跳过。")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # 🛡️ 指数退避重试循环 (加上临界锁严格防线：每一次尝试发送，都必须串行流控间隔 3.0 秒以上)
        max_attempts = 3
        global _last_medium_time
        for attempt in range(max_attempts):
            with _medium_lock:
                while True:
                    elapsed = time.time() - _last_medium_time
                    if elapsed < 3.0:
                        time.sleep(3.0 - elapsed)
                    else:
                        break

                _last_medium_time = time.time()
                try:
                    # 2.1 物理获取当前授权的 Author ID
                    user_url = "https://api.medium.com/v1/me"
                    user_resp = requests.get(user_url, headers=headers, timeout=self.timeout)
                    _last_medium_time = time.time()
                except requests.RequestException as req_err:
                    _last_medium_time = time.time()
                    if attempt < max_attempts - 1:
                        sleep_time = 2.0 + random.uniform(0.1, 0.5)
                        tlog.warning(f"⚠️ [Medium 网络失败] 正在休眠 {sleep_time:.2f} 秒后重新排队进行第 {attempt + 2} 次重试...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        tlog.error(f"🛑 [Medium] 网络请求失败: {req_err}")
                        raise RuntimeError(f"Medium 网络请求失败: {req_err}") from req_err
                except Exception as e:
                    _last_medium_time = time.time()
                    tlog.error(f"🛑 [Medium 失败]: {e}")
                    raise e

            # 释放锁后检查接口响应
            if user_resp.status_code == 429:
                if attempt < max_attempts - 1:
                    sleep_time = 6.0 * (2 ** attempt) + random.uniform(0.2, 0.5)
                    tlog.warning(f"⚠️ [Medium Rate Limit] 获取用户信息 429，正在休眠 {sleep_time:.2f} 秒后重新排队进行第 {attempt + 2} 次重试...")
                    time.sleep(sleep_time)
                    continue
                else:
                    raise RuntimeError("对端 Medium 接口频控限制 (429 Too Many Requests)，请稍后重试。")

            if user_resp.status_code != 200:
                if user_resp.status_code == 401:
                    raise RuntimeError("Medium 账户认证失败：Token 无效或已过期，请在插件配置中重新录入 Integration Token。")
                raise RuntimeError(f"Medium 账户认证失败 ({user_resp.status_code}): {user_resp.text}")

            author_id = user_resp.json().get("data", {}).get("id")
            if not author_id:
                raise RuntimeError("无法提取 Medium Author ID。")

            # 2.2 推送文章 (也需用锁进行并发管控)
            with _medium_lock:
                while True:
                    elapsed = time.time() - _last_medium_time
                    if elapsed < 3.0:
                        time.sleep(3.0 - elapsed)
                    else:
                        break
                _last_medium_time = time.time()
                try:
                    post_url = f"https://api.medium.com/v1/users/{author_id}/posts"
                    resp = requests.post(post_url, json=payload, headers=headers, timeout=self.timeout)
                    _last_medium_time = time.time()
                except Exception as e:
                    _last_medium_time = time.time()
                    tlog.error(f"🛑 [Medium 失败]: {e}")
                    raise e

            if resp.status_code == 429:
                if attempt < max_attempts - 1:
                    sleep_time = 6.0 * (2 ** attempt) + random.uniform(0.2, 0.5)
                    tlog.warning(f"⚠️ [Medium Rate Limit] 推送文章 429，正在休眠 {sleep_time:.2f} 秒后重新排队进行第 {attempt + 2} 次重试...")
                    time.sleep(sleep_time)
                    continue
                else:
                    raise RuntimeError("对端 Medium 接口频控限制 (429 Too Many Requests)，请稍后重试。")

            if resp.status_code in [200, 201]:
                post_link = resp.json().get("data", {}).get("url")
                tlog.info(f"✨ [Medium 同步成功] 链接: {post_link}")
                return {"url": post_link}
            else:
                raise RuntimeError(f"Medium API 报错 ({resp.status_code}): {resp.text}")
