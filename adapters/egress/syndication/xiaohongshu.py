#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Xiaohongshu (RED) Syndicator
模块职责：负责将稿件智能转换为小红书图文笔记并同步分发至创作者平台。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import re
import time
import random
import requests
import threading
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog

# 全局平滑流控防线：控制两次发送间隔时间在 2.0 秒以上
_last_xhs_time = 0.0
_xhs_lock = threading.Lock()


class XiaohongshuSyndicator(BaseSyndicator):
    PLUGIN_ID = "xiaohongshu"
    DISPLAY_NAME = "小红书"
    ICON = "📕"
    VERSION = "V1.8.0"
    DESCRIPTION = "将文章智能提炼为图文笔记，自动提取插图轮播与热门话题标签，同步至小红书创作者平台。"
    SLA_TIER = "tier2"
    SLA_LABEL = "Cookie辅助"
    SLA_DESC = "依赖小红书创作者平台 Web Cookie (a1/web_session)，需定期维护登录凭据。"

    REQUIRED_PACKAGES = ["requests"]

    def _normalize_image_url(self, raw_path: str, site_url: str) -> Optional[str]:
        """将本地相对路径、绝对路径或公网链接统一规范化为绝对公网 URL"""
        if not raw_path:
            return None
        p = str(raw_path).strip().strip("'\"")
        if p.startswith("http://") or p.startswith("https://"):
            return p
        if not site_url:
            return None
        base = site_url.rstrip("/") + "/"
        clean_rel = p.lstrip("/")
        return urljoin(base, clean_rel)

    def extract_images(self, content: str, metadata: dict, site_url: str) -> List[str]:
        """全域提取封面图、Markdown图片、HTML图片与Obsidian维基图片(上限9张)"""
        image_urls: List[str] = []

        # 1. 优先提取元数据中的封面图
        cover = metadata.get("cover") or metadata.get("image") or metadata.get("banner")
        norm_cover = self._normalize_image_url(cover, site_url)
        if norm_cover:
            image_urls.append(norm_cover)

        # 2. 正则提取 Markdown 标准语法: ![alt](url)
        md_imgs = re.findall(r'!\[.*?\]\(([^)\s]+)', content)
        for img in md_imgs:
            norm_img = self._normalize_image_url(img, site_url)
            if norm_img and norm_img not in image_urls:
                image_urls.append(norm_img)
                if len(image_urls) >= 9:
                    return image_urls

        # 3. 正则提取 HTML 语法: <img src="url">
        html_imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
        for img in html_imgs:
            norm_img = self._normalize_image_url(img, site_url)
            if norm_img and norm_img not in image_urls:
                image_urls.append(norm_img)
                if len(image_urls) >= 9:
                    return image_urls

        # 4. 正则提取 Obsidian 维基图片语法: ![[image.png]] 或 ![[image.png|300]]
        wiki_imgs = re.findall(r'!\[\[([^\|\]\n]+)(?:\|[^\]\n]+)?\]\]', content)
        for img in wiki_imgs:
            norm_img = self._normalize_image_url(img, site_url)
            if norm_img and norm_img not in image_urls:
                image_urls.append(norm_img)
                if len(image_urls) >= 9:
                    return image_urls

        return image_urls

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        site_url = self.site_url.rstrip('/') if self.site_url else ""
        if not canonical_url:
            canonical_url = f"{site_url}/{slug}".replace('//', '/').replace(':/', '://')

        metadata = metadata or {}

        # 1. 提取所有图像 URL 作为小红书卡片轮播图 (最多 9 张)
        image_urls = self.extract_images(content, metadata, site_url)

        # 2. 格式化热门话题标签 (Hashtags)
        raw_tags = metadata.get("tags") or []
        if isinstance(raw_tags, str):
            raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]

        clean_tags = []
        for t in raw_tags:
            t_clean = re.sub(r'^[#＃]+|[#＃]+$', '', str(t)).strip()
            if t_clean and t_clean not in clean_tags:
                clean_tags.append(t_clean)

        tags_str = " ".join([f"#{t}#" for t in clean_tags[:8]])

        # 3. 智能提炼笔记简短标题 (小红书标题上限 20 字)
        clean_title = title.replace("#", "").replace("*", "").strip()
        if len(clean_title) > 20:
            short_title = clean_title[:19] + "…"
        else:
            short_title = clean_title

        # 4. 笔记正文提炼与小红书专属移动端微排版
        note_body = content.strip()
        # 清理多余 Markdown 代码块
        note_body = re.sub(r'```[\s\S]*?```', '[💻 核心代码实现请查阅全文链接]', note_body)
        # 将各级 Markdown 标题转换为亲和的 Emoji 导向段落
        note_body = re.sub(r'(?m)^#{1,2}\s+(.+)$', r'📌 \1', note_body)
        note_body = re.sub(r'(?m)^#{3,4}\s+(.+)$', r'💡 \1', note_body)
        note_body = re.sub(r'(?m)^#{5,6}\s+(.+)$', r'✨ \1', note_body)
        # 移除裸 Obsidian 语法
        note_body = re.sub(r'!\[\[.*?\]\]', '', note_body)
        # 规整多余连续换行
        note_body = re.sub(r'\n{3,}', '\n\n', note_body).strip()

        # 严格遵守小红书 1000 字符限制 (预留尾部原文链接与标签)
        max_body_len = 820
        if len(note_body) > max_body_len:
            note_body = note_body[:max_body_len] + f"\n\n...\n📖 完整阅读与高清大图：{canonical_url}"

        full_note_text = f"{note_body}\n\n{tags_str}".strip() if tags_str else note_body

        return {
            "title": short_title,
            "content": full_note_text,
            "images": image_urls,
            "tags": clean_tags,
            "source_url": canonical_url,
            "post_type": "normal"
        }

    def push(self, payload: dict, remote_id: str = None, **kwargs):
        token = getattr(self.config, 'token', None) or (self.config.get('token') if isinstance(self.config, dict) else None)
        cookie = getattr(self.config, 'cookie', None) or (self.config.get('cookie') if isinstance(self.config, dict) else None)

        if not token and not cookie:
            tlog.warning("⚠️ [小红书] 缺少 token 或 cookie 凭据配置，分发跳过。")
            return

        api_endpoint = (
            getattr(self.config, 'api_endpoint', None)
            or (self.config.get('api_endpoint') if isinstance(self.config, dict) else None)
            or "https://edith.xiaohongshu.com/api/sns/web/v1/note"
        )
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
            # 精细化锁区间：仅在计算平滑流控时间戳时持有锁，网络请求在锁外执行
            with _xhs_lock:
                now = time.time()
                elapsed = now - _last_xhs_time
                wait_sec = max(0.0, 2.0 - elapsed)
                _last_xhs_time = now + wait_sec

            if wait_sec > 0:
                time.sleep(wait_sec)

            try:
                resp = requests.post(api_endpoint, json=payload, headers=headers, timeout=self.timeout)
            except requests.RequestException as req_err:
                if attempt < max_attempts - 1:
                    retry_wait = 2.0 + random.uniform(0.1, 0.5)
                    tlog.warning(f"⚠️ [小红书网络重试] 正在休眠 {retry_wait:.2f} 秒后重试...")
                    time.sleep(retry_wait)
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
