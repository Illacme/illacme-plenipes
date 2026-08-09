# -*- coding: utf-8 -*-
"""
🧪 [Integration Test] 多语种定向社交广播与译文智能装载集成测试
"""
import os
import sys
import shutil
import unittest
import yaml
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.governance.imprint_manager import ImprintManager
from services.api.logic.dispatch_ops_shards.pipeline_ops import _async_redispatch_task


class TestMultilingualSyndicationDispatch(unittest.TestCase):
    def setUp(self):
        self.test_press = "test_multi_syndicate_press"
        self.test_root = os.path.abspath("tests/test_sandbox_multi_syndicate")
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

    def test_target_lang_loading_from_disk_and_syndication(self):
        """测试从目标语种磁盘候选文件装载译文并定向分发至 Dev.to"""
        with patch('core.config.config.IMPRINT_DIR', self.imprint_root), \
             patch('core.runtime.engine_preflight.IMPRINT_DIR', self.imprint_root), \
             patch('core.governance.imprint_manager.IMPRINT_DIR', self.imprint_root), \
             patch('core.config.assembler.IMPRINT_DIR', self.imprint_root):
            
            im = ImprintManager(root_dir=self.test_root)
            mock_vault = os.path.abspath("test_mock_vault_multi_syndicate")
            if os.path.exists(mock_vault):
                shutil.rmtree(mock_vault)
            os.makedirs(mock_vault, exist_ok=True)
            
            try:
                im.init_sovereign_imprint(self.test_press, manuscripts_path=mock_vault)
                
                # 1. 写入原稿文件 (母语 zh)
                doc_path = "welcome-to-illacme-plenipes.md"
                with open(os.path.join(mock_vault, doc_path), 'w', encoding='utf-8') as f:
                    f.write(
                        "---\n"
                        "title: 欢迎使用 Illacme Plenipes\n"
                        "slug: welcome-to-illacme-plenipes\n"
                        "---\n"
                        "这是母语中文正文段落。"
                    )
                
                # 2. 模拟 AZ 语种已生成在内容候选目录中
                content_az_dir = os.path.join(self.imprint_dir, "themes", "default", "src", "content", "az")
                os.makedirs(content_az_dir, exist_ok=True)
                with open(os.path.join(content_az_dir, "welcome-to-illacme-plenipes.md"), 'w', encoding='utf-8') as f:
                    f.write(
                        "---\n"
                        "title: Illacme Plenipes-ə xoş gəlmisiniz\n"
                        "slug: welcome-to-illacme-plenipes\n"
                        "---\n"
                        "Bu Azərbaycan dilində tərcümə olunmuş mətndir."
                    )
                
                # 3. 配置 YAML 启用 Dev.to
                config_path = os.path.join(self.imprint_dir, "configs", "config.imprint.yaml")
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = yaml.safe_load(f)
                
                cfg['press_name'] = self.test_press
                cfg['vault_root'] = mock_vault
                cfg['site_url'] = "https://example.com"
                cfg['syndication'] = {
                    'devto': {
                        'enabled': True,
                        'api_key': 'dummy-devto-key'
                    }
                }
                cfg['output_paths'] = {
                    'source_dir': os.path.join(self.imprint_dir, 'dist/source'),
                    'site_dir': os.path.join(self.imprint_dir, 'dist/static'),
                    'content_dir': os.path.join(self.imprint_dir, "themes", "default", "src", "content"),
                    'assets_dir': os.path.join(self.imprint_dir, 'dist/assets'),
                    'graph_json_dir': os.path.join(self.imprint_dir, 'dist/graph')
                }
                cfg['metadata_db'] = os.path.join(self.imprint_dir, 'core/press.db')
                cfg['i18n_settings'] = {
                    'enabled': True,
                    'source': {'lang_code': 'zh', 'prompt_lang': 'Chinese'},
                    'targets': [{'lang_code': 'az', 'prompt_lang': 'Azerbaijani'}]
                }
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(cfg, f)
                
                from core.runtime.engine_factory import EngineFactory
                engine = EngineFactory.create_engine(config_path, no_ai=True, imprint_id=self.test_press)
                engine.meta.register_document(doc_path, "欢迎使用 Illacme Plenipes", source_lang="zh", slug="welcome-to-illacme-plenipes")
                
                # 4. 执行定向 AZ 语种广播分发任务
                with patch('adapters.egress.syndication.devto.requests.post') as mock_post, \
                     patch('adapters.egress.syndication.devto.requests.get') as mock_get:
                    mock_resp = MagicMock()
                    mock_resp.status_code = 201
                    mock_resp.json.return_value = {"id": 12345, "url": "https://dev.to/article/az-12345"}
                    mock_post.return_value = mock_resp

                    mock_probe = MagicMock()
                    mock_probe.status_code = 200
                    mock_probe.text = "<html><body>Article content</body></html>"
                    mock_get.return_value = mock_probe
                    
                    _async_redispatch_task(
                        engine=engine,
                        task_path=os.path.join(mock_vault, doc_path),
                        prefix="",
                        src_rel=doc_path,
                        target_slot="az",
                        clear_cache=False,
                        doc_id=doc_path,
                        target_channel="devto",
                        skip_syndication=False
                    )
                    
                    import time
                    for _ in range(50):
                        if mock_post.called and len(engine.meta.list_syndication_records_for_doc(doc_path, "az")) > 0:
                            break
                        time.sleep(0.05)
                    
                    # 验证 Dev.to push 被调用，且 payload 包含了 AZ 译文和标题
                    self.assertTrue(mock_post.called)
                    call_kwargs = mock_post.call_args[1]
                    payload = call_kwargs.get("json", {}).get("article", {})
                    self.assertEqual(payload.get("title"), "Illacme Plenipes-ə xoş gəlmisiniz")
                    self.assertIn("Azərbaycan dilində", payload.get("body_markdown", ""))
                    
                    # 验证物权账本记录的 lang_code 是 az，且 remote_url 是对应地址
                    records = engine.meta.list_syndication_records_for_doc(doc_path, "az")
                    self.assertEqual(len(records), 1)
                    self.assertEqual(records[0]["lang_code"], "az")
                    self.assertEqual(records[0]["remote_article_id"], "12345")
            finally:
                if os.path.exists(mock_vault):
                    shutil.rmtree(mock_vault)

    def test_missing_translation_records_failed_status_in_ledger(self):
        """测试当译文缺失时，账本中正确更新 FAILED 状态且不会被母语状态掩盖"""
        with patch('core.config.config.IMPRINT_DIR', self.imprint_root), \
             patch('core.runtime.engine_preflight.IMPRINT_DIR', self.imprint_root), \
             patch('core.governance.imprint_manager.IMPRINT_DIR', self.imprint_root), \
             patch('core.config.assembler.IMPRINT_DIR', self.imprint_root):
            
            im = ImprintManager(root_dir=self.test_root)
            mock_vault = os.path.abspath("test_mock_vault_failed_syndicate")
            if os.path.exists(mock_vault):
                shutil.rmtree(mock_vault)
            os.makedirs(mock_vault, exist_ok=True)
            
            try:
                im.init_sovereign_imprint(self.test_press, manuscripts_path=mock_vault)
                
                doc_path = "untranslated-doc.md"
                with open(os.path.join(mock_vault, doc_path), 'w', encoding='utf-8') as f:
                    f.write(
                        "---\n"
                        "title: 未翻译文档\n"
                        "---\n"
                        "纯中文原文。"
                    )
                
                config_path = os.path.join(self.imprint_dir, "configs", "config.imprint.yaml")
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = yaml.safe_load(f)
                
                cfg['press_name'] = self.test_press
                cfg['vault_root'] = mock_vault
                cfg['syndication'] = {
                    'devto': {
                        'enabled': True,
                        'api_key': 'dummy-devto-key'
                    }
                }
                cfg['output_paths'] = {
                    'source_dir': os.path.join(self.imprint_dir, 'dist/source'),
                    'site_dir': os.path.join(self.imprint_dir, 'dist/static'),
                    'assets_dir': os.path.join(self.imprint_dir, 'dist/assets'),
                    'graph_json_dir': os.path.join(self.imprint_dir, 'dist/graph')
                }
                cfg['metadata_db'] = os.path.join(self.imprint_dir, 'core/press.db')
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(cfg, f)
                
                from core.runtime.engine_factory import EngineFactory
                engine = EngineFactory.create_engine(config_path, no_ai=True, imprint_id=self.test_press)
                engine.meta.register_document(doc_path, "未翻译文档", source_lang="zh")
                
                # 执行未就绪语种广播
                _async_redispatch_task(
                    engine=engine,
                    task_path=os.path.join(mock_vault, doc_path),
                    prefix="",
                    src_rel=doc_path,
                    target_slot="fr",
                    clear_cache=False,
                    doc_id=doc_path,
                    target_channel="devto",
                    skip_syndication=False
                )
                
                # 验证账本中 devto 状态为 FAILED，且包含友好的未就绪错误提示
                doc_info = engine.meta.get_doc_info(doc_path)
                publish_status = doc_info.get("publish_status", {})
                devto_status = publish_status.get("devto", {})
                self.assertEqual(devto_status.get("status"), "FAILED")
                self.assertIn("FR", devto_status.get("error", ""))
                self.assertIn("尚未生成或就绪", devto_status.get("error", ""))
            finally:
                if os.path.exists(mock_vault):
                    shutil.rmtree(mock_vault)


if __name__ == '__main__':
    unittest.main()
