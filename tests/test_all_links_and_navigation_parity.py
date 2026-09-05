# -*- coding: utf-8 -*-
"""
Illacme Plenipes - All Links & Navigation Parity Test
测试目标：验证所有模板类型的文档首页链接、文章内容链接、导航菜单链接、左边栏导航链接均严格按配置推导生成，0 断链 0 404。
"""

import os
from unittest.mock import MagicMock

from core.editorial.router import RouteManager
from core.services.link_resolver import LinkResolver
from core.adapters.egress.ssg.generic_shards.navigation_builder import build_docs_sidebar
from themes.sovereign.adapters.sovereign_helpers import build_sidebar


class MockDocMeta:
    def __init__(self):
        self.docs = {
            "Docs/quick-start.md": {
                "slug": "quick-start",
                "title": "⚡ 5 分钟上手指南",
                "target_slot": "docs",
                "route_prefix": "docs",
                "sub_dir": ""
            },
            "Docs/themes-and-binding-visual-customization.md": {
                "slug": "themes-and-binding-visual-customization",
                "title": "🎨 装帧主题与视觉定制",
                "target_slot": "docs",
                "route_prefix": "docs",
                "sub_dir": ""
            },
            "Docs/engineering/block-cache-hub.md": {
                "slug": "block-cache-hub",
                "title": "🧱 段落缓存中枢",
                "target_slot": "docs",
                "route_prefix": "docs",
                "sub_dir": "engineering"
            },
            "Blog/future-of-publishing.md": {
                "slug": "future-of-publishing",
                "title": "🚀 出版的未来",
                "target_slot": "blog",
                "route_prefix": "blog",
                "sub_dir": ""
            },
            "about.md": {
                "slug": "about",
                "title": "关于我们",
                "target_slot": "page",
                "route_prefix": "",
                "sub_dir": ""
            }
        }

    def get_documents_snapshot(self):
        return self.docs

    def get_doc_info(self, logic_id):
        clean = logic_id.replace('\\', '/')
        if clean in self.docs:
            return self.docs[clean]
        for k, v in self.docs.items():
            if v['slug'] == clean or os.path.splitext(os.path.basename(k))[0] == clean:
                return v
        return None

    def resolve_link(self, target):
        clean = target.replace('\\', '/')
        for k, v in self.docs.items():
            if v['slug'] == clean or os.path.splitext(os.path.basename(k))[0] == clean:
                return k
        return None


def test_router_path_modes():
    """测试三大路径形态在不同文档类型下的物理路径与逻辑 URL 一致性"""
    mock_meta = MockDocMeta()
    router = RouteManager(mock_meta, None, default_lang="zh", active_theme="sovereign")

    # 1. Nested 模式
    cfg_nested = MagicMock()
    cfg_nested.translation.slug_dir_mode = 'nested'
    router.config = cfg_nested

    p_nested = router.resolve_physical_path("", "zh", "docs", "", "quick-start", ".html", "docs")
    assert p_nested.replace('\\', '/') == "docs/quick-start.html"

    p_nested_sub = router.resolve_physical_path("", "zh", "docs", "engineering", "block-cache-hub", ".html", "docs")
    assert p_nested_sub.replace('\\', '/') == "docs/engineering/block-cache-hub.html"

    # 2. Flat 模式
    cfg_flat = MagicMock()
    cfg_flat.translation.slug_dir_mode = 'flat'
    router.config = cfg_flat

    p_flat = router.resolve_physical_path("", "zh", "docs", "", "quick-start", ".html", "docs")
    assert p_flat.replace('\\', '/') == "quick-start.html"

    p_flat_sub = router.resolve_physical_path("", "zh", "docs", "engineering", "block-cache-hub", ".html", "docs")
    assert p_flat_sub.replace('\\', '/') == "block-cache-hub.html"

    # 3. Prefix 模式
    cfg_prefix = MagicMock()
    cfg_prefix.translation.slug_dir_mode = 'prefix'
    router.config = cfg_prefix

    p_prefix = router.resolve_physical_path("", "zh", "docs", "", "quick-start", ".html", "docs")
    assert p_prefix.replace('\\', '/') == "docs-quick-start.html"

    p_prefix_sub = router.resolve_physical_path("", "zh", "docs", "engineering", "block-cache-hub", ".html", "docs")
    assert p_prefix_sub.replace('\\', '/') == "engineering-block-cache-hub.html"


def test_link_resolver_content_healing():
    """测试正文内 Markdown 链接与 Wikilink 的自动愈合"""
    mock_meta = MockDocMeta()
    router = RouteManager(mock_meta, None, default_lang="zh", active_theme="sovereign")
    resolver = LinkResolver(mock_meta, router, "sovereign")

    # 1. 嵌套模式下的 Markdown 链接解析
    cfg_nested = MagicMock()
    cfg_nested.translation.slug_dir_mode = 'nested'
    router.config = cfg_nested

    raw_text = "请参考 [快速入门](quick-start.md) 与 [[themes-and-binding-visual-customization]]。"
    healed = resolver.heal_content(raw_text, "zh", "docs", "")
    assert "/docs/quick-start" in healed or "/docs/quick-start.html" in healed

    # 2. 扁平模式下的链接解析
    cfg_flat = MagicMock()
    cfg_flat.translation.slug_dir_mode = 'flat'
    router.config = cfg_flat

    healed_flat = resolver.heal_content(raw_text, "zh", "docs", "")
    assert "/quick-start" in healed_flat or "quick-start.html" in healed_flat


