#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Xiaohongshu (RED) Syndicator
模块职责：负责将稿件智能转换为小红书图文笔记并同步分发至创作者平台。
"""

import re
import requests
import threading
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

_last_xhs_time = 0.0
_xhs_lock = threading.Lock()

class XiaohongshuSyndicator(BaseSyndicator):
    PLUGIN_ID = "xiaohongshu"
    DISPLAY_NAME = "小红书"
    VERSION = "V1.0"
    DESCRIPTION = "将文章智能提炼为图文笔记，自动提取插图轮播与热门话题标签，同步至小红书创作者平台。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        # 1. 提取所有 Markdown 图像 URL 作为笔记卡片轮播图 (最多 9 张)
        image_urls = []
        cover = metadata.get("cover") or metadata.get("image")
        if cover:
            image_urls.append(cover)
        
        # 正则提取正文图片: ![alt](url)
        img_matches = re.findall(r'!\[.*?\]\((https?://[^\s\)]+)\)', content)
        for img in img_matches:
            if img not in image_urls:
                image_urls.append(img)
                if len(image_urls) >= 9:
                    break

        # 2. 提取并格式化话题标签 (Hashtags)
        raw_tags = metadata.get("tags") or []
        if isinstance(raw_tags, str):
            raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
        
        tags_str = " ".join([f"#{t}#" if not t.startswith("#") else t for t in raw_tags])

        # 3. 智能提炼笔记简短标题 (小红书标题上限 20 字)
        clean_title = title.replace("#", "").strip()
        if len(clean_title) > 20:
            short_title = clean_title[:19] + "…"
        else:
            short_title = clean_title

        # 4. 笔记正文提炼 (保留清晰段落与摘要，末尾附加话题)
        description = metadata.get("description") or metadata.get("summary") or ""
        note_body = content.strip()
        # 清理过长代码块为简写说明
        note_body = re.sub(r'```[\s\S]*?```', '[💡 核心代码实现请查阅全文链接]', note_body)
        
        if len(note_body) > 900:
            note_body = note_body[:850] + f"\n\n...\n📖 完整阅读与高清大图：{canonical_url}"

        full_note_text = f"{note_body}\n\n{tags_str}".strip()

        return {
            "title": short_title,
            "content": full_note_text,
            "images": image_urls,
            "tags": raw_tags,
            "source_url": canonical_url,
            "post_type": "normal"  # normal: 图文笔记
        }

    def push(self, payload: dict):
        import time
        import random

        token = getattr(self.config, 'token', None) or self.config.get('token')
        cookie = getattr(self.config, 'cookie', None) or self.config.get('cookie')

        if not token and not cookie:
            tlog.warning("⚠️ [小红书] 缺少 token 或 cookie 凭据配置，分发跳过。")
            return

        api_endpoint = getattr(self.config, 'api_endpoint', None) or self.config.get('api_endpoint') or "https://edith.xiaohongshu.com/api/sns/web/v1/note"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if cookie:
            headers["Cookie"] = cookie

        max_attempts = 3
        global _last_xhs_time
        for attempt in range(max_attempts):
            with _xhs_lock:
                while True:
                    elapsed = time.time() - _last_xhs_time
                    if elapsed < 2.0:
                        time.sleep(2.0 - elapsed)
                    else:
                        break

                _last_xhs_time = time.time()
                try:
                    resp = requests.post(api_endpoint, json=payload, headers=headers, timeout=self.timeout)
                    _last_xhs_time = time.time()
                except requests.RequestException as req_err:
                    _last_xhs_time = time.time()
                    if attempt < max_attempts - 1:
                        sleep_time = 2.0 + random.uniform(0.1, 0.5)
                        tlog.warning(f"⚠️ [小红书网络重试] 正在休眠 {sleep_time:.2f} 秒后重试...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        tlog.error(f"🛑 [小红书分发] 请求异常: {req_err}")
                        return

            if resp.status_code in [200, 201]:
                tlog.info(f"✅ [小红书] 图文笔记《{payload.get('title')}》成功同步分发！")
                return
            else:
                tlog.warning(f"⚠️ [小红书] 服务端返回状态码 {resp.status_code}: {resp.text}")
                return
