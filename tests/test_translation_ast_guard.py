# -*- coding: utf-8 -*-
"""
🧪 [Test] Markdown 翻译语法树断裂防线与结构完整性自动恢复守护 (P4) 单元测试
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.logic.ai.ai_scheduler_shards.dispatch_ops import AISchedulerDispatchOps


# 基础 Mock 类（继承并适配自 test_ai_fault_tolerance.py）
class MockTranslator:
    def __init__(self, node_name, behavior_list=None):
        self.node_name = node_name
        self.behavior_list = behavior_list or []
        self.call_count = 0
        self.received_remedies = []

    def translate(self, text, src_lang, target_lang, **kwargs):
        self.call_count += 1
        remedy = kwargs.get("remedy_instruction")
        self.received_remedies.append(remedy)
        
        if self.call_count <= len(self.behavior_list):
            behavior = self.behavior_list[self.call_count - 1]
            if isinstance(behavior, Exception):
                raise behavior
            return behavior
        return f"Default Translation: {text}"

    def translate_title(self, title, lang, is_dry_run, **kwargs):
        return f"Title: {title}"

    def translate_metadata(self, meta, type_name, lang, is_dry_run, **kwargs):
        return meta


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

    def get_block(self, code, fingerprint, style_hash):
        return self.cache.get((code, fingerprint, style_hash))

    def store_block(self, code, fingerprint, content, style_hash):
        self.cache[(code, fingerprint, style_hash)] = content


class MockCircuitBreaker:
    def call(self, func, *args, **kwargs):
        return func(*args, **kwargs)


class MockSeoConfig:
    pass


class MockConfig:
    def __init__(self):
        self.translation = MagicMock()
        self.translation.governance = None  # 🛡️ 显式设为 None，避免 MagicMock 产生链式虚假属性
        self.i18n_settings = MockI18nSettings()
        self.route_matrix = []


class MockSmartRouter:
    def __init__(self, engine):
        self.engine = engine
    def get_failover_node(self, failing_node):
        return None


class MockEngineMeta:
    def __init__(self):
        self.is_watch_mode = False


class MockEngine:
    def __init__(self, translator):
        self.i18n = MockI18nSettings()
        self.config = MockConfig()
        self.config.system = MagicMock()
        self.config.system.throttle = MagicMock()
        self.config.system.throttle.ai_block_delay = 0
        self.seo_cfg = MockSeoConfig()
        self.meter = MockUsageMeter()
        self.block_cache = MockBlockCache()
        self.translator = translator
        self.circuit_breakers = {"ai": MockCircuitBreaker()}
        self.smart_router = MockSmartRouter(self)
        self.no_ai = False
        self.brain = MagicMock()
        self.meta = MockEngineMeta()
        self.dispatcher = MagicMock()
        self.asset_index = MagicMock()


class MockContext:
    def __init__(self, content):
        self.masked_source = content
        self.body_content = content
        self.raw_content = content
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


# 为了模拟 block 解析，需要 mock MarkdownBlockParser 返回的 blocks
class DummyBlock:
    def __init__(self, content, block_type="paragraph"):
        self.content = content
        self.type = block_type
        self.fingerprint = f"fp_{hash(content)}"


class TestTranslationASTGuard(unittest.TestCase):
    
    def test_validate_block_structure_success(self):
        """测试结构守恒校验 - 正常闭合的场景"""
        source = "Here is a code block:\n```python\nprint('hello')\n```\nAnd a [[Wikilink]]. Also [link](http://test.com) and <span class='test'>HTML</span>, **bold**."
        translated = "这里是代码块：\n```python\nprint('hello')\n```\n以及一个 [[Wikilink]]。还有 [link](http://test.com) 和 <span class='test'>HTML</span>，**粗体**。"
        is_valid, err = AISchedulerDispatchOps.validate_block_structure(source, translated)
        self.assertTrue(is_valid)
        self.assertEqual(err, "")

    def test_validate_block_structure_code_block_unclosed(self):
        """测试结构守恒校验 - 代码块未闭合"""
        source = "```python\nprint('hello')\n```"
        translated = "```python\nprint('hello')"  # 未闭合的 ```
        is_valid, err = AISchedulerDispatchOps.validate_block_structure(source, translated)
        self.assertFalse(is_valid)
        self.assertIn("译文中代码块未闭合", err)

    def test_validate_block_structure_code_block_count_mismatch(self):
        """测试结构守恒校验 - 代码块数量不匹配"""
        source = "```python\nprint('a')\n```\n```python\nprint('b')\n```"
        translated = "```python\nprint('a')\n```"
        is_valid, err = AISchedulerDispatchOps.validate_block_structure(source, translated)
        self.assertFalse(is_valid)
        self.assertIn("代码块数量不匹配", err)

    def test_validate_block_structure_wikilinks_mismatch(self):
        """测试结构守恒校验 - Wikilinks 数量不匹配"""
        source = "Check [[Link1]] and [[Link2]]"
        translated = "查看 [[Link1]]"
        is_valid, err = AISchedulerDispatchOps.validate_block_structure(source, translated)
        self.assertFalse(is_valid)
        self.assertIn("双链 Wikilink 数量不匹配", err)

    def test_validate_block_structure_markdown_links_mismatch(self):
        """测试结构守恒校验 - Markdown 链接数量不匹配"""
        source = "Check [Link1](url1) and [Link2](url2)"
        translated = "查看 [Link1](url1)"
        is_valid, err = AISchedulerDispatchOps.validate_block_structure(source, translated)
        self.assertFalse(is_valid)
        self.assertIn("Markdown 链接数量不匹配", err)

    def test_validate_block_structure_html_tags_mismatch(self):
        """测试结构守恒校验 - HTML 标签数量不匹配"""
        source = "<div><span>Hello</span></div>"
        translated = "<div><span>Hello</div>"  # 缺少 </span>
        is_valid, err = AISchedulerDispatchOps.validate_block_structure(source, translated)
        self.assertFalse(is_valid)
        self.assertIn("HTML 标签数量不匹配", err)

    def test_validate_block_structure_bold_unclosed(self):
        """测试结构守恒校验 - 粗体未闭合"""
        source = "**bold** text"
        translated = "**bold text"  # 未闭合
        is_valid, err = AISchedulerDispatchOps.validate_block_structure(source, translated)
        self.assertFalse(is_valid)
        self.assertIn("译文中粗体/斜体控制符未闭合", err)

    @patch('core.logic.ai.ai_scheduler.AIScheduler.get_best_translator')
    @patch('core.logic.block_parser.MarkdownBlockParser.parse')
    @patch('core.logic.ai.ai_factory.TranslatorFactory._build_node')
    def test_dispatch_with_self_healing_success(self, mock_build_node, mock_parse, mock_get_best_translator):
        """测试在翻译流中自动发现格式破损、触发重试、追加 remedy 提示并最终成功"""
        source_content = "This is a **bold** structure."
        # Mock 翻译器的行为：第一次返回破损格式，第二次返回正确格式
        translator = MockTranslator("test_node", [
            "这是 **加粗 翻译",  # 格式破损（** 未闭合）
            "这是 **加粗** 翻译"   # 正常闭合
        ])
        mock_get_best_translator.return_value = translator
        mock_build_node.return_value = translator
        
        # Mock Markdown 解析，只返回这一个 block
        mock_parse.return_value = [DummyBlock(source_content, "paragraph")]

        engine = MockEngine(translator)
        ctx = MockContext(source_content)

        res = AISchedulerDispatchOps.dispatch_targets(
            engine, ctx, engine.i18n.targets, "docs", "test_source", False, "vault/doc.md", False
        )

        # 检查是否成功
        self.assertIn("en", res)
        self.assertTrue(res["en"]["health"])
        
        # 验证调用了 2 次
        self.assertEqual(translator.call_count, 2)
        
        # 验证第二次调用时 remedy_instruction 包含了自愈警告
        self.assertIsNone(translator.received_remedies[0])
        self.assertIsNotNone(translator.received_remedies[1])
        self.assertIn("主权自愈提示", translator.received_remedies[1])

        # 验证分发写入的内容是正确的译文
        args, kwargs = engine.dispatcher.dispatch.call_args
        body = args[3]
        self.assertEqual(body, "这是 **加粗** 翻译")

    @patch('core.logic.ai.ai_scheduler.AIScheduler.get_best_translator')
    @patch('core.logic.block_parser.MarkdownBlockParser.parse')
    @patch('core.logic.ai.ai_factory.TranslatorFactory._build_node')
    def test_dispatch_with_self_healing_fallback(self, mock_build_node, mock_parse, mock_get_best_translator):
        """测试在多次重试后仍然格式破损，安全回退使用原文"""
        source_content = "This is a **bold** structure."
        # 总是返回破损格式
        translator = MockTranslator("test_node", [
            "这是 **加粗 翻译 1",
            "这是 **加粗 翻译 2",
            "这是 **加粗 翻译 3",
        ])
        mock_get_best_translator.return_value = translator
        mock_build_node.return_value = translator
        
        mock_parse.return_value = [DummyBlock(source_content, "paragraph")]

        engine = MockEngine(translator)
        ctx = MockContext(source_content)

        res = AISchedulerDispatchOps.dispatch_targets(
            engine, ctx, engine.i18n.targets, "docs", "test_source", False, "vault/doc.md", False
        )

        # 检查结果，因为回退了原文，该语言目标的整体健康状态依旧被标记为 False
        self.assertIn("en", res)
        self.assertFalse(res["en"]["health"])
        
        # 验证调用了 3 次（达到了 max_retries = 3）
        self.assertEqual(translator.call_count, 3)

        # 验证分发未被调用（因为健康核验失败被拦截）
        engine.dispatcher.dispatch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
