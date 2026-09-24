# -*- coding: utf-8 -*-
"""
📱 tests/test_bindery_qr_sync.py
移动端/平板设备局域网扫码直传 (LAN Mobile Sync) 全链路自动化回归测试套件。
涵盖：
1. 局域网物理 IP 自动探测与容错降级
2. 二维码 Base64 Data URI 高清矢量/位图流生成
3. 后端 /api/bindery/qr 接口协议契约与路径穿越防御
4. 前端 vault.bindery.qr.js 在 Node 沙箱中的真实 DOM 拓扑与交互闭环
"""

import os
import subprocess
import pytest
from fastapi.testclient import TestClient

from core.bindery.qr_sync import get_lan_ip, generate_qr_data_uri, build_mobile_sync_payload
from services.api.server import app
from services.api.routes.system import verify_token


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


def test_qr_sync_core_functions():
    """测试底层局域网探测与二维码生成核心引擎"""
    ip = get_lan_ip()
    assert isinstance(ip, str)
    assert len(ip.split(".")) == 4

    test_url = f"http://{ip}:43212/api/bindery/download?file=test.epub"
    data_uri = generate_qr_data_uri(test_url)
    assert data_uri.startswith("data:image/png;base64,")
    assert len(data_uri) > 100

    # 测试 payload 构建 (普通 epub 下载)
    payload_dl = build_mobile_sync_payload("anthology.epub", port=43212, action="download")
    assert payload_dl["success"] is True
    assert payload_dl["filename"] == "anthology.epub"
    assert payload_dl["port"] == 43212
    assert payload_dl["action"] == "download"
    assert "/api/bindery/download?file=anthology.epub" in payload_dl["url"]
    assert payload_dl["qr_data_uri"].startswith("data:image/png;base64,")

    # 测试 payload 构建 (WebBook 在线查看 - 默认缺省 action 自动提升为 view)
    payload_wb_default = build_mobile_sync_payload("anthology.html", port=43212)
    assert payload_wb_default["success"] is True
    assert payload_wb_default["action"] == "view"
    assert "/api/bindery/view?file=anthology.html" in payload_wb_default["url"]

    # 测试 payload 构建 (WebBook 显式 view)
    payload_wb = build_mobile_sync_payload("anthology.html", port=43212, action="view")
    assert payload_wb["success"] is True
    assert payload_wb["action"] == "view"
    assert "/api/bindery/view?file=anthology.html" in payload_wb["url"]

    # 测试 payload 构建 (WebBook 强制下载参数 force_download)
    payload_wb_force = build_mobile_sync_payload("anthology.html", port=43212, action="force_download")
    assert payload_wb_force["action"] == "download"
    assert "/api/bindery/download?file=anthology.html" in payload_wb_force["url"]


def test_qr_sync_fallback_when_qrcode_missing(monkeypatch):
    """测试当宿主机缺少 qrcode 依赖时，系统平稳降级零崩溃"""
    import core.bindery.qr_sync as qr_module
    monkeypatch.setattr(qr_module, "qrcode", None)

    uri = qr_module.generate_qr_data_uri("http://example.com")
    assert uri == ""

    payload = qr_module.build_mobile_sync_payload("anthology.epub")
    assert payload["success"] is True
    assert payload["has_qr_engine"] is False
    assert payload["qr_data_uri"] == ""
    assert "http://" in payload["url"]


def test_bindery_qr_api_path_traversal_defense(client):
    """测试 /api/bindery/qr 接口防路径穿越防御"""
    res = client.get("/api/bindery/qr", params={"file": "../../../etc/passwd"})
    assert res.status_code == 400
    assert "非法" in res.json().get("detail", "")

    res_empty = client.get("/api/bindery/qr", params={"file": ""})
    assert res_empty.status_code == 400


def test_bindery_qr_api_success(client, tmp_path):
    """测试 /api/bindery/qr 正常成功场景"""
    mock_book = tmp_path / "sample_book.epub"
    mock_book.write_bytes(b"PK00mock_epub_content")

    # 临时将 bindery 模块的安全路径解析定向到该临时文件
    from services.api.routes.gov import bindery
    orig_safe_fn = bindery._get_safe_book_path
    bindery._get_safe_book_path = lambda f: str(mock_book)

    try:
        res = client.get("/api/bindery/qr", params={"file": "sample_book.epub"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["filename"] == "sample_book.epub"
        assert data["qr_data_uri"].startswith("data:image/png;base64,")
        assert "/api/bindery/download?file=sample_book.epub" in data["url"]
    finally:
        bindery._get_safe_book_path = orig_safe_fn


def test_bindery_qr_frontend_in_node_sandbox():
    """在 Node 沙箱中真实运行 vault.bindery.qr.js 并断言 DOM 拓扑与生命周期"""
    runner = """
    const fs = require('fs');

    const domStorage = {};
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
            if (id === 'bindery-qr-modal-root') {
                return createdElements.find(e => e.id === 'bindery-qr-modal-root') || null;
            }
            if (id === 'bindery-qr-content') {
                return {
                    set innerHTML(val) { this._html = val; },
                    get innerHTML() { return this._html || ''; }
                };
            }
            return null;
        },
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
            return {
                json: async () => ({
                    success: true,
                    filename: 'my_book.epub',
                    qr_data_uri: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...',
                    url: 'http://192.168.1.100:43212/api/bindery/download?file=my_book.epub',
                    lan_ip: '192.168.1.100',
                    port: 43212,
                    action: 'download'
                })
            };
        },
        showToast: () => {}
    };
    global.requestAnimationFrame = (cb) => { cb(); };

    // 1. 加载并执行 vault.bindery.qr_engine.js 与 vault.bindery.qr.js
    eval(fs.readFileSync('web/dashboard/js/vault/vault.bindery.qr_engine.js', 'utf8'));
    if (typeof window.generateBinderyQrSvg !== 'function') throw new Error('缺少 generateBinderyQrSvg 函数');
    const testSvg = window.generateBinderyQrSvg('http://example.com/download', 200);
    if (!testSvg.startsWith('<svg') || !testSvg.includes('</svg>')) throw new Error('SVG 二维码生成异常');

    eval(fs.readFileSync('web/dashboard/js/vault/vault.bindery.qr.js', 'utf8'));

    if (typeof window.openBinderyQrModal !== 'function') throw new Error('缺少 openBinderyQrModal 函数');
    if (typeof window.closeBinderyQrModal !== 'function') throw new Error('缺少 closeBinderyQrModal 函数');

    // 2. 模拟拉起二维码弹窗
    window.openBinderyQrModal('my_book.epub');

    const root = mockDoc.getElementById('bindery-qr-modal-root');
    if (!root) throw new Error('未能挂载 #bindery-qr-modal-root 容器');

    // 3. 模拟关闭弹窗
    window.closeBinderyQrModal();

    console.log('PASS');
    """
    proc = subprocess.run(["node", "-e", runner], capture_output=True, text=True)
    assert proc.returncode == 0, f"Node 沙箱执行失败: {proc.stderr}"
    assert "PASS" in proc.stdout
