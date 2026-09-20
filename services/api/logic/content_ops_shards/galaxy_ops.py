# -*- coding: utf-8 -*-
"""
🧠 Illacme Plenipes Content Operations Shard - galaxy_ops
职责：承载 3D 拓扑星系神经图谱的节点/连线混合渐进式计算算法。
符合 SOP-02 模块拆分协议与 300 行核心复杂度红线。
"""

import os
from services.api.logic.content_ops_shards.galaxy_title_ops import resolve_node_true_title


def get_galaxy_graph_logic(engine, mode: str = "full"):
    """🪰 [混合渐进式] 物理优先与高维全量图模式的节点/连线融合算法"""
    if not engine:
        return {"nodes": [], "links": [], "_debug": "no_engine"}

    docs_snapshot = None
    if hasattr(engine, "meta") and hasattr(engine.meta, "get_documents_snapshot"):
        try:
            docs_snapshot = engine.meta.get_documents_snapshot()
        except Exception:
            pass

    # 🪰 [混合渐进式] 静态骨架模式
    if mode == "skeleton":
        nodes_list = []
        links_list = []
        seen_links = set()

        if not hasattr(engine, "link_graph") or not engine.link_graph:
            return {"nodes": [], "links": []}

        for rel_path, data in engine.link_graph.items():
            meta = data.get("metadata", {})
            true_title = resolve_node_true_title(rel_path, meta.get("title"), docs_snapshot, engine)
            nodes_list.append({
                "id": rel_path,
                "title": true_title,
                "val": 1.0,
                "group": "document",
                "is_skeleton": True
            })
            for target in data.get("links", []):
                resolved = engine.meta.resolve_link(target)
                target_key = resolved or target
                if not resolved and target not in engine.link_graph:
                    for k in engine.link_graph:
                        if os.path.basename(k) == target or os.path.splitext(os.path.basename(k))[0] == target:
                            target_key = k
                            break
                link_id = tuple(sorted([rel_path, target_key]))
                if link_id not in seen_links:
                    seen_links.add(link_id)
                    links_list.append({"source": rel_path, "target": target_key, "strength": 1.0, "type": "wikilink", "is_manual": False, "is_skeleton": True})
        # 🔗 创作者手动连线具备最高主权，骨架模式同步合并
        if hasattr(engine, "knowledge_graph") and hasattr(engine.knowledge_graph, "nodes"):
            for doc_id, data in engine.knowledge_graph.nodes.items():
                if not isinstance(data, dict): continue
                for tid in data.get("manual_connections", {}):
                    link_id = tuple(sorted([doc_id, tid]))
                    if link_id not in seen_links:
                        seen_links.add(link_id)
                        links_list.append({
                            "source": doc_id,
                            "target": tid,
                            "strength": 1.0,
                            "type": "semantic",
                            "is_manual": True,
                            "is_skeleton": True
                        })
        return {"nodes": nodes_list, "links": links_list}

    # 🪰 [混合渐进式] 全量高维图模式 (合并物理 WikiLinks 与 AI 语义/用户手动连线)
    else:
        if not hasattr(engine, "knowledge_graph"):
            return {"nodes": [], "links": []}

        kg_graph = engine.knowledge_graph.get_galaxy_graph()
        nodes_map = {n["id"]: n for n in kg_graph.get("nodes", [])}
        for n in nodes_map.values():
            n["is_skeleton"] = False
            n["group"] = "document"

        # 合并物理节点
        if hasattr(engine, "link_graph") and engine.link_graph:
            for rel_path, data in engine.link_graph.items():
                meta = data.get("metadata", {})
                title = resolve_node_true_title(rel_path, meta.get("title"), docs_snapshot, engine)
                if rel_path not in nodes_map:
                    nodes_map[rel_path] = {
                        "id": rel_path,
                        "title": title,
                        "gist": meta.get("gist", ""),
                        "entities": meta.get("entities", {}),
                        "val": 1.0,
                        "group": "document",
                        "is_skeleton": True
                    }
                else:
                    nodes_map[rel_path]["is_skeleton"] = True
                    nodes_map[rel_path]["title"] = title
                    if not nodes_map[rel_path].get("gist") and meta.get("gist"):
                        nodes_map[rel_path]["gist"] = meta["gist"]
                    if not nodes_map[rel_path].get("entities") and meta.get("entities"):
                        nodes_map[rel_path]["entities"] = meta["entities"]

        # 🚀 [V106.2 标题真理智能对齐] 全量对齐真理标题，防止未命中 link_graph 的节点残留纯文件名
        for nid, n in nodes_map.items():
            n["title"] = resolve_node_true_title(nid, n.get("title"), docs_snapshot, engine)

        # 🛡️ 物理真理对准 (Physical Truth Alignment)：剔除物理文库中已不存在的历史幽灵孤儿节点
        vault_root_abs = os.path.abspath(engine.vault_root) if getattr(engine, "vault_root", None) else ""
        valid_physical_ids = set(engine.link_graph.keys()) if hasattr(engine, "link_graph") and engine.link_graph else set()
        if valid_physical_ids or vault_root_abs:
            ghost_ids = [
                nid for nid in list(nodes_map.keys())
                if nid not in valid_physical_ids and (not vault_root_abs or not os.path.exists(os.path.join(vault_root_abs, nid)))
            ]
            for gid in ghost_ids:
                nodes_map.pop(gid, None)

            # 🧹 数据库自愈闭环：若图谱内存对象中仍残存幽灵节点，同步剔除并刷盘
            if ghost_ids and hasattr(engine, "knowledge_graph") and hasattr(engine.knowledge_graph, "nodes"):
                try:
                    with engine.knowledge_graph._lock:
                        for gid in ghost_ids:
                            engine.knowledge_graph.nodes.pop(gid, None)
                            for ndata in engine.knowledge_graph.nodes.values():
                                if isinstance(ndata, dict):
                                    if "connections" in ndata and isinstance(ndata["connections"], dict):
                                        ndata["connections"].pop(gid, None)
                                    if "manual_connections" in ndata and isinstance(ndata["manual_connections"], dict):
                                        ndata["manual_connections"].pop(gid, None)
                    engine.knowledge_graph.save()
                except Exception:
                    pass

        # 合并连线：物理优先 (wikilink 青色优先，避免被 weak semantic 紫色连线遮蔽)
        links_list = []
        seen_links = set()

        # 1. 先合并物理 Wikilink 连线
        if hasattr(engine, "link_graph") and engine.link_graph:
                for target in data.get("links", []):
                    resolved = engine.meta.resolve_link(target)
                    target_key = resolved or target
                    if not resolved and target not in engine.link_graph:
                        for k in engine.link_graph:
                            if os.path.basename(k) == target or os.path.splitext(os.path.basename(k))[0] == target:
                                target_key = k
                                break
                    if rel_path in nodes_map and target_key in nodes_map:
                        link_id = tuple(sorted([rel_path, target_key]))
                        if link_id not in seen_links:
                            seen_links.add(link_id)
                            links_list.append({"source": rel_path, "target": target_key, "strength": 1.0, "type": "wikilink", "is_manual": False, "is_skeleton": True})

        # 2. 再合并语义与用户手动连线 (如果尚未存在物理连线的话)
        for l in kg_graph.get("links", []):
            src = l["source"]
            tgt = l["target"]
            # 🛡️ 严格确保连线两端的节点均在有效物理节点集合 nodes_map 中
            if src not in nodes_map or tgt not in nodes_map:
                continue
            link_id = tuple(sorted([src, tgt]))
            if link_id not in seen_links:
                seen_links.add(link_id)
                links_list.append({
                    "source": src,
                    "target": tgt,
                    "strength": l.get("strength", 0.5),
                    "type": l.get("type", "semantic"),
                    "is_manual": l.get("is_manual", False),
                    "is_skeleton": False
                })
        return {"nodes": list(nodes_map.values()), "links": links_list}


