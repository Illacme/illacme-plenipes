#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - Audit Ledger
模块职责：商业化合规审计。记录全量 AI 算力交易、配置变更与系统生命周期事件。
🛡️ [AEL-Iter-v1.0]：不可篡改的操作流水账本。
"""

import os
import sqlite3
import json
import time
import threading
from datetime import datetime
from core.utils.tracing import tlog

class AuditLedger:
    """🚀 [V1.0] 审计账本：商业合规底座"""

    def __init__(self, db_path: str):
        self.db_path = os.path.abspath(os.path.expanduser(db_path))
        self._local = threading.local()
        self._db_lock = threading.RLock()
        self._log_warned_truncate = False
        # 🛡️ [V50.3] 确保工业数据目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_conn(self):
        if not hasattr(self._local, "conn"):
            # Set connection timeout to 30.0 seconds to mitigate concurrency lock contention
            self._local.conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
            try:
                db_dir = os.path.abspath(self.db_path)
                is_mounted = any(db_dir.startswith(p) for p in ['/Volumes/', '/mnt/', '/media/', '\\\\'])
                
                # Windows remote/removable drive detection
                if not is_mounted and os.name == 'nt':
                    try:
                        import ctypes
                        drive = os.path.splitdrive(db_dir)[0] + "\\"
                        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
                        if drive_type in (2, 4):
                            is_mounted = True
                    except:
                        pass

                if is_mounted:
                    self._local.conn.execute("PRAGMA journal_mode=TRUNCATE")
                    self._local.conn.execute("PRAGMA synchronous=FULL")
                    if not getattr(self, '_log_warned_truncate', False):
                        tlog.info(f"🗄️ [AuditLedger] 检测到挂载卷或网络共享路径 {self.db_path}，已自动切换至 TRUNCATE 兼容模式并开启同步保护")
                        self._log_warned_truncate = True
                else:
                    self._local.conn.execute("PRAGMA journal_mode=WAL")
                    self._local.conn.execute("PRAGMA synchronous=NORMAL")
            except Exception as e:
                tlog.warning(f"⚠️ [AuditLedger] 无法配置 journal_mode: {e}")
        return self._local.conn

    def _init_db(self):
        with self._db_lock:
            conn = self._get_conn()
            with conn:
                # 🚀 [V50.3] 自动执行 Schema 物理迁移
                cursor = conn.execute("PRAGMA table_info(audit_logs)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if not columns:
                    # 初始创建
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS audit_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            imprint_id TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            event_type TEXT,
                            severity TEXT,
                            actor TEXT,
                            details TEXT,
                            metadata TEXT
                        )
                    """)
                elif "territory_id" in columns and "imprint_id" not in columns:
                    tlog.info("🧬 [AuditLedger] 侦测到旧版主权架构，正在执行物理迁移: territory_id -> imprint_id")
                    conn.execute("ALTER TABLE audit_logs RENAME COLUMN territory_id TO imprint_id")
                
                conn.execute("CREATE INDEX IF NOT EXISTS idx_imprint ON audit_logs(imprint_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_event ON audit_logs(event_type)")

    def log(self, event_type: str, details: str, imprint_id: str = "global", severity: str = "INFO", actor: str = "System", metadata: dict = None):
        """持久化一条审计记录"""
        with self._db_lock:
            try:
                conn = self._get_conn()
                with conn:
                    conn.execute(
                        "INSERT INTO audit_logs (imprint_id, event_type, severity, actor, details, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                        (imprint_id, event_type, severity, actor, details, json.dumps(metadata or {}))
                    )
            except Exception as e:
                tlog.error(f"❌ [AuditLedger] 记录审计失败: {e}")

    def export_report(self, imprint_id: str = None) -> list:
        """导出审计报告"""
        with self._db_lock:
            query = "SELECT * FROM audit_logs"
            params = []
            if imprint_id:
                query += " WHERE imprint_id = ?"
                params.append(imprint_id)
            
            query += " ORDER BY timestamp DESC"
            
            conn = self._get_conn()
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_total_cost(self, imprint_id: str = None) -> float:
        """从审计流水中聚合累计开销 (财务级数据)"""
        with self._db_lock:
            query = "SELECT SUM(CAST(json_extract(metadata, '$.cost') AS REAL)) as total FROM audit_logs WHERE event_type = 'AI_TRANSACTION'"
            params = []
            if imprint_id:
                query += " AND imprint_id = ?"
                params.append(imprint_id)
                
            conn = self._get_conn()
            row = conn.execute(query, params).fetchone()
            return row[0] if row and row[0] else 0.0

    def get_today_cost(self, imprint_id: str = "default") -> float:
        """🚀 [V22.0] 获取今日已消耗总额"""
        with self._db_lock:
            query = """
                SELECT SUM(CAST(json_extract(metadata, '$.cost') AS REAL))
                FROM audit_logs
                WHERE event_type = 'AI_TRANSACTION'
                AND imprint_id = ?
                AND date(timestamp) = date('now')
            """
            conn = self._get_conn()
            row = conn.execute(query, (imprint_id,)).fetchone()
            return row[0] if row and row[0] else 0.0

    def get_weekly_stats(self, imprint_id: str = "default") -> list:
        """🚀 [V22.0] 获取过去 7 天的统计趋势图数据"""
        with self._db_lock:
            query = """
                SELECT date(timestamp) as day, SUM(CAST(json_extract(metadata, '$.cost') AS REAL)) as cost
                FROM audit_logs
                WHERE event_type = 'AI_TRANSACTION'
                AND imprint_id = ?
                AND timestamp >= date('now', '-7 days')
                GROUP BY day
                ORDER BY day ASC
            """
            conn = self._get_conn()
            cursor = conn.execute(query, (imprint_id,))
            return [{"day": row[0], "cost": row[1] or 0.0} for row in cursor.fetchall()]


# 全局审计单例 (由 EngineFactory 在点火时显式调用 initialize_ledger)
ledger: AuditLedger = None

def initialize_ledger(db_path: str):
    """🛡️ [V35.2] 主权对正：显式初始化审计账本"""
    global ledger
    ledger = AuditLedger(db_path)
    return ledger
