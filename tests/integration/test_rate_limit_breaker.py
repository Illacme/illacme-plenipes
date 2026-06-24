#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_rate_limit_breaker.py
🛡️ [V88.0 Split] 熔断器状态机集成测试（从 test_rate_limit_governance.py 搬迁）。
覆盖 Sentinel 重试解析、HALF_OPEN 微流量探测惊群防御、弹性退避冷却倍增。
"""

import time
import pytest
from unittest.mock import patch, MagicMock

from core.adapters.ai.base import BaseTranslator
from core.governance.circuit_breaker import CircuitBreaker, BreakerState, NodeCircuitBreaker
from core.runtime.engine_singleton import set_global_engine

@pytest.fixture(autouse=True)
def cleanup_global_engine():
    """清理全局引擎单例以防止跨测试污染"""
    yield
    set_global_engine(None)


# ==========================================
# Mock 配置类（与 test_rate_limit_core 共享契约）
# ==========================================

class MockLimits:
    """Mock 限流参数"""
    def __init__(self, max_concurrency=5, timeout=60.0):
        self.max_concurrency = max_concurrency
        self.timeout = timeout
        self.rate_limit_qps = 100.0
        self.rate_limit_burst = 100

class MockNodeConfig:
    """Mock 节点配置"""
    def __init__(self, limits=None):
        self.limits = limits or MockLimits()

class MockTransConfig:
    """Mock 翻译模块配置"""
    def __init__(self):
        self.compute_nodes = {
            "deepseek_api": MockNodeConfig(),
            "ollama_local": MockNodeConfig()
        }
        self.max_retries = 2

class MockEngine:
    """Mock 运行时引擎，包含健康度注册与熔断器"""
    def __init__(self):
        self.imprint_id = "test-imprint"
        self.config = MagicMock()
        self.config.translation = MockTransConfig()
        self.config.get_ai_features_path.return_value = None
        self.governance = True
        self.health_registry = MagicMock()
        self.circuit_breakers = {
            "ai": CircuitBreaker("ai", failure_threshold=0.3, window_size=5, recovery_timeout=30.0)
        }

    def _resolve_path(self, p):
        """路径解析辅助"""
        return p


# ==========================================
# 熔断器状态机测试
# ==========================================

def test_sentinel_spec_retry_parsing():
    """🧪 测试六：追加验证来自 Sentinel 脚本与真实 HTTP JSON 响应中的各种特殊 429 重试标识匹配"""
    engine = MockEngine()
    set_global_engine(engine)
    
    # 物理实例化一个真实的 BaseTranslator 来做单体匹配测试（不需要真正的网络请求）
    class SimpleTranslator(BaseTranslator):
        """简易的 Mock 翻译器"""
        def _ask_ai(self, payload: dict) -> str:
            return "ok"
            
    trans = SimpleTranslator("deepseek_api", engine.config.translation)
    
    # 1. 驼峰命名且带双引号格式: "retryDelay": "15s"
    assert trans._parse_retry_after_from_error("{\"error\": {\"message\": \"Limit exceeded\", \"retryDelay\": \"15s\"}}") == 15.0
    
    # 2. 驼峰命名且带双引号数值格式: "retryDelay": "18.5"
    assert trans._parse_retry_after_from_error("{\"retryDelay\": \"18.5\"}") == 18.5

    # 3. 驼峰命名且无引号格式: retryDelay: 22
    assert trans._parse_retry_after_from_error("some error text retryDelay: 22") == 22.0

    # 4. 纯 retry in X 格式 (Sentinel 原生): "retry in 7"
    assert trans._parse_retry_after_from_error("Resource exhausted, please retry in 7 seconds") == 7.0
    assert trans._parse_retry_after_from_error("retry in 12") == 12.0

    # 5. 驼峰/连字符 retry-after 各种引号组合: "retry-after": "25"
    assert trans._parse_retry_after_from_error("{\"retry-after\": \"25\"}") == 25.0


def test_half_open_micro_flow_single_probe():
    """🧪 测试七：验证在 HALF_OPEN 状态下并发请求的惊群防御，确保同一时刻仅允许唯一的微流量探路请求"""
    # 物理实例化一个 NodeCircuitBreaker，设置极短的冷却时间 0.1s
    breaker = NodeCircuitBreaker("test_node", failure_threshold=0.3, window_size=5, recovery_timeout=0.1)
    
    # 模拟多次失败让其进入 OPEN 状态
    for _ in range(5):
        breaker.record_failure()
    assert breaker.state == BreakerState.OPEN
    
    # 等待冷却到期 0.15s
    time.sleep(0.15)
    
    # 此时，我们进行并发的 allow_request() 探测
    # 第一个 allow_request 应该成功（触发进入 HALF_OPEN，且 probe_in_progress 置为 True）
    assert breaker.allow_request() is True
    assert breaker.state == BreakerState.HALF_OPEN
    assert breaker.probe_in_progress is True
    
    # 此时在第一个探测还没返回之前，并发的第二个 allow_request 应当直接被拦截（由于 probe_in_progress == True）
    assert breaker.allow_request() is False
    
    # 当探测请求成功返回并执行 record_success 后，断言状态机恢复为 CLOSED，且 probe_in_progress 重置为 False
    breaker.record_success()
    assert breaker.state == BreakerState.CLOSED
    assert breaker.probe_in_progress is False


def test_half_open_failure_elastic_backoff():
    """🧪 测试八：验证 HALF_OPEN 探测失败时，状态机立即切回 OPEN 并对冷却时间进行弹性乘数倍增"""
    # 物理实例化一个 NodeCircuitBreaker，初始冷却时间 0.1s
    breaker = NodeCircuitBreaker("test_node", failure_threshold=0.3, window_size=5, recovery_timeout=0.1)
    
    # 模拟多次失败让其进入 OPEN 状态
    for _ in range(5):
        breaker.record_failure()
    assert breaker.state == BreakerState.OPEN
    assert breaker.current_recovery_timeout == 0.1
    
    # 等待冷却到期 0.12s
    time.sleep(0.12)
    
    # 允许第一个探测请求
    assert breaker.allow_request() is True
    assert breaker.state == BreakerState.HALF_OPEN
    assert breaker.probe_in_progress is True
    
    # 模拟探测请求失败
    breaker.record_failure()
    
    # 🚀 断言一：探测失败后应当立即重新切回 OPEN，无需等待任何历史窗口累积
    assert breaker.state == BreakerState.OPEN
    assert breaker.probe_in_progress is False
    
    # 🚀 断言二：冷却时间弹性翻倍 (0.1 * 2 = 0.2s)
    assert breaker.current_recovery_timeout == 0.2
    
    # 等待 0.15s，此时冷却时间还没到 0.2s，依然被拦截
    time.sleep(0.15)
    assert breaker.allow_request() is False
    
    # 等待剩余 of 冷却到期
    time.sleep(0.08)
    # 此时已经过了 0.23s，允许再次探测
    assert breaker.allow_request() is True
    assert breaker.state == BreakerState.HALF_OPEN
    
    # 模拟第二次探测成功
    breaker.record_success()
    
    # 🚀 断言三：探测成功后重回 CLOSED，且 current_recovery_timeout 重置为初始值 0.1s
    assert breaker.state == BreakerState.CLOSED
    assert breaker.current_recovery_timeout == 0.1
