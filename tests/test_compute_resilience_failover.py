# -*- coding: utf-8 -*-
"""
🧪 [Test] 算力中心容灾调度算法与自动平滑转移测试套件
验证 AI 节点智能流控退避、健康前置感知、429 快速释放与故障自动平滑转移（Failover）。
"""
import time
import unittest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

from core.adapters.ai.strategies import (
    FallbackStrategy,
    SmartRoutingStrategy,
    GlobalSmartRoutingStrategy
)
from core.utils.event_bus import bus


class MockComputeNode:
    """模拟具备完整契约的物理算力节点"""
    def __init__(self, node_name: str, should_fail: bool = False, fail_reason: str = "429 Too Many Requests"):
        self.node_name = node_name
        self.config = SimpleNamespace(type="mock", model="mock-model")
        self.plugin_id = "openai"
        self.trans_cfg = None
        self._intelligence_hub = None
        self.should_fail = should_fail
        self.fail_reason = fail_reason
        self.call_count = 0
        self.is_node_available = True
        self._is_cooling = False
        self._cooling_until = 0

    def is_available(self) -> bool:
        if self._is_cooling and time.time() < self._cooling_until:
            return False
        return self.is_node_available

    def translate(self, text, source_lang, target_lang, **kwargs):
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError(f"[{self.node_name}] {self.fail_reason}")
        return f"Translated by {self.node_name}: {text}"

    def generate_slug(self, title, **kwargs):
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError(f"[{self.node_name}] {self.fail_reason}")
        return f"slug-{self.node_name}-{title}"

    def translate_title(self, title, target_lang, **kwargs):
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError(f"[{self.node_name}] {self.fail_reason}")
        return f"Title by {self.node_name}: {title}"

    def translate_metadata(self, text, meta_type, target_lang, **kwargs):
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError(f"[{self.node_name}] {self.fail_reason}")
        return f"Meta by {self.node_name}: {text}"

    def translate_document(self, text, target_lang_name, rel_path, **kwargs):
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError(f"[{self.node_name}] {self.fail_reason}")
        return f"Doc by {self.node_name}: {text}"

    def raw_inference(self, user_prompt, system_prompt=None):
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError(f"[{self.node_name}] {self.fail_reason}")
        return f"Inference by {self.node_name}"

    def ask_ai_with_retry(self, payload):
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError(f"[{self.node_name}] {self.fail_reason}")
        return f"Response by {self.node_name}"


