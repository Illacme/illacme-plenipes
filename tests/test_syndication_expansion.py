#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — 6 New Syndication Plugins Tests
验证微信公众号、知乎专栏、稀土掘金、Substack、Telegram 频道、Discord Webhook 分发插件。
"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath('.'))


class TestWeChatSyndicator:
    """WeChat Syndicator Unit Tests"""
    def test_instantiate(self):
        from adapters.egress.syndication.wechat import WeChatSyndicator
        cfg = {"enabled": True, "app_id": "wx123", "app_secret": "secret123"}
        syn = WeChatSyndicator(config=cfg, site_url="https://blog.me")
        assert syn.PLUGIN_ID == "wechat"
        assert syn.config.get("app_id") == "wx123"
        assert syn.config.get("app_secret") == "secret123"

    @patch("requests.post")
    @patch("requests.get")
    def test_push_success(self, mock_get, mock_post):
        from adapters.egress.syndication.wechat import WeChatSyndicator
        cfg = MagicMock(app_id="wx123", app_secret="secret123", enabled=True)
        syn = WeChatSyndicator(config=cfg, site_url="https://blog.me")
        
        # Mock 获取 Access Token
        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = {"access_token": "token-xyz"}
        mock_get.return_value = mock_token_resp

        # Mock 推送草稿
        mock_draft_resp = MagicMock()
        mock_draft_resp.status_code = 200
        mock_draft_resp.json.return_value = {"media_id": "draft-media-123"}
        mock_post.return_value = mock_draft_resp

        payload = syn.format_payload("Title", "slug-1", "Content", {}, None)
        syn.push(payload)
        
        mock_get.assert_called_once()
        mock_post.assert_called_once()


class TestZhihuSyndicator:
    """Zhihu Syndicator Unit Tests"""
    @patch("requests.post")
    def test_push_success(self, mock_post):
        from adapters.egress.syndication.zhihu import ZhihuSyndicator
        cfg = MagicMock(token="token-123", column_id="col-abc", enabled=True)
        syn = ZhihuSyndicator(config=cfg, site_url="https://blog.me")

        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_post.return_value = mock_resp

        payload = syn.format_payload("Title", "slug-1", "Content", {}, None)
        syn.push(payload)

        mock_post.assert_called_once()
        headers = mock_post.call_args[1]["headers"]
        assert "Bearer token-123" in headers["Authorization"]


class TestJuejinSyndicator:
    """Juejin Syndicator Unit Tests"""
    @patch("requests.post")
    def test_push_success(self, mock_post):
        from adapters.egress.syndication.juejin import JuejinSyndicator
        cfg = MagicMock(cookie="cookie-123", api_token="token-123", enabled=True)
        syn = JuejinSyndicator(config=cfg, site_url="https://blog.me")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"err_no": 0, "data": {"draft_id": "draft-123"}}
        mock_post.return_value = mock_resp

        payload = syn.format_payload("Title", "slug-1", "Content", {}, None)
        syn.push(payload)

        mock_post.assert_called_once()
        headers = mock_post.call_args[1]["headers"]
        assert headers["Cookie"] == "cookie-123"
        assert headers["X-Juejin-Token"] == "token-123"


class TestSubstackSyndicator:
    """Substack Syndicator Unit Tests"""
    @patch("requests.post")
    def test_push_success(self, mock_post):
        from adapters.egress.syndication.substack import SubstackSyndicator
        cfg = MagicMock(url="https://myname.substack.com", cookie="sid-123", api_key="key-123", enabled=True)
        syn = SubstackSyndicator(config=cfg, site_url="https://blog.me")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        payload = syn.format_payload("Title", "slug-1", "Content", {}, None)
        syn.push(payload)

        mock_post.assert_called_once()
        assert "https://myname.substack.com/api/v1/posts" in mock_post.call_args[0][0]


class TestTelegramSyndicator:
    """Telegram Syndicator Unit Tests"""
    @patch("requests.post")
    def test_push_success(self, mock_post):
        from adapters.egress.syndication.telegram import TelegramSyndicator
        cfg = MagicMock(bot_token="bot-123", chat_id="chat-123", enabled=True)
        syn = TelegramSyndicator(config=cfg, site_url="https://blog.me")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        payload = syn.format_payload("Title", "slug-1", "Content", {}, None)
        syn.push(payload)

        mock_post.assert_called_once()
        assert "bot-123/sendMessage" in mock_post.call_args[0][0]


class TestDiscordSyndicator:
    """Discord Syndicator Unit Tests"""
    @patch("requests.post")
    def test_push_success(self, mock_post):
        from adapters.egress.syndication.discord import DiscordSyndicator
        cfg = MagicMock(webhook_url="https://discord.com/api/webhooks/123", enabled=True)
        syn = DiscordSyndicator(config=cfg, site_url="https://blog.me")

        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_post.return_value = mock_resp

        payload = syn.format_payload("Title", "slug-1", "Content", {}, None)
        syn.push(payload)

        mock_post.assert_called_once()
        assert mock_post.call_args[0][0] == "https://discord.com/api/webhooks/123"
