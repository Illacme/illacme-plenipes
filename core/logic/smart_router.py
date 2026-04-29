#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Logic - Smart Router
模块职责：智能算力路由。根据健康注册表的数据，动态决定每一个 AI 请求的最佳去向。
🛡️ [AEL-Iter-v1.0]：支持性能优先与高可用冗余调度。
"""

from typing import List, Optional
from core.governance.health_registry import health_registry
from core.utils.tracing import tlog

class SmartRouter:
    """🚀 [V1.0] 智能路由器：全自动算力 Failover"""
    
    def __init__(self, engine):
        self.engine = engine
        self.registry = health_registry

    def get_best_node(self, preferred_node: str = None) -> str:
        """
        🚀 动态获取当前最优健康节点
        :param preferred_node: 业务层建议的首选节点 (来自配置)
        :return: 最终路由到的节点 ID
        """
        # 1. 检查首选节点健康状况
        if preferred_node:
            node = self.registry.get_node(preferred_node)
            if node.health_score > 60: # 经验阈值：如果首选节点依然健康，则不轻易切流
                return preferred_node

        # 2. 如果首选节点已亚健康，寻找排行榜第一名
        rankings = self.registry.get_rankings()
        if rankings:
            best_node = rankings[0]["node"]
            if best_node != preferred_node:
                tlog.warning(f"🔀 [智能路由] 侦测到首选节点 {preferred_node} 指标下滑，正在自动 Failover 至最优节点: {best_node}")
            return best_node

        # 3. 兜底回退
        return preferred_node or "mock-node"

    def get_failover_node(self, failing_node: str) -> Optional[str]:
        """
        🚀 获取故障转移目标节点
        用于重试逻辑中，当一个节点物理失败后，立即换一个试试
        """
        rankings = self.registry.get_rankings()
        for r in rankings:
            if r["node"] != failing_node and r["health"] > 40:
                tlog.info(f"🩹 [故障转移] 节点 {failing_node} 异常，已动态切流至: {r['node']}")
                return r["node"]
        return None
