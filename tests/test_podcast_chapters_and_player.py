# -*- coding: utf-8 -*-
"""
🎙️ Unit & Contract Tests: Podcast Chapters, Timestamps, Show Notes & Native Theme Player
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
import json
import tempfile
from datetime import datetime, timezone

from core.podcast import (
    PodcastChapter,
    PodcastScript,
    DialogueTurn,
    PodcastScriptEngine,
    PodcastTTSEngine,
    PodcastRSSGenerator,
    PodcastEpisode
)
from themes.sovereign.adapters.sovereign_ui import build_audio_player_widget


def test_podcast_chapter_model_and_formatting():
    """测试章节数据模型的时间格式化与 Show Notes 生成"""
    ch1 = PodcastChapter(title="引言与背景", start_seconds=0, start_time="00:00")
    ch2 = PodcastChapter(title="架构内核揭秘", start_seconds=75, start_time="01:15")
    ch3 = PodcastChapter(title="终局总结", start_seconds=185, start_time="03:05")

    assert ch1.to_dict() == {
        "title": "引言与背景",
        "start_seconds": 0,
        "start_time": "00:00",
        "description": ""
    }
    assert PodcastChapter.format_timestamp(0) == "00:00"
    assert PodcastChapter.format_timestamp(65) == "01:05"
    assert PodcastChapter.format_timestamp(3665) == "61:05"

    shownotes = PodcastChapter.format_shownotes_timeline([ch1, ch2, ch3])
    assert "⏱️ 节目时间轴 (Chapters):" in shownotes
    assert "00:00 引言与背景" in shownotes
    assert "01:15 架构内核揭秘" in shownotes
    assert "03:05 终局总结" in shownotes


def test_script_engine_build_chapters_estimated_and_calibrated():
    """测试剧本引擎根据段落生成章节及毫秒级真实校准"""
    turns = [
        DialogueTurn(speaker="host_a", speaker_name="晓晓", text="大家好，欢迎收听本期技术播客！", intent="intro"),
        DialogueTurn(speaker="host_b", speaker_name="云希", text="今天我们深入剖析全景架构。", intent="dialogue"),
        DialogueTurn(speaker="host_a", speaker_name="晓晓", text="首先来看第一章核心机制。", intent="dialogue"),
        DialogueTurn(speaker="host_b", speaker_name="云希", text="总结来说，这个方案非常稳固。", intent="outro")
    ]
    sections = [
        {"heading": "核心机制深度拆解", "text": "内容..."}
    ]

    # 1. 估算生成
    est_chapters = PodcastScriptEngine.build_chapters(turns, sections, lang="zh")
    assert len(est_chapters) >= 2
    assert est_chapters[0].title == "话题引入与背景"
    assert est_chapters[0].start_seconds == 0
    assert any("核心机制" in c.title for c in est_chapters)

    # 2. 真实毫秒校准 (turn 0: 3000ms, turn 1: 5000ms, turn 2: 4000ms, turn 3: 3000ms)
    durations_ms = [3000, 5000, 4000, 3000]
    calibrated_chapters = PodcastScriptEngine.build_chapters(
        turns, sections, lang="zh", turn_durations_ms=durations_ms
    )
    assert len(calibrated_chapters) >= 2
    # turn 0 (3000ms + 400ms pause) -> turn 1 (first section) starts at 3.4s -> int(3.4) = 3s
    section_ch = [c for c in calibrated_chapters if "核心机制" in c.title][0]
    assert section_ch.start_seconds == 3
    assert section_ch.start_time == "00:03"


def test_tts_engine_sidecar_generation(monkeypatch):
    """测试语音合成产物自动生成 .chapters.json 伴随文件"""
    import asyncio
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_mp3 = os.path.join(tmp_dir, "test_article_zh_tech_deep.mp3")

        # 模拟合成单个台词 (返回有效 MP3 伪数据)
        fake_audio = b"\xff\xfb\x90\x00" * 200
        async def mock_synth_turn(*args, **kwargs):
            return fake_audio

        monkeypatch.setattr(PodcastTTSEngine, "synthesize_turn_audio", mock_synth_turn)

        script = PodcastScript(
            title="测试单轨伴读播客",
            topic="技术评测",
            lang="zh",
            style="tech_deep",
            turns=[
                DialogueTurn(speaker="host_a", speaker_name="晓晓", text="欢迎收听！", intent="intro"),
                DialogueTurn(speaker="host_b", speaker_name="云希", text="我们直奔主题。", intent="dialogue"),
                DialogueTurn(speaker="host_a", speaker_name="晓晓", text="下期再会！", intent="outro")
            ],
            sections=[{"heading": "设计模式剖析", "text": "细节"}]
        )

        res = asyncio.run(PodcastTTSEngine.synthesize_script(
            script=script,
            output_file_path=out_mp3,
            bgm_style="none"
        ))

        assert os.path.exists(out_mp3)
        assert res.file_size_bytes > 0
        assert len(res.chapters) > 0

        # 验证 Sidecar JSON 文件已正确生成
        sidecar_path = os.path.join(tmp_dir, "test_article_zh_tech_deep.chapters.json")
        assert os.path.exists(sidecar_path)

        with open(sidecar_path, "r", encoding="utf-8") as f:
            sc_data = json.load(f)
            assert sc_data["title"] == "测试单轨伴读播客"
            assert "chapters" in sc_data
            assert len(sc_data["chapters"]) == len(res.chapters)
            assert "⏱️ 节目时间轴" in sc_data["shownotes"]


def test_podcast_rss_generator_with_chapters():
    """测试 RSS 订阅源中自动嵌入节目时间轴与 Show Notes"""
    chaps = [
        {"title": "背景介绍", "start_seconds": 0, "start_time": "00:00"},
        {"title": "实战演示", "start_seconds": 90, "start_time": "01:30"}
    ]
    ep = PodcastEpisode(
        title="第101期：分布式架构",
        audio_url="https://cdn.example.com/podcast.mp3",
        audio_size_bytes=1048576,
        duration_sec=300,
        pub_date=datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc),
        description="深度探讨分布式系统",
        chapters=chaps
    )

    xml_content = PodcastRSSGenerator.generate_feed_xml(
        channel_title="Sovereign Podcast",
        channel_link="https://example.com",
        channel_desc="技术播客",
        episodes=[ep]
    )

    assert "<rss version=\"2.0\"" in xml_content
    assert "第101期：分布式架构" in xml_content
    assert "https://cdn.example.com/podcast.mp3" in xml_content
    assert "⏱️ 节目时间轴 (Chapters):" in xml_content
    assert "00:00 背景介绍" in xml_content
    assert "01:30 实战演示" in xml_content


def test_sovereign_theme_audio_player_with_chapters(monkeypatch):
    """测试官方 Sovereign 主题毛玻璃音频播放器解析 Sidecar 章节渲染药丸"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 伪造 cache 目录与播客文件
        imprint_cache = os.path.join(tmp_dir, ".plenipes", "cache", "podcasts", "default")
        os.makedirs(imprint_cache, exist_ok=True)

        slug = "architect-guide"
        mp3_name = f"{slug}_zh_tech_deep.mp3"
        sc_name = f"{slug}_zh_tech_deep.chapters.json"

        with open(os.path.join(imprint_cache, mp3_name), "wb") as f:
            f.write(b"RIFF....WAVE")

        with open(os.path.join(imprint_cache, sc_name), "w", encoding="utf-8") as f:
            json.dump({
                "chapters": [
                    {"title": "开篇简介", "start_seconds": 0, "start_time": "00:00"},
                    {"title": "核心重构", "start_seconds": 150, "start_time": "02:30"}
                ]
            }, f)

        # 替换工作目录模拟
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_dir)
            class MockAdapter:
                engine = None

            html = build_audio_player_widget(
                adapter=MockAdapter(),
                fm={"slug": slug},
                lang="zh",
                root_path="/"
            )

            assert "sovereign-audio-player" in html
            assert "audio-chapters-scroll" in html
            assert "chapter-pill" in html
            assert 'data-time="0"' in html
            assert '00:00' in html
            assert '开篇简介' in html
            assert 'data-time="150"' in html
            assert '02:30' in html
            assert '核心重构' in html

            # 验证 Frontmatter 显式关闭 (podcast: False) 拦截
            html_disabled = build_audio_player_widget(
                adapter=MockAdapter(),
                fm={"slug": slug, "podcast": False},
                lang="zh",
                root_path="/"
            )
            assert html_disabled == ""

            # 验证 Frontmatter 自定义外部人声音频外链 (podcast_audio: ...)
            html_custom = build_audio_player_widget(
                adapter=MockAdapter(),
                fm={"slug": "external-audio-doc", "podcast_audio": "https://cdn.example.com/human-show.mp3"},
                lang="zh",
                root_path="/"
            )
            assert "sovereign-audio-player" in html_custom
            assert 'data-audio-src="https://cdn.example.com/human-show.mp3"' in html_custom
        finally:
            os.chdir(old_cwd)


def test_api_routes_expose_chapters():
    """测试 REST API 接口暴露 chapters 与 shownotes_formatted"""
    from fastapi.testclient import TestClient
    from services.api.server import app

    client = TestClient(app)

    resp = client.post(
        "/api/podcast/script/extract",
        json={
            "content": "# 测试架构演进\n\n## 模块解耦\n解耦内容说明...\n\n## 高性能缓存\n缓存设计...",
            "lang": "zh",
            "style": "tech_deep",
            "max_turns": 8
        },
        headers={"Authorization": "Bearer test-token"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "chapters" in data
    assert len(data["chapters"]) >= 2
    assert "shownotes_formatted" in data
    assert "⏱️ 节目时间轴" in data["shownotes_formatted"]

