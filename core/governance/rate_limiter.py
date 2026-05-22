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
    """🚀 [V2.0] 治理守卫：管理全域限流策略，支持动态参数自适应热重载"""
    
    _limiters: Dict[str, RateLimiter] = {}
    _lock = threading.Lock()

    @classmethod
    def check_quota(cls, imprint_id: str, cost_unit: int = 1) -> bool:
        """检查配额，如果超限则返回 False"""
        with cls._lock:
            # 1. 尝试自适应热重载配置
            qps = 10.0
            burst = 20
            from core.runtime.cli_bootstrap import get_global_engine
            engine = get_global_engine()
            if engine and hasattr(engine, 'config') and hasattr(engine.config, 'translation'):
                trans_cfg = engine.config.translation
                primary = getattr(trans_cfg, 'primary_node', None)
                if primary and primary in trans_cfg.compute_nodes:
                    limits = trans_cfg.compute_nodes[primary].limits
                    qps = getattr(limits, 'rate_limit_qps', 10.0)
                    burst = getattr(limits, 'rate_limit_burst', 20)

            # 2. 如果不存在或者配置改变了，则进行热重载与自愈
            if imprint_id not in cls._limiters:
                cls._limiters[imprint_id] = RateLimiter(qps=qps, burst=burst)
            else:
                limiter = cls._limiters[imprint_id]
                if limiter.qps != qps or limiter.burst != burst:
                    tlog.info(f"🔄 [GovernanceGuard] 检测到限流配置发生物理变动，执行热重载自愈：QPS={qps}, Burst={burst}")
                    limiter.qps = qps
                    limiter.burst = burst
            
            limiter = cls._limiters[imprint_id]
        
        if not limiter.consume(cost_unit):
            tlog.warning(f"⚠️ [GovernanceGuard] 出版品牌 '{imprint_id}' 算力请求频率超限，已触发主动降级。")
            return False
        return True


# 全局治理守卫
guard = GovernanceGuard
