#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V76.0] LinkedIn UGC Posts API 分发插件单元测试
🛡️ [V88.0 Split] 从 test_syndication_plugins.py 物理克隆搬迁。
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath("."))


class TestLinkedInSyndicator:
    """LinkedIn UGC Posts API 分发插件单元测试"""

    def _make_config(self, **kwargs):
        cfg = MagicMock()
        cfg.enabled = kwargs.get("enabled", True)
        cfg.token = kwargs.get("token", "test_li_token")
        cfg.person_urn = kwargs.get("person_urn", "urn:li:person:test123")
        cfg.organization_urn = kwargs.get("organization_urn", "")
        cfg.visibility = kwargs.get("visibility", "PUBLIC")
        return cfg

    def test_import_and_instantiate(self):
        """验证 LinkedInSyndicator 可正常导入和实例化"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        syndicator = LinkedInSyndicator(config=self._make_config())
        assert syndicator.PLUGIN_ID == "linkedin"
        assert syndicator.person_urn == "urn:li:person:test123"
        assert syndicator.visibility == "PUBLIC"

    def test_push_skips_when_no_token(self):
        """缺少 token 时 push 应跳过"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        syndicator = LinkedInSyndicator(config=self._make_config(token=""))
        syndicator.push({})

    def test_push_skips_when_no_urn(self):
        """缺少 person_urn 和 organization_urn 时 push 应跳过"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        syndicator = LinkedInSyndicator(config=self._make_config(person_urn="", organization_urn=""))
        syndicator.push({})

    def test_format_payload_ugc_structure(self):
        """验证 format_payload 返回符合 LinkedIn UGC Post 结构"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        syndicator = LinkedInSyndicator(config=self._make_config())
        syndicator.site_url = "https://my-site.com"
        payload = syndicator.format_payload(
            title="Hello LinkedIn",
            slug="hello-linkedin",
            content="This is content for the article.",
            metadata={"description": "A brief summary."},
        )
        assert payload["author"] == "urn:li:person:test123"
        assert payload["lifecycleState"] == "PUBLISHED"
        share_content = payload["specificContent"]["com.linkedin.ugc.ShareContent"]
        assert share_content["shareMediaCategory"] == "ARTICLE"
        assert "Hello LinkedIn" in share_content["shareCommentary"]["text"]
        media = share_content["media"]
        assert len(media) == 1
        assert media[0]["originalUrl"] == "https://my-site.com/hello-linkedin"
        assert media[0]["title"]["text"] == "Hello LinkedIn"

    def test_format_payload_auto_excerpt(self):
        """验证无 description 时自动从正文截取摘要"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        syndicator = LinkedInSyndicator(config=self._make_config())
        long_content = "A" * 300
        payload = syndicator.format_payload("Title", "slug", long_content, {})
        commentary = payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"]["text"]
        assert "..." in commentary

    def test_format_payload_organization_urn_fallback(self):
        """验证 organization_urn 作为 author 兜底"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        cfg = self._make_config(person_urn="", organization_urn="urn:li:organization:9999")
        syndicator = LinkedInSyndicator(config=cfg)
        payload = syndicator.format_payload("Title", "slug", "content", {})
        assert payload["author"] == "urn:li:organization:9999"

    def test_format_payload_visibility(self):
        """验证 visibility 字段传递"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        syndicator = LinkedInSyndicator(config=self._make_config(visibility="CONNECTIONS"))
        payload = syndicator.format_payload("Title", "slug", "content", {})
        vis = payload["visibility"]["com.linkedin.ugc.MemberNetworkVisibility"]
        assert vis == "CONNECTIONS"

    @patch("requests.post")
    def test_push_success(self, mock_post):
        """模拟 LinkedIn 发布成功（HTTP 201）"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.headers = {"x-restli-id": "urn:li:ugcPost:987654321"}
        mock_post.return_value = mock_resp

        syndicator = LinkedInSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Hello LinkedIn", "hello-linkedin", "content", {})
        syndicator.push(payload)

        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        assert "linkedin.com" in call_url

    @patch("requests.post")
    def test_push_raises_on_401(self, mock_post):
        """模拟 LinkedIn 返回 401 时正确抛出并提示 Token 问题"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_post.return_value = mock_resp

        syndicator = LinkedInSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Test", "test", "content", {})
        with pytest.raises(RuntimeError, match="Access Token"):
            syndicator.push(payload)

    @patch("requests.post")
    def test_push_raises_on_403(self, mock_post):
        """模拟 LinkedIn 返回 403 时正确抛出并提示权限问题"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"
        mock_post.return_value = mock_resp

        syndicator = LinkedInSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Test", "test", "content", {})
        with pytest.raises(RuntimeError, match="w_member_social"):
            syndicator.push(payload)

    def test_inherits_base_syndicator(self):
        """验证正确继承 BaseSyndicator"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        from core.adapters.syndication.base import BaseSyndicator
        assert issubclass(LinkedInSyndicator, BaseSyndicator)
