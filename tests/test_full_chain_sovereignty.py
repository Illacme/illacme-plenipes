#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Phase 4 Full Chain Sovereignty Drill (Indentation & Mock Fix)
职责：验证全链路主权闭环，修复 Mock 属性与缩进故障。
🛡️ [V35.0]：终极验收脚本。
"""

import os
import shutil
import unittest
import yaml
from unittest.mock import MagicMock, patch
from core.governance.territory_manager import TerritoryManager
from core.runtime.engine_factory import EngineFactory

class TestFullChainSovereignty(unittest.TestCase):
    
    def setUp(self):
        self.test_press = "test_galaxy_press"
        self.territory_root = os.path.abspath("territories")
        self.workspace_dir = os.path.join(self.territory_root, self.test_press)
        if os.path.exists(self.territory_root):
            shutil.rmtree(self.territory_root)
        os.makedirs(self.territory_root, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.territory_root):
            shutil.rmtree(self.territory_root)

    @patch('core.bindery.deployment_manager.PluginLoader.load_plugins')
    def test_end_to_end_publishing_cycle(self, mock_load):
        """🚀 终极演习：验证全链路主权闭环"""
        from plugins.publishers.base import BasePublisher
        class MockPub(BasePublisher):
            PLUGIN_ID = "mock_pub"
            def push(self, bundle_path, metadata):
                return {"status": "success"}
        
        mock_load.return_value = [MockPub]
        from core.adapters.egress.publishers.base import PublisherRegistry
        PublisherRegistry.register("mock_pub")(MockPub)

        with patch.object(MockPub, 'push', return_value={"status": "success"}) as mock_push:
            # 2. 初始化主权空间
            wm = TerritoryManager()
            with patch('core.governance.license_guard.LicenseGuard.is_pro_feature_allowed', return_value=True):
                mock_vault = os.path.abspath("test_mock_vault")
                if os.path.exists(mock_vault): shutil.rmtree(mock_vault)
                os.makedirs(mock_vault, exist_ok=True)
                
                success = wm.init_sovereign_territory(self.test_press, manuscripts_path=mock_vault)
                self.assertTrue(success)
                
                # 3. 投递原稿并配置映射
                os.makedirs(os.path.join(mock_vault, "blog/tech"), exist_ok=True)
                with open(os.path.join(mock_vault, "blog/tech/first-post.md"), 'w') as f:
                    f.write("---\ntitle: Hello Galaxy\n---\nWelcome to the sovereign press.")
                
                config_path = os.path.join(self.workspace_dir, "configs", "system.yaml")
                with open(config_path, 'r') as f:
                    cfg = yaml.safe_load(f)
                
                cfg['press_name'] = self.test_press
                cfg['vault_root'] = mock_vault
                cfg['translation'] = {'enable_ai': False}
                cfg['publish_control'] = {'direct_upload': {'mock_pub': {'enabled': True}}}
                cfg['ingress_settings'] = {'ingress_rules': [{'source': 'blog/tech', 'target': 'posts/technology'}]}
                cfg['output_paths'] = {
                    'source_dir': os.path.join(self.workspace_dir, 'dist/source'),
                    'static_dir': os.path.join(self.workspace_dir, 'dist/static'),
                    'markdown_dir': os.path.join(self.workspace_dir, 'dist/source'),
                    'assets_dir': os.path.join(self.workspace_dir, 'dist/assets'),
                    'graph_json_dir': os.path.join(self.workspace_dir, 'dist/graph')
                }
                cfg['metadata_db'] = os.path.join(self.workspace_dir, 'metadata/press.db')
                cfg['i18n_settings'] = {'enable_multilingual': False, 'source': {'lang_code': 'zh', 'prompt_lang': 'Chinese'}, 'targets': []}
                cfg['system'] = {
                    'data_root': self.workspace_dir, 'allowed_extensions': ['.md'], 'data_paths': {},
                    'log_level': 'INFO', 'max_workers': 1, 'auto_save_interval': 60
                }
                cfg['theme_options'] = {'default': {}}
                cfg['active_theme'] = 'default'
                cfg['route_matrix'] = []
                cfg['framework_adapters'] = {}
                cfg['image_settings'] = {'base_url': 'http://localhost/'}
                cfg['seo_settings'] = {}
                cfg['syndication'] = {'enabled': False}
                cfg['ingress_settings']['source_type'] = 'local'
                cfg['ingress_settings']['active_dialects'] = []
                cfg['frontmatter_defaults'] = {}
                cfg['frontmatter_order'] = []
                
                with open(config_path, 'w') as f:
                    yaml.dump(cfg, f)

                # 4. 点火引擎执行同步
                engine = EngineFactory.create_engine(config_path, no_ai=True, territory_id=self.test_press)
                self.assertIsNotNone(engine)
                
                # 5. 模拟执行分发
                engine.dispatcher.dispatch(
                    asset_index=engine.asset_index, title="Hello Galaxy", slug="first-post",
                    masked_body="Welcome to the sovereign press.", fm_dict={}, rel_path="blog/tech/first-post.md",
                    lang_code="zh", route_prefix="", route_source="docs", mapped_sub_dir="posts/technology",
                    masks={}, is_dry_run=False, is_target=True
                )
                
                # 手动触发同步完成信号，激活全球分发渠道
                engine.bus.emit("SYNC_COMPLETED", engine=engine)
    
                # 6. 终极验证
                mock_push.assert_called()
                print(f"\n✅ [终极演习成功] 出版社 '{self.test_press}' 全链路主权闭环验证通过！")
                if os.path.exists(mock_vault): shutil.rmtree(mock_vault)

if __name__ == "__main__":
    unittest.main()
