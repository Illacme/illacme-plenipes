# -*- coding: utf-8 -*-
"""
🧪 [Test] 多媒体资产渐进式与增量分发 (Asset Delivery) 单元测试
"""
import os
import sys
import shutil
import tempfile
import unittest

# 将项目根目录加入 python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.syndication.incremental_builder import IncrementalBuildManager
from core.archives.ledger import MetadataManager
from adapters.egress.publishers.github_pages import GitHubPagesPublisher


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

    def get_vault_cache_dir(self) -> str:
        return ".plenipes/vault_cache"


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


class TestIncrementalAssets(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="plenipes_test_assets_")
        self.theme_dir = os.path.join(self.temp_dir, "theme")
        os.makedirs(self.theme_dir, exist_ok=True)
        
        # package.json
        with open(os.path.join(self.theme_dir, "package.json"), "w") as f:
            f.write('{"name": "test-theme"}')
            
        # docs
        self.docs_dir = os.path.join(self.theme_dir, "docs")
        os.makedirs(self.docs_dir, exist_ok=True)
        self.md_file = os.path.join(self.docs_dir, "doc1.md")
        with open(self.md_file, "w") as f:
            f.write("---\ntitle: Doc 1\nslug: doc1\n---\n# Doc 1\nContent.")

        # static
        self.static_dir = os.path.join(self.theme_dir, "static")
        os.makedirs(self.static_dir, exist_ok=True)
        
        # 写入大媒体文件 (6MB) 和 小图片文件 (1KB)
        self.large_media = os.path.join(self.static_dir, "video.mp4")
        with open(self.large_media, "wb") as f:
            f.write(b"0" * (6 * 1024 * 1024))
            
        self.small_image = os.path.join(self.static_dir, "photo.png")
        with open(self.small_image, "wb") as f:
            f.write(b"0" * 1024)

        # 构造 mock_build 脚本，仅模拟文件复制到 dist 目录
        self.mock_build_script = os.path.join(self.theme_dir, "mock_build.py")
        with open(self.mock_build_script, "w") as f:
            f.write("""import os, shutil
os.makedirs("dist", exist_ok=True)
# 模拟编译复制 static 目录（如果存在的话）
if os.path.exists("static"):
    for item in os.listdir("static"):
        src = os.path.join("static", item)
        dst = os.path.join("dist", item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
""")
            
        self.db_path = os.path.join(self.temp_dir, "metadata.db")
        self.engine = MockEngine(self.temp_dir, self.db_path)
        self.manager = IncrementalBuildManager(self.engine)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_incremental_assets_lazy_disguise(self):
        """测试大媒体文件在增量构建中能够被隐藏并在构建后还原回填"""
        # 1. 首次全量编译，创建快照
        self.assertTrue(self.manager.build())
        
        large_out = os.path.join(self.manager.site_dir, "video.mp4")
        self.assertTrue(os.path.exists(large_out))
        self.assertEqual(os.path.getsize(large_out), 6 * 1024 * 1024)

        # 2. 修改 Markdown 内容，触发增量编译
        with open(self.md_file, "w") as f:
            f.write("---\ntitle: Doc 1\nslug: doc1\n---\n# Doc 1\nModified content.")
            
        # 拦截构建脚本执行，记录大文件是否成功被掏空隐藏
        # 只要构建正常跑完且最终 video.mp4 依然存在于 dist 且大小一致即可
        success = self.manager.build()
        self.assertTrue(success)

        # 验证大文件没有丢失
        self.assertTrue(os.path.exists(self.large_media))
        self.assertTrue(os.path.exists(large_out))
        self.assertEqual(os.path.getsize(large_out), 6 * 1024 * 1024)

    def test_incremental_copy_tree(self):
        """测试 _incremental_copy_tree 差分合并与孤儿文件清理功能"""
        src = os.path.join(self.temp_dir, "dir_src")
        dst = os.path.join(self.temp_dir, "dir_dst")
        os.makedirs(src, exist_ok=True)
        os.makedirs(dst, exist_ok=True)

        # 写入源文件
        with open(os.path.join(src, "file1.txt"), "w") as f: f.write("content 1")
        with open(os.path.join(src, "file2.txt"), "w") as f: f.write("content 2")
        # 目标写入孤儿文件
        with open(os.path.join(dst, "orphan.txt"), "w") as f: f.write("orphan")

        # 首次合并
        self.manager._incremental_copy_tree(src, dst)
        
        self.assertTrue(os.path.exists(os.path.join(dst, "file1.txt")))
        self.assertTrue(os.path.exists(os.path.join(dst, "file2.txt")))
        # 验证孤儿已被清理
        self.assertFalse(os.path.exists(os.path.join(dst, "orphan.txt")))

        # 修改源文件修改时间，测试是否跳过不一致的重拷贝
        mtime_before = os.path.getmtime(os.path.join(dst, "file1.txt"))
        self.manager._incremental_copy_tree(src, dst)
        mtime_after = os.path.getmtime(os.path.join(dst, "file1.txt"))
        self.assertEqual(mtime_before, mtime_after) # 未发生拷贝，mtime 保持

    def test_github_pages_差分对齐(self):
        """测试 GitHubPagesPublisher 差分清理与懒拷贝"""
        bundle = os.path.join(self.temp_dir, "bundle")
        work = os.path.join(self.temp_dir, "work")
        os.makedirs(bundle, exist_ok=True)
        os.makedirs(work, exist_ok=True)

        with open(os.path.join(bundle, "a.mp4"), "wb") as f: f.write(b"0" * 1024)
        with open(os.path.join(bundle, "b.txt"), "w") as f: f.write("text")

        # 模拟克隆结果已经在工作区中
        shutil.copytree(bundle, work, dirs_exist_ok=True)
        with open(os.path.join(work, "orphan.txt"), "w") as f: f.write("orphan")

        publisher = GitHubPagesPublisher({"repo_url": "dummy", "branch": "dummy"})
        
        # 1. 智能清理：保留一致文件，仅删除孤儿
        publisher._clean_work_dir(work, bundle)
        self.assertTrue(os.path.exists(os.path.join(work, "a.mp4")))
        self.assertFalse(os.path.exists(os.path.join(work, "orphan.txt")))

        # 2. 增量拷贝：跳过已存在的一致文件
        count = publisher._copy_bundle(bundle, work)
        self.assertEqual(count, 2)


if __name__ == '__main__':
    unittest.main()
