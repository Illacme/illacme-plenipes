# -*- coding: utf-8 -*-
"""
🧪 [Test] 段落级翻译缓存与断点续传集成测试
"""
import os
import sys
import shutil
import unittest
import yaml
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.governance.imprint_manager import ImprintManager
from core.runtime.engine_factory import EngineFactory
from services.api.logic.dispatch_ops import get_dispatch_status_facade


class TestParagraphTranslationCache(unittest.TestCase):
    def setUp(self):
        self.test_press = "test_paragraph_cache_press"
        self.test_root = os.path.abspath("tests/test_sandbox_cache")
        self.imprint_root = os.path.join(self.test_root, "imprints")
        self.imprint_dir = os.path.join(self.imprint_root, self.test_press)
        
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
        os.makedirs(self.imprint_root, exist_ok=True)
        
        from core.utils.event_bus import bus
        bus.reset()

    def tearDown(self):
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
        from core.utils.event_bus import bus
        bus.reset()

    def test_paragraph_cache_and_resume_lifecycle(self):
        """🚀 测试段落级缓存、断点中断拦截、以及故障自愈续传的完整生命周期"""
        with patch('core.config.config.IMPRINT_DIR', self.imprint_root), \
             patch('core.runtime.engine_preflight.IMPRINT_DIR', self.imprint_root), \
             patch('core.governance.imprint_manager.IMPRINT_DIR', self.imprint_root), \
             patch('core.config.assembler.IMPRINT_DIR', self.imprint_root):
            
            im = ImprintManager(root_dir=self.test_root)
            mock_vault = os.path.abspath("test_mock_vault_cache")
            if os.path.exists(mock_vault):
                shutil.rmtree(mock_vault)
            os.makedirs(mock_vault, exist_ok=True)
            
            try:
                success = im.init_sovereign_imprint(self.test_press, manuscripts_path=mock_vault)
                self.assertTrue(success)
                
                # 1. 写入一个包含 3 个段落（语义块）的测试文档
                doc_path = "Docs/Sovereignty_Cache_Test.md"
                os.makedirs(os.path.join(mock_vault, "Docs"), exist_ok=True)
                with open(os.path.join(mock_vault, doc_path), 'w', encoding='utf-8') as f:
                    f.write(
                        "---\n"
                        "title: Paragraph Cache Test\n"
                        "---\n"
                        "First block content here.\n"
                        "\n"
                        "Second block content here.\n"
                        "\n"
                        "Third block content here."
                    )
                
                # 2. 配置 YAML (启用英语作为目标语种，以便触发翻译)
                config_path = os.path.join(self.imprint_dir, "configs", "config.imprint.yaml")
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = yaml.safe_load(f)
                
                cfg['press_name'] = self.test_press
                cfg['vault_root'] = mock_vault
                cfg['block_cache_dir'] = os.path.join(self.imprint_dir, 'blocks_cache')
                cfg['translation'] = {
                    'enable_ai': True,
                    'llm_concurrency': 1,
                    'compute_nodes': {
                        'lmstudio_local': {
                            'id': 'lmstudio_local',
                            'type': 'lmstudio',
                            'api_key': 'dummy-key',
                            'enabled': True
                        }
                    }
                }
                cfg['output_paths'] = {
                    'source_dir': os.path.join(self.imprint_dir, 'dist/source'),
                    'site_dir': os.path.join(self.imprint_dir, 'dist/static'),
                    'assets_dir': os.path.join(self.imprint_dir, 'dist/assets'),
                    'graph_json_dir': os.path.join(self.imprint_dir, 'dist/graph')
                }
                cfg['metadata_db'] = os.path.join(self.imprint_dir, 'core/press.db')
                cfg['i18n_settings'] = {
                    'enabled': True, 
                    'source': {'lang_code': 'zh', 'prompt_lang': 'Chinese'}, 
                    'targets': [{'lang_code': 'en', 'prompt_lang': 'English'}]
                }
                cfg['system'] = {
                    'data_root': self.imprint_dir, 
                    'allowed_extensions': ['.md'], 
                    'data_paths': {},
                    'log_level': 'INFO', 
                    'max_workers': 1, 
                    'auto_save_interval': 60
                }
                cfg['active_theme'] = 'default'
                cfg['route_matrix'] = []
                cfg['governance'] = {
                    'publishing_mode': 'global',
                    'seo_strategy': 'ai_sync'
                }
                cfg['ingress_settings'] = {
                    'source_type': 'local',
                    'ingress_rules': [{'source': 'Docs', 'target': 'docs'}]
                }
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(cfg, f)

                # 3. 实例化引擎并准备 Mock
                engine = EngineFactory.create_engine(config_path, no_ai=False, imprint_id=self.test_press)
                self.assertIsNotNone(engine)
                
                # 4. 设置 Mock 翻译器，确保不发起真实的网络 API 调用
                from unittest.mock import MagicMock
                mock_translator = MagicMock()
                mock_translator.node_name = "mock_translator"
                mock_translator.config = {}
                
                def mock_translate(content, source_lang, target_lang, **kwargs):
                    if "Second block content" in content:
                        raise RuntimeError("LLM API Timeout Error")
                    return f"Translated: {content}"
                
                mock_translator.translate = mock_translate
                mock_translator.generate_seo_metadata.return_value = ({}, True)
                mock_translator.translate_title.return_value = "Mocked Title"
                mock_translator.translate_metadata.side_effect = lambda val, *args, **kwargs: val
                
                engine.translator = mock_translator
                
                # 5. 执行同步，期待由于故障块导致整体翻译失败但无崩溃
                res = engine.sync_document(
                    doc_path, 
                    route_prefix="", 
                    route_source="Docs", 
                    is_dry_run=False,
                    force_sync=True
                )
                # 因为 ai_health_flag[0] 变为 False，但同步并没有直接 crash，
                # 并且因为 t_health 故障，物理 dispatch 应该被拦截，
                # 我们期待 target_path 的 HTML 没有被写入。
                target_html_path = os.path.join(self.imprint_dir, "dist/static", "docs", "en", "paragraph-cache-test.html")
                self.assertFalse(os.path.exists(target_html_path))
                
                # 6. 调用遥测 API 确认已缓存段落比例为 1/3 (33%)
                status_api = get_dispatch_status_facade(engine, doc_path)
                en_status = None
                for item in status_api["sync_matrix"]:
                    if item["locale"] == "English":
                        en_status = item
                        break
                
                self.assertIsNotNone(en_status)
                self.assertEqual(en_status["status"], "pending")
                self.assertEqual(en_status["progress"], 66)
                self.assertIn("已缓存 2/3 个段落", en_status["cache_info"])
                
                # 7. 解除 Mock 故障，使其能正常通过
                translate_calls_after = []
                def mock_translate_ok(content, source_lang, target_lang, **kwargs):
                    translate_calls_after.append(content)
                    return f"Translated: {content}"
                
                mock_translator.translate = mock_translate_ok
                
                # 8. 重新运行同步，期待断点续传（第 1 个 Block 缓存命中，不发起 AI 翻译，只翻译后面两个）
                res_second = engine.sync_document(
                    doc_path, 
                    route_prefix="", 
                    route_source="Docs", 
                    is_dry_run=False,
                    force_sync=True
                )
                
                # 验证第 1 个和第 3 个块命中缓存没有调用 translate，只有第 2 个块被调用了
                self.assertEqual(len(translate_calls_after), 1)
                self.assertNotIn("First block content here.", translate_calls_after)
                self.assertIn("Second block content here.", translate_calls_after)
                self.assertNotIn("Third block content here.", translate_calls_after)
                
                # 9. 验证最终物理 HTML 成功输出且翻译正确
                self.assertTrue(os.path.exists(target_html_path))
                with open(target_html_path, 'r', encoding='utf-8') as hf:
                    html_content = hf.read()
                    self.assertIn("Translated: First block content here.", html_content)
                    self.assertIn("Translated: Second block content here.", html_content)
                    self.assertIn("Translated: Third block content here.", html_content)
                
                # 10. 遥测状态应该变为 published 且 progress 达到 100
                status_api_final = get_dispatch_status_facade(engine, doc_path)
                en_status_final = None
                for item in status_api_final["sync_matrix"]:
                    if item["locale"] == "English":
                        en_status_final = item
                        break
                self.assertEqual(en_status_final["status"], "published")
                self.assertEqual(en_status_final["progress"], 100)
                
                # 11. 🚀 [V75.13] 清除缓存并强制重译测试
                translate_calls_after.clear()
                
                res_clear = engine.sync_document(
                    doc_path, 
                    route_prefix="", 
                    route_source="Docs", 
                    is_dry_run=False,
                    force_sync=True,
                    clear_cache=True
                )
                
                # 验证：即使所有段落都有有效缓存，指定 clear_cache=True 也能强制绕过并重新调用 AI 翻译
                self.assertEqual(len(translate_calls_after), 3)
                self.assertIn("First block content here.", translate_calls_after)
                self.assertIn("Second block content here.", translate_calls_after)
                self.assertIn("Third block content here.", translate_calls_after)
                
            finally:
                if os.path.exists(mock_vault):
                    shutil.rmtree(mock_vault)


if __name__ == "__main__":
    unittest.main()
