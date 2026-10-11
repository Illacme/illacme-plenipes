# -*- coding: utf-8 -*-
"""
🚀 [V125.0] Illacme Plenipes - Dispatch Overview Unified Aggregator
职责：聚合全域发布成果账本（包含社媒物权分发与全站/单篇托管部署），提供联合倒序排序与统一元数据解包。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple
from core.bindery.hosting_record_bridge import resolve_doc_title


def _resolve_unified_lang_meta(code: str) -> Tuple[str, str, str]:
    """🚀 [V123.0] 权威语种归一化解析：统一代码规范、母语官方名称与国旗图标"""
    clean = str(code or "").strip().lower()
    if not clean or clean in ("docs", "doc", "zh", "zh-hans", "zh-cn", "zh-sg", "cmn", "cmn-hans"):
        return "zh-Hans", "简体中文", "🇨🇳"
    if clean in ("zh-hant", "zh-tw", "zh-hk", "cmn-hant"):
        return "zh-Hant", "繁體中文", "🇭🇰"
    if clean in ("all", "*", "any"):
        return "all", "多语种全站", "🌐"
    try:
        from core.utils.language_hub import LanguageHub
        base = clean.split("-")[0].split("_")[0]
        for item in LanguageHub.get_supported_matrix():
            c = (item.get("code") or "").lower()
            if c == clean or c == base:
                return item.get("code", clean), item.get("name", clean.upper()), item.get("icon", "🌐")
    except Exception:
        pass
    return clean, clean.upper(), "🌐"


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

    cfg_vroot = getattr(engine.config, "vault_root", "") if hasattr(engine, "config") else ""
    vault_root = getattr(engine, "vault_root", "") or cfg_vroot
    unified: List[Dict[str, Any]] = []
    file_mtime_cache: Dict[str, Optional[float]] = {}

    def _to_ts(v: Any) -> Optional[float]:
        if not v: return None
        if isinstance(v, (int, float)): return float(v)
        try:
            from datetime import datetime
            return datetime.fromisoformat(str(v).strip().replace(" ", "T")).timestamp()
        except Exception: return None

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
                    saved_hash = rec.get("content_hash")

                    # 动态感知原稿物理变更：若本地原稿修改时间晚于该渠道发布时间，则判定为待更新滞后
                    if r_path and r_path not in file_mtime_cache:
                        abs_p = os.path.join(vault_root, r_path) if vault_root else r_path
                        if os.path.isfile(abs_p):
                            try: file_mtime_cache[r_path] = os.path.getmtime(abs_p)
                            except Exception: file_mtime_cache[r_path] = None
                        else:
                            file_mtime_cache[r_path] = None

                    f_mtime = file_mtime_cache.get(r_path)
                    up_ts = _to_ts(rec.get("updated_at") or rec.get("published_at"))
                    is_stale = bool(f_mtime and up_ts and (f_mtime > up_ts + 2.0))

                    doc_meta = meta.get_doc_info(r_path) if hasattr(meta, "get_doc_info") else {}
                    egress_map = doc_meta.get("publish_status", {}) if isinstance(doc_meta, dict) else {}
                    egress_info = egress_map.get(tid, {}) if isinstance(egress_map, dict) else {}
                    raw_status = str(egress_info.get("status") or "").lower()
                    raw_error = egress_info.get("error")
                    status_val = "failed" if (raw_status == "failed" or raw_error) else ("success" if raw_status in ("done", "draft", "success") else "idle")
                    diag = {}
                    if raw_error:
                        try:
                            from core.syndication.syndication_diagnostic import diagnose_syndication_error
                            diag = diagnose_syndication_error(tid, str(raw_error))
                        except Exception:
                            diag = {"friendly_message": str(raw_error), "suggestion": "请检查渠道配置或网络环境后重试。"}

                    l_code, l_name, l_icon = _resolve_unified_lang_meta(rec.get("lang_code", "zh-CN"))
                    ch_info = channel_map.get(tid, {})
                    rec_title = _resolve_rec_doc_title(engine, r_path, docs_snapshot, vault_root)

                    unified.append({
                        "id": str(rec.get("id") or f"syn_{tid}_{r_path}"), "rel_path": r_path,
                        "title": rec_title or r_path, "lang_code": l_code, "lang_name": l_name, "lang_icon": l_icon,
                        "target_id": tid, "target_type": ch_info.get("type", "social"),
                        "target_name": ch_info.get("name", tid), "target_icon": ch_info.get("icon", "🏷️"),
                        "remote_article_id": rec.get("remote_article_id", ""), "remote_url": rec.get("remote_url", ""),
                        "content_hash": saved_hash, "is_stale": is_stale,
                        "status": status_val, "error": raw_error, "last_error": raw_error, "diagnostic": diag,
                        "updated_at": str(rec.get("updated_at") or "")
                    })
        except Exception: pass

    # 2. 解包全站与单文档托管发布历史 (Hosting Deploy Batches)
    if hasattr(meta, "list_hosting_deploy_batches"):
        try:
            raw_batches = meta.list_hosting_deploy_batches(limit=limit)
            if isinstance(raw_batches, list):
                for b in raw_batches:
                    if not isinstance(b, dict): continue
                    bid = str(b.get("batch_id") or "")
                    targets = b.get("targets") or b.get("targets_json") or {}
                    if isinstance(targets, str):
                        try: targets = json.loads(targets)
                        except Exception: targets = {}

                    trig = str(b.get("trigger_source") or "")
                    doc_id = b.get("doc_id") or (targets.get("_trigger_doc") if isinstance(targets, dict) else None)
                    if not doc_id and trig.startswith("vault_drawer:"):
                        doc_id = trig.split("vault_drawer:", 1)[1]

                    r_path = doc_id or "全站发布 (整站)"
                    rec_title = b.get("doc_title") or _resolve_rec_doc_title(engine, r_path, docs_snapshot, vault_root)
                    started_at = str(b.get("started_at") or "")

                    for tid, tinfo in (targets.items() if isinstance(targets, dict) else []):
                        if not tid or tid.startswith("_") or not isinstance(tinfo, dict): continue
                        if tinfo.get("status") != "SUCCESS": continue

                        ch_info = channel_map.get(tid, {})
                        t_url = tinfo.get("url") or tinfo.get("site_url") or ""
                        t_at = str(tinfo.get("deployed_at") or started_at)

                        unified.append({
                            "id": f"hosting_{bid}_{tid}", "rel_path": r_path, "title": rec_title or r_path,
                            "lang_code": "all", "lang_name": "多语种全站", "lang_icon": "🌐",
                            "target_id": tid, "target_type": "hosting",
                            "target_name": ch_info.get("name", tid.upper()), "target_icon": ch_info.get("icon", "🌐"),
                            "remote_article_id": bid, "remote_url": t_url, "updated_at": t_at
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


def collect_unified_dead_letter_tasks(
    engine: Any,
    docs_snapshot: Optional[Dict[str, Any]] = None,
    channel_map: Optional[Dict[str, Dict[str, str]]] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    🎯 全域死信大聚合：无缝融合社交媒体分发失败与网站托管部署失败
    返回包含诊断建议的标准失败任务列表
    """
    channel_map = channel_map or {}
    meta = getattr(engine, "meta", None)
    if not meta: return []

    vault_root = getattr(engine, "vault_root", "") or (
        getattr(engine.config, "vault_root", "") if hasattr(engine, "config") else ""
    )
    dead_letters: List[Dict[str, Any]] = []

    # 1. 解包社交媒体分发死信任务 (Syndication Tasks)
    if hasattr(meta, "list_all_syndication_tasks"):
        try:
            from core.syndication.syndication_diagnostic import diagnose_syndication_error
        except Exception:
            diagnose_syndication_error = None

        try:
            raw_tasks = meta.list_all_syndication_tasks()
            if isinstance(raw_tasks, list):
                for item in raw_tasks:
                    if not isinstance(item, dict) or item.get("status") != "FAILED": continue
                    tid = str(item.get("target_id") or "")
                    rel_p = str(item.get("rel_path") or "")
                    l_code, l_name, l_icon = _resolve_unified_lang_meta(item.get("lang_code", "zh-CN"))
                    lerr = str(item.get("last_error") or "未知网络或认证异常")
                    diag = diagnose_syndication_error(tid, lerr) if (diagnose_syndication_error and tid) else {}
                    ch_info = channel_map.get(tid, {})
                    dead_letters.append({
                        "id": item.get("id"), "rel_path": rel_p, "target_id": tid,
                        "target_type": ch_info.get("type", "social"), "target_name": ch_info.get("name", tid),
                        "target_icon": ch_info.get("icon", "🏷️"), "title": item.get("title") or _resolve_rec_doc_title(engine, rel_p, docs_snapshot, vault_root),
                        "slug": item.get("slug", ""), "lang_code": l_code, "lang_name": l_name, "lang_icon": l_icon, "status": "FAILED",
                        "last_error": lerr, "retry_count": item.get("retry_count", 0), "next_retry_time": item.get("next_retry_time", 0),
                        "diagnostic": diag, "updated_at": str(item.get("updated_at") or "")
                    })
        except Exception: pass

    # 2. 解包网站托管部署异常批次 (Hosting Deploy Batches)
    if hasattr(meta, "list_hosting_deploy_batches"):
        try:
            raw_batches = meta.list_hosting_deploy_batches(limit=limit)
            if isinstance(raw_batches, list):
                seen_targets = set()
                for b in raw_batches:
                    if not isinstance(b, dict): continue
                    bid, overall_status = str(b.get("batch_id") or ""), b.get("overall_status")
                    started_at = str(b.get("started_at") or "")
                    targets = b.get("targets") or b.get("targets_json") or {}
                    if isinstance(targets, str):
                        try: targets = json.loads(targets)
                        except Exception: targets = {}
                    doc_id = b.get("doc_id") or (targets.get("_trigger_doc") if isinstance(targets, dict) else None)
                    trig = str(b.get("trigger_source") or "")
                    if not doc_id and trig.startswith("vault_drawer:"): doc_id = trig.split("vault_drawer:", 1)[1]
                    r_path = doc_id or "全站发布 (整站)"
                    rec_title = b.get("doc_title") or _resolve_rec_doc_title(engine, r_path, docs_snapshot, vault_root)

                    if isinstance(targets, dict) and targets:
                        for tid, tinfo in targets.items():
                            if not tid or tid.startswith("_") or not isinstance(tinfo, dict) or tid in seen_targets: continue
                            seen_targets.add(tid)
                            t_status = tinfo.get("status")
                            if t_status == "FAILED" or (t_status != "SUCCESS" and overall_status == "FAILED"):
                                ch_info = channel_map.get(tid, {})
                                raw_err = tinfo.get("error") or b.get("logs_excerpt") or "全站部署推流失败"
                                first_err = str(raw_err).strip().split("\n")[0][:120]
                                dead_letters.append({
                                    "id": f"hosting_{bid}_{tid}", "batch_id": bid, "rel_path": r_path,
                                    "target_id": tid, "target_type": "hosting", "target_name": ch_info.get("name", tid.upper()), "target_icon": ch_info.get("icon", "🌐"),
                                    "title": rec_title, "slug": "", "lang_code": "all", "lang_name": "多语种全站", "lang_icon": "🌐", "status": "FAILED",
                                    "last_error": first_err, "retry_count": 1, "next_retry_time": 0,
                                    "diagnostic": {"category": "hosting_deploy_failure", "suggestion": f"请检查 {ch_info.get('name', tid)} 的 Token 授权或网络连通性后在托管面板点击重新发布", "action": "redeploy"},
                                    "updated_at": str(tinfo.get("deployed_at") or started_at)
                                })
                    elif overall_status == "FAILED" and bid not in seen_targets:
                        seen_targets.add(bid)
                        dead_letters.append({
                            "id": f"hosting_{bid}", "batch_id": bid, "rel_path": r_path, "target_id": "hosting",
                            "target_type": "hosting", "target_name": "全站托管", "target_icon": "🌐",
                            "title": rec_title, "slug": "", "lang_code": "all", "lang_name": "多语种全站", "lang_icon": "🌐", "status": "FAILED",
                            "last_error": str(b.get("logs_excerpt") or "全站构建或部署失败").strip().split("\n")[0][:120], "retry_count": 1, "next_retry_time": 0,
                            "diagnostic": {"category": "hosting_batch_failure", "suggestion": "请查看部署日志详情排查构建错误", "action": "redeploy"},
                            "updated_at": started_at
                        })
        except Exception: pass

    return dead_letters[:limit]


def is_any_hosting_deploying(engine: Any) -> bool:
    """🌐 [全域感知] 检查是否有全站/单篇托管部署批次正处于 RUNNING 或 PENDING 活跃推流态"""
    meta = getattr(engine, "meta", None)
    if not meta or not hasattr(meta, "list_hosting_deploy_batches"):
        return False
    try:
        batches = meta.list_hosting_deploy_batches(limit=1)
        if batches and isinstance(batches, list):
            b = batches[0]
            if isinstance(b, dict):
                return str(b.get("overall_status") or "").upper() in ("RUNNING", "PENDING")
    except Exception:
        pass
    return False

