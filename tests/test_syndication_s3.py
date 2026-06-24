#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V76.0] S3 Publisher 适配器单元测试
🛡️ [V88.0 Split] 从 test_syndication_plugins.py 物理克隆搬迁。
"""
import os
import sys
import tempfile
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath("."))


class TestS3Publisher:
    """S3 Publisher 适配器单元测试"""

    def _make_config(self, **kwargs) -> dict:
        return {
            "enabled": kwargs.get("enabled", True),
            "bucket": kwargs.get("bucket", "my-test-bucket"),
            "region": kwargs.get("region", "us-east-1"),
            "access_key": kwargs.get("access_key", "test-access-key"),
            "secret_key": kwargs.get("secret_key", "test-secret-key"),
            "prefix": kwargs.get("prefix", ""),
            "endpoint_url": kwargs.get("endpoint_url", ""),
            "public_url": kwargs.get("public_url", ""),
            "acl": kwargs.get("acl", ""),
        }

    def test_import_and_instantiate(self):
        """验证 S3Publisher 可正常导入和实例化"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config())
        assert pub.PLUGIN_ID == "s3"
        assert pub.bucket == "my-test-bucket"
        assert pub.region == "us-east-1"

    def test_validate_config_all_valid(self):
        """完整配置应通过校验"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config())
        assert pub.validate_config() == []

    def test_validate_config_missing_bucket(self):
        """缺少 bucket 时校验应失败"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(bucket=""))
        errors = pub.validate_config()
        assert any("bucket" in e for e in errors)

    def test_validate_config_missing_access_key(self):
        """缺少 access_key 时校验应失败"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(access_key=""))
        errors = pub.validate_config()
        assert any("access_key" in e for e in errors)

    def test_validate_config_missing_secret_key(self):
        """缺少 secret_key 时校验应失败"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(secret_key=""))
        errors = pub.validate_config()
        assert any("secret_key" in e for e in errors)

    def test_push_skips_when_config_incomplete(self):
        """配置不完整时 push 应跳过"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(bucket=""))
        result = pub.push("/tmp/fake_bundle", {})
        assert result["status"] == "skipped"

    def test_push_errors_when_bundle_missing(self):
        """bundle_path 不存在时 push 应返回 error"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config())
        result = pub.push("/nonexistent/path/for/testing", {})
        assert result["status"] in ("error", "skipped")

    def test_get_deploy_url_with_public_url(self):
        """配置了 public_url 时应优先使用"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(public_url="https://cdn.example.com"))
        assert pub.get_deploy_url() == "https://cdn.example.com"

    def test_get_deploy_url_aws_default(self):
        """未配置 public_url 时推导 AWS S3 静态托管 URL"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(bucket="my-docs", region="ap-east-1"))
        url = pub.get_deploy_url()
        assert url is not None
        assert "my-docs" in url
        assert "ap-east-1" in url

    def test_get_deploy_url_none_for_custom_endpoint(self):
        """自定义 endpoint（R2/OSS）时 get_deploy_url 应返回 None"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(endpoint_url="https://r2.cloudflarestorage.com"))
        assert pub.get_deploy_url() is None

    def test_mime_type_mapping_completeness(self):
        """验证 MIME 类型映射覆盖主要静态资源格式"""
        from adapters.egress.publishers.s3 import _get_content_type
        assert "text/html" in _get_content_type("index.html")
        assert "text/css" in _get_content_type("style.css")
        assert "javascript" in _get_content_type("app.js")
        assert "image/webp" in _get_content_type("photo.webp")
        assert "image/png" in _get_content_type("logo.png")
        assert "image/svg" in _get_content_type("icon.svg")
        assert "font/woff2" in _get_content_type("font.woff2")
        assert "application/json" in _get_content_type("data.json")
        assert "octet-stream" in _get_content_type("binary.xyz")

    @patch("boto3.client")
    def test_push_success_full_upload(self, mock_boto_client):
        """模拟 boto3 全量上传成功"""
        from adapters.egress.publishers.s3 import S3Publisher

        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        with tempfile.TemporaryDirectory() as bundle_dir:
            with open(os.path.join(bundle_dir, "index.html"), "w") as f:
                f.write("<html>test</html>")
            os.makedirs(os.path.join(bundle_dir, "assets"))
            with open(os.path.join(bundle_dir, "assets", "style.css"), "w") as f:
                f.write("body { margin: 0; }")
            with open(os.path.join(bundle_dir, ".DS_Store"), "w") as f:
                f.write("")

            pub = S3Publisher(config=self._make_config(bucket="docs-bucket"))
            result = pub.push(bundle_dir, {})

        assert result["status"] == "success"
        assert result["files"] == 2
        assert mock_s3.upload_file.call_count == 2

    @patch("boto3.client")
    def test_push_with_prefix(self, mock_boto_client):
        """验证 prefix 被正确拼接到 S3 路径"""
        from adapters.egress.publishers.s3 import S3Publisher

        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        with tempfile.TemporaryDirectory() as bundle_dir:
            with open(os.path.join(bundle_dir, "index.html"), "w") as f:
                f.write("<html></html>")

            pub = S3Publisher(config=self._make_config(prefix="v2/docs"))
            pub.push(bundle_dir, {})

        upload_calls = mock_s3.upload_file.call_args_list
        assert len(upload_calls) == 1
        s3_key = upload_calls[0][0][2]
        assert s3_key.startswith("v2/docs/")

    def test_inherits_base_publisher(self):
        """验证正确继承 BasePublisher"""
        from adapters.egress.publishers.s3 import S3Publisher
        from core.adapters.egress.publishers.base import BasePublisher
        assert issubclass(S3Publisher, BasePublisher)
