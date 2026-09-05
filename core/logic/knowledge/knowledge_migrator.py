#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Knowledge Graph Legacy Migrator
职责：物理扫描旧版主题知识图谱并无损合并至版图全局单例中。
"""

import os
import json
from typing import Dict, Any
from core.utils.tracing import tlog

class KnowledgeGraphMigrator:
    """🚀 [V105.0] 知识图谱自愈迁移器：负责历史主题图谱无损聚合"""

    @staticmethod
    def migrate_legacy_theme_graphs(graph_path: str, current_nodes: Dict[str, Any]) -> int:
        """扫描同版图 metadata/themes/*/knowledge_graph_*.json 并无损合并至全局单例"""
        try:
            meta_dir = os.path.dirname(os.path.dirname(graph_path))
            themes_dir = os.path.join(meta_dir, "themes")
            if not os.path.isdir(themes_dir):
                return 0
            merged_count = 0
            for t_name in os.listdir(themes_dir):
                t_graph = os.path.join(themes_dir, t_name, f"knowledge_graph_{t_name}.json")
                if os.path.exists(t_graph):
                    try:
                        with open(t_graph, 'r', encoding='utf-8') as f:
                            t_nodes = json.load(f)
                        if isinstance(t_nodes, dict):
                            for nid, ndata in t_nodes.items():
                                if nid not in current_nodes and isinstance(ndata, dict):
                                    current_nodes[nid] = ndata
                                    merged_count += 1
                    except Exception:
                        pass
            if merged_count > 0:
                tlog.info(f"🌌 [KnowledgeGraph] 成功从历史主题图谱自愈迁移 {merged_count} 个节点至版图全局单例！")
            return merged_count
        except Exception as e:
            tlog.warning(f"⚠️ [KnowledgeGraph] 历史主题图谱合并探测忽略: {e}")
            return 0
