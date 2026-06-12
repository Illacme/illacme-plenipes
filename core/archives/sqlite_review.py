# -*- coding: utf-8 -*-
"""Illacme-plenipes Core - SQLite Review Operations Mixin"""

class SQLiteReviewMixin:
    """🔒 [I5] 人工校对锁底层数据库操作 Mixin"""

    def upsert_review(self, imprint_id, doc_id, lang_code,
                      reviewed_body=None, reviewed_title=None, reviewed_desc=None,
                      source_hash=None, reviewed_by="commander"):
        """🔒 [I5] 语种级校对记录 UPSERT"""
        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT INTO translation_reviews
                    (imprint_id, doc_id, lang_code, reviewed_body, reviewed_title,
                     reviewed_desc, source_hash, is_stale, reviewed_at, reviewed_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP, ?)
                ON CONFLICT(imprint_id, doc_id, lang_code) DO UPDATE SET
                    reviewed_body=excluded.reviewed_body,
                    reviewed_title=excluded.reviewed_title,
                    reviewed_desc=excluded.reviewed_desc,
                    source_hash=excluded.source_hash,
                    is_stale=0,
                    reviewed_at=CURRENT_TIMESTAMP,
                    reviewed_by=excluded.reviewed_by
            """, (imprint_id, doc_id, lang_code, reviewed_body, reviewed_title,
                  reviewed_desc, source_hash, reviewed_by))

    def get_review(self, imprint_id, doc_id, lang_code):
        """🔒 [I5] 获取指定语种的校对记录"""
        row = self._get_conn().execute(
            """SELECT * FROM translation_reviews
               WHERE imprint_id=? AND doc_id=? AND lang_code=?""",
            (imprint_id, doc_id, lang_code)
        ).fetchone()
        return dict(row) if row else None

    def delete_review(self, imprint_id, doc_id, lang_code):
        """🗑️ [I5] 删除校对记录"""
        conn = self._get_conn()
        with conn:
            conn.execute(
                """DELETE FROM translation_reviews
                   WHERE imprint_id=? AND doc_id=? AND lang_code=?""",
                (imprint_id, doc_id, lang_code)
            )

    def mark_review_stale(self, imprint_id, doc_id, lang_code):
        """⚠️ [I5] 标记校对记录为 stale"""
        conn = self._get_conn()
        with conn:
            conn.execute(
                """UPDATE translation_reviews SET is_stale=1
                   WHERE imprint_id=? AND doc_id=? AND lang_code=?""",
                (imprint_id, doc_id, lang_code)
            )

    def list_reviews_for_doc(self, imprint_id, doc_id):
        """📋 [I5] 获取文档所有语种的校对状态汇总"""
        rows = self._get_conn().execute(
            """SELECT lang_code, reviewed_title, reviewed_desc, source_hash,
                      is_stale, reviewed_at, reviewed_by
               FROM translation_reviews
               WHERE imprint_id=? AND doc_id=?""",
            (imprint_id, doc_id)
        ).fetchall()
        return {dict(r)["lang_code"]: dict(r) for r in rows}
