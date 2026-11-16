# -*- coding: utf-8 -*-
"""
🎙️ Core Podcast Module - Sovereign Dual-Host Podcast Engine
"""

import json
import os
import shutil
from typing import Any, Dict, Optional
from core.utils.tracing import tlog

from .podcast_script_engine import (
    PodcastScriptEngine,
    DialogueTurn,
    PodcastScript
)
from .podcast_models import (
    PodcastChapter,
    ScriptExtractRequest,
    TurnPayload,
    PodcastSynthesizeRequest,
    resolve_podcast_slug,
    get_podcast_candidate_slugs,
)
from .tts_engine import (
    PodcastTTSEngine,
    AudioResult,
    DEFAULT_VOICE_MAP
)
from .podcast_rss_generator import (
    PodcastRSSGenerator,
    PodcastEpisode,
    generate_podcast_rss
)
from .podcast_ai_writer import PodcastAIWriter
from .podcast_bgm_mixer import PodcastBGMMixer
from .podcast_storage_engine import PodcastStorageEngine


def auto_synthesize_pending_podcasts(engine: Any, snapshot: Optional[Dict[str, Any]] = None) -> int:
    """🎙️ 全站发布无人值守补齐：扫描显式开启 podcast: true 且尚未合成音频的原稿并自动合成"""
    if not engine or getattr(getattr(engine, "args", None), "dry_run", False):
        return 0
    snap = snapshot
    if not isinstance(snap, dict) and hasattr(engine, "meta") and hasattr(engine.meta, "get_documents_snapshot"):
        try:
            snap = engine.meta.get_documents_snapshot()
        except Exception:
            snap = {}
    if not isinstance(snap, dict) or not snap:
        return 0

    imprint_id = getattr(engine, "imprint_id", "default") or "default"
    base_cache = getattr(engine, "cache_dir", None) or os.path.join(os.getcwd(), ".plenipes", "cache")
    cache_dir = os.path.join(base_cache, "podcasts", imprint_id)
    os.makedirs(cache_dir, exist_ok=True)
    existing_mp3s = [f for f in os.listdir(cache_dir) if f.endswith(".mp3")]
    vault_dir = getattr(engine, "vault_dir", None) or (engine.paths.get("vault") if hasattr(engine, "paths") and isinstance(engine.paths, dict) else "vault")

    synthesized = 0
    import asyncio
    from core.utils.text import parse_frontmatter
    for rel_p, doc in snap.items():
        if not isinstance(doc, dict) or doc.get("podcast") is not True:
            continue
        raw_slug = str(doc.get("slug") or "")
        pod_slug = resolve_podcast_slug(rel_p, explicit_slug=raw_slug, engine=engine, snapshot=snap)
        cands = get_podcast_candidate_slugs(rel_path=rel_p, explicit_slug=raw_slug)
        if any(f.startswith(tuple(f"{c}_" for c in cands)) for f in existing_mp3s):
            continue
        md_path = os.path.join(vault_dir, rel_p) if vault_dir else ""
        if not md_path or not os.path.isfile(md_path):
            continue
        try:
            with open(md_path, "r", encoding="utf-8") as mf:
                fm_dict, body, _ = parse_frontmatter(mf.read())
            if not body or not body.strip():
                continue
            script = PodcastScriptEngine.extract_script(content=body, metadata=fm_dict or doc, lang="zh", style="tech_deep", max_turns=10, use_ai=False, engine=engine)
            out_mp3 = os.path.join(cache_dir, f"{pod_slug}_zh_tech_deep.mp3")
            coro = PodcastTTSEngine.synthesize_script(script=script, output_file_path=out_mp3, pause_ms=380, bgm_style="cyber_ambient")
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    pool.submit(asyncio.run, coro).result(timeout=60)
            else:
                asyncio.run(coro)
            if os.path.isfile(out_mp3):
                existing_mp3s.append(os.path.basename(out_mp3))
                synthesized += 1
                tlog.info(f"🎙️ [无人值守播客] 已在发布流水线中自动补合音频: {rel_p}")
        except Exception as e:
            tlog.warning(f"⚠️ [无人值守播客] 自动补合 {rel_p} 跳过: {e}")
    return synthesized


