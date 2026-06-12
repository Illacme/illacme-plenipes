# -*- coding: utf-8 -*-
"""
🧪 [Test] Slug Uniqueness & Conflict Detection Unit Tests
"""
import os
import sys
import tempfile
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.archives.ledger import MetadataManager
from services.api.logic.content_ops_shards.vault_ops import (
    update_document_metadata_logic, save_document_logic
)

class MockSystemConfig:
    def __init__(self):
        self.api_token = None
        self.resilience = type('MockResilience', (object,), {'db_timeout': 30.0})()

class MockConfig:
    def __init__(self):
        self.system = MockSystemConfig()

class MockEngine:
    def __init__(self, db_path, vault_root):
        self.vault_root = vault_root
        self.config = MockConfig()
        self.paths = {"cache": tempfile.mkdtemp()}
        self.meta = MetadataManager(db_path, engine=self)

    def _resolve_path(self, path):
        return os.path.abspath(os.path.join(self.vault_root, path))

class TestSlugUniqueness(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_root = os.path.join(self.temp_dir.name, "vault")
        os.makedirs(self.vault_root, exist_ok=True)
        self.db_path = os.path.join(self.temp_dir.name, "test_ledger.db")
        
        self.engine = MockEngine(self.db_path, self.vault_root)
        
        # Register two initial documents
        self.doc1_path = "doc1.md"
        self.doc2_path = "doc2.md"
        
        # Write files physically
        with open(os.path.join(self.vault_root, self.doc1_path), 'w', encoding='utf-8') as f:
            f.write("---\ntitle: Doc One\nslug: slug-one\n---\n# Content One")
        with open(os.path.join(self.vault_root, self.doc2_path), 'w', encoding='utf-8') as f:
            f.write("---\ntitle: Doc Two\nslug: slug-two\n---\n# Content Two")
            
        self.engine.meta.register_document(self.doc1_path, "Doc One", slug="slug-one")
        self.engine.meta.register_document(self.doc2_path, "Doc Two", slug="slug-two")

    def tearDown(self):
        # Close SQLite connections
        if hasattr(self.engine.meta, "sqlite") and hasattr(self.engine.meta.sqlite, "_local"):
            if hasattr(self.engine.meta.sqlite._local, "conn"):
                self.engine.meta.sqlite._local.conn.close()
                del self.engine.meta.sqlite._local.conn
        self.temp_dir.cleanup()

    def test_update_metadata_slug_conflict(self):
        """测试使用 update_document_metadata_logic 时，若修改 slug 为已有值，能正确触发拦截"""
        # Attempt to change doc2's slug to "slug-one" (owned by doc1)
        res = update_document_metadata_logic(self.engine, self.doc2_path, {"slug": "slug-one"})
        
        self.assertIsInstance(res, dict)
        self.assertFalse(res.get("success"))
        self.assertEqual(res.get("error_code"), "SLUG_CONFLICT")
        self.assertIn("已被文档 'doc1.md' 占用", res.get("error", ""))
        
        # Verify database was NOT updated
        doc2_info = self.engine.meta.sqlite.get_document(self.doc2_path)
        self.assertEqual(doc2_info.get("slug"), "slug-two")

    def test_update_metadata_slug_no_conflict(self):
        """测试使用 update_document_metadata_logic 时，修改为不冲突的 slug 可成功"""
        res = update_document_metadata_logic(self.engine, self.doc2_path, {"slug": "slug-three"})
        self.assertTrue(res.get("success"))
        
        doc2_info = self.engine.meta.sqlite.get_document(self.doc2_path)
        self.assertEqual(doc2_info.get("slug"), "slug-three")

    def test_save_document_slug_conflict(self):
        """测试使用 save_document_logic 保存文档时，若修改 slug 为已有值，能正确触发拦截"""
        req = {
            "content": "# New Content for Doc Two",
            "frontmatter": {
                "title": "Doc Two",
                "slug": "slug-one"
            },
            "slug": "slug-one"
        }
        res = save_document_logic(self.engine, self.doc2_path, req)
        
        self.assertIsInstance(res, dict)
        self.assertFalse(res.get("success"))
        self.assertEqual(res.get("error_code"), "SLUG_CONFLICT")
        
        # Verify physical file content was NOT updated
        with open(os.path.join(self.vault_root, self.doc2_path), 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("slug: slug-two", content)
            self.assertNotIn("New Content for Doc Two", content)

    def test_save_document_slug_no_conflict(self):
        """测试使用 save_document_logic 保存文档时，修改为不冲突 of the slug 可成功"""
        req = {
            "content": "# New Content for Doc Two",
            "frontmatter": {
                "title": "Doc Two",
                "slug": "slug-three"
            },
            "slug": "slug-three"
        }
        res = save_document_logic(self.engine, self.doc2_path, req)
        
        self.assertIsInstance(res, dict)
        self.assertNotIn("error_code", res)
        
        # Verify database and physical file updated
        doc2_info = self.engine.meta.sqlite.get_document(self.doc2_path)
        self.assertEqual(doc2_info.get("slug"), "slug-three")
        
        with open(os.path.join(self.vault_root, self.doc2_path), 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("slug: slug-three", content)
            self.assertIn("New Content for Doc Two", content)

    def test_clean_slug_preserves_slashes(self):
        """测试 AILogicHub.clean_slug 是否正确保留正斜杠 / 并按规范清洗"""
        from core.logic.ai.ai_logic_hub import AILogicHub
        
        # 正常混合情况：有空格、大写、下划线、斜杠和连续连字符
        res = AILogicHub.clean_slug("/Tech/Intro_Page-With--Many---Dirs//")
        self.assertEqual(res, "tech/intro-page-with-many-dirs")
        
        # 边界情况：只有斜杠与连字符
        self.assertEqual(AILogicHub.clean_slug("///---///"), "")

    def test_slug_dir_modes(self):
        """测试三种不同的 slug_dir_mode 拼接效果"""
        from core.editorial.steps.seo import AISlugAndSEOStep
        import os

        # 1. 模拟 route_manager 和 config
        class MockRouteManager:
            def get_mapped_sub_dir(self, sub, allow_ai=True):
                # 直接返回 mapped 子目录
                return sub

        class MockTranslationSettings:
            def __init__(self):
                self.slug_mode = "ai"
                self.slug_dir_mode = "flat"
                self.max_slug_length = 100
                self.prompts = type('MockPrompts', (object,), {
                    'slug_system': 'Generate slug',
                    'slug_user': '{title}'
                })()

        class MockConfig:
            def __init__(self):
                self.translation = MockTranslationSettings()
                self.system = MockSystemConfig()

        # 修改本测试用例的 MockEngine，提供需要的接口
        db_path = self.db_path
        vault_root = self.vault_root

        engine = MockEngine(db_path, vault_root)
        engine.config = MockConfig()
        engine.route_manager = MockRouteManager()
        engine.paths = {'vault': vault_root}
        engine.translator = None  # AI 留空降级

        # 2. 构造 PipelineContext
        class MockEngineRef:
            def __init__(self, e):
                self.paths = e.paths
                self.config = e.config
                self.route_manager = e.route_manager
                self.translator = e.translator

        class MockContext:
            def __init__(self):
                self.doc_info = {}
                self.rel_path = "tech/news/intro.md"
                # src_path 为物理绝对路径
                self.src_path = os.path.join(vault_root, "docs", "tech", "news", "intro.md")
                self.route_source = "docs"
                self.title = "Intro Page"
                self.is_silent_edit = False
                self.is_dry_run = False
                self.ai_health_flag = [True]
                self.raw_body = "Some body"
                self.engine = MockEngineRef(engine)
                self.slug = None
                self.seo_data = {}

        # A. 测试 flat 模式（默认）
        ctx = MockContext()
        step = AISlugAndSEOStep()
        step.process(ctx)
        self.assertEqual(ctx.slug, "intro-page")

        # B. 测试 prefix 模式
        ctx = MockContext()
        engine.config.translation.slug_dir_mode = "prefix"
        step.process(ctx)
        self.assertEqual(ctx.slug, "tech-news-intro-page")

        # C. 测试 nested 模式
        ctx = MockContext()
        engine.config.translation.slug_dir_mode = "nested"
        step.process(ctx)
        self.assertEqual(ctx.slug, "tech/news/intro-page")

if __name__ == '__main__':
    unittest.main()
