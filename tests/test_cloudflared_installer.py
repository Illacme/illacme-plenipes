# -*- coding: utf-8 -*-
"""
🛰️ [V126.0] Cloudflare Tunnel (cloudflared) Automated Installer Test Suite
测试职责：验证跨平台二进制包推演、已安装状态拦截、模拟下载与解包、以及 /api/plugins/install-deps 接口集成。
🛡️ [SOP-01 规范]：单文件代码行数严格 ≤ 300 行。
"""

import os
import io
import tarfile
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from services.api.routes.gov.context_shards.deps_binary_installer import (
    get_cloudflared_target_path,
    resolve_cloudflared_package_name,
    install_cloudflared_binary
)
from services.api.server import app
from services.api.routes.system import verify_token


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


def test_resolve_cloudflared_package_name_matrix():
    """验证不同操作系统与 CPU 架构推演出的组件文件名与提取格式"""
    with patch("platform.system", return_value="Darwin"), patch("platform.machine", return_value="arm64"):
        pkg, fmt = resolve_cloudflared_package_name()
        assert pkg == "cloudflared-darwin-arm64.tgz"
        assert fmt == "tgz"

    with patch("platform.system", return_value="Darwin"), patch("platform.machine", return_value="x86_64"):
        pkg, fmt = resolve_cloudflared_package_name()
        assert pkg == "cloudflared-darwin-amd64.tgz"
        assert fmt == "tgz"

    with patch("platform.system", return_value="Linux"), patch("platform.machine", return_value="x86_64"):
        pkg, fmt = resolve_cloudflared_package_name()
        assert pkg == "cloudflared-linux-amd64"
        assert fmt == "raw"

    with patch("platform.system", return_value="Windows"), patch("platform.machine", return_value="AMD64"):
        pkg, fmt = resolve_cloudflared_package_name()
        assert pkg == "cloudflared-windows-amd64.exe"
        assert fmt == "raw"


def test_get_cloudflared_target_path():
    """验证目标安装路径位于产品专属隔离目录 ~/.plenipes/bin/"""
    path = get_cloudflared_target_path()
    assert ".plenipes" in path
    assert "bin" in path
    assert "cloudflared" in os.path.basename(path)


def test_install_cloudflared_when_already_available():
    """验证当系统中已存在可用的 cloudflared 时直接返回成功日志，避免重复下载"""
    def dummy_log(level, msg):
        return {"time": "00:00:00", "level": level, "message": msg}

    with patch("shutil.which", return_value="/usr/local/bin/cloudflared"):
        res = install_cloudflared_binary(dummy_log)
        assert res["success"] is True
        messages = [l["message"] for l in res["logs"]]
        assert any("已存在" in m for m in messages)


def test_install_cloudflared_mock_download_flow(tmp_path):
    """模拟下载官方 tgz 压缩包解压部署并验证执行流程"""
    fake_bin_path = str(tmp_path / "cloudflared")

    # 创建一个内存中的 mock tar.gz 包包含可执行文件
    tar_buf = io.BytesIO()
    with tarfile.open(fileobj=tar_buf, mode="w:gz") as tar:
        data = b"#!/bin/sh\necho 'cloudflared version 2026.9.0'\n"
        ti = tarfile.TarInfo(name="cloudflared")
        ti.size = len(data)
        ti.mode = 0o755
        tar.addfile(ti, io.BytesIO(data))
    mock_tar_bytes = tar_buf.getvalue()

    def dummy_log(level, msg):
        return {"time": "00:00:00", "level": level, "message": msg}

    with patch("services.api.routes.gov.context_shards.deps_binary_installer.get_cloudflared_target_path", return_value=fake_bin_path), \
         patch("services.api.routes.gov.context_shards.deps_binary_installer.shutil.which", return_value=None), \
         patch("services.api.routes.gov.context_shards.deps_binary_installer.platform.system", return_value="Darwin"), \
         patch("services.api.routes.gov.context_shards.deps_binary_installer.platform.machine", return_value="arm64"), \
         patch("services.api.routes.gov.context_shards.deps_binary_installer.download_binary_stream", return_value=mock_tar_bytes), \
         patch("subprocess.run") as mock_run:

        mock_proc = MagicMock()
        mock_proc.stdout = "cloudflared version 2026.9.0 (built 2026)"
        mock_proc.stderr = ""
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        res = install_cloudflared_binary(dummy_log)
        assert res["success"] is True
        assert os.path.exists(fake_bin_path)


def test_api_install_deps_cloudflare_endpoint(client):
    """验证 /api/plugins/install-deps 端点能正常路由并执行 cloudflare 安装分流"""
    with patch("shutil.which", return_value="/usr/local/bin/cloudflared"):
        res = client.post("/api/plugins/install-deps", json={"id": "cloudflare"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "logs" in data
        assert any("已存在" in l["message"] for l in data["logs"])
