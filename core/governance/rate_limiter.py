#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - Rate Limiter (配额限流器)
模块职责：算力资源公平分配。防止单个工作空间过度消耗共享算力资源。
🛡️ [AEL-Iter-v1.0]：令牌桶算法限流实现。
"""

import time
import threading
from typing import Dict
from core.utils.tracing import tlog

class RateLimiter:
    """🚀 [V1.0] 限流器：保护系统不被算力洪峰冲垮"""
    
    def __init__(self, qps: float = 5.0, burst: int = 10):
        self.qps = qps
        self.burst = burst
        self.tokens = float(burst)
        self.last_refill = time.perf_counter()
        self.lock = threading.Lock()

    def consume(self, amount: int = 1) -> bool:
        """尝试消耗令牌"""
        with self.lock:
            now = time.perf_counter()
            # 补充令牌
            elapsed = now - self.last_refill
            self.tokens = min(float(self.burst), self.tokens + elapsed * self.qps)
            self.last_refill = now
            
            if self.tokens >= amount:
                self.tokens -= amount
                return True
            return False

class GovernanceGuard:
    """🚀 [V1.0] 治理守卫：管理全域限流策略"""
    
    _limiters: Dict[str, RateLimiter] = {}
    _lock = threading.Lock()

    @classmethod
    def check_quota(cls, territory_id: str, cost_unit: int = 1) -> bool:
        """检查配额，如果超限则返回 False"""
        with cls._lock:
            if territory_id not in cls._limiters:
                # 🚀 [V24.6 性能对齐] 默认 QPS 提升至 10.0，突发提升至 20 (对齐块级并行与多语种并发)
                cls._limiters[territory_id] = RateLimiter(qps=10.0, burst=20)
            
            limiter = cls._limiters[territory_id]
        
        if not limiter.consume(cost_unit):
            tlog.warning(f"⚠️ [GovernanceGuard] 主权疆域 '{territory_id}' 算力请求频率超限，已触发主动降级。")
            return False
        return True


# 全局治理守卫
guard = GovernanceGuard
