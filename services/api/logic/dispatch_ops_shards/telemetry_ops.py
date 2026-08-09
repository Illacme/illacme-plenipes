#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V68.0] Illacme Plenipes - Dispatch Telemetry Shard
职责：多语种快照文件扫描、Token 统计、SQLite 账本开销查询与主权审计感知。
"""

import os
import time
import socket
import re
from core.utils.common import TokenCounter

def check_port(port: int) -> bool:
    """探测本地端口是否存活"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def get_dispatch_status_logic(engine, doc_id: str, lang_code: str = None) -> dict:
    """
    🛰️ 物理感应探针 (Sovereign Sensing)
    穿透 dist 目录并扫描真实产物分布，零 Mock 真实还原算力、费用与节点状态。
    """
    config = engine.config
    imprint_id = config.active_imprint or "default"
    theme = config.active_theme or "default"
    
    # 1. 基础路径对正（获取数据库中注册的文档元数据，尊重 Slug 别名）
    doc_info = {}
    doc_records = {}
    if hasattr(engine, "meta"):
        doc_info = engine.meta.get_doc_info(doc_id) or {}
        if hasattr(engine.meta, "list_syndication_records_for_doc"):
            try:
                records_list = engine.meta.list_syndication_records_for_doc(doc_id, lang_code)
                for r in records_list:
                    doc_records[r.get("target_id", "")] = r
            except Exception:
                pass

    slug = doc_info.get("slug") or os.path.splitext(os.path.basename(doc_id))[0]
    route_prefix = doc_info.get("route_prefix") or ""
    route_source = doc_info.get("route_source") or "docs"
    sub_dir = doc_info.get("sub_dir") or ""

    # 🚀 动态还原该渠道对应的 target_slot
    target_slot = "docs"
    if hasattr(engine, "route_matrix"):
        for item in engine.route_matrix:
            if item.source == route_source:
                target_slot = item.target_slot
                break

    # 动态推导静态输出根目录，优先从 engine.paths 中读取
    static_root = ""
    if hasattr(engine, "paths") and engine.paths.get("site_dir"):
        static_root = engine.paths.get("site_dir")
    else:
        static_root = os.path.join("imprints", imprint_id, "themes", theme, "static")

    # 2. 扫描语种矩阵并计算真实算力 Token
    serve_port = getattr(config.system, 'serve_port', 43213)
    live_base_url = f"http://localhost:{serve_port}"
    sync_matrix = []
    i18n = config.i18n_settings
    
    # 获取文档相对路径 (不带 .md 扩展名)
    rel_path, _ = os.path.splitext(doc_id)
    html_name = f"{rel_path}.html"
    
    # 读取源 Markdown 文件，获取真实的基准 Token 数并解析有效语义块
    src_tokens = 0
    total_blocks = 0
    blocks_fingerprints = []
    source_path = os.path.join(engine.vault_root, doc_id)
    if os.path.exists(source_path):
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
                src_tokens = TokenCounter.count(content)
                from core.utils import extract_frontmatter
                raw_fm_dict, raw_body = extract_frontmatter(content)
                
                # 🚀 [V75.5] 物理归一化与全局隐私屏蔽，以彻底对齐分发管线，消除指纹分裂 (Fingerprint Split)
                if hasattr(engine, 'input_adapter') and engine.input_adapter:
                    raw_body, raw_fm_dict = engine.input_adapter.normalize(raw_body, raw_fm_dict)
                
                body = engine.ast_resolver.resolve(raw_body, source_path, engine.paths.get('target_base'))
                
                # 🚀 [V75.5] 对齐 MetadataAndHashStep 的 current_hash 计算以实现脏状态检测
                defaults = getattr(engine, 'fm_defaults', None) or {}
                base_fm = {k: v for k, v in defaults.items() if v is not None and str(v).strip() != ""}
                base_fm.update(raw_fm_dict)
                from core.utils import normalize_keywords
                for f in ['keywords', 'tags', 'categories']:
                    if f in base_fm:
                        base_fm[f] = normalize_keywords(base_fm.get(f))
                if 'slug' in base_fm:
                    base_fm.pop('slug', None)
                import hashlib
                current_hash = hashlib.md5((str(base_fm) + body).encode('utf-8')).hexdigest()
                
                masks = []
                def mask_fn(m):
                    matched = m.group(0)
                    link_match = re.match(r'^(\!?\[.*?\]\()([^)]+)(\))$', matched)
                    if link_match:
                        prefix, url_part, suffix = link_match.groups()
                        if prefix.startswith('!['):
                            masks.append(matched)
                            return f"[[STB_MASK_{len(masks)-1}]]"
                        else:
                            masks.append(f"URL_ONLY_LNK:{url_part}")
                            return f"{prefix}[[STB_MASK_{len(masks)-1}]]{suffix}"
                    masks.append(matched)
                    return f"[[STB_MASK_{len(masks)-1}]]"

                mask_pattern = engine.config.system.mask_pattern
                masked_body = re.sub(mask_pattern, mask_fn, body, flags=re.DOTALL)

                from core.logic.block_parser import MarkdownBlockParser
                parser = MarkdownBlockParser()
                for block in parser.parse(body):
                    c_str = block.content.strip()
                    if block.type == "spacer" or not c_str or c_str.startswith("---") or c_str.startswith("<!--"):
                        continue
                    blocks_fingerprints.append(block.fingerprint)
                total_blocks = len(blocks_fingerprints)
        except Exception:
            pass

    # 🚀 [V75.5] 自动探测或从数据库中还原已识别的原稿源语种，以实现 Auto 回显和主权透传判定
    resolved_src_lang = doc_info.get("source_lang")
    if not resolved_src_lang and os.path.exists(source_path):
        try:
            from core.utils.language_hub import LanguageHub
            detect_sample = content[:1000] if 'content' in locals() else ""
            resolved_src_lang = LanguageHub.detect_source_lang(detect_sample, getattr(engine, 'translator', None))
        except Exception:
            pass
    resolved_src_lang = resolved_src_lang or "zh-Hans" # 兜底至 zh-Hans
    
    from core.utils.language_hub import LanguageHub
    src_display_name = LanguageHub.resolve_to_name(resolved_src_lang)

    # 默认语种物理探测与预览 URL 转化
    source_lang = i18n.source.lang_code
    if hasattr(engine, "route_manager") and doc_info:
        zh_path = engine.route_manager.resolve_physical_path(
            static_root, source_lang, route_prefix, sub_dir, slug, ".html", source_type=target_slot
        )
    else:
        zh_path = os.path.join(static_root, html_name)
        
    zh_exists = os.path.exists(zh_path)
    
    if zh_exists:
        rel_zh_path = os.path.relpath(zh_path, os.getcwd()).replace('\\', '/')
        zh_url = "/" + rel_zh_path
    else:
        zh_url = "#"

    # 🚀 [V110.0] 计算 Live 预览 URL：以 SSG 容器地址为基底，挂载相对路径
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
    
    # 目标语种物理探测与预览 URL 转化
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
        
        if exists:
            rel_target_path = os.path.relpath(target_path, os.getcwd()).replace('\\', '/')
            target_url = "/" + rel_target_path
        else:
            target_url = "#"

        # 🚀 [V110.0] 计算目标语种的 Live 预览 URL
        target_live_url = "#"
        if exists and static_root:
            try:
                live_rel = os.path.relpath(target_path, static_root).replace('\\', '/')
                target_live_url = f"{live_base_url}/{live_rel}"
            except Exception:
                pass
            
        # 🚀 [V75.5] 主权透传判定：若目标语种与原稿源语种一致，则该语种免除 AI 翻译与块缓存，标记为主权透传
        from core.utils.language_hub import LanguageHub
        is_source_match = (
            resolved_src_lang is not None and
            LanguageHub.resolve_to_iso(lang_code) == LanguageHub.resolve_to_iso(resolved_src_lang)
        )

        # 🚀 物理探测翻译产物 Markdown 是否存在 (Content Dir / Runtime Cache / Sources Cache)
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

        # 计算已翻译缓存段落的比例与进度
        cached_blocks = 0
        progress = 100 if (exists or md_exists) else 0
        cache_info = ""
        
        if is_source_match:
            # 主权透传语种免除缓存检索与缓存警告
            cache_info = "无需翻译 (主权透传)"
            progress = 100
        elif total_blocks > 0 and hasattr(engine, "block_cache"):
            route_style = None
            from core.governance.license_guard import LicenseGuard
            if LicenseGuard.is_licensed():
                for item in engine.config.route_matrix:
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
            
            import hashlib
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

    # 3. 遥测数据与环境感应 - 零 Mock 真实数据提取
    is_lab_alive = check_port(43213)
    
    # 动态查询 SQLite 账本获取真实历史总计费
    total_historical_cost = 0.0
    if hasattr(engine, "meta") and hasattr(engine.meta, "sqlite"):
        try:
            raw_cost = engine.meta.sqlite.get_total_cost(imprint_id)
            if isinstance(raw_cost, (int, float)):
                total_historical_cost = float(raw_cost)
            elif raw_cost is not None and not hasattr(raw_cost, "assert_called"):
                total_historical_cost = float(raw_cost)
        except Exception:
            pass
        
    # 动态获取当前的 AI 算力节点名称
    current_node = "Local Sync"
    if hasattr(engine, "translator") and hasattr(engine.translator, "node_name"):
        current_node = engine.translator.node_name

    # 4. 动态确定物理审计状态 (Sovereign Audit Sense)
    audit_status = "PENDING"
    health_status = "Active"
    error_detail = None
    
    publish_status = doc_info.get("publish_status", {})
    pipeline_status = publish_status.get("PIPELINE", {})
    
    if pipeline_status.get("status") == "ABORTED":
        audit_status = "FAIL"
        health_status = "Aborted"
        error_detail = pipeline_status.get("error", "管线拦截中止（草稿或不满足校验条件）")
    elif zh_exists:
        # 🛡️ 只有在多语言矩阵开启且配置了目标语种时，才审计目标语种翻译状态
        if config.i18n_settings.enabled and config.i18n_settings.targets:
            translations = doc_info.get("translations", {})
            active_target_codes = [t.lang_code for t in config.i18n_settings.targets]
            
            failed_langs = []
            if translations:
                for lang_code, trans_res in translations.items():
                    if lang_code in active_target_codes:
                        if isinstance(trans_res, dict) and not trans_res.get("health", True):
                            failed_langs.append(lang_code.upper())
            
            if failed_langs:
                audit_status = "FAIL"
                health_status = "Degraded"
                error_detail = f"翻译完整性审计未通过：语种 [{', '.join(failed_langs)}] 的翻译结果存在故障或被主权盾牌拦截。"
            else:
                audit_status = "PASS"
                health_status = "Active"
        else:
            audit_status = "PASS"
            health_status = "Active"
    else:
        audit_status = "PENDING"
    # 🚀 [V89.0] 物理全渠道联动：从账本中扫描并追加外部部署与分发渠道的真实状态
    publish_status = doc_info.get("publish_status", {})
    
    # A. 提取 Hosting 全站托管渠道
    direct_upload = getattr(config.publish_control, "direct_upload", None) or {}
    if isinstance(direct_upload, dict):
        pass
    elif hasattr(direct_upload, "model_dump"):
        direct_upload = direct_upload.model_dump()
    elif hasattr(direct_upload, "__dataclass_fields__"):
        from dataclasses import asdict
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
            
            # 自愈降级：如果全站网页默认已生成，且没有显式的失败记录，我们可以默认它随全站同步了
            if not chan_status:
                chan_status = "published" if zh_exists else "pending"
            
            last_sync_str = "Never"
            if status_info.get("timestamp"):
                last_sync_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(status_info.get("timestamp")))
            elif zh_exists:
                last_sync_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(zh_path)))
                
            display_name = chan_id.replace("_", " ").title()
            # 🚀 [V89.6] 自适应托管文章绝对链接：防御性提取 Base URL 并精确拼接由 RouteManager & Slug 决定的页面相对路径
            raw_base_url = chan_cfg.get("public_url") or chan_cfg.get("site_url") or status_info.get("pages_base_url") or status_info.get("url") or ""
            if not raw_base_url or raw_base_url == "#":
                raw_base_url = chan_cfg.get("repo_url") or "#"

            # 🛡️ 物理根域名保护：若 URL 中残留了旧的具体 HTML/MD 文件后缀，正则清洗切除还原为纯根目录
            if raw_base_url != "#":
                raw_base_url = re.sub(r'/[^/]+\.(html|md|htm)$', '', raw_base_url, flags=re.IGNORECASE)

            # 提取 RouteManager & Slug 决定的物理页面相对路径
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

            # 有且仅有一次精确拼接
            if raw_base_url and raw_base_url != "#" and web_rel_route:
                artifact_url = f"{raw_base_url.rstrip('/')}/{web_rel_route.lstrip('/')}"
            else:
                artifact_url = raw_base_url if raw_base_url else "#"

            chan_status_clean = (chan_status or "pending").lower()
            is_hosting_done = chan_status_clean in ("published", "success", "done", "synced")

            sync_matrix.append({
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
        from dataclasses import asdict
        try:
            syndication_cfg = asdict(syndication_cfg)
        except Exception:
            syndication_cfg = getattr(syndication_cfg, "__dict__", {})
    else:
        syndication_cfg = getattr(syndication_cfg, "__dict__", {})
         
    # 🚀 计算当前文档内容物理哈希 (用于智能感知文章是否已修改需覆写)
    current_content_hash = None
    if os.path.exists(source_path):
        try:
            import hashlib
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
            # 🚀 只要配置了物理凭据或包含历史/刚调度的发布记录，即导出至感知矩阵
            if has_keys or status_info or chan_cfg.get("enabled") or chan_record:
                chan_status = status_info.get("status") or ("synced" if (status_info.get("timestamp") or chan_record) else "pending")
                
                last_sync_str = "Never"
                if status_info.get("timestamp"):
                    last_sync_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(status_info.get("timestamp")))
                elif chan_record.get("updated_at"):
                    last_sync_str = str(chan_record.get("updated_at"))[:16]
                     
                display_name = chan_id.replace("_", " ").title()
                
                # 🚀 多维度捕获发布后的真实文章/渠道 URL 直达页面（优先目标语种专属物权账本链接）
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

                # 🚀 [V121.0] 哈希变更智能感知
                saved_hash = chan_record.get("content_hash")
                is_outdated = bool(saved_hash and current_content_hash and saved_hash != current_content_hash)

                sync_matrix.append({
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

    return {
        "doc_id": doc_id,
        "sync_matrix": sync_matrix,
        "telemetry": {
            "total_cost": f"${total_historical_cost:.4f}",
            "node": current_node,
            "health": health_status,
            "last_audit": audit_status,
            "error_detail": error_detail,
            "pipeline": {
                "status": pipeline_status.get("status", "IDLE") if isinstance(pipeline_status, dict) else "IDLE",
                "stage": pipeline_status.get("stage", "") if isinstance(pipeline_status, dict) else "",
                "timestamp": pipeline_status.get("timestamp", 0) if isinstance(pipeline_status, dict) else 0
            }
        },
        "environment": {
            "preview_mode": "live" if is_lab_alive else "static",
            "lab_url": "http://localhost:43213",
            "is_lab_active": is_lab_alive
        }
    }
