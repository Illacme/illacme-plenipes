#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Default Theme - Blog Synthesizer
职责：负责将博文元数据合成物理列表页。
🛡️ [Sovereign-Theme-v1.0]：主题自洽合成引擎。
"""

import os
from core.utils.language_hub import LanguageHub

from core.utils.tracing import tlog

class BlogSynthesizer:
    @staticmethod
    def synthesize(engine, output_dir_pattern):
        """
        🚀 博客全息列表合成：将账本中的博文元数据转化为物理 HTML 列表。
        """
        ledger = engine.meta
        docs = ledger.data.get("documents", {})
        theme = engine.active_theme
        
        # 1. 语种分箱 (Language Binning)
        lang_bins = {} # { lang_code: [blog_entries] }
        default_lang_iso = LanguageHub.resolve_to_iso(engine.i18n.source.lang_code)
        
        for rel_path, info in docs.items():
            if info.get('prefix') != 'blog':
                continue
                
            lang = info.get('lang', 'zh')
            lang_iso = LanguageHub.resolve_to_iso(lang)
            
            if lang not in lang_bins:
                lang_bins[lang] = []
            
            # 🚀 [V1.1] 动态 URL 生成：默认语言不带前缀
            if lang_iso == default_lang_iso:
                url = f"/blog/{info.get('slug')}.html"
            else:
                url = f"/{lang}/blog/{info.get('slug')}.html"
                
            entry = {
                "title": info.get('title', 'Untitled'),
                "slug": info.get('slug', 'post'),
                "description": info.get('seo', {}).get('description', '探索最新科技趋势与实用指南。'),
                "date": info.get('fm', {}).get('date', '2026-04-26'),
                "tags": info.get('fm', {}).get('tags', []),
                "url": url
            }
            lang_bins[lang].append(entry)
            
        # 2. 物理渲染
        for lang, entries in lang_bins.items():
            entries.sort(key=lambda x: str(x['date']), reverse=True)
            list_html = BlogSynthesizer._render_list_fragment(entries, lang)
            
            target_path = output_dir_pattern.replace("{theme}", theme)
            lang_iso = LanguageHub.resolve_to_iso(lang)
            
            if lang_iso == default_lang_iso:
                dist_dir = os.path.join(target_path, "blog")
                sub_path = "blog/index.html"
            else:
                dist_dir = os.path.join(target_path, lang, "blog")
                sub_path = f"{lang}/blog/index.html"
                
            os.makedirs(dist_dir, exist_ok=True)
            output_file = os.path.join(dist_dir, "index.html")
            
            # 使用 SSG 适配器进行渲染
            render_result = engine.ssg_adapter.render(
                body=list_html,
                fm={
                    "layout": "showcase", 
                    "slug": "index",
                    "title": "Blog Archive" if lang == 'en' else "博客存档"
                }, 
                target_lang=lang,
                sub_path=sub_path
            )
            
            # 物理剥离 HTML
            full_page = render_result[0] if isinstance(render_result, tuple) else render_result
            
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(full_page)
                tlog.info(f"✨ [主题合成器] 博客列表已物理落盘: {output_file} ({len(entries)} 篇文章)")
            except Exception as e:
                tlog.error(f"❌ [主题合成器] 写入失败: {e}")

    @staticmethod
    def _render_list_fragment(entries, lang):
        """🚀 渲染赛博风格的卡片流片段"""
        is_en = (lang == 'en')
        title = "Archive" if is_en else "博文存档"
        html = ['<div class="blog-list-container">', f'<h1 class="list-hero-title">{title}</h1>', '<div class="blog-grid">']
        
        for entry in entries:
            tags_html = "".join([f'<span class="card-tag">{tag}</span>' for tag in entry['tags'][:3]])
            read_more = "Read Entry →" if is_en else "阅读全文 →"
            card = f"""
            <a href="{entry['url']}" class="card-pioneer blog-card">
                <div class="card-meta">
                    <span class="card-date">{entry['date']}</span>
                    <div class="card-tags">{tags_html}</div>
                </div>
                <h3>{entry['title']}</h3>
                <p>{entry['description']}</p>
                <div class="card-footer">
                    <span class="read-more">{read_more}</span>
                </div>
            </a>
            """
            html.append(card)
            
        html.append('</div></div>')
        return "\n".join(html)
