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
        from adapters.egress.syndication.wechat import WeChatSyndicator, wechat_token_cache
        wechat_token_cache.invalidate("wx123", "secret123")
        cfg = MagicMock(app_id="wx123", app_secret="secret123", enabled=True)
        syn = WeChatSyndicator(config=cfg, site_url="https://blog.me")
        
        # Mock 获取 Access Token
        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = {"access_token": "token-xyz"}
        mock_get.return_value = mock_token_resp

        # Mock 推送草稿及素材上传
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {"media_id": "draft-media-123"}
        mock_post.return_value = mock_post_resp

        payload = syn.format_payload("Title", "slug-1", "Content", {}, None)
        res = syn.push(payload, remote_id="optional-remote-id")
        
        mock_get.assert_called_once()
        assert mock_post.call_count >= 1
        assert res["media_id"] == "draft-media-123"

    @patch("adapters.egress.syndication.wechat_shards.wechat_uploader.requests.post")
    def test_ensure_valid_thumb_media_id_default_fallback(self, mock_post):
        from adapters.egress.syndication.wechat_shards.wechat_uploader import ensure_valid_thumb_media_id, _thumb_cache
        _thumb_cache.clear()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"media_id": "thumb_mat_888"}
        mock_post.return_value = mock_resp

        articles = [
            {
                "title": "无图文章",
                "thumb_media_id": "media_id_placeholder",
                "content": "<p>纯文本内容</p>"
            }
        ]

        result = ensure_valid_thumb_media_id(articles, access_token="mock_token")
        assert result[0]["thumb_media_id"] == "thumb_mat_888"

    def test_format_payload_with_inline_styles_and_footnotes(self):
        from adapters.egress.syndication.wechat import WeChatSyndicator
        cfg = {"enabled": True, "app_id": "wx123", "app_secret": "secret123", "author": "极客团队", "convert_footnotes": True}
        syn = WeChatSyndicator(config=cfg, site_url="https://blog.me")

        markdown_text = (
            "# 架构升级指南\n\n"
            "这是正文内容，欢迎查阅 [GitHub 源码](https://github.com/my-org/repo) 以及 [官方文档](https://example.com/docs)。\n\n"
            "同时也可以查看 [微信推文](https://mp.weixin.qq.com/s/abcdef)。\n\n"
            "```python\nprint('hello')\n```"
        )
        payload = syn.format_payload("测试文章", "test-post", markdown_text, {}, None)
        article = payload["articles"][0]

        assert article["author"] == "极客团队"
        content = article["content"]
        
        # 1. 验证内联样式注入
        assert 'style="font-size: 20px;' in content or 'font-size:' in content
        assert 'style="background-color: #1e1e1e;' in content or 'pre' in content
        
        # 2. 验证外部链接转化为带有样式的角标
        assert "GitHub 源码<sup style=" in content
        assert ">[1]</sup>" in content
        assert "官方文档<sup style=" in content
        assert ">[2]</sup>" in content
        
        # 3. 验证微信白名单链接保留未转角标
        assert 'href="https://mp.weixin.qq.com/s/abcdef"' in content
        
        # 4. 验证文末附带参考资料板块
        assert "📚 参考资料" in content
        assert "https://github.com/my-org/repo" in content
        assert "https://example.com/docs" in content

    def test_format_payload_strict_sanitization(self):
        from adapters.egress.syndication.wechat import WeChatSyndicator
        cfg = {"enabled": True, "app_id": "wx123", "app_secret": "secret123"}
        syn = WeChatSyndicator(config=cfg, site_url="http://localhost:43212")

        meta = {
            "title": "这是一个非常长非常长非常长非常长非常长非常长非常长非常长的标题测试",
            "author": "SuperLongAuthorNameThatExceedsLimit",
            "description": "专为海量 Markdown 构筑的 AI 原生全球出版引擎，让灵感在起草室点燃，在文库中沉淀，通过矩阵响彻全球。" * 2
        }
        payload = syn.format_payload(meta["title"], "test-slug", "正文内容", meta, canonical_url="http://localhost:43212/test-slug")
        art = payload["articles"][0]

        # 验证标题截断至 32 字符
        assert len(art["title"]) <= 32
        # 验证作者截断至 8 字符
        assert len(art["author"]) <= 8
        # 验证摘要清洗且截断至 40 字符 (防御 45004 description size out of limit)
        assert len(art["digest"]) <= 40
        assert "\n" not in art["digest"]
        # 验证 localhost 自动清洗置空 (防御 41039 invalid content_source_url)
        assert art["content_source_url"] == ""

        # 验证合法公网 URL 正常保留
        syn_public = WeChatSyndicator(config=cfg, site_url="https://illacme.org")
        payload_public = syn_public.format_payload("Title", "test-slug", "正文", {}, canonical_url="https://illacme.org/posts/test-slug")
        assert payload_public["articles"][0]["content_source_url"] == "https://illacme.org/posts/test-slug"

    def test_format_payload_convert_footnotes_disabled(self):
        from adapters.egress.syndication.wechat import WeChatSyndicator
        cfg = {"enabled": True, "app_id": "wx123", "app_secret": "secret123", "convert_footnotes": False}
        syn = WeChatSyndicator(config=cfg, site_url="https://blog.me")

        markdown_text = "查看 [外部链接](https://example.com/test)。"
        payload = syn.format_payload("测试文章", "test-post", markdown_text, {}, None)
        content = payload["articles"][0]["content"]

        # 不应转为上标角标
        assert "<sup>[1]</sup>" not in content
        assert "📚 参考资料" not in content
        assert 'href="https://example.com/test"' in content

    @patch("adapters.egress.syndication.wechat_shards.wechat_uploader.requests.post")
    @patch("adapters.egress.syndication.wechat_shards.wechat_uploader.requests.get")
    def test_transmute_article_images_success_and_caching(self, mock_get, mock_post):
        from adapters.egress.syndication.wechat_shards.wechat_uploader import transmute_article_images

        # 模拟外部图片拉取成功
        mock_img_resp = MagicMock()
        mock_img_resp.status_code = 200
        mock_img_resp.content = b"fake-image-bytes"
        mock_img_resp.headers = {"Content-Type": "image/png"}
        mock_get.return_value = mock_img_resp

        # 模拟微信 uploadimg 接口成功
        mock_upload_resp = MagicMock()
        mock_upload_resp.status_code = 200
        mock_upload_resp.json.return_value = {"url": "http://mmbiz.qpic.cn/mmbiz_png/test_hash/0?wx_fmt=png"}
        mock_post.return_value = mock_upload_resp

        articles = [
            {
                "title": "测试图片转存",
                "content": (
                    '<p>第一张图：<img src="https://example.com/pic1.png" alt="pic1" /></p>'
                    '<p>重复引用：<img src="https://example.com/pic1.png" alt="pic1_repeat" /></p>'
                    '<p>微信白名单图：<img src="http://mmbiz.qpic.cn/existing.png" alt="wx" /></p>'
                )
            }
        ]

        result = transmute_article_images(articles, access_token="token_abc")
        content = result[0]["content"]

        # 验证图片已替换为微信 CDN URL
        assert 'src="http://mmbiz.qpic.cn/mmbiz_png/test_hash/0?wx_fmt=png"' in content
        # 验证重复引用也同样被替换
        assert 'https://example.com/pic1.png' not in content
        # 验证微信已有域名保持原样
        assert 'src="http://mmbiz.qpic.cn/existing.png"' in content

        # 验证去重缓存：pic1 虽然出现两次，但 uploadimg 只调用了一次
        assert mock_post.call_count == 1

    @patch("adapters.egress.syndication.wechat_shards.wechat_uploader.requests.get")
    def test_transmute_article_images_graceful_fallback(self, mock_get):
        from adapters.egress.syndication.wechat_shards.wechat_uploader import transmute_article_images

        # 模拟下载异常
        mock_get.side_effect = RuntimeError("Network timeout")

        articles = [
            {
                "title": "测试降级",
                "content": '<p><img src="https://broken.com/image.png" /></p>'
            }
        ]

        # 异常不应当中断，平滑降级保留原链接
        result = transmute_article_images(articles, access_token="token_abc")
        assert 'src="https://broken.com/image.png"' in result[0]["content"]


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

    @patch("requests.post")
    def test_push_with_cookie_success(self, mock_post):
        from adapters.egress.syndication.zhihu import ZhihuSyndicator
        cfg = MagicMock(token="", cookie="z_c0=mock_cookie_val", column_id="col-abc", enabled=True)
        syn = ZhihuSyndicator(config=cfg, site_url="https://blog.me")

        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_post.return_value = mock_resp

        payload = syn.format_payload("Title", "slug-1", "Content", {}, None)
        syn.push(payload)

        mock_post.assert_called_once()
        headers = mock_post.call_args[1]["headers"]
        assert headers.get("Cookie") == "z_c0=mock_cookie_val"


