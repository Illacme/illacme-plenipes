# -*- coding: utf-8 -*-
"""
🎨 Bindery Asset Syncer (装订工坊媒体资产物权同步中枢)
职责：将装订工坊自定义上传的封面图片统一归拢落盘至设计中心媒体资产库，并自动登记至 SQLite 物权账本。
规范：遵循 SOP-01 规范，纯 Python 极简优雅架构，单文件行数严格 ≤ 300 行。
"""

import os
import hashlib
import base64
from typing import Optional, Any
from core.utils.tracing import tlog


class BinderyAssetSyncer:
    """装订工坊与设计中心媒体资产同步器"""

    @classmethod
    def sync_custom_cover(
        cls,
        custom_cover_data: str,
        vault_dir: str,
        slug_prefix: str,
        out_dir: str = "dist/books",
        engine: Optional[Any] = None,
        book_title: str = "出版典籍"
    ) -> Optional[str]:
        """
        解码自定义封面数据，落盘到 dist/books 导出目录，
        同时同步归拢至设计中心媒体资产目录 (.plenipes/cache/covers/) 并登记至 SQLite 物权账本。
        """
        if not custom_cover_data:
            return None

        raw_bytes = None
        ext = ".png"

        # 1. 尝试从 DataURI 解码二进制流
        if custom_cover_data.startswith("data:image/"):
            try:
                hdr, b64 = custom_cover_data.split(",", 1)
                ext = ".jpg" if ("jpeg" in hdr or "jpg" in hdr) else (".webp" if "webp" in hdr else ".png")
                raw_bytes = base64.b64decode(b64)
            except Exception as e:
                tlog.warning(f"⚠️ [BinderySyncer] 自定义封面 DataURI 解码失败: {e}")
                return None
        elif os.path.isfile(custom_cover_data):
            try:
                with open(custom_cover_data, "rb") as f:
                    raw_bytes = f.read()
                _, src_ext = os.path.splitext(custom_cover_data)
                if src_ext:
                    ext = src_ext.lower()
            except Exception as e:
                tlog.warning(f"⚠️ [BinderySyncer] 读取自定义封面文件失败: {e}")
                return None
        else:
            return None

        if not raw_bytes:
            return None

        # 2. 写入书籍装订产物本地目录 (如 dist/books/cover_xxx_custom.png)
        os.makedirs(out_dir, exist_ok=True)
        local_cover_file = os.path.join(out_dir, f"cover_{slug_prefix}_custom{ext}")
        try:
            with open(local_cover_file, "wb") as f:
                f.write(raw_bytes)
        except Exception as e:
            tlog.warning(f"⚠️ [BinderySyncer] 写入 dist/books 封面异常: {e}")

        # 3. 统一同步落盘至设计中心媒体资产库 (.plenipes/cache/covers/)
        try:
            content_hash = hashlib.sha256(raw_bytes).hexdigest()[:12]
            stored_filename = f"upload_bindery_{slug_prefix}_{content_hash}{ext}"
            v_dir = vault_dir or (getattr(engine, "vault_root", None) if engine else None) or os.getcwd()
            covers_dir = os.path.join(v_dir, ".plenipes", "cache", "covers")
            os.makedirs(covers_dir, exist_ok=True)
            media_asset_path = os.path.join(covers_dir, stored_filename)

            with open(media_asset_path, "wb") as f:
                f.write(raw_bytes)

            source_url = f"/api/design/assets/covers/{stored_filename}"
            rel_path = f".plenipes/cache/covers/{stored_filename}"
            prompt_text = f"装订工坊自定义封面: {book_title}"

            # 4. 登记至 SQLite 物权账本 (visual_assets 表)
            cls.register_visual_asset(engine, rel_path, source_url, prompt_text)
            tlog.info(f"✨ [BinderySyncer] 自定义封面已成功归拢至设计中心媒体资产库: {stored_filename}")
        except Exception as e:
            tlog.warning(f"⚠️ [BinderySyncer] 同步媒体资产库异常 (非致命): {e}")

        return os.path.abspath(local_cover_file)

    @classmethod
    def register_visual_asset(
        cls,
        engine: Optional[Any],
        rel_path: str,
        source_url: str,
        prompt_text: str
    ) -> bool:
        """登记视觉资产物权记录至 SQLite 账本"""
        if not engine:
            try:
                from core.runtime.engine_singleton import get_global_engine
                engine = get_global_engine()
            except Exception:
                pass

        if not engine or not hasattr(engine, "meta") or not getattr(engine.meta, "sqlite", None):
            return False

        try:
            conn = engine.meta.sqlite.get_connection()
            with conn:
                cur = conn.cursor()
                # 检查是否已存在同路径或同 URL 的资产记录，避免重复写入
                cur.execute(
                    "SELECT id FROM visual_assets WHERE rel_path = ? OR source_url = ?",
                    (rel_path, source_url)
                )
                existing = cur.fetchone()
                if not existing:
                    cur.execute(
                        """
                        INSERT INTO visual_assets (rel_path, asset_type, strategy, source_url, cdn_url, media_id, prompt)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (rel_path, "cover", "bindery_upload", source_url, "", "", prompt_text)
                    )
                    tlog.info(f"📊 [BinderySyncer] 媒体资产账本登记完成: #{cur.lastrowid} -> {rel_path}")
            return True
        except Exception as e:
            tlog.warning(f"⚠️ [BinderySyncer] 登记 SQLite 视觉资产账本异常: {e}")
            return False
