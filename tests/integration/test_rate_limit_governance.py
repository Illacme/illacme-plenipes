#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_rate_limit_governance.py
物理防雪崩集成测试：验证高并发多语种同步下，AI 限流治理的隔离熔断、去冗余汇报及 Jitter 随机指数退避重试的正确性。
"""

import time
import pytest
import threading
from unittest.mock import patch, MagicMock

from core.adapters.ai.base import BaseTranslator
from core.governance.circuit_breaker import CircuitBreaker, BreakerState
from core.runtime.engine_singleton import set_global_engine

@pytest.fixture(autouse=True)
def cleanup_global_engine():
    yield
    set_global_engine(None)

# ==========================================
# 1. 物理 Mock 配置类
# ==========================================

class MockLimits:
    def __init__(self, max_concurrency=5, timeout=60.0):
        self.max_concurrency = max_concurrency
        self.timeout = timeout
        self.rate_limit_qps = 10.0
        self.rate_limit_burst = 20

class MockNodeConfig:
    def __init__(self, limits=None):
        self.limits = limits or MockLimits()

class MockTransConfig:
    def __init__(self):
        self.compute_nodes = {
            "deepseek_api": MockNodeConfig(),
            "ollama_local": MockNodeConfig()
        }
        self.max_retries = 2

class MockEngine:
    def __init__(self):
        self.imprint_id = "test-imprint"
        self.config = MagicMock()
        self.config.translation = MockTransConfig()
        self.governance = True
        self.health_registry = MagicMock()
        
        # 熔断器配置
        self.circuit_breakers = {
            "ai": CircuitBreaker("ai", failure_threshold=0.3, window_size=5, recovery_timeout=30.0)
        }

    def _resolve_path(self, p):
        return p

# ==========================================
# 2. 物理 Mock 翻译网关
# ==========================================

class FakeTranslator(BaseTranslator):
    def __init__(self, node_name, trans_cfg, behavior_func):
        super().__init__(node_name, trans_cfg)
        self.behavior_func = behavior_func

    def _ask_ai(self, payload: dict) -> str:
        return self.behavior_func(payload)

# ==========================================
# 3. 核心集成测试
# ==========================================

def test_full_jitter_backoff_and_cooling():
    """🧪 测试一：验证 Full Jitter 随机指数退避和 30s 冷却物理缩短机制"""
    engine = MockEngine()
    set_global_engine(engine)

    sleep_times = []
    
    def dummy_sleep(secs):
        sleep_times.append(secs)
        
    call_count = 0
    def bad_ai_behavior(payload):
        nonlocal call_count
        call_count += 1
        raise Exception("HTTP 429 Rate Limit Exceeded")

    trans = FakeTranslator("deepseek_api", engine.config.translation, bad_ai_behavior)

    # 物理拦截 BaseTranslator 内部的物理休眠通道以避免测试阻塞，并记录退避时间
    with patch.object(BaseTranslator, "_sleep", side_effect=dummy_sleep):
        with pytest.raises(Exception) as exc_info:
            trans.ask_ai_with_retry({"prompt": "Hello"})
            
        assert "429" in str(exc_info.value).lower() or "rate limit" in str(exc_info.value).lower()

    # max_retries = 2，所以总共调用了 1 + 2 = 3 次
    assert call_count == 3
    # time.sleep 应该被触发了 2 次
    assert len(sleep_times) == 2
    
    # 验证 Full Jitter 退避公式的边界：
    # 第一次重试 wait_time = random.uniform(0, min(15.0, 2**0 * 1.5)) -> [0, 1.5]
    # 第二次重试 wait_time = random.uniform(0, min(15.0, 2**1 * 1.5)) -> [0, 3.0]
    assert 0.0 <= sleep_times[0] <= 1.5
    assert 0.0 <= sleep_times[1] <= 3.0

    # 验证 30s 冷却物理触发
    assert trans.is_cooling() is True
    assert 25.0 <= (trans._cooling_until - time.time()) <= 31.0


def test_node_level_isolation_breaker():
    """🧪 测试二：验证单节点遭遇算力限流被熔断后，本地健康节点完全不受影响"""
    engine = MockEngine()
    set_global_engine(engine)

    # 用来统计各自调用的标志
    deepseek_called = 0
    ollama_called = 0

    def deepseek_behavior(payload):
        nonlocal deepseek_called
        deepseek_called += 1
        raise Exception("HTTP 429 Rate Limit Exceeded")

    def ollama_behavior(payload):
        nonlocal ollama_called
        ollama_called += 1
        return "Translated Content"

    ds_trans = FakeTranslator("deepseek_api", engine.config.translation, deepseek_behavior)
    ol_trans = FakeTranslator("ollama_local", engine.config.translation, ollama_behavior)

    cb = engine.circuit_breakers["ai"]

    # 1. 物理触发 deepseek_api 故障并由最外层 call 包装，引发熔断
    # 我们的 cb.failure_threshold = 0.3, window_size = 5。
    # 至少需要积累 5 个样本才会起爆。我们这里连续调用 5 次，确保跨过 len(history) >= 5 的门槛并 100% 触发熔断
    with patch("time.sleep"):  # 拦截重试等待
        for _ in range(5):
            try:
                cb.call(ds_trans.ask_ai_with_retry, {"prompt": "Hello"}, node_name="deepseek_api")
            except Exception:
                pass

    # 断言 deepseek_api 节点的状态已物理熔断为 OPEN
    ds_breaker = cb._get_breaker("deepseek_api")
    assert ds_breaker.state == BreakerState.OPEN

    # 2. 再次尝试调用 deepseek_api，应该直接被熔断阻断拦截
    with pytest.raises(Exception) as exc_info:
        cb.call(ds_trans.ask_ai_with_retry, {"prompt": "Hello"}, node_name="deepseek_api")
    assert "处于熔断状态" in str(exc_info.value) or "AI_CIRCUIT_BREAKER_OPEN" in str(exc_info.value)

    # 3. 此时物理验证 ollama_local 本地健康节点的状态是否依然为 CLOSED，且能完美调用成功！
    ol_breaker = cb._get_breaker("ollama_local")
    assert ol_breaker.state == BreakerState.CLOSED

    # 完美成功，调用不受 deepseek_api 级联株连！
    res = cb.call(ol_trans.ask_ai_with_retry, {"prompt": "Hello"}, node_name="ollama_local")
    assert res == "Translated Content"
    assert ollama_called == 1


def test_single_responsibility_telemetry():
    """🧪 测试三：验证去冗余故障汇报，杜绝双重上报的故障计数放大"""
    engine = MockEngine()
    set_global_engine(engine)

    def bad_ai_behavior(payload):
        raise Exception("Fatal Error")

    trans = FakeTranslator("deepseek_api", engine.config.translation, bad_ai_behavior)
    cb = engine.circuit_breakers["ai"]
    ds_breaker = cb._get_breaker("deepseek_api")

    # 初始状态
    assert len(ds_breaker.history) == 0

    # 物理调用一次失败（带 max_retries = 2 重试，底层重试了 3 次，但最外层仅捕获 1 次异常并记录 1 次 failure）
    with patch.object(BaseTranslator, "_sleep"):
        try:
            cb.call(trans.ask_ai_with_retry, {"prompt": "Hello"}, node_name="deepseek_api")
        except Exception:
            pass

    # 验证去冗余：物理熔断器历史中，应当只有 1 次失败记录！而不是 3 次或 4 次！
    assert len(ds_breaker.history) == 1
    assert ds_breaker.history[0][1] is False  # 是一次失败的记录


def test_concurrency_governance_avalanche_prevention():
    """🧪 测试四：模拟 15 个高并发多语种翻译线程，测试 Full Jitter 在大并发下的雪崩压实能力"""
    engine = MockEngine()
    set_global_engine(engine)

    sleep_values = []
    lock = threading.Lock()

    def thread_safe_sleep(secs):
        with lock:
            sleep_values.append(secs)

    def bad_ai_behavior(payload):
        raise Exception("HTTP 429 Rate Limit Exceeded")

    trans = FakeTranslator("deepseek_api", engine.config.translation, bad_ai_behavior)
    cb = engine.circuit_breakers["ai"]

    # 准备并发启动 15 个翻译线程
    threads = []
    exceptions_caught = []
    
    def worker():
        try:
            cb.call(trans.ask_ai_with_retry, {"prompt": "Hello"}, node_name="deepseek_api")
        except Exception as e:
            with lock:
                exceptions_caught.append(e)

    # 物理拦截 BaseTranslator 内部的物理休眠通道以避免阻塞，并多线程安全地记录退避时间
    with patch.object(BaseTranslator, "_sleep", side_effect=thread_safe_sleep):
        for _ in range(15):
            t = threading.Thread(target=worker)
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    # 验证熔断器的起爆防御性表现：
    # 1. 熔断状态必须被置为 OPEN
    ds_breaker = cb._get_breaker("deepseek_api")
    assert ds_breaker.state == BreakerState.OPEN

    # 2. 至少有部分前期调用的线程正常进入了 retry loop，产生了一些 Jitter 退避时长
    assert len(sleep_values) > 0

    # 3. 产生的所有退避时间都符合 Full Jitter 的边界
    for val in sleep_values:
        assert 0.0 <= val <= 3.0

    # 4. 后期启动的线程应该被熔断器直接拦截，表现为直接抛出快速失败异常
    # 异常应该包含“熔断状态”或“AI_CIRCUIT_BREAKER_OPEN”
    has_circuit_breaker_exception = False
    for exc in exceptions_caught:
        msg = str(exc)
        if "处于熔断状态" in msg or "AI_CIRCUIT_BREAKER_OPEN" in msg:
            has_circuit_breaker_exception = True
            break
            
    assert has_circuit_breaker_exception is True, "熔断起爆后，并没有任何并发线程被快速阻断拦截！"
