# -*- coding: utf-8 -*-
"""
⚡ [V126.0] Bindery QR Diagnostic & Auto-Heal Test Suite
测试范围：局域网物理多网卡探针、候选 IP 切换直链生成、公网隧道回环主动检测与链路故障自愈推荐。
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from services.api.server import app
from services.api.routes.system import verify_token
from core.bindery.tunnel_diagnostic import get_lan_candidates, probe_lan_health, probe_public_tunnel, auto_heal_public_tunnel


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


def test_lan_candidates_probe():
    """验证局域网网卡探针能够发现候选 IP 并进行亲和性优先级排序"""
    candidates = get_lan_candidates()
    assert isinstance(candidates, list)
    assert len(candidates) >= 1
    pref = [c for c in candidates if c.get("is_preferred")]
    assert len(pref) == 1
    assert "ip" in pref[0]
    assert "interface" in pref[0]


def test_lan_health_probe_api(client):
    """测试 /api/bindery/probe/lan 接口返回格式与排障提示"""
    res = client.get("/api/bindery/probe/lan")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "active_ip" in data
    assert "port" in data
    assert "candidates" in data
    assert isinstance(data["tips"], list)
    assert len(data["tips"]) >= 1


def test_qr_lan_switch_ip(client):
    """验证指定自定义候选 IP 时，局域网二维码能正确使用目标 IP 生成直链"""
    test_ip = "192.168.100.222"
    res = client.get(f"/api/bindery/qr?file=sample.epub&ip={test_ip}")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["lan_ip"] == test_ip
    assert f"http://{test_ip}:" in data["url"]
    assert "lan_candidates" in data


def test_public_tunnel_probe_empty():
    """测试无有效域名时的探针容错"""
    res = probe_public_tunnel("")
    assert res["healthy"] is False
    assert res["error_code"] == "NO_URL"


def test_public_tunnel_probe_no_tunnel_at_host():
    """测试精准识别 'no tunnel here' 远端中继未就绪错误特征"""
    mock_resp = MagicMock()
    mock_resp.getcode.return_value = 502
    mock_resp.read.return_value = b"<html><body>no tunnel here :(</body></html>"
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = probe_public_tunnel("https://d873ec7f18a760.lhr.life")
        assert res["healthy"] is False
        assert res["error_code"] == "NO_TUNNEL_AT_HOST"
        assert "no tunnel here" in res["message"]


def test_public_tunnel_probe_healthy():
    """测试公网隧道回环连通并计算时延"""
    mock_resp = MagicMock()
    mock_resp.getcode.return_value = 200
    mock_resp.read.return_value = b'{"success": true}'
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = probe_public_tunnel("https://my-good-tunnel.serveo.net")
        assert res["healthy"] is True
        assert res["rtt_ms"] is not None
        assert res["rtt_ms"] >= 0
        assert "通畅" in res["message"]


def test_tunnel_probe_api(client):
    """测试 /api/bindery/tunnel/probe 接口在未启动隧道时的优雅降级"""
    res = client.get("/api/bindery/tunnel/probe")
    assert res.status_code == 200
    data = res.json()
    assert data["healthy"] is False


def test_auto_heal_public_tunnel():
    """测试在当前隧道故障时，自愈中枢能调度并尝试备用隧道"""
    hub = MagicMock()
    # 模拟当前隧道状态故障
    hub.get_status.return_value = {
        "is_running": True,
        "public_url": "https://broken.lhr.life",
        "provider": "localhost_run"
    }
    hub.list_available_drivers.return_value = [
        {"id": "localhost_run", "name": "Localhost.run"},
        {"id": "serveo", "name": "Serveo SSH"}
    ]
    # 模拟切换至 serveo 成功
    hub.start_tunnel.return_value = {
        "is_running": True,
        "public_url": "https://healthy.serveo.net",
        "provider": "serveo",
        "provider_name": "Serveo SSH"
    }

    mock_resp = MagicMock()
    mock_resp.getcode.return_value = 200
    mock_resp.read.return_value = b'{"success": true}'
    mock_resp.__enter__.return_value = mock_resp

    # 第一次对 broken.lhr.life 发送探针失败，第二次对 healthy.serveo.net 成功
    def mock_urlopen(req, *args, **kwargs):
        if "broken" in req.full_url:
            mock_bad = MagicMock()
            mock_bad.getcode.return_value = 502
            mock_bad.read.return_value = b"no tunnel here :("
            mock_bad.__enter__.return_value = mock_bad
            return mock_bad
        return mock_resp

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        heal_res = auto_heal_public_tunnel(hub, current_driver="localhost_run", port=43212)
        assert heal_res["success"] is True
        assert heal_res["healed"] is True
        assert heal_res["public_url"] == "https://healthy.serveo.net"
        assert heal_res["probe"]["healthy"] is True


def test_pure_path_download_and_view(client, tmp_path):
    """验证纯路径公网下载与在线阅读端点，确保在丢弃 Query 参数时依然 100% 成功交付"""
    from core.bindery.tunnel import get_tunnel_hub
    import os

    # 准备测试文件
    books_dir = os.path.abspath("dist/books")
    os.makedirs(books_dir, exist_ok=True)
    test_html = os.path.join(books_dir, "test_pure_path.html")
    with open(test_html, "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Pure Path Content</h1></body></html>")

    hub = get_tunnel_hub()
    token = hub.issue_token("test_pure_path.html")

    # 1. 纯路径在线阅读验证
    res_v = client.get(f"/api/bindery/view/{token}/test_pure_path.html")
    assert res_v.status_code == 200
    assert "Pure Path Content" in res_v.text

    # 2. 纯路径直接下载验证
    res_d = client.get(f"/api/bindery/download/{token}/test_pure_path.html")
    assert res_d.status_code == 200
    assert res_d.headers.get("content-disposition") is not None

    # 3. 令牌防越权防御验证
    res_bad = client.get("/api/bindery/download/fake_token/test_pure_path.html")
    assert res_bad.status_code == 403

    # 清理
    if os.path.exists(test_html):
        os.remove(test_html)

