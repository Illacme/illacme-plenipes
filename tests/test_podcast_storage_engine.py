# -*- coding: utf-8 -*-
"""
🧪 Test Suite for Podcast Storage Engine & Diagnostics Routes
验证：
1. 播客专属音频云存储 (Cloudflare R2 / S3) 配置感知与 is_configured 判定；
2. 端点解析 (R2 Account ID -> Endpoint URL)；
3. 音频 CDN 直链重写与路径前缀组装；
4. 模拟 boto3 S3 客户端文件上传转储流程；
5. 存储桶健康探针 (probe_storage_connectivity)；
6. /api/podcast/storage/status 与 /api/podcast/storage/sync REST 端点；
7. /api/podcast/diagnostics/{imprint_id} 全网播客发行规范诊断。
🛡️ [SOP-01] 物理行数严格收敛于 300 行以内。
"""

import os
import tempfile
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from core.podcast.podcast_storage_engine import PodcastStorageEngine
from services.api.server import app

client = TestClient(app)


def test_storage_engine_config_and_endpoint():
    """验证配置感知与 S3/R2 Endpoint 智能生成"""
    mock_engine = MagicMock()
    mock_engine.config.podcast = {
        "podcast_r2_storage": {
            "enabled": True,
            "provider": "cloudflare_r2",
            "account_id": "test_account_123",
            "bucket": "my-podcasts",
            "access_key_id": "ak_123",
            "secret_access_key": "sk_456",
            "public_cdn_url": "https://audio.example.com",
            "path_prefix": "episodes"
        }
    }

    # 1. 验证已配置状态
    assert PodcastStorageEngine.is_configured(mock_engine) is True

    # 2. 验证 R2 端点自动拼接
    cfg = PodcastStorageEngine.get_config(mock_engine)
    endpoint = PodcastStorageEngine.get_endpoint_url(cfg)
    assert endpoint == "https://test_account_123.r2.cloudflarestorage.com"

    # 3. 验证未配置状态
    empty_engine = MagicMock()
    empty_engine.config.podcast = {}
    assert PodcastStorageEngine.is_configured(empty_engine) is False


def test_audio_public_url_cdn_rewrite():
    """验证播客音频公开访问链接在配置 CDN 后的自动重写"""
    mock_engine = MagicMock()
    mock_engine.config.podcast = {
        "podcast_r2_storage": {
            "enabled": True,
            "bucket": "my-podcasts",
            "access_key_id": "ak",
            "secret_access_key": "sk",
            "public_cdn_url": "https://cdn.podcasts.com",
            "path_prefix": "episodes"
        }
    }

    local_url = "http://localhost:43212/api/podcast/audio/default/test.mp3"
    rewritten = PodcastStorageEngine.get_audio_public_url("test.mp3", local_url, mock_engine)
    assert rewritten == "https://cdn.podcasts.com/episodes/test.mp3"

    # 禁用时应回退到本地直链
    mock_engine.config.podcast["podcast_r2_storage"]["enabled"] = False
    fallback = PodcastStorageEngine.get_audio_public_url("test.mp3", local_url, mock_engine)
    assert fallback == local_url


def test_upload_audio_mocked_s3():
    """模拟 S3 客户端文件上传转储流程"""
    mock_engine = MagicMock()
    mock_engine.config.podcast = {
        "podcast_r2_storage": {
            "enabled": True,
            "provider": "cloudflare_r2",
            "account_id": "acc_123",
            "bucket": "pod-bucket",
            "access_key_id": "ak",
            "secret_access_key": "sk",
            "public_cdn_url": "https://audio.pod.com",
            "path_prefix": "audio"
        }
    }

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
        tf.write(b"ID3_MOCK_MP3_CONTENT")
        tmp_mp3 = tf.name

    try:
        mock_s3 = MagicMock()
        with patch("boto3.session.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session.client.return_value = mock_s3
            mock_session_cls.return_value = mock_session

            res = PodcastStorageEngine.upload_audio(tmp_mp3, "episode1.mp3", mock_engine)

            assert res["success"] is True
            assert res["cdn_url"] == "https://audio.pod.com/audio/episode1.mp3"
            assert res["bucket"] == "pod-bucket"
            mock_s3.put_object.assert_called_once()
    finally:
        if os.path.exists(tmp_mp3):
            os.remove(tmp_mp3)


def test_probe_storage_connectivity():
    """测试存储桶探针握手检测"""
    mock_engine = MagicMock()
    mock_engine.config.podcast = {
        "podcast_r2_storage": {
            "enabled": True,
            "bucket": "probe-bucket",
            "access_key_id": "ak",
            "secret_access_key": "sk"
        }
    }

    with patch("boto3.session.Session") as mock_session_cls:
        mock_s3 = MagicMock()
        mock_session = MagicMock()
        mock_session.client.return_value = mock_s3
        mock_session_cls.return_value = mock_session

        probe_res = PodcastStorageEngine.probe_storage_connectivity(mock_engine)
        assert probe_res["success"] is True
        assert probe_res["healthy"] is True
        mock_s3.head_bucket.assert_called_once_with(Bucket="probe-bucket")


def test_api_storage_status_and_diagnostics():
    """测试 /api/podcast/storage/status 与 /api/podcast/diagnostics 端点"""
    mock_engine = MagicMock()
    mock_engine.config.system.data_root = "/tmp"
    mock_engine.config.podcast = {
        "podcast_hub": {
            "title": "测试技术对谈",
            "email": "pod@test.com",
            "cover_url": "https://img.test.com/cover.jpg"
        },
        "podcast_r2_storage": {
            "enabled": True,
            "bucket": "b",
            "access_key_id": "ak",
            "secret_access_key": "sk",
            "public_cdn_url": "https://cdn.test.com"
        }
    }

    with patch("services.api.routes.podcast_storage_routes.get_global_engine", return_value=mock_engine):
        # 1. 状态查询
        resp_status = client.get("/api/podcast/storage/status")
        assert resp_status.status_code == 200
        data = resp_status.json()
        assert data["status"] == "success"
        assert data["configured"] is True
        assert data["public_cdn_url"] == "https://cdn.test.com"

        # 2. 诊断报告
        resp_diag = client.get("/api/podcast/diagnostics/default")
        assert resp_diag.status_code == 200
        diag = resp_diag.json()
        assert diag["status"] == "success"
        assert "health_score" in diag
        assert diag["cdn_accelerated"] is True
        assert len(diag["checks"]) >= 4

        # 3. 播客分发总览
        resp_ov = client.get("/api/podcast/overview")
        assert resp_ov.status_code == 200
        ov = resp_ov.json()
        assert ov["status"] == "success"
        assert "metrics" in ov
        assert "platforms" in ov
        assert "episodes" in ov
        assert len(ov["platforms"]) >= 6

