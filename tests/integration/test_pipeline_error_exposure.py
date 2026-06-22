# -*- coding: utf-8 -*-
"""
🧪 [Test] 发布管线拦截与审计失败在 Dashboard 反馈的集成测试
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


class TestPipelineErrorExposure(unittest.TestCase):
    def setUp(self):
        self.test_press = "test_error_exposure_press"
        self.test_root = os.path.abspath("tests/test_sandbox_error")
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

    def test_pipeline_abort_telemetry_exposure(self):
        """🚀 测试管线审计拦截后，错误成功持久化并在 Telemetry API 曝光"""
        # 1. 物理主权对齐 Mock
        with patch('core.config.config.IMPRINT_DIR', self.imprint_root), \
             patch('core.runtime.engine_preflight.IMPRINT_DIR', self.imprint_root), \
             patch('core.governance.imprint_manager.IMPRINT_DIR', self.imprint_root), \
             patch('core.config.assembler.IMPRINT_DIR', self.imprint_root):
            
            # 2. 初始化测试沙箱
            im = ImprintManager(root_dir=self.test_root)
            mock_vault = os.path.abspath("test_mock_vault_error")
            if os.path.exists(mock_vault):
                shutil.rmtree(mock_vault)
            os.makedirs(mock_vault, exist_ok=True)
            
            try:
                # 3. 初始化主权空间
                success = im.init_sovereign_imprint(self.test_press, manuscripts_path=mock_vault)
                self.assertTrue(success)
                
                # 4. 创建一个会导致 VerificationStep 残留占位符审计失败的文档
                doc_path = "Docs/Sovereignty_Test.md"
                os.makedirs(os.path.join(mock_vault, "Docs"), exist_ok=True)
                with open(os.path.join(mock_vault, doc_path), 'w', encoding='utf-8') as f:
                    # 包含 [[STB_MASK_123]] 强制触发审计失败
                    f.write("---\ntitle: Sovereignty Test\n---\nWelcome [[STB_MASK_123]] to sovereign press.")
                
                # 5. 读取并注入测试用 YAML 配置
                config_path = os.path.join(self.imprint_dir, "configs", "config.imprint.yaml")
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = yaml.safe_load(f)
                
                cfg['press_name'] = self.test_press
                cfg['vault_root'] = mock_vault
                cfg['translation'] = {'enable_ai': False}
                cfg['output_paths'] = {
                    'source_dir': os.path.join(self.imprint_dir, 'dist/source'),
                    'site_dir': os.path.join(self.imprint_dir, 'dist/static'),
                    'assets_dir': os.path.join(self.imprint_dir, 'dist/assets'),
                    'graph_json_dir': os.path.join(self.imprint_dir, 'dist/graph')
                }
                cfg['metadata_db'] = os.path.join(self.imprint_dir, 'core/press.db')
                cfg['i18n_settings'] = {
                    'enabled': False,
                    'source': {'lang_code': 'zh', 'prompt_lang': 'Chinese'},
                    'targets': []
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
                cfg['ingress_settings'] = {
                    'source_type': 'local',
                    'ingress_rules': [{'source': 'Docs', 'target': 'docs'}]
                }
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(cfg, f)

                # 6. 点火引擎
                engine = EngineFactory.create_engine(config_path, no_ai=True, imprint_id=self.test_press)
                self.assertIsNotNone(engine)
                
                # 7. 运行同步该错误文档，它应当触发 VerificationStep 拦截失败，并被 FingerprintSyncStrategy 识别
                res = engine.sync_document(
                    doc_path,
                    route_prefix="",
                    route_source="Docs",
                    is_dry_run=False
                )
                self.assertEqual(res, "SKIP") # 拦截时返回 SKIP
                
                # 8. 验证账本中的发布状态，应当记入 PIPELINE -> ABORTED，且包含错误细节
                doc_info = engine.meta.get_doc_info(doc_path)
                self.assertIsNotNone(doc_info)
                
                publish_status = doc_info.get("publish_status", {})
                self.assertIn("PIPELINE", publish_status)
                self.assertEqual(publish_status["PIPELINE"]["status"], "ABORTED")
                self.assertIn("侦测到残留占位符", publish_status["PIPELINE"]["error"])
                
                # 9. 调用 API 门面，验证 API 输出是否对齐
                status_api = get_dispatch_status_facade(engine, doc_path)
                self.assertEqual(status_api["telemetry"]["last_audit"], "FAIL")
                self.assertEqual(status_api["telemetry"]["health"], "Aborted")
                self.assertIn("侦测到残留占位符", status_api["telemetry"]["error_detail"])
                
            finally:
                if os.path.exists(mock_vault):
                    shutil.rmtree(mock_vault)


if __name__ == "__main__":
    unittest.main()
