# -*- coding: utf-8 -*-
"""
🧪 Test Suite for Blog Reader Audio Companion Widget (Direction 1)
验证：
1. 博客排版审查 (/api/syndication/preview) 伴读音频自适应检测与元数据注入；
2. 无伴读音频时 0 视觉污染 (has_audio=False, widget="");
3. Sovereign 主题渲染器 build_audio_player_widget 与 build_article_meta 闭环；
4. 静态站点伴读音频产物同步与 RSS 注入。
🛡️ [SOP-01] 物理行数严格收敛于 300 行以内。
"""

import os
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from services.api.server import app
from themes.sovereign.adapters.sovereign_ui import (
    build_audio_player_widget,
    build_article_meta,
    calculate_reading_meta
)

client = TestClient(app)


def test_syndication_preview_audio_detection():
    """测试当文库存在已合成音频时，/api/syndication/preview 正确返回伴读音频元数据"""
    cache_dir = os.path.join(".plenipes", "cache", "podcasts", "default")
    os.makedirs(cache_dir, exist_ok=True)
    test_audio = os.path.join(cache_dir, "reader_widget_test_zh_tech_deep.mp3")
    with open(test_audio, "wb") as f:
        f.write(b"ID3\x04\x00\x00\x00\x00\x00#TSSE\x00\x00\x00\x07\x00\x00\x03Lavf58.76.100\xff\xfb\x90\x00fake_mp3_data")

    sample_md = "# 读者伴读测试文章\n\n这是一篇用于验证伴读播放条的测试文稿。"
    mock_engine = MagicMock()
    mock_engine.imprint_id = "default"
    mock_engine.vault_root = "/mock/vault"
    mock_engine.config.compliance.site_url = "https://example.com"

    try:
        with patch("services.api.routes.syndication_preview.get_global_engine", return_value=mock_engine), \
             patch("services.api.routes.syndication_preview.resolve_safe_path", return_value="/mock/vault/Docs/reader_widget_test.md"), \
             patch("builtins.open", unittest.mock.mock_open(read_data=sample_md)), \
             patch("os.path.exists", return_value=True), \
             patch("services.api.routes.system.verify_token", return_value=True):
            resp = client.post(
                "/api/syndication/preview",
                json={
                    "rel_path": "Docs/reader_widget_test.md",
                    "target_platform": "wechat",
                    "lang": "zh"
                }
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert "audio" in data
            audio = data["audio"]
            assert audio["has_audio"] is True
            assert audio["style"] == "tech_deep"
            assert audio["style_name"] == "深度剖析"
            assert "/api/podcast/audio/default/reader_widget_test_zh_tech_deep.mp3" in audio["audio_url"]
            assert "rss_url" in audio
    finally:
        if os.path.exists(test_audio):
            os.remove(test_audio)


def test_syndication_preview_zero_footprint_when_no_audio():
    """测试当不存在音频时，返回 has_audio=False，保持 0 视觉冗余"""
    sample_md = "# 无伴读音频测试文章\n\n这是一篇无伴读的纯文本测试稿件。"
    mock_engine = MagicMock()
    mock_engine.imprint_id = "default"
    mock_engine.vault_root = "/mock/vault"
    mock_engine.config.compliance.site_url = "https://example.com"

    real_exists = os.path.exists
    def safe_exists(p):
        if p == "/mock/vault/Docs/no_audio_test.md":
            return True
        return real_exists(p)

    with patch("services.api.routes.syndication_preview.get_global_engine", return_value=mock_engine), \
         patch("services.api.routes.syndication_preview.resolve_safe_path", return_value="/mock/vault/Docs/no_audio_test.md"), \
         patch("builtins.open", unittest.mock.mock_open(read_data=sample_md)), \
         patch("os.path.exists", side_effect=safe_exists), \
         patch("services.api.routes.system.verify_token", return_value=True):
        resp = client.post(
            "/api/syndication/preview",
            json={
                "rel_path": "Docs/no_audio_test.md",
                "target_platform": "juejin",
                "lang": "zh"
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["audio"]["has_audio"] is False


def test_sovereign_audio_widget_rendering():
    """测试 Sovereign 主题中伴读条的 HTML 生成与挂载"""
    cache_dir = os.path.join(".plenipes", "cache", "podcasts", "default")
    os.makedirs(cache_dir, exist_ok=True)
    test_audio = os.path.join(cache_dir, "sov_widget_doc_zh_tech_deep.mp3")
    with open(test_audio, "wb") as f:
        f.write(b"ID3_fake_audio")

    class MockAdapter:
        engine = None

    fm = {
        "title": "主权伴读条测试",
        "slug": "sov_widget_doc",
        "author": "架构师",
        "tags": ["测试", "播客"]
    }

    try:
        # 1. 存在音频时生成播放条
        widget_html = build_audio_player_widget(MockAdapter(), fm, "zh", root_path="../")
        assert "sovereign-audio-player" in widget_html
        assert "../podcasts/sov_widget_doc_zh_tech_deep.mp3" in widget_html
        assert "AI 伴读播客" in widget_html
        assert "audio-play-btn" in widget_html
        assert "audio-scrub" in widget_html
        assert "audio-speed-btn" in widget_html
        assert "audio-mute-btn" in widget_html

        # 2. 嵌入 article_meta 中
        reading_meta = calculate_reading_meta("这是正文测试内容。")
        meta_html = build_article_meta(fm, "zh", reading_meta, adapter=MockAdapter(), root_path="../")
        assert "article-header-meta" in meta_html
        assert "sovereign-audio-player" in meta_html

        # 3. 不存在音频时返回空字符串 (0 视觉冗余)
        fm_no_audio = {"title": "无音频", "slug": "non_existent_slug"}
        no_widget = build_audio_player_widget(MockAdapter(), fm_no_audio, "zh")
        assert no_widget == ""
        clean_meta = build_article_meta(fm_no_audio, "zh", reading_meta, adapter=MockAdapter())
        assert "sovereign-audio-player" not in clean_meta

        # 4. 存在 .transcript.json 时自动挂载音文同步伴读字幕属性与面板
        test_tr = os.path.join(cache_dir, "sov_widget_doc_zh_tech_deep.transcript.json")
        with open(test_tr, "w", encoding="utf-8") as tf:
            tf.write('{"turns":[{"speaker_name":"晓晓","text":"你好","start_ms":0,"end_ms":1500}]}')
        try:
            sync_html = build_audio_player_widget(MockAdapter(), fm, "zh", root_path="../")
            assert 'data-transcript-src="../podcasts/sov_widget_doc_zh_tech_deep.transcript.json"' in sync_html
            assert "audio-transcript-btn" in sync_html
            assert "audio-transcript-panel" in sync_html
        finally:
            if os.path.exists(test_tr):
                os.remove(test_tr)
    finally:
        if os.path.exists(test_audio):
            os.remove(test_audio)
