# -*- coding: utf-8 -*-
"""
🎙️ Podcast Engine REST API Routes
职责：提供播客剧本提炼、双人语音合成、音频流式播放与 RSS 订阅源服务。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import FileResponse, Response

from core.runtime.engine_singleton import get_global_engine
from core.utils.tracing import tlog
from core.utils.text import parse_frontmatter
from core.podcast import (
    PodcastScriptEngine, DialogueTurn, PodcastScript, PodcastChapter,
    PodcastTTSEngine, DEFAULT_VOICE_MAP, ScriptExtractRequest, PodcastSynthesizeRequest
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


def _get_audio_cache_dir(engine, imprint_id: str = "") -> str:
    """获取播客音频缓存物理目录（优先尊重路由显式传入的 imprint_id）"""
    imp = (imprint_id or getattr(engine, "imprint_id", "default") or "default") if engine or imprint_id else "default"
    base_dir = getattr(engine, "cache_dir", os.path.join(os.getcwd(), ".plenipes", "cache")) if engine else os.path.join(os.getcwd(), ".plenipes", "cache")
    p_dir = os.path.join(base_dir, "podcasts", imp)
    os.makedirs(p_dir, exist_ok=True)
    return p_dir


def _resolve_podcast_slug(rel_path: str, engine=None) -> str:
    """解析防跨目录冲突的播客文件前缀（对子目录 index/readme 或同名文件自动附加目录前缀）"""
    clean_rel = os.path.splitext((rel_path or "").replace("\\", "/").strip("/"))[0]
    base_stem = os.path.basename(clean_rel)
    sub_dir = os.path.dirname(clean_rel)
    if not sub_dir:
        return base_stem
    if base_stem.lower() in ("index", "readme"):
        return clean_rel.lower().replace("/", "__")
    if engine and hasattr(engine, "meta") and hasattr(engine.meta, "get_documents_snapshot"):
        try:
            snap = engine.meta.get_documents_snapshot() or {}
            same_stem = [k for k in snap.keys() if os.path.splitext(os.path.basename(k))[0].lower() == base_stem.lower()]
            if len(same_stem) > 1:
                return clean_rel.lower().replace("/", "__")
        except Exception:
            pass
    return base_stem


def _resolve_localized_content(engine, rel_path: str, target_lang: str, safe_path: str = "", fallback_title: str = ""):
    """解析指定目标语种的本地化译文快照（优先多语种缓存，回退至 TranslationResolver）"""
    if not engine or not rel_path or not target_lang or target_lang.startswith("zh"):
        return None, None, None
    try:
        from services.api.routes.gov.context_shards.review_ops import get_translation_snapshot_impl
        snap = get_translation_snapshot_impl(engine, rel_path)
        lang_data = snap.get("langs", {}).get(target_lang)
        if lang_data and not lang_data.get("is_missing"):
            paras = [p.get("text", "") for p in lang_data.get("paragraphs", []) if p.get("type") != "spacer" and p.get("text")]
            if paras:
                return "\n\n".join(paras), lang_data.get("title"), lang_data.get("desc")
    except Exception as e:
        tlog.warning(f"Failed to resolve localized podcast content for {rel_path} ({target_lang}): {e}")
    if safe_path and os.path.isfile(safe_path):
        try:
            from core.bindery.translation_resolver import TranslationResolver
            vault_dir = getattr(engine, "vault_dir", "vault")
            res_title, res_body = TranslationResolver.resolve_chapter(
                file_path=safe_path, target_lang=target_lang, fallback_title=fallback_title, fallback_body="", vault_dir=vault_dir
            )
            if res_body and res_body.strip():
                return res_body, res_title, None
        except Exception:
            pass
    return None, None, None


@router.get("/api/podcast/voices")
async def get_podcast_voices() -> Dict[str, Any]:
    """获取系统支持的官方神经语音角色矩阵与 TTS 引擎清单（含本机实时就绪探测）"""
    from core.podcast.podcast_models import SUPPORTED_TTS_PROVIDERS, probe_ready_tts_providers
    return {"status": "success", "data": DEFAULT_VOICE_MAP, "providers": SUPPORTED_TTS_PROVIDERS, "ready_providers": probe_ready_tts_providers(get_global_engine())}


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

        # 多语言自动对接：若非中文广播，优先提取对应语种的本地化译文，无缓存时允许跨语种自动衍生
        if not target_lang.startswith("zh") and engine:
            loc_body, loc_title, loc_desc = _resolve_localized_content(
                engine, req.rel_path, target_lang, safe_path=safe_path or "", fallback_title=str(metadata.get("title") or "")
            )
            if loc_body:
                raw_content = loc_body
                if loc_title:
                    metadata["title"] = loc_title
                if loc_desc:
                    metadata["description"] = loc_desc

    if not raw_content.strip():
        raise HTTPException(status_code=400, detail="未提供有效的稿件文本内容以提炼剧本")

    try:
        script = PodcastScriptEngine.extract_script(
            content=raw_content, metadata=metadata, lang=target_lang, style=req.style or "tech_deep",
            max_turns=req.max_turns or 10, use_ai=bool(req.use_ai), engine=engine,
            focus_prompt=req.focus_prompt, host_a_name=req.host_a_name, host_b_name=req.host_b_name,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        tlog.error(f"🚨 播客剧本提炼异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"提炼剧本失败: {str(e)}")

    chaps = [c.to_dict() for c in script.chapters] if getattr(script, "chapters", None) else []
    shownotes = PodcastChapter.format_shownotes_timeline(script.chapters) if getattr(script, "chapters", None) else ""
    return {"status": "success", "data": {
        "title": script.title, "topic": script.topic, "lang": script.lang,
        "style": script.style, "summary": script.summary, "estimated_duration_sec": script.estimated_duration_sec,
        "turns": [{"speaker": t.speaker, "speaker_name": t.speaker_name, "text": t.text, "intent": t.intent} for t in script.turns],
        "chapters": chaps, "shownotes_formatted": shownotes
    }}


@router.post("/api/podcast/synthesize", dependencies=[Depends(verify_token)])
async def synthesize_podcast(req: PodcastSynthesizeRequest) -> Dict[str, Any]:
    """执行双人对谈语音合成，缝合生成单轨 MP3 音频"""
    engine = get_global_engine()
    imprint_id = getattr(engine, "imprint_id", "default") if engine else "default"
    cache_dir = _get_audio_cache_dir(engine, imprint_id)

    slug = _resolve_podcast_slug(req.rel_path, engine)
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
            imprint_name=brand_name, bgm_style=req.bgm_style or "cyber_ambient", tts_provider=req.tts_provider or "edge", engine=engine
        )
    except Exception as e:
        tlog.error(f"🚨 播客语音合成失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")
    audio_url = f"/api/podcast/audio/{imprint_id}/{filename}"
    _, shownotes = _load_sidecar_info(target_path)
    return {"status": "success", "data": {
        "filename": filename, "audio_url": audio_url, "file_size_bytes": res.file_size_bytes,
        "duration_ms": res.duration_ms, "turn_count": res.turn_count, "lang": res.lang,
        "voices_used": res.voices_used, "bgm_style": req.bgm_style or "cyber_ambient",
        "actual_provider": res.actual_provider, "fallback_reason": res.fallback_reason,
        "chapters": res.chapters, "shownotes_formatted": shownotes,
        "transcript_url": f"/api/podcast/audio/{imprint_id}/{os.path.splitext(filename)[0]}.vtt"
    }}


@router.api_route("/api/podcast/audio/{imprint_id}/{filename}", methods=["GET", "HEAD"])
async def serve_podcast_audio(imprint_id: str, filename: str):
    """安全流式返回播客 MP3 音频文件（支持拖拽进度条）"""
    engine = get_global_engine()
    safe_name = os.path.basename(filename)
    audio_path = os.path.join(_get_audio_cache_dir(engine, imprint_id), safe_name)
    if not os.path.isfile(audio_path):
        raise HTTPException(status_code=404, detail="未找到对应的播客音频文件")
    return FileResponse(path=audio_path, media_type="audio/mpeg", filename=safe_name)


@router.delete("/api/podcast/audio/{imprint_id}/{filename}", dependencies=[Depends(verify_token)])
async def delete_podcast_audio(imprint_id: str, filename: str) -> Dict[str, Any]:
    """物理清理指定播客单集 MP3 与章节 Sidecar 缓存文件"""
    engine = get_global_engine()
    safe_name = os.path.basename(filename)
    cache_dir = _get_audio_cache_dir(engine, imprint_id)
    audio_path = os.path.join(cache_dir, safe_name)
    if not os.path.isfile(audio_path):
        raise HTTPException(status_code=404, detail="未找到对应的播客音频文件")
    os.remove(audio_path)
    sc_path = os.path.splitext(audio_path)[0] + ".chapters.json"
    if os.path.isfile(sc_path):
        os.remove(sc_path)
    return {"status": "success", "deleted": safe_name}


def _find_podcast_file(cache_dir: str, slug: str, base_stem: str, lg: str, style_key: str):
    """按优先级查找指定语种和风格的播客音频文件"""
    candidates = [f"{slug}_{lg}_{style_key}.mp3"]
    if slug != base_stem and base_stem.lower() not in ("index", "readme"):
        candidates.append(f"{base_stem}_{lg}_{style_key}.mp3")
    if style_key == "tech_deep":
        candidates.append(f"{slug}_{lg}.mp3")
    for name in candidates:
        p = os.path.join(cache_dir, name)
        if os.path.isfile(p):
            return name, p
    return candidates[0], os.path.join(cache_dir, candidates[0])


@router.get("/api/podcast/info")
async def get_podcast_info(rel_path: str, lang: str = "zh", style: str = "tech_deep", langs: str = "") -> Dict[str, Any]:
    """查询指定稿件是否已生成就绪的播客音频（支持 langs 逗号列表批量探测已生成语种）"""
    engine = get_global_engine()
    imprint_id = getattr(engine, "imprint_id", "default") if engine else "default"
    slug = _resolve_podcast_slug(rel_path, engine)
    base_stem = os.path.splitext(os.path.basename(rel_path))[0]
    cache_dir = _get_audio_cache_dir(engine, imprint_id)
    style_key = style or "tech_deep"
    filename, target_path = _find_podcast_file(cache_dir, slug, base_stem, lang, style_key)
    avail = [c.strip() for c in langs.split(",") if c.strip() and os.path.isfile(_find_podcast_file(cache_dir, slug, base_stem, c.strip(), style_key)[1])] if langs else []

    if os.path.isfile(target_path):
        chaps, shownotes = _load_sidecar_info(target_path)
        return {"status": "success", "exists": True, "available_langs": avail, "data": {
            "filename": filename, "audio_url": f"/api/podcast/audio/{imprint_id}/{filename}",
            "file_size_bytes": os.path.getsize(target_path), "lang": lang, "style": style_key,
            "chapters": chaps, "shownotes_formatted": shownotes
        }}
    return {"status": "success", "exists": False, "available_langs": avail, "data": None}


@router.get("/api/podcast/bgm_options")
async def get_podcast_bgm_options() -> Dict[str, Any]:
    """获取所有受支持的播客垫乐风格列表"""
    from core.podcast.podcast_bgm_mixer import PodcastBGMMixer
    return {"status": "success", "options": PodcastBGMMixer.get_supported_styles()}


@router.post("/api/podcast/tts/test", dependencies=[Depends(verify_token)])
async def test_podcast_tts_provider(body: Dict[str, Any]) -> Dict[str, Any]:
    """单句试听与连通性测试（不降级掩盖错误，直接返回实际可用性）"""
    import base64
    from types import SimpleNamespace
    from core.podcast.podcast_models import synthesize_external_tts
    provider = str(body.get("tts_provider") or "edge").strip().lower()
    lang = str(body.get("lang") or "zh").strip().lower()
    sample = str(body.get("text") or ("你好，这是播客语音引擎连通性试听测试。" if lang == "zh" else "Hello, this is a podcast TTS engine connectivity test.")).strip()
    v_a = PodcastTTSEngine.get_voice_for_role(lang, "host_a")
    if provider == "edge":
        audio_bytes = await PodcastTTSEngine.synthesize_turn_audio(text=sample, voice=v_a, tts_provider="edge")
    else:
        eng = get_global_engine()
        base_pod = dict(getattr(getattr(eng, "config", None), "podcast", None) or {})
        merged_tts = dict(base_pod.get("podcast_tts_engines") or {})
        if isinstance(body.get("overrides"), dict):
            merged_tts.update({k: v for k, v in body["overrides"].items() if v not in (None, "")})
        proxy_eng = SimpleNamespace(config=SimpleNamespace(podcast={"podcast_tts_engines": merged_tts}))
        audio_bytes = await synthesize_external_tts(sample, v_a, provider, engine=proxy_eng)
    if not audio_bytes:
        raise HTTPException(status_code=400, detail=f"{provider} 引擎未返回有效音频，请检查密钥、模型名或本地服务地址是否已启动")
    return {"status": "success", "provider": provider, "audio_base64": base64.b64encode(audio_bytes).decode("ascii"), "mime": "audio/mpeg"}


@router.get("/api/podcast/feed/{imprint_id}")
async def get_podcast_rss_feed(request: Request, imprint_id: str, lang: str = "zh") -> Response:
    """生成并提供标准 Podcast RSS 2.0 XML 订阅源（联动原稿元数据与播客主控台配置）"""
    from core.podcast.podcast_rss_generator import generate_podcast_rss
    engine = get_global_engine()
    podcast_dir = _get_audio_cache_dir(engine, imprint_id)
    xml_str = generate_podcast_rss(imprint_id=imprint_id, base_url=str(request.base_url).rstrip("/"), lang=lang, podcast_dir=podcast_dir, engine=engine, use_api_audio_route=True)
    return Response(content=xml_str, media_type="application/xml")
