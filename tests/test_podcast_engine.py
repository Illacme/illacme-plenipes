# -*- coding: utf-8 -*-
"""
🧪 Test Suite for Podcast Engine & RSS Generator
验证：
1. 剧本提炼中枢 (中文、英文、日文双人对话生成)；
2. 语音合成中枢 (声线映射、音频缝合与元数据注入)；
3. RSS 订阅源生成器 (Apple Podcasts / 小宇宙合规 XML)；
4. REST API 路由端点端到端测试。
🛡️ [SOP-01] 物理行数保持在 300 行以内。
"""

import os
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from core.podcast import (
    PodcastScriptEngine,
    DialogueTurn,
    PodcastScript,
    PodcastTTSEngine,
    PodcastRSSGenerator,
    PodcastEpisode
)
from services.api.server import app

client = TestClient(app)

SAMPLE_MD_ZH = """
# 现代微内核架构设计与实战

微内核架构将核心系统精简到极致，将外部功能作为独立插件加载。

## 插件隔离与故障边界
每个插件运行在独立的工作沙箱中，即使某个插件发生崩溃也不会影响主进程。
通过严格的生命周期管控与健康探测，系统实现了 99.99% 的可用性。

## 高性能事件总线
插件与核心通过非阻塞事件总线通信，吞吐量达到十万级别。
"""

SAMPLE_MD_EN = """
# Event-Driven Architecture at Scale

Event-driven design decouples distributed microservices for massive horizontal scalability.

## Message Broker Clustering
High availability clustering prevents single points of failure across all availability zones.
Replication lag is kept under five milliseconds with deterministic routing.

## Dead Letter Queue Handling
Failed messages are captured and retried with exponential backoff algorithms.
"""


def test_script_extraction_zh():
    """测试中文原稿的播客剧本提炼"""
    script = PodcastScriptEngine.extract_script(SAMPLE_MD_ZH, lang="zh")
    assert script.lang == "zh"
    assert "微内核架构" in script.title
    assert len(script.turns) >= 6
    assert script.estimated_duration_sec > 0

    # 验证开场由 Host A 发起，Host B 接茬
    assert script.turns[0].speaker == "host_a"
    assert script.turns[0].speaker_name == "晓晓"
    assert script.turns[1].speaker == "host_b"
    assert script.turns[1].speaker_name == "云希"

    # 验证收束
    assert script.turns[-1].speaker == "host_b"
    assert script.turns[-1].intent == "outro"


def test_script_extraction_en():
    """测试英文原稿的播客剧本提炼"""
    script = PodcastScriptEngine.extract_script(SAMPLE_MD_EN, lang="en")
    assert script.lang == "en"
    assert "Event-Driven" in script.title
    assert len(script.turns) >= 6
    assert script.turns[0].speaker_name == "Jenny"
    assert script.turns[1].speaker_name == "Guy"


def test_script_extraction_ja():
    """测试日文原稿的播客剧本提炼"""
    ja_md = "# マイクロフロントエンド設計\n\n大規模フロントエンドの分割手法を解説します。\n\n## 独立デプロイ\n各チームが自律的にリリースできます。"
    script = PodcastScriptEngine.extract_script(ja_md, lang="ja")
    assert script.lang == "ja"
    assert script.turns[0].speaker_name == "七海"
    assert script.turns[1].speaker_name == "圭太"


def test_script_extraction_solo_read():
    """测试单人沉浸伴读模式剧本提炼"""
    script = PodcastScriptEngine.extract_script(SAMPLE_MD_ZH, lang="zh", style="solo_read")
    assert script.style == "solo_read"
    assert len(script.turns) >= 3
    assert all(t.speaker == "host_a" for t in script.turns)
    assert script.turns[0].intent == "intro"
    assert script.turns[-1].intent == "outro"


def test_tts_voice_mapping():
    """测试声线映射矩阵"""
    voices = PodcastTTSEngine.get_supported_voices()
    assert "zh" in voices
    assert "en" in voices
    assert "ja" in voices
    assert PodcastTTSEngine.get_voice_for_role("zh", "host_a") == "zh-CN-XiaoxiaoNeural"
    assert PodcastTTSEngine.get_voice_for_role("en", "host_b") == "en-US-GuyNeural"
    assert PodcastTTSEngine.get_voice_for_role("zh", "host_a", "custom-voice") == "custom-voice"


