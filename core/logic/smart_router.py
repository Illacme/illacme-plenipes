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

    def _is_node_allowed(self, node_name: str) -> bool:
        """检查节点是否未被熔断"""
        if not node_name:
            return False
        if self.engine and hasattr(self.engine, 'circuit_breakers'):
            breaker = self.engine.circuit_breakers.get("ai")
            if breaker and hasattr(breaker, 'allow_request'):
                return breaker.allow_request(node_name)
        return True

    def get_best_node(self, preferred_node: str = None) -> str:
        """
        🚀 动态获取当前最优健康节点
        :param preferred_node: 业务层建议的首选节点 (来自配置)
        :return: 最终路由到的节点 ID
        """
        # 1. 检查首选节点健康状况与熔断状态
        if preferred_node and self._is_node_allowed(preferred_node):
            node = self.registry.get_node(preferred_node)
            if node.health_score > 60: # 经验阈值：如果首选节点依然健康且未熔断，则不轻易切流
                return preferred_node

        # 2. 如果首选节点已亚健康或熔断，寻找排行榜第一名且未熔断的节点
        rankings = self.registry.get_rankings()
        for r in (rankings or []):
            candidate = (r or {}).get("node")
            if candidate and self._is_node_allowed(candidate):
                if candidate != preferred_node:
                    tlog.warning(f"🔀 [智能路由] 侦测到首选节点 {preferred_node} 状态下滑或熔断，正在自动平滑转移至最优节点: {candidate}")
                return candidate

        # 3. 兜底回退：若首选节点未熔断则回退，若已熔断则尝试配置中的备用节点
        if preferred_node and self._is_node_allowed(preferred_node):
            return preferred_node

        if self.engine and hasattr(self.engine, 'config') and hasattr(self.engine.config, 'translation'):
            cfg_fallback = getattr(self.engine.config.translation, 'fallback_node', None)
            if cfg_fallback and self._is_node_allowed(cfg_fallback):
                tlog.warning(f"🔀 [智能路由] 首选节点 {preferred_node} 熔断，依赖算力中心配置平滑回退至备用节点: {cfg_fallback}")
                return cfg_fallback

        return "mock-node"

    def get_failover_node(self, failing_node: str) -> Optional[str]:
        """
        🚀 获取故障转移目标节点
        用于容灾调度算法中，当一个节点物理失败后，根据健康度与熔断状态动态决选最佳替代节点
        """
        rankings = self.registry.get_rankings()
        for r in (rankings or []):
            node_id = (r or {}).get("node")
            health = (r or {}).get("health", 0)
            if node_id and node_id != failing_node and health > 40 and self._is_node_allowed(node_id):
                tlog.info(f"🩹 [故障转移] 依赖算力调度算法，节点 {failing_node} 异常，已自动平滑切流至健康节点: {node_id}")
                return node_id

        # 若排行榜未覆盖，尝试从配置中回退 fallback_node
        if self.engine and hasattr(self.engine, 'config') and hasattr(self.engine.config, 'translation'):
            cfg_fallback = getattr(self.engine.config.translation, 'fallback_node', None)
            if cfg_fallback and cfg_fallback != failing_node and self._is_node_allowed(cfg_fallback):
                tlog.info(f"🩹 [故障转移] 依赖算力中心配置，节点 {failing_node} 异常，平滑回退至配置备用节点: {cfg_fallback}")
                return cfg_fallback

        return None
