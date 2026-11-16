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


def test_universal_audio_player_and_asset_sync(tmp_path):
    """验证 Universal 等多主题伴读音频播放条渲染与静态资产同步"""
    from core.podcast import build_universal_audio_player_html, sync_podcast_assets_to_dist
    from core.adapters.egress.ssg.generic_shards.page_renderer import render_html_page

    cache_root = tmp_path / "cache"
    pod_dir = cache_root / "podcasts" / "default"
    pod_dir.mkdir(parents=True, exist_ok=True)
    (pod_dir / "my-post_zh_tech_deep.mp3").write_bytes(b"ID3_FAKE_AUDIO")
    (pod_dir / "my-post_zh_tech_deep.chapters.json").write_text(
        '{"chapters": [{"start_seconds": 0, "start_time": "00:00", "title": "开场导读"}]}',
        encoding="utf-8",
    )

    dist_dir = tmp_path / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    mock_engine = MagicMock()
    mock_engine.imprint_id = "default"
    mock_engine.cache_dir = str(cache_root)
    mock_engine.paths = {"site_dir": str(dist_dir)}
    mock_engine.config.podcast = {"podcast_hub": {"title": "极客主权电台", "email": "host@press.io", "cover_url": "https://press.io/cover.jpg"}}
    mock_engine.config.imprint.site_name = "Test Press"
    mock_engine.config.imprint.tagline = "Tagline"
    mock_engine.config.imprint.author = "Author"
    mock_engine.config.compliance.site_url = "http://localhost:43213"
    mock_engine.meta.get_documents_snapshot.return_value = {"Blog/my-post.md": {"title": "段落级影子缓存", "slug": "my-post", "url": "blog/my-post.html"}}

    fm = {"title": "测试播客文章", "slug": "my-post", "podcast": True, "layout": "blog"}
    widget_html = build_universal_audio_player_html(mock_engine, fm, "zh", root_path="../")
    assert "universal-audio-player" in widget_html
    assert "../podcasts/my-post_zh_tech_deep.mp3" in widget_html
    assert "开场导读" in widget_html

    full_page = render_html_page("<h1>测试播客文章</h1><p>正文</p>", fm, "zh", "blog/my-post.html", "../", engine=mock_engine)
    assert "universal-audio-player" in full_page

    copied = sync_podcast_assets_to_dist(mock_engine, str(dist_dir))
    assert copied == 1
    assert (dist_dir / "podcasts" / "my-post_zh_tech_deep.mp3").exists()
    rss_text = (dist_dir / "podcast-feed.xml").read_text(encoding="utf-8")
    assert "极客主权电台" in rss_text and "段落级影子缓存" in rss_text and "host@press.io" in rss_text

    # 验证 WebBook 与 EPUB 3 电子出版物伴读音频自动内嵌
    import zipfile
    from core.adapters.egress.ebook.webbook import WebBookAdapter
    from core.adapters.egress.ebook.epub import EpubAdapter

    chapters = [{"order": 1, "title": "测试播客文章", "slug": "my-post", "html_body": "<p>正文内容</p>", "assets": [], "headings": []}]
    book_meta = {"title": "伴读典籍", "author": "Author", "publisher": "Press", "is_single_article": True}

    wb_out = tmp_path / "book.html"
    assert WebBookAdapter(engine=mock_engine).bind_book(chapters, dict(book_meta), target_lang="zh", output_file_path=str(wb_out)) is True
    wb_html = wb_out.read_text(encoding="utf-8")
    assert "wb-chapter-audio" in wb_html and "data:audio/mpeg;base64," in wb_html

    epub_out = tmp_path / "book.epub"
    assert EpubAdapter(engine=mock_engine).bind_book(chapters, dict(book_meta), target_lang="zh", output_file_path=str(epub_out)) is True
    with zipfile.ZipFile(epub_out, "r") as zf:
        assert "OEBPS/audio/my-post_zh_tech_deep.mp3" in zf.namelist()
        assert 'media-type="audio/mpeg"' in zf.read("OEBPS/content.opf").decode("utf-8")
        assert "epub-audio-box" in zf.read("OEBPS/text/ch_1.xhtml").decode("utf-8")


def test_ai_compute_tracker_and_emergency_abort():
    """验证实时 AI 算力任务追踪器与紧急熔断协议"""
    import pytest
    from core.adapters.ai.network_mixin import (
        register_ai_call,
        unregister_ai_call,
        get_active_ai_status,
        abort_all_ai_calls,
        check_ai_abort_or_raise,
    )

    dummy_adapter = MagicMock()
    dummy_adapter.node_name = "lmstudio_local"
    orig_session = MagicMock()
    dummy_adapter._session = orig_session

    call_id = register_ai_call(dummy_adapter, {"model": "qwen2.5-7b"})
    try:
        status = get_active_ai_status()
        assert status["active_count"] >= 1
        assert any(t["call_id"] == call_id and t["node"] == "lmstudio_local" for t in status["tasks"])

        aborted = abort_all_ai_calls()
        assert aborted >= 1
        orig_session.close.assert_called_once()

        with pytest.raises(RuntimeError, match="AI_ABORTED_BY_USER"):
            check_ai_abort_or_raise(call_id=call_id)
    finally:
        unregister_ai_call(call_id)
        import core.adapters.ai.network_mixin as nm
        nm._AI_ABORT_UNTIL = 0.0


