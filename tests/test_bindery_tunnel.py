# -*- coding: utf-8 -*-
"""
⚡ tests/test_bindery_tunnel.py
零配置临时公网穿透 (Zero-Config Public Tunnel) 与限时防越权安全令牌全链路测试套件。
涵盖：
1. TunnelHub 单例生命周期与 Token 签发/校验/过期清除机制
2. FastAPI 隧道状态接口与公网扫码 Token 契约
3. 防越权拦截与错误保护
4. 前端 vault.bindery.qr.js 双模切换与 Node 沙箱交互
"""

import time
import subprocess
import pytest
from fastapi.testclient import TestClient

from core.bindery.tunnel import get_tunnel_hub, TunnelHub
from services.api.server import app
from services.api.routes.system import verify_token


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


def test_tunnel_hub_token_lifecycle():
    """测试临时安全令牌签发、防串号校验与过期清理机制"""
    hub = get_tunnel_hub()
    fn = "vol1_sample.epub"

    # 1. 签发有效令牌 (30 分钟)
    token = hub.issue_token(fn, ttl_seconds=1800)
    assert isinstance(token, str) and len(token) > 16
    assert hub.verify_token(fn, token) is True

    # 2. 防越权与目标文件不匹配测试
    assert hub.verify_token("other_book.epub", token) is False
    assert hub.verify_token(fn, "invalid_fake_token") is False
    assert hub.verify_token(fn, None) is False

    # 3. 模拟过期令牌
    short_token = hub.issue_token("temp.epub", ttl_seconds=-1)
    assert hub.verify_token("temp.epub", short_token) is False


def test_tunnel_status_and_not_running_public_qr(client):
    """测试隧道初始未启动时的状态与公网二维码拦截"""
    hub = get_tunnel_hub()
    hub.stop_tunnel()

    res = client.get("/api/bindery/tunnel/status")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["is_running"] is False

    # 未启动隧道时请求公网二维码应当被友好拦截 (400)
    res_qr = client.get("/api/bindery/qr/public", params={"file": "sample.epub"})
    assert res_qr.status_code == 400
    assert "临时公网隧道未启动" in res_qr.json()["detail"]


def test_tunnel_active_public_qr_flow(client, monkeypatch):
    """模拟公网隧道启动后，获取包含 30 分钟临时凭证的公网二维码载荷"""
    hub = get_tunnel_hub()

    # 模拟隧道已成功分配 Cloudflare 临时域名
    monkeypatch.setattr(hub, "_public_url", "https://mystic-pub.trycloudflare.com")
    monkeypatch.setattr(hub, "_provider", "cloudflare")
    monkeypatch.setattr(hub, "_start_time", time.time())
    # 模拟存在活跃进程对象
    class DummyProc:
        def poll(self): return None
        def terminate(self): pass
        def wait(self, timeout=None): pass
    monkeypatch.setattr(hub, "_process", DummyProc())

    # 1. 验证状态接口
    res_st = client.get("/api/bindery/tunnel/status")
    assert res_st.status_code == 200
    assert res_st.json()["is_running"] is True
    assert res_st.json()["public_url"] == "https://mystic-pub.trycloudflare.com"

    # 2. 获取公网二维码载荷
    res_pub = client.get("/api/bindery/qr/public", params={"file": "anthology.epub"})
    assert res_pub.status_code == 200
    pub_data = res_pub.json()
    assert pub_data["success"] is True
    assert pub_data["is_public"] is True
    assert pub_data["filename"] == "anthology.epub"
    assert pub_data["token"] is not None
    assert "token=" in pub_data["url"]
    assert "https://mystic-pub.trycloudflare.com/api/bindery/download?file=anthology.epub&token=" in pub_data["url"]

    # 3. 校验该生成的 token 确实已被注册在内存令牌池
    assert hub.verify_token("anthology.epub", pub_data["token"]) is True