def test_sidebar_generation_and_active_matching():
    """测试左侧栏目录树生成的链接准确性"""
    mock_meta = MockDocMeta()
    engine = MagicMock()
    engine.meta = mock_meta
    router = RouteManager(mock_meta, None, default_lang="zh", active_theme="sovereign")
    engine.route_manager = router
    adapter = MagicMock()
    adapter.engine = engine

    # 1. 测试 Sovereign 侧边栏
    sidebar_html = build_sidebar(adapter, "zh", "docs", "docs/quick-start.html", "./", {"slug": "quick-start"})
    assert "quick-start.html" in sidebar_html
    assert "themes-and-binding-visual-customization.html" in sidebar_html

    # 2. 测试 Universal 侧边栏
    docs_sidebar_html = build_docs_sidebar("quick-start", "./", "", engine, "zh")
    assert "quick-start.html" in docs_sidebar_html


def test_sovereign_standalone_page_navbar_link_parity(tmp_path):
    """测试 Sovereign 独立单页在顶部导航栏中生成正确的相对链接，杜绝多余的关于目录"""
    from core.adapters.egress.ssg.base_shards.ssg_nav_synthesizer import SSGNavSynthesizer
    from themes.sovereign.adapters.sovereign import SovereignSSGAdapter

    mock_engine = MagicMock()
    mock_engine.vault_root = str(tmp_path)
    mock_engine.config.translation.slug_dir_mode = 'nested'
    mock_engine.config.translation.clean_urls = False
    mock_engine.config.site.theme = "sovereign"
    mock_engine.config.nav = [
        {"text": "✨ 关于我们", "url": "/about", "slot": "pages"},
        {"text": "📚 文档指南", "url": "/docs/", "slot": "docs"},
    ]
    mock_engine.config.i18n.languages = []
    mock_engine.config.i18n.default_lang = "zh"
    meta = MockDocMeta()
    mock_engine.meta = meta
    router = RouteManager(meta, mock_engine.config, default_lang="zh", active_theme="sovereign")
    mock_engine.route_manager = router
    mock_engine.paths = {"site_dir": str(tmp_path / "dist")}

    adapter = SovereignSSGAdapter(engine=mock_engine)
    adapter.site_output_dir = str(tmp_path / "dist")

    # 1. 验证 SSGNavSynthesizer 输出 /about.html
    nav_data = SSGNavSynthesizer.generate_navigation_items(adapter)
    about_link = next(item for item in nav_data.get("nav_links", []) if item.get("slot") == "pages")
    assert about_link["url"] == "/about.html"

    # 2. 验证 adapter.render 在渲染 about.html 时的导航输出
    body = "# 关于我们\n欢迎查阅。"
    fm = {"title": "关于我们", "slug": "about", "target_slot": "pages", "route_prefix": ""}
    rendered_html, _ = adapter.render(body, fm, target_lang="zh", sub_path="about.html")

    assert '<a href="./about.html" class="active">✨ 关于我们</a>' in rendered_html
    assert './about/index.html' not in rendered_html


def test_dev_server_recursion_collapse_and_single_page_redirect(tmp_path):
    """测试本地预览服务器对套娃路径折叠及单页虚拟目录的 302 重定向保护"""
    from core.utils.dev_server import SovereignHandler
    import io

    # 创建一个虚拟网站输出目录
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    (dist_dir / "about.html").write_text("<html>About Us</html>", encoding="utf-8")
    (dist_dir / "index.html").write_text("<html>Home</html>", encoding="utf-8")

    class DummyRequest:
        def makefile(self, *args, **kwargs):
            return io.BytesIO()

    # 1. 测试套娃递归路径折叠: /about/about/about/index.html -> 302 /about/index.html
    handler1 = SovereignHandler(DummyRequest(), ('127.0.0.1', 8888), None)
    handler1.directory = str(dist_dir)
    handler1.path = "/about/about/about/index.html"
    
    responses = []
    headers = {}
    handler1.send_response = lambda code, message=None: responses.append(code)
    handler1.send_header = lambda k, v: headers.update({k: v})
    handler1.end_headers = lambda: None

    handler1.do_GET()
    assert responses == [302]
    assert headers.get('Location') == "/about/index.html"

    # 2. 测试单页虚拟目录重定向: /about/index.html -> 302 /about.html
    responses.clear()
    headers.clear()
    handler2 = SovereignHandler(DummyRequest(), ('127.0.0.1', 8888), None)
    handler2.directory = str(dist_dir)
    handler2.path = "/about/index.html"
    handler2.send_response = lambda code, message=None: responses.append(code)
    handler2.send_header = lambda k, v: headers.update({k: v})
    handler2.end_headers = lambda: None

    handler2.do_GET()
    assert responses == [302]
    assert headers.get('Location') == "/about.html"
