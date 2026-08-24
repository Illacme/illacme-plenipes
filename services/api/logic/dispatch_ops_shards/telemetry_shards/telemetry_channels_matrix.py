# -*- coding: utf-8 -*-
"""
📡 Telemetry Shard - Hosting & Syndication Channels Matrix Scanner
职责：扫描 Direct Upload (Hosting) 独立站托管渠道与 Syndication 社媒分发渠道状态、计算变更哈希。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
"""

import os
import time
import re
import hashlib
from dataclasses import asdict

def build_channels_matrix(
    engine,
    doc_id: str,
    doc_info: dict,
    doc_records: dict,
    static_root: str,
    zh_path: str,
    zh_exists: bool,
    source_path: str
) -> list:
    """
    扫描全站托管 (Hosting) 与社交平台分发 (Syndication) 渠道并构建通道感知列表
    """
    config = engine.config
    slug = doc_info.get("slug") or os.path.splitext(os.path.basename(doc_id))[0]
    publish_status = doc_info.get("publish_status", {})
    channels_matrix = []

    # A. 提取 Hosting 全站托管渠道
    direct_upload = getattr(config.publish_control, "direct_upload", None) or {}
    if isinstance(direct_upload, dict):
        pass
    elif hasattr(direct_upload, "model_dump"):
        direct_upload = direct_upload.model_dump()
    elif hasattr(direct_upload, "__dataclass_fields__"):
        try:
            direct_upload = asdict(direct_upload)
        except Exception:
            direct_upload = getattr(direct_upload, "__dict__", {})
    else:
        direct_upload = getattr(direct_upload, "__dict__", {})
            
    for chan_id, chan_cfg in direct_upload.items():
        if isinstance(chan_cfg, dict) and chan_cfg.get("enabled"):
            status_info = publish_status.get(chan_id, {})
            chan_status = status_info.get("status")
            
            if not chan_status:
                chan_status = "published" if zh_exists else "pending"
            
            last_sync_str = "Never"
            if status_info.get("timestamp"):
                last_sync_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(status_info.get("timestamp")))
            elif zh_exists and os.path.exists(zh_path):
                last_sync_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(zh_path)))
                
            display_name = chan_id.replace("_", " ").title()
            raw_base_url = chan_cfg.get("public_url") or chan_cfg.get("site_url") or status_info.get("pages_base_url") or status_info.get("url") or ""
            if not raw_base_url or raw_base_url == "#":
                raw_base_url = chan_cfg.get("repo_url") or "#"

            if raw_base_url != "#":
                raw_base_url = re.sub(r'/[^/]+\.(html|md|htm)$', '', raw_base_url, flags=re.IGNORECASE)

            web_rel_route = ""
            if zh_path and static_root and os.path.exists(zh_path):
                try:
                    web_rel_route = os.path.relpath(zh_path, static_root).replace('\\', '/')
                except Exception:
                    web_rel_route = ""

            if not web_rel_route:
                web_rel_route = doc_info.get("target_path") or doc_info.get("route_path") or ""

            if not web_rel_route and slug:
                web_rel_route = f"{slug}.html"

            if web_rel_route.lower().endswith((".md", ".markdown")):
                web_rel_route = web_rel_route.rsplit(".", 1)[0] + ".html"

            if raw_base_url and raw_base_url != "#" and web_rel_route:
                artifact_url = f"{raw_base_url.rstrip('/')}/{web_rel_route.lstrip('/')}"
            else:
                artifact_url = raw_base_url if raw_base_url else "#"

            chan_status_clean = (chan_status or "pending").lower()
            is_hosting_done = chan_status_clean in ("published", "success", "done", "synced")

            channels_matrix.append({
                "channel_id": chan_id,
                "locale": f"🌐 {display_name}",
                "lang_code": "HOSTING",
                "status": chan_status_clean,
                "last_sync": last_sync_str,
                "artifact_url": artifact_url,
                "tokens": 0,
                "progress": 100 if is_hosting_done else 0,
                "cache_info": "全站托管",
                "reason": status_info.get("error") or ""
            })
             
    # B. 提取 Syndication 分发渠道
    syndication_cfg = getattr(config, "syndication", {}) or {}
    if isinstance(syndication_cfg, dict):
        pass
    elif hasattr(syndication_cfg, "model_dump"):
        syndication_cfg = syndication_cfg.model_dump()
    elif hasattr(syndication_cfg, "__dataclass_fields__"):
        try:
            syndication_cfg = asdict(syndication_cfg)
        except Exception:
            syndication_cfg = getattr(syndication_cfg, "__dict__", {})
    else:
        syndication_cfg = getattr(syndication_cfg, "__dict__", {})
         
    current_content_hash = None
    if os.path.exists(source_path):
        try:
            with open(source_path, 'rb') as sf:
                current_content_hash = hashlib.sha256(sf.read()).hexdigest()
        except Exception:
            pass

    for chan_id, chan_cfg in syndication_cfg.items():
        if isinstance(chan_cfg, dict):
            clean_chan_key = chan_id.lower().replace("_", "").replace("-", "")
            status_info = publish_status.get(chan_id)
            if not status_info:
                for k, v in publish_status.items():
                    if k.lower().replace("_", "").replace("-", "") == clean_chan_key:
                        status_info = v
                        break
            status_info = status_info or {}

            chan_record = doc_records.get(chan_id)
            if not chan_record:
                for k, v in doc_records.items():
                    if k.lower().replace("_", "").replace("-", "") == clean_chan_key:
                        chan_record = v
                        break
            chan_record = chan_record or {}
            record_url = chan_record.get("remote_url")
            
            has_keys = any(
                k not in ("enabled", "proxy", "force_push") and v and str(v).strip()
                for k, v in chan_cfg.items()
            )
            if has_keys or status_info or chan_cfg.get("enabled") or chan_record:
                chan_status = status_info.get("status") or ("synced" if (status_info.get("timestamp") or chan_record) else "pending")
                
                last_sync_str = "Never"
                if status_info.get("timestamp"):
                    last_sync_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(status_info.get("timestamp")))
                elif chan_record.get("updated_at"):
                    last_sync_str = str(chan_record.get("updated_at"))[:16]
                     
                display_name = chan_id.replace("_", " ").title()
                
                if status_info.get("status") == "syncing":
                    chan_status = "syncing"
                    syndication_url = "#"
                elif record_url:
                    syndication_url = record_url
                elif chan_record.get("remote_article_id"):
                    syndication_url = (
                        status_info.get("url")
                        or status_info.get("target_url")
                        or status_info.get("post_url")
                        or status_info.get("web_url")
                        or status_info.get("article_url")
                        or status_info.get("link")
                        or "#"
                    )
                else:
                    syndication_url = "#"

                chan_status_clean = (chan_status or "pending").lower()
                error_reason = status_info.get("error") or ""
                if chan_record.get("remote_article_id"):
                    if chan_status_clean != "syncing":
                        chan_status_clean = "published"
                        error_reason = ""
                elif chan_status_clean != "syncing":
                    if chan_status_clean not in ("failed", "error"):
                        chan_status_clean = "pending"

                is_syndication_done = chan_status_clean in ("published", "success", "done", "synced", "skipped")

                saved_hash = chan_record.get("content_hash")
                is_outdated = bool(saved_hash and current_content_hash and saved_hash != current_content_hash)

                channels_matrix.append({
                    "channel_id": chan_id,
                    "locale": f"📡 {display_name}",
                    "lang_code": "SYNDICATION",
                    "status": chan_status_clean,
                    "last_sync": last_sync_str,
                    "artifact_url": syndication_url,
                    "tokens": 0,
                    "progress": 100 if is_syndication_done else 0,
                    "cache_info": "内容已变更" if is_outdated else "分发渠道",
                    "is_outdated": is_outdated,
                    "reason": error_reason
                })

    return channels_matrix
