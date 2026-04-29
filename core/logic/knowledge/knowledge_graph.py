#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes V18 - Knowledge Graph Hub
职责：管理知识节点间的拓扑关系，支持语义链接的持久化与检索。
"""

import os
import json
import threading
from typing import Dict, List, Any
from core.utils.tracing import tlog

class KnowledgeGraph:
    """🚀 [V18.0] 知识图谱中枢：定义知识的引力场"""
    
    def __init__(self, graph_path: str):
        self.graph_path = graph_path
        self._lock = threading.RLock()
        self.nodes: Dict[str, Dict[str, Any]] = {}  # doc_id -> {title, connections: {target_id: strength}}
        self._load()

    def _load(self):
        """物理加载图谱数据"""
        if os.path.exists(self.graph_path):
            try:
                with open(self.graph_path, 'r', encoding='utf-8') as f:
                    self.nodes = json.load(f)
            except Exception as e:
                tlog.error(f"❌ [KnowledgeGraph] 加载失败: {e}")
                self.nodes = {}

    def save(self):
        """原子化持久化图谱"""
        with self._lock:
            try:
                # 确保父目录存在
                os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
                temp_path = self.graph_path + ".tmp"
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(self.nodes, f, ensure_ascii=False, indent=2)
                os.replace(temp_path, self.graph_path)
            except Exception as e:
                tlog.error(f"❌ [KnowledgeGraph] 持久化失败: {e}")

    def upsert_node(self, doc_id: str, title: str, entities: Dict[str, List[str]] = None, gist: str = None):
        """🚀 [V24.5] 增强型节点更新：支持实体与语义指纹"""
        with self._lock:
            if doc_id not in self.nodes:
                self.nodes[doc_id] = {
                    "title": title,
                    "connections": {},
                    "manual_connections": {}, # 🚀 [V20.0] 用户主权链路
                    "entities": entities or {},
                    "gist": gist or ""
                }
            else:
                self.nodes[doc_id]["title"] = title
                if isinstance(entities, dict):
                    # 🚀 [V24.6] 强类型合并：确保实体类目与项的结构完整性
                    current_entities = self.nodes[doc_id].get("entities", {})
                    if not isinstance(current_entities, dict): current_entities = {}
                    
                    for cat, items in entities.items():
                        if isinstance(items, list):
                            # 执行去重合并
                            existing_items = current_entities.get(cat, [])
                            if not isinstance(existing_items, list): existing_items = []
                            current_entities[cat] = list(set(existing_items + items))
                    
                    self.nodes[doc_id]["entities"] = current_entities
                if gist:
                    self.nodes[doc_id]["gist"] = gist
                
                if "manual_connections" not in self.nodes[doc_id]:
                    self.nodes[doc_id]["manual_connections"] = {}

    def link(self, src_id: str, target_id: str, strength: float = 1.0, is_manual: bool = False, rel_type: str = "RELATED"):
        """建立语义链接 (双向引力)"""
        if src_id == target_id: return
        
        with self._lock:
            if src_id in self.nodes and target_id in self.nodes:
                # 选择连接池
                pool_key = "manual_connections" if is_manual else "connections"
                
                # 更新 A -> B
                existing = self.nodes[src_id][pool_key].get(target_id, {})
                if isinstance(existing, (float, int)): existing = {"strength": existing, "type": "RELATED"}
                
                new_strength = max(existing.get("strength", 0), strength)
                self.nodes[src_id][pool_key][target_id] = {
                    "strength": new_strength,
                    "type": rel_type if strength >= existing.get("strength", 0) else existing.get("type", "RELATED")
                }

                # 更新 B -> A (对等关联)
                self.nodes[target_id][pool_key][src_id] = {
                    "strength": new_strength,
                    "type": rel_type if strength >= existing.get("strength", 0) else existing.get("type", "RELATED")
                }
                
                prefix = "🛡️ [用户定义]" if is_manual else "🌌 [AI 发现]"
                tlog.debug(f"{prefix} 链路建立: {src_id} <-> {target_id} ({rel_type})")

    @staticmethod
    def _normalize_link_data(v):
        """🚀 [V24.5] 兼容性归一化：支持旧版浮点权重与新版字典格式"""
        if isinstance(v, dict): return v
        return {"strength": v, "type": "RELATED"}

    def get_related(self, doc_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """🚀 [V24.5] 增强型关联查询：返回包含实体与摘要的富元数据"""
        node = self.nodes.get(doc_id)
        if not node: return []
        
        # 整合 AI 发现与手动建立的链路
        all_conns = {**node.get("connections", {}), **node.get("manual_connections", {})}
        
        # 按强度排序
        conns = sorted(all_conns.items(), key=lambda x: self._normalize_link_data(x[1])["strength"], reverse=True)
        results = []
        for tid, val in conns[:limit]:
            if tid in self.nodes:
                target_node = self.nodes[tid]
                meta = self._normalize_link_data(val)
                results.append({
                    "id": tid,
                    "title": target_node.get("title", tid),
                    "strength": meta["strength"],
                    "type": meta["type"],
                    "entities": target_node.get("entities", {}),
                    "gist": target_node.get("gist", "")
                })
        return results
    def add_manual_link(self, src_id: str, target_id: str):
        """🚀 [V20.1] 手动建立主权链路：用户定义的关联具有最高优先级"""
        with self._lock:
            # 确保节点存在 (即便没有标题也建立占位符)
            if src_id not in self.nodes: self.upsert_node(src_id, src_id)
            if target_id not in self.nodes: self.upsert_node(target_id, target_id)
            
            self.link(src_id, target_id, strength=1.0, is_manual=True)
            self.save()
            tlog.info(f"🔗 [KnowledgeGraph] 手动链路已固化: {src_id} <-> {target_id}")

    def get_galaxy_graph(self) -> Dict[str, Any]:
        """🚀 [V20.2] 导出 3D 银河标准格式数据"""
        with self._lock:
            nodes_list = []
            links_list = []
            
            for doc_id, data in self.nodes.items():
                if not isinstance(data, dict): continue
                
                nodes_list.append({
                    "id": doc_id,
                    "title": data.get("title", doc_id),
                    "val": 1  # 初始权重
                })
                
                # 导出所有链路 (去重)
                all_conns = {**data.get("connections", {}), **data.get("manual_connections", {})}
                for tid, val in all_conns.items():
                    if doc_id < tid: # 仅导出一次
                        meta = self._normalize_link_data(val)
                        links_list.append({
                            "source": doc_id,
                            "target": tid,
                            "strength": meta["strength"],
                            "type": meta["type"],
                            "is_manual": tid in data.get("manual_connections", {})
                        })
            
            return {"nodes": nodes_list, "links": links_list}
