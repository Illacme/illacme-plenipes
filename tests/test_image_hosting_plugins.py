#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V48.3] 新增图床插件及连接探测测试 (全量扩充)
"""
import os
import sys
import pytest
import tempfile
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath('.'))

from adapters.egress.image_hosting.github import GitHubImageHost
from adapters.egress.image_hosting.sm_ms import SmMsImageHost
from adapters.egress.image_hosting.imgur import ImgurImageHost
from adapters.egress.image_hosting.telegraph import TelegraphImageHost

from adapters.egress.image_hosting.aliyun_oss import AliyunOssImageHost
from adapters.egress.image_hosting.tencent_cos import TencentCosImageHost

from services.api.routes.gov.context_shards.plugin_ops import probe_plugin_impl

class TestImageHostingPlugins:
    """所有图床插件的单元测试"""

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

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp.write(b"fake image data")
            tmp.flush()

            with patch("requests.put") as mock_put:
                mock_resp = MagicMock()
                mock_resp.status_code = 201
                mock_put.return_value = mock_resp

                url = host.upload(tmp.name)
                assert url is not None
                assert "images/" in url
                assert url.startswith("https://cdn.my.com")

    def test_sm_ms_image_host(self):
        host = SmMsImageHost(config={"token": "token-123"})
        assert host.token == "token-123"

        host_no_conf = SmMsImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp.write(b"fake sm.ms data")
            tmp.flush()

            with patch("requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "success": True,
                    "data": {"url": "https://sm.ms/img.png"}
                }
                mock_post.return_value = mock_resp

                url = host.upload(tmp.name)
                assert url == "https://sm.ms/img.png"

    def test_imgur_image_host(self):
        host = ImgurImageHost(config={"client_id": "client-123", "token": "token-123"})
        assert host.client_id == "client-123"
        assert host.token == "token-123"

        host_no_conf = ImgurImageHost(config={})
        assert host_no_conf.upload("fake_path") is None

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp.write(b"fake imgur data")
            tmp.flush()

            with patch("requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "success": True,
                    "data": {"link": "https://imgur.com/img.png"}
                }
                mock_post.return_value = mock_resp

                url = host.upload(tmp.name)
                assert url == "https://imgur.com/img.png"

    def test_telegraph_image_host(self):
        host = TelegraphImageHost(config={"endpoint": "https://telegra.ph"})
        assert host.endpoint == "https://telegra.ph"

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp.write(b"fake telegraph data")
            tmp.flush()

            with patch("requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = [{"src": "/file/img.png"}]
                mock_post.return_value = mock_resp

                url = host.upload(tmp.name)
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

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp.write(b"fake aliyun oss data")
            tmp.flush()

            # 模拟 oss2 模块存在及上传成功
            mock_oss2 = MagicMock()
            mock_auth = MagicMock()
            mock_bucket = MagicMock()
            
            with patch.dict(sys.modules, {'oss2': mock_oss2}):
                mock_oss2.Auth.return_value = mock_auth
                mock_oss2.Bucket.return_value = mock_bucket

                url = host.upload(tmp.name)
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

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp.write(b"fake tencent cos data")
            tmp.flush()

            mock_cos = MagicMock()
            with patch.dict(sys.modules, {'qcloud_cos': mock_cos}):
                url = host.upload(tmp.name)
                assert url is not None
                assert url.startswith("https://cdn.cos.com/images")



    @pytest.mark.anyio
    async def test_probe_image_hosting_plugins(self):
        """测试 plugin_ops 中的健康探测逻辑对图床的感应"""
        mock_engine = MagicMock()
        mock_engine.config.image_hosting = {"provider": "telegraph"}
        
        with patch("services.api.routes.gov.context_shards.plugin_ops.get_global_engine", return_value=mock_engine):
            for provider_id in ["telegraph", "aliyun_oss", "tencent_cos", "qiniu_kodo", "upyun_uss", "loli_io", "superbed", "lsky_pro"]:
                res = await probe_plugin_impl({"id": provider_id})
                assert res["success"] is True
                assert res["healthy"] is True
                assert "图床驱动已挂载" in res["message"]



    @pytest.mark.anyio
    async def test_install_plugin_deps(self):
        """测试一键安装依赖包接口"""
        from services.api.routes.gov.context_shards.plugin_ops import install_plugin_deps_impl
        
        # 1. 缺失 ID
        res_fail = await install_plugin_deps_impl({})
        assert res_fail["success"] is False
        assert "Plugin ID" in res_fail["error"]

        # 2. 不需要外部依赖的插件
        res_none = await install_plugin_deps_impl({"id": "telegraph"})
        assert res_none["success"] is True
        assert "不需要外部" in res_none["logs"][0]["message"]

        # 3. 模拟 pip 成功安装
        with patch("subprocess.run") as mock_run:
            mock_res = MagicMock()
            mock_res.returncode = 0
            mock_res.stdout = "Successfully installed"
            mock_res.stderr = ""
            mock_run.return_value = mock_res

            res_ok = await install_plugin_deps_impl({"id": "aliyun_oss"})
            assert res_ok["success"] is True
            assert any("成功安装" in log["message"] for log in res_ok["logs"])

        # 4. 模拟 pip 安装失败
        with patch("subprocess.run") as mock_run:
            mock_res = MagicMock()
            mock_res.returncode = 1
            mock_res.stdout = ""
            mock_res.stderr = "Connection error"
            mock_run.return_value = mock_res

            res_fail = await install_plugin_deps_impl({"id": "aliyun_oss"})
            assert res_fail["success"] is False
            assert any("安装失败" in log["message"] for log in res_fail["logs"])
