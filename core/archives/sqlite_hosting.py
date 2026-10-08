# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SQLite Hosting Deploy Mixin
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10] 全站托管部署批次持久化 Mixin。
职责：提供 hosting_deploy_records 表的 CRUD 操作与整站发布批次流水持久化。
"""
import json
import time
from typing import List, Dict, Any, Optional


class SQLiteHostingMixin:
    """🌐 全站托管部署批次 Mixin — 通过 MRO 继承 self._get_conn()"""

    def create_hosting_deploy_batch(
        self,
        batch_id: str,
        trigger_source: str = "workbench",
        imprint_id: str = "default",
        theme: str = "default",
        pages_count: int = 0,
        bundle_size_kb: float = 0.0,
        targets_json: Any = None,
        overall_status: str = "RUNNING"
    ) -> str:
        """创建新的整站部署批次流水"""
        tjson = json.dumps(targets_json or {}) if not isinstance(targets_json, str) else targets_json
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO hosting_deploy_records (
                    batch_id, trigger_source, imprint_id, theme,
                    pages_count, bundle_size_kb, targets_json,
                    overall_status, started_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                batch_id, trigger_source, imprint_id, theme,
                pages_count, bundle_size_kb, tjson, overall_status
            ))
        return batch_id

    def update_hosting_deploy_batch(
        self,
        batch_id: str,
        overall_status: Optional[str] = None,
        duration_sec: Optional[float] = None,
        targets_json: Any = None,
        logs_excerpt: Optional[str] = None
    ) -> None:
        """更新整站部署批次状态与渠道结果"""
        updates = []
        params = []
        if overall_status is not None:
            updates.append("overall_status = ?")
            params.append(overall_status)
            if overall_status in ("SUCCESS", "FAILED", "PARTIAL_SUCCESS"):
                updates.append("completed_at = CURRENT_TIMESTAMP")
        if duration_sec is not None:
            updates.append("duration_sec = ?")
            params.append(duration_sec)
        if targets_json is not None:
            tjson = json.dumps(targets_json) if not isinstance(targets_json, str) else targets_json
            updates.append("targets_json = ?")
            params.append(tjson)
        if logs_excerpt is not None:
            updates.append("logs_excerpt = ?")
            params.append(logs_excerpt)

        if not updates:
            return

        params.append(batch_id)
        sql = f"UPDATE hosting_deploy_records SET {', '.join(updates)} WHERE batch_id = ?"
        with self._get_conn() as conn:
            conn.execute(sql, tuple(params))

    def list_hosting_deploy_batches(
        self,
        imprint_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """按时间倒序查询整站部署流水"""
        conn = self._get_conn()
        if imprint_id:
            rows = conn.execute("""
                SELECT * FROM hosting_deploy_records
                WHERE imprint_id = ?
                ORDER BY id DESC LIMIT ? OFFSET ?
            """, (imprint_id, limit, offset)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM hosting_deploy_records
                ORDER BY id DESC LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()

        results = []
        for r in rows:
            d = dict(r)
            try:
                d["targets"] = json.loads(d.get("targets_json") or "{}")
            except Exception:
                d["targets"] = {}
            results.append(d)
        return results

    def get_hosting_deploy_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """获取单个部署批次详情"""
        row = self._get_conn().execute(
            "SELECT * FROM hosting_deploy_records WHERE batch_id = ?",
            (batch_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["targets"] = json.loads(d.get("targets_json") or "{}")
        except Exception:
            d["targets"] = {}
        return d

    def delete_hosting_deploy_batch(self, batch_id: str) -> None:
        """删除部署批次"""
        with self._get_conn() as conn:
            conn.execute("DELETE FROM hosting_deploy_records WHERE batch_id = ?", (batch_id,))