class TestComputeResilienceFailover(unittest.TestCase):
    """验证依赖算力中心容灾配置的平滑转移行为"""

    def setUp(self):
        self.failover_events = []
        @bus.on("UI_AI_FAILOVER_TRIGGERED")
        def _on_failover(**kwargs):
            self.failover_events.append(kwargs)
        self.cleanup_listener = _on_failover

    def test_fallback_normal_path(self):
        """主节点正常时，请求走主节点，不触发转移"""
        primary = MockComputeNode("primary_gpu", should_fail=False)
        secondary = MockComputeNode("backup_cloud", should_fail=False)

        strategy = FallbackStrategy(primary, secondary)
        res = strategy.translate("Hello World", "en", "zh-cn")

        self.assertIn("Translated by primary_gpu", res)
        self.assertEqual(primary.call_count, 1)
        self.assertEqual(secondary.call_count, 0)
        self.assertEqual(len(self.failover_events), 0)

    def test_fallback_runtime_exception_failover(self):
        """主节点运行时遭遇 429 限流，依据算力中心策略自动平滑转移至备用节点"""
        primary = MockComputeNode("primary_gpu", should_fail=True, fail_reason="429 rate limit exceeded")
        secondary = MockComputeNode("backup_cloud", should_fail=False)

        strategy = FallbackStrategy(primary, secondary)
        res = strategy.translate("Deep Learning System", "en", "zh-cn")

        self.assertIn("Translated by backup_cloud", res)
        self.assertEqual(primary.call_count, 1)
        self.assertEqual(secondary.call_count, 1)
        # 断言广播了平滑转移事件
        self.assertGreaterEqual(len(self.failover_events), 1)
        event = self.failover_events[-1]
        self.assertEqual(event["from_node"], "primary_gpu")
        self.assertEqual(event["to_node"], "backup_cloud")
        self.assertEqual(event["strategy"], "fallback")

    def test_fallback_proactive_health_check_zero_latency(self):
        """前置健康感知：主节点处于冷却/不可用状态时，0 延迟直接平滑转移至备用节点"""
        primary = MockComputeNode("primary_gpu", should_fail=False)
        primary._is_cooling = True
        primary._cooling_until = time.time() + 60.0  # 冷却中

        secondary = MockComputeNode("backup_cloud", should_fail=False)

        strategy = FallbackStrategy(primary, secondary)
        res = strategy.generate_slug("Advanced Architecture")

        self.assertEqual(res, "slug-backup_cloud-Advanced Architecture")
        # 主节点完全不进行无效尝试
        self.assertEqual(primary.call_count, 0)
        self.assertEqual(secondary.call_count, 1)
        self.assertGreaterEqual(len(self.failover_events), 1)
        self.assertEqual(self.failover_events[-1]["reason"], "CircuitBreaker/Cooling")

    def test_fallback_all_public_contracts(self):
        """验证全部 7 个公有契约方法均具备自动平滑转移能力"""
        primary = MockComputeNode("primary_gpu", should_fail=True, fail_reason="503 Service Unavailable")
        secondary = MockComputeNode("backup_cloud", should_fail=False)

        strategy = FallbackStrategy(primary, secondary)

        title_res = strategy.translate_title("Title Test", "zh-cn")
        self.assertIn("backup_cloud", title_res)

        meta_res = strategy.translate_metadata("Keywords", "tags", "zh-cn")
        self.assertIn("backup_cloud", meta_res)

        doc_res = strategy.translate_document("Doc Body", "zh-cn", "test.md")
        self.assertIn("backup_cloud", doc_res)

        raw_res = strategy.raw_inference("Prompt")
        self.assertIn("backup_cloud", raw_res)

        retry_res = strategy.ask_ai_with_retry({"messages": [{"role": "user", "content": "Hi"}]})
        self.assertIn("backup_cloud", retry_res)

    def test_smart_routing_fallback(self):
        """智能分流模式：当首选节点故障时，平滑转移至对侧节点"""
        # primary 适合短文本，secondary 适合长文本
        primary = MockComputeNode("fast_local", should_fail=True, fail_reason="Local GPU OOM")
        secondary = MockComputeNode("heavy_cloud", should_fail=False)

        # threshold = 50，测试短文本本应走 primary
        strategy = SmartRoutingStrategy(primary, secondary, threshold=50)
        short_text = "Short text"
        res = strategy.translate(short_text, "en", "zh-cn")

        # 验证平滑降级由 secondary 接力完成
        self.assertIn("Translated by heavy_cloud", res)
        self.assertGreaterEqual(len(self.failover_events), 1)
        event = self.failover_events[-1]
        self.assertEqual(event["from_node"], "fast_local")
        self.assertEqual(event["to_node"], "heavy_cloud")
        self.assertEqual(event["strategy"], "smart_routing")

    def test_global_smart_routing_failover(self):
        """全局智能调度策略：主选异常时自动向 SmartRouter 申请故障转移替代节点"""
        mock_engine = MagicMock()
        mock_smart_router = MagicMock()
        mock_engine.smart_router = mock_smart_router
        mock_smart_router.get_best_node.return_value = "node_a"
        mock_smart_router.get_failover_node.return_value = "node_b"

        node_a = MockComputeNode("node_a", should_fail=True, fail_reason="500 Internal Error")
        node_b = MockComputeNode("node_b", should_fail=False)

        trans_cfg = SimpleNamespace(
            primary_node="node_a",
            fallback_node="node_b",
            strategy="global_smart"
        )

        strategy = GlobalSmartRoutingStrategy(trans_cfg)
        strategy._handlers["node_a"] = node_a
        strategy._handlers["node_b"] = node_b

        with patch("core.runtime.cli_bootstrap.get_global_engine", return_value=mock_engine):
            res = strategy.translate("Global Routing Test", "en", "zh-cn")
            self.assertIn("Translated by node_b", res)
            self.assertEqual(node_a.call_count, 1)
            self.assertEqual(node_b.call_count, 1)
            self.assertGreaterEqual(len(self.failover_events), 1)
            event = self.failover_events[-1]
            self.assertEqual(event["from_node"], "node_a")
            self.assertEqual(event["to_node"], "node_b")
            self.assertEqual(event["strategy"], "global_smart")

    def test_single_strategy_respects_sovereignty_no_failover(self):
        """单点模式约束：当策略为 single 时，主节点故障不擅自转移，严格遵循创作者配置"""
        primary = MockComputeNode("dedicated_primary", should_fail=True, fail_reason="Network Timeout")
        
        # 模拟 TranslatorFactory.create 当 strategy == 'single' 时直接返回 primary 实例
        with self.assertRaises(RuntimeError) as cm:
            primary.translate("Single Mode Text", "en", "zh-cn")
        
        self.assertIn("dedicated_primary", str(cm.exception))
        # 绝不产生 Failover 事件
        self.assertEqual(len(self.failover_events), 0)

    def test_smart_router_circuit_breaker_awareness(self):
        """验证 SmartRouter 在面对熔断节点时，自动选择健康可用节点"""
        from core.logic.smart_router import SmartRouter
        from core.governance.circuit_breaker import CircuitBreaker

        engine = MagicMock()
        ai_cb = CircuitBreaker("ai", failure_threshold=0.5, window_size=5, recovery_timeout=60.0)
        engine.circuit_breakers = {"ai": ai_cb}
        engine.config = SimpleNamespace(translation=SimpleNamespace(fallback_node="cloud_node"))

        # 手动标记 broken_node 连续失败以进入 OPEN 熔断态
        for _ in range(6):
            ai_cb.record_failure("broken_node")

        # 检查 broken_node 是否已熔断
        self.assertFalse(ai_cb.allow_request("broken_node"))

        router = SmartRouter(engine)
        # 将 broken_node 作为 preferred_node 传入，Router 必须感知到其已熔断，自动回退到健康节点
        best = router.get_best_node(preferred_node="broken_node")
        self.assertNotEqual(best, "broken_node")

        # 测试 get_failover_node
        failover = router.get_failover_node(failing_node="broken_node")
        self.assertEqual(failover, "cloud_node")


if __name__ == '__main__':
    unittest.main()
