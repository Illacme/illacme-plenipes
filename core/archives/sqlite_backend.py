# -*- coding: utf-8 -*-
"""Illacme-plenipes Core - SQLite Persistence Backend
🛡️ [V48.3 Refactored]"""
import sqlite3
import json
import threading
import os
import time
from core.utils.tracing import tlog
from .sql_statements import INIT_SCHEMA, UPSERT_DOC, UPSERT_TRANS
from .sqlite_review import SQLiteReviewMixin

class SQLiteBackend(SQLiteReviewMixin):
    """🚀 [V48.3] 工业级元数据存储方案"""
    
    def __init__(self, db_path, engine=None):
        self.db_path = os.path.abspath(os.path.expanduser(db_path))
        self.engine = engine
        self._local = threading.local()
        self._db_lock = threading.RLock()
        self._log_warned_truncate = False
        
        # 🚀 [V100.6] 进程内串行化包装，确保多线程下访问 SQLite 串行进行以防止挂载盘锁冲突
        self._wrap_db_methods()
        
        # 🛡️ [V35.2] 物理加固：确保数据库父目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _wrap_db_methods(self):
        for attr_name in dir(self):
            if attr_name.startswith('_') or attr_name in ('db_path', 'engine'):
                continue
            attr_val = getattr(self, attr_name)
            if callable(attr_val):
                setattr(self, attr_name, self._wrap_method(attr_val))

    def _wrap_method(self, method):
        def wrapper(*args, **kwargs):
            with self._db_lock:
                return method(*args, **kwargs)
        return wrapper

    def _get_conn(self):
        if not hasattr(self._local, "conn"):
            timeout = getattr(self.engine.config.system.resilience, 'db_timeout', 30.0) if self.engine else 30.0
            self._local.conn = sqlite3.connect(self.db_path, timeout=timeout, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
            try:
                # 🚀 [V100.5] 挂载卷/网络共享盘跨平台兼容：停用 WAL 模式以防止 disk I/O error
                db_dir = os.path.abspath(self.db_path)
                is_mounted = any(db_dir.startswith(p) for p in ['/Volumes/', '/mnt/', '/media/', '\\\\'])
                
                # 针对 Windows 进一步检测映射的网络驱动器 (DRIVE_REMOTE=4) 或可移动U盘 (DRIVE_REMOVABLE=2)
                if not is_mounted and os.name == 'nt':
                    try:
                        import ctypes
                        drive = os.path.splitdrive(db_dir)[0] + "\\"
                        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
                        if drive_type in (2, 4):  # 2: DRIVE_REMOVABLE, 4: DRIVE_REMOTE
                            is_mounted = True
                    except:
                        pass

                if is_mounted:
                    self._local.conn.execute("PRAGMA journal_mode=TRUNCATE")
                    self._local.conn.execute("PRAGMA synchronous=FULL")
                    if not getattr(self, '_log_warned_truncate', False):
                        tlog.info(f"🗄️ [SQLite] 检测到挂载卷或网络共享路径 {self.db_path}，已自动切换至 TRUNCATE 兼容模式并开启同步保护")
                        self._log_warned_truncate = True
                else:
                    self._local.conn.execute("PRAGMA journal_mode=WAL")
                    self._local.conn.execute("PRAGMA synchronous=NORMAL")
            except Exception as e:
                tlog.warning(f"⚠️ [SQLite] 无法配置 journal_mode: {e}")
        return self._local.conn

    def _init_db(self):
        conn = self._get_conn()
        with conn:
            for sql in INIT_SCHEMA: conn.execute(sql)
            
            # 🚀 [V50.3] 自动迁移：确保 usage_ledger 包含 imprint_id
            try:
                cursor = conn.execute("PRAGMA table_info(usage_ledger)")
                columns = [row[1] for row in cursor.fetchall()]
                if columns and "imprint_id" not in columns:
                    tlog.warning("🛰️ [SQLite] 检测到旧版账本，正在执行物理迁移 (Add imprint_id)...")
                    conn.execute("ALTER TABLE usage_ledger ADD COLUMN imprint_id TEXT")
            except Exception as e:
                tlog.error(f"❌ [SQLite] 自动迁移失败: {e}")
                
        tlog.debug(f"🗄️ [SQLite] 后端初始化完成: {self.db_path}")

    def upsert_document(self, rel_path, data):
        conn = self._get_conn()
        with conn:
            indexed = ["title", "slug", "source_hash", "shadow_hash", "route_prefix", "route_source", "sub_dir", "persistent_date"]
            main = {k: (data or {}).get(k) for k in indexed}
            other = {k: v for k, v in (data or {}).items() if k not in indexed and k != "translations"}
            
            conn.execute(UPSERT_DOC, (
                rel_path, main.get("title"), main.get("slug"), main.get("source_hash"), main.get("shadow_hash"),
                main.get("route_prefix"), main.get("route_source"), main.get("sub_dir"), main.get("persistent_date"),
                json.dumps(other)
            ))
            
            if "translations" in (data or {}):
                for lang, res in (data.get("translations") or {}).items():
                    conn.execute(UPSERT_TRANS, (rel_path, lang, "DONE", json.dumps(res)))

    def upsert_asset(self, asset_hash, metadata):
        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT INTO asset_registry (asset_hash, metadata_json, last_seen)
                VALUES (?, ?, ?)
                ON CONFLICT(asset_hash) DO UPDATE SET
                    metadata_json=excluded.metadata_json, last_seen=excluded.last_seen
            """, (asset_hash, json.dumps(metadata), int(time.time())))

    def get_asset(self, asset_hash):
        row = self._get_conn().execute("SELECT metadata_json FROM asset_registry WHERE asset_hash = ?", (asset_hash,)).fetchone()
        return json.loads(dict(row).get("metadata_json")) if row else None

    def upsert_dir_slug(self, raw_dir, slug):
        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT INTO dir_index (raw_dir, slug)
                VALUES (?, ?)
                ON CONFLICT(raw_dir) DO UPDATE SET slug=excluded.slug
            """, (raw_dir, slug))

    def get_dir_slugs(self):
        rows = self._get_conn().execute("SELECT * FROM dir_index").fetchall()
        return {dict(r).get("raw_dir"): dict(r).get("slug") for r in rows}

    def get_document(self, rel_path):
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM documents WHERE rel_path = ?", (rel_path,)).fetchone()
        if not row: return None
        data = dict(row)
        extra = json.loads(data.pop("metadata_json") or "{}")
        if "seo" in extra and "seo_data" not in extra:
            extra["seo_data"] = extra.pop("seo")
        data.update(extra)
        trans = conn.execute("SELECT lang_code, result_json FROM translations WHERE rel_path = ?", (rel_path,)).fetchall()
        data["translations"] = {dict(r).get("lang_code"): json.loads(dict(r).get("result_json")) for r in trans}
        return data

    def get_all_documents(self):
        conn = self._get_conn()
        main_rows = conn.execute("SELECT * FROM documents").fetchall()
        trans_rows = conn.execute("SELECT rel_path, lang_code, result_json FROM translations").fetchall()
        trans_map = {}
        for r in trans_rows:
            dr = dict(r)
            trans_map.setdefault(dr.get("rel_path"), {})[dr.get("lang_code")] = json.loads(dr.get("result_json"))
        results = {}
        for row in main_rows:
            dr = dict(row)
            rel_path = dr.get("rel_path")
            data = dict(row)
            extra = json.loads(data.pop("metadata_json") or "{}")
            if "seo" in extra and "seo_data" not in extra: extra["seo_data"] = extra.pop("seo")
            data.update(extra)
            data["translations"] = trans_map.get(rel_path, {})
            results[rel_path] = data
        return results

    def list_all_documents(self):
        return [dict(r).get("rel_path") for r in self._get_conn().execute("SELECT rel_path FROM documents").fetchall()]

    def find_by_hash(self, source_hash):
        row = self._get_conn().execute("SELECT rel_path FROM documents WHERE source_hash = ?", (source_hash,)).fetchone()
        return self.get_document(dict(row).get("rel_path")) if row else None

    def insert_usage_record(self, imprint_id, event_type, description, cost, metadata):
        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT INTO usage_ledger (imprint_id, event_type, description, cost, metadata_json)
                VALUES (?, ?, ?, ?, ?)
            """, (imprint_id, event_type, description, cost, json.dumps(metadata)))

    def get_total_cost(self, imprint_id):
        row = self._get_conn().execute("SELECT SUM(cost) FROM usage_ledger WHERE imprint_id = ?", (imprint_id,)).fetchone()
        return row[0] if row and row[0] is not None else 0.0
    def list_documents_paginated(self, page=1, limit=20, query=None, folder=None):
        offset = (page - 1) * limit
        sql = "SELECT * FROM documents"
        params = []
        
        conditions = []
        if query:
            conditions.append("(title LIKE ? OR rel_path LIKE ? OR slug LIKE ?)")
            p = f"%{query}%"
            params.extend([p, p, p])
            
        if folder:
            conditions.append("rel_path LIKE ?")
            params.append(f"{folder}/%")
            
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
            
        sql += " ORDER BY last_updated DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        rows = self._get_conn().execute(sql, params).fetchall()
        
        # 批量获取 translations 和 translation_reviews (Q6=B)
        t_map = {}
        if rows:
            paths = [row["rel_path"] for row in rows]
            placeholders = ",".join(["?"] * len(paths))
            
            # 1. 翻译状态
            t_rows = self._get_conn().execute(
                f"SELECT rel_path, lang_code, status FROM translations WHERE rel_path IN ({placeholders})", paths
            ).fetchall()
            for tr in t_rows:
                rp, lc, st = tr["rel_path"], tr["lang_code"], tr["status"]
                if rp not in t_map: t_map[rp] = {}
                t_map[rp][lc] = {"status": st, "human_approved": False, "review_is_stale": False}
                
            # 2. 人工校对锁
            r_rows = self._get_conn().execute(
                f"SELECT doc_id, lang_code, is_stale FROM translation_reviews WHERE doc_id IN ({placeholders})", paths
            ).fetchall()
            for rr in r_rows:
                rp, lc, stale = rr["doc_id"], rr["lang_code"], rr["is_stale"]
                if rp not in t_map: t_map[rp] = {}
                if lc not in t_map[rp]: t_map[rp][lc] = {"status": "DONE"}
                t_map[rp][lc]["human_approved"] = True
                t_map[rp][lc]["review_is_stale"] = bool(stale)

        results = []
        for row in rows:
            data = dict(row)
            extra = json.loads(data.pop("metadata_json") or "{}")
            data.update(extra)
            # 注入 translations 字段供前端 Vault 判断
            data["translations"] = t_map.get(data["rel_path"], {})
            results.append(data)
        return results

    def update_document_metadata(self, rel_path, metadata_updates):
        """🚀 [V52.0] 局部元数据注入：仅更新 metadata_json 中的特定字段"""
        conn = self._get_conn()
        with conn:
            row = conn.execute("SELECT metadata_json FROM documents WHERE rel_path = ?", (rel_path,)).fetchone()
            if not row: return False

            # 🛡️ [Slug 唯一性守卫] 如果本次更新包含 slug，先做全库冲突检测。
            # slug 是路由层面的唯一标识符（直接映射为 URL 路径），
            # 两个不同物理路径的文档若共享同一 slug，会导致静态站点路由冲突、
            # SEO 索引混乱，以及译文缓存命中错误文档等严重问题。
            if "slug" in metadata_updates:
                new_slug = metadata_updates["slug"]
                conflict_row = conn.execute(
                    "SELECT rel_path FROM documents WHERE slug = ? AND rel_path != ?",
                    (new_slug, rel_path)
                ).fetchone()
                if conflict_row:
                    conflict_path = dict(conflict_row).get("rel_path", "?")
                    return {"conflict": True, "slug": new_slug, "occupied_by": conflict_path}

            existing_meta = json.loads(dict(row).get("metadata_json") or "{}")
            existing_meta.update(metadata_updates)

            # 如果更新中包含 title 或 slug，也同步更新主表字段
            if "title" in metadata_updates:
                conn.execute("UPDATE documents SET title = ?, metadata_json = ? WHERE rel_path = ?",
                           (metadata_updates["title"], json.dumps(existing_meta), rel_path))
            elif "slug" in metadata_updates:
                 conn.execute("UPDATE documents SET slug = ?, metadata_json = ? WHERE rel_path = ?",
                           (metadata_updates["slug"], json.dumps(existing_meta), rel_path))
            else:
                conn.execute("UPDATE documents SET metadata_json = ? WHERE rel_path = ?",
                           (json.dumps(existing_meta), rel_path))
            return True


    def get_documents_count_filtered(self, query=None, folder=None):
        sql = "SELECT COUNT(*) FROM documents"
        params = []
        conditions = []
        if query:
            conditions.append("(title LIKE ? OR rel_path LIKE ? OR slug LIKE ?)")
            p = f"%{query}%"
            params.extend([p, p, p])
        if folder:
            conditions.append("rel_path LIKE ?")
            params.append(f"{folder}/%")
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        res = self._get_conn().execute(sql, params).fetchone()
        return res[0] if res else 0

    def get_total_documents_count(self):
        res = self._get_conn().execute("SELECT COUNT(*) FROM documents").fetchone()
        return res[0] if res else 0

    def delete_document(self, rel_path):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM documents WHERE rel_path = ?", (rel_path,))
            conn.execute("DELETE FROM translations WHERE rel_path = ?", (rel_path,))

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
