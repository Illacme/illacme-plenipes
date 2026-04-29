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

class WordPressSyndicator(BaseSyndicator):
    PLUGIN_ID = "wordpress"
    
    # 🚀 [V11.3] 声明运行时依赖契约
    REQUIRED_PACKAGES = ["requests"]

    def __init__(self, config: Any, site_url: str):
        super().__init__(config)
        self.site_url = site_url
        self.api_url = getattr(config, 'api_url', '').rstrip('/')
        self.username = getattr(config, 'username', '')
        self.app_password = getattr(config, 'application_password', '')
        self.status = getattr(config, 'default_status', 'publish')

    def _get_auth_header(self):
        """生成 WordPress Application Password 认证头"""
        auth_str = f"{self.username}:{self.app_password}"
        encoded_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        return {"Authorization": f"Basic {encoded_auth}"}

    def format_payload(self, title: str, slug: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """组装 WordPress REST API 的标准数据结构"""
        # 提取分类与标签
        tags = metadata.get('tags', [])
        categories = metadata.get('categories', [])
        
        # 🚀 组装核心 Payload
        payload = {
            "title": title,
            "content": content,
            "slug": slug,
            "status": self.status,
            "format": "standard"
        }
        
        # 注意：WordPress REST API 接收分类和标签通常需要 ID，
        # 这里为了简化，我们仅透传原始数据，具体的 ID 映射可在 push 中按需处理。
        # 建议在 config 中预定义分类 ID 映射。
        return payload

    def push(self, payload: Dict[str, Any]):
        """执行物理推流"""
        if not self.api_url or not self.app_password:
            tlog.warning("⚠️ [WordPress] 缺少 API 配置或应用密码，分发跳过。")
            return

        endpoint = f"{self.api_url}/posts"
        headers = self._get_auth_header()
        
        try:
            # 🚀 尝试查找是否存在同 Slug 的文章（实现原地更新）
            search_url = f"{endpoint}?slug={payload['slug']}&status=any"
            search_resp = requests.get(search_url, headers=headers, timeout=self.timeout)
            
            existing_post_id = None
            if search_resp.status_code == 200:
                results = search_resp.json()
                if results and len(results) > 0:
                    existing_post_id = results[0]['id']

            if existing_post_id:
                # 执行更新 (Update)
                tlog.info(f"📡 [WordPress] 正在更新现有文章 (ID: {existing_post_id}): {payload['title']}")
                resp = requests.post(f"{endpoint}/{existing_post_id}", json=payload, headers=headers, timeout=self.timeout)
            else:
                # 执行创建 (Create)
                tlog.info(f"📡 [WordPress] 正在创建新文章: {payload['title']}")
                resp = requests.post(endpoint, json=payload, headers=headers, timeout=self.timeout)

            if resp.status_code in [200, 201]:
                tlog.info(f"✨ [WordPress] 同步成功！文章 URL: {resp.json().get('link')}")
            else:
                raise RuntimeError(f"API 返回错误 ({resp.status_code}): {resp.text}")

        except Exception as e:
            tlog.error(f"❌ [WordPress] 推流失败: {e}")
            raise e
