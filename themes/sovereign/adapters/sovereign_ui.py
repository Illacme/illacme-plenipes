# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Theme UI Components & Generators
模块职责：主权原生主题页面组件（面包屑、元数据、文章导航、特性卡片等）生成器。
"""

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


def build_article_meta(fm: Dict[str, Any], lang: str, reading_meta: Dict[str, int]) -> str:
    """构建文章顶部元数据区域（作者、日期、阅读时间、字数、标签）"""
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
    
    return f"""
    <div class="article-header-meta">
        <div class="meta-row">
            {' '.join(meta_items)}
        </div>
        {tags_html}
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
