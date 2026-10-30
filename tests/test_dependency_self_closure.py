# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Critical Dependency Self-Closure Test Suite
测试职责：验证关键依赖自闭环机制、编译清单完整性、冻结沙箱降级与 Netlify Zero-CLI 原生直传。
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# 确保项目根目录在 sys.path
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from desktop.packager_manifest import get_hidden_imports, get_data_mappings
from core.adapters.egress.publishers.base import BasePublisher
from adapters.egress.publishers.netlify import NetlifyPublisher
from adapters.egress.publishers.netlify_utils import deploy_via_direct_api, probe_site_api
from adapters.egress.publishers.vercel import VercelPublisher
from adapters.egress.publishers.cloudflare_pages import CloudflarePagesPublisher
from themes.sovereign.adapters.sovereign import SovereignSSGAdapter


class DummyPublisher(BasePublisher):
    PLUGIN_ID = "dummy"

    def push(self, bundle_path: str, metadata: dict) -> dict:
        return {"status": "ok"}


def test_packager_manifest_critical_modules_coverage():
    """断言打包编译清单包含全部文档装订、PDF、图像与网络自闭环依赖"""
    hidden = get_hidden_imports()

    # 1. 基础运行环境与网络协议
    assert "fastapi" in hidden
    assert "uvicorn.logging" in hidden
    assert "cryptography" in hidden
    assert "requests" in hidden
    assert "watchdog" in hidden
    assert "orjson" in hidden
    assert "qrcode" in hidden

    # 2. 电子书装订与核心导出引擎 (Word/PDF/MathML)
    assert "docx" in hidden
    assert "reportlab" in hidden
    assert "pypdf" in hidden
    assert "fitz" in hidden
    assert "mathml2omml" in hidden
    assert "latex2mathml" in hidden
    assert "PIL" in hidden

    # 3. 动态原生主题适配器
    assert "themes.sovereign.adapters.sovereign" in hidden

    # 4. 资源映射完整性
    mappings = get_data_mappings("build/desktop/staged_themes")
    dst_dirs = [m[1] for m in mappings]
    assert "web/dashboard" in dst_dirs
    assert "themes" in dst_dirs
    assert "configs" in dst_dirs


def test_ensure_python_dependency_frozen_protection():
    """断言独立封装环境 (sys.frozen) 下禁止调用外部 pip，保障运行时安全自闭环"""
    pub = DummyPublisher({})

    # 模拟处于 PyInstaller 冻结环境
    with patch.object(sys, "frozen", True, create=True):
        result = pub.ensure_python_dependency("non_existent_module_xyz")
        assert result is False


def test_ensure_npm_dependency_graceful_handling():
    """断言在缺失 Node/npm 环境下平滑报告感知信息，不引发崩溃"""
    pub = DummyPublisher({})

    with patch("shutil.which", return_value=None):
        with patch("os.path.exists", return_value=False):
            result = pub.ensure_npm_dependency("non_existent_tool_abc")
            assert result is False


def test_sovereign_theme_zero_external_dependency():
    """断言主权原生主题满足零外部技术栈依赖契约"""
    assert SovereignSSGAdapter.PLUGIN_ID == "sovereign"
    build_cmd = SovereignSSGAdapter.get_build_command()
    assert "npm" not in build_cmd
    assert "node" not in build_cmd


def test_netlify_publisher_zero_cli_direct_api_success(tmp_path):
    """断言 Netlify 在宿主机无 CLI 情况下可无缝降级为 Native Direct API 纯 HTTP 直传"""
    # 创建模拟静态产物目录
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    (dist_dir / "index.html").write_text("<h1>Hello Sovereign</h1>", encoding="utf-8")
    (dist_dir / "style.css").write_text("body { background: #000; }", encoding="utf-8")

    pub = NetlifyPublisher({
        "site_id": "test-site-12345",
        "auth_token": "secret_token_abc",
        "prod": True
    })

    # 1. 断言在无 CLI 情况下健康度探针依然为 True (双模就绪)
    with patch.object(pub, "_has_cli", return_value=False):
        assert pub.is_healthy() is True

    # 2. 模拟 Netlify OpenAPI 返回成功响应
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "deploy_67890",
        "state": "ready",
        "ssl_url": "https://test-site.netlify.app",
        "deploy_ssl_url": "https://deploy-67890.netlify.app"
    }

    with patch.object(pub, "_has_cli", return_value=False), patch("shutil.which", return_value=None):
        with patch("requests.post", return_value=mock_resp) as mock_post:
            result = pub.push(str(dist_dir), {"title": "Test Deploy"})

            assert result["status"] == "success"
            assert result["url"] == "https://test-site.netlify.app"
            assert "Zero-CLI" in result["message"]
            assert mock_post.called

            # 校验请求 URL 与认证头
            call_args, call_kwargs = mock_post.call_args
            assert call_args[0] == "https://api.netlify.com/api/v1/sites/test-site-12345/deploys"
            assert call_kwargs["headers"]["Authorization"] == "Bearer secret_token_abc"
            assert call_kwargs["headers"]["Content-Type"] == "application/zip"


