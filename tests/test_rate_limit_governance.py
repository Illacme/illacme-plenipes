# -*- coding: utf-8 -*-
"""
🧪 [Test] 自适应滑动窗口限流器 (Rate Limit Shield P4) 单元测试
"""
import os
import sys
import time
import unittest
import threading
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.logic.ai.rate_limit_shield import RateLimitShield
from core.adapters.ai.base import BaseTranslator


class DummyLimits:
    def __init__(self, qps=10.0, tpm=40000):
        self.rate_limit_qps = qps
        self.max_tokens_per_min = tpm
        self.max_concurrency = 5
        self.timeout = 60.0


class TestRateLimitShield(unittest.TestCase):
    
    def setUp(self):
        self.current_time = 1000.0
        self.sleep_calls = []

    def mock_time(self):
        self.current_time += 0.001
        return self.current_time

    def mock_sleep(self, seconds):
        self.sleep_calls.append(seconds)
        self.current_time += seconds

    def test_qps_sliding_window_blocking(self):
        """测试 QPS 超出限制时，限流盾主动阻塞排队"""
        with patch('time.time', side_effect=self.mock_time), \
             patch('time.sleep', side_effect=self.mock_sleep):
             
            limits = DummyLimits(qps=2.0)
            shield = RateLimitShield("test_node", limits)
            
            # 模拟 3 次请求
            shield.acquire(estimated_tokens=10)
            shield.acquire(estimated_tokens=10)
            
            # 前两次应该没有任何 sleep 调用
            self.assertEqual(len(self.sleep_calls), 0)
            
            # 第三次，因为当前 1s 内已经有 2 个了，会触发等待
            shield.acquire(estimated_tokens=10)
            self.assertGreaterEqual(len(self.sleep_calls), 1)
            self.assertAlmostEqual(self.sleep_calls[0], 1.0, delta=0.1)

    def test_tpm_sliding_window_blocking(self):
        """测试 TPM 令牌数超出限制时，限流盾主动阻塞"""
        with patch('time.time', side_effect=self.mock_time), \
             patch('time.sleep', side_effect=self.mock_sleep):
             
            limits = DummyLimits(tpm=100)
            shield = RateLimitShield("test_node", limits)
            
            # 第一次请求消耗 60 token
            shield.acquire(estimated_tokens=60)
            self.assertEqual(len(self.sleep_calls), 0)
            
            # 第二次请求预估 50 token (60 + 50 = 110 > 100)，应该触发 sleep 60s 左右
            shield.acquire(estimated_tokens=50)
            self.assertGreaterEqual(len(self.sleep_calls), 1)
            self.assertGreaterEqual(self.sleep_calls[0], 59.9)

    def test_aimd_feedback_decay_and_recovery(self):
        """测试 AIMD 的自适应乘性衰减和加性恢复"""
        limits = DummyLimits(qps=10.0, tpm=40000)
        shield = RateLimitShield("test_node", limits)
        
        # 初始应与 limits 一致
        self.assertEqual(shield.adaptive_qps, 10.0)
        self.assertEqual(shield.adaptive_tpm, 40000.0)
        
        # 触发 429 限流报错，衰减为 70%
        shield.record_rate_limit_error()
        self.assertAlmostEqual(shield.adaptive_qps, 7.0)
        self.assertAlmostEqual(shield.adaptive_tpm, 28000.0)
        
        # 再次触发
        shield.last_429_time = 0.0
        shield.record_rate_limit_error()
        self.assertAlmostEqual(shield.adaptive_qps, 4.9)
        self.assertAlmostEqual(shield.adaptive_tpm, 19600.0)
        
        # 模拟成功调用，加性递增恢复
        shield.update_tokens(time.time(), 100)
        self.assertAlmostEqual(shield.adaptive_qps, 5.0)
        self.assertAlmostEqual(shield.adaptive_tpm, 19800.0)

    def test_multithreaded_concurrency_safety(self):
        """压力测试：模拟 10 个并发线程同时调用，验证线程安全和发送率被平滑排队"""
        limits = DummyLimits(qps=5.0)
        shield = RateLimitShield("test_node", limits)
        
        errors = []
        start_time = time.time()
        
        def worker():
            try:
                shield.acquire(estimated_tokens=10)
            except Exception as e:
                errors.append(e)
                
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        duration = time.time() - start_time
        
        # 验证无任何异常抛出（说明多线程锁安全）
        self.assertEqual(len(errors), 0)
        # 10 个请求，QPS 是 5.0，所以后 5 个被限速，总体排队时间应大于等于 0.8s
        self.assertGreaterEqual(duration, 0.8)


class MockTranslatorImpl(BaseTranslator):
    def _ask_ai(self, payload):
        # 模拟返回
        resp = MagicMock()
        resp.text = "Mocked Response text"
        resp.usage = {"prompt_tokens": 100, "completion_tokens": 50}
        return resp


class TestTranslatorIntegrationWithShield(unittest.TestCase):
    
    @patch('core.runtime.cli_bootstrap.get_global_engine')
    def test_translator_rate_limiter_integration(self, mock_get_engine):
        # Mock engine 和 config
        mock_engine = MagicMock()
        mock_engine.imprint_id = "test-imprint"
        mock_engine.config.get_ai_features_path.return_value = None
        mock_get_engine.return_value = mock_engine
        
        trans_cfg = MagicMock()
        trans_cfg.max_retries = 3
        limits = DummyLimits(qps=10.0, tpm=40000)
        node_cfg = MagicMock()
        node_cfg.limits = limits
        trans_cfg._synced_providers = {"test_node": node_cfg}
        trans_cfg.compute_nodes = {"test_node": node_cfg}
        
        translator = MockTranslatorImpl("test_node", trans_cfg)
        
        # 验证限流盾实例被成功初始化
        self.assertIsNotNone(translator.rate_limiter)
        self.assertEqual(translator.rate_limiter.limits.rate_limit_qps, 10.0)
        
        # 模拟调用 ask_ai_with_retry
        payload = {
            "messages": [
                {"role": "user", "content": "Hello LLM rate limit test."}
            ]
        }
        
        # 正常调用，应成功并更新 token
        res = translator.ask_ai_with_retry(payload)
        self.assertEqual(res, "Mocked Response text")
        
        # 验证限流盾里的 tpm_window 成功记录了更新后的真实 token 数
        self.assertTrue(len(translator.rate_limiter.tpm_window) > 0)
        record = translator.rate_limiter.tpm_window[-1]
        self.assertTrue(record[3])  # is_completed == True
        self.assertEqual(record[2], 150)  # real_tokens == 150 (100 + 50)


if __name__ == '__main__':
    unittest.main()
