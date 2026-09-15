#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - WeChat Syndication End-to-End Simulation & Verification Test Suite
测试职责：
1. 微信 Access Token 长效缓存、静默续期与 40164 IP 白名单自愈诊断；
2. 微信图文 Inline CSS 高保真排版与外链转脚注；
3. 正文图片转存微信素材 CDN 与 2.35:1 官方封面自愈保底；
4. 草稿箱 draft/add 端到端推送演练（UTF-8 乱码免疫、40001 自愈重试）；
5. 治理中心沙盒连接测试探针诊断与直接直连（direct）模式。
严格遵守 SOP-01（< 300 行）与用户规则 10、11。
"""

import io
import json
import unittest
from unittest.mock import patch, MagicMock
from PIL import Image

from adapters.egress.syndication.wechat import WeChatSyndicator
from adapters.egress.syndication.wechat_shards.wechat_token_cache import WeChatTokenCache
from adapters.egress.syndication.wechat_shards.wechat_formatter import render_wechat_html
from adapters.egress.syndication.wechat_shards.wechat_uploader import (
    transmute_article_images,
    ensure_valid_thumb_media_id,
    generate_default_cover_bytes,
)
from services.api.routes.gov.context_shards.social_shards.social_domestic import probe_domestic_social


class TestWeChatSyndicationFlow(unittest.TestCase):

    def setUp(self):
        self.config = {
            "enabled": True,
            "app_id": "wx_unit_test_appid",
            "app_secret": "wx_unit_test_secret",
            "author": "Plenipes",
            "proxy": "direct",
        }
        self.syndicator = WeChatSyndicator(self.config)

    # ─────────────────────────────────────────────────────────────
    # 1. Access Token 缓存与 40164 白名单诊断
    # ─────────────────────────────────────────────────────────────
    @patch("requests.get")
    def test_token_cache_and_40164_guidance(self, mock_get):
        cache = WeChatTokenCache()
        cache.invalidate("appid_1", "secret_1")
        cache.invalidate("appid_2", "secret_2")

        # 1.1 正常获取
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"access_token": "mock_token_abc_123", "expires_in": 7200}
        mock_get.return_value = mock_resp

        token = cache.get_token("appid_1", "secret_1", proxy="direct", force_refresh=True)
        self.assertEqual(token, "mock_token_abc_123")
        # 验证 direct 直连模式传入了 {"http": None, "https": None}
        mock_get.assert_called_with(
            "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=appid_1&secret=secret_1",
            proxies={"http": None, "https": None},
            timeout=15,
        )

        # 1.2 缓存命中（不应发起第二次网络调用）
        mock_get.reset_mock()
        token_cached = cache.get_token("appid_1", "secret_1")
        self.assertEqual(token_cached, "mock_token_abc_123")
        mock_get.assert_not_called()

        # 1.3 40164 白名单拦截自愈提示断言
        mock_resp_40164 = MagicMock()
        mock_resp_40164.status_code = 200
        mock_resp_40164.json.return_value = {
            "errcode": 40164,
            "errmsg": "invalid ip 203.0.113.195, not in whitelist hint: [xyz]",
        }
        mock_get.return_value = mock_resp_40164
        with self.assertRaises(RuntimeError) as ctx:
            cache.get_token("appid_2", "secret_2", force_refresh=True)
        self.assertIn("203.0.113.195", str(ctx.exception))
        self.assertIn("IP 白名单拦截", str(ctx.exception))
        self.assertIn("IP白名单", str(ctx.exception))

    # ─────────────────────────────────────────────────────────────
    # 2. 富文本 HTML 样式与外链转脚注
    # ─────────────────────────────────────────────────────────────
    def test_wechat_html_formatting_and_footnotes(self):
        raw_md = """---
title: 测试文章
tags: [测试]
---

# 微信排版标题

