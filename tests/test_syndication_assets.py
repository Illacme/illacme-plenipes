# -*- coding: utf-8 -*-
"""
🧪 [Test] 自动图床与 Markdown AST 规范化单元测试
"""
import os
import shutil
import unittest
import tempfile
from unittest.mock import patch, MagicMock

from core.editorial.ast_processor import MarkdownASTProcessor
from core.syndication.hub import ContentSyndicator

class TestSyndicationAssets(unittest.TestCase):
    def setUp(self):
        # 创建临时笔记库目录
        self.test_dir = tempfile.mkdtemp()
        self.doc_dir = os.path.join(self.test_dir, "posts")
        os.makedirs(self.doc_dir, exist_ok=True)
        
        # 创建一个虚拟的本地图片文件
        self.image_path = os.path.join(self.test_dir, "assets", "test_pic.png")
        os.makedirs(os.path.dirname(self.image_path), exist_ok=True)
        with open(self.image_path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01") # 虚拟PNG文件

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_ast_processor_image_replacement(self):
        processor = MarkdownASTProcessor()
        content = "这是一个测试文稿。\n![配图](../assets/test_pic.png)\n还有 HTML 图片：<img src=\"../assets/test_pic.png\" alt=\"html_img\">"
        
        # 模拟上传回调函数
        def mock_upload(abs_path):
            self.assertTrue(os.path.isabs(abs_path))
            self.assertTrue(abs_path.endswith("test_pic.png"))
            return "https://cdn.mock.com/test_pic.png"

        result = processor.process_images(content, self.doc_dir, mock_upload)
        self.assertIn("![配图](https://cdn.mock.com/test_pic.png)", result)
        self.assertIn("<img src=\"https://cdn.mock.com/test_pic.png\" alt=\"html_img\">", result)

    def test_ast_processor_header_adaptation(self):
        processor = MarkdownASTProcessor()
        content = "# H1 标题\n## H2 子标题\n### H3 三级标题\n普通正文内容。"
        
        # 测试 Medium 标题降级
        medium_result = processor.adapt_format(content, "medium")
        self.assertIn("### H1 标题", medium_result)
        self.assertIn("### H2 子标题", medium_result)
        self.assertIn("### H3 三级标题", medium_result)
        lines = medium_result.splitlines()
        self.assertTrue(lines[0].startswith("### H1"))
        self.assertTrue(lines[1].startswith("### H2"))
        
        # 测试非 Medium 平台不降级
        devto_result = processor.adapt_format(content, "devto")
        self.assertIn("# H1 标题", devto_result)
        self.assertIn("## H2 子标题", devto_result)

    @patch("boto3.client")
    def test_syndicator_image_upload_flow(self, mock_boto_client):
        # 模拟 S3 客户端行为
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        # 构造带有 S3 图床配置 of syndicator
        syndication_cfg = {
            "mock_platform": {
                "enabled": True,
                "platform": "mock_platform"
            }
        }
        sys_tuning = {
            "vault_root": self.test_dir,
            "publish_control": {
                "direct_upload": {
                    "s3": {
                        "enabled": True,
                        "bucket": "test-bucket",
                        "access_key": "fake-access-key",
                        "secret_key": "fake-secret-key",
                        "region": "ap-east-1",
                        "public_url": "https://cdn.my-images.com"
                    }
                }
            }
        }
        
        syndicator = ContentSyndicator(
            syndication_cfg=syndication_cfg,
            site_url="https://example.com",
            sys_tuning_cfg=sys_tuning,
            meta=None
        )

        content = "文章内容：![图片](../assets/test_pic.png)"
        
        # 动态测试 S3 上传流
        from core.syndication.uploader import ImageUploader
        uploader = ImageUploader(syndicator.cfg, syndicator.sys_tuning)
        
        # 校验图床插件已被动态自发现和挂载
        self.assertIsNotNone(uploader.host_instance)
        self.assertEqual(uploader.host_instance.PLUGIN_ID, "s3")

        processor = MarkdownASTProcessor()
        result_content = processor.process_images(
            content,
            self.doc_dir,
            uploader.upload_image
        )
        
        # 校验 boto3 被正确调用
        mock_s3.upload_file.assert_called_once()
        
        # 校验 CDN URL 链接已被成功替换
        self.assertIn("https://cdn.my-images.com/cdn/images/", result_content)
        self.assertIn("test_pic_", result_content)

    @patch("boto3.client")
    def test_syndicator_image_upload_flow_style_b(self, mock_boto_client):
        # 模拟 S3 客户端行为
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        # 构造带有 Style B 新版图床配置的 syndicator
        syndication_cfg = {
            "mock_platform": {
                "enabled": True,
                "platform": "mock_platform"
            }
        }
        sys_tuning = {
            "vault_root": self.test_dir,
            "image_hosting": {
                "s3": {
                    "enabled": True,
                    "bucket": "style-b-bucket",
                    "access_key": "style-b-access-key",
                    "secret_key": "style-b-secret-key",
                    "region": "ap-southeast-1",
                    "public_url": "https://cdn.style-b.com"
                }
            }
        }
        
        syndicator = ContentSyndicator(
            syndication_cfg=syndication_cfg,
            site_url="https://example.com",
            sys_tuning_cfg=sys_tuning,
            meta=None
        )

        content = "文章内容：![图片](../assets/test_pic.png)"
        
        # 动态测试 S3 上传流
        from core.syndication.uploader import ImageUploader
        uploader = ImageUploader(syndicator.cfg, syndicator.sys_tuning)
        
        # 校验图床插件已被动态自发现和挂载
        self.assertIsNotNone(uploader.host_instance)
        self.assertEqual(uploader.host_instance.PLUGIN_ID, "s3")

        processor = MarkdownASTProcessor()
        result_content = processor.process_images(
            content,
            self.doc_dir,
            uploader.upload_image
        )
        
        # 校验 boto3 被正确调用
        mock_s3.upload_file.assert_called_once()
        
        # 校验 CDN URL 链接已被成功替换
        self.assertIn("https://cdn.style-b.com/cdn/images/", result_content)
        self.assertIn("test_pic_", result_content)

if __name__ == "__main__":
    unittest.main()