def test_bindery_qr_dual_mode_in_node_sandbox():
    """在 Node 沙箱中真实调用 vault.bindery.qr.js 验证双模网络切换逻辑"""
    runner = """
    const fs = require('fs');

    const createdElements = [];
    const mockDoc = {
        createElement: (tag) => {
            const el = {
                tagName: tag.toUpperCase(),
                id: '',
                style: {},
                children: [],
                appendChild: (child) => { el.children.push(child); return child; },
                removeChild: (child) => {
                    const idx = el.children.indexOf(child);
                    if (idx >= 0) el.children.splice(idx, 1);
                },
                parentNode: null,
                set innerHTML(val) { el._html = val; },
                get innerHTML() { return el._html || ''; }
            };
            el.parentNode = mockDoc.body;
            createdElements.push(el);
            return el;
        },
        getElementById: (id) => {
            return createdElements.find(e => e.id === id) || null;
        },
        querySelectorAll: (sel) => [],
        body: {
            children: [],
            appendChild: (child) => { mockDoc.body.children.push(child); child.parentNode = mockDoc.body; },
            removeChild: (child) => {
                const idx = mockDoc.body.children.indexOf(child);
                if (idx >= 0) mockDoc.body.children.splice(idx, 1);
                child.parentNode = null;
            }
        },
        addEventListener: () => {},
        removeEventListener: () => {}
    };

    global.document = mockDoc;
    global.window = {
        document: mockDoc,
        apiFetch: async (url) => {
            if (url.includes('/api/bindery/tunnel/status')) {
                return { json: async () => ({ is_running: false }) };
            }
            return {
                json: async () => ({
                    success: true,
                    filename: 'test.epub',
                    qr_data_uri: '',
                    url: 'http://192.168.1.1:43212/api/bindery/download?file=test.epub',
                    lan_ip: '192.168.1.1',
                    port: 43212
                })
            };
        },
        showToast: () => {}
    };
    global.requestAnimationFrame = (cb) => { cb(); };

    // 1. 载入矢量引擎与主弹窗分片
    eval(fs.readFileSync('web/dashboard/js/vault/vault.bindery.qr_engine.js', 'utf8'));
    eval(fs.readFileSync('web/dashboard/js/vault/vault.bindery.qr.js', 'utf8'));

    if (typeof window.switchBinderyQrNetworkMode !== 'function') throw new Error('缺少 switchBinderyQrNetworkMode');

    // 2. 模拟打开弹窗 (默认局域网)
    window.openBinderyQrModal('book.epub');
    if (window._binderyQrCurrentFile !== 'book.epub') throw new Error('当前文件未正确记录');

    // 3. 模拟切换至公网模式
    window.switchBinderyQrNetworkMode('public');
    if (window._binderyQrNetworkMode !== 'public') throw new Error('网络模式未切换至 public');

    // 4. 模拟切回局域网
    window.switchBinderyQrNetworkMode('lan');
    if (window._binderyQrNetworkMode !== 'lan') throw new Error('网络模式未切换回 lan');

    // 5. 模拟通道选择函数
    if (typeof window.selectBinderyTunnelDriver !== 'function') throw new Error('缺少 selectBinderyTunnelDriver');
    window._binderyQrDrivers = [
        { id: 'cloudflare', name: 'Cloudflare', icon: '☁️' },
        { id: 'pinggy', name: 'Pinggy', icon: '⚡' }
    ];
    window.selectBinderyTunnelDriver('pinggy');
    if (window._binderyQrSelectedDriver !== 'pinggy') throw new Error('驱动未选中 pinggy');

    console.log('PASS');
    """
    proc = subprocess.run(["node", "-e", runner], capture_output=True, text=True)
    assert proc.returncode == 0, f"Node 沙箱执行失败: {proc.stderr}"
    assert "PASS" in proc.stdout


def test_tunnel_drivers_endpoint(client):
    """测试获取可用穿透通道列表接口 GET /api/bindery/tunnel/drivers"""
    res = client.get("/api/bindery/tunnel/drivers")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "drivers" in data
    assert isinstance(data["drivers"], list)
    assert "active_driver" in data
    # 验证驱动列表结构
    driver_ids = [d["id"] for d in data["drivers"]]
    assert "cloudflare" in driver_ids
    assert "pinggy" in driver_ids
    for d in data["drivers"]:
        assert "name" in d
        assert "icon" in d
        assert "is_enabled" in d


def test_tunnel_start_with_specified_driver(client, monkeypatch):
    """测试指定 driver 参数触发启动"""
    hub = get_tunnel_hub()
    called_driver = []

    def mock_start_tunnel(port=43212, timeout_seconds=15, driver=None):
        called_driver.append(driver)
        return {
            "is_running": True,
            "url": "https://test.trycloudflare.com",
            "provider": driver or "cloudflare",
            "provider_name": "Cloudflare Anycast"
        }

    monkeypatch.setattr(hub, "start_tunnel", mock_start_tunnel)

    # 1. 传递 driver=pinggy
    res1 = client.post("/api/bindery/tunnel/start", json={"driver": "pinggy"})
    assert res1.status_code == 200
    assert called_driver[-1] == "pinggy"

    # 2. 传递 driver=cloudflare
    res2 = client.post("/api/bindery/tunnel/start", json={"driver": "cloudflare"})
    assert res2.status_code == 200
    assert called_driver[-1] == "cloudflare"

    # 3. 不传 driver (默认自动队列)
    res3 = client.post("/api/bindery/tunnel/start")
    assert res3.status_code == 200
    assert called_driver[-1] is None

