# -*- coding: utf-8 -*-
"""
🛰️ [V126.0] Illacme Plenipes - Tunnel Plugins Test Suite
测试职责：验证网络穿透插件注册表、Pinggy/Cloudflare 驱动契约、矩阵映射与探针连通性。
🛡️ [SOP-01]：单文件严格 ≤ 300 行。
"""

import pytest
from fastapi.testclient import TestClient

from core.adapters.tunnel import TunnelRegistry, BaseTunnelAdapter
from core.adapters.tunnel.pinggy import PinggyTunnelAdapter
from core.adapters.tunnel.cloudflare import CloudflareTunnelAdapter
from services.api.routes.gov.plugin_collector_channels import collect_tunnel_plugins
from services.api.routes.gov.plugin_mapper import assemble_plugin_matrix
from services.api.routes.gov.context_shards.plugin_ops import probe_plugin_impl
from core.runtime.engine_singleton import get_global_engine
from services.api.server import app
from services.api.routes.system import verify_token


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


def test_tunnel_registry_auto_discovery():
    """验证驱动中枢自动扫描并注册了内置驱动"""
    drivers = TunnelRegistry.list_all()
    assert "pinggy" in drivers
    assert "cloudflare" in drivers
    assert issubclass(drivers["pinggy"], BaseTunnelAdapter)
    assert issubclass(drivers["cloudflare"], BaseTunnelAdapter)


def test_pinggy_driver_contracts():
    """验证 Pinggy 驱动的属性契约与基本生命周期"""
    adapter = PinggyTunnelAdapter()
    assert adapter.PLUGIN_ID == "pinggy"
    assert adapter.CATEGORY == "tunnel"
    assert adapter.HAS_CONFIG is False
    status = adapter.get_status()
    assert status["is_running"] is False
    assert status["provider"] == "pinggy"

    # 执行连通性探测 (probe)
    probe_res = adapter.probe()
    assert "success" in probe_res
    assert "message" in probe_res


def test_cloudflare_driver_contracts():
    """验证 Cloudflare 驱动的属性契约与配置支持"""
    adapter = CloudflareTunnelAdapter(config={"tunnel_token": "mock-token-xyz"})
    assert adapter.PLUGIN_ID == "cloudflare"
    assert adapter.CATEGORY == "tunnel"
    assert adapter.HAS_CONFIG is True
    assert adapter.config.get("tunnel_token") == "mock-token-xyz"

    probe_res = adapter.probe()
    assert "success" in probe_res
    assert "healthy" in probe_res


def test_collect_tunnel_plugins_matrix(client):
    """验证全域插件矩阵收集器正确收集了 tunnel 驱动"""
    engine = get_global_engine()
    plugins = collect_tunnel_plugins(engine, disabled=set(), system_track="V24.0")
    assert len(plugins) >= 2
    cat_ids = [p["category"] for p in plugins]
    assert all(cat == "tunnel" for cat in cat_ids)
    plugin_ids = [p["id"] for p in plugins]
    assert "pinggy" in plugin_ids
    assert "cloudflare" in plugin_ids


def test_assemble_plugin_matrix_includes_tunnels():
    """验证全局组装器包含 tunnel 类别"""
    from unittest.mock import MagicMock, patch
    engine_mock = MagicMock()
    engine_mock.config.tunnel = {}
    engine_mock.config.plugins.disabled_plugins = []
    engine_mock.config.active_theme = "default"

    with patch("services.api.routes.gov.plugin_mapper.get_global_engine", return_value=engine_mock):
        matrix = assemble_plugin_matrix()

    tunnel_plugins = [p for p in matrix if p.get("category") == "tunnel"]
    assert len(tunnel_plugins) >= 2


@pytest.mark.anyio
async def test_probe_plugin_impl_tunnel():
    """验证 /api/plugins/probe 接口能成功路由并探测网络穿透驱动"""
    from unittest.mock import MagicMock, patch
    with patch("services.api.routes.gov.context_shards.plugin_ops.get_global_engine", return_value=MagicMock()):
        res = await probe_plugin_impl({"id": "pinggy", "category": "tunnel"})
    assert "success" in res
    assert "message" in res


