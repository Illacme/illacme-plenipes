# -*- coding: utf-8 -*-
"""
🚀 [V125.0] Illacme Plenipes - Dispatch Overview Unified Aggregator
职责：聚合全域发布成果账本（包含社媒物权分发与全站/单篇托管部署），提供联合倒序排序与统一元数据解包。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import json
from typing import Dict, Any, List, Optional
from core.bindery.hosting_record_bridge import resolve_doc_title


def collect_unified_recent_records(
    engine: Any,
    docs_snapshot: Optional[Dict[str, Any]] = None,
    channel_map: Optional[Dict[str, Dict[str, str]]] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    🎯 全域成果大聚合：无缝融合社交媒体分发与网站托管部署历史
    返回按 updated_at 倒序排列的标准成果记录列表
    """
    channel_map = channel_map or {}
    meta = getattr(engine, "meta", None)
    if not meta:
        return []

    vault_root = getattr(engine, "vault_root", "") or (
        getattr(engine.config, "vault_root", "") if hasattr(engine, "config") else ""
    )

    unified: List[Dict[str, Any]] = []

    # 1. 解包社交媒体分发历史 (Syndication Ledger)
    if hasattr(meta, "list_all_syndication_records"):
        try:
            raw_syn = meta.list_all_syndication_records(limit=limit)
            if isinstance(raw_syn, list):
                for rec in raw_syn:
                    if not isinstance(rec, dict):
                        continue
                    r_path = rec.get("rel_path", "")
                    tid = rec.get("target_id", "")
                    l_code = rec.get("lang_code", "zh-CN")
                    ch_info = channel_map.get(tid, {})
                    rec_title = _resolve_rec_doc_title(engine, r_path, docs_snapshot, vault_root)

                    unified.append({
                        "id": str(rec.get("id") or f"syn_{tid}_{r_path}"),
                        "rel_path": r_path,
                        "title": rec_title or r_path,
                        "lang_code": l_code,
                        "lang_name": l_code.upper(),
                        "lang_icon": "🌐",
                        "target_id": tid,
                        "target_type": ch_info.get("type", "social"),
                        "target_name": ch_info.get("name", tid),
                        "target_icon": ch_info.get("icon", "🏷️"),
                        "remote_article_id": rec.get("remote_article_id", ""),
                        "remote_url": rec.get("remote_url", ""),
                        "updated_at": str(rec.get("updated_at") or "")
                    })
        except Exception:
            pass

    # 2. 解包全站与单文档托管发布历史 (Hosting Deploy Batches)
    if hasattr(meta, "list_hosting_deploy_batches"):
        try:
            raw_batches = meta.list_hosting_deploy_batches(limit=limit)
            if isinstance(raw_batches, list):
                for b in raw_batches:
                    if not isinstance(b, dict):
                        continue
                    bid = str(b.get("batch_id") or "")
                    targets = b.get("targets") or b.get("targets_json") or {}
                    if isinstance(targets, str):
                        try:
                            targets = json.loads(targets)
                        except Exception:
                            targets = {}

                    trig = str(b.get("trigger_source") or "")
                    doc_id = b.get("doc_id") or targets.get("_trigger_doc")
                    if not doc_id and trig.startswith("vault_drawer:"):
                        doc_id = trig.split("vault_drawer:", 1)[1]

                    r_path = doc_id or "全站发布 (整站)"
                    rec_title = b.get("doc_title") or _resolve_rec_doc_title(engine, r_path, docs_snapshot, vault_root)
                    started_at = str(b.get("started_at") or "")

                    for tid, tinfo in targets.items():
                        if not tid or tid.startswith("_") or not isinstance(tinfo, dict):
                            continue
                        if tinfo.get("status") != "SUCCESS":
                            continue

                        ch_info = channel_map.get(tid, {})
                        t_url = tinfo.get("url") or tinfo.get("site_url") or ""
                        t_at = str(tinfo.get("deployed_at") or started_at)

                        unified.append({
                            "id": f"hosting_{bid}_{tid}",
                            "rel_path": r_path,
                            "title": rec_title or r_path,
                            "lang_code": "all",
                            "lang_name": "多语种全站",
                            "lang_icon": "🌐",
                            "target_id": tid,
                            "target_type": "hosting",
                            "target_name": ch_info.get("name", tid.upper()),
                            "target_icon": ch_info.get("icon", "🌐"),
                            "remote_article_id": bid,
                            "remote_url": t_url,
                            "updated_at": t_at
                        })
        except Exception:
            pass

    # 3. 按 updated_at 倒序联合排序
    unified.sort(key=lambda x: str(x.get("updated_at") or ""), reverse=True)
    return unified[:limit]


def _resolve_rec_doc_title(
    engine: Any,
    rel_path: str,
    docs_snapshot: Optional[Dict[str, Any]] = None,
    vault_root: str = ""
) -> str:
    """智能解析文档可读标题"""
    if not rel_path or rel_path.startswith("全站发布"):
        return rel_path or "全站静态站点"
    if docs_snapshot and isinstance(docs_snapshot.get(rel_path), dict):
        t = docs_snapshot[rel_path].get("title")
        if t:
            return str(t)
    return resolve_doc_title(rel_path, vault_root)