def rebuild_node_semantics_logic(engine, doc_id: str):
    """
    针对单篇文档执行增量重构与语义链接分析。
    """
    if not engine:
        return {"error": "Engine not initialized"}

    from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path
    abs_path = resolve_safe_path(engine, doc_id)
    from core.utils.tracing import tlog
    tlog.info(f"🔎 [rebuild_node] target abs_path is: {abs_path}")
    if not abs_path or not os.path.exists(abs_path):
        return {"error": f"Document path invalid or not found: {doc_id}"}

    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}

    from core.utils.text import parse_frontmatter
    metadata, pure_content, _ = parse_frontmatter(content)
    title = metadata.get("title") or os.path.splitext(os.path.basename(doc_id))[0]

    if not hasattr(engine, "nlp_adapter"):
        from core.adapters.ai.nlp import NLPAdapter
        engine.nlp_adapter = NLPAdapter(engine)

    # 1. 提取实体与摘要
    try:
        entities = engine.nlp_adapter.extract_entities(pure_content)
        gist = engine.nlp_adapter.generate_gist(pure_content)
    except Exception as e:
        return {"error": f"NLP processing failed: {e}"}

    # 2. 物理原稿真理源同步回写与内存元数据对齐 (Single Source of Truth)
    try:
        from core.utils.text import inject_frontmatter
        from core.utils.io import atomic_write
        if gist:
            metadata["gist"] = gist
        if entities:
            metadata["entities"] = entities
        updated_content = inject_frontmatter(pure_content, metadata)
        atomic_write(abs_path, updated_content)
        if hasattr(engine, "link_graph") and doc_id in engine.link_graph:
            engine.link_graph[doc_id].setdefault("metadata", {})
            engine.link_graph[doc_id]["metadata"]["title"] = title
            if gist:
                engine.link_graph[doc_id]["metadata"]["gist"] = gist
            if entities:
                engine.link_graph[doc_id]["metadata"]["entities"] = entities
    except Exception as e:
        from core.utils.tracing import tlog
        tlog.error(f"🚨 [rebuild_node] Frontmatter sync failed for {abs_path}: {e}", exc_info=True)

    # 3. 更新图谱节点
    engine.knowledge_graph.upsert_node(doc_id, title, entities=entities, gist=gist)

    # 3. 语义向量关联
    discovery_count = 0
    if engine.embedding_adapter and hasattr(engine, "vector_index"):
        try:
            embedding = engine.embedding_adapter.embed_text(pure_content)
            if embedding:
                hits = engine.vector_index.search(embedding, top_k=6)
                for target_id, score in hits:
                    if target_id != doc_id and score > 0.75:
                        engine.knowledge_graph.link(doc_id, target_id, strength=score, rel_type="SEMANTIC_SIMILARITY")
                        discovery_count += 1
        except Exception as e:
            print(f"[rebuild_node] Embedding similarity mapping ignored: {e}")

    # 4. 基于共享实体关联
    if isinstance(entities, dict):
        all_entities = set()
        for cat_list in entities.values():
            if isinstance(cat_list, list):
                all_entities.update(cat_list)

        if all_entities:
            STOP_ENTITIES = {
                "Illacme Plenipes", "Illacme", "Plenipes",
                "主权数字出版底座", "主权出版系统", "系统",
                "好未来：数字教育未来趋势白皮书", "数字教育未来趋势白皮书",
                "好未来", "数字教育", "未来趋势", "白皮书", "welcome-to-illacme"
            }
            filtered_all = {e for e in all_entities if e not in STOP_ENTITIES and len(e) > 1}

            for other_id, other_node in engine.knowledge_graph.nodes.items():
                if other_id == doc_id or not isinstance(other_node, dict):
                    continue
                other_entities = set()
                o_ent_data = other_node.get("entities", {})
                if isinstance(o_ent_data, dict):
                    for cat_list in o_ent_data.values():
                        if isinstance(cat_list, list):
                            other_entities.update(cat_list)
                filtered_other = {e for e in other_entities if e not in STOP_ENTITIES and len(e) > 1}
                common = filtered_all.intersection(filtered_other)
                if len(common) >= 2:
                    strength = min(0.5 + (len(common) * 0.1), 0.95)
                    engine.knowledge_graph.link(doc_id, other_id, strength=strength, rel_type="SHARED_ENTITY")
                    discovery_count += 1

    engine.knowledge_graph.save(debounce=False)
    msg = f"已完成摘要与实体提炼，并编织了 {discovery_count} 条跨篇概念连线！" if discovery_count > 0 else "已完成摘要与实体提炼（暂未发现达到引力阈值的跨篇概念关联）。"
    return {"success": True, "message": msg, "entities": entities, "gist": gist}