def test_configuration_tunnel_field_and_governance_routing():
    """验证 Configuration 模型中存在 tunnel 属性，且凭据正确归属于 local 治理层级"""
    from core.config.config_models import Configuration
    from core.config.governance_map import resolve_governance_level

    cfg = Configuration()
    assert hasattr(cfg, "tunnel")
    assert isinstance(cfg.tunnel, dict)

    # 验证治理层级解析至 local (config.local.yaml)
    assert resolve_governance_level("tunnel.cloudflare.tunnel_token") == "local"
    assert resolve_governance_level("tunnel.cloudflare.hostname") == "local"


def test_cloudflare_token_mode_behavior():
    """验证配置了自建 Tunnel Token 与 Hostname 后的 Cloudflare 驱动行为"""
    from unittest.mock import patch

    adapter = CloudflareTunnelAdapter(config={
        "tunnel_token": "eyJh_mock_token_123",
        "hostname": "press.mycustomdomain.com"
    })

    # 1. 模拟未安装 cloudflared 组件场景
    with patch.object(adapter, "_locate_bin", return_value=None):
        probe_res = adapter.probe()
        assert probe_res["success"] is True
        assert "专属 Tunnel Token" in probe_res["message"]
        assert probe_res["details"]["has_token"] is True
        assert probe_res["details"]["hostname"] == "press.mycustomdomain.com"

    # 2. 模拟已安装 cloudflared 组件场景
    with patch.object(adapter, "_locate_bin", return_value="/usr/local/bin/cloudflared"):
        probe_res_installed = adapter.probe()
        assert probe_res_installed["success"] is True
        assert probe_res_installed["healthy"] is True
        assert "企业级 Anycast 节点就绪" in probe_res_installed["message"]
        assert "press.mycustomdomain.com" in probe_res_installed["message"]


def test_tunnel_plugin_dry_run_endpoint(client):
    """验证 /api/plugins/dry-run 能够对 Cloudflare 和 Pinggy 发起沙盒测试"""
    res = client.post("/api/plugins/dry-run", json={
        "id": "cloudflare",
        "settings": {
            "tunnel_token": "eyJh_dry_run_token_mock",
            "hostname": "press.dryrun.com"
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "logs" in data
    messages = [log["message"] for log in data["logs"]]
    assert any("穿透链路探测" in m for m in messages)
    assert any("Cloudflare Tunnel Token" in m for m in messages)


def test_tunnel_plugin_drawer_validation_optional_token():
    """验证前端表单校验对 Cloudflare Tunnel 的 tunnel_token 留空予以豁免通过"""
    import subprocess
    js_code = """
    const fs = require('fs');
    global.window = {};
    eval(fs.readFileSync('web/dashboard/js/plugins/sandbox_shards/sandbox.saver.js', 'utf8'));

    const mockInput = {
        disabled: false,
        type: 'password',
        classList: { contains: () => false },
        closest: (sel) => {
            if (sel === '.setting-row') {
                return {
                    querySelector: (s) => {
                        if (s === '.setting-label') return { innerText: 'Tunnel Token 隧道运行令牌' };
                        if (s === '.setting-desc') return { innerText: '留空则自动降级为 Quick 临时免密通道。' };
                        return null;
                    }
                };
            }
            return null;
        },
        getAttribute: (attr) => {
            if (attr === 'data-path') return 'tunnel.cloudflare.tunnel_token';
            if (attr === 'data-optional') return 'true';
            return null;
        },
        hasAttribute: () => false,
        placeholder: '留空使用 Quick 临时通道...',
        value: ''
    };

    const mockDrawerBody = {
        querySelectorAll: () => [mockInput],
        querySelector: () => null
    };

    const result = window.validatePluginDrawerForm(mockDrawerBody, 'cloudflare');
    if (!result.valid) {
        process.exit(1);
    }
    process.exit(0);
    """
    res = subprocess.run(["node", "-e", js_code], capture_output=True, text=True)
    assert res.returncode == 0, f"Validation failed with error: {res.stderr}"
