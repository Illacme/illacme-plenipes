# -*- coding: utf-8 -*-
"""
🧪 [Test] 多态封面自适应派生与全渠道分发联动测试套件
验证各渠道标准画幅画像映射、焦点智能裁切、物理派生文件生成与推流装配。
"""
import os
import io
import unittest
from unittest.mock import MagicMock, patch
from PIL import Image

from core.design.cover_engine.cover_deriver import (
    get_channel_aspect_ratio,
    crop_image_bytes,
    derive_cover_asset,
    CHANNEL_ASPECT_MAP,
    DIMENSION_MAP
)


class TestPolymorphicCoverDerivation(unittest.TestCase):

    def setUp(self):
        # 构造一张 16:9 测试图片 (1200x675)
        self.test_img = Image.new("RGB", (1200, 675), color=(40, 80, 120))
        buf = io.BytesIO()
        self.test_img.save(buf, format="JPEG")
        self.test_img_bytes = buf.getvalue()

    def test_channel_aspect_mapping(self):
        """验证各核心渠道官方标准画幅映射"""
        self.assertEqual(get_channel_aspect_ratio("wechat"), "2.35:1")
        self.assertEqual(get_channel_aspect_ratio("xiaohongshu"), "3:4")
        self.assertEqual(get_channel_aspect_ratio("rednote"), "3:4")
        self.assertEqual(get_channel_aspect_ratio("devto"), "16:9")
        self.assertEqual(get_channel_aspect_ratio("zhihu"), "16:9")
        self.assertEqual(get_channel_aspect_ratio("unknown_channel"), "16:9")

    def test_crop_image_aspect_and_focal(self):
        """验证基于 focal_y 焦点裁切后图像的标准几何分辨率"""
        # 1. 微信 2.35:1 裁切
        wechat_bytes = crop_image_bytes(self.test_img_bytes, "2.35:1", focal_y=0.2)
        self.assertIsNotNone(wechat_bytes)
        w_img = Image.open(io.BytesIO(wechat_bytes))
        self.assertEqual(w_img.size, DIMENSION_MAP["2.35:1"])

        # 2. 小红书 3:4 裁切 (带 zoom 放大 1.4 倍)
        xhs_bytes = crop_image_bytes(self.test_img_bytes, "3:4", focal_x=0.7, focal_y=0.8, zoom=1.4)
        self.assertIsNotNone(xhs_bytes)
        x_img = Image.open(io.BytesIO(xhs_bytes))
        self.assertEqual(x_img.size, DIMENSION_MAP["3:4"])

    def test_derive_cover_asset_caching(self):
        """验证物理派生产物落盘与 URL 索引生成"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_vault:
            # 写入本地原图
            src_path = os.path.join(tmp_vault, "cover.jpg")
            with open(src_path, "wb") as f:
                f.write(self.test_img_bytes)

            rel_url, d_bytes = derive_cover_asset(
                source_cover=src_path,
                target_ratio="2.35:1",
                focal_y=0.4,
                vault_root=tmp_vault
            )
            self.assertIsNotNone(rel_url)
            self.assertIsNotNone(d_bytes)
            self.assertTrue(rel_url.startswith("/api/design/assets/covers/derived_"))
            self.assertIn("2.35x1", rel_url)

            # 验证磁盘物理文件存在
            cache_file = os.path.join(tmp_vault, ".plenipes", "cache", "covers", os.path.basename(rel_url))
            self.assertTrue(os.path.isfile(cache_file))

    def test_pipeline_task_runner_with_overrides(self):
        """验证 pipeline_task_runner 接收 target_channel 与 overrides 时装配专属派生封面"""
        from services.api.logic.dispatch_ops_shards.pipeline_shards.pipeline_task_runner import _async_redispatch_task
        mock_engine = MagicMock()
        mock_engine.vault_root = "/mock/vault"
        mock_engine.meta.get_doc_info.return_value = {"title": "Test Doc", "slug": "test-doc"}
        mock_engine.config.publish_control.direct_upload = {}
        mock_engine.config.syndication = {"wechat": {"enabled": True}}

        # 测试渠道专属 override_url
        with patch("services.api.logic.dispatch_ops_shards.pipeline_shards.pipeline_task_runner.get_enabled_syndication_channels", return_value=[("wechat", {})]), \
             patch("services.api.logic.dispatch_ops_shards.pipeline_shards.pipeline_task_runner.load_syndication_content_and_metadata", return_value=("Test", "Body", {"cover": "http://example.com/master.jpg"})), \
             patch("core.syndication.hub.ContentSyndicator.syndicate") as mock_syndicate:

            _async_redispatch_task(
                engine=mock_engine,
                task_path="/mock/test.md",
                prefix="",
                src_rel="test.md",
                target_slot="zh",
                clear_cache=False,
                doc_id="test.md",
                target_channel="wechat",
                skip_syndication=False,
                cover_overrides={"wechat": {"override_url": "http://example.com/wechat_override.jpg"}}
            )
            self.assertTrue(mock_syndicate.called)
            called_meta = mock_syndicate.call_args[1]["metadata"]
            self.assertEqual(called_meta["cover"], "http://example.com/wechat_override.jpg")

        # 测试自动派生微信 2.35:1 封面并传递
        with patch("services.api.logic.dispatch_ops_shards.pipeline_shards.pipeline_task_runner.get_enabled_syndication_channels", return_value=[("wechat", {})]), \
             patch("services.api.logic.dispatch_ops_shards.pipeline_shards.pipeline_task_runner.load_syndication_content_and_metadata", return_value=("Test", "Body", {"cover": "http://example.com/master.jpg"})), \
             patch("core.design.cover_engine.cover_deriver.derive_cover_asset", return_value=("/api/design/assets/covers/derived_123_2.35x1.jpg", b"fake_bytes")), \
             patch("core.syndication.hub.ContentSyndicator.syndicate") as mock_syndicate:

            _async_redispatch_task(
                engine=mock_engine,
                task_path="/mock/test.md",
                prefix="",
                src_rel="test.md",
                target_slot="zh",
                clear_cache=False,
                doc_id="test.md",
                target_channel="wechat",
                skip_syndication=False,
                cover_overrides={"wechat": {"focal_y": 0.3}}
            )
            self.assertTrue(mock_syndicate.called)
            called_meta = mock_syndicate.call_args[1]["metadata"]
            self.assertEqual(called_meta["cover"], "/api/design/assets/covers/derived_123_2.35x1.jpg")


if __name__ == "__main__":
    unittest.main()
