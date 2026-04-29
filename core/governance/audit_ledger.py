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
from datetime import datetime
from core.utils.tracing import tlog

class AuditLedger:
    """🚀 [V1.0] 审计账本：商业合规底座"""

    def __init__(self, db_path: str = ".plenipes/ledger_audit.db"):
        self.db_path = db_path
        # 🛡️ [V24.6] 确保工业数据目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workspace_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    severity TEXT,
                    actor TEXT,
                    details TEXT,
                    metadata TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_workspace ON audit_logs(workspace_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_event ON audit_logs(event_type)")

    def log(self, event_type: str, details: str, workspace_id: str = "global", severity: str = "INFO", actor: str = "System", metadata: dict = None):
        """持久化一条审计记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO audit_logs (workspace_id, event_type, severity, actor, details, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                    (workspace_id, event_type, severity, actor, details, json.dumps(metadata or {}))
                )
        except Exception as e:
            tlog.error(f"❌ [AuditLedger] 记录审计失败: {e}")

    def export_report(self, workspace_id: str = None) -> list:
        """导出审计报告"""
        query = "SELECT * FROM audit_logs"
        params = []
        if workspace_id:
            query += " WHERE workspace_id = ?"
            params.append(workspace_id)
        
        query += " ORDER BY timestamp DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_total_cost(self, workspace_id: str = None) -> float:
        """从审计流水中聚合累计开销 (财务级数据)"""
        query = "SELECT SUM(CAST(json_extract(metadata, '$.cost') AS REAL)) as total FROM audit_logs WHERE event_type = 'AI_TRANSACTION'"
        params = []
        if workspace_id:
            query += " AND workspace_id = ?"
            params.append(workspace_id)
            
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(query, params).fetchone()
            return row[0] if row and row[0] else 0.0

    def get_today_cost(self, workspace_id: str = "default") -> float:
        """🚀 [V22.0] 获取今日已消耗总额"""
        query = """
            SELECT SUM(CAST(json_extract(metadata, '$.cost') AS REAL))
            FROM audit_logs
            WHERE event_type = 'AI_TRANSACTION'
            AND workspace_id = ?
            AND date(timestamp) = date('now')
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(query, (workspace_id,)).fetchone()
            return row[0] if row and row[0] else 0.0

    def get_weekly_stats(self, workspace_id: str = "default") -> list:
        """🚀 [V22.0] 获取过去 7 天的统计趋势图数据"""
        query = """
            SELECT date(timestamp) as day, SUM(CAST(json_extract(metadata, '$.cost') AS REAL)) as cost
            FROM audit_logs
            WHERE event_type = 'AI_TRANSACTION'
            AND workspace_id = ?
            AND timestamp >= date('now', '-7 days')
            GROUP BY day
            ORDER BY day ASC
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, (workspace_id,))
            return [{"day": row[0], "cost": row[1] or 0.0} for row in cursor.fetchall()]

# 全局审计单例 (由 EngineFactory 在点火时挂载)
ledger = AuditLedger()
