#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - Health Registry
模块职责：算力节点全时健康度监测。实时记录每个 AI 节点的响应速度、成功率与负载状态。
🛡️ [AEL-Iter-v1.0]：基于指数移动平均 (EMA) 的动态评分系统。
"""

import time
import threading
from typing import Dict, Any, List
from core.utils.tracing import tlog

class NodeMetrics:
    """单个算力节点的健康指标"""
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.success_count = 0
        self.failure_count = 0
        self.total_latency = 0.0
        self.avg_latency = 0.0
        self.last_used = 0.0
        self.health_score = 100.0 # 初始分满分
        self._lock = threading.Lock()

    def record_success(self, latency: float):
        with self._lock:
            self.success_count += 1
            self.total_latency += latency
            self.last_used = time.time()
            # 采用 EMA 算法更新平均延迟 (Alpha=0.2)
            if self.avg_latency == 0: self.avg_latency = latency
            else: self.avg_latency = (self.avg_latency * 0.8) + (latency * 0.2)
            
            # 缓慢恢复健康分
            self.health_score = min(100.0, self.health_score + 1.0)

    def record_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_used = time.time()
            # 惩罚健康分
            self.health_score = max(0.0, self.health_score - 20.0)

    def get_score(self) -> float:
        """综合评分：健康分 * (1 / 平均延迟影响因子)"""
        if self.avg_latency > 0:
            # 延迟惩罚因子：延迟每增加 1s，分数衰减
            latency_factor = 1.0 / (1.0 + self.avg_latency / 5.0)
            return self.health_score * latency_factor
        return self.health_score

class HealthRegistry:
    """🚀 [V1.0] 全局算力健康中枢 (Singleton)"""
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(HealthRegistry, cls).__new__(cls)
                cls._instance.nodes: Dict[str, NodeMetrics] = {}
        return cls._instance

    def get_node(self, node_name: str) -> NodeMetrics:
        if node_name not in self.nodes:
            self.nodes[node_name] = NodeMetrics(node_name)
        return self.nodes[node_name]

    def report_success(self, node_name: str, latency: float):
        self.get_node(node_name).record_success(latency)

    def report_failure(self, node_name: str):
        self.get_node(node_name).record_failure()

    def get_rankings(self) -> List[Dict[str, Any]]:
        """获取算力节点排行榜"""
        ranking = []
        for name, metrics in self.nodes.items():
            ranking.append({
                "node": name,
                "score": metrics.get_score(),
                "health": metrics.health_score,
                "latency": round(metrics.avg_latency, 2),
                "success_rate": round(metrics.success_count / (metrics.success_count + metrics.failure_count + 1e-6) * 100, 1)
            })
        return sorted(ranking, key=lambda x: x["score"], reverse=True)

# 全局单例
health_registry = HealthRegistry()
