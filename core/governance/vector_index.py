#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - Vector Index
模块职责：轻量级本地向量数据库。负责管理文档的语义特征，并提供秒级的余弦相似度检索。
🛡️ [AEL-Iter-v1.0]：纯 Python 实现的轻量级 ANN。
"""

import os
import json
import math
from typing import Dict, List, Tuple, Any
from core.utils.tracing import tlog

class VectorIndex:
    """🚀 [V1.0] 轻量级向量索引：个人用户的语义搜索基石"""
    
    def __init__(self, index_path: str):
        self.index_path = index_path
        self.data: Dict[str, List[float]] = {} # rel_path -> vector
        self._load()

    def _load(self):
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                tlog.warning(f"⚠️ [向量索引加载失败]: {e}")

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        try:
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f)
        except Exception as e:
            tlog.error(f"🛑 [向量索引保存失败]: {e}")

    def update_document(self, rel_path: str, vector: List[float]):
        if vector:
            self.data[rel_path] = vector

    def remove_document(self, rel_path: str):
        if rel_path in self.data:
            del self.data[rel_path]

    def is_indexed(self, rel_path: str) -> bool:
        """🚀 [V22.2] 快速核验文档是否已向量化"""
        return rel_path in self.data

    @staticmethod
    def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2): return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0 or norm_b == 0: return 0.0
        return dot_product / (norm_a * norm_b)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        全量暴力检索 (针对个人用户几千个文档的规模，耗时极低)
        """
        if not query_vector: return []
        
        results = []
        for rel_path, doc_vector in self.data.items():
            score = self._cosine_similarity(query_vector, doc_vector)
            results.append((rel_path, score))
        
        # 按得分降序排列
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

# 🚀 [V14.0] 挂载逻辑由 Engine 启动时完成
