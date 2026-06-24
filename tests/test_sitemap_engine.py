#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_sitemap_engine.py
🛡️ [V88.0] Sitemap 导出引擎测试
验证 Hreflang 矩阵生成与 x-default 默认源语言注入。
"""

import os
import tempfile
import xml.etree.ElementTree as ET
import pytest
from unittest.mock import MagicMock

from core.logic.sitemap_engine import SitemapGenerator


class MockLanguage:
    """Mock 语言代码"""
    def __init__(self, code):
        self.lang_code = code


class MockRouteManager:
    """Mock 路由管理器"""
    def resolve_logical_url(self, lang, route_prefix, sub_dir, slug):
        """生成模拟的逻辑 URL"""
        return f"/{lang}/{route_prefix}/{sub_dir}/{slug}".replace("//", "/")


class MockEngine:
    """Mock 核心引擎，用于提供配置与生命周期支持"""
    def __init__(self, site_url, target_base_dir):
        self.config = MagicMock()
        self.config.site_url = site_url
        self.config.get_health_report_path.return_value = "sentinel_health.json"
        self.config.get_history_dir.return_value = "history"

        self.i18n = MagicMock()
        self.i18n.source = MockLanguage("zh-Hans")

        self.route_manager = MockRouteManager()

        self.paths = {
            "target_base": target_base_dir
        }

        self.meta = MagicMock()


class TestSitemapEngine:
    """Sitemap 引擎测试类"""

    def test_sitemap_generator_fallback(self):
        """测试 site_url 为空或 None 时的安全降级回退机制"""
        engine = MockEngine(None, "/tmp")
        generator = SitemapGenerator(engine)
        assert generator.site_url == "http://localhost"

        engine2 = MockEngine("https://my-site.com/", "/tmp")
        generator2 = SitemapGenerator(engine2)
        assert generator2.site_url == "https://my-site.com"

    def test_generate_sitemap_xml(self):
        """测试全量 Sitemap XML 的生成、写入与命名空间验证"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            engine = MockEngine("https://example.com", tmp_dir)
            generator = SitemapGenerator(engine)

            # Mock 两个文档的元数据快照
            all_docs = {
                "post1.md": {
                    "route_prefix": "blog",
                    "sub_dir": "tech",
                    "slug": "hello-world",
                    "persistent_date": "2026-06-24T00:00:00Z",
                    "translations": {
                        "en": {},
                        "ja": {}
                    }
                },
                "post2.md": {
                    "route_prefix": "news",
                    "sub_dir": "",
                    "slug": "announcement",
                    "persistent_date": None,
                    "translations": {}
                }
            }

            generator.generate(all_docs_snapshot=all_docs)

            sitemap_file = os.path.join(tmp_dir, "sitemap.xml")
            assert os.path.exists(sitemap_file)

            # 解析生成的 XML 结构进行验证
            tree = ET.parse(sitemap_file)
            root = tree.getroot()

            # ElementTree 解析含命名空间的 XML 时标签名带有前缀
            NS_SITEMAP = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
            NS_XHTML = "{http://www.w3.org/1999/xhtml}"

            assert root.tag == f"{NS_SITEMAP}urlset"

            urls = root.findall(f"{NS_SITEMAP}url")
            # post1.md 包含 zh-Hans + en + ja = 3 个 URL
            # post2.md 仅包含 zh-Hans = 1 个 URL
            # 总共应有 4 个 url 节点
            assert len(urls) == 4

            # 抽取所有 loc
            locs = [loc.text for loc in root.findall(f".//{NS_SITEMAP}loc")]
            assert "https://example.com/zh-Hans/blog/tech/hello-world" in locs
            assert "https://example.com/en/blog/tech/hello-world" in locs
            assert "https://example.com/ja/blog/tech/hello-world" in locs
            assert "https://example.com/zh-Hans/news/announcement" in locs

            # 验证 Hreflang 和 x-default 链路
            url_post1 = urls[0]
            links = url_post1.findall(f"{NS_XHTML}link")
            # 3 个语言版本 (zh-Hans, en, ja) 对应的 Hreflang 应该各有对应的 alternate
            # 同时对于源语言 (zh-Hans) 还必须多注入一个 x-default，共 3 + 1 = 4 个链接 (因为 alternate 对每一个 available_langs 都是 3 次 * 2 次)
            # 让我们仔细检查 sitemap_engine.py 的逻辑：
            # 对每个 url_node (即单个 url)，它都会遍历 available_langs (共有 3 个：zh-Hans, en, ja)
            # 在遍历 available_langs 时：
            #  1. 注入 hreflang=h_lang (3个)
            #  2. 若 h_lang == source_lang，注入 hreflang=x-default (1个)
            # 所以每个 url_node 中应该恰好有 4 个 alternate link 标签
            assert len(links) == 4

            hreflangs = [link.get("hreflang") for link in links]
            assert "zh-Hans" in hreflangs
            assert "en" in hreflangs
            assert "ja" in hreflangs
            assert "x-default" in hreflangs
