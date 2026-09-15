# -*- coding: utf-8 -*-
"""
🎨 CoverEngine Core - Cover Resolver & Strategy Dispatcher
职责：封面策略解析器与阶梯自愈调度中枢。
特性：
1. 统一调度 5 大策略：og_card, brand_presets, minimal_badge, unsplash, ai_generator；
2. 智能阶梯回退链 (Auto Fallback Pipeline)：出现任何异常毫秒级自愈兜底；
3. 输出合规的二进制图片与元数据；
🛡️ [SOP-01] 物理行数保持在 300 行以内。
"""

import os
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from .og_card_renderer import render_og_card
from .brand_presets_rotator import resolve_brand_preset_cover
from .minimal_badge_renderer import render_minimal_badge
from .first_image_extractor import extract_first_image_from_doc
from .ai_cover_generator import generate_ai_cover

class CoverResolver:
    """智能封面策略解析与分发供给中枢"""

    @staticmethod
    def resolve_cover(
        title: str,
        slug: str = "",
        author: str = "Illacme Plenipes",
        category: str = "Technology",
        brand_name: str = "ILLACME SOVEREIGN",
        brand_id: str = "default",
        strategy: str = "auto",
        aspect_ratio: str = "16:9",
        offset: int = 0,
        doc_id: str = "",
        vault_root: str = ""
    ) -> Tuple[bytes, str]:
        """
        根据指定策略或智能阶梯生成封面图片。
        返回元组: (图片二进制字节流, 实际生效的策略标识)
        """
        clean_strategy = (strategy or "auto").lower().strip()
        tlog.info(f"🎨 [CoverEngine] 启动封面供给解析: {clean_strategy} (文档: {slug or title})")

        # ── 1. 正文首图优先提取模式 ────────────────────────────────────
        if clean_strategy in ("first_image", "content_first", "first"):
            try:
                data = extract_first_image_from_doc(
                    doc_id=doc_id or slug,
                    vault_root=vault_root,
                    aspect_ratio=aspect_ratio
                )
                if data:
                    return data, "first_image"
                tlog.info("ℹ️ [CoverEngine] 正文未提取到图片，平滑进入自愈回退")
            except Exception as e:
                tlog.warning(f"⚠️ [CoverEngine] 正文首图提取异常，启动自愈回退: {e}")

        # ── 2. AI 智能生图模式 ─────────────────────────────────────────
        if clean_strategy in ("ai_generation", "ai_generator", "ai"):
            try:
                res = generate_ai_cover(
                    title=title,
                    category=category,
                    aspect_ratio=aspect_ratio,
                    offset=offset
                )
                if res and res[0]:
                    return res[0], res[1]
                tlog.info("ℹ️ [CoverEngine] AI 生图未返回有效内容，平滑进入自愈回退")
            except Exception as e:
                tlog.warning(f"⚠️ [CoverEngine] AI 生图发生异常，启动自愈回退: {e}")

        # ── 3. 动态 OG 技术卡片模式 ────────────────────────────────────
        if clean_strategy in ("og_card", "og", "card"):
            try:
                data = render_og_card(
                    title=title,
                    author=author,
                    category=category,
                    brand_name=brand_name,
                    aspect_ratio=aspect_ratio,
                    offset=offset
                )
                if data:
                    return data, "og_card"
            except Exception as e:
                tlog.warning(f"⚠️ [CoverEngine] OG 卡片渲染失败，启动自愈回退: {e}")

        # ── 4. 品牌母本图库轮巡模式 ────────────────────────────────────
        if clean_strategy in ("brand_presets", "presets", "preset"):
            try:
                data = resolve_brand_preset_cover(
                    doc_id=doc_id or slug,
                    slug=slug,
                    brand_id=brand_id,
                    offset=offset,
                    vault_root=vault_root
                )
                if data:
                    return data, "brand_presets"
            except Exception as e:
                tlog.warning(f"⚠️ [CoverEngine] 品牌母本挑选失败，启动自愈回退: {e}")

        # ── 5. 极简首字徽章模式 ────────────────────────────────────────
        if clean_strategy in ("minimal_badge", "badge", "minimal"):
            try:
                data = render_minimal_badge(
                    title=title,
                    brand_name=brand_name,
                    aspect_ratio=aspect_ratio,
                    offset=offset
                )
                if data:
                    return data, "minimal_badge"
            except Exception as e:
                tlog.warning(f"⚠️ [CoverEngine] 极简徽章渲染失败，启动自愈回退: {e}")

        # ── 6. 智能阶梯自愈链 (Auto Fallback) ───────────────────────────
        # 阶梯 1: 尝试动态 OG 卡片 (携带 offset 配色轮巡)
        try:
            data = render_og_card(
                title=title,
                author=author,
                category=category,
                brand_name=brand_name,
                aspect_ratio=aspect_ratio,
                offset=offset
            )
            if data:
                return data, "og_card"
        except Exception as e:
            tlog.warning(f"⚠️ [CoverEngine-Auto] 阶梯 1 (OG) 失败: {e}")

        # 阶梯 2: 尝试品牌母本轮巡
        try:
            data = resolve_brand_preset_cover(
                doc_id=doc_id or slug,
                slug=slug,
                brand_id=brand_id,
                offset=offset,
                vault_root=vault_root
            )
            if data:
                return data, "brand_presets"
        except Exception as e:
            tlog.warning(f"⚠️ [CoverEngine-Auto] 阶梯 2 (母本) 失败: {e}")

        # 阶梯 3: 极简徽章终极兜底
        return render_minimal_badge(title=title, brand_name=brand_name, aspect_ratio=aspect_ratio, offset=offset), "minimal_badge"