class TestJuejinSyndicator:
    """Juejin Syndicator Unit Tests"""
    @patch("requests.post")
    def test_push_create_draft_success(self, mock_post):
        from adapters.egress.syndication.juejin import JuejinSyndicator
        cfg = MagicMock(cookie="cookie-123", api_token="token-123", enabled=True)
        syn = JuejinSyndicator(config=cfg, site_url="https://blog.me")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"err_no": 0, "data": {"draft_id": "draft-123"}}
        mock_post.return_value = mock_resp

        payload = syn.format_payload("Title", "slug-1", "## Hello\n**World** content here", {}, None)
        assert payload["brief_content"] == "Hello World content here"
        assert payload["category_id"] == "6809637767543259144"

        res = syn.push(payload)

        mock_post.assert_called_once()
        assert "article_draft/create" in mock_post.call_args[0][0]
        headers = mock_post.call_args[1]["headers"]
        assert headers["Cookie"] == "cookie-123"
        assert headers["X-Juejin-Token"] == "token-123"
        assert res["draft_id"] == "draft-123"
        assert res["url"] == "https://juejin.cn/editor/drafts/draft-123"
        assert res["draft"] is True

    @patch("requests.post")
    def test_push_update_draft_success(self, mock_post):
        from adapters.egress.syndication.juejin import JuejinSyndicator
        cfg = {"cookie": "cookie-xyz", "category_id": "6809637767543259143"}
        syn = JuejinSyndicator(config=cfg, site_url="https://blog.me")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"err_no": 0, "data": {"id": "draft-existing-999"}}
        mock_post.return_value = mock_resp

        payload = syn.format_payload("Update Title", "slug-2", "New Content", {}, None)
        assert payload["category_id"] == "6809637767543259143"

        res = syn.push(payload, remote_id="draft-existing-999")

        assert "article_draft/update" in mock_post.call_args[0][0]
        assert mock_post.call_args[1]["json"]["id"] == "draft-existing-999"
        assert res["draft_id"] == "draft-existing-999"
        assert res["url"] == "https://juejin.cn/editor/drafts/draft-existing-999"

    @patch("requests.get")
    def test_juejin_connection_probe(self, mock_get):
        from services.api.routes.gov.context_shards.social_shards.social_domestic import probe_domestic_social
        logs = []
        def log_fn(level, msg):
            return f"[{level}] {msg}"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "err_no": 0,
            "data": {"user_id": "998877", "user_name": "掘金极客"}
        }
        mock_get.return_value = mock_resp

        ok = probe_domestic_social(
            plugin_id="juejin",
            settings={"cookie": "session-valid"},
            logs=logs,
            log_func=log_fn,
            proxies=None
        )
        assert ok is True
        assert any("掘金极客" in line and "998877" in line for line in logs)



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


