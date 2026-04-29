# -*- coding: utf-8 -*-
import os
from typing import Dict, Any

class LedgerChecker:
    """🚀 [V24.6] 账本与元数据一致性诊断器"""
    
    @staticmethod
    def check(engine) -> Dict[str, Any]:
        """账本数据一致性审计"""
        res = {"name": "Ledger & Metadata", "status": "PASS", "details": []}
        meta = engine.meta
        config = engine.config

        # 1. 统计数据
        all_docs = meta.get_documents_snapshot()
        doc_count = len(all_docs)
        res.get('details').append(f"🧬 当前激活账本: {config.metadata_db}")
        res.get('details').append(f"📊 当前账本在册文档: {doc_count} 篇")

        # 2. 检查 Slug 冲突
        slugs = {}
        conflicts = []
        for rel_path, info in all_docs.items():
            s = info.get("slug")
            if s:
                if s in slugs: conflicts.append((rel_path, slugs[s]))
                slugs[s] = rel_path

        if conflicts:
            res['status'] = "WARN"
            res.get('details').append(f"⚠️ 发现 {len(conflicts)} 处 Slug 物理冲突！")
            for c1, c2 in conflicts[:3]:
                res.get('details').append(f"   - 冲突路径: {c1} <-> {c2}")

        # 3. SQLite 物理完整性校验
        try:
            conn = meta.sqlite._get_conn()
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            row = cursor.fetchone()

            if row and row[0] == "ok":
                res.get('details').append("🟢 SQLite 物理层一致性校验通过：Data Integrity Valid。")
            else:
                res['status'] = "FAIL"
                res.get('details').append(f"❌ 数据库物理损坏: {row[0] if row else 'Unknown'}")
        except Exception as e:
            res['status'] = "FAIL"
            res.get('details').append(f"❌ 数据库审计发生异常: {e}")

        return res
