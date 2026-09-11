#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AST Shards: Metadata Sanitizer (元数据与标签治理器)
职责：规范化社媒分发元数据，处理 Tags 合规性、封面图公网化与 Canonical URL 原创物权注入。
🛡️ [SOP-01] 物理行数保持在 300 行以内。
"""

import re
from typing import Dict, Any, List
from urllib.parse import urljoin

class MetadataSanitizer:
    """🚀 [V121.0] 社媒分发元数据深度治理器"""

    @staticmethod
    def sanitize_tags(tags: Any, max_tags: int = 4, target_platform: str = "devto") -> List[str]:
        """
        清洗文章标签，使其符合 Dev.to / Hashnode 等平台极为严苛的格式规约：
        1. 仅允许小写字母、数字及下划线；
        2. 剔除特殊字符与空格；
        3. 中文等非 ASCII 标签自动过滤或规范化；
        4. 强制去重并截断至平台上限 (Dev.to 为 4 个)。
        """
        if not tags:
            return ["technology", "publishing"]

        raw_list = tags if isinstance(tags, list) else [str(t).strip() for t in str(tags).split(',')]
        clean_tags = []

        for t in raw_list:
            t_str = str(t).strip().lower()
            # 移除非字母数字字符 (保留下划线)
            sanitized = re.sub(r'[^a-z0-9_]', '', t_str)
            if sanitized and len(sanitized) >= 2:
                if sanitized not in clean_tags:
                    clean_tags.append(sanitized)

        # 若未提取到任何有效 ASCII 标签，注入安全默认兜底标签
        if not clean_tags:
            clean_tags = ["technology", "publishing"]

        return clean_tags[:max_tags]

    @staticmethod
    def resolve_cover_image(fm: Dict[str, Any], site_url: str = "") -> str:
        """
        验证并规范化封面图 URL。
        若为相对路径，自动结合 site_url 升级为公网绝对路径，彻底免疫 Dev.to 422 报错。
        """
        if not fm:
            return ""

        raw_cover = fm.get("cover") or fm.get("image") or fm.get("hero_image") or fm.get("main_image") or ""
        if not raw_cover or not isinstance(raw_cover, str):
            return ""

        raw_cover = raw_cover.strip()
        if raw_cover.startswith(('http://', 'https://')):
            return raw_cover

        # 相对路径补全为绝对路径
        if site_url:
            clean_rel = raw_cover.lstrip('./').lstrip('/')
            return urljoin(site_url.rstrip('/') + '/', clean_rel)

        return ""

    @staticmethod
    def build_canonical_url(doc_id: str, slug: str, lang_code: str, site_url: str = "") -> str:
        """
        基于创作者独立站地址与文档语种构建全局唯一的 Canonical URL 原创物权声明。
        """
        if not site_url:
            return ""

        base = site_url.rstrip('/')
        clean_slug = (slug or doc_id.replace('\\', '/').split('/')[-1].split('.')[0]).strip('/')
        clean_lang = (lang_code or "").lower().strip()

        # 源语种或默认语种直接位于根路径，非默认语种追加前缀
        if clean_lang in ("zh", "zh-hans", "auto", "default", ""):
            return f"{base}/{clean_slug}.html"
        return f"{base}/{clean_lang}/{clean_slug}.html"