class TestCookieAutoCapture:
    """Cookie Auto Capture Tests"""
    @patch("services.api.routes.gov.context_shards.plugin_capture_ops.get_global_engine")
    @patch("requests.get")
    @patch("services.api.routes.gov.config.update_config")
    def test_auto_capture_juejin_success(self, mock_update_cfg, mock_get, mock_engine):
        import asyncio
        from services.api.routes.gov.context_shards.plugin_capture_ops import auto_capture_cookie_impl

        mock_engine.return_value = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "err_no": 0,
            "data": {"user_id": "888888", "user_name": "极客创作者"}
        }
        mock_get.return_value = mock_resp
        
        async def fake_update_config(*args, **kwargs):
            return {"status": "success"}
        mock_update_cfg.side_effect = fake_update_config

        res = asyncio.run(auto_capture_cookie_impl({
            "plugin_id": "juejin",
            "cookie": "sessionid=test_cookie_val"
        }))

        assert res["success"] is True
        assert res["user_name"] == "极客创作者"
        assert res["user_id"] == "888888"
        mock_update_cfg.assert_called_once()
        assert mock_update_cfg.call_args[0][0]["syndication.juejin.cookie"] == "sessionid=test_cookie_val"

    @patch("urllib.request.urlopen")
    @patch("websockets.connect")
    @patch("services.api.routes.gov.context_shards.plugin_capture_ops.auto_capture_cookie_impl")
    def test_auto_sniff_juejin_success(self, mock_auto_capture, mock_ws_connect, mock_urlopen):
        import asyncio
        import json
        from services.api.routes.gov.context_shards.plugin_capture_ops import auto_sniff_local_browser_impl

        # Mock urllib response for http://localhost:9222/json
        mock_pages_json = json.dumps([
            {
                "type": "page",
                "title": "掘金创作者中心",
                "url": "https://juejin.cn/creator",
                "webSocketDebuggerUrl": "ws://localhost:9222/devtools/page/TEST_PAGE_ID"
            }
        ]).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value.read.return_value = mock_pages_json

        # Mock websocket
        class MockWs:
            async def __aenter__(self):
                return self
            async def __aexit__(self, *args):
                pass
            async def send(self, data):
                pass
            async def recv(self):
                return json.dumps({
                    "id": 1,
                    "result": {
                        "cookies": [
                            {"name": "sessionid", "value": "sniffed_session_val"},
                            {"name": "passport_token", "value": "token_abc"}
                        ]
                    }
                })

        mock_ws_connect.return_value = MockWs()

        async def fake_capture(payload):
            return {
                "success": True,
                "plugin_id": "juejin",
                "user_name": "嗅探创作者",
                "user_id": "999999",
                "cookie": payload["cookie"],
                "message": "成功"
            }
        mock_auto_capture.side_effect = fake_capture

        res = asyncio.run(auto_sniff_local_browser_impl({"plugin_id": "juejin", "browser_port": 9222}))
        assert res.get("success") is True, f"Error was: {res}"
        assert res["user_name"] == "嗅探创作者"
        assert "sessionid=sniffed_session_val" in res["cookie"]

    @patch("urllib.request.urlopen")
    @patch("websockets.connect")
    @patch("services.api.routes.gov.context_shards.plugin_capture_ops.auto_capture_cookie_impl")
    def test_auto_sniff_zhihu_success(self, mock_auto_capture, mock_ws_connect, mock_urlopen):
        import asyncio
        import json
        from services.api.routes.gov.context_shards.plugin_capture_ops import auto_sniff_local_browser_impl

        mock_pages_json = json.dumps([
            {
                "type": "page",
                "title": "知乎首页",
                "url": "https://www.zhihu.com/creator",
                "webSocketDebuggerUrl": "ws://localhost:9222/devtools/page/ZHIHU_ID"
            }
        ]).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value.read.return_value = mock_pages_json

        class MockWs:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def send(self, data): pass
            async def recv(self):
                return json.dumps({
                    "id": 101,
                    "result": {
                        "cookies": [
                            {"name": "z_c0", "value": "2|1:0|mock_zc0_token"},
                            {"name": "_zap", "value": "zap_123"}
                        ]
                    }
                })
        mock_ws_connect.return_value = MockWs()

        async def fake_capture(payload):
            return {
                "success": True, "plugin_id": "zhihu", "user_name": "知乎极客",
                "cookie": payload["cookie"], "token": "2|1:0|mock_zc0_token"
            }
        mock_auto_capture.side_effect = fake_capture

        res = asyncio.run(auto_sniff_local_browser_impl({"plugin_id": "zhihu"}))
        assert res.get("success") is True, f"Error: {res}"
        assert res["user_name"] == "知乎极客"
        assert "z_c0=" in res["cookie"]

    @patch("urllib.request.urlopen")
    @patch("websockets.connect")
    @patch("services.api.routes.gov.context_shards.plugin_capture_ops.auto_capture_cookie_impl")
    def test_auto_sniff_bilibili_success(self, mock_auto_capture, mock_ws_connect, mock_urlopen):
        import asyncio
        import json
        from services.api.routes.gov.context_shards.plugin_capture_ops import auto_sniff_local_browser_impl

        mock_pages_json = json.dumps([
            {
                "type": "page",
                "title": "Bilibili 创作中心",
                "url": "https://member.bilibili.com/platform/home",
                "webSocketDebuggerUrl": "ws://localhost:9222/devtools/page/BILI_ID"
            }
        ]).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value.read.return_value = mock_pages_json

        class MockWs:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def send(self, data): pass
            async def recv(self):
                return json.dumps({
                    "id": 101,
                    "result": {
                        "cookies": [
                            {"name": "SESSDATA", "value": "mock_sessdata_abc"},
                            {"name": "bili_jct", "value": "mock_jct_123"}
                        ]
                    }
                })
        mock_ws_connect.return_value = MockWs()

        async def fake_capture(payload):
            return {
                "success": True, "plugin_id": "bilibili", "user_name": "B站知名UP主",
                "sessdata": "mock_sessdata_abc", "bili_jct": "mock_jct_123"
            }
        mock_auto_capture.side_effect = fake_capture

        res = asyncio.run(auto_sniff_local_browser_impl({"plugin_id": "bilibili"}))
        assert res.get("success") is True, f"Error: {res}"
        assert res["user_name"] == "B站知名UP主"
        assert res["sessdata"] == "mock_sessdata_abc"


