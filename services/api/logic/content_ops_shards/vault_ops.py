# -*- coding: utf-8 -*-
"""
📂 Illacme Plenipes Content Operations Shard - vault_ops
职责：承载物理稿件检索、详情获取、元数据更新与存盘安全核心逻辑，并聚合文件/目录操作子分片。
符合 SOP-02 模块拆分协议与 300 行核心复杂度红线。
"""

import os
import json
from core.utils.text import parse_frontmatter, inject_frontmatter, calculate_universal_word_count
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path
from services.api.logic.content_ops_shards.vault_file_ops import (
    create_document_logic,
    create_directory_logic,
    delete_directory_logic,
    move_document_logic,
    upload_asset_logic,
    generate_slug_logic,
    fallback_slugify,
)

# 保持对外统一导出
__all__ = [
    "search_vault_logic",
    "get_document_detail_logic",
    "update_document_metadata_logic",
    "save_document_logic",
    "create_document_logic",
    "create_directory_logic",
    "delete_directory_logic",
    "move_document_logic",
    "upload_asset_logic",
    "generate_slug_logic",
    "fallback_slugify",
]


def search_vault_logic(engine, q: str = "", page: int = 1, limit: int = 50, folder: str = ""):
    """🚀 [V55.0] 联邦检索入口：服务于 Dashboard Vault 视图"""
    if not engine:
        return {"error": "Engine not initialized"}
    total = engine.meta.sqlite.get_documents_count_filtered(query=q, folder=folder)

    # 🛡️ 物理真理对正：若账本为空但文库物理存在，执行自愈全量索引重构
    if total == 0 and getattr(engine, "vault_root", None) and os.path.exists(engine.vault_root):
        try:
            from core.editorial.vault_indexer import VaultIndexer
            if hasattr(engine, 'manuscript_source') and engine.manuscript_source:
                VaultIndexer.build_indexes(engine.manuscript_source, config=engine.config, ledger=engine.meta)
                total = engine.meta.sqlite.get_documents_count_filtered(query=q, folder=folder)
        except Exception:
            pass

    docs = engine.meta.sqlite.list_documents_paginated(page, limit, query=q, folder=folder)
    # 🚀 [V106.1 标题真理智能回填] 优先使用真实中文标题，防止纯文件名覆盖
    for d in docs:
        base_name = os.path.splitext(os.path.basename(d.get("rel_path", "")))[0]
        curr_title = d.get("title", "")
        seo_title = (d.get("seo_data") or {}).get("title")
        if (not curr_title or curr_title == base_name) and seo_title and seo_title != base_name:
            d["title"] = seo_title
    return {"items": docs, "total": total}


def get_document_detail_logic(engine, doc_id: str):
    """获取文档详情：查询 SQLite 元数据 + 物理文件读取 + frontmatter 解析"""
    if not engine:
        return {"error": "Engine not initialized"}
    doc = engine.meta.sqlite.get_document(doc_id)
    if not doc:
        return {"error": "Document not found"}

    abs_path = resolve_safe_path(engine, doc_id)
    content = ""
    if abs_path and os.path.exists(abs_path):
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            pass

    metadata, pure_content, has_fm = parse_frontmatter(content)
    doc["content"] = pure_content
    doc["frontmatter"] = metadata
    doc["has_frontmatter"] = has_fm

    # 🚀 [V106.1 标题真理智能纠偏] 优先原稿显式标题，防止打开编辑器时英文文件名回填
    base_name = os.path.splitext(os.path.basename(doc_id))[0]
    fm_title = metadata.get("title")
    h1_title = ""
    if pure_content:
        for line in pure_content.splitlines():
            line_s = line.strip()
            if line_s.startswith("# "):
                h1_title = line_s[2:].strip()
                break

    seo_title = (doc.get("seo_data") or {}).get("title")
    if fm_title and fm_title != base_name:
        doc["title"] = fm_title
    elif h1_title and h1_title != base_name:
        doc["title"] = h1_title
    elif seo_title and seo_title != base_name:
        doc["title"] = seo_title

    # 🧠 [深度语义聚合] 优先使用原稿 frontmatter，若原稿中无则无损回填知识图谱中的 AI 派生语义
    kg_gist = ""
    kg_entities = {}
    if hasattr(engine, "knowledge_graph") and hasattr(engine.knowledge_graph, "nodes"):
        node_data = engine.knowledge_graph.nodes.get(doc_id)
        if isinstance(node_data, dict):
            kg_gist = node_data.get("gist", "")
            kg_entities = node_data.get("entities", {})

    final_gist = metadata.get("gist") or kg_gist or ""
    final_entities = metadata.get("entities") or kg_entities or {}
    doc["gist"] = final_gist
    doc["entities"] = final_entities
    if not metadata.get("gist") and final_gist:
        metadata["gist"] = final_gist
    if not metadata.get("entities") and final_entities:
        metadata["entities"] = final_entities

    # 📚 [V105.0] 标准化字数透传：全球全语种通用度量 (Universal Multilingual Word Count)
    seo_data = doc.get("seo_data")
    if isinstance(seo_data, str):
        try:
            seo_data = json.loads(seo_data)
        except Exception:
            seo_data = {}

    wc = seo_data.get("word_count") if isinstance(seo_data, dict) else 0
    if not wc and pure_content:
        wc = calculate_universal_word_count(pure_content)
    doc["word_count"] = int(wc or 0)

    return doc


