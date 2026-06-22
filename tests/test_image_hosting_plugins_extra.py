#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V48.3] 图床插件及连接探测测试 (扩展分片)
"""
import os
import sys
import pytest
import tempfile
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath('.'))

from adapters.egress.image_hosting.qiniu_kodo import QiniuKodoImageHost
from adapters.egress.image_hosting.upyun_uss import UpyunUssImageHost
from adapters.egress.image_hosting.loli_io import LoliIoImageHost
from adapters.egress.image_hosting.superbed import SuperbedImageHost
from adapters.egress.image_hosting.lsky_pro import LskyProImageHost

from services.api.routes.gov.context_shards.plugin_ops import dry_run_plugin_impl

class TestImageHostingPluginsExtra:
    """额外图床插件的单元测试"""

    def test_qiniu_kodo_image_host(self) -> None:
        """测试七牛云 Kodo 图床"""
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

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp.write(b"fake qiniu kodo data")
            tmp.flush()

            mock_qiniu = MagicMock()
            mock_auth = MagicMock()
            mock_info = MagicMock()
            mock_info.status_code = 200
            
            with patch.dict(sys.modules, {'qiniu': mock_qiniu}):
                mock_qiniu.Auth.return_value = mock_auth
                mock_qiniu.put_file.return_value = ({"key": "val"}, mock_info)

                url = host.upload(tmp.name)
                assert url is not None
                assert url.startswith("http://img.test.com/images")

    def test_upyun_uss_image_host(self) -> None:
        """测试又拍云 USS 图床"""
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

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp.write(b"fake upyun data")
            tmp.flush()

            with patch("requests.put") as mock_put:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_put.return_value = mock_resp

                url = host.upload(tmp.name)
                assert url is not None
                assert url.startswith("https://img.upyun.com/images")

    def test_loli_io_image_host(self) -> None:
        """测试路过图床"""
        host = LoliIoImageHost(config={
            "token": "token-123",
            "endpoint": "https://img.lol/api/v1/upload"
        })
        assert host.token == "token-123"
        assert host.endpoint == "https://img.lol/api/v1/upload"

        host_no_conf = LoliIoImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp.write(b"fake loli.io data")
            tmp.flush()

            with patch("requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "status": 200,
                    "data": {"url": "https://img.lol/img1.png"}
                }
                mock_post.return_value = mock_resp

                url = host.upload(tmp.name)
                assert url == "https://img.lol/img1.png"

    def test_superbed_image_host(self) -> None:
        """测试聚合图床"""
        host = SuperbedImageHost(config={
            "token": "token-123",
            "endpoint": "https://api.superbed.cn/upload"
        })
        assert host.token == "token-123"
        assert host.endpoint == "https://api.superbed.cn/upload"

        host_no_conf = SuperbedImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp.write(b"fake superbed data")
            tmp.flush()

            with patch("requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "err": 0,
                    "url": "https://p.superbed.cn/img.jpg"
                }
                mock_post.return_value = mock_resp

                url = host.upload(tmp.name)
                assert url == "https://p.superbed.cn/img.jpg"

    def test_lsky_pro_image_host(self) -> None:
        """测试兰空图床"""
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

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp.write(b"fake lsky data")
            tmp.flush()

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

                url = host.upload(tmp.name)
                assert url == "https://lsky.test.com/storage/img.png"

    @pytest.mark.anyio
    async def test_dry_run_image_hosting_plugins(self) -> None:
        """测试 plugin_ops 中的 Dry-Run 自检逻辑"""
        payload_telegraph = {"id": "telegraph", "settings": {"endpoint": "https://telegra.ph"}}
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_get.return_value = mock_resp
            res = await dry_run_plugin_impl(payload_telegraph)
            assert res["success"] is True
            assert any("Telegraph 属于免配授权图床" in log["message"] for log in res["logs"])

        res_oss_fail = await dry_run_plugin_impl({"id": "aliyun_oss", "settings": {"bucket": ""}})
        assert res_oss_fail["success"] is False

        with patch("requests.head") as mock_head:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_head.return_value = mock_resp
            res_oss_ok = await dry_run_plugin_impl({
                "id": "aliyun_oss",
                "settings": {"bucket": "my-bucket", "endpoint": "oss-cn-beijing.aliyuncs.com", "access_key_id": "ak", "access_key_secret": "sk"}
            })
            assert res_oss_ok["success"] is True

        with patch("requests.head") as mock_head:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_head.return_value = mock_resp
            res_cos_ok = await dry_run_plugin_impl({
                "id": "tencent_cos",
                "settings": {"bucket": "my-cos-bucket-12500000", "region": "ap-beijing", "secret_id": "sid", "secret_key": "skey"}
            })
            assert res_cos_ok["success"] is True

        with patch("requests.head") as mock_head:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_head.return_value = mock_resp
            res_kodo_ok = await dry_run_plugin_impl({
                "id": "qiniu_kodo",
                "settings": {"bucket": "my-bucket", "access_key": "ak", "secret_key": "sk", "domain": "http://img.test.com"}
            })
            assert res_kodo_ok["success"] is True

        with patch("requests.head") as mock_head:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_head.return_value = mock_resp
            res_uss_ok = await dry_run_plugin_impl({
                "id": "upyun_uss",
                "settings": {"bucket": "my-bucket", "operator": "op", "password": "pwd", "domain": "img.upyun.com"}
            })
            assert res_uss_ok["success"] is True

        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_get.return_value = mock_resp
            res_loli = await dry_run_plugin_impl({"id": "loli_io", "settings": {"token": "my-token"}})
            assert res_loli["success"] is True

        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_get.return_value = mock_resp
            res_super = await dry_run_plugin_impl({"id": "superbed", "settings": {"token": "my-token"}})
            assert res_super["success"] is True

        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_get.return_value = mock_resp
            res_lsky = await dry_run_plugin_impl({
                "id": "lsky_pro",
                "settings": {"endpoint": "https://lsky.test.com", "token": "my-token"}
            })
            assert res_lsky["success"] is True
