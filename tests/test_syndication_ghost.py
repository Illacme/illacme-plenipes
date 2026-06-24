#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V76.0] Ghost Admin API 分发插件单元测试
🛡️ [V88.0 Split] 从 test_syndication_plugins.py 物理克隆搬迁。
"""
import os
import sys
import json
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath("."))


class TestGhostSyndicator:
    """Ghost Admin API 分发插件单元测试"""

    def _make_config(self, **kwargs):
        """构造 Mock 配置对象"""
        cfg = MagicMock()
        cfg.enabled = kwargs.get("enabled", True)
        cfg.url = kwargs.get("url", "https://ghost.example.com")
        cfg.admin_api_key = kwargs.get("admin_api_key", "deadbeef01:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
        cfg.update_existing = kwargs.get("update_existing", True)
        cfg.default_status = kwargs.get("default_status", "draft")
        return cfg

    def test_import_and_instantiate(self):
        """验证 GhostSyndicator 可正常导入和实例化"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        syndicator = GhostSyndicator(config=self._make_config())
        assert syndicator.PLUGIN_ID == "ghost"
        assert syndicator.url == "https://ghost.example.com"
        assert syndicator.default_status == "draft"

    def test_push_skips_when_no_url(self):
        """缺少 url 时 push 应跳过（不抛异常）"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        cfg = self._make_config(url="")
        syndicator = GhostSyndicator(config=cfg)
        syndicator.push({"posts": [{"title": "Test", "slug": "test"}]})

    def test_push_skips_when_no_api_key(self):
        """缺少 admin_api_key 时 push 应跳过"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        cfg = self._make_config(admin_api_key="")
        syndicator = GhostSyndicator(config=cfg)
        syndicator.push({"posts": [{"title": "Test", "slug": "test"}]})

    def test_push_raises_on_invalid_key_format(self):
        """admin_api_key 格式错误时应抛出 ValueError"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        cfg = self._make_config(admin_api_key="no-colon-here")
        syndicator = GhostSyndicator(config=cfg)
        with pytest.raises(ValueError, match="格式错误"):
            syndicator.push({"posts": [{"title": "Test", "slug": "test"}]})

    def test_format_payload_structure(self):
        """验证 format_payload 返回正确的 Ghost API 结构"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        syndicator = GhostSyndicator(config=self._make_config())
        payload = syndicator.format_payload(
            title="Hello Ghost",
            slug="hello-ghost",
            content="# Hello\nThis is a test.",
            metadata={"tags": ["python", "tech"]},
        )
        assert "posts" in payload
        post = payload["posts"][0]
        assert post["title"] == "Hello Ghost"
        assert post["slug"] == "hello-ghost"
        assert post["status"] == "draft"
        assert isinstance(post["tags"], list)
        assert len(post["tags"]) == 2
        assert post["tags"][0]["name"] == "python"
        mobiledoc = json.loads(post["mobiledoc"])
        assert mobiledoc["version"] == "0.3.1"
        assert mobiledoc["cards"][0][0] == "markdown"
        assert "Hello" in mobiledoc["cards"][0][1]["markdown"]

    def test_jwt_header_contains_kid(self):
        """验证 JWT header 中包含正确的 kid（key_id）"""
        import base64
        from adapters.egress.syndication.ghost import _build_ghost_jwt
        jwt = _build_ghost_jwt(
            key_id="deadbeef01",
            hex_secret="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        )
        parts = jwt.split(".")
        assert len(parts) == 3
        header_b64 = parts[0] + "=="
        header = json.loads(base64.urlsafe_b64decode(header_b64).decode())
        assert header["alg"] == "HS256"
        assert header["kid"] == "deadbeef01"
        assert header["typ"] == "JWT"

    def test_jwt_payload_contains_aud(self):
        """验证 JWT payload 中包含 Ghost 要求的 aud 字段"""
        import base64
        from adapters.egress.syndication.ghost import _build_ghost_jwt
        jwt = _build_ghost_jwt(
            key_id="abc",
            hex_secret="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        )
        parts = jwt.split(".")
        payload_b64 = parts[1] + "=="
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
        assert payload["aud"] == "/admin/"
        assert "iat" in payload
        assert "exp" in payload
        assert payload["exp"] > payload["iat"]

    @patch("requests.get")
    @patch("requests.post")
    def test_push_create_success(self, mock_post, mock_get):
        """模拟创建新文章成功"""
        from adapters.egress.syndication.ghost import GhostSyndicator

        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 404
        mock_get.return_value = mock_get_resp

        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 201
        mock_post_resp.json.return_value = {
            "posts": [{"id": "abc123", "url": "https://ghost.example.com/hello-ghost/", "slug": "hello-ghost"}]
        }
        mock_post.return_value = mock_post_resp

        syndicator = GhostSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Hello Ghost", "hello-ghost", "# Hello", {"tags": []})
        syndicator.push(payload)

        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        assert "/ghost/api/admin/posts/" in call_url

    @patch("requests.get")
    def test_push_raises_on_auth_failure(self, mock_get):
        """模拟 Ghost API 返回 401 时正确抛出"""
        from adapters.egress.syndication.ghost import GhostSyndicator

        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 401
        mock_get_resp.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_get.return_value = mock_get_resp

        syndicator = GhostSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Test", "test", "content", {"tags": []})
        with pytest.raises(Exception):
            syndicator.push(payload)

    def test_inherits_base_syndicator(self):
        """验证正确继承 BaseSyndicator"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        from core.adapters.syndication.base import BaseSyndicator
        assert issubclass(GhostSyndicator, BaseSyndicator)
