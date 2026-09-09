# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch, MagicMock
from services.api.routes.gov.actions_shards.health_radar_ops import probe_single_url, probe_all_urls_impl

def test_probe_single_url_success():
    """测试单个 URL 正常 200 响应时的健康状态与延迟识别"""
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.headers = {
        "server": "Vercel",
        "x-vercel-id": "hkg1::iad1::12345"
    }

    with patch("urllib.request.build_opener") as mock_build_opener:
        mock_opener = MagicMock()
        mock_opener.open.return_value.__enter__.return_value = mock_resp
        mock_build_opener.return_value = mock_opener

        res = probe_single_url("https://illacme-press.vercel.app/")
        assert res["url"] == "https://illacme-press.vercel.app/"
        assert res["status_code"] == 200
        assert res["is_healthy"] is True
        assert res["server"] == "Vercel"
        assert res["latency_ms"] >= 1


def test_probe_single_url_github_pages():
    """测试 GitHub Pages 厂商指纹识别"""
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.headers = {
        "server": "GitHub.com",
        "x-github-request-id": "ABCD:1234"
    }

    with patch("urllib.request.build_opener") as mock_build_opener:
        mock_opener = MagicMock()
        mock_opener.open.return_value.__enter__.return_value = mock_resp
        mock_build_opener.return_value = mock_opener

        res = probe_single_url("https://illacme.github.io/illacme-press/")
        assert res["status_code"] == 200
        assert res["is_healthy"] is True
        assert res["server"] == "GitHub Pages"


def test_probe_all_urls_batch():
    """测试多路并发批量探测接口"""
    with patch("services.api.routes.gov.actions_shards.health_radar_ops.probe_single_url") as mock_probe:
        mock_probe.side_effect = lambda u, proxy=None: {
            "url": u,
            "status_code": 200,
            "latency_ms": 50,
            "server": "Edge CDN",
            "is_healthy": True,
            "message": "OK"
        }

        urls = [
            "https://illacme-press.vercel.app/",
            "https://illacme.github.io/illacme-press/"
        ]
        results = probe_all_urls_impl(urls)
        assert len(results) == 2
        assert all(r["is_healthy"] for r in results)
