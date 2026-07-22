#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Adapter - WordPress Syndicator (REST API)
模块职责：通过 WordPress REST API 将内容同步至站点。
🚀 [V13.1] 生产级适配器：支持分类、标签与原子级发布。
"""

import base64
import requests
from typing import Dict, Any
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

import threading

# 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
_last_wordpress_time = 0.0
_wordpress_lock = threading.Lock()

class WordPressSyndicator(BaseSyndicator):
    PLUGIN_ID = "wordpress"
    DISPLAY_NAME = "WordPress"
    VERSION = "V1.0"
    DESCRIPTION = "通过 WordPress REST API 进行内容同步，支持文章分类、标签映射与 Slug 冲突自愈。"
    
    # 🚀 [V11.3] 声明运行时依赖契约
    REQUIRED_PACKAGES = ["requests"]

    def __init__(self, config: Any, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.api_url = getattr(config, 'api_url', '').rstrip('/')
        self.username = getattr(config, 'username', '')
        self.app_password = getattr(config, 'application_password', '')
        self.status = getattr(config, 'default_status', 'publish')


    def _get_auth_header(self):
        """生成 WordPress Application Password 认证头"""
        auth_str = f"{self.username}:{self.app_password}"
        encoded_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        return {"Authorization": f"Basic {encoded_auth}"}

    def format_payload(self, title: str, slug: str, content: str, metadata: Dict[str, Any], canonical_url: str = None) -> Dict[str, Any]:
        """组装 WordPress REST API 的标准数据结构"""
        # 提取分类与标签
        metadata.get('tags', [])
        metadata.get('categories', [])
        
        # 🚀 组装核心 Payload
        payload = {
            "title": title,
            "content": content,
            "slug": slug,
            "status": self.status,
            "format": "standard"
        }
        
        if canonical_url:
            payload["meta"] = {"_yoast_wpseo_canonical": canonical_url}
            
        return payload

    def push(self, payload: Dict[str, Any]):
        """执行物理推流"""
        import time
        import random

        if not self.api_url or not self.app_password:
            tlog.warning("⚠️ [WordPress] 缺少 API 配置或应用密码，分发跳过。")
            return

        endpoint = f"{self.api_url}/posts"
        headers = self._get_auth_header()

        # 🛡️ 1. 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上 (加上线程锁防止竞态穿透)
        global _last_wordpress_time
        with _wordpress_lock:
            while True:
                elapsed = time.time() - _last_wordpress_time
                if elapsed < 1.5:
                    time.sleep(1.5 - elapsed)
                else:
                    break

            _last_wordpress_time = time.time()

        # 🛡️ 2. 指数退避重试循环 (对冲 429 频控)
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # 🚀 尝试查找是否存在同 Slug 的文章（实现原地更新）
                search_url = f"{endpoint}?slug={payload['slug']}&status=any"
                search_resp = requests.get(search_url, headers=headers, timeout=self.timeout)
                _last_wordpress_time = time.time()

                if search_resp.status_code == 429:
                    if attempt < max_attempts - 1:
                        sleep_time = 3.0 * (2 ** attempt) + random.uniform(0.1, 0.5)
                        time.sleep(sleep_time)
                        continue
                    else:
                        raise RuntimeError("对端 WordPress 接口频控限制 (429 Too Many Requests)，请稍后重试。")

                if search_resp.status_code == 401:
                    raise RuntimeError("WordPress 认证失败（401）：用户名或应用密码 (Application Password) 错误，请检查插件设置。")
                elif search_resp.status_code == 403:
                    raise RuntimeError("WordPress 权限不足（403）：请确保您所配账户具备文章编辑和发布权限。")
                
                search_resp.raise_for_status()
                
                existing_post_id = None
                results = search_resp.json()
                if results and len(results) > 0:
                    existing_post_id = results[0]['id']

                if existing_post_id:
                    # 执行更新 (Update)
                    tlog.info(f"📡 [WordPress] 正在更新现有文章 (ID: {existing_post_id}): {payload['title']} (第 {attempt + 1} 次尝试)")
                    resp = requests.post(f"{endpoint}/{existing_post_id}", json=payload, headers=headers, timeout=self.timeout)
                else:
                    # 执行创建 (Create)
                    tlog.info(f"📡 [WordPress] 正在创建新文章: {payload['title']} (第 {attempt + 1} 次尝试)")
                    resp = requests.post(endpoint, json=payload, headers=headers, timeout=self.timeout)
                
                _last_wordpress_time = time.time()

                if resp.status_code == 429:
                    if attempt < max_attempts - 1:
                        sleep_time = 3.0 * (2 ** attempt) + random.uniform(0.1, 0.5)
                        time.sleep(sleep_time)
                        continue
                    else:
                        raise RuntimeError("对端 WordPress 接口频控限制 (429 Too Many Requests)，请稍后重试。")

                if resp.status_code in [200, 201]:
                    link = resp.json().get('link')
                    tlog.info(f"✨ [WordPress] 同步成功！文章 URL: {link}")
                    return {"url": link}
                else:
                    raise RuntimeError(f"WordPress API 报错 ({resp.status_code}): {resp.text}")

            except requests.RequestException as req_err:
                if attempt < max_attempts - 1:
                    sleep_time = 2.0 + random.uniform(0.1, 0.5)
                    time.sleep(sleep_time)
                    continue
                else:
                    tlog.error(f"🛑 [WordPress] 网络请求失败: {req_err}")
                    raise RuntimeError(f"WordPress 网络请求失败: {req_err}") from req_err
            except Exception as e:
                tlog.error(f"❌ [WordPress] 推流失败: {e}")
                raise e