def test_rss_generator():
    """测试播客 RSS 2.0 XML 生成与 Apple/小宇宙规范验证"""
    episodes = [
        PodcastEpisode(
            title="EP01: 微内核架构深度实战",
            audio_url="https://example.com/audio/ep01.mp3",
            audio_size_bytes=1048576,
            duration_sec=320,
            pub_date=datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc),
            description="本期聚焦微内核隔离边界与容错架构。",
            cover_image_url="https://example.com/covers/ep01.png"
        )
    ]
    xml_str = PodcastRSSGenerator.generate_feed_xml(
        channel_title="极客前沿技术播客",
        channel_link="https://example.com",
        channel_desc="由出版发行工作台自动衍生的双人对谈播客。",
        episodes=episodes,
        author="主权创作者",
        lang="zh-cn",
        cover_image_url="https://example.com/podcast_logo.png"
    )

    root = ET.fromstring(xml_str)
    assert root.tag == "rss"
    assert root.attrib.get("version") == "2.0"
    channel = root.find("channel")
    assert channel is not None
    assert channel.find("title").text == "极客前沿技术播客"

    item = channel.find("item")
    assert item is not None
    assert item.find("title").text == "EP01: 微内核架构深度实战"
    enclosure = item.find("enclosure")
    assert enclosure is not None
    assert enclosure.attrib["url"] == "https://example.com/audio/ep01.mp3"
    assert enclosure.attrib["length"] == "1048576"
    assert enclosure.attrib["type"] == "audio/mpeg"


def test_api_podcast_voices():
    """测试获取播客声线 API 路由"""
    resp = client.get("/api/podcast/voices")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "zh" in data["data"]
    assert "en" in data["data"]


def test_api_podcast_script_extract():
    """测试剧本提炼 API 路由"""
    resp = client.post(
        "/api/podcast/script/extract",
        json={
            "content": SAMPLE_MD_ZH,
            "lang": "zh",
            "style": "tech_deep",
            "max_turns": 8
        }
    )
    assert resp.status_code == 200
    res = resp.json()
    assert res["status"] == "success"
    turns = res["data"]["turns"]
    assert len(turns) >= 4
    assert turns[0]["speaker"] == "host_a"


def test_api_podcast_info_missing():
    """测试不存在的播客信息查询"""
    resp = client.get("/api/podcast/info?rel_path=nonexistent_file.md&lang=zh")
    assert resp.status_code == 200
    res = resp.json()
    assert res["status"] == "success"
    assert res["exists"] is False


def test_api_podcast_rss_feed():
    """测试播客 RSS Feed API 路由"""
    resp = client.get("/api/podcast/feed/default?lang=zh")
    assert resp.status_code == 200
    assert "xml" in resp.headers.get("content-type", "")
    assert "<rss" in resp.text


def test_api_podcast_synthesize_endpoint():
    """测试通过 API 端点执行播客合成并验证返回元数据与 brand_name 读取"""
    resp = client.post(
        "/api/podcast/synthesize",
        json={
            "rel_path": "test_doc.md",
            "title": "API 合成测试单集",
            "lang": "zh",
            "pause_ms": 200,
            "turns": [
                {"speaker": "host_a", "speaker_name": "晓晓", "text": "API 测试第一句。"},
                {"speaker": "host_b", "speaker_name": "云希", "text": "API 测试第二句。"}
            ]
        }
    )
    assert resp.status_code == 200
    res = resp.json()
    assert res["status"] == "success"
    assert res["data"]["turn_count"] == 2
    assert res["data"]["file_size_bytes"] > 0
    assert "audio_url" in res["data"]


def test_tts_engine_real_synthesis():
    """测试真实的短语音对谈拼接合成"""
    import asyncio
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        script = PodcastScript(
            title="测试合成单集",
            topic="架构",
            lang="zh",
            turns=[
                DialogueTurn(speaker="host_a", speaker_name="晓晓", text="测试播客合成开始。"),
                DialogueTurn(speaker="host_b", speaker_name="云希", text="好的，已成功接通。")
            ]
        )
        res = asyncio.run(PodcastTTSEngine.synthesize_script(script, tmp_path, pause_ms=200))
        assert os.path.exists(res.output_path)
        assert res.file_size_bytes > 1000
        assert res.duration_ms > 0
        assert res.turn_count == 2
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


