#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V48.3] 图床插件单元测试（第一部分）
🛡️ [V88.0 Split] 从 test_image_hosting_plugins.py 物理克隆搬迁并进行二次拆分。
"""
import os
import sys
import pytest
import contextlib
import tempfile
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath('.'))

from adapters.egress.image_hosting.github import GitHubImageHost
from adapters.egress.image_hosting.sm_ms import SmMsImageHost
from adapters.egress.image_hosting.imgur import ImgurImageHost
from adapters.egress.image_hosting.telegraph import TelegraphImageHost
from adapters.egress.image_hosting.aliyun_oss import AliyunOssImageHost
from adapters.egress.image_hosting.tencent_cos import TencentCosImageHost


class BaseImageHostTest:
    """图床单元测试共享基类，提供安全的临时测试图片资源生命周期管理"""

    @contextlib.contextmanager
    def _temp_image(self, content: bytes = b"fake image data"):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(content)
            tmp.close()
            try:
                yield tmp.name
            finally:
                if os.path.exists(tmp.name):
                    try:
                        os.remove(tmp.name)
                    except Exception:
                        pass


class TestImageHostingPluginsPart1(BaseImageHostTest):
    """图床插件第一部分单元测试套件"""

    def test_github_image_host(self):
        host = GitHubImageHost(config={
            "repo": "owner/repo",
            "branch": "main",
            "token": "token-123",
            "path": "images",
            "cdn_url": "https://cdn.my.com"
        })
        assert host.repo == "owner/repo"
        assert host.branch == "main"
        assert host.token == "token-123"
        assert host.path == "images"
        assert host.cdn_url == "https://cdn.my.com"

        host_no_conf = GitHubImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        host_valid = GitHubImageHost(config={"repo": "owner/repo", "token": "token-123"})
        assert host_valid.upload("/nonexistent/file.png") is None

        with self._temp_image() as img_path:
            with patch("requests.put") as mock_put:
                mock_resp = MagicMock()
                mock_resp.status_code = 201
                mock_put.return_value = mock_resp

                url = host.upload(img_path)
                assert url is not None
                assert "images/" in url
                assert url.startswith("https://cdn.my.com")

    def test_sm_ms_image_host(self):
        host = SmMsImageHost(config={"token": "token-123"})
        assert host.token == "token-123"

        host_no_conf = SmMsImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with self._temp_image() as img_path:
            with patch("requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "success": True,
                    "data": {"url": "https://sm.ms/img.png"}
                }
                mock_post.return_value = mock_resp

                url = host.upload(img_path)
                assert url == "https://sm.ms/img.png"

    def test_imgur_image_host(self):
        host = ImgurImageHost(config={"client_id": "client-123", "token": "token-123"})
        assert host.client_id == "client-123"
        assert host.token == "token-123"

        host_no_conf = ImgurImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with self._temp_image() as img_path:
            with patch("requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "success": True,
                    "data": {"link": "https://imgur.com/img.png"}
                }
                mock_post.return_value = mock_resp

                url = host.upload(img_path)
                assert url == "https://imgur.com/img.png"

    def test_telegraph_image_host(self):
        host = TelegraphImageHost(config={"endpoint": "https://telegra.ph"})
        assert host.endpoint == "https://telegra.ph"

        with self._temp_image() as img_path:
            with patch("requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = [{"src": "/file/img.png"}]
                mock_post.return_value = mock_resp

                url = host.upload(img_path)
                assert url == "https://telegra.ph/file/img.png"

    def test_aliyun_oss_image_host(self):
        host = AliyunOssImageHost(config={
            "bucket": "test-bucket",
            "endpoint": "oss-cn-beijing.aliyuncs.com",
            "access_key_id": "ak",
            "access_key_secret": "sk",
            "path": "images",
            "cdn_url": "https://cdn.oss.com"
        })
        assert host.bucket_name == "test-bucket"
        assert host.endpoint == "oss-cn-beijing.aliyuncs.com"
        assert host.access_key_id == "ak"
        assert host.access_key_secret == "sk"
        assert host.path == "images"
        assert host.cdn_url == "https://cdn.oss.com"

        host_no_conf = AliyunOssImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with self._temp_image() as img_path:
            mock_oss2 = MagicMock()
            mock_auth = MagicMock()
            mock_bucket = MagicMock()
            
            with patch.dict(sys.modules, {'oss2': mock_oss2}):
                mock_oss2.Auth.return_value = mock_auth
                mock_oss2.Bucket.return_value = mock_bucket

                url = host.upload(img_path)
                assert url is not None
                assert url.startswith("https://cdn.oss.com/images")

    def test_tencent_cos_image_host(self):
        host = TencentCosImageHost(config={
            "bucket": "test-bucket-125000000",
            "region": "ap-beijing",
            "secret_id": "sid",
            "secret_key": "skey",
            "path": "images",
            "cdn_url": "https://cdn.cos.com"
        })
        assert host.bucket == "test-bucket-125000000"
        assert host.region == "ap-beijing"
        assert host.secret_id == "sid"
        assert host.secret_key == "skey"

        host_no_conf = TencentCosImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with self._temp_image() as img_path:
            mock_cos = MagicMock()
            with patch.dict(sys.modules, {'qcloud_cos': mock_cos}):
                url = host.upload(img_path)
                assert url is not None
                assert url.startswith("https://cdn.cos.com/images")
