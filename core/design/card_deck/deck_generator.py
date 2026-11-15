# -*- coding: utf-8 -*-
"""
⚙️ CardDeck Core - Multi-Ratio Deck Batch Generator & Packaging Hub
职责：知识卡片切片调度、批量多画幅渲染 (3:4 / 1:1 / 16:9)、磁盘持久化与 ZIP 打包中枢。
特性：
1. 统一协调 segmenter 与 renderer；
2. 缓存按画幅物理隔离落地于 .plenipes/cache/cards/{slug}_{ratio}/；
3. 自动生成多画幅卡片 ZIP 归档包；
4. 严格防目录穿越与防超大并发；
🛡️ [SOP-01] 物理行数保持在 300 行以内。
"""

import os
import io
import zipfile
from typing import List, Dict, Any, Optional
from core.utils.tracing import tlog
from .deck_segmenter import DeckSegmenter, DeckCardData
from .deck_card_renderer import render_deck_card


class DeckGenerator:
    """卡片海报生成器中枢"""

    @classmethod
    def generate_deck(
        cls,
        content: str,
        slug: str,
        metadata: Optional[Dict[str, Any]] = None,
        offset: int = 0,
        max_cards: int = 6,
        aspect_ratio: str = "3:4",
        vault_root: str = "",
        cache_base_dir: str = ""
    ) -> Dict[str, Any]:
        """
        完整执行文章切片、批量生成卡片并落盘。
        支持 3:4 (900x1200), 1:1 (1080x1080), 16:9 (1200x675)
        """
        meta = metadata or {}
        safe_slug = "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in (slug or "card_deck")])
        if not safe_slug:
            safe_slug = "card_deck"

        clean_ratio = str(aspect_ratio or "3:4").strip().lower()
        if clean_ratio not in ("3:4", "1:1", "16:9"):
            clean_ratio = "3:4"
        ratio_tag = clean_ratio.replace(":", "x")

        # 1. 确定落盘根目录与画幅隔离目录
        base_dir = cache_base_dir
        if not base_dir:
            root = vault_root or os.getcwd()
            base_dir = os.path.join(root, ".plenipes", "cache", "cards")

        dir_name = f"{safe_slug}_{ratio_tag}"
        target_dir = os.path.join(base_dir, dir_name)
        os.makedirs(target_dir, exist_ok=True)

        # 2. 文本结构智能切片
        cards_data: List[DeckCardData] = DeckSegmenter.segment_document(
            content=content,
            metadata=meta,
            max_cards=max_cards
        )

        rendered_cards: List[Dict[str, Any]] = []
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for c_data in cards_data:
                try:
                    # 3. 逐张渲染为指定画幅 JPEG
                    img_bytes = render_deck_card(c_data, offset=offset, aspect_ratio=clean_ratio)
                    filename = f"card_{c_data.index:02d}.jpg"
                    file_path = os.path.join(target_dir, filename)

                    with open(file_path, "wb") as f:
                        f.write(img_bytes)

                    zf.writestr(filename, img_bytes)

                    rel_url = f"/api/design/assets/cards/{dir_name}/{filename}"
                    rendered_cards.append({
                        "index": c_data.index,
                        "total": c_data.total,
                        "card_type": c_data.card_type,
                        "title": c_data.title,
                        "subtitle": c_data.subtitle,
                        "url": rel_url,
                        "filename": filename,
                        "aspect_ratio": clean_ratio
                    })
                except Exception as e:
                    tlog.warning(f"⚠️ [CardDeck] 渲染卡片 0{c_data.index} 异常: {e}")

        # 4. 保存 ZIP 归档文件
        zip_filename = f"deck_{safe_slug}_{ratio_tag}.zip"
        zip_path = os.path.join(target_dir, zip_filename)
        with open(zip_path, "wb") as f:
            f.write(zip_buffer.getvalue())

        zip_url = f"/api/design/assets/cards/{dir_name}/{zip_filename}"
        tlog.info(f"✨ [CardDeck] 成功批量生成 {len(rendered_cards)} 张 {clean_ratio} 知识卡片海报: {dir_name}")

        return {
            "status": "ok",
            "slug": safe_slug,
            "aspect_ratio": clean_ratio,
            "dir_name": dir_name,
            "total": len(rendered_cards),
            "zip_url": zip_url,
            "zip_filename": zip_filename,
            "cards": rendered_cards
        }
