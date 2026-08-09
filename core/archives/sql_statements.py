# -*- coding: utf-8 -*-

"""🚀 [V48.3] 静态 SQL 语句仓库"""

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
        imprint_id TEXT,
        event_type TEXT,
        description TEXT,
        cost REAL,
        metadata_json TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # 6. 🆕 [I5] 翻译人工校对回流表 (Translation Human Review)
    # 语种级锁定 (Q2=A)，存储 SSG 渲染前中间态 Markdown (Q4=A)
    """
    CREATE TABLE IF NOT EXISTS translation_reviews (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        imprint_id     TEXT NOT NULL DEFAULT 'default',
        doc_id         TEXT NOT NULL,
        lang_code      TEXT NOT NULL,
        reviewed_body  TEXT,
        reviewed_title TEXT,
        reviewed_desc  TEXT,
        source_hash    TEXT,
        is_stale       INTEGER NOT NULL DEFAULT 0,
        reviewed_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
        reviewed_by    TEXT DEFAULT 'commander',
        UNIQUE(imprint_id, doc_id, lang_code)
    )
    """,
    # 7. 🚀 多渠道分发异步重试队列
    """
    CREATE TABLE IF NOT EXISTS syndication_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rel_path TEXT NOT NULL,
        target_id TEXT NOT NULL,
        title TEXT,
        slug TEXT,
        content TEXT,
        metadata_json TEXT,
        lang_code TEXT,
        retry_count INTEGER DEFAULT 0,
        max_retries INTEGER DEFAULT 3,
        last_error TEXT,
        next_retry_time INTEGER DEFAULT 0,
        status TEXT DEFAULT 'PENDING',
        UNIQUE(rel_path, target_id)
    )
    """,
    # 8. 🚀 [V120.0] 全渠道文章生命周期物权记录表 (Syndication Records)
    """
    CREATE TABLE IF NOT EXISTS syndication_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rel_path TEXT NOT NULL,
        lang_code TEXT NOT NULL DEFAULT 'zh',
        target_id TEXT NOT NULL,
        remote_article_id TEXT NOT NULL,
        remote_url TEXT,
        content_hash TEXT,
        published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(rel_path, lang_code, target_id)
    )
    """
]

UPSERT_DOC = """
INSERT INTO documents (rel_path, title, slug, source_hash, shadow_hash, route_prefix, route_source, sub_dir, persistent_date, metadata_json)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(rel_path) DO UPDATE SET
    title=excluded.title, slug=excluded.slug, source_hash=excluded.source_hash,
    shadow_hash=excluded.shadow_hash, route_prefix=excluded.route_prefix,
    route_source=excluded.route_source, sub_dir=excluded.sub_dir,
    persistent_date=excluded.persistent_date, metadata_json=excluded.metadata_json,
    last_updated=CASE
        WHEN title IS NOT excluded.title
             OR slug IS NOT excluded.slug
             OR source_hash IS NOT excluded.source_hash
             OR shadow_hash IS NOT excluded.shadow_hash
             OR route_prefix IS NOT excluded.route_prefix
             OR route_source IS NOT excluded.route_source
             OR sub_dir IS NOT excluded.sub_dir
             OR persistent_date IS NOT excluded.persistent_date
             OR metadata_json IS NOT excluded.metadata_json
        THEN CURRENT_TIMESTAMP
        ELSE last_updated
    END
"""

UPSERT_TRANS = """
INSERT INTO translations (rel_path, lang_code, status, result_json)
VALUES (?, ?, ?, ?)
ON CONFLICT(rel_path, lang_code) DO UPDATE SET
    status=excluded.status, result_json=excluded.result_json
"""
