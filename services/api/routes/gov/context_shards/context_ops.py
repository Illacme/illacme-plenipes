# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Context & System Diagnosis Ops
职责：承载系统上下文、诊断日志读取与健康状态监控的底层原子实现。
"""

import os
from core.runtime.engine_singleton import get_global_engine

def get_system_context_impl():
    """
    承载系统上下文及运行元数据构建的原子逻辑实现。
    """
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}

    from core.governance.imprint_manager import im
    from core.ui.delegate import DisplayDelegate
    from core.utils.language_hub import LanguageHub

    ai_cfg = engine.config.translation
    active_node = ai_cfg.primary_node
    active_provider = "Unknown"
    active_model = ai_cfg.primary_model or "Unknown"

    if active_node in ai_cfg.compute_nodes:
        node_cfg = ai_cfg.compute_nodes[active_node]
        active_provider = (getattr(node_cfg, "type", "") or "Unknown").upper()

    # 📡 物理算力容灾拓扑对正 (V75.12)
    primary_node = ai_cfg.primary_node or "Unknown"
    fallback_node = ai_cfg.fallback_node or "Unknown"
    primary_model = ai_cfg.primary_model or "Unknown"
    fallback_model = ai_cfg.fallback_model or "Unknown"
    
    primary_provider = "UNKNOWN"
    if primary_node in ai_cfg.compute_nodes:
        primary_provider = (getattr(ai_cfg.compute_nodes[primary_node], "type", "") or "UNKNOWN").upper()
        
    fallback_provider = "UNKNOWN"
    if fallback_node in ai_cfg.compute_nodes:
        fallback_provider = (getattr(ai_cfg.compute_nodes[fallback_node], "type", "") or "UNKNOWN").upper()

    strategy_str = ai_cfg.strategy.value if hasattr(ai_cfg.strategy, "value") else str(ai_cfg.strategy)

    active_imprint = im.get_active_imprint()

    theme_map = {
        "default": "Sovereign (default)",
        "starlight": "Starlight (official)",
        "docusaurus": "Docusaurus (classic)",
        "vitepress": "VitePress (next)",
        "nextra": "Nextra (docs)"
    }
    raw_theme = engine.active_theme
    display_theme = theme_map.get(raw_theme, f"Custom ({raw_theme})")


    from core.ingress.registry import ingress_registry
    ingress_cfg = engine.config.ingress_settings
    active_dialects = ingress_cfg.active_dialects or ["auto"]
    
    if "auto" in active_dialects:
        dialect_display = "自动感应 (Auto-Sensing)"
    else:
        active_dialect_id = active_dialects[0] if active_dialects else "generic"
        dialect_cls = ingress_registry.get_dialect(active_dialect_id)
        dialect_display = getattr(dialect_cls, "DISPLAY_NAME", active_dialect_id.upper()) if dialect_cls else active_dialect_id.upper()

    # 🛡️ 优雅解耦：直接从底层的 plugin_mapper 加载插件矩阵，避免循环引用 Hub 文件
    from services.api.routes.gov.plugin_mapper import assemble_plugin_matrix
    plugins = assemble_plugin_matrix()

    # 📡 算力状态检测
    enable_ai = getattr(ai_cfg, 'enable_ai', True) and not getattr(engine, 'no_ai', False)
    if not enable_ai:
        ai_status = "disabled"
        warning_msg = "AI 算力总控已关闭，系统运行于纯本地出版模式。"
    elif getattr(engine.translator, 'node_name', '') == 'fallback_mock':
        ai_status = "degraded"
        warning_msg = "当前版图的主力算力节点配置缺失，系统已自动切换至模拟/离线模式。"
    else:
        ai_status = "online"
        warning_msg = None

    return {
        "version": DisplayDelegate.get_system_version(engine.config),
        "imprint": active_imprint,
        "imprint_name": engine.config.imprint_name,
        "publishing_mode": getattr(engine.config.governance, 'publishing_mode', 'basic'),
        "theme": display_theme,
        "onboarding_required": engine.onboarding_required,
        "vault": {
            "root": engine.vault_root,
            "dialect": dialect_display
        },
        "ai": {
            "provider": active_provider,
            "model": active_model,
            "status": ai_status,
            "warning": warning_msg,
            "strategy": strategy_str.upper(),
            "primary": {
                "node": primary_node,
                "provider": primary_provider,
                "model": primary_model
            },
            "fallback": {
                "node": fallback_node,
                "provider": fallback_provider,
                "model": fallback_model
            }
        },
        "i18n": {
            "enabled": engine.config.i18n_settings.enabled,
            "source": getattr(engine.config.i18n_settings.source, 'name', '') or getattr(engine.config.i18n_settings.source, 'lang_code', 'ZH').upper(),
            "targets": [
                LanguageHub.resolve_to_native_name(t.lang_code if hasattr(t, 'lang_code') else str(t))
                for t in engine.config.i18n_settings.targets
            ]
        },
        "plugins": plugins # 🚀 [V74.88] 物理补全插件指纹，驱动前端联动逻辑
    }

def get_lessons_impl():
    """
    承载 lessons-learned 诊断记录加载的原子逻辑实现。
    """
    engine = get_global_engine()
    if not engine: return []
    path = engine._resolve_path(engine.config.get_lessons_learned_path())
    if os.path.exists(path):
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return []

def get_sync_stats_impl():
    """
    承载同步状态流量看板的原子逻辑实现。
    """
    engine = get_global_engine()
    if not engine: return {}
    
    from datetime import datetime
    
    # 1. 读取原始同步元数据
    path = engine._resolve_path(engine.config.get_sync_stats_path())
    sync_data = {}
    if os.path.exists(path):
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                sync_data = json.load(f)
        except: pass

    # 2. 丰富统计：文档规模、发布状态、字数
    docs = engine.meta.get_documents_snapshot()
    total_docs = len(docs)
    total_words = 0
    live_count = 0
    draft_count = 0
    
    lang_stats = {}
    source_lang = engine.config.i18n_settings.source.lang_code.lower() if getattr(engine.config.i18n_settings, 'source', None) else "zh"
    target_langs = [t.lang_code.lower() for t in engine.config.i18n_settings.targets] if getattr(engine.config.i18n_settings, 'targets', None) else []
    
    if isinstance(docs, dict):
        for rel_path, info in docs.items():
            if not isinstance(info, dict): continue
            seo_data = info.get("seo_data") if isinstance(info.get("seo_data"), dict) else {}
            word_count = seo_data.get("word_count") if isinstance(seo_data, dict) and isinstance(seo_data.get("word_count"), (int, float)) else 0
            total_words += word_count
            
            status_map = info.get("publish_status") if isinstance(info.get("publish_status"), dict) else {}
            live_channels = [ch for ch, s in status_map.items() if isinstance(s, dict) and str(s.get("status", "")).upper() in ("SUCCESS", "DONE")]
            if live_channels:
                live_count += 1
            else:
                draft_count += 1
                
            translations = info.get("translations") if isinstance(info.get("translations"), dict) else {}
            for lang, t_info in translations.items():
                if isinstance(t_info, dict) and (t_info.get("status") == "DONE" or t_info.get("health") is True or bool(t_info.get("seo"))):
                    lang_stats[lang.lower()] = lang_stats.get(lang.lower(), 0) + 1

    # 翻译覆盖率百分比
    translation_coverage = {}
    for lang in target_langs:
        cnt = lang_stats.get(lang, 0)
        coverage = round(cnt / total_docs * 100, 1) if total_docs > 0 else 0.0
        translation_coverage[lang] = {
            "translated_count": cnt,
            "coverage_percent": coverage
        }

    # 3. 丰富统计：知识图谱与双链健康 (优先融合 engine.link_graph 手写 Wikilinks 与 AI 高维图谱)
    total_nodes = 0
    total_links = 0
    isolated_nodes = 0
    broken_links = 0
    
    # 🚀 [V74.90] 物理优先：优先提取 link_graph 中的原生手写 Wikilinks
    link_graph = getattr(engine, "link_graph", {}) or {}
    if link_graph:
        total_nodes = len(link_graph)
        all_node_keys = set(link_graph.keys())
        
        for rel_path, data in link_graph.items():
            links = data.get("links", []) if isinstance(data, dict) else []
            # 过滤掉图片/静态资源，仅保留文本/文档类引用
            doc_links = [l for l in links if not l.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'))]
            total_links += len(doc_links)
            
            if len(doc_links) == 0:
                isolated_nodes += 1
                
            for target in doc_links:
                # 解析目标是否存在于文库中
                resolved = engine.meta.resolve_link(target) if hasattr(engine.meta, "resolve_link") else None
                if not resolved:
                    # 匹配文件名基名
                    found = any(
                        target == k or target == os.path.basename(k) or target == os.path.splitext(os.path.basename(k))[0]
                        for k in all_node_keys
                    )
                    if not found:
                        broken_links += 1
    elif hasattr(engine, "knowledge_graph") and engine.knowledge_graph:
        nodes = getattr(engine.knowledge_graph, "nodes", {})
        total_nodes = len(nodes)
        
        for node_id, node_data in nodes.items():
            connections = node_data.get("connections", {})
            manual = node_data.get("manual_connections", {})
            all_conn = {**connections, **manual}
            total_links += len(all_conn)
            
            if len(all_conn) == 0:
                isolated_nodes += 1
                
            for target_id in all_conn.keys():
                if target_id not in nodes:
                    broken_links += 1

    # 4. 读取最近算力账本
    recent_usage = []
    try:
        conn = engine.meta.sqlite._get_conn()
        cursor = conn.execute("""
            SELECT event_type, description, cost, timestamp
            FROM usage_ledger
            WHERE imprint_id = ?
            ORDER BY timestamp DESC
            LIMIT 5
        """, (engine.imprint_id,))
        for r in cursor.fetchall():
            rd = dict(r)
            if rd.get("timestamp"):
                # 转换时间戳为更易读的字符串格式
                import time
                rd["time_str"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rd["timestamp"]))
            recent_usage.append(rd)
    except Exception:
        pass

    # 🚀 [V74.89] 修复健康度漏洞：结合死链扣分与孤儿节点扣分，避免无链接时盲目显示 100 分假象
    if total_nodes == 0:
        health_score = 100
    elif total_links == 0:
        # 没有任何双链连接（100% 孤儿），处于未织就状态，基准健康度给 60 分
        health_score = 60
    else:
        broken_penalty = (broken_links / total_links) * 50
        isolated_penalty = (isolated_nodes / total_nodes) * 30
        health_score = max(0, min(100, int(100 - broken_penalty - isolated_penalty)))

    enriched_stats = {
        "imprint": engine.imprint_id,
        "processed_timestamp": sync_data.get("processed_timestamp", datetime.now().isoformat()),
        "engine_version": sync_data.get("engine_version", "V50.3"),
        "documents": {
            "total_count": total_docs,
            "total_word_count": total_words,
            "live_count": live_count,
            "draft_count": draft_count,
            "live_percent": round(live_count / total_docs * 100, 1) if total_docs > 0 else 0.0
        },
        "translation": {
            "source_lang": source_lang,
            "target_langs": target_langs,
            "coverage": translation_coverage
        },
        "knowledge_graph": {
            "total_nodes": total_nodes,
            "total_links": total_links,
            "isolated_count": isolated_nodes,
            "broken_link_count": broken_links,
            "health_score": health_score
        },
        "usage": {
            "session_cost": sync_data.get("usage", {}).get("session_cost", 0.0),
            "total_historical_cost": sync_data.get("usage", {}).get("total_historical_cost", 0.0),
            "recent_ledger": recent_usage
        }
    }
    return enriched_stats

def get_health_report_impl():
    """
    承载系统健康自愈与异常诊断报告的原子逻辑实现。
    """
    engine = get_global_engine()
    if not engine: return {}
    path = engine._resolve_path(engine.config.get_health_report_path())
    if os.path.exists(path):
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {}

def get_pulse_impl():
    """
    承载系统实时脉搏与调度指标加载的原子逻辑实现。
    """
    engine = get_global_engine()
    if not engine: return {}
    path = engine._resolve_path(engine.config.get_pulse_path())
    if os.path.exists(path):
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {}