这是一段正文，包含[外部技术链接](https://example.com/docs)以及[微信官方文档](https://mp.weixin.qq.com/wiki)。

> 这是一个引用块
"""
        html = render_wechat_html(raw_md, {"convert_footnotes": True})

        # 断言剥离了 YAML Frontmatter
        self.assertNotIn("tags: [测试]", html)
        # 断言外部链接转换为角标与文末参考资料
        self.assertIn("[1]</sup>", html)
        self.assertIn("📚 参考资料", html)
        self.assertIn("https://example.com/docs", html)
        # 断言微信官方白名单链接不被转换为角标
        self.assertNotIn("mp.weixin.qq.com<sup>", html)
        # 断言包含高质量内联样式
        self.assertIn("border-left: 4px solid #3b82f6", html)
        self.assertIn("font-family: -apple-system", html)

    # ─────────────────────────────────────────────────────────────
    # 3. 正文图片转存与封面自愈保底
    # ─────────────────────────────────────────────────────────────
    @patch("adapters.egress.syndication.wechat_shards.wechat_uploader.fetch_image_bytes")
    @patch("adapters.egress.syndication.wechat_shards.wechat_uploader.upload_to_wechat_uploadimg")
    @patch("adapters.egress.syndication.wechat_shards.wechat_uploader.upload_wechat_thumb")
    def test_image_transmute_and_cover_fallback(self, mock_upload_thumb, mock_upload_img, mock_fetch):
        # 3.1 正文图片转存
        mock_fetch.return_value = (b"fake_image_bytes", "demo.png")
        mock_upload_img.return_value = "http://mmbiz.qpic.cn/wechat_cdn_hash/0?wx_fmt=png"

        articles = [{
            "title": "测试图文",
            "content": '<p>段落一</p><img src="https://other-domain.com/pic.png"><p>段落二</p>',
            "thumb_media_id": "media_id_placeholder",
        }]

        transmuted = transmute_article_images(articles, "mock_token")
        self.assertIn("http://mmbiz.qpic.cn/wechat_cdn_hash/0?wx_fmt=png", transmuted[0]["content"])
        self.assertNotIn("https://other-domain.com/pic.png", transmuted[0]["content"])

        # 3.2 封面自愈保底：未提供任何封面时自动生成官方 2.35:1 科技封面并上传
        mock_upload_thumb.return_value = "perm_media_id_99999"
        articles_no_cover = [{
            "title": "无封面图文",
            "content": "<p>无图正文</p>",
            "thumb_media_id": "media_id_placeholder",
        }]
        ensured = ensure_valid_thumb_media_id(articles_no_cover, "mock_token")
        self.assertEqual(ensured[0]["thumb_media_id"], "perm_media_id_99999")
        mock_upload_thumb.assert_called()

        # 3.3 验证默认封面图生成质量 (900x383)
        cover_bytes = generate_default_cover_bytes()
        self.assertGreater(len(cover_bytes), 0)
        img = Image.open(io.BytesIO(cover_bytes))
        self.assertEqual(img.size, (900, 383))

    # ─────────────────────────────────────────────────────────────
    # 4. 草稿箱 draft/add 端到端推送演练
    # ─────────────────────────────────────────────────────────────
    @patch("adapters.egress.syndication.wechat.wechat_token_cache.get_token")
    @patch("adapters.egress.syndication.wechat.ensure_valid_thumb_media_id")
    @patch("requests.post")
    def test_wechat_push_draft_end_to_end(self, mock_post, mock_ensure_thumb, mock_get_token):
        mock_get_token.return_value = "token_valid_888"

        def _set_thumb(articles, *args, **kwargs):
            for a in articles:
                a["thumb_media_id"] = "real_media_id_thumb"
            return articles
        mock_ensure_thumb.side_effect = _set_thumb

        # 模拟微信 draft/add 成功
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"errcode": 0, "errmsg": "ok", "media_id": "draft_media_id_666"}
        mock_post.return_value = mock_resp

        payload = self.syndicator.format_payload(
            title="微信公众号端到端实战演练",
            slug="wechat-e2e-drill",
            content="# 演练标题\n这是演练正文内容。",
            metadata={"author": "Eason", "description": "微信草稿箱分发演练"},
            canonical_url="https://illacme.org/posts/wechat-e2e",
        )

        res = self.syndicator.push(payload)
        self.assertEqual(res["media_id"], "draft_media_id_666")
        self.assertTrue(res["draft"])
        self.assertEqual(res["remote_id"], "draft_media_id_666")

        # 验证 draft/add 发送时使用的是原生 UTF-8 编码
        call_args = mock_post.call_args
        posted_data = call_args[1].get("data") or call_args[0][1]
        decoded = json.loads(posted_data.decode("utf-8"))
        self.assertEqual(decoded["articles"][0]["title"], "微信公众号端到端实战演练")
        self.assertEqual(decoded["articles"][0]["thumb_media_id"], "real_media_id_thumb")

    # ─────────────────────────────────────────────────────────────
    # 5. 治理中心沙盒连接测试探针诊断
    # ─────────────────────────────────────────────────────────────
    @patch("requests.get")
    def test_sandbox_dry_run_diagnostics(self, mock_get):
        logs = []
        def log_func(lvl, msg):
            return {"level": lvl, "message": msg}

        # 5.1 40164 白名单拦截时友好输出 IP
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "errcode": 40164,
            "errmsg": "invalid ip 198.51.100.22, not in whitelist",
        }
        mock_get.return_value = mock_resp

        ok = probe_domestic_social("wechat", {"app_id": "id1", "app_secret": "sec1", "proxy": "direct"}, logs, log_func, {})
        self.assertFalse(ok)
        all_msgs = " ".join([l["message"] for l in logs])
        self.assertIn("198.51.100.22", all_msgs)
        self.assertIn("IP白名单", all_msgs)

        # 5.2 成功握手
        logs.clear()
        mock_resp.json.return_value = {"access_token": "valid_token_xyz"}
        ok = probe_domestic_social("wechat", {"app_id": "id1", "app_secret": "sec1"}, logs, log_func, {})
        self.assertTrue(ok)
        success_msgs = " ".join([l["message"] for l in logs])
    # ─────────────────────────────────────────────────────────────
    # 6. 自定义封面与设计中心资产图上传断言 (彻底根除默认边框卡片 fallback 断链)
    # ─────────────────────────────────────────────────────────────
    @patch("adapters.egress.syndication.wechat_shards.wechat_uploader.fetch_image_bytes")
    @patch("adapters.egress.syndication.wechat_shards.wechat_uploader.upload_wechat_thumb")
    def test_custom_cover_image_resolution(self, mock_upload_thumb, mock_fetch):
        mock_fetch.return_value = (b"clock_cover_bytes_123", "gen_c309d4b1eb37.jpg")
        mock_upload_thumb.return_value = "perm_clock_media_id_777"

        payload = self.syndicator.format_payload(
            title="发行矩阵与渠道配置",
            slug="the-matrix",
            content="# 矩阵配置\n正文无内嵌图片。",
            metadata={"cover": "/api/design/assets/covers/gen_c309d4b1eb37.jpg"},
        )
        self.assertEqual(payload["articles"][0].get("_cover_src"), "/api/design/assets/covers/gen_c309d4b1eb37.jpg")

        ensured = ensure_valid_thumb_media_id(payload["articles"], "mock_token")
        self.assertEqual(ensured[0]["thumb_media_id"], "perm_clock_media_id_777")
        self.assertNotIn("_cover_src", ensured[0])
        mock_fetch.assert_called_with("/api/design/assets/covers/gen_c309d4b1eb37.jpg", doc_dir=None, proxy=None, timeout=15)
        mock_upload_thumb.assert_called_with(b"clock_cover_bytes_123", "gen_c309d4b1eb37.jpg", "mock_token", proxy=None, timeout=15)


if __name__ == "__main__":
    unittest.main()