def update_document_metadata_logic(engine, doc_id: str, req: dict):
    """SQLite 核心元数据更新接口"""
    if not engine:
        return {"error": "Engine not initialized"}
    dir_mode = getattr(getattr(engine, 'config', None), 'translation', None)
    dir_mode_val = getattr(dir_mode, 'slug_dir_mode', 'nested') if dir_mode else 'nested'
    result = engine.meta.sqlite.update_document_metadata(doc_id, req, dir_mode=dir_mode_val)

    # 🛡️ [Slug 冲突透传] 底层检测到 slug 被其他文档占用时，返回冲突 dict 而非 bool
    if isinstance(result, dict) and result.get("conflict"):
        occupied_by = result.get("occupied_by", "?")
        slug = result.get("slug", "?")
        error_hint = "（当前网址形态为【极简根目录】，需保持 Slug 全域唯一）" if dir_mode_val == "flat" else ""
        return {
            "success": False,
            "error": f"Slug 冲突：「{slug}」已被文档 '{occupied_by}' 占用，请更换其他 Slug。{error_hint}",
            "error_code": "SLUG_CONFLICT",
            "occupied_by": occupied_by
        }
    return {"success": bool(result)}


def save_document_logic(engine, doc_id: str, req: dict):
    """原稿保存：frontmatter 注入与物理磁盘写入"""
    if not engine:
        return {"error": "Engine not initialized"}

    # 🛡️ [安全防线] 拦截非法 doc_id，防止产生物理 'null'/'undefined' 脏资产文件
    if not doc_id or doc_id.strip() in ("", "null", "undefined", "None"):
        return {"success": False, "error": "非法的原稿文件路径名称"}

    content = req.get("content", "")
    metadata = req.get("frontmatter", {}) or {}
    title, slug = req.get("title"), req.get("slug")

    from core.logic.ai.ai_logic_hub import AILogicHub
    if slug:
        slug = AILogicHub.clean_slug(slug)

    # 🛡️ [双层物理一致性自愈] 剥离可能包含的旧 YAML 头，防叠头部，防特殊字符漏网
    old_meta, pure_content, has_head = parse_frontmatter(content)

    merged_meta = {**old_meta, **metadata}
    if title:
        merged_meta["title"] = title
    if slug:
        merged_meta["slug"] = slug
    elif "slug" in merged_meta:
        merged_meta["slug"] = AILogicHub.clean_slug(merged_meta["slug"])

    # 🛡️ [Slug 唯一性守卫] 结合治理中心网址路径组织形态 (slug_dir_mode) 进行冲突校验
    final_slug = merged_meta.get("slug")
    if final_slug:
        conn = engine.meta.sqlite._get_conn()
        conflict_rows = conn.execute(
            "SELECT rel_path FROM documents WHERE slug = ? AND rel_path != ?",
            (final_slug, doc_id)
        ).fetchall()
        dir_mode = getattr(getattr(engine, 'config', None), 'translation', None)
        dir_mode_val = getattr(dir_mode, 'slug_dir_mode', 'nested') if dir_mode else 'nested'
        for c_row in conflict_rows:
            conflict_path = dict(c_row).get("rel_path", "?")
            is_conflict = getattr(engine.meta.sqlite, 'is_slug_conflict', None)
            if is_conflict and not is_conflict(final_slug, doc_id, conflict_path, dir_mode=dir_mode_val):
                continue
            error_hint = "（当前网址形态为【极简根目录】，全站普通稿件均平铺于根目录，需保持 Slug 全域唯一）" if dir_mode_val == "flat" else ""
            return {
                "success": False,
                "error": f"Slug 冲突：「{final_slug}」已被文档 '{conflict_path}' 占用，请更换其他 Slug。{error_hint}",
                "error_code": "SLUG_CONFLICT",
                "occupied_by": conflict_path
            }

    full_content = inject_frontmatter(pure_content, merged_meta)

    abs_path = resolve_safe_path(engine, doc_id)
    if not abs_path:
        return {"error": "权限拒绝：检测到非法的物理路径穿越指令"}

    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
    except Exception as e:
        return {"error": f"Failed to write physical file: {e}"}

    # 物理计算字数与自愈元数据更新
    try:
        word_count = calculate_universal_word_count(full_content)
    except Exception:
        word_count = 0

    doc_info = engine.meta.get_doc_info(doc_id) or {}
    seo_data = doc_info.get("seo_data") or {}
    seo_data["word_count"] = word_count

    engine.meta.register_document(
        doc_id,
        title or doc_info.get("title") or os.path.splitext(os.path.basename(doc_id))[0],
        slug=slug,
        seo_data=seo_data
    )

    # 🚀 [V100.0] 双层物理一致性自愈：即时重塑物理索引与语义知识图谱节点
    _sync_indexer_and_knowledge_graph(engine, doc_id, abs_path, full_content, title)

    return {"success": True}


def _sync_indexer_and_knowledge_graph(engine, doc_id: str, abs_path: str, full_content: str, title: str):
    """即时重塑物理索引与语义知识图谱节点，确保 3D 图谱完美同步刷新。"""
    try:
        from core.editorial.vault_indexer import VaultIndexer
        from core.ingress.language_sentinel import LanguageSentinel

        mtime = os.path.getmtime(abs_path)
        detected_lang = LanguageSentinel.detect_language(full_content, os.path.basename(doc_id))
        links = VaultIndexer.extract_links(full_content)
        meta = VaultIndexer._quick_parse_meta(full_content)
        meta["size"] = len(full_content)
        meta["mtime"] = mtime
        meta["lang"] = detected_lang

        if hasattr(engine, "link_graph"):
            engine.link_graph[doc_id] = {"links": links, "metadata": meta}

        if hasattr(engine, "knowledge_graph"):
            actual_title = title or meta.get("title") or os.path.splitext(os.path.basename(doc_id))[0]
            engine.knowledge_graph.upsert_node(doc_id, actual_title)
            engine.knowledge_graph.save(debounce=False)
    except Exception:
        pass
