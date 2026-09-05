#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Universal Navigation Synthesis & Multi-SSG Theme Tests
测试矩阵：
1. RouteItem 导航属性向后兼容性与自愈验证
2. BaseSSGAdapter 统一导航合成引擎验证 (默认项、自定义频道、外部直链)
3. 8 大 SSG 主题全景映射与 theme.options 桥接验证
"""

import json
from unittest.mock import MagicMock
from core.config.config_models import RouteItem
from core.adapters.egress.ssg.base import BaseSSGAdapter


def test_route_item_backward_compatibility():
    """验证 RouteItem 原有字段与扩展字段的 100% 兼容与默认值"""
    # 1. 传统旧版配置数据
    legacy_data = {
        "source": "Docs",
        "prefix": "docs",
        "target_slot": "docs"
    }
    item = RouteItem(**legacy_data)
    assert item.source == "Docs"
    assert item.prefix == "docs"
    assert item.target_slot == "docs"
    assert item.show_in_nav is True
    assert item.nav_label is None
    assert item.nav_icon is None
    assert item.nav_position == "left"
    assert item.external_url is None

    # 2. 现代扩展导航数据
    modern_data = {
        "source": "Blog",
        "prefix": "blog",
        "target_slot": "blog",
        "nav_label": "官方资讯",
        "nav_icon": "📰",
        "show_in_nav": True,
        "nav_position": "left",
        "nav_order": 2,
        "external_url": None
    }
    item2 = RouteItem(**modern_data)
    assert item2.nav_label == "官方资讯"
    assert item2.nav_icon == "📰"
    assert item2.nav_order == 2


class ConcreteTestAdapter(BaseSSGAdapter):
    def render(self, content, fm, target_lang, sub_path, is_default=False):
        return content, fm


def test_universal_navigation_synthesis():
    """验证全景导航合成算法"""
    # 构造 Mock 引擎配置
    mock_engine = MagicMock()
    mock_config = MagicMock()
    mock_engine.config = mock_config
    
    # 注入多个频道与外部链接
    mock_config.route_matrix = [
        RouteItem(source="Docs", prefix="docs", target_slot="docs", nav_label="知识库", nav_icon="📚", nav_order=1),
        RouteItem(source="Blog", prefix="blog", target_slot="blog", nav_label="博客", nav_icon="📰", nav_order=2),
        RouteItem(source="Hidden", prefix="hidden", target_slot="pages", show_in_nav=False), # 隐藏项
        RouteItem(source="", prefix="", target_slot="external", nav_label="GitHub", nav_icon="🐙", external_url="https://github.com/Illacme/illacme-plenipes", nav_order=3)
    ]
    mock_config.i18n_settings = None
    mock_config.site_url = "https://example.com"

    adapter = ConcreteTestAdapter(engine=mock_engine)
    nav_data = adapter.generate_navigation_items()

    navbar_items = nav_data["navbar_items"]
    nav_links = nav_data["nav_links"]

    # 验证导航项数量（Hidden 项不展示在前端导航中，加上 GitHub 项共 3 项）
    assert len(navbar_items) == 3
    
    # 验证第一项 Docs
    assert navbar_items[0]["label"] == "📚 知识库"
    assert navbar_items[0]["to"] == "/docs/"
    assert navbar_items[0]["type"] == "docSidebar"

    # 验证第二项 Blog
    assert navbar_items[1]["label"] == "📰 博客"
    assert navbar_items[1]["to"] == "/blog/"
    assert navbar_items[1]["type"] == "link"

    # 验证第三项 外部链接
    assert navbar_items[2]["label"] == "🐙 GitHub"
    assert navbar_items[2]["href"] == "https://github.com/Illacme/illacme-plenipes"
    assert navbar_items[2]["external"] is True


def test_theme_options_compilation(tmp_path):
    """验证 compile_theme_options 能够正确生成带 navbar_items 与 nav_links 的 options 文件"""
    mock_engine = MagicMock()
    mock_config = MagicMock()
    mock_engine.config = mock_config
    mock_engine.paths = {"themes": str(tmp_path)}
    
    mock_config.route_matrix = [
        RouteItem(source="Docs", prefix="docs", target_slot="docs", nav_label="文档中心", nav_icon="📚")
    ]
    mock_config.i18n_settings = None
    mock_config.site_url = "https://example.com"

    mock_theme_settings = MagicMock()
    mock_theme_settings.name = "sovereign"
    mock_theme_settings.options = {"site_name": "Test Site", "enable_custom_style": False}

    adapter = ConcreteTestAdapter(engine=mock_engine, theme_settings=mock_theme_settings)
    adapter.compile_theme_options()

    # 验证生成文件
    theme_dir = tmp_path / "sovereign"
    json_file = theme_dir / "theme.options.json"
    js_file = theme_dir / "theme.options.js"

    assert json_file.exists()
    assert js_file.exists()

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "navbar_items" in data
    assert len(data["navbar_items"]) >= 1
    assert data["navbar_items"][0]["raw_label"] == "文档中心"
    assert "nav_links" in data


def test_sovereign_nav_html_rendering():
    """验证 Sovereign 原生 HTML 顶栏动态导航注入"""
    from themes.sovereign.adapters.sovereign_helpers import apply_template
    
    mock_adapter = MagicMock()
    mock_adapter.template_path = "themes/sovereign/templates/layout.html"
    mock_adapter.get_custom_options.return_value = {
        "site_name": "Sovereign Portal",
        "nav_links": [
            {"text": "📚 知识文档", "url": "/docs/", "external": False},
            {"text": "📰 官方博客", "url": "/blog/", "external": False},
            {"text": "🐙 GitHub", "url": "https://github.com/Illacme/illacme-plenipes", "external": True}
        ]
    }
    mock_adapter.engine = MagicMock()
    mock_adapter.engine.config.site_url = "https://example.com"
    mock_adapter.engine.config.governance.publishing_mode = "global"

    fm = {"title": "Test Page", "route_prefix": "docs", "slug": "test"}
    html_res = apply_template(mock_adapter, "<p>Content</p>", fm, "zh", "docs/test.html", is_default=True)

    assert "📚 知识文档" in html_res
    assert "📰 官方博客" in html_res
    assert "🐙 GitHub" in html_res
    assert 'target="_blank"' in html_res


def test_all_ssg_adapters_feature_slots():
    """验证全部 8 大 SSG 适配器的槽位与寻址体系完整性"""
    from adapters.egress.ssg.docusaurus import DocusaurusAdapter
    from adapters.egress.ssg.starlight import StarlightAdapter
    from adapters.egress.ssg.vitepress import VitepressAdapter
    from adapters.egress.ssg.nextra import NextraAdapter
    from adapters.egress.ssg.hexo import HexoAdapter
    from adapters.egress.ssg.hugo import HugoAdapter
    from core.adapters.egress.ssg.generic import GenericSSGAdapter
    from themes.sovereign.adapters.sovereign import SovereignSSGAdapter

    adapters = [
        DocusaurusAdapter,
        StarlightAdapter,
        VitepressAdapter,
        NextraAdapter,
        HexoAdapter,
        HugoAdapter,
        GenericSSGAdapter,
        SovereignSSGAdapter
    ]

    for adapter_cls in adapters:
        instance = adapter_cls()
        slots = instance.get_feature_slots()
        assert isinstance(slots, dict)
        assert "docs" in slots or "default" in slots or len(slots) > 0
        
        mappings = adapter_cls.get_default_path_mappings()
        assert isinstance(mappings, dict)
        assert "source_dir" in mappings
        assert "site_dir" in mappings


def test_reordering_and_custom_icons_synthesis():
    """验证排序 (nav_order) 与常见/自定义图标的合成结果"""
    mock_engine = MagicMock()
    mock_config = MagicMock()
    mock_engine.config = mock_config
    
    # 模拟用户在前端通过 ▲ / ▼ 调整了顺序 (Blog 排在第一位，Docs 排在第二位)
    mock_config.route_matrix = [
        RouteItem(source="Blog", prefix="blog", target_slot="blog", nav_label="最新资讯", nav_icon="🔥", nav_order=0),
        RouteItem(source="Docs", prefix="docs", target_slot="docs", nav_label="核心指南", nav_icon="💎", nav_order=1),
        RouteItem(source="", prefix="", target_slot="external", nav_label="官方论坛", nav_icon="💬", external_url="https://forum.example.com", nav_order=2)
    ]
    mock_config.i18n_settings = None
    mock_config.site_url = "https://example.com"

    adapter = ConcreteTestAdapter(engine=mock_engine)
    nav_data = adapter.generate_navigation_items()

    navbar_items = nav_data["navbar_items"]
    nav_links = nav_data["nav_links"]

    # 1. 验证根据 nav_order 正确排序：第一项为 Blog，带有 🔥 图标
    assert navbar_items[0]["label"] == "🔥 最新资讯"
    assert navbar_items[0]["to"] == "/blog/"

    # 2. 第二项为 Docs，带有 💎 图标
    assert navbar_items[1]["label"] == "💎 核心指南"
    assert navbar_items[1]["to"] == "/docs/"

    # 3. 第三项为 官方论坛，带有 💬 图标
    assert navbar_items[2]["label"] == "💬 官方论坛"
    assert navbar_items[2]["href"] == "https://forum.example.com"

    # 4. 验证 nav_links 同时保持严格一致的顺序与属性
    assert nav_links[0]["text"] == "🔥 最新资讯"
    assert nav_links[0]["url"] == "/blog/"
    assert nav_links[1]["text"] == "💎 核心指南"
    assert nav_links[2]["text"] == "💬 官方论坛"
    assert nav_links[2]["external"] is True


def test_all_8_ssg_themes_compilation_matrix(tmp_path):
    """验证全部 8 大 SSG 引擎适配器在真实 Theme 编译流程中的 100% 兼容性"""
    from adapters.egress.ssg.docusaurus import DocusaurusAdapter
    from adapters.egress.ssg.starlight import StarlightAdapter
    from adapters.egress.ssg.vitepress import VitepressAdapter
    from adapters.egress.ssg.nextra import NextraAdapter
    from adapters.egress.ssg.hexo import HexoAdapter
    from adapters.egress.ssg.hugo import HugoAdapter
    from core.adapters.egress.ssg.generic import GenericSSGAdapter
    from themes.sovereign.adapters.sovereign import SovereignSSGAdapter

    adapter_classes = [
        ("sovereign", SovereignSSGAdapter),
        ("docusaurus", DocusaurusAdapter),
        ("starlight", StarlightAdapter),
        ("vitepress", VitepressAdapter),
        ("nextra", NextraAdapter),
        ("universal", GenericSSGAdapter),
        ("hexo", HexoAdapter),
        ("hugo", HugoAdapter)
    ]

    mock_engine = MagicMock()
    mock_config = MagicMock()
    mock_engine.config = mock_config
    mock_engine.paths = {"themes": str(tmp_path)}

    mock_config.route_matrix = [
        RouteItem(source="Docs", prefix="docs", target_slot="docs", nav_label="知识文档", nav_icon="📚", nav_order=0),
        RouteItem(source="Blog", prefix="blog", target_slot="blog", nav_label="团队动态", nav_icon="📰", nav_order=1),
        RouteItem(source="", prefix="", target_slot="external", nav_label="GitHub", nav_icon="🐙", external_url="https://github.com/Illacme/illacme-plenipes", nav_order=2)
    ]
    mock_config.i18n_settings = None
    mock_config.site_url = "https://illacme.org"

    for theme_name, adapter_cls in adapter_classes:
        mock_theme_settings = MagicMock()
        mock_theme_settings.name = theme_name
        mock_theme_settings.options = {"site_name": f"Test {theme_name.title()}", "enable_custom_style": True}

        adapter = adapter_cls(engine=mock_engine, theme_settings=mock_theme_settings)
        adapter.compile_theme_options()

        # 验证每个 SSG 主题目录均生成了标准的 options 桥接文件
        theme_dir = tmp_path / theme_name
        json_file = theme_dir / "theme.options.json"
        js_file = theme_dir / "theme.options.js"

        assert json_file.exists(), f"Theme {theme_name} failed to generate theme.options.json"
        assert js_file.exists(), f"Theme {theme_name} failed to generate theme.options.js"

        with open(json_file, "r", encoding="utf-8") as f:
            opts = json.load(f)

        assert "navbar_items" in opts
        assert "nav_links" in opts
        assert len(opts["navbar_items"]) == 3
        assert opts["navbar_items"][0]["label"] == "📚 知识文档"
        assert opts["navbar_items"][1]["label"] == "📰 团队动态"
        assert opts["navbar_items"][2]["label"] == "🐙 GitHub"


def test_multilingual_navigation_synthesis():
    """验证多语言导航矩阵合成 (nav_label_i18n 自定义与内置字典自动翻译)"""
    mock_engine = MagicMock()
    mock_config = MagicMock()
    mock_engine.config = mock_config
    
    mock_i18n = MagicMock()
    mock_i18n.source.lang_code = "zh"
    target_en = MagicMock()
    target_en.lang_code = "en"
    target_en.enabled = True
    target_ja = MagicMock()
    target_ja.lang_code = "ja"
    target_ja.enabled = True
    target_fr = MagicMock()
    target_fr.lang_code = "fr"
    target_fr.enabled = True
    mock_i18n.targets = [target_en, target_ja, target_fr]
    mock_config.i18n_settings = mock_i18n
    mock_config.site_url = "https://example.com"

    # 包含：1. 自定义 i18n 映射项；2. 缺省走内置字典自愈项；3. 外部链接
    mock_config.route_matrix = [
        RouteItem(
            source="Tutorials", prefix="tutorials", target_slot="docs",
            nav_label="实战指南", nav_icon="🚀",
            nav_label_i18n={"en": "Hands-on Guide", "ja": "実践ガイド", "fr": "Guide Pratique"},
            nav_order=0
        ),
        RouteItem(
            source="Blog", prefix="blog", target_slot="blog",
            nav_label="官方博客", nav_icon="📰",
            nav_label_i18n=None, # 走内置字典自愈 (Blog -> ブログ / Blog)
            nav_order=1
        ),
        RouteItem(
            source="", prefix="", target_slot="external",
            nav_label="GitHub", nav_icon="🐙",
            external_url="https://github.com/Illacme/illacme-plenipes",
            nav_order=2
        )
    ]

    adapter = ConcreteTestAdapter(engine=mock_engine)
    nav_data = adapter.generate_navigation_items()

    nav_links_i18n = nav_data["nav_links_i18n"]
    navbar_items_i18n = nav_data["navbar_items_i18n"]

    assert "zh" in nav_links_i18n
    assert "en" in nav_links_i18n
    assert "ja" in nav_links_i18n
    assert "fr" in nav_links_i18n

    # 1. 验证英文导航 (en)
    en_links = nav_links_i18n["en"]
    assert en_links[0]["text"] == "🚀 Hands-on Guide" # 自定义翻译
    assert en_links[1]["text"] == "📰 Blog"           # 内置字典自愈

    # 2. 验证日文导航 (ja)
    ja_links = nav_links_i18n["ja"]
    assert ja_links[0]["text"] == "🚀 実践ガイド"     # 自定义翻译
    assert ja_links[1]["text"] == "📰 ブログ"          # 内置字典自愈

    # 3. 验证法文导航 (fr)
    fr_links = nav_links_i18n["fr"]
    assert fr_links[0]["text"] == "🚀 Guide Pratique" # 自定义翻译
    assert fr_links[1]["text"] == "📰 Blog"           # 内置字典自愈

    # 4. 验证 Sovereign 模板在法文环境下渲染出法文导航
    from themes.sovereign.adapters.sovereign_helpers import apply_template
    mock_adapter = MagicMock()
    mock_adapter.template_path = "themes/sovereign/templates/layout.html"
    mock_adapter.get_custom_options.return_value = {
        "site_name": "Sovereign Multi-lang",
        "nav_links": nav_data["nav_links"],
        "nav_links_i18n": nav_links_i18n
    }
    mock_adapter.engine = mock_engine
    mock_config.governance.publishing_mode = "global"

    fm = {"title": "Guide de Démarrage", "route_prefix": "tutorials", "slug": "start"}
    fr_html = apply_template(mock_adapter, "<p>Contenu</p>", fm, "fr", "tutorials/start.html", is_default=False)

    assert "🚀 Guide Pratique" in fr_html
    assert "📰 Blog" in fr_html
    assert 'href="../fr/tutorials/index.html"' in fr_html or 'href="/fr/tutorials/index.html"' in fr_html or 'tutorials/index.html' in fr_html


def test_translate_nav_labels_api():
    """验证 /api/governance/translate-nav-labels API 端点与标准字典/AI 回填"""
    from fastapi.testclient import TestClient
    from services.api.server import app
    
    client = TestClient(app)
    response = client.post(
        "/api/governance/translate-nav-labels",
        json={
            "label": "文档中心",
            "target_languages": ["en", "ja", "fr", "de", "es", "ru", "ko"],
            "slot": "docs",
            "source_language": "zh"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    translations = data["translations"]
    assert translations["en"] == "Documentation"
    assert translations["ja"] == "ドキュメント"
    assert translations["fr"] == "Documentation"
    assert translations["de"] == "Dokumentation"
    assert translations["es"] == "Documentación"
    assert translations["ru"] == "Документация"
    assert translations["ko"] == "문서 센터"


def test_nextra_and_vitepress_standalone_page_and_i18n_parity(tmp_path):
    """验证 Nextra 与 VitePress 独立单页 (无末尾斜杠) 与多语言前缀自愈及 Options 编译"""
    mock_engine = MagicMock()
    mock_config = MagicMock()
    mock_engine.config = mock_config
    mock_engine.paths = {"themes": str(tmp_path / "themes")}

    mock_i18n = MagicMock()
    mock_i18n.source.lang_code = "zh"
    mock_i18n.source.name = "简体中文"
    target_en = MagicMock()
    target_en.lang_code = "en"
    target_en.name = "English"
    target_en.enabled = True
    target_ja = MagicMock()
    target_ja.lang_code = "ja"
    target_ja.name = "日本語"
    target_ja.enabled = True
    mock_i18n.targets = [target_en, target_ja]
    mock_config.i18n_settings = mock_i18n
    mock_config.site_url = "https://example.com"

    mock_config.route_matrix = [
        RouteItem(
            source="Tutorials", prefix="docs", target_slot="docs",
            nav_label="文档中心", nav_icon="📚",
            nav_order=0
        ),
        RouteItem(
            source="About", prefix="about", target_slot="pages",
            nav_label="关于我们", nav_icon="💡",
            nav_order=1
        ),
        RouteItem(
            source="Single", prefix="privacy", target_slot="pages",
            nav_label="隐私协议",
            nav_order=2
        )
    ]

    from adapters.egress.ssg.nextra import NextraAdapter
    from adapters.egress.ssg.vitepress import VitepressAdapter
    from core.adapters.egress.ssg.base_shards.ssg_theme_compiler import SSGThemeCompiler

    # 1. 验证 NextraAdapter
    nextra_adapter = NextraAdapter(engine=mock_engine)
    nextra_adapter.theme_settings = MagicMock()
    nextra_adapter.theme_settings.name = "nextra"
    nextra_adapter.theme_settings.options = {}
    nextra_nav = nextra_adapter.generate_navigation_items()

    # 1.1 主语言单页无末尾斜杠，频道保留末尾斜杠
    assert nextra_nav["nav_links"][0]["url"] == "/docs/"
    assert nextra_nav["nav_links"][1]["url"] == "/about"
    assert nextra_nav["nav_links"][2]["url"] == "/privacy"

    # 1.2 多语言导航感知语言前缀
    assert nextra_nav["nav_links_i18n"]["en"][0]["url"] == "/en/docs/"
    assert nextra_nav["nav_links_i18n"]["en"][1]["url"] == "/en/about"
    assert nextra_nav["nav_links_i18n"]["en"][2]["url"] == "/en/privacy"

    assert nextra_nav["nav_links_i18n"]["ja"][0]["url"] == "/ja/docs/"
    assert nextra_nav["nav_links_i18n"]["ja"][1]["url"] == "/ja/about"
    assert nextra_nav["nav_links_i18n"]["ja"][2]["url"] == "/ja/privacy"

    # 1.3 Nextra theme.options 编译与落盘验证
    ok = SSGThemeCompiler.compile_theme_options(nextra_adapter)
    assert ok is True
    nextra_json_path = tmp_path / "themes" / "nextra" / "theme.options.json"
    assert nextra_json_path.exists()
    with open(nextra_json_path, 'r', encoding='utf-8') as f:
        nextra_opts = json.load(f)
    assert "i18n" in nextra_opts
    assert nextra_opts["defaultLocale"] == "zh"
    locales = [item["locale"] for item in nextra_opts["i18n"]]
    assert "zh" in locales
    assert "en" in locales
    assert "ja" in locales

    # 2. 验证 VitepressAdapter
    vite_adapter = VitepressAdapter(engine=mock_engine)
    vite_adapter.theme_settings = MagicMock()
    vite_adapter.theme_settings.name = "vitepress"
    vite_adapter.theme_settings.options = {}
    vite_nav = vite_adapter.generate_navigation_items()

    # 2.1 主语言单页无末尾斜杠
    assert vite_nav["nav_links"][0]["url"] == "/docs/"
    assert vite_nav["nav_links"][1]["url"] == "/about"
    assert vite_nav["nav_links"][2]["url"] == "/privacy"

    # 2.2 多语言导航
    assert vite_nav["nav_links_i18n"]["en"][1]["url"] == "/en/about"
    assert vite_nav["nav_links_i18n"]["ja"][1]["url"] == "/ja/about"

    # 2.3 Vitepress theme.options locales 编译与落盘验证
    ok_vp = SSGThemeCompiler.compile_theme_options(vite_adapter)
    assert ok_vp is True
    vp_json_path = tmp_path / "themes" / "vitepress" / "theme.options.json"
    assert vp_json_path.exists()
    with open(vp_json_path, 'r', encoding='utf-8') as f:
        vite_opts = json.load(f)
    assert "locales" in vite_opts
    assert "root" in vite_opts["locales"]
    assert "en" in vite_opts["locales"]
    assert "ja" in vite_opts["locales"]
    assert vite_opts["locales"]["en"]["link"] == "/en/"
    assert vite_opts["locales"]["ja"]["link"] == "/ja/"




