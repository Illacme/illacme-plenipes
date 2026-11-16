"""
Tests for multi-engine podcast TTS provider adapters in core/podcast/podcast_tts_providers.py.
Covers OpenAI-compatible local/open-source engines (kokoro, chattts, cosyvoice, piper, openai)
and commercial APIs (minimax, volcengine, gemini, elevenlabs, fish_audio).
"""
import asyncio
import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.podcast.podcast_models import SUPPORTED_TTS_PROVIDERS, synthesize_external_tts


def _make_engine(tts_cfg):
    return SimpleNamespace(config=SimpleNamespace(podcast={"podcast_tts_engines": tts_cfg}))


@pytest.mark.parametrize(
    "provider,expected_url,expected_voice_a",
    [
        ("kokoro", "http://127.0.0.1:8880/v1/audio/speech", "af_heart"),
        ("chattts", "http://127.0.0.1:9966/v1/audio/speech", "female"),
        ("cosyvoice", "http://127.0.0.1:9880/v1/audio/speech", "nova"),
        ("piper", "http://127.0.0.1:5000/v1/audio/speech", "nova"),
    ],
)
def test_openai_compatible_local_providers(provider, expected_url, expected_voice_a):
    mock_resp = MagicMock(status_code=200, content=b"ID3-MP3-LOCAL")
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_cm):
        out = asyncio.run(synthesize_external_tts("你好世界", "zh-CN-XiaoxiaoNeural", provider, engine=_make_engine({})))

    assert out == b"ID3-MP3-LOCAL"
    assert mock_client.post.call_args[0][0] == expected_url
    assert mock_client.post.call_args[1]["json"]["voice"] == expected_voice_a


def test_minimax_hex_audio_decoding():
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {"data": {"audio": b"MINIMAX_MP3".hex()}}
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    eng = _make_engine({"minimax_api_key": "mm-key", "minimax_group_id": "grp-1"})
    with patch("httpx.AsyncClient", return_value=mock_cm):
        out = asyncio.run(synthesize_external_tts("测试 MiniMax", "zh-CN-YunxiNeural", "minimax", engine=eng))

    assert out == b"MINIMAX_MP3"
    assert "GroupId=grp-1" in mock_client.post.call_args[0][0]


def test_volcengine_base64_audio_decoding():
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {"data": base64.b64encode(b"VOLC_MP3").decode()}
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    eng = _make_engine({"volcengine_app_id": "app-1", "volcengine_access_token": "tok-1"})
    with patch("httpx.AsyncClient", return_value=mock_cm):
        out = asyncio.run(synthesize_external_tts("测试豆包语音", "zh-CN-XiaoxiaoNeural", "volcengine", engine=eng))

    assert out == b"VOLC_MP3"
    assert mock_client.post.call_args[1]["headers"]["Authorization"] == "Bearer;tok-1"


def test_gemini_tts_mp3_decoding():
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"inlineData": {"mimeType": "audio/mp3", "data": base64.b64encode(b"GEM_MP3").decode()}}]}}]
    }
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    eng = _make_engine({"gemini_api_key": "gem-key"})
    with patch("httpx.AsyncClient", return_value=mock_cm):
        out = asyncio.run(synthesize_external_tts("Hello Gemini", "en-US-JennyNeural", "gemini", engine=eng))

    assert out == b"GEM_MP3"


def test_supported_tts_providers_includes_all_11_engines():
    ids = {item["id"] for item in SUPPORTED_TTS_PROVIDERS}
    assert ids == {"edge", "kokoro", "chattts", "cosyvoice", "piper", "openai", "minimax", "volcengine", "gemini", "elevenlabs", "fish_audio"}


def test_synthesize_turn_records_fallback_reason():
    from core.podcast.tts_engine import PodcastTTSEngine

    tracker = []
    with patch("core.podcast.podcast_models.synthesize_external_tts", AsyncMock(return_value=None)), \
         patch("edge_tts.Communicate") as mock_comm:
        async def _fake_stream():
            yield {"type": "audio", "data": b"EDGE-FALLBACK"}
        mock_comm.return_value.stream = _fake_stream
        out = asyncio.run(PodcastTTSEngine.synthesize_turn_audio("你好", "zh-CN-XiaoxiaoNeural", tts_provider="kokoro", fallback_tracker=tracker))

    assert out == b"EDGE-FALLBACK"
    assert tracker and "kokoro" in tracker[0]


def test_tts_test_endpoint_returns_base64_and_handles_missing_config():
    from fastapi import HTTPException
    from services.api.routes.podcast_routes import test_podcast_tts_provider

    with patch("core.podcast.podcast_models.synthesize_external_tts", AsyncMock(return_value=b"TEST-MP3")):
        res = asyncio.run(test_podcast_tts_provider({"tts_provider": "minimax", "overrides": {"minimax_api_key": "k"}}))
    assert res["status"] == "success"
    assert base64.b64decode(res["audio_base64"]) == b"TEST-MP3"

    with patch("core.podcast.podcast_models.synthesize_external_tts", AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc:
            asyncio.run(test_podcast_tts_provider({"tts_provider": "minimax"}))
    assert exc.value.status_code == 400
