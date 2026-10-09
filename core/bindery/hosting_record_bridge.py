# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Hosting Record Bridge
🛡️ [SOP-02 模块规范] 将全域发布 (Global Publish) 产生的全渠道部署成果无缝同步至网站发布历史批次账本。
"""
import os
import time
import uuid
import json
from typing import Dict, Any, Optional
from core.utils.tracing import tlog


def _inspect_bundle(bundle_path: str) -> tuple[int, float, str]:
    """快速物理扫描构建产物的页面数量与体积"""
    total_files, total_bytes, html_pages = 0, 0, 0
    if bundle_path and os.path.exists(bundle_path) and os.path.isdir(bundle_path):
        try:
            for root, _, files in os.walk(bundle_path):
                total_files += len(files)
                for f in files:
                    try:
                        st = os.stat(os.path.join(root, f))
                        total_bytes += st.st_size
                        if f.lower().endswith(".html"):
                            html_pages += 1
                    except Exception:
                        pass
        except Exception:
            pass

    size_kb = round(total_bytes / 1024, 2)
    size_formatted = f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb / 1024, 2)} MB"
    effective_pages = html_pages if html_pages > 0 else total_files
    return effective_pages, size_kb, size_formatted


def inspect_doc_bundle_artifact(bundle_path: str, doc_id: str, theme: str = "", imprint_id: str = "default") -> Dict[str, Any]:
    """快速物理探测单篇原稿对应的构建产物 HTML 页面数量、体积与公网相对路径"""
    if not doc_id:
        return {"pages_count": 0, "size_kb": 0.0, "size_formatted": "0 KB", "web_rel_path": ""}
    
    doc_stem = os.path.splitext(os.path.basename(doc_id))[0].lower()
    doc_dir = os.path.dirname(doc_id).lower()
    search_dirs = [bundle_path] if bundle_path and os.path.exists(bundle_path) else []
    if theme:
        for t_dir in [f"imprints/{imprint_id}/themes/{theme}/dist", f"themes/{theme}/dist", "dist"]:
            if os.path.exists(t_dir) and t_dir not in search_dirs:
                search_dirs.append(t_dir)

    matched_htmls, effective_root = [], bundle_path
    for s_dir in search_dirs:
        for root, _, files in os.walk(s_dir):
            for f in files:
                if f.lower().endswith(".html") and os.path.splitext(f)[0].lower() == doc_stem:
                    matched_htmls.append((os.path.join(root, f), s_dir))
        if matched_htmls:
            effective_root = s_dir
            break

    primary_html = None
    if matched_htmls:
        for p, r_root in matched_htmls:
            rel = os.path.relpath(p, r_root).replace("\\", "/")
            if doc_dir and doc_dir in rel.lower() and not any(rel.lower().startswith(x) for x in ["en/", "ja/", "fr/", "de/"]):
                primary_html = (p, r_root)
                break
        if not primary_html:
            for p, r_root in matched_htmls:
                rel = os.path.relpath(p, r_root).replace("\\", "/")
                if not any(rel.lower().startswith(x) for x in ["en/", "ja/", "fr/", "de/"]):
                    primary_html = (p, r_root)
                    break
        if not primary_html:
            primary_html = matched_htmls[0]
            
    total_bytes = sum(os.path.getsize(p) for p, _ in matched_htmls if os.path.exists(p)) if matched_htmls else 0
    size_kb = round(total_bytes / 1024, 2)
    size_fmt = f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb / 1024, 2)} MB"
    web_rel = os.path.relpath(primary_html[0], primary_html[1]).replace("\\", "/") if primary_html else (doc_id.rsplit(".", 1)[0].lower() + ".html")
    
    real_pages = len(matched_htmls)
    return {
        "pages_count": real_pages,
        "matched_pages": real_pages,
        "size_kb": size_kb if size_kb > 0 else 0.0,
        "size_formatted": size_fmt if total_bytes > 0 else "0.0 KB",
        "web_rel_path": web_rel
    }


def resolve_doc_title(doc_id: str, vault_root: str = "") -> str:
    """物理提取单篇原稿在 Frontmatter 中的真实标题"""
    if not doc_id: return ""
    for base in [vault_root, "vault", "."]:
        p = os.path.join(base, doc_id) if base else doc_id
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    in_fm = False
                    for _ in range(30):
                        line = f.readline()
                        if not line: break
                        s = line.strip()
                        if s == "---":
                            in_fm = not in_fm; continue
                        if in_fm and s.lower().startswith("title:"):
                            return s.split(":", 1)[1].strip().strip("\"'")
                        if not in_fm and s.startswith("# "):
                            return s[2:].strip()
            except Exception: pass
            break
    return os.path.splitext(os.path.basename(doc_id))[0]


def resolve_doc_channel_url(base_site_url: str, web_rel_path: str) -> str:
    """基于平台根地址与单文档相对路由合成单篇文档的具体可访问公网链接"""
    if not base_site_url or not web_rel_path:
        return base_site_url or ""
    return f"{base_site_url.rstrip('/')}/{web_rel_path.lstrip('/')}"


def normalize_batch_for_doc(engine: Any, b: Dict[str, Any], bundle_path: str) -> Dict[str, Any]:
    """智能纠偏历史批次中的单文档真实统计数据与公网文章链接"""
    trig = b.get("trigger_source") or ""
    targets = b.get("targets") or b.get("targets_json") or {}
    if isinstance(targets, str):
        try: targets = json.loads(targets)
        except Exception: targets = {}
    doc_id = trig.split("vault_drawer:", 1)[1] if trig.startswith("vault_drawer:") else targets.get("_trigger_doc")
    if doc_id:
        v_root = getattr(engine, "vault_root", "") or (getattr(engine.config, "vault_root", "") if hasattr(engine, "config") else "")
        b["doc_title"] = resolve_doc_title(doc_id, v_root)
        b["doc_id"] = doc_id
        theme = b.get("theme") or (getattr(engine, "active_theme", "default") if engine else "default")
        imp_id = b.get("imprint_id") or "default"
        doc_stat = inspect_doc_bundle_artifact(bundle_path, doc_id, theme=theme, imprint_id=imp_id)
        real_pages = doc_stat["pages_count"]
        real_kb = doc_stat["size_kb"]
        doc_web_rel = doc_stat.get("web_rel_path") or ""
        needs_fix = (b.get("pages_count") != real_pages) or (b.get("bundle_size_kb") != real_kb) or any(
            t.get("url") and not t.get("url").endswith((".html", ".htm"))
            for k, t in targets.items() if not k.startswith("_") and isinstance(t, dict)
        )
        if needs_fix:
            b["pages_count"] = real_pages
            b["bundle_size_kb"] = real_kb
            updated_targets = dict(targets)
            logs_str = b.get("logs_excerpt") or ""
            for ch, tinfo in updated_targets.items():
                if ch.startswith("_") or not isinstance(tinfo, dict): continue
                curr_url = tinfo.get("url", "")
                if curr_url and not curr_url.endswith((".html", ".htm")):
                    site_u = curr_url
                    doc_u = resolve_doc_channel_url(curr_url, doc_web_rel)
                    tinfo["site_url"] = site_u
                    tinfo["url"] = doc_u
                    if logs_str:
                        logs_str = logs_str.replace(f"线上公网: {site_u}", f"线上公网: {doc_u}")
            b["targets"] = updated_targets
            b["targets_json"] = updated_targets
            b["logs_excerpt"] = logs_str
            meta = getattr(engine, "meta", None)
            if meta and hasattr(meta, "update_hosting_deploy_batch"):
                try:
                    meta.update_hosting_deploy_batch(
                        batch_id=b["batch_id"], pages_count=real_pages,
                        bundle_size_kb=real_kb, targets_json=updated_targets,
                        logs_excerpt=logs_str
                    )
                except Exception: pass
    return b


def record_global_deploy_batch(
    engine: Any,
    bundle_path: str,
    deployment_results: Dict[str, Any],
    duration_sec: Optional[float] = None
) -> Optional[str]:
    """
    🌐 将全域发布的部署成果同步写入 hosting_deploy_records 表
    """
    if not deployment_results or not isinstance(deployment_results, dict):
        return None
    if deployment_results.get("status") == "skipped":
        return None

    summary = deployment_results.get("summary") or {}
    channels_summary = summary.get("channels") or []
    if not channels_summary:
        return None

    try:
        imprint_id = getattr(engine, "imprint_id", "default") or "default"
        theme = getattr(engine, "active_theme", "default") or "default"
        pages_count, size_kb, size_formatted = _inspect_bundle(bundle_path)

        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        ch_details = deployment_results.get("channels", {})
        targets_json = {}
        for ch in channels_summary:
            cid = ch.get("id")
            if not cid:
                continue
            st = "SUCCESS" if ch.get("status") == "success" else "FAILED"
            ch_item = ch_details.get(cid) or {}
            if not ch_item:
                for k, v in ch_details.items():
                    if k.lower().startswith(cid) or cid in k.lower():
                        ch_item = v
                        break
            ch_dur = ch.get("duration_sec") or ch_item.get("duration_sec") or 0.0
            ch_at = ch.get("deployed_at") or ch_item.get("deployed_at") or now_str
            targets_json[cid] = {
                "status": st,
                "url": ch.get("url") or "",
                "error": ch.get("error") or "",
                "duration_sec": ch_dur,
                "deployed_at": ch_at
            }

        total_ch = summary.get("total_channels", len(channels_summary))
        fail_cnt = summary.get("fail_count", 0)
        success_cnt = summary.get("success_count", total_ch - fail_cnt)

        if fail_cnt == 0:
            overall_status = "SUCCESS"
        elif success_cnt > 0:
            overall_status = "PARTIAL_SUCCESS"
        else:
            overall_status = "FAILED"

        dur = round(duration_sec, 2) if duration_sec is not None else 0.0
        batch_id = f"deploy_{int(time.time())}_{uuid.uuid4().hex[:6]}"

        # 组织终端流水日志：优先直接使用物理部署执行时原汁原味的时间推移流水
        proc_logs = deployment_results.get("process_logs")
        if proc_logs and isinstance(proc_logs, list):
            first_ts = proc_logs[0][1:9] if (len(proc_logs[0]) >= 10 and proc_logs[0].startswith("[")) else now_str.split(" ")[-1]
            bundle_line = f"[{first_ts}] [BUNDLE] 物理产物就绪: 主题={theme}, 页面数={pages_count}, 体积={size_formatted} (批次: #{batch_id.split('_')[-1]})"
            if len(proc_logs) > 1:
                log_lines = [proc_logs[0], bundle_line] + proc_logs[1:]
            else:
                log_lines = [bundle_line] + proc_logs
        else:
            log_lines = [
                f"[{now_str.split(' ')[-1]}] [INIT] 全域发布驱动整站部署任务启动 (批次: #{batch_id.split('_')[-1]})",
                f"[{now_str.split(' ')[-1]}] [BUNDLE] 物理产物就绪: 主题={theme}, 页面数={pages_count}, 体积={size_formatted}",
                f"[{now_str.split(' ')[-1]}] [ROUTING] 目标平台列表: {', '.join(targets_json.keys())}"
            ]
            for cid, t_info in targets_json.items():
                st_text = t_info.get("status", "UNKNOWN")
                url_text = t_info.get("url")
                err_text = t_info.get("error")
                ch_d = t_info.get("duration_sec", 0.0)
                if st_text == "SUCCESS":
                    u_str = f" -> 线上地址: {url_text}" if url_text else ""
                    log_lines.append(f"[{now_str.split(' ')[-1]}] [SUCCESS] 平台 [{cid}] 部署完成{u_str} (耗时 {ch_d}s)")
                else:
                    log_lines.append(f"[{now_str.split(' ')[-1]}] [ERROR] 平台 [{cid}] 部署失败: {err_text or '未知异常'} (耗时 {ch_d}s)")
            log_lines.append(f"[{now_str.split(' ')[-1]}] [FINISH] 全域部署完成，总状态: {overall_status}，总耗时: {dur}s")

        logs_excerpt = "\n".join(log_lines)

        meta = getattr(engine, "meta", None)
        if meta and hasattr(meta, "create_hosting_deploy_batch"):
            meta.create_hosting_deploy_batch(
                batch_id=batch_id,
                trigger_source="global_publish",
                imprint_id=imprint_id,
                theme=theme,
                pages_count=pages_count,
                bundle_size_kb=size_kb,
                targets_json=targets_json,
                overall_status=overall_status,
                started_at=now_str,
                logs_excerpt=logs_excerpt
            )
            if hasattr(meta, "update_hosting_deploy_batch"):
                meta.update_hosting_deploy_batch(
                    batch_id=batch_id,
                    overall_status=overall_status,
                    duration_sec=dur,
                    targets_json=targets_json,
                    logs_excerpt=logs_excerpt
                )
            tlog.info(f"📜 [网站发布历史] 已将全域发布成果记录至批次账本: {batch_id} (平台数: {len(targets_json)}, 状态: {overall_status})")
            return batch_id
    except Exception as e:
        tlog.warning(f"⚠️ [全域发布历史记录桥接] 写入发布批次异常: {e}")

    return None
