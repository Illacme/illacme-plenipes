#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V76.0] S3 图床适配器单元测试
"""
import os
import sys

sys.path.insert(0, os.path.abspath("."))


class TestS3ImageHost:
    """S3 ImageHost 适配器单元测试"""

    def _make_config(self, **kwargs) -> dict:
        return {
            "enabled": kwargs.get("enabled", True),
            "bucket": kwargs.get("bucket", "my-test-bucket"),
            "region": kwargs.get("region", "us-east-1"),
            "access_key_id": kwargs.get("access_key_id", "test-access-key"),
            "secret_access_key": kwargs.get("secret_access_key", "test-secret-key"),
            "prefix": kwargs.get("prefix", ""),
            "endpoint_url": kwargs.get("endpoint_url", ""),
            "cdn_url": kwargs.get("cdn_url", ""),
        }

    def test_import_and_instantiate(self):
        """验证 S3ImageHost 可正常导入和实例化"""
        from adapters.egress.image_hosting.s3 import S3ImageHost
        host = S3ImageHost(config=self._make_config())
        assert host.PLUGIN_ID == "s3"
        assert host.bucket == "my-test-bucket"
        assert host.region == "us-east-1"