def sync_podcast_assets_to_dist(engine: Any, dist_dir: Optional[str] = None, snapshot: Optional[Dict[str, Any]] = None) -> int:
    """将当前品牌的播客音频 (.mp3)、章节标记 (.chapters.json) 与 RSS Feed 同步至目标发布目录"""
    if not engine:
        return 0
    auto_synthesize_pending_podcasts(engine, snapshot=snapshot)
    if not dist_dir and hasattr(engine, "paths") and isinstance(engine.paths, dict):
        dist_dir = engine.paths.get("site_dir") or engine.paths.get("target_base")
    if not dist_dir or not os.path.isdir(dist_dir):
        return 0

    imprint_id = getattr(engine, "imprint_id", "default") or "default"
    base_cache = getattr(engine, "cache_dir", None) or os.path.join(os.getcwd(), ".plenipes", "cache")
    cache_dir = os.path.join(base_cache, "podcasts", imprint_id)
    if not os.path.isdir(cache_dir):
        return 0

    copied = 0
    try:
        out_podcasts = os.path.join(dist_dir, "podcasts")
        os.makedirs(out_podcasts, exist_ok=True)
        for fname in os.listdir(cache_dir):
            if fname.endswith((".mp3", ".chapters.json")):
                src_f = os.path.join(cache_dir, fname)
                dst_f = os.path.join(out_podcasts, fname)
                if not os.path.exists(dst_f) or os.path.getsize(src_f) != os.path.getsize(dst_f):
                    shutil.copy2(src_f, dst_f)
                if fname.endswith(".mp3"):
                    copied += 1

        raw_url = getattr(getattr(engine.config, "compliance", None), "site_url", None)
        site_url = raw_url if isinstance(raw_url, str) and raw_url else "http://localhost:43213"
        def_lang_obj = getattr(getattr(engine.config, "i18n_settings", None), "source", None)
        raw_lang = getattr(def_lang_obj, "lang_code", "zh") if def_lang_obj else "zh"
        cur_default_code = raw_lang if isinstance(raw_lang, str) and raw_lang and raw_lang != "auto" else "zh"
        rss_xml = generate_podcast_rss(
            imprint_id=imprint_id,
            base_url=site_url,
            lang=cur_default_code,
            podcast_dir=cache_dir,
            engine=engine,
        )
        if isinstance(rss_xml, str):
            with open(os.path.join(dist_dir, "podcast-feed.xml"), "w", encoding="utf-8") as rf:
                rf.write(rss_xml)
    except Exception as e:
        tlog.warning(f"⚠️ [伴读音频同步] 复制音频产物异常: {e}")
    return copied


