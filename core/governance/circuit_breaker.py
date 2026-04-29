#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - AI Circuit Breaker
模块职责：防御性算力保护。监控 AI 请求异常率，在 API 级联故障时自动熔断。
🛡️ [AEL-Iter-v1.0]：商用级 AI 可靠性网关。
"""

import threading
import time
from enum import Enum
from core.utils.tracing import tlog

class BreakerState(Enum):
    CLOSED = "CLOSED"     # 正常工作
    OPEN = "OPEN"         # 熔断中 (拦截请求)
    HALF_OPEN = "HALF"   # 尝试恢复

class CircuitBreaker:
    """🚀 [V1.0] AI 算力熔断器"""

    def __init__(self, name: str, failure_threshold: float = 0.5, window_size: int = 20, recovery_timeout: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.window_size = window_size
        self.recovery_timeout = recovery_timeout
        
        self.state = BreakerState.CLOSED
        self.history = []  # [(timestamp, success_bool)]
        self.lock = threading.Lock()
        self.last_failure_time = 0

    def call(self, func, *args, **kwargs):
        """🚀 [V22.5] 熔断器包装执行：监控异常并保护后端算力"""
        if not self.allow_request():
            raise Exception(f"🛡️ [Breaker] {self.name} 处于熔断状态 ({self.state})，请求已被拦截。")
            
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e

    def allow_request(self) -> bool:
        """准入检查：判断是否允许发起 AI 请求"""
        with self.lock:
            if self.state == BreakerState.CLOSED:
                return True
                
            if self.state == BreakerState.OPEN:
                # 检查冷却时间是否已过
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    tlog.info("🛡️ [Breaker] 熔断冷却结束，尝试进入 HALF_OPEN 探测模式...")
                    self.state = BreakerState.HALF_OPEN
                    return True
                return False
                
            if self.state == BreakerState.HALF_OPEN:
                # 仅允许一个探测请求 (简单实现)
                return True
                
        return False

    def record_success(self):
        with self.lock:
            self._add_to_history(True)
            if self.state == BreakerState.HALF_OPEN:
                tlog.info("🟢 [Breaker] 探测请求成功，AI 算力网关已恢复 (CLOSED)。")
                self.state = BreakerState.CLOSED
                self.history = [] # 重置历史

    def record_failure(self):
        with self.lock:
            self._add_to_history(False)
            self.last_failure_time = time.time()
            
            # 计算失败率
            failures = [h for h in self.history if not h[1]]
            if len(self.history) >= 5: # 至少有 5 个样本再判定
                failure_rate = len(failures) / len(self.history)
                if failure_rate > self.failure_threshold:
                    if self.state != BreakerState.OPEN:
                        tlog.error(f"🚨 [Breaker] AI 连续请求异常 (失败率: {failure_rate*100:.1f}%)！触发算力熔断。")
                        self.state = BreakerState.OPEN
                        from core.utils.event_bus import bus
                        bus.emit("UI_AI_BREAKER_TRIPPED", rate=failure_rate)

    def _add_to_history(self, success: bool):
        self.history.append((time.time(), success))
        # 维持滑动窗口
        if len(self.history) > self.window_size:
            self.history.pop(0)

# 🚀 全局 AI 熔断器 (默认回退)
ai_breaker = CircuitBreaker("Global-AI")
