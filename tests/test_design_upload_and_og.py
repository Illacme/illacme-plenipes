# -*- coding: utf-8 -*-
"""
🎨 Design Studio - Local OG Provider & Asset Upload Tests
职责：验证本地极客 OG 排版引擎与媒体资产本地上传入库的核心业务逻辑。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import io
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image

from core.design.providers.local_og_provider import LocalOGProvider
from core.design.providers.provider_registry import ProviderRegistry


class TestLocalOGProvider:
    """本地原生排版引擎单测套件"""

    def test_local_og_provider_registration(self):
        """测试本地 OG 提供商在注册表中成功挂载且为开箱即用状态"""
        providers = ProviderRegistry.list_supported_providers()
        local_og = next((p for p in providers if p["id"] == "local_og"), None)
        assert local_og is not None
        assert local_og["config_status"] == "out_of_box"
        assert local_og["requires_credentials"] is False

    def test_local_og_connection_test(self):
        """测试本地原生排版引擎连通性自检"""
        provider = LocalOGProvider()
        res = provider.test_connection()
        assert res["success"] is True
        assert "免Key离线运行" in res["message"]
        assert res["latency_ms"] >= 0

    def test_local_og_image_generation_multiratio(self):
        """测试本地极客排版引擎多比例封面渲染"""
        provider = LocalOGProvider({
            "brand_name": "TEST SOVEREIGN",
            "author": "Antigravity",
            "category": "Architecture"
        })

        for ratio in ["16:9", "2.35:1", "1:1"]:
            img_bytes, err = provider.generate_image(
                prompt="深入理解分布式系统与主权架构",
                aspect_ratio=ratio,
                style="vivid"
            )
            assert err is None
            assert img_bytes is not None
            assert len(img_bytes) > 1000

            # 验证生成为真实有效图片并符合比例
            img = Image.open(io.BytesIO(img_bytes))
            assert img.width > 500
            assert img.height > 200

    def test_local_og_badge_mode(self):
        """测试极简微标模式渲染"""
        provider = LocalOGProvider()
        img_bytes, err = provider.generate_image(
            prompt="极简设计微标封面",
            aspect_ratio="16:9",
            style="badge"
        )
        assert err is None
        assert img_bytes is not None


class TestAssetUploadRoutes:
    """媒体资产本地上传路由单测套件"""

    @pytest.mark.anyio
    async def test_upload_invalid_extension(self):
        """测试非法格式拦截"""
        from fastapi import HTTPException
        from services.api.routes.design_shards.design_upload_routes import upload_visual_asset

        mock_file = MagicMock()
        mock_file.filename = "malicious_script.sh"

        mock_engine = MagicMock()
        with patch("services.api.routes.design_shards.design_upload_routes.get_global_engine", return_value=mock_engine):
            with pytest.raises(HTTPException) as exc_info:
                await upload_visual_asset(file=mock_file, prompt="test")
            assert exc_info.value.status_code == 400
            assert "不支持的图片格式" in exc_info.value.detail

    @pytest.mark.anyio
    async def test_upload_valid_image(self, tmp_path):
        """测试正常图片上传与 SQLite 账本写入"""
        from services.api.routes.design_shards.design_upload_routes import upload_visual_asset

        # 创建一个内存中的有效 png
        img = Image.new("RGB", (100, 100), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png_data = buf.getvalue()

        mock_file = MagicMock()
        mock_file.filename = "my_custom_cover.png"
        mock_file.read = MagicMock(side_effect=[png_data, b""])

        mock_engine = MagicMock()
        mock_engine.vault_root = str(tmp_path)
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.lastrowid = 888
        mock_conn.cursor.return_value = mock_cur
        mock_engine.meta.sqlite.get_connection.return_value = mock_conn

        with patch("services.api.routes.design_shards.design_upload_routes.get_global_engine", return_value=mock_engine):
            res = await upload_visual_asset(file=mock_file, prompt="手绘极简封面")
            assert res["success"] is True
            assert res["asset_id"] == 888
            assert "my_custom_cover" in res["filename"]
            assert res["url"].startswith("/api/design/assets/covers/")
