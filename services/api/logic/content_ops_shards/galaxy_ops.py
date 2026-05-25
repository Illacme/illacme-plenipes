# -*- coding: utf-8 -*-
"""
🧠 Illacme Plenipes Content Operations Shard - galaxy_ops
职责：承载 3D 拓扑星系神经图谱的节点/连线混合渐进式计算算法。
符合 SOP-02 模块拆分协议与 300 行核心复杂度红线。
"""

import os


def get_galaxy_graph_logic(engine, mode: str = "full"):
    """🪰 [混合渐进式] 物理优先与高维全量图模式的节点/连线融合算法"""
    if not engine:
        return {"nodes": [], "links": []}

    # 🪰 [混合渐进式] 静态骨架模式
    if mode == "skeleton":
        nodes_list = []
        links_list = []
        seen_links = set()

        if not hasattr(engine, "link_graph") or not engine.link_graph:
            return {"nodes": [], "links": []}

        for rel_path, data in engine.link_graph.items():
            meta = data.get("metadata", {})
            nodes_list.append({
                "id": rel_path,
                "title": meta.get("title") or os.path.splitext(os.path.basename(rel_path))[0],
                "val": 1.0,
                "group": "document",
                "is_skeleton": True
            })
            for target in data.get("links", []):
                resolved = engine.meta.resolve_link(target)
                if resolved:
                    target_key = resolved
                else:
                    target_key = target
                    if target not in engine.link_graph:
                        for k in engine.link_graph:
                            if os.path.basename(k) == target or os.path.splitext(os.path.basename(k))[0] == target:
                                target_key = k
                                break
                link_id = tuple(sorted([rel_path, target_key]))
                if link_id not in seen_links:
                    seen_links.add(link_id)
                    links_list.append({
                        "source": rel_path,
                        "target": target_key,
                        "strength": 1.0,
                        "type": "wikilink",
                        "is_manual": False,
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
                title = meta.get("title") or os.path.splitext(os.path.basename(rel_path))[0]
                if rel_path not in nodes_map:
                    nodes_map[rel_path] = {
                        "id": rel_path,
                        "title": title,
                        "val": 1.0,
                        "group": "document",
                        "is_skeleton": True
                    }
                else:
                    nodes_map[rel_path]["is_skeleton"] = True
                    # 🚀 [V100.0] 双重对齐保险：强制对齐最新物理 title 属性，打破缓存在 full 模式下的遮蔽缺陷
                    nodes_map[rel_path]["title"] = title

        # 合并连线：物理优先 (wikilink 青色优先，避免被 weak semantic 紫色连线遮蔽)
        links_list = []
        seen_links = set()

        # 1. 先合并物理 Wikilink 连线
        if hasattr(engine, "link_graph") and engine.link_graph:
            for rel_path, data in engine.link_graph.items():
                for target in data.get("links", []):
                    resolved = engine.meta.resolve_link(target)
                    if resolved:
                        target_key = resolved
                    else:
                        target_key = target
                        if target not in engine.link_graph:
                            for k in engine.link_graph:
                                if os.path.basename(k) == target or os.path.splitext(os.path.basename(k))[0] == target:
                                    target_key = k
                                    break
                    if rel_path in nodes_map and target_key in nodes_map:
                        link_id = tuple(sorted([rel_path, target_key]))
                        if link_id not in seen_links:
                            seen_links.add(link_id)
                            links_list.append({
                                "source": rel_path,
                                "target": target_key,
                                "strength": 1.0,
                                "type": "wikilink",
                                "is_manual": False,
                                "is_skeleton": True
                            })

        # 2. 再合并语义与用户手动连线 (如果尚未存在物理连线的话)
        for l in kg_graph.get("links", []):
            src = l["source"]
            tgt = l["target"]
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
