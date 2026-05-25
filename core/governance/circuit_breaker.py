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

class NodeCircuitBreaker:
    """🛡️ [V3.0] 独立的单节点熔断状态机 (半开微流量与弹性恢复版)"""
    
    def __init__(self, name: str, failure_threshold: float, window_size: int, recovery_timeout: float):
        self.name = name
        self.failure_threshold = failure_threshold
        self.window_size = window_size
        self.recovery_timeout = recovery_timeout
        
        self.state = BreakerState.CLOSED
        self.history = []  # [(timestamp, success_bool)]
        self.lock = threading.Lock()
        self.last_failure_time = 0
        
        # 🚀 [V3.0] 动态算力熔断因子
        self.current_recovery_timeout = recovery_timeout
        self.probe_in_progress = False

    def allow_request(self) -> bool:
        """准入检查：判断是否允许发起 AI 请求"""
        with self.lock:
            if self.state == BreakerState.CLOSED:
                return True
                
            if self.state == BreakerState.OPEN:
                # 检查自适应弹性的冷却时间是否已过
                if time.time() - self.last_failure_time > self.current_recovery_timeout:
                    tlog.info(f"🛡️ [Breaker] {self.name} 熔断冷却结束，尝试进入 HALF_OPEN 探测模式...")
                    self.state = BreakerState.HALF_OPEN
                    self.probe_in_progress = True
                    return True
                return False
                
            if self.state == BreakerState.HALF_OPEN:
                # 🚀 [V3.0] 仅允许唯一的探测请求进行微流量探路，防止高并发下探路惊群效应
                if self.probe_in_progress:
                    return False
                self.probe_in_progress = True
                return True
                
        return False

    def record_success(self):
        with self.lock:
            self._add_to_history(True)
            self.probe_in_progress = False
            if self.state == BreakerState.HALF_OPEN:
                tlog.info(f"🟢 [Breaker] 探测请求成功，{self.name} 算力网关已恢复 (CLOSED)。")
                self.state = BreakerState.CLOSED
                self.current_recovery_timeout = self.recovery_timeout  # 重置弹性冷却时间
                self.history = [] # 重置历史

    def record_failure(self):
        with self.lock:
            self._add_to_history(False)
            self.last_failure_time = time.time()
            self.probe_in_progress = False
            
            # 🚀 [V3.0] 探测失败快速闭环：在 HALF_OPEN 下如果失败，立即踢回 OPEN，并拉长冷却时间
            if self.state == BreakerState.HALF_OPEN:
                # 弹性倍增冷却时间，最大不超过 300 秒 (5分钟)
                self.current_recovery_timeout = min(300.0, self.current_recovery_timeout * 2)
                tlog.error(f"🚨 [Breaker] {self.name} 探测请求失败，重新切回 OPEN 熔断状态。下一次冷却时间弹性拉长至: {self.current_recovery_timeout}s")
                self.state = BreakerState.OPEN
                return
            
            # 原有 CLOSED 状态下的失败率判定逻辑保持不变
            failures = [h for h in self.history if not h[1]]
            if len(self.history) >= 5: # 至少有 5 个样本再判定
                failure_rate = len(failures) / len(self.history)
                if failure_rate > self.failure_threshold:
                    if self.state != BreakerState.OPEN:
                        tlog.error(f"🚨 [Breaker] {self.name} 连续请求异常 (失败率: {failure_rate*100:.1f}%)！触发算力熔断。")
                        self.state = BreakerState.OPEN
                        # 进入 OPEN 时，初始化弹性冷却时间
                        self.current_recovery_timeout = self.recovery_timeout
                        from core.utils.event_bus import bus
                        bus.emit("UI_AI_BREAKER_TRIPPED", rate=failure_rate, node_name=self.name)

    def _add_to_history(self, success: bool):
        self.history.append((time.time(), success))
        # 维持滑动窗口
        if len(self.history) > self.window_size:
            self.history.pop(0)


class CircuitBreaker:
    """🚀 [V2.0] 自适应节点隔离型 AI 算力熔断器 (多维度容器)"""

    def __init__(self, name: str, failure_threshold: float = 0.5, window_size: int = 20, recovery_timeout: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.window_size = window_size
        self.recovery_timeout = recovery_timeout
        
        # 默认的全局熔断状态 (兼容旧测试)
        self.global_breaker = NodeCircuitBreaker(name, failure_threshold, window_size, recovery_timeout)
        self.node_breakers = {}
        self.lock = threading.Lock()
        self._thread_local = threading.local()

    def _get_breaker(self, node_name: str = None) -> NodeCircuitBreaker:
        if not node_name:
            return self.global_breaker
        with self.lock:
            if node_name not in self.node_breakers:
                self.node_breakers[node_name] = NodeCircuitBreaker(
                    node_name,
                    self.failure_threshold,
                    self.window_size,
                    self.recovery_timeout
                )
            return self.node_breakers[node_name]

    def call(self, func, *args, node_name: str = None, **kwargs):
        """🚀 [V2.0] 熔断器包装执行：监控异常并保护后端算力"""
        # 智能提取 node_name
        if not node_name:
            node_name = getattr(func, '__self__', None) and getattr(func.__self__, 'node_name', None)
            
        breaker = self._get_breaker(node_name)
        if not breaker.allow_request():
            raise Exception(f"🛡️ [Breaker] {breaker.name} 处于熔断状态 ({breaker.state})，请求已被拦截。")
            
        # 初始化线程局部状态
        self._thread_local.reported = False
        self._thread_local.current_node = node_name
        
        try:
            result = func(*args, **kwargs)
            # 若底层已经完成了去冗余上报，最外层不再重复上报
            if not getattr(self._thread_local, 'reported', False):
                breaker.record_success()
            return result
        except Exception as e:
            if not getattr(self._thread_local, 'reported', False):
                breaker.record_failure()
            raise e
        finally:
            self._thread_local.reported = False
            self._thread_local.current_node = None

    def allow_request(self, node_name: str = None) -> bool:
        """准入检查：判断是否允许发起 AI 请求"""
        return self._get_breaker(node_name).allow_request()

    def record_success(self, node_name: str = None):
        self._get_breaker(node_name).record_success()

    def record_failure(self, node_name: str = None):
        self._get_breaker(node_name).record_failure()


# 🚀 全局 AI 熔断器 (默认回退)
ai_breaker = CircuitBreaker("Global-AI")

