#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V48.3] 图床插件单元测试与连接探测（已合并基类精简版）
职责：合并原有的 test_image_hosting_plugins.py 与 test_image_hosting_plugins_extra.py。
通过提取 BaseImageHostTest 共享基类与统一的临时文件生命周期管理，全面提升测试健壮性与可维护性。
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
from adapters.egress.image_hosting.qiniu_kodo import QiniuKodoImageHost
from adapters.egress.image_hosting.upyun_uss import UpyunUssImageHost
from adapters.egress.image_hosting.loli_io import LoliIoImageHost
from adapters.egress.image_hosting.superbed import SuperbedImageHost
from adapters.egress.image_hosting.lsky_pro import LskyProImageHost

from services.api.routes.gov.context_shards.plugin_ops import (
    probe_plugin_impl,
    dry_run_plugin_impl,
    install_plugin_deps_impl
)

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

class TestImageHostingPlugins(BaseImageHostTest):
    """所有图床插件的合并单元测试套件"""

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

    @pytest.mark.anyio
    async def test_install_plugin_deps(self):
        """测试一键安装依赖包接口与环境自愈降级"""
        res_fail = await install_plugin_deps_impl({})
        assert res_fail["success"] is False
        assert "Plugin ID" in res_fail["error"]

        res_none = await install_plugin_deps_impl({"id": "telegraph"})
        assert res_none["success"] is True
        assert "不需要外部" in res_none["logs"][0]["message"]

        # 1. 模拟直接成功
        with patch("subprocess.run") as mock_run:
            mock_res = MagicMock()
            mock_res.returncode = 0
            mock_res.stdout = "Successfully installed"
            mock_res.stderr = ""
            mock_run.return_value = mock_res

            res_ok = await install_plugin_deps_impl({"id": "aliyun_oss"})
            assert res_ok["success"] is True
            assert any("成功" in log["message"] for log in res_ok["logs"])

        # 2. 模拟全部源均安装失败
        with patch("subprocess.run") as mock_run:
            mock_res = MagicMock()
            mock_res.returncode = 1
            mock_res.stdout = ""
            mock_res.stderr = "Connection error"
            mock_run.return_value = mock_res

            res_fail = await install_plugin_deps_impl({"id": "aliyun_oss"})
            assert res_fail["success"] is False
            assert any("安装失败" in log["message"] for log in res_fail["logs"])

        # 3. 模拟镜像源 Failover 自愈降级 (第一轮失败，第二轮成功)
        with patch("subprocess.run") as mock_run:
            mock_res_fail = MagicMock()
            mock_res_fail.returncode = 1
            mock_res_fail.stderr = "Connection timeout"
            
            mock_res_ok = MagicMock()
            mock_res_ok.returncode = 0
            mock_res_ok.stdout = "Successfully installed"
            
            mock_run.side_effect = [mock_res_fail, mock_res_ok]
            
            res_failover = await install_plugin_deps_impl({"id": "aliyun_oss"})
            assert res_failover["success"] is True
            assert any("阿里云" in log["message"] and "成功" in log["message"] for log in res_failover["logs"])

        # 4. 模拟权限不足与系统托管自愈 (第一轮权限不足/系统托管报错，第二轮自愈追加参数成功)
        with patch("subprocess.run") as mock_run:
            mock_res_permission = MagicMock()
            mock_res_permission.returncode = 1
            mock_res_permission.stderr = "error: externally-managed-environment\nPermission denied"
            
            mock_res_ok = MagicMock()
            mock_res_ok.returncode = 0
            mock_res_ok.stdout = "Successfully installed"
            
            mock_run.side_effect = [mock_res_permission, mock_res_ok]
            
            res_self_healing = await install_plugin_deps_impl({"id": "aliyun_oss"})
            assert res_self_healing["success"] is True
            assert any("权限拦截" in log["message"] or "系统库锁定" in log["message"] for log in res_self_healing["logs"])
            
            # 检验是否被传入了自愈追加的参数
            args_passed = mock_run.call_args_list[1][0][0]
            assert "--user" in args_passed or "--break-system-packages" in args_passed
