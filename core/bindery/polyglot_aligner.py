# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Polyglot Block-Level Alignment Engine
模块职责：将多语种（中/英/日等）章节 HTML 正文对齐为块级 (Block-Level) 多语对照 DOM 节点。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import re
from typing import Dict, Any, List


class PolyglotAligner:
    """🌐 多语平行对照块级对齐器"""

    # 顶层块级标签正则匹配器
    BLOCK_SPLIT_REGEX = re.compile(
        r'(<(?:p|h[1-6]|blockquote|pre|table|ul|ol|div)[^>]*>.*?</(?:p|h[1-6]|blockquote|pre|table|ul|ol|div)>)',
        re.DOTALL | re.IGNORECASE
    )

    @classmethod
    def split_into_blocks(cls, html_body: str) -> List[str]:
        """使用标准 HTML DOM 解析器将章节 HTML 提取为 100% 完整闭合的顶级语义块列表"""
        if not html_body or not html_body.strip():
            return []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_body, 'html.parser')
            blocks = []
            for c in soup.contents:
                s = str(c).strip()
                if not s: continue
                if not getattr(c, 'name', None):
                    blocks.append(f"<p>{s}</p>")
                else:
                    blocks.append(s)
            if blocks:
                return blocks
        except (ImportError, Exception):
            pass

        # 正则回退提取
        raw_blocks = cls.BLOCK_SPLIT_REGEX.findall(html_body)
        blocks = [b.strip() for b in raw_blocks if b.strip()]
        if not blocks:
            paragraphs = [p.strip() for p in re.split(r'\n\s*\n', html_body) if p.strip()]
            blocks = [f"<p>{p}</p>" for p in paragraphs]

        return blocks if blocks else [html_body.strip()]

    @classmethod
    def align_chapter_polyglot(
        cls,
        chapter_by_lang: Dict[str, Dict[str, Any]],
        primary_lang: str = "zh",
        ordered_langs: List[str] = None
    ) -> Dict[str, Any]:
        """将单章节多语种内容对齐合成多栏并列对照研读矩阵"""
        if not ordered_langs:
            ordered_langs = list(chapter_by_lang.keys())
            if primary_lang in ordered_langs:
                ordered_langs.remove(primary_lang)
                ordered_langs.insert(0, primary_lang)

        lang_titles = {
            "zh": "🇨🇳 简体中文原稿",
            "en": "🇬🇧 English Translation",
            "ja": "🇯🇵 日本語訳",
            "fr": "🇫🇷 Traduction Française",
            "de": "🇩🇪 Deutsche Übersetzung"
        }

        base_ch = chapter_by_lang.get(primary_lang) or next(iter(chapter_by_lang.values()), {})
        base_raw_body = base_ch.get("html_body", "").strip()

        # 综合主标题与各语种标题字典
        main_title = base_ch.get("title", "未命名章节")
        titles_by_lang = {l: (chapter_by_lang.get(l) or {}).get("title", main_title) for l in ordered_langs}

        # 每个语种作为整章贯通的完整分栏呈现，并将各语种标题归位于分栏内
        columns_html = []
        for l in ordered_langs:
            ch_data = chapter_by_lang.get(l) or {}
            raw_body = ch_data.get("html_body", "").strip()
            tag_label = l.upper()
            lang_name = lang_titles.get(l, f"{tag_label} Edition")
            l_title = titles_by_lang.get(l, main_title)
            is_untranslated = (l != primary_lang) and (not raw_body or raw_body == base_raw_body or ch_data.get("is_pending"))
            if not raw_body:
                raw_body = base_raw_body or "<p></p>"

            # 剥离正文首行重复的 h1 标签
            cleaned_body = re.sub(r'^\s*<h1\b[^>]*>.*?</h1>\s*', '', raw_body, flags=re.DOTALL | re.IGNORECASE)

            if is_untranslated:
                content_html = (
                    f'  <div class="wb-poly-pending">\n'
                    f'    <span class="wb-poly-pending-icon">⏳</span>\n'
                    f'    <span>该章节 {lang_name} 对照译文待生成，暂显原文供研读参考。</span>\n'
                    f'  </div>\n'
                    f'  <div class="wb-poly-content wb-poly-untranslated" style="opacity:0.75;">{cleaned_body}</div>'
                )
            else:
                content_html = f'  <div class="wb-poly-content">{cleaned_body}</div>'

            title_html = f'  <h2 class="wb-poly-col-title">{l_title}</h2>\n' if l_title else ""
            columns_html.append(
                f'<div class="wb-poly-item wb-poly-column" data-lang="{l}">\n'
                f'  <div class="wb-poly-header">\n'
                f'    <span class="wb-lang-badge">{tag_label}</span>\n'
                f'    <span class="wb-poly-lang-name">{lang_name}</span>\n'
                f'  </div>\n'
                f'{title_html}'
                f'{content_html}\n'
                f'</div>'
            )

        full_body_html = f'<div class="wb-polyglot-block wb-polyglot-columns">\n{"".join(columns_html)}\n</div>'

        sub_titles = []
        for l in ordered_langs:
            if l != primary_lang and l in chapter_by_lang:
                t = chapter_by_lang[l].get("title")
                if t and t != main_title:
                    sub_titles.append(f'<span class="wb-poly-subtitle" data-lang="{l}">[{l.upper()}] {t}</span>')

        # 生成适合文档/Markdown/TXT 的多语对照 Markdown 正文
        poly_md_sections = []
        for l in ordered_langs:
            ch_data = chapter_by_lang.get(l) or {}
            l_body = (ch_data.get("raw_body") or "").strip()
            if not l_body and l == primary_lang:
                l_body = (base_ch.get("raw_body") or "").strip()
            tag_label = l.upper()
            lang_name = lang_titles.get(l, f"{tag_label} Edition")
            if l_body:
                poly_md_sections.append(f"### {lang_name} ({tag_label})\n\n{l_body}")
            else:
                poly_md_sections.append(f"### {lang_name} ({tag_label})\n\n*(待生成对照译文)*")
        full_body_markdown = "\n\n---\n\n".join(poly_md_sections)

        titles_by_lang = {l: (chapter_by_lang.get(l) or {}).get("title", main_title) for l in ordered_langs}
        return {
            "title": main_title,
            "titles_by_lang": titles_by_lang,
            "sub_titles_html": " ".join(sub_titles),
            "html_body": full_body_html,
            "raw_body": full_body_markdown,
            "languages": ordered_langs,
            "block_count": 1
        }

    @classmethod
    def build_polyglot_chapters(
        cls,
        assembler: Any,
        category: str,
        polyglot_langs: List[str],
        single_file: str = None
    ) -> List[Dict[str, Any]]:
        """调度收集多个语种章节并逐章通过全局绝对文件路径精准对齐，彻底消除 slug 冲突"""
        from .translation_resolver import TranslationResolver

        for l in polyglot_langs:
            if l != "zh": TranslationResolver.warm_up(l)

        lang_chapter_maps: Dict[str, Dict[str, Dict[str, Any]]] = {}
        primary_lang = polyglot_langs[0]
        base_chapters = assembler._collect_chapters(category=category, target_lang=primary_lang, single_file=single_file)

        # 核心保障：必须使用绝对物理文件路径 file_path 建立映射，彻底杜绝 slug 重复导致的章节错位
        for l in polyglot_langs:
            chs = base_chapters if l == primary_lang else assembler._collect_chapters(category=category, target_lang=l, single_file=single_file)
            lang_chapter_maps[l] = {ch.get("file_path", str(idx)): ch for idx, ch in enumerate(chs)}

        polyglot_tree: List[Dict[str, Any]] = []
        for idx, base_ch in enumerate(base_chapters):
            ch_key = base_ch.get("file_path", str(idx))
            chapter_by_lang = {l: lang_chapter_maps[l].get(ch_key, base_ch) for l in polyglot_langs}
            aligned = cls.align_chapter_polyglot(chapter_by_lang, primary_lang=primary_lang, ordered_langs=polyglot_langs)
            merged_ch = dict(base_ch)
            merged_ch["title"] = aligned["title"]
            merged_ch["titles_by_lang"] = aligned["titles_by_lang"]
            merged_ch["sub_titles_html"] = aligned["sub_titles_html"]
            merged_ch["html_body"] = aligned["html_body"]
            merged_ch["raw_body"] = aligned.get("raw_body") or base_ch.get("raw_body", "")
            merged_ch["languages"] = aligned["languages"]
            merged_ch["headings_by_lang"] = {l: chapter_by_lang[l].get("headings", []) for l in polyglot_langs}
            merged_ch["chapter_by_lang"] = chapter_by_lang
            polyglot_tree.append(merged_ch)

        return polyglot_tree



