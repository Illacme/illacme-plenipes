# -*- coding: utf-8 -*-
"""Illacme-plenipes Core - SQLite Persistence Backend
🛡️ [V48.3 Refactored]
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10] 社媒分发与维护方法已纵切至 Mixin 子分片。
"""
import sqlite3
import json
import threading
import os
import time
from core.utils.tracing import tlog
from .sql_statements import INIT_SCHEMA, UPSERT_DOC, UPSERT_TRANS
from .sqlite_review import SQLiteReviewMixin
from .sqlite_syndication import SQLiteSyndicationMixin
from .sqlite_maintenance import SQLiteMaintenanceMixin
from .sqlite_doc_queries import SQLiteDocQueryMixin

class SQLiteBackend(SQLiteReviewMixin, SQLiteSyndicationMixin, SQLiteMaintenanceMixin, SQLiteDocQueryMixin):
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
                    except Exception:
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
        if not row:
            row = conn.execute("SELECT * FROM documents WHERE LOWER(rel_path) = LOWER(?)", (rel_path,)).fetchone()
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

    def delete_document(self, rel_path):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM documents WHERE rel_path = ?", (rel_path,))
            conn.execute("DELETE FROM translations WHERE rel_path = ?", (rel_path,))

