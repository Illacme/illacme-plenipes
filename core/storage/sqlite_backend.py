# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SQLite Persistence Backend
模块职责：提供高性能的物理存储层。
🛡️ [V24.6 Refactored]：解耦后的轻量化持久化引擎。
"""
import sqlite3
import json
import threading
import os
import time
from core.utils.tracing import tlog
from .sql_statements import INIT_SCHEMA, UPSERT_DOC, UPSERT_TRANS

class SQLiteBackend:
    """🚀 [V24.6] 工业级元数据存储方案"""
    
    def __init__(self, db_path, engine=None):
        self.db_path = os.path.abspath(os.path.expanduser(db_path))
        self.engine = engine
        self._local = threading.local()
        self._init_db()

    def _get_conn(self):
        if not hasattr(self._local, "conn"):
            timeout = self.engine.config.system.resilience.db_timeout if self.engine else 30.0
            self._local.conn = sqlite3.connect(self.db_path, timeout=timeout, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
            try:
                self._local.conn.execute("PRAGMA journal_mode=WAL")
                self._local.conn.execute("PRAGMA synchronous=NORMAL")
            except: pass
        return self._local.conn

    def _init_db(self):
        conn = self._get_conn()
        with conn:
            for sql in INIT_SCHEMA: conn.execute(sql)
        tlog.debug(f"🗄️ [SQLite] 后端初始化完成: {self.db_path}")

    def upsert_document(self, rel_path, data):
        conn = self._get_conn()
        with conn:
            indexed = ["title", "slug", "source_hash", "shadow_hash", "route_prefix", "route_source", "sub_dir", "persistent_date"]
            main = {k: data.get(k) for k in indexed}
            other = {k: v for k, v in data.items() if k not in indexed and k != "translations"}
            
            conn.execute(UPSERT_DOC, (
                rel_path, main["title"], main["slug"], main["source_hash"], main["shadow_hash"],
                main["route_prefix"], main["route_source"], main["sub_dir"], main["persistent_date"],
                json.dumps(other)
            ))
            
            if "translations" in data:
                for lang, res in data["translations"].items():
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
        return json.loads(row["metadata_json"]) if row else None

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
        return {r["raw_dir"]: r["slug"] for r in rows}

    def get_document(self, rel_path):
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM documents WHERE rel_path = ?", (rel_path,)).fetchone()
        if not row: return None
        data = dict(row)
        extra = json.loads(data.pop("metadata_json") or "{}")
        # 🚀 [V16.7] 兼容性：如果旧版本存的是 'seo'，映射到新版的 'seo_data'
        if "seo" in extra and "seo_data" not in extra:
            extra["seo_data"] = extra.pop("seo")
        data.update(extra)
        trans = conn.execute("SELECT lang_code, result_json FROM translations WHERE rel_path = ?", (rel_path,)).fetchall()
        data["translations"] = {r["lang_code"]: json.loads(r["result_json"]) for r in trans}
        return data

    def get_all_documents(self):
        """🚀 [V16.8] 工业级性能优化：单次物理查询获取全量文档矩阵"""
        conn = self._get_conn()
        main_rows = conn.execute("SELECT * FROM documents").fetchall()
        trans_rows = conn.execute("SELECT rel_path, lang_code, result_json FROM translations").fetchall()
        trans_map = {}
        for r in trans_rows:
            trans_map.setdefault(r["rel_path"], {})[r["lang_code"]] = json.loads(r["result_json"])
        results = {}
        for row in main_rows:
            rel_path = row["rel_path"]
            data = dict(row)
            extra = json.loads(data.pop("metadata_json") or "{}")
            if "seo" in extra and "seo_data" not in extra: extra["seo_data"] = extra.pop("seo")
            data.update(extra)
            data["translations"] = trans_map.get(rel_path, {})
            results[rel_path] = data
        return results

    def list_all_documents(self):
        return [r["rel_path"] for r in self._get_conn().execute("SELECT rel_path FROM documents").fetchall()]

    def find_by_hash(self, source_hash):
        """🚀 [V23.0] 工业级哈希反查"""
        row = self._get_conn().execute("SELECT rel_path FROM documents WHERE source_hash = ?", (source_hash,)).fetchone()
        return self.get_document(row["rel_path"]) if row else None

    def insert_usage_record(self, workspace_id, event_type, description, cost, metadata):
        """🚀 [V23.0] 记录计费流水"""
        conn = self._get_conn()
        with conn:
            conn.execute("""
                INSERT INTO usage_ledger (workspace_id, event_type, description, cost, metadata_json)
                VALUES (?, ?, ?, ?, ?)
            """, (workspace_id, event_type, description, cost, json.dumps(metadata)))

    def get_total_cost(self, workspace_id):
        row = self._get_conn().execute("SELECT SUM(cost) FROM usage_ledger WHERE workspace_id = ?", (workspace_id,)).fetchone()
        return row[0] if row and row[0] is not None else 0.0

    def list_documents_paginated(self, page=1, limit=20):
        offset = (page - 1) * limit
        rows = self._get_conn().execute("SELECT * FROM documents ORDER BY last_updated DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
        results = []
        for row in rows:
            data = dict(row)
            extra = json.loads(data.pop("metadata_json") or "{}")
            data.update(extra)
            results.append(data)
        return results

    def get_total_documents_count(self):
        return self._get_conn().execute("SELECT COUNT(*) FROM documents").fetchone()[0]

    def delete_document(self, rel_path):
        conn = self._get_conn()
        with conn:
            conn.execute("DELETE FROM documents WHERE rel_path = ?", (rel_path,))
            conn.execute("DELETE FROM translations WHERE rel_path = ?", (rel_path,))
