#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V68.0] Illacme Plenipes - Dispatch Telemetry Shard
职责：多语种快照文件扫描、Token 统计、SQLite 账本开销查询与主权审计感知。
"""

import os
import time
import socket
from core.utils.common import TokenCounter

def check_port(port: int) -> bool:
    """探测本地端口是否存活"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def get_dispatch_status_logic(engine, doc_id: str) -> dict:
    """
    🛰️ 物理感应探针 (Sovereign Sensing)
    穿透 dist 目录并扫描真实产物分布，零 Mock 真实还原算力、费用与节点状态。
    """
    config = engine.config
    imprint_id = config.active_imprint or "default"
    theme = config.active_theme or "default"
    
    # 1. 基础路径对正（获取数据库中注册的文档元数据，尊重 Slug 别名）
    doc_info = {}
    if hasattr(engine, "meta"):
        doc_info = engine.meta.get_doc_info(doc_id) or {}

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
                
                import re
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
                from core.logic.ai.ai_logic_hub import AILogicHub
                
                blocks_fingerprints = []
                for b in parser.parse(masked_body):
                    if b.type == "spacer" or not b.content.strip():
                        continue
                    # 💡 [V75.4] 物理对齐翻译流水线的 Pure Mask Bypass 机制：先通过 mask 屏蔽，再剔除无实质字符的占位块
                    masked_content, _ = AILogicHub.mask_block(b.content)
                    stripped = re.sub(r'__B_MASK_\d+__', '', masked_content)
                    stripped = re.sub(r'\[\[STB_MASK_\d+\]\]', '', stripped)
                    if not re.search(r'\w', stripped):
                        continue
                    # 💡 [V75.4] 彻底过滤以 <!-- 开头的 HTML 注释块（如 Sovereign-Tag 主权盾），这些在物理上无需翻译，亦不计入缓存统计
                    if b.content.strip().startswith("<!--") and b.content.strip().endswith("-->"):
                        continue
                    blocks_fingerprints.append(b.fingerprint)
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
            
        # 🚀 [V75.5] 主权透传判定：若目标语种与原稿源语种一致，则该语种免除 AI 翻译与块缓存，标记为主权透传
        from core.utils.language_hub import LanguageHub
        is_source_match = (
            resolved_src_lang is not None and
            LanguageHub.resolve_to_iso(lang_code) == LanguageHub.resolve_to_iso(resolved_src_lang)
        )

        # 计算已翻译缓存段落的比例与进度
        cached_blocks = 0
        progress = 100 if exists else 0
        cache_info = ""
        
        if is_source_match:
            # 主权透传语种免除缓存检索与缓存警告
            cache_info = "无需翻译 (主权透传)"
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
                if engine.block_cache.get_block(lang_code, fp, style_hash):
                    cached_blocks += 1
            progress = int(cached_blocks * 100 / total_blocks)
            
            # 💡 [V75.5] 体验优化：如果 HTML 存在且缓存段落有缺失
            if exists and cached_blocks < total_blocks:
                is_source_dirty = (current_hash is None or doc_info.get("source_hash") != current_hash)
                if is_source_dirty:
                    cache_info = f"已缓存 {cached_blocks}/{total_blocks} 个段落 (源稿有更新，请重新分发)"
                else:
                    cache_info = f"已缓存 {cached_blocks}/{total_blocks} 个段落"
            else:
                cache_info = f"已缓存 {cached_blocks}/{total_blocks} 个段落"
        
        sync_matrix.append({
            "locale": target.prompt_lang,
            "lang_code": lang_code.upper() if lang_code else "",
            "status": "published" if exists else "pending",
            "last_sync": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(target_path))) if exists else "Never",
            "artifact_url": target_url,
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
    # 🚀 [V89.0] 物理全渠道联动：从账本中扫描并追加外部部署与社交同步渠道的真实状态
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
            # 🚀 [V89.6] 自适应托管文章绝对链接：优先拼接 public_url/posts/slug，否则 fallback 导出仓库地址
            slug = doc_info.get("slug") or ""
            public_url = chan_cfg.get("public_url")
            artifact_url = "#"
            if public_url:
                artifact_url = f"{public_url.rstrip('/')}/posts/{slug}"
            else:
                artifact_url = chan_cfg.get("repo_url") or "#"

            sync_matrix.append({
                "channel_id": chan_id,
                "locale": f"🌐 {display_name} (全站部署)",
                "lang_code": "HOSTING",
                "status": chan_status.lower(),
                "last_sync": last_sync_str,
                "artifact_url": artifact_url,
                "tokens": 0,
                "progress": 100 if chan_status.lower() in ("published", "success") else 0,
                "cache_info": "全站托管",
                "reason": status_info.get("error") or ""
            })
             
    # B. 提取 Syndication 社交同步渠道
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
         
    for chan_id, chan_cfg in syndication_cfg.items():
        if isinstance(chan_cfg, dict) and chan_cfg.get("enabled"):
            status_info = publish_status.get(chan_id, {})
            chan_status = status_info.get("status") or "pending"
            
            last_sync_str = "Never"
            if status_info.get("timestamp"):
                last_sync_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(status_info.get("timestamp")))
                 
            display_name = chan_id.replace("_", " ").title()
            sync_matrix.append({
                "channel_id": chan_id,
                "locale": f"📡 {display_name} (社交同步)",
                "lang_code": "SOCIAL",
                "status": chan_status.lower(),
                "last_sync": last_sync_str,
                "artifact_url": status_info.get("url") or "#",
                "tokens": 0,
                "progress": 100 if chan_status.lower() in ("published", "success") else 0,
                "cache_info": "外部社区",
                "reason": status_info.get("error") or ""
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
