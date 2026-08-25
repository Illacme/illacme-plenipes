# -*- coding: utf-8 -*-
"""Illacme-plenipes Core - SQLite Maintenance Mixin
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10] 从 sqlite_backend.py 纵切分离。
职责：文档指纹清理、AI 生成元数据清空、全库清空等维护操作。
"""
import json


class SQLiteMaintenanceMixin:
    """🧹 数据库维护操作 Mixin — 通过 MRO 继承 self._get_conn()"""

    def clear_fingerprints_only(self):
        """⚡ [V106.0] 仅清空文档指纹记录，保留 AI Slug、SEO 元数据与译文记录"""
        with self._get_conn() as conn:
            conn.execute("UPDATE documents SET source_hash = NULL, shadow_hash = NULL")

    def clear_ai_metadata(self, mode="all"):
        """🏷️ [V106.0] 清空 AI 生成的 Slug 与 SEO 元数据"""
        with self._get_conn() as conn:
            if mode in ("all", "slug"):
                conn.execute("UPDATE documents SET slug = NULL")
            if mode in ("all", "seo"):
                rows = conn.execute("SELECT rel_path, metadata_json FROM documents").fetchall()
                for row in rows:
                    rel_path = row[0]
                    try:
                        meta = json.loads(row[1] or "{}")
                        if isinstance(meta, dict) and "seo_data" in meta:
                            meta.pop("seo_data", None)
                            conn.execute("UPDATE documents SET metadata_json = ? WHERE rel_path = ?", (json.dumps(meta), rel_path))
                    except Exception: pass

    def clear_all_documents(self):
        """🗑️ [V105.0] 彻底清空所有文档记录、指纹与多语言译文账本"""
        with self._get_conn() as conn:
            conn.execute("DELETE FROM documents")
            conn.execute("DELETE FROM translations")
