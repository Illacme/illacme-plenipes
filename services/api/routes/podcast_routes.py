# -*- coding: utf-8 -*-
"""
🎙️ Podcast Engine REST API Routes
职责：提供播客剧本提炼、双人语音合成、音频流式播放与 RSS 订阅源服务。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import FileResponse, Response

from core.runtime.engine_singleton import get_global_engine
from core.utils.tracing import tlog
from core.utils.text import parse_frontmatter
from core.podcast import (
    PodcastScriptEngine,
    DialogueTurn,
    PodcastScript,
    PodcastChapter,
    PodcastTTSEngine,
    DEFAULT_VOICE_MAP,
    PodcastRSSGenerator,
    PodcastEpisode,
    ScriptExtractRequest,
    PodcastSynthesizeRequest
)
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path
from .system import verify_token

router = APIRouter(tags=["Podcast Engine"])


def _load_sidecar_info(target_path: str):
    """读取音频旁伴 Sidecar 章节与 Show Notes 元数据"""
    sc_f = os.path.splitext(target_path)[0] + ".chapters.json"
    if os.path.isfile(sc_f):
        try:
            with open(sc_f, "r", encoding="utf-8") as sf:
                d = json.load(sf)
                return d.get("chapters", []), d.get("shownotes", "")
        except Exception:
            pass
    return [], ""


def _get_audio_cache_dir(engine) -> str:
    """获取播客音频缓存物理目录"""
    imprint_id = getattr(engine, "imprint_id", "default") if engine else "default"
    base_dir = getattr(engine, "cache_dir", os.path.join(os.getcwd(), ".plenipes", "cache")) if engine else os.path.join(os.getcwd(), ".plenipes", "cache")
    p_dir = os.path.join(base_dir, "podcasts", imprint_id)
    os.makedirs(p_dir, exist_ok=True)
    return p_dir


def _resolve_localized_content(engine, rel_path: str, target_lang: str):
    """解析指定目标语种的本地化译文快照"""
    if not engine or not rel_path or not target_lang or target_lang.startswith("zh"):
        return None, None, None
    try:
        from services.api.routes.gov.context_shards.review_ops import get_translation_snapshot_impl
        snap = get_translation_snapshot_impl(engine, rel_path)
        lang_data = snap.get("langs", {}).get(target_lang)
        if not lang_data or lang_data.get("is_missing"):
            return None, None, None
        paras = [p.get("text", "") for p in lang_data.get("paragraphs", []) if p.get("type") != "spacer" and p.get("text")]
        return ("\n\n".join(paras), lang_data.get("title"), lang_data.get("desc")) if paras else (None, None, None)
    except Exception as e:
        tlog.warning(f"Failed to resolve localized podcast content for {rel_path} ({target_lang}): {e}")
        return None, None, None


@router.get("/api/podcast/voices")
async def get_podcast_voices() -> Dict[str, Any]:
    """获取系统支持的官方神经语音角色矩阵"""
    return {"status": "success", "data": DEFAULT_VOICE_MAP}


@router.post("/api/podcast/script/extract", dependencies=[Depends(verify_token)])
async def extract_podcast_script(req: ScriptExtractRequest) -> Dict[str, Any]:
    """从 Markdown 稿件或输入内容中提炼双人对谈剧本"""
    engine = get_global_engine()
    raw_content = req.content or ""
    metadata = {}
    target_lang = (req.lang or "zh").lower()

    if req.rel_path:
        safe_path = resolve_safe_path(engine, req.rel_path) if engine else os.path.join(os.getcwd(), req.rel_path)
        if safe_path and os.path.isfile(safe_path):
            with open(safe_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
            fm_dict, body, _ = parse_frontmatter(raw_text)
            raw_content = body
            metadata = fm_dict

        # 多语言自动对接：若非中文广播，优先提取对应语种的本地化译文
        if not target_lang.startswith("zh") and engine:
            loc_body, loc_title, loc_desc = _resolve_localized_content(engine, req.rel_path, target_lang)
            if loc_body:
                raw_content = loc_body
                if loc_title:
                    metadata["title"] = loc_title
                if loc_desc:
                    metadata["description"] = loc_desc
            elif any('\u4e00' <= c <= '\u9fff' for c in raw_content):
                lang_names = {"en": "English", "ja": "日本語"}
                name_disp = lang_names.get(target_lang, target_lang.upper())
                raise HTTPException(
                    status_code=400,
                    detail=f"未找到该文档的 {name_disp} 译文。请先在「多语种译文校对」中生成翻译，或选择中文母语广播。"
                )

    if not raw_content.strip():
        raise HTTPException(status_code=400, detail="未提供有效的稿件文本内容以提炼剧本")

    try:
        script = PodcastScriptEngine.extract_script(
            content=raw_content,
            metadata=metadata,
            lang=target_lang,
            style=req.style or "tech_deep",
            max_turns=req.max_turns or 10,
            use_ai=bool(req.use_ai),
            engine=engine
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        tlog.error(f"🚨 播客剧本提炼异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"提炼剧本失败: {str(e)}")

    chaps = [c.to_dict() for c in script.chapters] if getattr(script, "chapters", None) else []
    shownotes = PodcastChapter.format_shownotes_timeline(script.chapters) if getattr(script, "chapters", None) else ""
    return {
        "status": "success",
        "data": {
            "title": script.title, "topic": script.topic, "lang": script.lang,
            "style": script.style, "summary": script.summary,
            "estimated_duration_sec": script.estimated_duration_sec,
            "turns": [{"speaker": t.speaker, "speaker_name": t.speaker_name, "text": t.text, "intent": t.intent} for t in script.turns],
            "chapters": chaps, "shownotes_formatted": shownotes
        }
    }


@router.post("/api/podcast/synthesize", dependencies=[Depends(verify_token)])
async def synthesize_podcast(req: PodcastSynthesizeRequest) -> Dict[str, Any]:
    """执行双人对谈语音合成，缝合生成单轨 MP3 音频"""
    engine = get_global_engine()
    imprint_id = getattr(engine, "imprint_id", "default") if engine else "default"
    cache_dir = _get_audio_cache_dir(engine)

    slug = os.path.splitext(os.path.basename(req.rel_path))[0]
    style_key = req.style or "tech_deep"
    filename = f"{slug}_{req.lang}_{style_key}.mp3"
    target_path = os.path.join(cache_dir, filename)

    dialogue_turns = [DialogueTurn(speaker=t.speaker, speaker_name=t.speaker_name, text=t.text, intent=t.intent or "dialogue") for t in req.turns]
    script = PodcastScript(title=req.title, topic="技术对谈", lang=req.lang or "zh", style=req.style or "tech_deep", turns=dialogue_turns)

    brand_name = "SOVEREIGN PRESS"
    if engine and hasattr(engine, "config") and engine.config:
        brand_name = getattr(engine.config, "site_name", None) or getattr(engine.config, "imprint_name", None) or "SOVEREIGN PRESS"

    try:
        res = await PodcastTTSEngine.synthesize_script(
            script=script, output_file_path=target_path, voice_a=req.voice_a, voice_b=req.voice_b,
            pause_ms=req.pause_ms or 400, rate=req.rate or "+0%", pitch=req.pitch or "+0Hz",
            imprint_name=brand_name, bgm_style=req.bgm_style or "cyber_ambient"
        )
    except Exception as e:
        tlog.error(f"🚨 播客语音合成失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")

    audio_url = f"/api/podcast/audio/{imprint_id}/{filename}"
    _, shownotes = _load_sidecar_info(target_path)
    return {
        "status": "success",
        "data": {
            "filename": filename, "audio_url": audio_url, "file_size_bytes": res.file_size_bytes,
            "duration_ms": res.duration_ms, "turn_count": res.turn_count, "lang": res.lang,
            "voices_used": res.voices_used, "bgm_style": req.bgm_style or "cyber_ambient",
            "chapters": res.chapters, "shownotes_formatted": shownotes
        }
    }


@router.api_route("/api/podcast/audio/{imprint_id}/{filename}", methods=["GET", "HEAD"])
async def serve_podcast_audio(imprint_id: str, filename: str):
    """安全流式返回播客 MP3 音频文件（支持拖拽进度条）"""
    engine = get_global_engine()
    audio_path = os.path.join(_get_audio_cache_dir(engine), filename)
    if not os.path.isfile(audio_path):
        raise HTTPException(status_code=404, detail="未找到对应的播客音频文件")
    return FileResponse(path=audio_path, media_type="audio/mpeg", filename=filename)


@router.get("/api/podcast/info")
async def get_podcast_info(rel_path: str, lang: str = "zh", style: str = "tech_deep") -> Dict[str, Any]:
    """查询指定稿件是否已生成就绪的播客音频"""
    engine = get_global_engine()
    imprint_id = getattr(engine, "imprint_id", "default") if engine else "default"
    slug = os.path.splitext(os.path.basename(rel_path))[0]
    cache_dir = _get_audio_cache_dir(engine)
    style_key = style or "tech_deep"
    filename = f"{slug}_{lang}_{style_key}.mp3"
    target_path = os.path.join(cache_dir, filename)

    if not os.path.isfile(target_path) and style_key == "tech_deep":
        legacy_name = f"{slug}_{lang}.mp3"
        legacy_path = os.path.join(cache_dir, legacy_name)
        if os.path.isfile(legacy_path):
            filename, target_path = legacy_name, legacy_path

    if os.path.isfile(target_path):
        chaps, shownotes = _load_sidecar_info(target_path)
        return {
            "status": "success", "exists": True,
            "data": {
                "filename": filename, "audio_url": f"/api/podcast/audio/{imprint_id}/{filename}",
                "file_size_bytes": os.path.getsize(target_path), "lang": lang, "style": style_key,
                "chapters": chaps, "shownotes_formatted": shownotes
            }
        }
    return {"status": "success", "exists": False, "data": None}


@router.get("/api/podcast/bgm_options")
async def get_podcast_bgm_options() -> Dict[str, Any]:
    """获取所有受支持的播客垫乐风格列表"""
    from core.podcast.podcast_bgm_mixer import PodcastBGMMixer
    return {"status": "success", "options": PodcastBGMMixer.get_supported_styles()}


@router.get("/api/podcast/feed/{imprint_id}")
async def get_podcast_rss_feed(request: Request, imprint_id: str, lang: str = "zh") -> Response:
    """生成并提供标准 Podcast RSS 2.0 XML 订阅源"""
    engine = get_global_engine()
    podcast_dir = _get_audio_cache_dir(engine)
    base_url = str(request.base_url).rstrip("/")

    episodes: List[PodcastEpisode] = []
    if os.path.isdir(podcast_dir):
        from core.podcast.podcast_storage_engine import PodcastStorageEngine
        for f in os.listdir(podcast_dir):
            if f.endswith(".mp3") and (f.endswith(f"_{lang}.mp3") or f"_{lang}_" in f):
                f_path = os.path.join(podcast_dir, f)
                size, mtime = os.path.getsize(f_path), os.path.getmtime(f_path)
                pub_dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
                title = f.replace(".mp3", "").replace(f"_{lang}", "").replace("-", " ").replace("_", " ").title()
                local_url = f"{base_url}/api/podcast/audio/{imprint_id}/{f}"
                audio_url = PodcastStorageEngine.get_audio_public_url(f, local_url, engine)
                sc_chaps, sc_notes = _load_sidecar_info(f_path)
                episodes.append(PodcastEpisode(
                    title=f"【技术对谈】{title}", audio_url=audio_url, audio_size_bytes=size,
                    duration_sec=max(30, int(size / 16000)), pub_date=pub_dt,
                    description=f"{title} 的双人技术深度播客", chapters=sc_chaps, shownotes=sc_notes
                ))

    channel_title = f"{imprint_id.title()} 技术前沿播客"
    channel_link = base_url
    channel_desc = f"{imprint_id} 旗下由出版发行工作台自动衍生的多语种双人技术对谈播客。"

    xml_str = PodcastRSSGenerator.generate_feed_xml(
        channel_title=channel_title,
        channel_link=channel_link,
        channel_desc=channel_desc,
        episodes=episodes,
        author="创作者指南",
        lang=f"{lang}-cn" if lang == "zh" else lang
    )
    return Response(content=xml_str, media_type="application/xml")
