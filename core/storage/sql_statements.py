# -*- coding: utf-8 -*-

"""🚀 [V24.6] 静态 SQL 语句仓库"""

INIT_SCHEMA = [
    # 1. 文档主表
    """
    CREATE TABLE IF NOT EXISTS documents (
        rel_path TEXT PRIMARY KEY,
        title TEXT,
        slug TEXT,
        source_hash TEXT,
        shadow_hash TEXT,
        route_prefix TEXT,
        route_source TEXT,
        sub_dir TEXT,
        persistent_date TEXT,
        metadata_json TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # 2. 翻译状态表
    """
    CREATE TABLE IF NOT EXISTS translations (
        rel_path TEXT,
        lang_code TEXT,
        status TEXT,
        result_json TEXT,
        PRIMARY KEY (rel_path, lang_code)
    )
    """,
    # 3. 资产注册表
    """
    CREATE TABLE IF NOT EXISTS asset_registry (
        asset_hash TEXT PRIMARY KEY,
        metadata_json TEXT,
        last_seen INTEGER
    )
    """,
    # 4. 目录索引表
    """
    CREATE TABLE IF NOT EXISTS dir_index (
        raw_dir TEXT PRIMARY KEY,
        slug TEXT
    )
    """,
    # 5. 计费审计流水表
    """
    CREATE TABLE IF NOT EXISTS usage_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id TEXT,
        event_type TEXT,
        description TEXT,
        cost REAL,
        metadata_json TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
]

UPSERT_DOC = """
INSERT INTO documents (rel_path, title, slug, source_hash, shadow_hash, route_prefix, route_source, sub_dir, persistent_date, metadata_json)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(rel_path) DO UPDATE SET
    title=excluded.title, slug=excluded.slug, source_hash=excluded.source_hash,
    shadow_hash=excluded.shadow_hash, route_prefix=excluded.route_prefix,
    metadata_json=excluded.metadata_json, last_updated=CURRENT_TIMESTAMP
"""

UPSERT_TRANS = """
INSERT INTO translations (rel_path, lang_code, status, result_json)
VALUES (?, ?, ?, ?)
ON CONFLICT(rel_path, lang_code) DO UPDATE SET
    status=excluded.status, result_json=excluded.result_json
"""
