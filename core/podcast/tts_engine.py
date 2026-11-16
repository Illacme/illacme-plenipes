# -*- coding: utf-8 -*-
"""
🎙️ Podcast TTS Engine - Multi-Voice Speech Synthesis & Stitching
职责：调用 edge-tts 神经语音模型，将双人剧本拼接合成为流畅的技术播客单轨 MP3 音频。
特性：
1. 角色声线映射矩阵：男女双声线、跨语种专业播音员级声线；
2. 自然转场停顿：台词间插入 300~500ms 拟人化静音转场，杜绝机械抢话；
3. 纯本地高效缝合：优先通过 pydub / 直接 MP3 帧级无损拼接，零本地重度模型开销；
4. 元数据标签封装：自动注入 ID3 标签（标题、艺术家、专辑、播客流派）；
5. 异步流式处理与代理自愈感知。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
import io
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from core.utils.tracing import tlog
from .podcast_script_engine import DialogueTurn, PodcastScript


# 官方认证的高品质微软神经声线矩阵
DEFAULT_VOICE_MAP: Dict[str, Dict[str, Dict[str, str]]] = {
    "zh": {
        "host_a": {"voice": "zh-CN-XiaoxiaoNeural", "name": "晓晓", "gender": "female", "role": "沉稳主讲"},
        "host_b": {"voice": "zh-CN-YunxiNeural", "name": "云希", "gender": "male", "role": "敏锐搭档"},
    },
    "en": {
        "host_a": {"voice": "en-US-JennyNeural", "name": "Jenny", "gender": "female", "role": "Host"},
        "host_b": {"voice": "en-US-GuyNeural", "name": "Guy", "gender": "male", "role": "Co-Host"},
    },
    "ja": {
        "host_a": {"voice": "ja-JP-NanamiNeural", "name": "七海", "gender": "female", "role": "メイン解説"},
        "host_b": {"voice": "ja-JP-KeitaNeural", "name": "圭太", "gender": "male", "role": "聞き手"},
    }
}


@dataclass
class AudioResult:
    """音频合成结果载荷"""
    output_path: str
    file_size_bytes: int
    duration_ms: int
    turn_count: int
    lang: str
    voices_used: Dict[str, str]
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    actual_provider: str = "edge"
    fallback_reason: Optional[str] = None


class PodcastTTSEngine:
    """双人播客语音合成中枢"""

    @classmethod
    def get_supported_voices(cls) -> Dict[str, Dict[str, Dict[str, str]]]:
        """获取所有语种的官方推荐声线"""
        return DEFAULT_VOICE_MAP

    @classmethod
    def get_voice_for_role(
        cls, lang: str, speaker: str, custom_voice: Optional[str] = None
    ) -> str:
        """获取指定角色声线"""
        if custom_voice:
            return custom_voice
        lang_code = lang.lower() if lang else "zh"
        if not lang_code.startswith(("zh", "en", "ja")):
            lang_code = "en"
        role_map = DEFAULT_VOICE_MAP.get(lang_code, DEFAULT_VOICE_MAP["en"])
        role_info = role_map.get(speaker, role_map.get("host_a"))
        return role_info["voice"]

    @classmethod
    async def synthesize_turn_audio(
        cls,
        text: str,
        voice: str,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        proxy: Optional[str] = None,
        tts_provider: str = "edge",
        engine: Any = None,
        fallback_tracker: Optional[List[str]] = None,
    ) -> bytes:
        """单个台词回合的语音合成（支持多引擎路由，失败时记录降级原因并回退 edge-tts）"""
        if (tts_provider or "edge").lower() != "edge":
            try:
                from .podcast_models import synthesize_external_tts
                ext_bytes = await synthesize_external_tts(text, voice, tts_provider, engine=engine)
                if ext_bytes:
                    return ext_bytes
                if fallback_tracker is not None:
                    fallback_tracker.append(f"{tts_provider} 未配置有效密钥或服务返回空响应，已自动回退 Edge TTS")
            except Exception as ext_err:
                tlog.warning(f"⚠️ [{tts_provider} TTS 降级] 回退至 edge-tts: {ext_err}")
                if fallback_tracker is not None:
                    fallback_tracker.append(f"{tts_provider} 调用异常 ({ext_err})，已自动回退 Edge TTS")

        import edge_tts
        proxy_url = proxy or os.environ.get("https_proxy") or os.environ.get("http_proxy")
        comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, proxy=proxy_url)
        audio_buffer = bytearray()
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio_buffer.extend(chunk["data"])
        return bytes(audio_buffer)

    @classmethod
    async def synthesize_script(
        cls,
        script: PodcastScript,
        output_file_path: str,
        voice_a: Optional[str] = None,
        voice_b: Optional[str] = None,
        pause_ms: int = 400,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        proxy: Optional[str] = None,
        imprint_name: str = "SOVEREIGN PRESS",
        bgm_style: Optional[str] = "cyber_ambient",
        tts_provider: str = "edge",
        engine: Any = None,
    ) -> AudioResult:
        """将完整剧本并发合成为单轨播客 MP3 音频，并同步导出章节与逐句字幕 Sidecar"""
        os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)
        v_a = cls.get_voice_for_role(script.lang, "host_a", voice_a)
        v_b = cls.get_voice_for_role(script.lang, "host_b", voice_b)

        tlog.info(f"🎙️ [播客合成] 并发合成《{script.title}》共 {len(script.turns)} 轮 | 引擎: {tts_provider} | 垫乐: {bgm_style}")

        # 1. 信号量并发合成各回合音频片段并保持顺序
        sem = asyncio.Semaphore(4)
        fallback_notes: List[str] = []
        async def _synth_one(idx: int, turn: DialogueTurn) -> bytes:
            voice = v_a if turn.speaker == "host_a" else v_b
            async with sem:
                try:
                    return await cls.synthesize_turn_audio(text=turn.text, voice=voice, rate=rate, pitch=pitch, proxy=proxy, tts_provider=tts_provider, engine=engine, fallback_tracker=fallback_notes)
                except Exception as e:
                    tlog.error(f"🚨 [播客合成] 第 {idx + 1} 轮合成失败 ({voice}): {e}")
                    raise

        raw_results = await asyncio.gather(*[_synth_one(i, t) for i, t in enumerate(script.turns)])
        turn_audios: List[bytes] = [b for b in raw_results if b]

        if not turn_audios:
            raise RuntimeError("播客音频合成失败：未能产出有效的音频数据片段")

        # 2. 拼接多段音频（带静音停顿与氛围垫乐混音）
        duration_ms, turn_durations_ms = cls._stitch_and_save(
            turn_audios=turn_audios,
            output_path=output_file_path,
            pause_ms=pause_ms,
            title=script.title,
            imprint_name=imprint_name,
            bgm_style=bgm_style
        )

        # 3. 基于毫秒级实际时长精准校准章节时间戳并持久化 Sidecar
        from .podcast_script_engine import PodcastScriptEngine
        from .podcast_models import PodcastChapter
        calibrated = PodcastScriptEngine.build_chapters(
            turns=script.turns,
            sections=getattr(script, "sections", []),
            lang=script.lang,
            turn_durations_ms=turn_durations_ms
        )
        if not calibrated and script.chapters:
            calibrated = script.chapters
        chapters_data = [c.to_dict() if hasattr(c, "to_dict") else c for c in calibrated]

        sidecar_path = os.path.splitext(output_file_path)[0] + ".chapters.json"
        try:
            with open(sidecar_path, "w", encoding="utf-8") as f_sc:
                json.dump({
                    "title": script.title,
                    "lang": script.lang,
                    "duration_ms": duration_ms,
                    "chapters": chapters_data,
                    "shownotes": PodcastChapter.format_shownotes_timeline(calibrated)
                }, f_sc, ensure_ascii=False, indent=2)
            tlog.info(f"⏱️ [章节元数据] 成功写入 Sidecar: {sidecar_path} ({len(chapters_data)} 个章节)")
        except Exception as sc_err:
            tlog.warning(f"⚠️ [章节元数据] 写入 Sidecar 失败: {sc_err}")

        # 3.5 导出逐句对齐字幕 Sidecar (.transcript.json & .vtt)
        cls._write_transcript_sidecars(output_file_path, script.turns, turn_durations_ms, pause_ms, bgm_style)

        file_size = os.path.getsize(output_file_path)
        tlog.info(f"🎙️ [播客合成完毕] {output_file_path} | 体积: {file_size} 字节 | 时长: {duration_ms}ms")

        actual_p = "edge" if fallback_notes else (tts_provider or "edge").lower()
        return AudioResult(
            output_path=output_file_path,
            file_size_bytes=file_size,
            duration_ms=duration_ms,
            turn_count=len(script.turns),
            lang=script.lang,
            voices_used={"host_a": v_a, "host_b": v_b},
            chapters=chapters_data,
            actual_provider=actual_p,
            fallback_reason=fallback_notes[0] if fallback_notes else None,
        )

    @classmethod
    def _stitch_and_save(
        cls,
        turn_audios: List[bytes],
        output_path: str,
        pause_ms: int,
        title: str,
        imprint_name: str,
        bgm_style: Optional[str] = "cyber_ambient"
    ) -> Tuple[int, List[int]]:
        """拼接音频片段并打上 ID3 标签，返回 (总时长ms, 各回合时长ms列表)"""
        turn_durations_ms: List[int] = []
        try:
            from pydub import AudioSegment
            combined = AudioSegment.empty()
            pause = AudioSegment.silent(duration=pause_ms)

            for i, raw_bytes in enumerate(turn_audios):
                seg = AudioSegment.from_file(io.BytesIO(raw_bytes), format="mp3")
                turn_durations_ms.append(len(seg))
                combined += seg
                if i < len(turn_audios) - 1:
                    combined += pause

            # 🎵 听觉质感升华：混入商业级氛围垫乐与自适应闪避 + -16 dBFS 广播响度均衡
            if bgm_style and bgm_style != "none":
                from .podcast_bgm_mixer import PodcastBGMMixer
                combined = PodcastBGMMixer.mix_with_smart_ducking(combined, style=bgm_style)
            if len(combined) > 0 and getattr(combined, "dBFS", float("-inf")) > -60.0:
                gain = max(-12.0, min(12.0, -16.0 - float(combined.dBFS)))
                if abs(gain) >= 0.5:
                    combined = combined.apply_gain(gain)

            # 导出为标准 MP3
            tags = {
                "title": title,
                "artist": "Illacme Plenipes",
                "album": imprint_name,
                "genre": "Podcast"
            }
            combined.export(output_path, format="mp3", bitrate="128k", tags=tags)
            return len(combined), turn_durations_ms
        except Exception as e:
            tlog.warning(f"⚠️ [pydub 拼接降级] 使用直接二进制拼接: {e}")
            # 保底：若 pydub 发生异常，直接拼接 MP3 字节流 (MP3 天然支持帧拼接)
            with open(output_path, "wb") as f_out:
                for b in turn_audios:
                    turn_durations_ms.append(int(len(b) / 16 * 1000))
                    f_out.write(b)
            # 粗略估算时长 (按 128kbps = 16000 字节/秒)
            return int(os.path.getsize(output_path) / 16 * 1000), turn_durations_ms

    @classmethod
    def _write_transcript_sidecars(
        cls, output_file_path: str, turns: List[DialogueTurn], turn_durations_ms: List[int], pause_ms: int, bgm_style: Optional[str]
    ) -> None:
        """写入逐句毫秒级对齐字幕 (.transcript.json 与 WebVTT .vtt)"""
        try:
            from .podcast_models import PodcastChapter
            cursor_ms = 1800 if (bgm_style and bgm_style != "none") else 0
            entries, vtt_lines = [], ["WEBVTT", ""]
            for i, turn in enumerate(turns):
                dur = turn_durations_ms[i] if i < len(turn_durations_ms) else 2500
                start_ms, end_ms = cursor_ms, cursor_ms + dur
                entries.append({"index": i + 1, "speaker": turn.speaker, "speaker_name": turn.speaker_name, "text": turn.text, "start_ms": start_ms, "end_ms": end_ms})
                vtt_lines.append(f"{PodcastChapter.format_vtt_timestamp(start_ms)} --> {PodcastChapter.format_vtt_timestamp(end_ms)}")
                vtt_lines.append(f"{turn.speaker_name}: {turn.text}\n")
                cursor_ms = end_ms + pause_ms
            base = os.path.splitext(output_file_path)[0]
            with open(base + ".transcript.json", "w", encoding="utf-8") as jf:
                json.dump({"turns": entries}, jf, ensure_ascii=False, indent=2)
            with open(base + ".vtt", "w", encoding="utf-8") as vf:
                vf.write("\n".join(vtt_lines))
        except Exception as e:
            tlog.warning(f"⚠️ [字幕 Sidecar] 写入失败: {e}")

    @classmethod
    def synthesize_script_sync(
        cls,
        script: PodcastScript,
        output_file_path: str,
        **kwargs
    ) -> AudioResult:
        """同步包装方法，方便非异步场景调用"""
        return asyncio.run(cls.synthesize_script(script, output_file_path, **kwargs))

