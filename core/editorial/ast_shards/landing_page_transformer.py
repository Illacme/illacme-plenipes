#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AST Shards: Landing Page Transformer (首页通告化转换器)
职责：当广播首页等非标准文章时，智能将其转换为格式优雅的“项目发布与全景指南”博客通告。
🛡️ [SOP-01] 物理行数保持在 300 行以内。
"""

import re
from typing import Dict, Any

class LandingPageTransformer:
    """🚀 [V121.0] 站点首页营销组件转 GFM 结构化转换器"""

    @staticmethod
    def is_landing_page(slug: str, fm: Dict[str, Any] = None) -> bool:
        """判定文档是否为站点首页或非博客类通用页面"""
        clean_slug = (slug or "").lower().strip()
        if clean_slug in ("index", "home", ""):
            return True
        if fm and isinstance(fm, dict):
            if fm.get("layout") == "page" and "home" in str(fm.get("tags", [])).lower():
                return True
        return False

    @staticmethod
    def transform_hero_components(content: str, title: str = "", site_url: str = "") -> str:
        """
        将复杂的前端卡片 (如 stats-matrix, stat-card, hero-cta-group) 优雅规约为 GFM 引用与列表。
        """
        if not content:
            return content

        t = content

        # 1. 提取 stat-card 数据卡片，转为精美的引用块
        # 匹配 <div class="stat-card">...<div>标签</div><div>数值</div>...</div>
        card_pattern = re.compile(
            r'<div\s+class=["\']stat-card["\'][^>]*>.*?<div[^>]*>(.*?)</div>.*?<div[^>]*>(.*?)</div>.*?</div>',
            re.IGNORECASE | re.DOTALL
        )

        cards = []
        for match in card_pattern.finditer(t):
            label = re.sub(r'<[^>]+>', '', match.group(1)).strip()
            val = re.sub(r'<[^>]+>', '', match.group(2)).strip()
            if label or val:
                cards.append(f"> - **{label}**: {val}")

        if cards:
            cards_block = "\n".join(cards)
            # 替换掉包含 stats-matrix 的大容器
            t = re.sub(
                r'<div\s+class=["\']stats-matrix["\'][^>]*>.*?</div>\s*</div>',
                f"\n\n### 📊 核心指标与架构特性\n\n{cards_block}\n\n",
                t,
                flags=re.IGNORECASE | re.DOTALL
            )

        # 2. 规约 CTA 按钮群 (hero-cta-group)
        t = re.sub(r'<div\s+class=["\']hero-cta-group["\'][^>]*>', '\n\n', t, flags=re.IGNORECASE)

        # 3. 底部追加官方资源指引卡片
        if site_url:
            canonical_home = site_url.rstrip('/')
            docs_entry = f"{canonical_home}/docs/quick-start.html"
            cta_footer = (
                f"\n\n---\n\n"
                f"### 🔗 官方资源直达\n\n"
                f"- [⚡ 快速上手官方文档]({docs_entry})\n"
                f"- [🌐 访问全息私人出版独立站]({canonical_home})\n"
            )
            # 避免重复追加
            if "### 🔗 官方资源直达" not in t:
                t = t.rstrip() + cta_footer

        return t
