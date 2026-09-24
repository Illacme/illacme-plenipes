# -*- coding: utf-8 -*-
"""
🛡️ [V127.0] Illacme Plenipes - Plugin Brand Activation Sovereignty Test Suite
测试职责：验证所有插件分类在当前品牌启用的逻辑合理性。
硬性准则：缺少关键配置/未就绪的插件，绝对禁止被标记为启用 (is_in_use) 或允许在未配置时被开启。
"""

import pytest
from types import SimpleNamespace
from services.api.routes.gov.plugin_collector_channels import (
    is_plugin_config_ready,
    collect_tunnel_plugins,
    collect_hosting_plugins,
    collect_syndication_plugins,
    collect_image_hosting_plugins,
    collect_notification_plugins
)
from core.bindery.tunnel import get_tunnel_hub


def test_is_plugin_config_ready_guard():
    """验证各分类关键凭据就绪校验算子"""
    # 1. Tunnel: ngrok / frp 必须非空参数，localhost_run / serveo / pinggy 免配即用
    assert is_plugin_config_ready("tunnel", "localhost_run", {}) is True
    assert is_plugin_config_ready("tunnel", "serveo", {}) is True
    assert is_plugin_config_ready("tunnel", "pinggy", {}) is True
    assert is_plugin_config_ready("tunnel", "cloudflare", {}) is True
    assert is_plugin_config_ready("tunnel", "ngrok", {}) is False
    assert is_plugin_config_ready("tunnel", "ngrok", {"authtoken": ""}) is False
    assert is_plugin_config_ready("tunnel", "ngrok", {"authtoken": "YOUR_NGROK_TOKEN"}) is False
    assert is_plugin_config_ready("tunnel", "ngrok", {"authtoken": "valid_token_12345"}) is True

    assert is_plugin_config_ready("tunnel", "frp", {}) is False
    assert is_plugin_config_ready("tunnel", "frp", {"server_addr": "frp.example.com"}) is True

    # 2. Hosting: 缺少 repo / token 禁止就绪
    assert is_plugin_config_ready("hosting", "github_pages", {}) is False
    assert is_plugin_config_ready("hosting", "github_pages", {"token": ""}) is False
    assert is_plugin_config_ready("hosting", "github_pages", {"token": "ghp_valid"}) is True
    assert is_plugin_config_ready("hosting", "github_pages", {"repo_url": "https://github.com/org/repo"}) is True

    # 3. Publisher: 缺少 token / webhook 禁止就绪
    assert is_plugin_config_ready("publisher", "zhihu", {}) is False
    assert is_plugin_config_ready("publisher", "zhihu", {"cookie": "z_c0=123"}) is True

    # 4. Image Hosting: catbox 免配即用，其余需配置
    assert is_plugin_config_ready("image_hosting", "catbox", {}) is True
    assert is_plugin_config_ready("image_hosting", "imgbb", {}) is False
    assert is_plugin_config_ready("image_hosting", "imgbb", {"api_key": "img_key"}) is True

    # 5. Notification: 需配置 webhook / token
    assert is_plugin_config_ready("notification", "feishu", {}) is False
    assert is_plugin_config_ready("notification", "feishu", {"webhook_url": "https://open.feishu.cn/..."}) is True


def test_unconfigured_ngrok_cannot_be_in_use_even_with_dirty_config():
    """验证即使配置中有 enabled: True 或 active_driver: ngrok，未填 token 时也禁止在用"""
    mock_engine = SimpleNamespace(
        config=SimpleNamespace(
            tunnel={
                "active_driver": "ngrok",
                "ngrok": {"enabled": True, "authtoken": ""},
                "localhost_run": {},
                "serveo": {},
                "pinggy": {}
            }
        )
    )
    plugins = collect_tunnel_plugins(mock_engine, set(), "V1.0")
    plugin_map = {p["id"]: p for p in plugins}

    assert plugin_map["ngrok"]["is_in_use"] is False
    assert plugin_map["ngrok"]["status"] == "Ready"

    # 免配即用的三大官方 OpenSSH 驱动保持在用
    assert plugin_map["localhost_run"]["is_in_use"] is True
    assert plugin_map["serveo"]["is_in_use"] is True
    assert plugin_map["pinggy"]["is_in_use"] is True


def test_bindery_tunnel_hub_filters_unconfigured_drivers():
    """验证扫码通道列表自动剔除未配置凭据的 ngrok，并将首选降级至 localhost_run"""
    hub = get_tunnel_hub()
    # 模拟环境配置
    orig_get_cfg = hub._get_tunnel_config
    hub._get_tunnel_config = lambda: {
        "active_driver": "ngrok",
        "ngrok": {"enabled": True, "authtoken": ""},
        "frp": {"enabled": True, "server_addr": ""},
        "localhost_run": {"enabled": True}
    }
    try:
        enabled_drivers = hub.list_available_drivers(only_enabled=True)
        driver_ids = [d["id"] for d in enabled_drivers]
        assert "ngrok" not in driver_ids
        assert "frp" not in driver_ids
        assert "localhost_run" in driver_ids

        # 首选驱动必须自动回退至就绪的 localhost_run，而不是未配置的 ngrok
        pref = next(d for d in enabled_drivers if d.get("is_preferred"))
        assert pref["id"] == "localhost_run"
    finally:
        hub._get_tunnel_config = orig_get_cfg