class TestSyndicationDiagnostic:
    """Syndication Diagnostic Hub & Error Root Cause Attribution Tests"""
    def test_diagnose_wechat_invalid_media_id(self):
        from core.syndication.syndication_diagnostic import diagnose_syndication_error
        diag = diagnose_syndication_error("wechat", "errcode 40007: invalid media_id hint: [xxx]")
        assert diag["code"] == "WECHAT_INVALID_MEDIA_ID"
        assert diag["badge"] == "🖼️ 封面素材失效"
        assert diag["quick_drawer_id"] == "wechat"
        assert "封面" in diag["suggestion"]

    def test_diagnose_wechat_digest_out_of_limit(self):
        from core.syndication.syndication_diagnostic import diagnose_syndication_error
        diag = diagnose_syndication_error("wechat", "45004 description size out of limit")
        assert diag["code"] == "WECHAT_DIGEST_LIMIT"
        assert diag["badge"] == "✂️ 摘要超长拦截"
        assert "摘要" in diag["friendly_message"]

    def test_diagnose_wechat_local_source_url(self):
        from core.syndication.syndication_diagnostic import diagnose_syndication_error
        diag = diagnose_syndication_error("wechat", "41039 invalid content_source_url")
        assert diag["code"] == "WECHAT_LOCAL_SOURCE_URL"
        assert diag["badge"] == "🌐 原文链接受限"
        assert "公网可访问" in diag["suggestion"]

    def test_diagnose_auth_cookie_expired(self):
        from core.syndication.syndication_diagnostic import diagnose_syndication_error
        diag = diagnose_syndication_error("juejin", "HTTP 401 Unauthorized: session expired")
        assert diag["code"] == "AUTH_INVALID_TOKEN"
        assert diag["badge"] == "⚠️ 凭据失效/未授权"
        assert diag["quick_drawer_id"] == "juejin"
        assert "重新授权" in diag["suggestion"]

    def test_diagnose_rate_limit(self):
        from core.syndication.syndication_diagnostic import diagnose_syndication_error
        diag = diagnose_syndication_error("zhihu", "429 Too Many Requests: frequency limited")
        assert diag["code"] == "RATE_LIMIT_EXCEEDED"
        assert diag["badge"] == "🛑 频率受限超限"
        assert "稍候重试" in diag["suggestion"]

    def test_diagnose_network_timeout(self):
        from core.syndication.syndication_diagnostic import diagnose_syndication_error
        diag = diagnose_syndication_error("devto", "Connection reset by peer: Timeout 15s")
        assert diag["code"] == "NETWORK_ERROR"
        assert diag["badge"] == "⚡ 网络连接超时"
        assert "代理" in diag["suggestion"]

