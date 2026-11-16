#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗑️ [V68.0] Illacme Plenipes - Pipeline Destroy Operations Shard
职责：物理销毁磁盘资产及其所有多语言出版产物，递归清理空文件夹并在账本中彻底注销。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
"""

import os

def destroy_artifact_logic(engine, doc_id: str) -> dict:
    """
    🗑️ 物理销毁逻辑：抹除磁盘资产及其所有出版产物，并在账本中彻底注销
    """
    deleted_paths = []
    
    try:
        # 1. 物理撤销 Vault 源文件
        source_path = os.path.abspath(os.path.join(engine.vault_root, doc_id))
        if os.path.exists(source_path):
            os.remove(source_path)
            deleted_paths.append(source_path)
            
            # 清理 Vault 中因删除产生的空父文件夹
            parent = os.path.dirname(source_path)
            vault_root_abs = os.path.abspath(engine.vault_root)
            while parent != vault_root_abs and parent.startswith(vault_root_abs):
                try:
                    if os.path.exists(parent) and not os.listdir(parent):
                        os.rmdir(parent)
                        parent = os.path.dirname(parent)
                    else:
                        break
                except Exception:
                    break

        # 2. 物理抹除 dist 目录中的多语言出版快照 (支持 nested / flat / prefix 与自定义 slug)
        config = engine.config
        imprint_id = getattr(config, "active_imprint", None) or getattr(engine, "imprint_id", "default") or "default"
        theme = getattr(config, "active_theme", "default") or "default"
        dist_root = os.path.abspath(os.path.join("imprints", imprint_id, "themes", theme, "dist"))
        doc_info = engine.meta.get_doc_info(doc_id) if hasattr(engine, "meta") else {}

        rel_path, _ = os.path.splitext(doc_id)
        rel_clean = rel_path.replace("\\", "/").strip("/")
        base_stem = os.path.basename(rel_clean)
        doc_slug = (doc_info.get("slug") if isinstance(doc_info, dict) else None) or base_stem
        r_prefix = ((doc_info.get("route_prefix") if isinstance(doc_info, dict) else None) or "").strip("/")
        sub_dir = os.path.dirname(rel_clean).strip("/")

        cand_html_rels = {
            f"{rel_clean}.html",
            f"{rel_clean.lower()}.html",
            f"{doc_slug}.html",
        }
        if sub_dir:
            cand_html_rels.add(f"{sub_dir}/{doc_slug}.html")
            cand_html_rels.add(f"{sub_dir.lower()}/{doc_slug}.html")
            cand_html_rels.add(f"{sub_dir.lower().replace('/', '-')}-{doc_slug}.html")
        if r_prefix:
            cand_html_rels.add(f"{r_prefix}/{doc_slug}.html")
            cand_html_rels.add(f"{r_prefix}-{doc_slug}.html")

        i18n = getattr(config, "i18n_settings", None)
        target_langs = [t.lang_code for t in (getattr(i18n, "targets", []) or []) if getattr(t, "lang_code", None)]
        lang_roots = [dist_root] + [os.path.join(dist_root, lc) for lc in target_langs]

        for l_root in lang_roots:
            for h_rel in cand_html_rels:
                h_abs = os.path.join(l_root, h_rel)
                if os.path.isfile(h_abs):
                    os.remove(h_abs)
                    deleted_paths.append(h_abs)
                    h_dir = os.path.dirname(h_abs)
                    while h_dir != l_root and h_dir.startswith(l_root):
                        try:
                            if os.path.exists(h_dir) and not os.listdir(h_dir):
                                os.rmdir(h_dir)
                                h_dir = os.path.dirname(h_dir)
                            else:
                                break
                        except Exception:
                            break

        # 3. 清理关联的播客音频与章节缓存 (兼容路径前缀与单层 slug)
        base_cache = getattr(engine, "cache_dir", None) or os.path.join(os.getcwd(), ".plenipes", "cache")
        podcast_dir = os.path.join(base_cache, "podcasts", imprint_id)
        if os.path.isdir(podcast_dir):
            path_slug = rel_clean.lower().replace("/", "__")
            prefixes = {f"{path_slug}_"}
            if not sub_dir:
                prefixes.add(f"{base_stem}_")
                prefixes.add(f"{doc_slug}_")
            for pf in os.listdir(podcast_dir):
                if any(pf.startswith(px) for px in prefixes) and (pf.endswith(".mp3") or pf.endswith(".chapters.json")):
                    try:
                        p_abs = os.path.join(podcast_dir, pf)
                        os.remove(p_abs)
                        deleted_paths.append(p_abs)
                    except Exception:
                        pass

        # 4. 从 SQLite 主权账本、双链索引与 3D 知识星谱中彻底注销元数据
        if hasattr(engine, "meta"):
            engine.meta.remove_document(doc_id)
        if hasattr(engine, "link_graph") and isinstance(engine.link_graph, dict):
            engine.link_graph.pop(doc_id, None)
        if hasattr(engine, "knowledge_graph") and hasattr(engine.knowledge_graph, "nodes"):
            with engine.knowledge_graph._lock:
                if isinstance(engine.knowledge_graph.nodes, dict):
                    engine.knowledge_graph.nodes.pop(doc_id, None)
                    engine.knowledge_graph.save(debounce=False)

        return {
            "success": True,
            "message": f"资产 {doc_id} 及其所有多语言出版产物已在全网物理销毁。",
            "deleted_items_count": len(deleted_paths)
        }
    except Exception as e:
        return {"success": False, "message": f"物理销毁失败: {str(e)}"}
