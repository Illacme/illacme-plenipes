#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V48.3] 图床插件 Plugin Ops 集成测试（探测/Dry-Run/依赖安装）
🛡️ [V88.0 Split] 从 test_image_hosting_plugins.py 物理克隆搬迁 — probe/dry-run/install 集成测试。
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath('.'))

from services.api.routes.gov.context_shards.plugin_ops import (
    probe_plugin_impl,
    dry_run_plugin_impl,
    install_plugin_deps_impl
)


class TestImageHostingPluginOps:
    """图床插件 Plugin Ops 集成测试套件"""

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
