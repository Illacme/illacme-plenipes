# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Image Hub Facade
职责：图像创作管理核心业务总门面。
特性：
1. 统一调度封面智能解析、落盘缓存与物权记录登记；
2. 跨模块支撑：社媒分发抽屉即时覆盖、微信封面兜底、独立站 OG 渲染；
3. 为后续图像资产库、海报导出与多图文分发预留物权插槽；
🛡️ [SOP-01] 物理行数保持在 300 行以内。
"""

import os
import time
import hashlib
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.cover_engine.cover_resolver import CoverResolver

class ImageHub:
    """图像创作管理业务中枢门面"""

    def __init__(self, vault_root: str = "", cache_dir: str = ""):
        self.vault_root = vault_root or os.getcwd()
        self.cache_dir = cache_dir or os.path.join(self.vault_root, ".plenipes", "cache", "covers")
        os.makedirs(self.cache_dir, exist_ok=True)

    def generate_cover_for_document(
        self,
        doc_id: str,
        title: str,
        slug: str = "",
        author: str = "Illacme Plenipes",
        category: str = "Engineering",
        brand_id: str = "default",
        brand_name: str = "ILLACME SOVEREIGN",
        strategy: str = "auto",
        aspect_ratio: str = "16:9",
        offset: int = 0
    ) -> Tuple[str, bytes, str]:
        """
        为文档即时生成封面，并写入缓存目录。
        返回元组: (本地相对缓存路径, 图片二进制流, 实际生效的策略名)
        """
        clean_slug = slug or os.path.splitext(os.path.basename(doc_id))[0]
        img_bytes, used_strat = CoverResolver.resolve_cover(
            title=title,
            slug=clean_slug,
            author=author,
            category=category,
            brand_name=brand_name,
            brand_id=brand_id,
            strategy=strategy,
            aspect_ratio=aspect_ratio,
            offset=offset,
            doc_id=doc_id,
            vault_root=self.vault_root
        )

        # 基于文档内容、语种标题与策略计算稳定指纹
        hash_seed = f"{doc_id}_{clean_slug}_{used_strat}_{offset}_{aspect_ratio}_{title}"
        file_hash = hashlib.md5(hash_seed.encode("utf-8")).hexdigest()[:12]
        filename = f"cover_{file_hash}.jpg"
        save_path = os.path.join(self.cache_dir, filename)

        try:
            with open(save_path, "wb") as f:
                f.write(img_bytes)
            tlog.info(f"✨ [ImageHub] 封面已成功落盘缓存: {filename} (策略: {used_strat})")
        except Exception as e:
            tlog.error(f"🛑 [ImageHub] 封面写盘异常: {e}")

        rel_url = f"/api/design/assets/covers/{filename}"
        return rel_url, img_bytes, used_strat

    def record_visual_asset(
        self,
        meta_manager: Any,
        rel_path: str,
        asset_type: str,
        strategy: str,
        source_url: str = "",
        cdn_url: str = "",
        media_id: str = "",
        prompt: str = ""
    ) -> bool:
        """向 SQLite 记录视觉资产物权账本"""
        if not meta_manager or not hasattr(meta_manager, "sqlite") or not meta_manager.sqlite:
            return False
        try:
            conn = meta_manager.sqlite.get_connection()
            with conn:
                conn.execute(
                    """
                    INSERT INTO visual_assets (rel_path, asset_type, strategy, source_url, cdn_url, media_id, prompt)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (rel_path, asset_type, strategy, source_url, cdn_url, media_id, prompt)
                )
            tlog.info(f"📊 [ImageHub] 视觉资产物权已登记: {rel_path} -> {strategy} (MediaID: {media_id or 'N/A'})")
            return True
        except Exception as e:
            tlog.warning(f"⚠️ [ImageHub] 登记视觉资产异常 (非致命): {e}")
            return False

# 全局单例
image_hub = ImageHub()