def test_netlify_probe_site_api():
    """断言 Netlify 站点 API 连通性探针"""
    mock_resp = MagicMock()
    mock_resp.status_code = 200

    with patch("requests.get", return_value=mock_resp):
        assert probe_site_api("test-site", "test-token") is True

    mock_resp.status_code = 404
    with patch("requests.get", return_value=mock_resp):
        assert probe_site_api("test-site", "test-token") is False


def test_vercel_publisher_zero_cli_direct_api_success(tmp_path):
    """断言 Vercel 在宿主机无 CLI 情况下可无缝降级为 Native Direct API 纯 HTTP 直传"""
    dist_dir = tmp_path / "dist_vercel"
    dist_dir.mkdir()
    (dist_dir / "index.html").write_text("<h1>Hello Vercel Sovereign</h1>", encoding="utf-8")

    pub = VercelPublisher({
        "project_name": "my-press-site",
        "token": "vercel_secret_token",
        "prod": True
    })

    # 1. 无 CLI 下健康探针仍为 True (配置了 token 即可走 Direct API)
    with patch.object(pub, "_has_cli", return_value=False):
        assert pub.is_healthy() is True

    # 2. 模拟 Vercel API 返回部署成功
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "dpl_vercel123",
        "url": "my-press-site-xyz.vercel.app",
        "readyState": "READY"
    }

    with patch.object(pub, "_has_cli", return_value=False), patch("shutil.which", return_value=None):
        with patch("requests.post", return_value=mock_resp) as mock_post:
            result = pub.push(str(dist_dir), {"title": "Test Vercel Deploy"})

            assert result["status"] == "success"
            assert result["url"] == "https://my-press-site.vercel.app"
            assert "Zero-CLI" in result["message"]
            assert mock_post.called

            # 校验请求 URL 与认证头
            call_args, call_kwargs = mock_post.call_args
            assert "api.vercel.com/v13/deployments" in call_args[0]
            assert call_kwargs["headers"]["Authorization"] == "Bearer vercel_secret_token"
            assert call_kwargs["json"]["target"] == "production"


def test_cloudflare_pages_publisher_zero_cli_direct_api_success(tmp_path):
    """断言 Cloudflare Pages 在宿主机无 Wrangler 情况下可无缝降级为 Native Direct API 直传"""
    dist_dir = tmp_path / "dist_cf"
    dist_dir.mkdir()
    (dist_dir / "index.html").write_text("<h1>Hello CF Pages Sovereign</h1>", encoding="utf-8")

    pub = CloudflarePagesPublisher({
        "project_name": "my-cf-site",
        "account_id": "cf_account_123",
        "token": "cf_secret_token",
        "branch": "production"
    })

    # 1. 无 CLI 下健康探针仍为 True
    with patch.object(pub, "_has_cli", return_value=False):
        assert pub.is_healthy() is True

    # 2. 模拟 check-missing 与 create deployment API
    mock_check_resp = MagicMock()
    mock_check_resp.status_code = 200
    mock_check_resp.json.return_value = {"result": [], "jwt": "jwt_token_xyz"}

    mock_deploy_resp = MagicMock()
    mock_deploy_resp.status_code = 200
    mock_deploy_resp.json.return_value = {
        "result": {
            "id": "cf_deploy_abc",
            "url": "https://hash.my-cf-site.pages.dev"
        }
    }

    with patch.object(pub, "_has_cli", return_value=False):
        with patch("requests.post", side_effect=[mock_check_resp, mock_deploy_resp]) as mock_post:
            result = pub.push(str(dist_dir), {"title": "Test CF Deploy"})

            assert result["status"] == "success"
            assert result["project"] == "my-cf-site"
            assert "pages.dev" in result["url"]
            assert "Zero-CLI" in result["message"]
            assert mock_post.call_count == 2


