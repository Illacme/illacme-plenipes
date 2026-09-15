# -*- coding: utf-8 -*-
"""
🎨 Design Studio - Visual Assets Management Routes Shard
职责：提供媒体资产查询、单项/批量物理删除与文档封面应用接口。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
import math
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from core.runtime.engine_singleton import get_global_engine
from core.utils.tracing import tlog
from core.utils.text import parse_frontmatter, inject_frontmatter
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path

router = APIRouter()

def verify_token(x_token: Optional[str] = Header(None, alias="X-Token")) -> None:
    engine = get_global_engine()
    if not engine or not getattr(engine, 'config', None) or not getattr(engine.config, 'system', None) or not getattr(engine.config.system, 'api_token', None):
        return
    if x_token != engine.config.system.api_token:
        raise HTTPException(status_code=403, detail="Unauthorized")

class ApplyCoverRequest(BaseModel):
    doc_id: str
    cover_url: str

class BatchDeleteAssetsRequest(BaseModel):
    asset_ids: List[int]
    remove_from_docs: bool = True

def _scan_vault_references(vault_root: str) -> list:
    docs_cache = []
    if not vault_root or not os.path.isdir(vault_root):
        return docs_cache
    for root, _, files in os.walk(vault_root):
        if ".plenipes" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith(".md"):
                fp = os.path.join(root, f)
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as s:
                        content = s.read()
                    metadata, pure_content, _ = parse_frontmatter(content)
                    docs_cache.append({
                        "rel_path": os.path.relpath(fp, vault_root),
                        "title": metadata.get("title") or f,
                        "cover": str(metadata.get("cover", "") or ""),
                        "content": pure_content
                    })
                except Exception:
                    pass
    return docs_cache

@router.get("/api/design/assets", dependencies=[Depends(verify_token)])
async def list_visual_assets(page: int = 1, limit: int = 60, provider: Optional[str] = None):
    engine = get_global_engine()
    if not engine or not hasattr(engine, "meta") or not getattr(engine.meta, "sqlite", None):
        return {"success": True, "assets": [], "total": 0, "page": page, "limit": limit, "total_pages": 1}
    try:
        vault_root = getattr(engine, "vault_root", os.getcwd())
        docs_cache = _scan_vault_references(vault_root)
        conn = engine.meta.sqlite.get_connection()
        cur = conn.cursor()

        # 1. 计算总条数 (Total Count)
        if provider and provider != 'all':
            strat = f"ai_{provider}"
            cur.execute("SELECT COUNT(*) FROM visual_assets WHERE strategy = ?", (strat,))
            total = cur.fetchone()[0]
        else:
            cur.execute("SELECT COUNT(*) FROM visual_assets")
            total = cur.fetchone()[0]

        # 2. 分页偏移计算 (Pagination Offset)
        limit = max(1, min(limit, 200))
        total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1
        page = max(1, min(page, total_pages)) if total > 0 else 1
        offset = (page - 1) * limit

        # 3. 分页查询记录 (Slice Query)
        if provider and provider != 'all':
            cur.execute(
                "SELECT id, rel_path, asset_type, strategy, source_url, cdn_url, media_id, prompt, created_at "
                "FROM visual_assets WHERE strategy = ? ORDER BY id DESC LIMIT ? OFFSET ?", (strat, limit, offset)
            )
        else:
            cur.execute(
                "SELECT id, rel_path, asset_type, strategy, source_url, cdn_url, media_id, prompt, created_at "
                "FROM visual_assets ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)
            )
        rows = cur.fetchall()
        assets = []
        for r in rows:
            source_url = r[4] or ""
            fn = os.path.basename(source_url.split("?")[0]) if source_url else ""
            refs = []
            for doc in docs_cache:
                ref_types = []
                if (source_url and source_url in doc["cover"]) or (fn and fn in doc["cover"]):
                    ref_types.append("cover")
                if (source_url and source_url in doc["content"]) or (fn and fn in doc["content"]):
                    ref_types.append("body")
                if ref_types:
                    refs.append({"rel_path": doc["rel_path"], "title": doc["title"], "ref_types": ref_types})
            assets.append({
                "id": r[0], "rel_path": r[1], "asset_type": r[2], "strategy": r[3],
                "source_url": source_url, "url": source_url, "engine": r[3],
                "cdn_url": r[5], "media_id": r[6], "prompt": r[7], "created_at": r[8],
                "references": refs, "reference_count": len(refs)
            })
        return {
            "success": True,
            "assets": assets,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    except Exception as e:
        tlog.warning(f"⚠️ [设计中心] 查询资产记录失败: {e}")
        return {"success": True, "assets": [], "total": 0, "page": page, "limit": limit, "total_pages": 1}

@router.delete("/api/design/assets/{asset_id}", dependencies=[Depends(verify_token)])
async def delete_visual_asset(asset_id: int):
    engine = get_global_engine()
    if not engine or not hasattr(engine, "meta") or not getattr(engine.meta, "sqlite", None):
        raise HTTPException(status_code=500, detail="元数据引擎未初始化")
    try:
        conn = engine.meta.sqlite.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, source_url FROM visual_assets WHERE id = ?", (asset_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="资产不存在或已被删除")
        source_url = row[1] or ""
        if "/api/design/assets/covers/" in source_url:
            fn = source_url.split("/api/design/assets/covers/")[-1].split("?")[0]
            target_file = os.path.join(getattr(engine, "vault_root", os.getcwd()), ".plenipes", "cache", "covers", fn)
            if os.path.exists(target_file):
                try: os.remove(target_file)
                except Exception: pass
        cur.execute("DELETE FROM visual_assets WHERE id = ?", (asset_id,))
        conn.commit()
        return {"success": True, "message": f"资产 #{asset_id} 已成功删除"}
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {e}")

@router.post("/api/design/assets/batch-delete", dependencies=[Depends(verify_token)])
async def batch_delete_visual_assets(req: BatchDeleteAssetsRequest):
    """
    ⚡ 批量物理删除指定媒体资产，并可选同步从对应原稿 Frontmatter 中彻底解绑清空封面
    """
    engine = get_global_engine()
    if not engine or not hasattr(engine, "meta") or not getattr(engine.meta, "sqlite", None):
        raise HTTPException(status_code=500, detail="元数据引擎未初始化")
    if not req.asset_ids:
        return {"success": True, "deleted_count": 0, "unbound_docs_count": 0}

    vault_root = getattr(engine, "vault_root", os.getcwd())
    conn = engine.meta.sqlite.get_connection()
    cur = conn.cursor()
    placeholders = ",".join(["?"] * len(req.asset_ids))
    cur.execute(f"SELECT id, source_url FROM visual_assets WHERE id IN ({placeholders})", req.asset_ids)
    rows = cur.fetchall()
    if not rows:
        return {"success": True, "deleted_count": 0, "unbound_docs_count": 0}

    urls_to_delete = {r[1] for r in rows if r[1]}
    fns_to_delete = {os.path.basename(r[1].split("?")[0]) for r in rows if r[1]}

    unbound_count = 0
    if req.remove_from_docs and (urls_to_delete or fns_to_delete):
        docs_cache = _scan_vault_references(vault_root)
        for doc in docs_cache:
            cover_val = doc.get("cover", "")
            if any(u in cover_val for u in urls_to_delete) or any(fn in cover_val for fn in fns_to_delete if fn):
                abs_p = resolve_safe_path(engine, doc["rel_path"])
                if abs_p and os.path.isfile(abs_p):
                    try:
                        with open(abs_p, "r", encoding="utf-8") as f:
                            raw = f.read()
                        meta, pure, _ = parse_frontmatter(raw)
                        meta["cover"] = ""
                        new_content = inject_frontmatter(pure, meta)
                        with open(abs_p, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        if hasattr(engine.meta.sqlite, "update_document_metadata"):
                            engine.meta.sqlite.update_document_metadata(doc["rel_path"], {"cover": ""})
                        unbound_count += 1
                    except Exception as ue:
                        tlog.warning(f"⚠️ [设计中心] 解绑原稿封面失败: {doc['rel_path']} ({ue})")

    for _, src in rows:
        if src and "/api/design/assets/covers/" in src:
            fn = src.split("/api/design/assets/covers/")[-1].split("?")[0]
            target_f = os.path.join(vault_root, ".plenipes", "cache", "covers", fn)
            if os.path.exists(target_f):
                try: os.remove(target_f)
                except Exception: pass

    cur.execute(f"DELETE FROM visual_assets WHERE id IN ({placeholders})", req.asset_ids)
    conn.commit()
    tlog.info(f"🗑️ [设计中心] 批量删除完成: 物理清理 {len(rows)} 项, 同步解绑文库 {unbound_count} 篇原稿")
    return {
        "success": True,
        "deleted_count": len(rows),
        "unbound_docs_count": unbound_count,
        "message": f"成功物理删除 {len(rows)} 项资产" + (f"，已从 {unbound_count} 篇原稿中解绑封面" if unbound_count else "")
    }

@router.post("/api/design/assets/apply-cover", dependencies=[Depends(verify_token)])
async def apply_asset_as_cover(req: ApplyCoverRequest):
    engine = get_global_engine()
    if not engine: raise HTTPException(status_code=500, detail="系统引擎未启动")
    abs_path = resolve_safe_path(engine, req.doc_id)
    if not abs_path or not os.path.isfile(abs_path):
        if not req.doc_id.endswith(".md"): abs_path = resolve_safe_path(engine, req.doc_id + ".md")
    if not abs_path or not os.path.isfile(abs_path):
        raise HTTPException(status_code=404, detail=f"未找到目标原稿文件: {req.doc_id}")
    clean_doc = os.path.relpath(abs_path, getattr(engine, "vault_root", os.getcwd()))
    try:
        with open(abs_path, "r", encoding="utf-8") as f: raw_content = f.read()
        metadata, pure_content, _ = parse_frontmatter(raw_content)
        if req.cover_url: metadata["cover"] = req.cover_url
        elif "cover" in metadata: del metadata["cover"]
        new_content = inject_frontmatter(pure_content, metadata)
        with open(abs_path, "w", encoding="utf-8") as f: f.write(new_content)
        if hasattr(engine, "meta") and getattr(engine.meta, "sqlite", None):
            try: engine.meta.sqlite.update_document_metadata(clean_doc, {"cover": req.cover_url or ""})
            except Exception: pass
        return {"success": True, "message": f"已成功将封面应用至《{metadata.get('title') or clean_doc}》"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"应用封面异常: {e}")

@router.post("/api/design/assets/cleanup-idle", dependencies=[Depends(verify_token)])
async def cleanup_idle_assets():
    engine = get_global_engine()
    if not engine or not hasattr(engine, "meta") or not getattr(engine.meta, "sqlite", None):
        raise HTTPException(status_code=500, detail="元数据引擎未初始化")
    try:
        vault_root = getattr(engine, "vault_root", os.getcwd())
        docs_cache = _scan_vault_references(vault_root)
        conn = engine.meta.sqlite.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, source_url FROM visual_assets ORDER BY id DESC")
        rows = cur.fetchall()
        cleaned_count, freed_bytes, skipped_count = 0, 0, 0
        for r in rows:
            asset_id, source_url = r[0], r[1] or ""
            fn = os.path.basename(source_url.split("?")[0]) if source_url else ""
            has_ref = any(
                ((source_url and source_url in d["cover"]) or (fn and fn in d["cover"]) or
                 (source_url and source_url in d["content"]) or (fn and fn in d["content"]))
                for d in docs_cache
            )
            if has_ref:
                skipped_count += 1
                continue
            if "/api/design/assets/covers/" in source_url:
                target_file = os.path.join(vault_root, ".plenipes", "cache", "covers", fn)
                if os.path.exists(target_file):
                    try:
                        freed_bytes += os.path.getsize(target_file)
                        os.remove(target_file)
                    except Exception: pass
            cur.execute("DELETE FROM visual_assets WHERE id = ?", (asset_id,))
            cleaned_count += 1
        conn.commit()
        return {
            "success": True, "cleaned_count": cleaned_count, "freed_bytes": freed_bytes,
            "skipped_count": skipped_count, "message": f"成功安全清理 {cleaned_count} 项闲置资产"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理失败: {e}")
