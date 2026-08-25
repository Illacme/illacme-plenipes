# -*- coding: utf-8 -*-
"""Illacme-plenipes Core - SQLite Syndication Mixin
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10] 从 sqlite_backend.py 纵切分离。
职责：社媒分发异步重试队列 CRUD + 全渠道文章生命周期物权记录表 CRUD。
"""
import json
import time


class SQLiteSyndicationMixin:
    """📡 社媒分发队列与物权记录 Mixin — 通过 MRO 继承 self._get_conn()"""

    # 🆕 多渠道分发异步重试队列数据库操作
    def upsert_syndication_queue(self, rel_path, target_id, title, slug, content, metadata_json, lang_code, error_msg):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO syndication_queue (
                    rel_path, target_id, title, slug, content, metadata_json, lang_code, last_error, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
                ON CONFLICT(rel_path, target_id) DO UPDATE SET
                    title=excluded.title, slug=excluded.slug, content=excluded.content,
                    metadata_json=excluded.metadata_json, lang_code=excluded.lang_code,
                    last_error=excluded.last_error, status='PENDING'
            """, (rel_path, target_id, title, slug, content, json.dumps(metadata_json or {}), lang_code, error_msg))

    def get_pending_syndication_tasks(self):
        now = int(time.time())
        rows = self._get_conn().execute("""
            SELECT * FROM syndication_queue
            WHERE status = 'PENDING' AND next_retry_time <= ? AND retry_count < max_retries
        """, (now,)).fetchall()
        return [{**dict(r), "metadata": json.loads(dict(r).get("metadata_json") or "{}")} for r in rows]

    def mark_syndication_success(self, rel_path, target_id):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM syndication_queue WHERE rel_path = ? AND target_id = ?", (rel_path, target_id))

    def mark_syndication_failure(self, rel_path, target_id, error_msg, backoff_seconds):
        now = int(time.time())
        next_retry = now + backoff_seconds
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE syndication_queue
                SET retry_count = retry_count + 1, last_error = ?, next_retry_time = ?,
                    status = CASE WHEN retry_count + 1 >= max_retries THEN 'FAILED' ELSE 'PENDING' END
                WHERE rel_path = ? AND target_id = ?
            """, (error_msg, next_retry, rel_path, target_id))

    def list_all_syndication_tasks(self):
        rows = self._get_conn().execute("SELECT * FROM syndication_queue ORDER BY id DESC").fetchall()
        return [{**dict(r), "metadata": json.loads(dict(r).get("metadata_json") or "{}")} for r in rows]

    def retry_syndication_task(self, rel_path=None, target_id=None):
        with self._get_conn() as conn:
            if rel_path and target_id:
                conn.execute("""
                    UPDATE syndication_queue
                    SET retry_count = 0, status = 'PENDING', next_retry_time = 0, last_error = NULL
                    WHERE rel_path = ? AND target_id = ?
                """, (rel_path, target_id))
            else:
                conn.execute("""
                    UPDATE syndication_queue
                    SET retry_count = 0, status = 'PENDING', next_retry_time = 0, last_error = NULL
                    WHERE status = 'FAILED'
                """)

    def delete_syndication_task(self, rel_path=None, target_id=None):
        with self._get_conn() as conn:
            if rel_path and target_id:
                conn.execute("DELETE FROM syndication_queue WHERE rel_path = ? AND target_id = ?", (rel_path, target_id))
            else:
                conn.execute("DELETE FROM syndication_queue WHERE status = 'FAILED'")

    def _normalize_paths_for_query(self, rel_path: str) -> tuple:
        """🚀 [V121.0] 双向路径归一化：消除带/不带 .md 及前导斜杠对物权账本查询的影响"""
        if not rel_path:
            return ("",)
        clean = rel_path.strip().lstrip('/')
        clean_no_md = clean[:-3] if clean.endswith('.md') else clean
        clean_md = clean_no_md + '.md'
        return tuple(set([
            rel_path,
            clean,
            clean_no_md,
            clean_md,
            f"/{clean}",
            f"/{clean_md}",
            f"/{clean_no_md}"
        ]))

    # 🚀 [V120.0] 全渠道文章生命周期物权记录表 CRUD 方法
    def save_syndication_record(self, rel_path: str, lang_code: str, target_id: str, remote_article_id: str, remote_url: str = None, content_hash: str = None):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO syndication_records (rel_path, lang_code, target_id, remote_article_id, remote_url, content_hash, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(rel_path, lang_code, target_id) DO UPDATE SET
                    remote_article_id=excluded.remote_article_id,
                    remote_url=excluded.remote_url,
                    content_hash=excluded.content_hash,
                    updated_at=CURRENT_TIMESTAMP
            """, (rel_path, lang_code, target_id, str(remote_article_id), remote_url, content_hash))

    def get_syndication_record(self, rel_path: str, lang_code: str, target_id: str) -> dict:
        candidates = self._normalize_paths_for_query(rel_path)
        placeholders = ','.join('?' * len(candidates))
        row = self._get_conn().execute(
            f"SELECT * FROM syndication_records WHERE rel_path IN ({placeholders}) AND lang_code = ? AND target_id = ?",
            (*candidates, lang_code, target_id)
        ).fetchone()
        return dict(row) if row else None

    def list_syndication_records_for_doc(self, rel_path: str, lang_code: str = None) -> list:
        candidates = self._normalize_paths_for_query(rel_path)
        placeholders = ','.join('?' * len(candidates))
        if lang_code:
            rows = self._get_conn().execute(
                f"SELECT * FROM syndication_records WHERE rel_path IN ({placeholders}) AND lang_code = ?",
                (*candidates, lang_code)
            ).fetchall()
        else:
            rows = self._get_conn().execute(
                f"SELECT * FROM syndication_records WHERE rel_path IN ({placeholders})",
                candidates
            ).fetchall()
        return [dict(r) for r in rows]

    def delete_syndication_record(self, rel_path: str, lang_code: str, target_id: str):
        candidates = self._normalize_paths_for_query(rel_path)
        placeholders = ','.join('?' * len(candidates))
        with self._get_conn() as conn:
            conn.execute(
                f"DELETE FROM syndication_records WHERE rel_path IN ({placeholders}) AND lang_code = ? AND target_id = ?",
                (*candidates, lang_code, target_id)
            )
