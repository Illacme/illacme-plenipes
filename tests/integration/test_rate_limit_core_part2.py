#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_rate_limit_core_part2.py
🛡️ [V88.0 Split] 物理防雪崩核心集成测试（第二部分）。
覆盖高并发雪崩防御、429 自适应解析。
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
    """清理全局引擎单例以防止跨测试污染"""
    yield
    set_global_engine(None)


# ==========================================
# 1. 物理 Mock 配置类
# ==========================================

class MockLimits:
    """Mock 限制参数配置类"""
    def __init__(self, max_concurrency=5, timeout=60.0):
        self.max_concurrency = max_concurrency
        self.timeout = timeout
        self.rate_limit_qps = 100.0
        self.rate_limit_burst = 100


class MockNodeConfig:
    """Mock 计算节点配置类"""
    def __init__(self, limits=None):
        self.limits = limits or MockLimits()


class MockTransConfig:
    """Mock 翻译模块配置类"""
    def __init__(self):
        self.compute_nodes = {
            "deepseek_api": MockNodeConfig(),
            "ollama_local": MockNodeConfig()
        }
        self.max_retries = 2


class MockEngine:
    """Mock 运行时引擎，提供熔断器和配置注册"""
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
        """物理路径解析辅助"""
        return p


# ==========================================
# 2. 物理 Mock 翻译网关
# ==========================================

class FakeTranslator(BaseTranslator):
    """用于测试重试与异常行为的 Mock 翻译器"""
    def __init__(self, node_name, trans_cfg, behavior_func):
        super().__init__(node_name, trans_cfg)
        self.behavior_func = behavior_func

    def _ask_ai(self, payload: dict) -> str:
        """核心询问逻辑，直接代入测试指定的行为函数"""
        return self.behavior_func(payload)


# ==========================================
# 3. 核心集成测试
# ==========================================

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

    # 物理拦截 BaseTranslator 内部的物理休眠通道以避免阻断，并多线程安全地记录退避时间
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
    # 异常应该包含"熔断状态"或"AI_CIRCUIT_BREAKER_OPEN"
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
        """Mock Gemini 的重试延迟持续时间"""
        def __init__(self, seconds, nanos=0):
            self.seconds = seconds
            self.nanos = nanos

    class MockGeminiException(Exception):
        """Mock Gemini/Google Cloud 异常类"""
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
