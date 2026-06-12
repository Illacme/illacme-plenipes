# -*- coding: utf-8 -*-
"""
🧪 [Test] 增量静态装帧 (Incremental Build Cache) 单元测试
"""
import os
import sys
import shutil
import tempfile
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.syndication.incremental_builder import IncrementalBuildManager
from core.archives.ledger import MetadataManager

class MockI18nLanguage:
    def __init__(self, lang_code, name):
        self.lang_code = lang_code
        self.name = name

class MockI18nSettings:
    def __init__(self):
        self.enabled = False
        self.source = MockI18nLanguage("zh", "简体中文")
        self.targets = []

class MockSSGAdapter:
    def __init__(self):
        class ActiveRenderer:
            def get_default_path_mappings(self):
                return {'site_dir': 'dist'}
            def get_feature_slots(self):
                return {'docs': {'single': 'docs', 'multi': 'i18n/{lang}/docs'}}
            def get_build_command(self):
                return "python3 mock_build.py"
            def get_language_code(self, code):
                return ""
        self.active_renderer = ActiveRenderer()

class MockRouteManager:
    def __init__(self):
        self.lang_mapping = {}
    def get_mapped_sub_dir(self, t_sub, is_dry_run, allow_ai):
        return ""

class MockResilience:
    def __init__(self):
        self.db_timeout = 30.0

class MockSystem:
    def __init__(self):
        self.resilience = MockResilience()

class MockConfig:
    def __init__(self):
        self.system = MockSystem()
        self.i18n_settings = None

class MockEngine:
    def __init__(self, temp_dir, db_path):
        self.config = MockConfig()
        self.active_theme = "docusaurus"
        self.paths = {
            'source_dir': os.path.join(temp_dir, 'theme'),
            'vault': os.path.join(temp_dir, 'vault'),
            'target_base': os.path.join(temp_dir, 'theme')
        }
        self.meta = MetadataManager(db_path, engine=self)
        self.ssg_adapter = MockSSGAdapter()
        self.i18n = MockI18nSettings()
        self.route_manager = MockRouteManager()

    def _resolve_path(self, path):
        return os.path.join(self.paths['source_dir'], path)

class TestIncrementalBuild(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="plenipes_test_build_")
        self.theme_dir = os.path.join(self.temp_dir, "theme")
        os.makedirs(self.theme_dir, exist_ok=True)
        
        with open(os.path.join(self.theme_dir, "package.json"), "w") as f:
            f.write('{"name": "test-theme"}')
            
        self.docs_dir = os.path.join(self.theme_dir, "docs")
        os.makedirs(self.docs_dir, exist_ok=True)
        
        self.md_file1 = os.path.join(self.docs_dir, "tut1.md")
        with open(self.md_file1, "w") as f:
            f.write("---\ntitle: Tutorial 1\nslug: tut1\n---\n# Tutorial 1\nThis is content 1.")
            
        self.md_file2 = os.path.join(self.docs_dir, "tut2.md")
        with open(self.md_file2, "w") as f:
            f.write("---\ntitle: Tutorial 2\nslug: tut2\n---\n# Tutorial 2\nThis is content 2.")

        mock_build_script = """
import os, sys
os.makedirs("dist", exist_ok=True)
for file in os.listdir("docs"):
    if file.endswith(".md"):
        name = file[:-3]
        os.makedirs(f"dist/docs/{name}", exist_ok=True)
        with open(f"docs/{file}", "r") as f:
            content = f.read()
        with open(f"dist/docs/{name}/index.html", "w") as out:
            out.write(f"<html><body>Rendered: {content}</body></html>")
"""
        with open(os.path.join(self.theme_dir, "mock_build.py"), "w") as f:
            f.write(mock_build_script)
            
        db_path = os.path.join(self.temp_dir, "meta.db")
        self.engine = MockEngine(self.temp_dir, db_path)
        
        self.engine.meta.register_document("docs/tut1.md", "Tutorial 1", slug="tut1", route_prefix="docs")
        self.engine.meta.register_document("docs/tut2.md", "Tutorial 2", slug="tut2", route_prefix="docs")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_incremental_build_flow(self):
        manager = IncrementalBuildManager(self.engine)
        
        success = manager.build()
        self.assertTrue(success)
        
        html1_path = os.path.join(manager.site_dir, "docs/tut1/index.html")
        html2_path = os.path.join(manager.site_dir, "docs/tut2/index.html")
        self.assertTrue(os.path.exists(html1_path))
        self.assertTrue(os.path.exists(html2_path))
        
        with open(html1_path, "r") as f:
            self.assertIn("This is content 1.", f.read())
            
        success = manager.build()
        self.assertTrue(success)
        
        with open(self.md_file1, "w") as f:
            f.write("---\ntitle: Tutorial 1\nslug: tut1\n---\n# Tutorial 1\nModified content 1.")
            
        success = manager.build()
        self.assertTrue(success)
        
        with open(html1_path, "r") as f:
            self.assertIn("Modified content 1.", f.read())
            
        with open(html2_path, "r") as f:
            content2 = f.read()
            self.assertIn("This is content 2.", content2)
            self.assertNotIn("Incremental Build Cache Placeholder", content2)
            
        with open(self.md_file2, "r") as f:
            self.assertIn("This is content 2.", f.read())

if __name__ == "__main__":
    unittest.main()
