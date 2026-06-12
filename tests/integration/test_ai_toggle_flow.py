# -*- coding: utf-8 -*-
"""
🔬 [V74.98] AI 算力开关与发布流程全链路单元测试脚本
验证内容：
1. 关闭 AI 算力时，组件卸载、API 诊断跳过以及流水线物理兜底正常跑通（无健康降级）。
2. 开启 AI 算力时，组件热重载重新被装配。
"""
import sys
import os
import shutil
import tempfile
import unittest
import copy
from unittest.mock import MagicMock

# 确保能加载项目根目录下的 core 模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from core.config.config_models import Configuration
from core.runtime.engine import IllacmeEngine
from core.logic.ai.ai_factory import TranslatorFactory
from core.governance.checks.ai import AIChecker, check_ai_availability_or_raise
from core.editorial.steps.seo import AISlugAndSEOStep
from core.editorial.image_step import ContextualImageAltStep
from core.editorial.context import SyncContext

class TestAIToggleFlow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        # 🚀 初始化物理审计账本，解决 'NoneType' object has no attribute 'log' 报错
        from core.governance.audit_ledger import initialize_ledger
        initialize_ledger(os.path.join(self.temp_dir, "audit.db"))
        
        # 建立最小化的配置模型
        self.base_data = {
            "site_url": "https://example.com",
            "metadata_dir": "metadata",
            "i18n_settings": {
                "enabled": True,
                "targets": [{"lang_code": "en", "name": "English", "prompt_lang": "English"}]
            },
            "translation": {
                "enable_ai": True,
                "compute_nodes": {
                    "test_node": {
                        "id": "test_node",
                        "type": "openai",
                        "api_key": "valid-api-key-with-enough-length",
                        "enabled": True
                    }
                },
                "primary_node": "test_node",
                "strategy": "single"
            },
            "governance": {
                "publishing_mode": "global",
                "seo_strategy": "ai_sync"
            }
        }
        self.config = Configuration.model_validate(self.base_data)
        
        # 实例化模拟的 Engine
        self.engine = IllacmeEngine(None, no_ai=False, config=self.config)
        self.engine.active_theme = "default"
        self.engine.vault_root = self.temp_dir
        self.engine.manuscript_source = MagicMock()
        self.engine.manuscript_source.root_path = self.engine.vault_root
        
        # 注入最基本的 paths 属性
        self.engine.paths = {
            "vault": self.engine.vault_root,
            "metadata": os.path.join(self.engine.vault_root, ".metadata"),
            "source_dir": os.path.join(self.engine.vault_root, "src"),
            "target_base": os.path.join(self.engine.vault_root, "dist")
        }
        os.makedirs(self.engine.paths["metadata"], exist_ok=True)
        
        # 使用工厂初始化真实的 translator（应创建成功）
        self.engine.translator = TranslatorFactory.create(self.config.translation)
        
        # 模拟 route_manager 并将 translator 对正
        self.engine.route_manager = MagicMock()
        self.engine.route_manager.translator = self.engine.translator

    def tearDown(self):
        # 释放 ledger 关联 of 连接，清理临时目录
        import gc
        gc.collect()
        shutil.rmtree(self.temp_dir)

    def test_ai_toggle_hot_unload_and_reload(self):
        """验证关闭 AI 时 translator 组件被热卸载为 None，开启时重新热加载"""
        
        # 1. 验证初始状态下，已绑定了 translator
        self.assertIsNotNone(self.engine.translator)
        
        # 2. 模拟配置关闭 AI (使用 deepcopy 彻底解耦，防止测试污染)
        closed_data = copy.deepcopy(self.base_data)
        closed_data["translation"]["enable_ai"] = False
        closed_data["governance"]["publishing_mode"] = "basic"
        closed_data["governance"]["seo_strategy"] = "heuristic"
        
        closed_config = Configuration.model_validate(closed_data)
        
        # 触发热重载事件
        self.engine._on_config_reloaded(closed_config)
        
        # 验证内存中的 translator 被清空置 None
        self.assertIsNone(self.engine.translator)
        self.assertIsNone(self.engine.route_manager.translator)
        
        # 3. 模拟配置重新开启 AI
        opened_data = copy.deepcopy(self.base_data)
        opened_config = Configuration.model_validate(opened_data)
        
        # 触发热重载事件
        self.engine._on_config_reloaded(opened_config)
        
        # 验证内存中的 translator 被重新实例化并对齐
        self.assertIsNotNone(self.engine.translator)
        self.assertIsNotNone(self.engine.route_manager.translator)

    def test_basic_mode_checks_bypass(self):
        """验证在关闭 AI 算力时，AI 可用性检查跳过且不抛错熔断"""
        
        # 1. 模拟配置关闭 AI 算力并触发热更
        closed_data = copy.deepcopy(self.base_data)
        closed_data["translation"]["enable_ai"] = False
        closed_data["governance"]["publishing_mode"] = "basic"
        closed_config = Configuration.model_validate(closed_data)
        self.engine._on_config_reloaded(closed_config)
        
        # 2. 审计连通性诊断报告
        report = AIChecker.check(self.engine)
        self.assertEqual(report["status"], "PASS")
        self.assertIn("AI 算力总控已关闭", "".join(report["details"]))
        
        # 3. 运行强关联熔断，不应抛出任何 RuntimeError 异常
        try:
            check_ai_availability_or_raise(self.engine)
        except RuntimeError as e:
            self.fail(f"在关闭 AI 时，可用性检查错误的抛出了 RuntimeError 熔断异常: {e}")

    def test_pipeline_physical_fallback_with_ai_off(self):
        """验证 AI 算力关闭时，Slug 生成和图片处理能物理兜底且不标记健康降级"""
        
        # 1. 模拟配置关闭 AI 算力并热重载
        closed_data = copy.deepcopy(self.base_data)
        closed_data["translation"]["enable_ai"] = False
        closed_data["governance"]["publishing_mode"] = "basic"
        closed_config = Configuration.model_validate(closed_data)
        self.engine._on_config_reloaded(closed_config)
        
        # 创建一个测试用的 markdown 原稿
        test_doc_path = os.path.join(self.engine.vault_root, "hello-world.md")
        with open(test_doc_path, "w", encoding="utf-8") as f:
            f.write("# Hello World\n这是一个测试图片：![](images/pic.png)")
            
        ctx = SyncContext(self.engine, test_doc_path, "", "Docs", False, False)
        ctx.title = "Hello World"
        ctx.raw_body = "这是一个测试图片：![](images/pic.png)"
        ctx.body_content = ctx.raw_body
        
        # 2. 运行 Slug 生成步骤 (AISlugAndSEOStep)
        step_seo = AISlugAndSEOStep()
        step_seo.process(ctx)
        
        # 验证 Slug 是否被物理兜底生成（如由字符清洗产生 hello-world），而不是 None
        self.assertEqual(ctx.slug, "hello-world")
        # 验证 AI 健康标记，依然是 True，不被标记为 False
        self.assertTrue(ctx.ai_health_flag[0])
        
        # 3. 运行图片处理步骤 (ContextualImageAltStep)
        step_image = ContextualImageAltStep()
        # 即使我们在配置中把 image_settings.generate_alt 开启
        self.engine.config.image_settings.generate_alt = True
        
        # 运行后应该平稳退出，不因为没有 translator 而报错
        try:
            step_image.process(ctx)
        except AttributeError as ae:
            self.fail(f"图片处理工序因为没有 translator 而抛出 AttributeError 异常: {ae}")

if __name__ == '__main__':
    unittest.main()
