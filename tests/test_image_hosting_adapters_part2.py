#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V48.3] 图床插件单元测试（第二部分）
🛡️ [V88.0 Split] 从 test_image_hosting_plugins.py 物理克隆搬迁并进行二次拆分。
"""
import os
import sys
import contextlib
import tempfile
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath('.'))

from adapters.egress.image_hosting.qiniu_kodo import QiniuKodoImageHost
from adapters.egress.image_hosting.upyun_uss import UpyunUssImageHost
from adapters.egress.image_hosting.loli_io import LoliIoImageHost
from adapters.egress.image_hosting.superbed import SuperbedImageHost
from adapters.egress.image_hosting.lsky_pro import LskyProImageHost


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


class TestImageHostingPluginsPart2(BaseImageHostTest):
    """图床插件第二部分单元测试套件"""

    def test_qiniu_kodo_image_host(self) -> None:
        host = QiniuKodoImageHost(config={
            "bucket": "test-bucket",
            "access_key": "ak",
            "secret_key": "sk",
            "domain": "http://img.test.com",
            "path": "images"
        })
        assert host.bucket == "test-bucket"
        assert host.access_key == "ak"
        assert host.secret_key == "sk"
        assert host.domain == "http://img.test.com"

        host_no_conf = QiniuKodoImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with self._temp_image() as img_path:
            mock_qiniu = MagicMock()
            mock_auth = MagicMock()
            mock_info = MagicMock()
            mock_info.status_code = 200
            
            with patch.dict(sys.modules, {'qiniu': mock_qiniu}):
                mock_qiniu.Auth.return_value = mock_auth
                mock_qiniu.put_file.return_value = ({"key": "val"}, mock_info)

                url = host.upload(img_path)
                assert url is not None
                assert url.startswith("http://img.test.com/images")

    def test_upyun_uss_image_host(self) -> None:
        host = UpyunUssImageHost(config={
            "bucket": "test-bucket",
            "operator": "op",
            "password": "pwd",
            "path": "images",
            "domain": "https://img.upyun.com"
        })
        assert host.bucket == "test-bucket"
        assert host.operator == "op"
        assert host.password == "pwd"
        assert host.domain == "https://img.upyun.com"

        host_no_conf = UpyunUssImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with self._temp_image() as img_path:
            with patch("requests.put") as mock_put:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_put.return_value = mock_resp

                url = host.upload(img_path)
                assert url is not None
                assert url.startswith("https://img.upyun.com/images")

    def test_loli_io_image_host(self) -> None:
        host = LoliIoImageHost(config={
            "token": "token-123",
            "endpoint": "https://img.lol/api/v1/upload"
        })
        assert host.token == "token-123"
        assert host.endpoint == "https://img.lol/api/v1/upload"

        host_no_conf = LoliIoImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with self._temp_image() as img_path:
            with patch("requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "status": 200,
                    "data": {"url": "https://img.lol/img1.png"}
                }
                mock_post.return_value = mock_resp

                url = host.upload(img_path)
                assert url == "https://img.lol/img1.png"

    def test_superbed_image_host(self) -> None:
        host = SuperbedImageHost(config={
            "token": "token-123",
            "endpoint": "https://api.superbed.cn/upload"
        })
        assert host.token == "token-123"
        assert host.endpoint == "https://api.superbed.cn/upload"

        host_no_conf = SuperbedImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with self._temp_image() as img_path:
            with patch("requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "err": 0,
                    "url": "https://p.superbed.cn/img.jpg"
                }
                mock_post.return_value = mock_resp

                url = host.upload(img_path)
                assert url == "https://p.superbed.cn/img.jpg"

    def test_lsky_pro_image_host(self) -> None:
        host = LskyProImageHost(config={
            "endpoint": "https://lsky.test.com",
            "token": "my-token",
            "strategy_id": "1",
            "album_id": "2"
        })
        assert host.endpoint == "https://lsky.test.com"
        assert host.token == "my-token"
        assert host.strategy_id == "1"
        assert host.album_id == "2"

        host_no_conf = LskyProImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with self._temp_image() as img_path:
            with patch("requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "status": True,
                    "data": {
                        "links": {"url": "https://lsky.test.com/storage/img.png"}
                    }
                }
                mock_post.return_value = mock_resp

                url = host.upload(img_path)
                assert url == "https://lsky.test.com/storage/img.png"
