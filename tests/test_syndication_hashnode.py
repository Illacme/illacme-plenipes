#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V76.0] Hashnode GraphQL 分发插件单元测试
🛡️ [V88.0 Split] 从 test_syndication_plugins.py 物理克隆搬迁。
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath("."))


class TestHashnodeSyndicator:
    """Hashnode GraphQL 分发插件单元测试"""

    def _make_config(self, **kwargs):
        cfg = MagicMock()
        cfg.enabled = kwargs.get("enabled", True)
        cfg.token = kwargs.get("token", "test_hashnode_token")
        cfg.publication_id = kwargs.get("publication_id", "pub-id-12345")
        cfg.hide_from_feed = kwargs.get("hide_from_feed", False)
        return cfg

    def test_import_and_instantiate(self):
        """验证 HashnodeSyndicator 可正常导入和实例化"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        syndicator = HashnodeSyndicator(config=self._make_config())
        assert syndicator.PLUGIN_ID == "hashnode"
        assert syndicator.token == "test_hashnode_token"
        assert syndicator.publication_id == "pub-id-12345"

    def test_push_skips_when_no_token(self):
        """缺少 token 时 push应跳过"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        syndicator = HashnodeSyndicator(config=self._make_config(token=""))
        syndicator.push({"query": "...", "variables": {"input": {"title": "Test"}}})

    def test_push_skips_when_no_publication_id(self):
        """缺少 publication_id 时 push 应跳过"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        syndicator = HashnodeSyndicator(config=self._make_config(publication_id=""))
        syndicator.push({"query": "...", "variables": {"input": {"title": "Test"}}})

    def test_format_payload_graphql_structure(self):
        """验证 format_payload 返回符合 Hashnode GraphQL 规范的结构"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        syndicator = HashnodeSyndicator(config=self._make_config())
        payload = syndicator.format_payload(
            title="Hello Hashnode",
            slug="hello-hashnode",
            content="# Test\nContent here.",
            metadata={"tags": ["Python", "AI"]},
        )
        assert "query" in payload
        assert "variables" in payload
        variables = payload["variables"]
        assert "input" in variables
        inp = variables["input"]
        assert inp["title"] == "Hello Hashnode"
        assert inp["slug"] == "hello-hashnode"
        assert inp["contentMarkdown"] == "# Test\nContent here."
        assert inp["publicationId"] == "pub-id-12345"
        assert isinstance(inp["tags"], list)
        assert inp["tags"][0]["slug"] == "python"
        assert inp["tags"][0]["name"] == "Python"
        assert inp["hideFromHashnodeFeed"] is False

    def test_format_payload_canonical_url_injected(self):
        """验证 site_url 被注入为 originalArticleURL"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        cfg = self._make_config()
        syndicator = HashnodeSyndicator(config=cfg)
        syndicator.site_url = "https://my-site.com"
        payload = syndicator.format_payload("Title", "my-slug", "content", {})
        inp = payload["variables"]["input"]
        assert inp.get("originalArticleURL") == "https://my-site.com/my-slug"

    def test_format_payload_tags_capped_at_5(self):
        """验证标签数量不超过 5 个"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        syndicator = HashnodeSyndicator(config=self._make_config())
        many_tags = ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7"]
        payload = syndicator.format_payload("T", "t", "c", {"tags": many_tags})
        assert len(payload["variables"]["input"]["tags"]) == 5

    @patch("requests.post")
    def test_push_success(self, mock_post):
        """模拟 GraphQL 发布成功"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "publishPost": {
                    "post": {
                        "id": "post-abc",
                        "slug": "hello-hashnode",
                        "url": "https://hashnode.dev/hello-hashnode",
                        "title": "Hello Hashnode",
                    }
                }
            }
        }
        mock_post.return_value = mock_resp

        syndicator = HashnodeSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Hello Hashnode", "hello-hashnode", "# Hi", {})
        syndicator.push(payload)

        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        assert "hashnode.com" in call_url

    @patch("requests.post")
    def test_push_raises_on_graphql_error(self, mock_post):
        """模拟 GraphQL 返回 errors 字段时正确抛出"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "errors": [{"message": "Post with this slug already exists"}]
        }
        mock_post.return_value = mock_resp

        syndicator = HashnodeSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Test", "test", "content", {})
        with pytest.raises(RuntimeError, match="Hashnode GraphQL 错误"):
            syndicator.push(payload)

    def test_inherits_base_syndicator(self):
        """验证正确继承 BaseSyndicator"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        from core.adapters.syndication.base import BaseSyndicator
        assert issubclass(HashnodeSyndicator, BaseSyndicator)
