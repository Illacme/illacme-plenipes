# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Single-File Interactive WebBook Adapter
模块职责：将文库全卷编排导出为单个自包含、免阅读器依赖的高清离线网页书 (HTML)，支持多语对照矩阵。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import base64
from html import escape
from typing import Dict, Any, List, Optional

from core.adapters.egress.ebook.base import BaseEBookAdapter
from core.adapters.egress.ebook.colophon import ColophonBuilder
from core.adapters.egress.ebook.webbook_assets import WebBookAssets
from core.bindery.toc_builder import TocBuilder
from core.utils.tracing import tlog


class WebBookAdapter(BaseEBookAdapter):
    """🌐 单文件交互式网页书驱动（100% 离线自包含，支持多语对照研读矩阵）"""
    PLUGIN_ID = "webbook"
    DISPLAY_NAME = "单文件网页书 (WebBook)"
    OUTPUT_EXTENSION = ".html"
    MIME_TYPE = "text/html; charset=utf-8"
    VERSION = "V2.0"
    DESCRIPTION = "零阅读器依赖，内置侧边目录、多语对照矩阵、三模主题与即时搜索的高清离线电子书。"

    def bind_book(
        self,
        manuscript_tree: List[Dict[str, Any]],
        book_metadata: Dict[str, Any],
        cover_image_path: Optional[str] = None,
        target_lang: str = "zh",
        output_file_path: str = ""
    ) -> bool:
        if not output_file_path:
            tlog.error("❌ [WebBook 装订] 未指定输出文件路径！")
            return False

        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)
            book_title = book_metadata.get("title", "未命名作品集")
            author = book_metadata.get("author", "极客创作者")
            iso_lang = target_lang if target_lang != "zh" else "zh-CN"
            polyglot_langs: List[str] = book_metadata.get("polyglot_langs", [])

            # 1. 抽取并内联封面图片为 Data URI
            cover_data_uri = ""
            if cover_image_path and os.path.exists(cover_image_path):
                ext = os.path.splitext(cover_image_path)[1].lower()
                mime = "image/png" if ext == ".png" else ("image/svg+xml" if ext == ".svg" else "image/jpeg")
                with open(cover_image_path, "rb") as cf:
                    cover_data_uri = f"data:{mime};base64,{base64.b64encode(cf.read()).decode('utf-8')}"

            # 2. 预编译物理插图为 Base64 并构建快速查找表
            asset_map: Dict[str, str] = {}
            for ch in manuscript_tree:
                for asset in ch.get("assets", []):
                    t_name = asset.get("target_name")
                    s_path = asset.get("src_path") or asset.get("abs_path")
                    if t_name and s_path and t_name not in asset_map and os.path.exists(s_path):
                        a_ext = os.path.splitext(s_path)[1].lower()
                        a_mime = asset.get("mime_type") or ("image/png" if a_ext == ".png" else "image/jpeg")
                        try:
                            with open(s_path, "rb") as af:
                                asset_map[t_name] = f"data:{a_mime};base64,{base64.b64encode(af.read()).decode('utf-8')}"
                        except Exception:
                            pass

            # 3. 编排章节正文与侧边目录
            toc_items = []
            chapters_html = []

            for idx, ch in enumerate(manuscript_tree):
                ch_id = f"ch_{idx + 1}"
                ch_title = escape(ch.get("title", f"第 {idx + 1} 节"))
                raw_body = ch.get("html_body", "<p></p>")

                # 内联插图 Data URI 替换
                def repl_img(m):
                    src = m.group(1).strip()
                    for t_name, b64_uri in asset_map.items():
                        if t_name in src:
                            return m.group(0).replace(f'src="{src}"', f'src="{b64_uri}"').replace(f"src='{src}'", f"src='{b64_uri}'")
                    return m.group(0)

                body_with_images = re.sub(r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>', repl_img, raw_body)
                healed_body = re.sub(r'href="ch_\d+\.xhtml#(.*?)"', r'href="#\1"', body_with_images)
                healed_body = re.sub(r'href="(ch_\d+)\.xhtml"', r'href="#\1"', healed_body)

                sub_titles_html = ch.get("sub_titles_html", "")
                sub_title_block = f'<div class="wb-poly-subtitles">{sub_titles_html}</div>' if sub_titles_html else ""

                titles_by_lang = ch.get("titles_by_lang", {})
                data_attrs = "".join([f' data-title-{l}="{escape(t)}"' for l, t in titles_by_lang.items()])

                headings = TocBuilder.get_or_extract_headings(ch)
                headings_by_lang = ch.get("headings_by_lang", {})
                toc_items.append(TocBuilder.render_webbook_toc_group(
                    idx, ch_id, ch_title, headings,
                    titles_by_lang=titles_by_lang,
                    headings_by_lang=headings_by_lang
                ))
                chapters_html.append(f"""
                <article id="{ch_id}" class="wb-chapter" data-title="{ch_title}">
                    <header class="wb-chapter-header">
                        <span class="wb-chapter-badge">Chapter {idx + 1}</span>
                        <h2 class="wb-chapter-title"{data_attrs}>{ch_title}</h2>
                        {sub_title_block}
                    </header>
                    <div class="wb-chapter-body">{healed_body}</div>
                </article>""")

            # 4. 版记 Colophon 组装 (支持多语版记无缝变脸)
            colophon_data = ColophonBuilder.build_colophon_data(manuscript_tree, book_metadata, "webbook")
            colophon_nav_attrs = ""
            colophon_cards = []
            active_langs = polyglot_langs if polyglot_langs else [target_lang]
            for l in active_langs:
                c_iso = l if l != "zh" else "zh-CN"
                c_lbl = ColophonBuilder.get_nav_label(c_iso)
                colophon_nav_attrs += f' data-title-{l}="{escape(c_lbl)}"'
                c_body = ColophonBuilder.render_xhtml(colophon_data, iso_lang=c_iso)
                c_match = re.search(r'<body[^>]*>(.*?)</body>', c_body, flags=re.DOTALL)
                colophon_cards.append(f'<div class="wb-poly-item wb-colophon-card" data-lang="{l}">{c_match.group(1) if c_match else c_body}</div>')

            nav_lbl = ColophonBuilder.get_nav_label(iso_lang)
            toc_items.append(f'<div class="wb-toc-group" data-ch-id="colophon"><div class="wb-toc-row"><a href="#colophon" class="wb-toc-item wb-toc-chapter" data-id="colophon"><span class="wb-toc-num">✦</span> <span class="wb-toc-text"{colophon_nav_attrs}>{nav_lbl}</span></a></div></div>')
            chapters_html.append(f'<article id="colophon" class="wb-chapter"><div class="wb-polyglot-block">{"".join(colophon_cards)}</div></article>')

            # 5. 渲染整卷完整自包含 WebBook
            full_html = self._render_full_document(
                book_title, author, iso_lang, cover_data_uri,
                ''.join(toc_items), ''.join(chapters_html),
                polyglot_langs=polyglot_langs
            )
            with open(output_file_path, "w", encoding="utf-8") as out_f:
                out_f.write(full_html)

            tlog.info(f"✨ [WebBook 装订成功] 离线网页书已落盘: {output_file_path} (共 {len(manuscript_tree)} 章节)")
            return True
        except Exception as e:
            tlog.error(f"❌ [WebBook 装订异常] 封包失败: {e}")
            return False

    def _render_full_document(
        self, title: str, author: str, lang: str, cover_uri: str,
        toc_html: str, content_html: str, polyglot_langs: List[str] = None
    ) -> str:
        cover_block = f'<div class="wb-cover-box"><img src="{cover_uri}" alt="Cover" class="wb-cover-img"/></div>' if cover_uri else ""
        search_ph = "🔍 Search chapters..." if lang == "en" else ("🔍 目次・章を検索..." if lang == "ja" else "🔍 快速查找章节...")
        toggle_title = "Toggle Sidebar" if lang == "en" else ("目次切替" if lang == "ja" else "切换目录")

        # 多语切换器与多栏并列对照栏控制条 (若为多语合卷版本)
        polyglot_bar = ""
        if polyglot_langs and len(polyglot_langs) >= 2:
            lang_names = {"zh": "🇨🇳 简体中文", "en": "🇬🇧 English", "ja": "🇯🇵 日本語", "fr": "🇫🇷 Français", "de": "🇩🇪 Deutsch"}
            capsules = []
            for l in polyglot_langs:
                active_cls = " active" if (l == lang or (l == "zh" and lang == "zh-CN")) else ""
                lbl = lang_names.get(l, l.upper())
                capsules.append(f'<button type="button" class="wb-primary-item{active_cls}" data-lang="{l}">{lbl}</button>')

            polyglot_bar = f"""
            <div class="wb-polyglot-bar">
                <div class="wb-poly-switcher-group">
                    <div class="wb-primary-group">
                        <span class="wb-bar-label">主语言:</span>
                        <div class="wb-segmented-capsule" role="tablist" aria-label="全书主语言切换">
                            {''.join(capsules)}
                        </div>
                    </div>
                    <span class="wb-bar-sep">|</span>
                    <div class="wb-compare-group">
                        <span class="wb-bar-label">+ 对照栏:</span>
                        <div id="wb-compare-chips" class="wb-compare-chips" data-all-langs="{','.join(polyglot_langs)}"></div>
                    </div>
                </div>
            </div>"""



        return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="dark">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{escape(title)}</title>
<style>{WebBookAssets.get_embedded_css()}</style>
</head>
<body>
<div id="wb-progress" class="wb-progress-bar"></div>
<header class="wb-topbar">
    <div style="display:flex;align-items:center;gap:10px;">
        <button id="wb-toggle-sidebar" class="wb-btn" title="{toggle_title}">☰</button>
        <span class="wb-book-title">{escape(title)}</span>
    </div>
    {polyglot_bar}
    <div class="wb-controls">
        <button class="wb-theme-btn" data-theme="light" title="Light">☀️</button>
        <button class="wb-theme-btn active" data-theme="dark" title="Dark">🌙</button>
        <button class="wb-theme-btn" data-theme="sepia" title="Sepia">☕</button>
        <button id="wb-font-dec" class="wb-btn" title="A-">A-</button>
        <button id="wb-font-inc" class="wb-btn" title="A+">A+</button>
    </div>
</header>
<div class="wb-layout">
    <aside id="wb-sidebar" class="wb-sidebar">
        {cover_block}
        <div class="wb-search-box"><input type="text" id="wb-search" placeholder="{search_ph}" /></div>
        <nav class="wb-toc" id="wb-toc-nav">{toc_html}</nav>
        <div class="wb-sidebar-footer">© {escape(author)} · Illacme Press</div>
    </aside>
    <main class="wb-main" id="wb-main-container">
        <div class="wb-content-wrapper">{content_html}</div>
    </main>
</div>
<script>{WebBookAssets.get_embedded_js()}</script>
</body></html>"""
