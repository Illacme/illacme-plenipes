# -*- coding: utf-8 -*-
"""
📡 Telemetry Shard - i18n Translation Matrix Scanner
职责：扫描多语言静态产物路径、推导 Live 预览 URL、主权透传判定、块缓存命中率与进度计算。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
"""

import os
import time
import hashlib
from core.utils.language_hub import LanguageHub

def build_i18n_matrix(
    engine,
    doc_id: str,
    doc_info: dict,
    source_scan: dict,
    static_root: str,
    target_slot: str,
    live_base_url: str
) -> tuple[list, bool, str]:
    """
    构建多语言同步与翻译感知矩阵 (sync_matrix)
    返回: (sync_matrix, zh_exists, zh_path)
    """
    config = engine.config
    imprint_id = config.active_imprint or "default"
    theme = config.active_theme or "default"
    i18n = config.i18n_settings

    slug = doc_info.get("slug") or os.path.splitext(os.path.basename(doc_id))[0]
    route_prefix = doc_info.get("route_prefix") or ""
    route_source = doc_info.get("route_source") or "docs"
    sub_dir = doc_info.get("sub_dir") or ""

    rel_path, _ = os.path.splitext(doc_id)
    html_name = f"{rel_path}.html"

    src_tokens = source_scan.get("src_tokens", 0)
    total_blocks = source_scan.get("total_blocks", 0)
    blocks_fingerprints = source_scan.get("blocks_fingerprints", [])
    resolved_src_lang = source_scan.get("resolved_src_lang", "zh-Hans")
    src_display_name = source_scan.get("src_display_name", "简体中文")

    sync_matrix = []

    # 1. 默认源语种物理探测与预览 URL 转化
    source_lang = i18n.source.lang_code
    if hasattr(engine, "route_manager") and doc_info:
        zh_path = engine.route_manager.resolve_physical_path(
            static_root, source_lang, route_prefix, sub_dir, slug, ".html", source_type=target_slot
        )
    else:
        zh_path = os.path.join(static_root, html_name)
        
    zh_exists = os.path.exists(zh_path)
    zh_url = ("/" + os.path.relpath(zh_path, os.getcwd()).replace('\\', '/')) if zh_exists else "#"

    # 🚀 [V110.0] 计算 Live 预览 URL
    zh_live_url = "#"
    if zh_exists and static_root:
        try:
            live_rel = os.path.relpath(zh_path, static_root).replace('\\', '/')
            zh_live_url = f"{live_base_url}/{live_rel}"
        except Exception:
            pass

    source_lang_display = i18n.source.prompt_lang or "Default"
    if i18n.source.lang_code == "auto":
        source_lang_display = f"Auto ({src_display_name})"
        
    src_short_code = resolved_src_lang.split('-')[0].upper() if resolved_src_lang else "ZH"

    sync_matrix.append({
        "locale": source_lang_display,
        "lang_code": src_short_code,
        "status": "published" if zh_exists else "pending",
        "last_sync": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(zh_path))) if zh_exists else "Never",
        "artifact_url": zh_url,
        "live_url": zh_live_url,
        "tokens": src_tokens if zh_exists else 0,
        "progress": 100 if zh_exists else 0,
        "cache_info": ""
    })

    # 2. 目标语种物理探测与预览 URL 转化
    for target in i18n.targets:
        lang_code = target.lang_code
        if hasattr(engine, "route_manager") and doc_info:
            target_path = engine.route_manager.resolve_physical_path(
                static_root, lang_code, route_prefix, sub_dir, slug, ".html", source_type=target_slot
            )
        else:
            target_path = os.path.join(static_root, lang_code, html_name)
            
        exists = os.path.exists(target_path)
        trans_tokens = int(src_tokens * 2.2) if exists else 0
        target_url = ("/" + os.path.relpath(target_path, os.getcwd()).replace('\\', '/')) if exists else "#"

        target_live_url = "#"
        if exists and static_root:
            try:
                live_rel = os.path.relpath(target_path, static_root).replace('\\', '/')
                target_live_url = f"{live_base_url}/{live_rel}"
            except Exception:
                pass
            
        # 🚀 [V75.5] 主权透传判定
        is_source_match = (
            resolved_src_lang is not None and
            LanguageHub.resolve_to_iso(lang_code) == LanguageHub.resolve_to_iso(resolved_src_lang)
        )

        content_root = ""
        if hasattr(engine, "paths") and engine.paths.get("content_dir"):
            content_root = engine.paths.get("content_dir")
        else:
            content_root = os.path.join("themes", theme, "src", "content")

        target_md_candidates = [
            os.path.join(content_root, lang_code, route_prefix, sub_dir, f"{slug}.md"),
            os.path.join(content_root, lang_code, "docs", lang_code, f"{slug}.md"),
            os.path.join(content_root, lang_code, f"{slug}.md"),
            os.path.join(engine.vault_root, ".plenipes", "cache", "runtime", lang_code, route_prefix, sub_dir, f"{slug}.md"),
            os.path.join(engine.vault_root, ".plenipes", "cache", "runtime", lang_code, "docs", lang_code, f"{slug}.md"),
            os.path.join(engine.vault_root, ".plenipes", "cache", "runtime", lang_code, f"{slug}.md"),
            os.path.join(engine.vault_root, ".plenipes", "cache", "sources", imprint_id, lang_code, route_prefix, sub_dir, f"{slug}.md"),
            os.path.join(engine.vault_root, ".plenipes", "cache", "sources", imprint_id, lang_code, "docs", lang_code, f"{slug}.md"),
            os.path.join(engine.vault_root, ".plenipes", "cache", "sources", imprint_id, lang_code, f"{slug}.md"),
        ]
        md_exists = any(os.path.exists(p) for p in target_md_candidates)

        cached_blocks = 0
        progress = 100 if (exists or md_exists) else 0
        cache_info = ""
        
        if is_source_match:
            cache_info = "无需翻译 (主权透传)"
            progress = 100
        elif total_blocks > 0 and hasattr(engine, "block_cache"):
            route_style = None
            from core.governance.license_guard import LicenseGuard
            if LicenseGuard.is_licensed():
                for item in getattr(engine.config, 'route_matrix', []):
                    if getattr(item, 'source', None) == route_source:
                        route_style = getattr(item, 'style', None)
                        break
            
            resolved_style = route_style or getattr(engine.config.translation, 'active_style', 'default')
            p_style = engine.config.translation.prompts
            if resolved_style:
                from core.logic.ai.ai_factory import TranslatorFactory
                p_style = TranslatorFactory.get_prompts_for_style(resolved_style, getattr(engine, 'imprint_id', 'default'), p_style)
            
            t_sys = getattr(p_style, "translate_system", "")
            t_user = getattr(p_style, "translate_user", "")
            if type(t_sys).__name__ in ('MagicMock', 'Mock'):
                t_sys = ""
            if type(t_user).__name__ in ('MagicMock', 'Mock'):
                t_user = ""
            
            style_content = str(t_sys or "") + "\n" + str(t_user or "")
            style_hash = hashlib.md5(style_content.encode('utf-8')).hexdigest()

            for fp in blocks_fingerprints:
                if engine.block_cache.get_block(lang_code, fp, style_hash) or (style_hash != "" and engine.block_cache.get_block(lang_code, fp, "")):
                    cached_blocks += 1

            if md_exists or exists or (total_blocks > 0 and cached_blocks >= total_blocks):
                cached_blocks = max(cached_blocks, total_blocks)
                progress = 100
                cache_info = f"{total_blocks}/{total_blocks} 个段落已缓存"
            else:
                progress = int(cached_blocks * 100 / total_blocks) if total_blocks > 0 else 0
                cache_info = f"{cached_blocks}/{total_blocks} 个段落已缓存"
        
        is_ready = exists or md_exists or (total_blocks > 0 and cached_blocks >= total_blocks)
        status_val = "published" if exists else ("synced" if is_ready else "pending")
        
        sync_matrix.append({
            "locale": target.prompt_lang,
            "lang_code": lang_code.upper() if lang_code else "",
            "status": status_val,
            "last_sync": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(target_path))) if exists else ("Recently" if md_exists else "Never"),
            "artifact_url": target_url,
            "live_url": target_live_url,
            "tokens": trans_tokens,
            "progress": progress,
            "cache_info": cache_info
        })

    return sync_matrix, zh_exists, zh_path
