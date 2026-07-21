#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Plugin Probe Routing & Toggle Safety Tests
验证插件物理探测（PROBE）在多分类同名 ID 下的精准分流路由及开关绑定校验防呆逻辑。
"""

import sys
import pytest
from unittest.mock import MagicMock, patch

# 注入 Mock 依赖以防本地 Python 环境未安装包时引发导入错误
sys.modules['oss2'] = MagicMock()
sys.modules['qcloud_cos'] = MagicMock()
sys.modules['paramiko'] = MagicMock()

from services.api.routes.gov.context_shards.plugin_ops import probe_plugin_impl, toggle_plugin_impl

@pytest.mark.anyio
async def test_probe_routing_with_category_hosting():
    """
    验证当指定 category="hosting" 时，aliyun_oss 能够精准路由到托管分支，而非被图床分支拦截。
    """
    mock_engine = MagicMock()
    # 模拟托管配置
    mock_engine.config.publish_control.direct_upload = {
        "aliyun_oss": {
            "bucket": "my-bucket",
            "endpoint": "oss-cn-hangzhou.aliyuncs.com",
            "access_key_id": "key-id",
            "access_key_secret": "key-secret"
        }
    }
    mock_engine.config.dict.return_value = {}

    # Mock oss2.Bucket 使得 is_healthy() 返回 True
    import oss2
    mock_bucket_instance = MagicMock()
    oss2.Bucket.return_value = mock_bucket_instance

    with patch("services.api.routes.gov.context_shards.plugin_ops.get_global_engine", return_value=mock_engine), \
         patch("core.adapters.egress.publishers.base.BasePublisher.ensure_python_dependency", return_value=True):
        # 探测 aliyun_oss 并指定 category="hosting"
        res = await probe_plugin_impl({
            "id": "aliyun_oss",
            "category": "hosting"
        })
        assert res["success"] is True
        assert res["healthy"] is True
        # 托管探测返回的信息应该包含 "托管渠道已就绪"
        assert "托管渠道已就绪" in res["message"]


@pytest.mark.anyio
async def test_probe_routing_with_category_image_hosting():
    """
    验证当指定 category="image_hosting" 时，aliyun_oss 能够精准路由到图床分支。
    """
    mock_engine = MagicMock()
    mock_engine.config.image_hosting = {"provider": "aliyun_oss"}

    with patch("services.api.routes.gov.context_shards.plugin_ops.get_global_engine", return_value=mock_engine):
        # 探测 aliyun_oss 并指定 category="image_hosting"
        res = await probe_plugin_impl({
            "id": "aliyun_oss",
            "category": "image_hosting"
        })
        assert res["success"] is True
        assert res["healthy"] is True
        # 图床探测返回的信息应该包含 "图床驱动已挂载"
        assert "图床驱动已挂载" in res["message"]


@pytest.mark.anyio
async def test_probe_routing_backward_compatibility():
    """
    验证当不指定 category 时，能够通过降级路由（Fallback）默认先路由至图床（兼容旧版测试和接口行为）。
    """
    mock_engine = MagicMock()
    mock_engine.config.image_hosting = {"provider": "aliyun_oss"}

    with patch("services.api.routes.gov.context_shards.plugin_ops.get_global_engine", return_value=mock_engine):
        # 探测 aliyun_oss 且不指定 category
        res = await probe_plugin_impl({
            "id": "aliyun_oss"
        })
        assert res["success"] is True
        assert res["healthy"] is True
        # 由于默认图床判断更靠前，不带 category 会默认走图床自检
        assert "图床驱动已挂载" in res["message"]


@pytest.mark.anyio
async def test_toggle_plugin_safety_across_categories():
    """
    验证 toggle_plugin_impl 开关自愈防呆检验：
    若某个插件 ID（例如 aliyun_oss）在任意一个分类（例如 hosting）中被绑定使用，
    则试图在全局层面禁用它（enable=False）时，应被安全拦截，报错拒绝。
    """
    mock_engine = MagicMock()
    
    # 模拟 assemble_plugin_matrix 返回的插件矩阵
    # 假设 aliyun_oss 在 image_hosting 中没有使用，但在 hosting 中是在激活使用的 (is_in_use=True)
    mock_matrix = [
        {"id": "aliyun_oss", "category": "image_hosting", "is_in_use": False, "is_enabled": True},
        {"id": "aliyun_oss", "category": "hosting", "is_in_use": True, "is_enabled": True}
    ]

    with patch("services.api.routes.gov.context_shards.plugin_ops.get_global_engine", return_value=mock_engine), \
         patch("services.api.routes.gov.plugin_mapper.assemble_plugin_matrix", return_value=mock_matrix):
        
        # 尝试禁用 aliyun_oss
        res = await toggle_plugin_impl({
            "id": "aliyun_oss",
            "enable": False
        })
        assert res["status"] == "error"
        assert "该插件正在被当前品牌绑定使用" in res["error"]
