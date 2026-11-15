# -*- coding: utf-8 -*-
"""
🧪 Test Suite for Podcast BGM Mixer & Smart Audio Ducking Engine
验证：
1. 垫乐风格元数据注册完整性；
2. 科技未来、Lo-Fi、微风粉噪三种程序化免版税垫乐生成器；
3. 智能闪避混音流水线（片头先导、人声下潜衬底、片尾余音回扬与渐隐）；
4. 纯净干音 (style="none") 无损透传；
5. REST API 端点 /api/podcast/bgm_options 与 /api/podcast/synthesize 联动。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

from pydub import AudioSegment
from fastapi.testclient import TestClient

from core.podcast import (
    PodcastBGMMixer
)
from services.api.server import app

client = TestClient(app)


def test_bgm_supported_styles():
    """验证支持的垫乐风格列表及元数据契约"""
    styles = PodcastBGMMixer.get_supported_styles()
    assert "cyber_ambient" in styles
    assert "lofi_chill" in styles
    assert "white_noise" in styles
    assert "none" in styles
    assert "name" in styles["cyber_ambient"]
    assert "desc" in styles["cyber_ambient"]


def test_procedural_bgm_generation():
    """验证纯程序化生成各种风格的环境垫乐"""
    # 1. 科技未来
    cyber_bgm = PodcastBGMMixer.generate_procedural_bgm("cyber_ambient", duration_sec=3.0)
    assert len(cyber_bgm) >= 2900
    assert cyber_bgm.rms > 0

    # 2. 温暖 Lo-Fi
    lofi_bgm = PodcastBGMMixer.generate_procedural_bgm("lofi_chill", duration_sec=3.0)
    assert len(lofi_bgm) >= 2900
    assert lofi_bgm.rms > 0

    # 3. 沉浸微风底噪
    noise_bgm = PodcastBGMMixer.generate_procedural_bgm("white_noise", duration_sec=3.0)
    assert len(noise_bgm) >= 2900
    assert noise_bgm.rms > 0

    # 4. 纯 Python 无 NumPy 降级生成器验证
    pure_bgm = PodcastBGMMixer._generate_procedural_pure_python("lofi_chill", duration_sec=2.5, sr=24000)
    assert len(pure_bgm) >= 2400
    assert pure_bgm.rms > 0


def test_smart_ducking_mixing_flow():
    """验证智能闪避混音与时序编排"""
    # 模拟 3 秒的人声音频
    voice = AudioSegment.silent(duration=3000)
    intro_ms = 1500
    outro_ms = 2000

    # 1. 测试 style="none" 纯人声透传
    pure_voice = PodcastBGMMixer.mix_with_smart_ducking(voice, style="none")
    assert len(pure_voice) == len(voice)

    # 2. 测试垫乐混合与时长扩充
    mixed = PodcastBGMMixer.mix_with_smart_ducking(
        voice,
        style="cyber_ambient",
        duck_volume_db=-22.0,
        normal_volume_db=-14.0,
        intro_ms=intro_ms,
        outro_ms=outro_ms
    )
    expected_dur = intro_ms + len(voice) + outro_ms
    assert len(mixed) == expected_dur
    assert mixed.rms > 0


def test_api_bgm_options_endpoint():
    """测试 /api/podcast/bgm_options REST 路由端点"""
    resp = client.get("/api/podcast/bgm_options")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    options = data["options"]
    assert "cyber_ambient" in options
    assert "lofi_chill" in options


def test_api_synthesize_with_bgm_style():
    """测试调用 /api/podcast/synthesize 并注入指定垫乐风格"""
    resp = client.post(
        "/api/podcast/synthesize",
        json={
            "rel_path": "Docs/bgm_test.md",
            "title": "BGM 混音测试",
            "lang": "zh",
            "style": "tech_deep",
            "bgm_style": "lofi_chill",
            "turns": [
                {"speaker": "host_a", "speaker_name": "晓晓", "text": "这是测试带有背景音乐的第一句话。"},
                {"speaker": "host_b", "speaker_name": "云希", "text": "好的，背景氛围很温暖。"}
            ]
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["bgm_style"] == "lofi_chill"
    assert data["data"]["file_size_bytes"] > 0
    assert "audio_url" in data["data"]
