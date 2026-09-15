#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - WeChat Preflight and Image Compression Test Suite
测试职责：验证微信发布前防呆预检（标题/作者/摘要硬限截断）与内存级图片等比压缩防线。
严格遵守用户规则 10（不修改真实配置与文库）与规则 11（严密凭证闭环）。
"""

import io
import unittest
from PIL import Image
from adapters.egress.syndication.wechat import WeChatSyndicator
from adapters.egress.syndication.wechat_shards.wechat_image_optimizer import optimize_image_for_wechat

class TestWeChatPreflightAndCompression(unittest.TestCase):

    def setUp(self):
        self.valid_config = {
            "enabled": True,
            "app_id": "wx_mock_app_123",
            "app_secret": "wx_mock_secret_456",
            "author": "PlenipesCore"
        }
        self.syndicator = WeChatSyndicator(self.valid_config)

    def test_preflight_missing_credentials(self):
        bad_syndicator = WeChatSyndicator({"enabled": True})
        res = bad_syndicator.validate_preflight("测试标题", "测试正文", {})
        self.assertFalse(res["valid"])
        self.assertTrue(any("未配置 AppID" in e for e in res["errors"]))

    def test_preflight_title_truncation(self):
        # 微信标题硬限制 32 字符
        long_title = "这是一个超级超级超级长长长长长长长长长长长长长长长长长长长长长长长的文章标题，绝对超过了三十二个字"
        self.assertGreater(len(long_title), 32)

        res = self.syndicator.validate_preflight(long_title, "这是文章的正文内容", {})
        self.assertTrue(res["valid"])
        self.assertEqual(len(res["sanitized"]["title"]), 32)
        self.assertTrue(any("超过微信官方 32 字符" in w for w in res["warnings"]))

    def test_preflight_author_truncation(self):
        # 微信作者限制 8 字符
        long_author_meta = {"author": "超级技术专家全栈架构师"}
        res = self.syndicator.validate_preflight("合规标题", "文章正文", long_author_meta)
        self.assertTrue(res["valid"])
        self.assertEqual(len(res["sanitized"]["metadata"]["author"]), 8)
        self.assertTrue(any("超过微信 8 字符上限" in w for w in res["warnings"]))

    def test_image_compression_under_limit_returns_original(self):
        # 小于 2MB 的小图不压缩，原样返回
        buf = io.BytesIO()
        img = Image.new("RGB", (200, 200), color=(100, 150, 200))
        img.save(buf, format="JPEG", quality=80)
        orig_bytes = buf.getvalue()

        compressed_bytes, fn = optimize_image_for_wechat(orig_bytes, "small_pic.jpg", max_size_bytes=2 * 1024 * 1024)
        self.assertEqual(len(compressed_bytes), len(orig_bytes))
        self.assertEqual(compressed_bytes, orig_bytes)

    def test_image_compression_oversized_downsamples_under_2mb(self):
        # 动态创建一张分辨率 3000x2500 且体积 > 2MB 的大图
        buf = io.BytesIO()
        img = Image.new("RGBA", (3200, 2400), color=(255, 120, 50, 255))
        # 写入随机杂色防止 JPEG 压缩率过高，确保体积膨胀
        import os
        noise_bytes = os.urandom(3200 * 2400)
        noise_img = Image.frombytes("L", (3200, 2400), noise_bytes)
        img.paste(noise_img, (0, 0))
        img.save(buf, format="PNG") # PNG 体积通常大于 3MB
        raw_big_bytes = buf.getvalue()
        
        # 确保原始体积确实超过了 2MB
        max_limit = 2 * 1024 * 1024 # 2MB
        if len(raw_big_bytes) < max_limit:
            # 如测试环境较快压缩，强行填充
            raw_big_bytes = raw_big_bytes + (b"\x00" * (max_limit + 1024))

        # 执行自愈等比压缩
        comp_bytes, comp_fn = optimize_image_for_wechat(raw_big_bytes, "huge_artwork.png", max_size_bytes=max_limit)
        
        # 断言输出体积被严格压缩至 2MB 阈值之内
        self.assertLessEqual(len(comp_bytes), max_limit)
        self.assertGreater(len(comp_bytes), 0)

        # 断言压缩后的图片依然是可读取的合法图片
        comp_img = Image.open(io.BytesIO(comp_bytes))
        self.assertIn(comp_img.format, ("JPEG", "PNG"))
        self.assertLessEqual(max(comp_img.size), 1920)

if __name__ == "__main__":
    unittest.main()
