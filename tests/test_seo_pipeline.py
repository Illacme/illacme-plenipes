# -*- coding: utf-8 -*-
"""
Illacme-plenipes Tests - SEO Pipeline Optimization Tests
模块职责：验证高阶 SEO 策略数据管道在分发与渲染阶段的合并、传递与注入逻辑。
"""
import json
from unittest.mock import MagicMock
from core.adapters.egress.ssg.generic import GenericSSGAdapter
from core.bindery.bindery_dispatcher import BinderyDispatcher

def test_inject_seo_backward_compatibility():
    """验证 inject_seo 签名的向后兼容性（旧版参数传入）"""
    adapter = GenericSSGAdapter()
    fm = {}
    description = "Test description"
    keywords = ["test", "seo"]
    
    # 用旧签名传入描述和关键字
    res = adapter.inject_seo(fm, description, keywords)
    assert res['description'] == "Test description"
    assert res['keywords'] == ["test", "seo"]

def test_inject_seo_rich_data():
    """验证 Protocol / AI 策略的高阶/多维数据（OG, Twitter, Canonical, 结构化数据）的透传与增量合并"""
    adapter = GenericSSGAdapter()
    fm = {
        "og_title": "Existing OG Title", # Frontmatter 已存在，不覆盖
    }
    
    seo_data = {
        "description": "AI Generated Desc",
        "keywords": ["ai", "enhanced"],
        "og_title": "New OG Title",
        "og_description": "OG Desc",
        "og_type": "article",
        "og_locale": "zh_CN",
        "twitter_card": "summary_large_image",
        "twitter_title": "Twitter Title",
        "twitter_description": "Twitter Desc",
        "canonical_url": "https://example.com/page",
        "json_ld": {"@context": "https://schema.org", "@type": "WebPage", "name": "Test Page"},
        "faq_ld": {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": []},
        "breadcrumb_ld": {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": []}
    }
    
    res = adapter.inject_seo(fm, seo_data)
    
    # 验证 Frontmatter 优先原则（已有的不覆盖）
    assert res["og_title"] == "Existing OG Title"
    
    # 验证新字段成功合并
    assert res["description"] == "AI Generated Desc"
    assert res["keywords"] == ["ai", "enhanced"]
    assert res["og_description"] == "OG Desc"
    assert res["og_type"] == "article"
    assert res["og_locale"] == "zh_CN"
    assert res["twitter_card"] == "summary_large_image"
    assert res["twitter_title"] == "Twitter Title"
    assert res["twitter_description"] == "Twitter Desc"
    assert res["canonical_url"] == "https://example.com/page"
    
    # 验证结构化数据层序列化写入 Frontmatter 中的 structured_data 字段
    assert "structured_data" in res
    s_data = res["structured_data"]
    
    # 检查反序列化内容
    json_ld_parsed = json.loads(s_data["json_ld"])
    assert json_ld_parsed["name"] == "Test Page"
    
    faq_ld_parsed = json.loads(s_data["faq_ld"])
    assert faq_ld_parsed["@type"] == "FAQPage"
    
    breadcrumb_ld_parsed = json.loads(s_data["breadcrumb_ld"])
    assert breadcrumb_ld_parsed["@type"] == "BreadcrumbList"

def test_bindery_dispatcher_i18n_seo_cross_injection():
    """验证在物理落盘分发阶段，i18n_seo 矩阵针对目标语种的交叉注入合并逻辑"""
    # 1. 模拟依赖项
    paths = {"source_dir": "src", "site_dir": "dist", "vault": "."}
    meta = MagicMock()
    route_manager = MagicMock()
    # 模拟物理路径解析与逻辑 URL 解析
    route_manager.resolve_physical_path.return_value = "dist/en/test-slug.html"
    route_manager.resolve_logical_url.return_value = "/en/test-slug/"
    
    asset_pipeline = MagicMock()
    
    # 模拟 SSG 适配器
    mock_ssg_adapter = MagicMock()
    mock_ssg_adapter.get_output_schema.return_value = ["static"]
    mock_ssg_adapter.supports_frontmatter.return_value = True
    # render 应正常返回
    mock_ssg_adapter.render.return_value = ("rendered body", {"title": "Test"})
    mock_ssg_adapter.output_extensions = {"static": ".html"}
    
    ast_resolver = MagicMock()
    
    pub_cfg = MagicMock()
    pub_cfg.append_credit = False
    
    i18n_cfg = MagicMock()
    i18n_cfg.source.lang_code = "zh"
    i18n_cfg.targets = [MagicMock(lang_code="en")]
    i18n_cfg.injection_matrix = {}
    
    dispatcher = BinderyDispatcher(
        paths=paths,
        meta=meta,
        route_manager=route_manager,
        asset_pipeline=asset_pipeline,
        ssg_adapter=mock_ssg_adapter,
        ast_resolver=ast_resolver,
        pub_cfg=pub_cfg,
        fm_order=[],
        i18n_cfg=i18n_cfg
    )
    
    # 构造含 i18n_seo 翻译矩阵的 seo_data
    seo_data = {
        "description": "默认中文描述",
        "keywords": ["中文"],
        "i18n_seo": {
            "en": {
                "description": "English Description",
                "keywords": ["english", "seo"],
                "canonical_url": "https://example.com/en/page"
            }
        }
    }
    
    # 2. 执行分发（is_target=True, 目标语言为 "en"）
    dispatcher.dispatch(
        asset_index={},
        title="测试标题",
        slug="test-slug",
        masked_body="Body content",
        fm_dict={},
        rel_path="test.md",
        lang_code="en",
        route_prefix="",
        route_source="",
        mapped_sub_dir="",
        masks={},
        is_dry_run=True, # 使用 dry_run 避免物理写盘
        is_target=True,
        seo_data=seo_data
    )
    
    # 3. 验证 ssg_adapter.render() 接收到的 seo_data 被正确合并
    called_args, called_kwargs = mock_ssg_adapter.render.call_args
    passed_seo = called_kwargs.get("seo_data")
    
    assert passed_seo is not None
    assert passed_seo["description"] == "English Description"
    assert passed_seo["keywords"] == ["english", "seo"]
    assert passed_seo["canonical_url"] == "https://example.com/en/page"
    # i18n_seo 本身仍保留在字典中
    assert "i18n_seo" in passed_seo

def test_bindery_dispatcher_no_cross_injection_for_non_target():
    """验证当不是目标语种时，不进行 i18n_seo 的语种特定合并（仅透传默认 seo_data）"""
    paths = {"source_dir": "src", "site_dir": "dist", "vault": "."}
    meta = MagicMock()
    route_manager = MagicMock()
    route_manager.resolve_physical_path.return_value = "dist/zh/test-slug.html"
    route_manager.resolve_logical_url.return_value = "/zh/test-slug/"
    
    mock_ssg_adapter = MagicMock()
    mock_ssg_adapter.get_output_schema.return_value = ["static"]
    mock_ssg_adapter.supports_frontmatter.return_value = True
    mock_ssg_adapter.render.return_value = ("rendered body", {"title": "Test"})
    mock_ssg_adapter.output_extensions = {"static": ".html"}
    
    i18n_cfg = MagicMock()
    i18n_cfg.source.lang_code = "zh"
    i18n_cfg.targets = [MagicMock(lang_code="en")]
    i18n_cfg.injection_matrix = {}
    
    dispatcher = BinderyDispatcher(
        paths=paths,
        meta=meta,
        route_manager=route_manager,
        asset_pipeline=MagicMock(),
        ssg_adapter=mock_ssg_adapter,
        ast_resolver=MagicMock(),
        pub_cfg=MagicMock(append_credit=False),
        fm_order=[],
        i18n_cfg=i18n_cfg
    )
    
    seo_data = {
        "description": "默认中文描述",
        "keywords": ["中文"],
        "i18n_seo": {
            "en": {
                "description": "English Description"
            }
        }
    }
    
    # is_target=False
    dispatcher.dispatch(
        asset_index={},
        title="测试标题",
        slug="test-slug",
        masked_body="Body content",
        fm_dict={},
        rel_path="test.md",
        lang_code="zh",
        route_prefix="",
        route_source="",
        mapped_sub_dir="",
        masks={},
        is_dry_run=True,
        is_target=False,
        seo_data=seo_data
    )
    
    called_args, called_kwargs = mock_ssg_adapter.render.call_args
    passed_seo = called_kwargs.get("seo_data")
    
    # 应该仍然是默认的 "默认中文描述"，没被 "English Description" 覆盖
    assert passed_seo["description"] == "默认中文描述"