def build_universal_audio_player_html(
    engine: Any,
    fm: Dict[str, Any],
    lang: str,
    root_path: str = "",
) -> str:
    """构建跨主题通用的读者伴读音频播放条 HTML (兼容 Sovereign 与 Universal 等主题)"""
    if not isinstance(fm, dict):
        return ""
    if fm.get("podcast") is False or fm.get("audio") is False or fm.get("audio_player") is False:
        return ""

    imprint_id = getattr(engine, "imprint_id", "default") or "default" if engine else "default"
    custom_audio = fm.get("podcast_audio") or fm.get("podcast_url") or (
        fm.get("audio") if isinstance(fm.get("audio"), str) else None
    )
    raw_slug = fm.get("slug") or ""
    rel_p = fm.get("rel_path") or ""
    file_slug = fm.get("file_slug") or (os.path.splitext(os.path.basename(rel_p))[0] if rel_p else "")
    cand_slugs = get_podcast_candidate_slugs(rel_path=rel_p, explicit_slug=raw_slug, file_slug=file_slug)

    if raw_slug and engine and hasattr(engine, "meta") and hasattr(engine.meta, "get_documents_snapshot"):
        try:
            for r_p, d in engine.meta.get_documents_snapshot().items():
                if isinstance(d, dict) and d.get("slug") == raw_slug:
                    base = os.path.splitext(os.path.basename(r_p))[0]
                    if base and base not in cand_slugs:
                        cand_slugs.append(base)
                    break
        except Exception:
            pass

    if not cand_slugs and not custom_audio:
        return ""

    base_cache = getattr(engine, "cache_dir", None) or os.path.join(os.getcwd(), ".plenipes", "cache")
    cache_dir = os.path.join(base_cache, "podcasts", imprint_id)
    matched_file = None
    detected_style = fm.get("podcast_style") or "tech_deep"

    if not custom_audio and os.path.isdir(cache_dir):
        for s in cand_slugs:
            for st in ("tech_deep", "casual_brief", "debate", "solo_read"):
                cand = f"{s}_{lang}_{st}.mp3"
                if os.path.exists(os.path.join(cache_dir, cand)):
                    matched_file, detected_style = cand, st
                    break
            if matched_file:
                break
            cand_legacy = f"{s}_{lang}.mp3"
            if os.path.exists(os.path.join(cache_dir, cand_legacy)):
                matched_file = cand_legacy
                break
            for f in os.listdir(cache_dir):
                if f.startswith(f"{s}_") and f.endswith(".mp3"):
                    matched_file = f
                    break
            if matched_file:
                break

    if not matched_file and not custom_audio:
        return ""

    style_names = {
        "tech_deep": "深度剖析",
        "casual_brief": "通俗快讯",
        "debate": "观点交锋",
        "solo_read": "单人沉浸伴读",
    }
    style_label = style_names.get(detected_style, "技术播客")
    audio_src = custom_audio if custom_audio else f"{root_path}podcasts/{matched_file}"
    rss_url = f"{root_path}podcast-feed.xml"

    if matched_file and not custom_audio:
        try:
            audio_src = PodcastStorageEngine.get_audio_public_url(matched_file, audio_src, engine)
        except Exception:
            pass

    chapters_html = ""
    sc_file = (os.path.splitext(matched_file)[0] + ".chapters.json") if matched_file else None
    sc_path = os.path.join(cache_dir, sc_file) if (sc_file and os.path.isdir(cache_dir)) else None
    if sc_path and os.path.exists(sc_path):
        try:
            with open(sc_path, "r", encoding="utf-8") as sf:
                sc_data = json.load(sf)
                chapters = sc_data.get("chapters", [])
                if chapters:
                    pills = [
                        f'<button type="button" class="chapter-pill" data-time="{c.get("start_seconds", 0)}">'
                        f'<span class="pill-time">{c.get("start_time", "00:00")}</span> {c.get("title", "")}</button>'
                        for c in chapters
                    ]
                    chapters_html = f'<div class="audio-chapters-scroll">{"".join(pills)}</div>'
        except Exception:
            pass

    return f"""
    <div class="sovereign-audio-player universal-audio-player" data-audio-src="{audio_src}">
        <div class="audio-player-top">
            <div class="audio-badge">
                <span class="audio-pulse-dot"></span>
                <span class="audio-icon">🎧</span>
                <span class="audio-label">AI 伴读播客 · <b>{style_label}</b></span>
            </div>
            <div class="audio-actions">
                <a href="{rss_url}" target="_blank" class="audio-chip" title="订阅播客 RSS">📻 播客订阅</a>
                <a href="{audio_src}" download class="audio-chip audio-download" title="下载原版 MP3">⬇️ 下载</a>
            </div>
        </div>
        <div class="audio-controls-row">
            <button type="button" class="audio-play-btn" title="播放 / 暂停">▶</button>
            <span class="audio-cur-time">0:00</span>
            <div class="audio-slider-wrap">
                <input type="range" class="audio-scrub" min="0" max="100" value="0" step="0.1">
                <div class="audio-track-fill"></div>
            </div>
            <span class="audio-total-time">--:--</span>
            <button type="button" class="audio-speed-btn" title="切换播放倍速">1.0x</button>
            <button type="button" class="audio-mute-btn" title="静音切换">🔊</button>
        </div>
        {chapters_html}
        <audio class="audio-native" preload="metadata" src="{audio_src}"></audio>
    </div>
    """


__all__ = [
    "PodcastScriptEngine",
    "DialogueTurn",
    "PodcastScript",
    "PodcastChapter",
    "PodcastTTSEngine",
    "AudioResult",
    "DEFAULT_VOICE_MAP",
    "PodcastRSSGenerator",
    "PodcastEpisode",
    "generate_podcast_rss",
    "PodcastAIWriter",
    "PodcastBGMMixer",
    "PodcastStorageEngine",
    "sync_podcast_assets_to_dist",
    "build_universal_audio_player_html",
]

