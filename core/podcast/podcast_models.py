# -*- coding: utf-8 -*-
"""
🎙️ Podcast Data Models
职责：定义双人对话播客台词 (DialogueTurn)、剧本结构 (PodcastScript) 与章节时间戳 (PodcastChapter)。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import os
from pydantic import BaseModel


def resolve_podcast_slug(
    rel_path: str,
    explicit_slug: str = "",
    engine: Any = None,
    snapshot: Optional[Dict[str, Any]] = None,
) -> str:
    """生成无冲突的播客物理文件名前缀：子目录 index/readme 或跨目录同名原稿采用 docs__index 消歧"""
    clean_rel = (rel_path or "").replace("\\", "/").strip("/")
    base = os.path.splitext(os.path.basename(clean_rel))[0]
    rel_no_ext = os.path.splitext(clean_rel)[0]
    if "/" in rel_no_ext:
        if base.lower() in ("index", "readme"):
            return rel_no_ext.replace("/", "__")
        snap = snapshot
        if not isinstance(snap, dict) and engine and hasattr(engine, "meta") and hasattr(engine.meta, "get_documents_snapshot"):
            try:
                snap = engine.meta.get_documents_snapshot()
            except Exception:
                snap = {}
        if isinstance(snap, dict):
            same_stem = [
                rp for rp in snap.keys()
                if os.path.splitext(os.path.basename(rp))[0].lower() == base.lower()
            ]
            if len(same_stem) > 1:
                return rel_no_ext.replace("/", "__")
    return explicit_slug or base or "episode"


def get_podcast_candidate_slugs(
    rel_path: str = "",
    explicit_slug: str = "",
    file_slug: str = "",
    vault_dir: str = "",
) -> List[str]:
    """构建播客音频匹配候选前缀列表：对子目录 index/readme 优先匹配路径限定名 (如 docs__index)"""
    clean_rel = (rel_path or "").replace("\\", "/")
    if os.path.isabs(clean_rel) and vault_dir:
        try:
            clean_rel = os.path.relpath(clean_rel, os.path.abspath(vault_dir)).replace("\\", "/")
        except Exception:
            pass
    clean_rel = clean_rel.strip("/")
    base = os.path.splitext(os.path.basename(clean_rel))[0] if clean_rel else file_slug
    rel_no_ext = os.path.splitext(clean_rel)[0] if clean_rel else ""
    rel_slug = rel_no_ext.replace("/", "__") if "/" in rel_no_ext else ""
    if base and base.lower() in ("index", "readme") and rel_slug:
        raw_list = [rel_slug, explicit_slug]
    else:
        raw_list = [rel_slug, explicit_slug, file_slug, base]
    cands: List[str] = []
    for s in raw_list:
        if s and s not in cands:
            cands.append(s)
    return cands


@dataclass
class DialogueTurn:
    """单条播客台词载荷"""
    speaker: str               # "host_a" | "host_b"
    speaker_name: str          # 角色名，如 "晓晓" / "云希" 或 "Jenny" / "Guy"
    text: str                  # 播客台词内容
    intent: str = "dialogue"   # "intro" | "question" | "explanation" | "contrast" | "summary" | "outro"


@dataclass
class PodcastChapter:
    """播客章节时间戳标记 (Podcasting 2.0 & Show Notes 标准)"""
    title: str
    start_seconds: int = 0
    start_time: str = "00:00"
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "start_seconds": self.start_seconds,
            "start_time": self.start_time,
            "description": self.description
        }

    @staticmethod
    def format_vtt_timestamp(ms: int) -> str:
        """毫秒转 WebVTT 标准 HH:MM:SS.mmm 格式"""
        total_ms = max(0, int(ms))
        h, rem = divmod(total_ms, 3600000)
        m, rem = divmod(rem, 60000)
        s, millis = divmod(rem, 1000)
        return f"{h:02d}:{m:02d}:{s:02d}.{millis:03d}"

    @staticmethod
    def format_timestamp(seconds: int) -> str:
        """秒数转标准 mm:ss 格式"""
        sec = max(0, int(seconds))
        m = sec // 60
        s = sec % 60
        return f"{m:02d}:{s:02d}"

    @classmethod
    def format_shownotes_timeline(cls, chapters: List["PodcastChapter"]) -> str:
        """生成小宇宙、Apple、Spotify 标准识别的 Show Notes 时间轴文本"""
        if not chapters:
            return ""
        lines = ["⏱️ 节目时间轴 (Chapters):"]
        for c in chapters:
            t = c.start_time or cls.format_timestamp(c.start_seconds)
            lines.append(f"{t} {c.title}")
        return "\n".join(lines)


@dataclass
class PodcastScript:
    """完整播客对谈剧本"""
    title: str
    topic: str
    lang: str = "zh"
    style: str = "tech_deep"
    turns: List[DialogueTurn] = field(default_factory=list)
    summary: str = ""
    estimated_duration_sec: int = 0
    chapters: List[PodcastChapter] = field(default_factory=list)
    sections: List[Dict[str, Any]] = field(default_factory=list)


class ScriptExtractRequest(BaseModel):
    rel_path: Optional[str] = None
    content: Optional[str] = None
    lang: Optional[str] = "zh"
    style: Optional[str] = "tech_deep"
    max_turns: Optional[int] = 10
    use_ai: Optional[bool] = False
    focus_prompt: Optional[str] = None
    host_a_name: Optional[str] = None
    host_b_name: Optional[str] = None


class TurnPayload(BaseModel):
    speaker: str
    speaker_name: str
    text: str
    intent: Optional[str] = "dialogue"


class PodcastSynthesizeRequest(BaseModel):
    rel_path: str
    title: str
    turns: List[TurnPayload]
    lang: Optional[str] = "zh"
    style: Optional[str] = "tech_deep"
    voice_a: Optional[str] = None
    voice_b: Optional[str] = None
    pause_ms: Optional[int] = 400
    rate: Optional[str] = "+0%"
    pitch: Optional[str] = "+0Hz"
    bgm_style: Optional[str] = "cyber_ambient"
    tts_provider: Optional[str] = "edge"


SUPPORTED_TTS_PROVIDERS = [
    {"id": "edge", "name": "Edge TTS (免费免配 · 默认)", "tier": "free"},
    {"id": "kokoro", "name": "Kokoro TTS (开源 82M 本地)", "tier": "free"},
    {"id": "chattts", "name": "ChatTTS (开源对话拟真)", "tier": "free"},
    {"id": "cosyvoice", "name": "CosyVoice / 音色克隆 (本地)", "tier": "free"},
    {"id": "piper", "name": "Piper TTS (开源离线极轻)", "tier": "free"},
    {"id": "openai", "name": "OpenAI TTS (及兼容接口)", "tier": "commercial"},
    {"id": "minimax", "name": "MiniMax Speech (海螺中文旗舰)", "tier": "commercial"},
    {"id": "volcengine", "name": "火山引擎 · 豆包语音", "tier": "commercial"},
    {"id": "gemini", "name": "Google Gemini TTS", "tier": "commercial"},
    {"id": "elevenlabs", "name": "ElevenLabs (多语旗舰)", "tier": "commercial"},
    {"id": "fish_audio", "name": "Fish Audio", "tier": "commercial"},
]


_OPENAI_COMPAT_SPECS: Dict[str, tuple] = {
    "openai": ("https://api.openai.com/v1", "tts-1", "nova", "onyx", True),
    "kokoro": ("http://127.0.0.1:8880/v1", "kokoro", "af_heart", "am_michael", False),
    "chattts": ("http://127.0.0.1:9966/v1", "chattts", "female", "male", False),
    "cosyvoice": ("http://127.0.0.1:9880/v1", "cosyvoice", "nova", "onyx", False),
    "piper": ("http://127.0.0.1:5000/v1", "piper", "nova", "onyx", False),
}


def _pcm_to_mp3(pcm_bytes: bytes, sample_rate: int = 24000) -> bytes:
    """将 Gemini TTS 返回的 16-bit PCM 裸流封装为 128k MP3"""
    import io
    from pydub import AudioSegment
    buf = io.BytesIO()
    AudioSegment(data=pcm_bytes, sample_width=2, frame_rate=sample_rate, channels=1).export(buf, format="mp3", bitrate="128k")
    return buf.getvalue()


async def synthesize_external_tts(text: str, voice: str, provider: str, engine: Any = None) -> Optional[bytes]:
    """路由至第三方云端或本地开源 TTS 服务（支持 11 种主流引擎，未配置或异常返回 None 以便回退 Edge TTS）"""
    import base64, uuid, httpx
    p_cfg = (getattr(getattr(engine, "config", None), "podcast", None) or {}) if engine else {}
    t_cfg = p_cfg.get("podcast_tts_engines", {}) if isinstance(p_cfg, dict) and isinstance(p_cfg.get("podcast_tts_engines"), dict) else {}
    def _cfg(k: str, env_k: str, default: str = "") -> str:
        return str(t_cfg.get(k) or os.environ.get(env_k) or default).strip()

    p = (provider or "edge").strip().lower()
    is_f = any(k in (voice or "").lower() for k in ("xiaoxiao", "jenny", "nanami", "nova", "shimmer", "heart", "kore"))

    if p in _OPENAI_COMPAT_SPECS:
        def_url, def_model, def_va, def_vb, req_key = _OPENAI_COMPAT_SPECS[p]
        ep = p.upper()
        api_key = _cfg(f"{p}_api_key", f"{ep}_API_KEY", "" if req_key else "local")
        if req_key and not api_key:
            return None
        base_url = _cfg(f"{p}_base_url", f"{ep}_BASE_URL", def_url).rstrip("/")
        model = _cfg(f"{p}_model", f"{ep}_TTS_MODEL", def_model)
        c_voice = _cfg(f"{p}_voice_a" if is_f else f"{p}_voice_b", f"{ep}_VOICE_A" if is_f else f"{ep}_VOICE_B", def_va if is_f else def_vb)
        async with httpx.AsyncClient(timeout=45.0) as client:
            r = await client.post(f"{base_url}/audio/speech", headers={"Authorization": f"Bearer {api_key}"}, json={"model": model, "input": text, "voice": c_voice, "response_format": "mp3"})
            return r.content if (r.status_code == 200 and r.content) else None

    if p == "minimax":
        api_key = _cfg("minimax_api_key", "MINIMAX_API_KEY")
        if not api_key:
            return None
        gid = _cfg("minimax_group_id", "MINIMAX_GROUP_ID")
        vid = _cfg("minimax_voice_a" if is_f else "minimax_voice_b", "MINIMAX_VOICE_A" if is_f else "MINIMAX_VOICE_B") or ("Chinese (Mandarin)_Warm_Girl" if is_f else "male-qn-jingying")
        url = f"https://api.minimaxi.chat/v1/t2a_v2?GroupId={gid}" if gid else "https://api.minimaxi.chat/v1/t2a_v2"
        payload = {"model": _cfg("minimax_model", "MINIMAX_TTS_MODEL", "speech-02-hd"), "text": text, "stream": False, "voice_setting": {"voice_id": vid, "speed": 1.0, "vol": 1.0, "pitch": 0}, "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3"}}
        async with httpx.AsyncClient(timeout=45.0) as client:
            r = await client.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=payload)
            hx = (r.json().get("data") or {}).get("audio") if r.status_code == 200 else None
            return bytes.fromhex(hx) if hx else None

    if p == "volcengine":
        app_id, tok = _cfg("volcengine_app_id", "VOLCENGINE_TTS_APP_ID"), _cfg("volcengine_access_token", "VOLCENGINE_TTS_ACCESS_TOKEN")
        if not app_id or not tok:
            return None
        vid = _cfg("volcengine_voice_a" if is_f else "volcengine_voice_b", "VOLCENGINE_VOICE_A" if is_f else "VOLCENGINE_VOICE_B") or ("zh_female_cancan_mars_bigtts" if is_f else "zh_male_yangguangqingnian_moon_bigtts")
        payload = {"app": {"appid": app_id, "token": tok, "cluster": _cfg("volcengine_cluster", "VOLCENGINE_TTS_CLUSTER", "volcano_tts")}, "user": {"uid": "illacme_podcast"}, "audio": {"voice_type": vid, "encoding": "mp3", "speed_ratio": 1.0}, "request": {"reqid": uuid.uuid4().hex, "text": text, "operation": "query"}}
        async with httpx.AsyncClient(timeout=45.0) as client:
            r = await client.post("https://openspeech.bytedance.com/api/v1/tts", headers={"Authorization": f"Bearer;{tok}"}, json=payload)
            b64 = r.json().get("data") if r.status_code == 200 else None
            return base64.b64decode(b64) if b64 else None

    if p == "gemini":
        api_key = _cfg("gemini_api_key", "GEMINI_API_KEY")
        if not api_key:
            return None
        model = _cfg("gemini_model", "GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
        vid = _cfg("gemini_voice_a" if is_f else "gemini_voice_b", "GEMINI_VOICE_A" if is_f else "GEMINI_VOICE_B") or ("Kore" if is_f else "Charon")
        payload = {"contents": [{"parts": [{"text": text}]}], "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": vid}}}}}
        async with httpx.AsyncClient(timeout=45.0) as client:
            r = await client.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}", json=payload)
            if r.status_code == 200:
                parts = ((r.json().get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
                inline = (parts[0] if parts else {}).get("inlineData") or {}
                b64 = inline.get("data")
                if not b64:
                    return None
                raw = base64.b64decode(b64)
                return raw if any(x in (inline.get("mimeType") or "").lower() for x in ("mp3", "mpeg")) else _pcm_to_mp3(raw)
        return None

    if p == "elevenlabs":
        api_key = _cfg("elevenlabs_api_key", "ELEVENLABS_API_KEY")
        if not api_key:
            return None
        vid = _cfg("elevenlabs_voice_a" if is_f else "elevenlabs_voice_b", "ELEVENLABS_VOICE_A" if is_f else "ELEVENLABS_VOICE_B") or ("21m00Tcm4TlvDq8ikWAM" if is_f else "TxGEqnHWrfWFTfGW9XjX")
        async with httpx.AsyncClient(timeout=45.0) as client:
            r = await client.post(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}", headers={"xi-api-key": api_key}, json={"text": text, "model_id": "eleven_multilingual_v2"})
            return r.content if (r.status_code == 200 and r.content) else None

    if p == "fish_audio":
        api_key = _cfg("fish_audio_api_key", "FISH_AUDIO_API_KEY")
        if not api_key:
            return None
        payload: Dict[str, Any] = {"text": text, "format": "mp3"}
        ref_id = _cfg("fish_audio_ref_a" if is_f else "fish_audio_ref_b", "FISH_AUDIO_REF_A" if is_f else "FISH_AUDIO_REF_B")
        if ref_id:
            payload["reference_id"] = ref_id
        async with httpx.AsyncClient(timeout=45.0) as client:
            r = await client.post("https://api.fish.audio/v1/tts", headers={"Authorization": f"Bearer {api_key}"}, json=payload)
            return r.content if (r.status_code == 200 and r.content) else None

    return None
