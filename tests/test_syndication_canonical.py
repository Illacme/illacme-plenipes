#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V76.1] 主权 SEO 防御与 Canonical 绑定测试套件
验证各个分发插件对 canonical_url 契约的支持，以及 ContentSyndicator 分流时的拼装行为。
符合 SOP-01 行数红线限制。
"""
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath("."))

from core.syndication.hub import ContentSyndicator

class TestSyndicationCanonical:
    """Canonical 绑定与分发单元测试"""

    def test_content_syndicator_dispatches_canonical_url(self):
        """验证 ContentSyndicator 在分发时是否根据 site_url 拼接 canonical_url 并传入插件"""
        mock_plugin = MagicMock()
        mock_plugin.is_enabled.return_value = True
        mock_plugin.__class__.__name__ = "MockSyndicator"

        # 实例化 ContentSyndicator，模拟 site_url 和配置
        syndicator = ContentSyndicator(
            syndication_cfg={"mock_target": {"enabled": True}},
            site_url="https://my-blog.com/",
            meta=MagicMock()
        )
        syndicator.plugins = [mock_plugin]

        # 触发分发
        syndicator._dispatch_to_plugin(
            plugin=mock_plugin,
            title="Hello Plenipes",
            slug="hello-plenipes-post",
            content="Markdown body",
            metadata={"tags": []},
            rel_path="vault/hello.md",
            lang_code="zh",
            is_dry_run=False
        )

        # 校验 mock_plugin.format_payload 接收到的 canonical_url
        mock_plugin.format_payload.assert_called_once_with(
            "Hello Plenipes",
            "hello-plenipes-post",
            "Markdown body",
            {"tags": []},
            canonical_url="https://my-blog.com/posts/hello-pre-commit-slug" if False else "https://my-blog.com/posts/hello-plenipes-post"
        )

    def test_medium_canonical_url_handling(self):
        """验证 MediumSyndicator 的 format_payload 优先使用传入的 canonical_url"""
        from adapters.egress.syndication.medium import MediumSyndicator
        cfg = MagicMock()
        cfg.enabled = True
        cfg.publish_status = "draft"
        
        # 1. 传入具体的 canonical_url
        syndicator = MediumSyndicator(config=cfg, site_url="https://site.com")
        payload = syndicator.format_payload(
            title="Test",
            slug="test-slug",
            content="Content",
            metadata={},
            canonical_url="https://canonical.com/injected"
        )
        assert payload["canonicalUrl"] == "https://canonical.com/injected"

        # 2. 不传时使用 fallback 推导
        payload_fallback = syndicator.format_payload(
            title="Test",
            slug="test-slug",
            content="Content",
            metadata={}
        )
        assert payload_fallback["canonicalUrl"] == "https://site.com/test-slug"

    def test_devto_canonical_url_handling(self):
        """验证 DevToSyndicator 的 format_payload 优先使用传入的 canonical_url"""
        from adapters.egress.syndication.devto import DevToSyndicator
        cfg = MagicMock()
        cfg.enabled = True
        
        # 1. 传入具体的 canonical_url
        syndicator = DevToSyndicator(config=cfg, site_url="https://site.com")
        payload = syndicator.format_payload(
            title="Test",
            slug="test-slug",
            content="Content",
            metadata={},
            canonical_url="https://canonical.com/injected"
        )
        assert payload["article"]["canonical_url"] == "https://canonical.com/injected"

        # 2. Fallback 推导
        payload_fallback = syndicator.format_payload(
            title="Test",
            slug="test-slug",
            content="Content",
            metadata={}
        )
        assert payload_fallback["article"]["canonical_url"] == "https://site.com/test-slug"

    def test_hashnode_canonical_url_handling(self):
        """验证 HashnodeSyndicator 的 format_payload 处理"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        cfg = MagicMock()
        cfg.enabled = True
        
        syndicator = HashnodeSyndicator(config=cfg, site_url="https://site.com")
        payload = syndicator.format_payload(
            title="Test",
            slug="test-slug",
            content="Content",
            metadata={},
            canonical_url="https://canonical.com/injected"
        )
        variables = payload["variables"]["input"]
        assert variables["originalArticleURL"] == "https://canonical.com/injected"

    def test_ghost_canonical_url_handling(self):
        """验证 GhostSyndicator 的 format_payload 处理"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        cfg = MagicMock()
        cfg.enabled = True
        
        syndicator = GhostSyndicator(config=cfg, site_url="https://site.com")
        payload = syndicator.format_payload(
            title="Test",
            slug="test-slug",
            content="Content",
            metadata={},
            canonical_url="https://canonical.com/injected"
        )
        post = payload["posts"][0]
        assert post["canonical_url"] == "https://canonical.com/injected"

    def test_wordpress_canonical_url_handling(self):
        """验证 WordPressSyndicator 的 format_payload 处理"""
        from adapters.egress.syndication.wordpress import WordPressSyndicator
        cfg = MagicMock()
        cfg.enabled = True
        
        syndicator = WordPressSyndicator(config=cfg)
        payload = syndicator.format_payload(
            title="Test",
            slug="test-slug",
            content="Content",
            metadata={},
            canonical_url="https://canonical.com/injected"
        )
        assert payload["meta"]["_yoast_wpseo_canonical"] == "https://canonical.com/injected"
