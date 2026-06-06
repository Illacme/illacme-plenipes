# -*- coding: utf-8 -*-
"""
🧪 [Test] 运行时 AI 任务热接力与自动重试 单元测试
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.logic.ai.ai_scheduler_shards.dispatch_ops import AISchedulerDispatchOps
from core.logic.ai.model_intelligence import ModelIntelligenceHub
from core.logic.orchestration.task_orchestrator import TaskPriority


# 1. 模拟翻译器客户端
class MockTranslator:
    def __init__(self, node_name, config=None):
        self.node_name = node_name
        self.config = config or {}

    def translate(self, text, src_lang, target_lang, **kwargs):
        if self.node_name == "failing_node":
            raise RuntimeError("Simulated API Error")
        return f"Translated [{self.node_name}]: {text}"

    def generate_seo_metadata(self, text, lang, is_dry_run, **kwargs):
        return {"description": f"SEO [{self.node_name}]", "keywords": []}, True

    def translate_title(self, title, lang, is_dry_run, **kwargs):
        return f"Title [{self.node_name}]: {title}"

    def translate_metadata(self, meta, type_name, lang, is_dry_run, **kwargs):
        return meta


# 2. 模拟配置和引擎
class MockI18nTarget:
    def __init__(self, lang_code, prompt_lang):
        self.lang_code = lang_code
        self.prompt_lang = prompt_lang


class MockI18nSource:
    def __init__(self, lang_code, prompt_lang):
        self.lang_code = lang_code
        self.prompt_lang = prompt_lang


class MockI18nSettings:
    def __init__(self):
        self.enabled = True
        self.source = MockI18nSource("zh", "Chinese")
        self.targets = [MockI18nTarget("en", "English")]


class MockUsageMeter:
    def check_and_block(self, source, targets, path):
        return True


class MockBlockCache:
    def __init__(self):
        self.cache = {}

    def get_block(self, code, fingerprint):
        return self.cache.get((code, fingerprint))

    def store_block(self, code, fingerprint, content):
        self.cache[(code, fingerprint)] = content


class MockCircuitBreaker:
    def call(self, func, *args, **kwargs):
        return func(*args, **kwargs)


class MockSeoConfig:
    def __init__(self):
        self.autopilot_enabled = True


class MockConfig:
    def __init__(self):
        self.translation = MagicMock()
        self.i18n_settings = MockI18nSettings()
        self.route_matrix = []


class MockSmartRouter:
    def __init__(self, engine):
        self.engine = engine

    def get_best_node(self, preferred_node):
        return preferred_node

    def get_failover_node(self, failing_node):
        if failing_node == "failing_node":
            return "healthy_node"
        return None


class MockEngineMeta:
    def __init__(self):
        self.is_watch_mode = False


class MockEngine:
    def __init__(self):
        self.i18n = MockI18nSettings()
        self.config = MockConfig()
        self.config.system = MagicMock()
        self.config.system.throttle = MagicMock()
        self.config.system.throttle.ai_block_delay = 0
        self.seo_cfg = MockSeoConfig()
        self.meter = MockUsageMeter()
        self.block_cache = MockBlockCache()
        self.translator = MockTranslator("failing_node")
        self.circuit_breakers = {"ai": MockCircuitBreaker()}
        self.smart_router = MockSmartRouter(self)
        self.no_ai = False
        self.brain = MagicMock()
        self.meta = MockEngineMeta()
        self.dispatcher = MagicMock()
        self.asset_index = MagicMock()


class MockContext:
    def __init__(self):
        self.masked_source = "Test paragraph for translation."
        self.body_content = "Test paragraph for translation."
        self.raw_content = "Test paragraph for translation."
        self.title = "Test Title"
        self.base_fm = {}
        self.ael_iter_id = "test-ael"
        self.rel_path = "vault/doc.md"
        self.ai_health_flag = [True]
        self.slug = "test-slug"
        self.mapped_sub_dir = ""
        self.masks = {}
        self.node_assets = []
        self.node_ext_assets = []
        self.node_outlinks = []
        self.assets_lock = MagicMock()


class TestAIFaultTolerance(unittest.TestCase):
    @patch('core.logic.ai.ai_factory.TranslatorFactory._build_node')
    def test_ai_hot_failover_and_retry(self, mock_build_node):
        # 让工厂能根据节点名正确实例化对应的 MockTranslator
        mock_build_node.side_effect = lambda name, cfg: MockTranslator(name)

        engine = MockEngine()
        ctx = MockContext()

        # 初始时，failing_node 的健康分应为 100
        ModelIntelligenceHub.record_success("failing_node")
        self.assertEqual(ModelIntelligenceHub().get_health_score("failing_node"), 100)

        # 执行翻译任务调度
        res = AISchedulerDispatchOps.dispatch_targets(
            engine, ctx, engine.i18n.targets, "docs", "test_source", False, "vault/doc.md", False
        )

        # 验证返回结果
        self.assertIn("en", res)
        health = res["en"]["health"]
        seo_data = res["en"]["seo"]

        # 1. 验证健康状况和结果内容 (翻译内容必须由 healthy_node 生成)
        self.assertTrue(health)
        engine.dispatcher.dispatch.assert_called_once()
        args, kwargs = engine.dispatcher.dispatch.call_args
        
        # 对应参数位置：
        # engine.asset_index, t_fm.get('title', ctx.title), ctx.slug, t_body, t_fm, rel_path,
        # t_code, route_prefix, route_source, ctx.mapped_sub_dir, ctx.masks,
        # is_dry_run, is_target=True, node_assets=ctx.node_assets...
        title = args[1]
        body = args[3]
        target_fm = args[4]

        self.assertIn("Translated [healthy_node]", body)
        self.assertEqual(title, "Title [healthy_node]: Test Title")
        self.assertEqual(target_fm["title"], "Title [healthy_node]: Test Title")
        self.assertEqual(seo_data["description"], "SEO [healthy_node]")

        # 2. 验证 failing_node 被成功降低了健康分
        self.assertLess(ModelIntelligenceHub().get_health_score("failing_node"), 100)

        # 3. 验证缓存成功写入
        self.assertTrue(len(engine.block_cache.cache) > 0)


if __name__ == '__main__':
    unittest.main()
