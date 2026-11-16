# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Theme UI Components & Generators
模块职责：主权原生主题页面组件（面包屑、元数据、文章导航、特性卡片等）生成器。
"""

import os
import math
import re
from typing import Dict, Any, Optional
from .sovereign_i18n import get_ui_i18n


def calculate_reading_meta(text: str) -> Dict[str, int]:
    """计算预估阅读时间与字数统计"""
    clean_text = re.sub(r'<[^>]+>', '', text)
    # 统计中文字符数与英文单词数
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', clean_text))
    english_words = len(re.findall(r'[a-zA-Z0-9]+', clean_text))
    total_words = chinese_chars + english_words
    # 按中文 300 字/分，英文 180 词/分粗略估算
    minutes = max(1, math.ceil(chinese_chars / 300 + english_words / 180))
    return {
        "words": total_words,
        "minutes": minutes
    }


def build_breadcrumbs(lang: str, prefix: str, sub_path: str, title: str, root_path: str, nav_lang_prefix: str = "") -> str:
    """构建文章顶部面包屑导航条"""
    t = get_ui_i18n(lang)

    # 🚀 若未传入 nav_lang_prefix，自动从 sub_path 探测语种前缀
    if not nav_lang_prefix:
        _parts = sub_path.replace('\\', '/').strip('/').split('/')
        if _parts and len(_parts[0]) <= 3 and _parts[0].isalpha() and _parts[0].islower() and _parts[0] != "zh":
            nav_lang_prefix = f"{_parts[0]}/"

    home_url = f"{root_path}{nav_lang_prefix}index.html".replace('//', '/')
    items = [f'<a href="{home_url}" class="breadcrumb-item">{t.get("nav_home", "Home")}</a>']
    
    clean_prefix = prefix.strip("/\\") if prefix else ""
    
    # 1. 频道层级 (Docs, Blog, Showcase 等)
    if clean_prefix and clean_prefix.lower() not in ("page", "home"):
        prefix_title = t.get(f"nav_{clean_prefix.lower()}", clean_prefix.capitalize())
        prefix_url = f"{root_path}{nav_lang_prefix}{clean_prefix}/index.html".replace('//', '/')
        items.append(f'<span class="breadcrumb-sep">/</span><a href="{prefix_url}" class="breadcrumb-item">{prefix_title}</a>')
    
    # 2. 真实子目录层级 (智能去重：过滤与频道名相同的段落如 blog/ 以及语种段 en/ 等)
    parts = [p for p in sub_path.replace('\\', '/').split('/') if p and not p.endswith('.html')]
    for part in parts:
        part_clean = part.strip()
        if part_clean.lower() == clean_prefix.lower():
            continue
        if part_clean.lower() in ("zh", "en", "ja", "ko", "fr", "de", "es", "ru", "ar", "pt", "it", "zh-hans", "zh-hant"):
            continue
        items.append(f'<span class="breadcrumb-sep">/</span><span class="breadcrumb-item">{part_clean}</span>')
    
    # 3. 当前文章标题
    items.append(f'<span class="breadcrumb-sep">/</span><span class="breadcrumb-item active">{title}</span>')
    
    return f"""
    <nav class="breadcrumb-container" aria-label="breadcrumbs">
        {''.join(items)}
    </nav>
    """


def build_audio_player_widget(adapter: Any, fm: Dict[str, Any], lang: str, root_path: str = "") -> str:
    """构建读者消费闭环：伴读播放条 (Blog Reader Audio Widget)"""
    # 0. 创作者原稿主权显式禁用检查 (Frontmatter: podcast: false 或 audio: false)
    if fm.get('podcast') is False or fm.get('audio') is False or fm.get('audio_player') is False:
        return ""

    engine = getattr(adapter, 'engine', None)
    imprint_id = getattr(engine, 'imprint_id', 'default') or 'default' if engine else 'default'
    custom_audio = fm.get('podcast_audio') or fm.get('podcast_url') or (fm.get('audio') if isinstance(fm.get('audio'), str) else None)
    raw_slug = fm.get('slug') or ''
    rel_p = (fm.get('rel_path') or '').replace('\\', '/').strip('/')
    file_slug = fm.get('file_slug') or (os.path.splitext(os.path.basename(rel_p))[0] if rel_p else '')
    path_slug = os.path.splitext(rel_p)[0].lower().replace('/', '__') if rel_p else ''
    is_sub_idx = bool(os.path.dirname(rel_p)) and file_slug.lower() in ('index', 'readme')
    cand_slugs = [s for s in ([path_slug, raw_slug] if is_sub_idx else [path_slug, raw_slug, file_slug]) if s and not (is_sub_idx and s.lower() in ('index', 'readme'))]

    if raw_slug and engine and hasattr(engine, 'meta') and hasattr(engine.meta, 'get_documents_snapshot'):
        try:
            for r_p, d in engine.meta.get_documents_snapshot().items():
                if isinstance(d, dict) and d.get('slug') == raw_slug:
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
    detected_style = fm.get('podcast_style') or "tech_deep"

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
        "tech_deep": "深度剖析", "casual_brief": "通俗快讯",
        "debate": "观点交锋", "solo_read": "单人沉浸伴读"
    }
    style_label = style_names.get(detected_style, "技术播客")
    audio_src = custom_audio if custom_audio else f"{root_path}podcasts/{matched_file}"
    rss_url = f"{root_path}podcast-feed.xml"

    # 若配置了云端存储 CDN，优先使用 CDN 加速分发外链
    if matched_file and not custom_audio:
        try:
            from core.podcast.podcast_storage_engine import PodcastStorageEngine
            audio_src = PodcastStorageEngine.get_audio_public_url(matched_file, audio_src, engine)
        except Exception:
            pass

    # 解析 Sidecar 章节标记并生成平滑滚动章节药丸
    chapters_html = ""
    sc_file = (os.path.splitext(matched_file)[0] + ".chapters.json") if matched_file else None
    sc_path = os.path.join(cache_dir, sc_file) if (sc_file and os.path.isdir(cache_dir)) else None
    if sc_path and os.path.exists(sc_path):
        try:
            import json
            with open(sc_path, "r", encoding="utf-8") as sf:
                sc_data = json.load(sf)
                chapters = sc_data.get("chapters", [])
                if chapters:
                    pills = []
                    for c in chapters:
                        sec = c.get("start_seconds", 0)
                        timestr = c.get("start_time", "00:00")
                        title = c.get("title", "")
                        pills.append(
                            f'<button type="button" class="chapter-pill" data-time="{sec}">'
                            f'<span class="pill-time">{timestr}</span> {title}</button>'
                        )
                    chapters_html = f'<div class="audio-chapters-scroll">{"".join(pills)}</div>'
        except Exception:
            pass

    return f"""
    <div class="sovereign-audio-player" data-audio-src="{audio_src}">
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


