# -*- coding: utf-8 -*-
"""Illacme-plenipes Core - SQLite Document Query Mixin
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10] 从 sqlite_backend.py 纵切分离。
职责：文档分页查询、过滤计数与局部元数据注入等高级查询操作。
"""
import json
import os


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

    @staticmethod
    def is_slug_conflict(candidate_slug: str, current_path: str, conflict_path: str, dir_mode: str = "nested") -> bool:
        """
        判定两个文档是否构成真实的路由与 slug 冲突，深度结合治理中心【网址路径组织形态】(slug_dir_mode)。
        1. 目录索引页豁免：对于 index / home / readme，不同父目录天然隔离，互不冲突；
        2. nested (目录树复刻，默认)：最终 URL 包含各自目录层级，只有同父目录下相同 slug 才冲突；
        3. prefix (智能前缀)：拼接父目录前缀后的完整 slug 相同才冲突；
        4. flat (极简根目录)：所有普通文档平铺至根目录，跨目录同名普通 slug 构成物理覆盖冲突。
        """
        if not candidate_slug or not current_path or not conflict_path:
            return False
        
        c_dir = os.path.dirname(current_path.replace("\\", "/")).strip("/").lower()
        t_dir = os.path.dirname(conflict_path.replace("\\", "/")).strip("/").lower()
        
        # 1. 目录索引页豁免权 (无论哪种模式，频道首页与全站首页均被 RouteManager 语义收敛隔离)
        if candidate_slug.lower() in ("index", "home", "readme"):
            return c_dir == t_dir

        # 2. 依据 slug_dir_mode 判定真实 URL 碰撞
        mode = (dir_mode or "nested").lower()
        if mode == "nested":
            return c_dir == t_dir
        elif mode == "prefix":
            c_prefix = f"{c_dir.replace('/', '-')}-" if c_dir else ""
            t_prefix = f"{t_dir.replace('/', '-')}-" if t_dir else ""
            return f"{c_prefix}{candidate_slug.lower()}" == f"{t_prefix}{candidate_slug.lower()}"
        else:
            return True

    def update_document_metadata(self, rel_path, metadata_updates, dir_mode: str = "nested"):
        """🚀 [V52.0] 局部元数据注入：仅更新 metadata_json 中的特定字段"""
        conn = self._get_conn()
        with conn:
            row = conn.execute("SELECT metadata_json FROM documents WHERE rel_path = ?", (rel_path,)).fetchone()
            if not row: return False

            # 🛡️ [Slug 唯一性守卫] 结合 slug_dir_mode 进行真实 URL 冲突检测
            if "slug" in metadata_updates:
                new_slug = metadata_updates["slug"]
                conflict_rows = conn.execute(
                    "SELECT rel_path FROM documents WHERE slug = ? AND rel_path != ?",
                    (new_slug, rel_path)
                ).fetchall()
                for c_row in conflict_rows:
                    conflict_path = dict(c_row).get("rel_path", "?")
                    if self.is_slug_conflict(new_slug, rel_path, conflict_path, dir_mode=dir_mode):
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
