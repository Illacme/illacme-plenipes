#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ [V48.4] Illacme Plenipes Knowledge Graph Offline Remodeler
职责：根据最新的高精度 SHARED_ENTITY 关系逻辑，离线洗涤并重新织网已有的高维语义图谱。
"""

import os
import json
import shutil

# 定义停用实体
STOP_ENTITIES = {
    "Illacme Plenipes", "Illacme", "Plenipes",
    "主权数字出版底座", "主权出版系统", "系统",
    "好未来：数字教育未来趋势白皮书", "数字教育未来趋势白皮书",
    "好未来", "数字教育", "未来趋势", "白皮书", "welcome-to-illacme"
}

GRAPH_PATH = "/Volumes/Notebook/omni-hub/illacme-plenipes/imprints/testim/metadata/themes/starlight/knowledge_graph_starlight.json"

def main():
    if not os.path.exists(GRAPH_PATH):
        print(f"❌ 找不到图谱数据文件: {GRAPH_PATH}")
        return

    # 1. 备份数据
    bak_path = GRAPH_PATH + ".bak"
    shutil.copy2(GRAPH_PATH, bak_path)
    print(f"💾 备份已创建: {bak_path}")

    # 2. 读取图谱
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        graph = json.load(f)

    # 3. 提取所有节点的实体，并预先清除已有的 SHARED_ENTITY 连接
    node_entities = {}
    for node_id, data in graph.items():
        # 获取全部实体并展平
        all_ents = set()
        ents_dict = data.get("entities", {})
        if isinstance(ents_dict, dict):
            for cat_list in ents_dict.values():
                if isinstance(cat_list, list):
                    all_ents.update(cat_list)
        
        # 过滤停用词与短实体
        filtered = {e for e in all_ents if e not in STOP_ENTITIES and len(e) > 1}
        node_entities[node_id] = filtered

        # 清除已有的 SHARED_ENTITY 连线
        connections = data.get("connections", {})
        cleaned_connections = {}
        for target, conn_meta in connections.items():
            if conn_meta.get("type") != "SHARED_ENTITY":
                cleaned_connections[target] = conn_meta
        data["connections"] = cleaned_connections

    # 4. 两两比对节点，重新精准计算 SHARED_ENTITY 连接
    node_ids = list(graph.keys())
    new_links_count = 0
    for i in range(len(node_ids)):
        for j in range(i + 1, len(node_ids)):
            id_a = node_ids[i]
            id_b = node_ids[j]

            ents_a = node_entities[id_a]
            ents_b = node_entities[id_b]

            common = ents_a.intersection(ents_b)
            if len(common) >= 2:
                # 共享实体越多，强度越高
                strength = min(0.5 + (len(common) * 0.1), 0.95)
                # 为双方建立双向连接
                if "connections" not in graph[id_a]:
                    graph[id_a]["connections"] = {}
                if "connections" not in graph[id_b]:
                    graph[id_b]["connections"] = {}
                graph[id_a]["connections"][id_b] = {
                    "strength": round(strength, 2),
                    "type": "SHARED_ENTITY"
                }
                graph[id_b]["connections"][id_a] = {
                    "strength": round(strength, 2),
                    "type": "SHARED_ENTITY"
                }
                new_links_count += 1
                print(f"✨ 建立精准语义链路: {id_a} ⇄ {id_b} \n   ├── 共享实体: {list(common)}\n   └── 强度: {strength:.2f}")

    # 5. 写回数据
    with open(GRAPH_PATH, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 [SUCCESS] 离线重置与自愈清洗完成！共建立 {new_links_count} 条高精度双向语义关系链路，覆盖 {len(node_ids)} 个节点。")

if __name__ == "__main__":
    main()