def build_article_meta(fm: Dict[str, Any], lang: str, reading_meta: Dict[str, int], adapter: Any = None, root_path: str = "") -> str:
    """构建文章顶部元数据区域（作者、日期、阅读时间、字数、标签、伴读音频条）"""
    t = get_ui_i18n(lang)
    author = fm.get('author', '')
    date_str = fm.get('date_formatted') or fm.get('date') or ''
    tags = fm.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    meta_items = []
    if author:
        meta_items.append(f'<span class="meta-item author"><span class="meta-icon">✍️</span> {author}</span>')
    if date_str:
        meta_items.append(f'<span class="meta-item date"><span class="meta-icon">📅</span> {date_str}</span>')
    
    min_read = reading_meta.get("minutes", 1)
    word_count = reading_meta.get("words", 0)
    meta_items.append(f'<span class="meta-item read-time"><span class="meta-icon">⏱️</span> {min_read} {t.get("min_read", "min read")} ({word_count} {t.get("word_count", "words")})</span>')
    
    tags_html = ""
    if tags:
        tag_pills = "".join([f'<span class="tag-pill">#{tag}</span>' for tag in tags])
        tags_html = f'<div class="meta-tags">{tag_pills}</div>'
    
    audio_widget = build_audio_player_widget(adapter, fm, lang, root_path) if adapter else ""

    return f"""
    <div class="article-header-meta">
        <div class="meta-row">
            {' '.join(meta_items)}
        </div>
        {tags_html}
        {audio_widget}
    </div>
    """


def build_doc_pagination(prev_doc: Optional[Dict[str, str]], next_doc: Optional[Dict[str, str]], lang: str) -> str:
    """构建文章底部上一篇/下一篇导航翻页器"""
    t = get_ui_i18n(lang)
    prev_html = ""
    next_html = ""
    
    if prev_doc:
        prev_html = f"""
        <a href="{prev_doc['url']}" class="doc-pagination-item prev">
            <span class="pagination-sublabel">« {t.get('prev_doc', 'Previous')}</span>
            <span class="pagination-title">{prev_doc['title']}</span>
        </a>
        """
    else:
        prev_html = '<div class="doc-pagination-item empty"></div>'
        
    if next_doc:
        next_html = f"""
        <a href="{next_doc['url']}" class="doc-pagination-item next">
            <span class="pagination-sublabel">{t.get('next_doc', 'Next')} »</span>
            <span class="pagination-title">{next_doc['title']}</span>
        </a>
        """
    else:
        next_html = '<div class="doc-pagination-item empty"></div>'
        
    return f"""
    <div class="doc-pagination-wrapper">
        {prev_html}
        {next_html}
    </div>
    """
