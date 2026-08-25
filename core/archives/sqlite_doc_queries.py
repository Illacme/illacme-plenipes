# -*- coding: utf-8 -*-
"""Illacme-plenipes Core - SQLite Document Query Mixin
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10] 从 sqlite_backend.py 纵切分离。
职责：文档分页查询、过滤计数与局部元数据注入等高级查询操作。
"""
import json


class SQLiteDocQueryMixin:
    """📄 文档高级查询操作 Mixin — 通过 MRO 继承 self._get_conn()"""

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
