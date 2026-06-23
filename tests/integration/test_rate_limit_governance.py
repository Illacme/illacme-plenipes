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
        self.rate_limit_qps = 100.0
        self.rate_limit_burst = 100

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
        self.config.get_ai_features_path.return_value = None
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


def test_adaptive_429_parsing_and_retry_backoff():
    """🧪 测试五：追加验证 429 报错中 Retry-After/try again 及 Gemini 特有结构化重试属性的智能提取与应用"""
    engine = MockEngine()
    set_global_engine(engine)

    sleep_times = []
    def dummy_sleep(secs):
        sleep_times.append(secs)

    # 模拟 Gemini / Google Cloud SDK 专有的 ResourceExhausted 异常结构
    class MockGeminiDuration:
        def __init__(self, seconds, nanos=0):
            self.seconds = seconds
            self.nanos = nanos

    class MockGeminiException(Exception):
        def __init__(self, message, retry_seconds=None, metadata=None):
            super().__init__(message)
            if retry_seconds is not None:
                self.retry_delay = MockGeminiDuration(retry_seconds)
            if metadata is not None:
                self.metadata = metadata

    # 1. 第一次重试：模拟普通 429 文本解析（try again in 8.5 seconds）
    # 2. 第二次重试：模拟 Gemini 异常对象 metadata 属性解析（retry-after: 9.5）
    # 3. 彻底失败：模拟 Gemini 异常对象 retry_delay 结构化属性（12.0s）
    call_count = 0
    def adaptive_ai_behavior(payload):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("HTTP 429: Rate Limit. Please try again in 8.5 seconds.")
        elif call_count == 2:
            raise MockGeminiException("Quota exceeded", metadata={"retry-after": "9.5"})
        else:
            raise MockGeminiException("Quota exceeded", retry_seconds=12.0)

    trans = FakeTranslator("deepseek_api", engine.config.translation, adaptive_ai_behavior)

    with patch.object(BaseTranslator, "_sleep", side_effect=dummy_sleep):
        with pytest.raises(Exception) as exc_info:
            trans.ask_ai_with_retry({"prompt": "Hello"})
            
        assert "quota exceeded" in str(exc_info.value).lower() or "429" in str(exc_info.value).lower()

    # max_retries = 2，一共调用了 3 次
    assert call_count == 3
    # 发生了 2 次重试等待
    assert len(sleep_times) == 2
    
    # 第一次等待：由 "try again in 8.5 seconds" 得到 8.5，加上 Jitter 噪声 [0.1, 0.5] -> [8.6, 9.0]
    assert 8.6 <= sleep_times[0] <= 9.0
    # 第二次等待：由 metadata {"retry-after": "9.5"} 得到 9.5，加上 Jitter 噪声 [0.1, 0.5] -> [9.6, 10.0]
    assert 9.6 <= sleep_times[1] <= 10.0

    # 验证最终彻底失败时，物理冷冻时间根据最后的 retry_delay 属性（12.0s）自适应设置为 12.0s
    assert trans.is_cooling() is True
    assert 11.0 <= (trans._cooling_until - time.time()) <= 13.0


def test_sentinel_spec_retry_parsing():
    """🧪 测试六：追加验证来自 Sentinel 脚本与真实 HTTP JSON 响应中的各种特殊 429 重试标识匹配"""
    engine = MockEngine()
    set_global_engine(engine)
    
    # 物理实例化一个真实的 BaseTranslator 来做单体匹配测试（不需要真正的网络请求）
    class SimpleTranslator(BaseTranslator):
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
    from core.governance.circuit_breaker import BreakerState, NodeCircuitBreaker
    
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
    from core.governance.circuit_breaker import BreakerState, NodeCircuitBreaker
    
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
    
    # 等待剩余的冷却到期
    time.sleep(0.08)
    # 此时已经过了 0.23s，允许再次探测
    assert breaker.allow_request() is True
    assert breaker.state == BreakerState.HALF_OPEN
    
    # 模拟第二次探测成功
    breaker.record_success()
    
    # 🚀 断言三：探测成功后重回 CLOSED，且 current_recovery_timeout 重置为初始值 0.1s
    assert breaker.state == BreakerState.CLOSED
    assert breaker.current_recovery_timeout == 0.1



