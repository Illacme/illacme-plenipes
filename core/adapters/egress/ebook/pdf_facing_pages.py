# -*- coding: utf-8 -*-
"""
Illacme Plenipes - PDF Facing Pages Concordance Engine
模块职责：为固定版式 PDF 构建洛布古典丛书级（Loeb-Style）双开面对照排版。
排版规则：
  - 左页 (Verso / 偶数页)：源语言完整原稿，章眉居左，外切口居左，书脊装订线居右；
  - 右页 (Recto / 奇数页)：对译语言完整译稿，章眉居右，外切口居右，书脊装订线居左；
  - 自动插入必要空白补白页，确保翻到任何一个对开跨页时，左右双眼始终平行对照。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import re
from html import escape
from typing import Dict, Any, List, Optional
from core.bindery.html_sanitizer import HtmlSanitizer


class PDFFacingPagesBuilder:
    """📖 PDF 经典双开面对照（Facing Pages）排版构建器"""

    @classmethod
    def render_facing_chapters(
        cls,
        manuscript_tree: List[Dict[str, Any]],
        polyglot_langs: List[str],
        asset_map: Dict[str, str],
        publisher: str,
        author: str,
        is_single: bool = False
    ) -> List[str]:
        """将全书章节逐章重构为对称双开面（Verso / Recto）印刷序列"""
        if len(polyglot_langs) < 2:
            return []

        primary_lang = polyglot_langs[0]
        secondary_lang = polyglot_langs[1]
        sections: List[str] = []

        for idx, ch in enumerate(manuscript_tree, 1):
            ch_id = f"ch_{idx}"
            ch_by_lang = ch.get("chapter_by_lang") or {}

            # 1. 提取中英文章节标题与正文
            zh_data = ch_by_lang.get(primary_lang) or ch
            en_data = ch_by_lang.get(secondary_lang) or {}

            zh_title = zh_data.get("title") or ch.get("title", f"第 {idx} 章")
            en_title = en_data.get("title") or ch.get("titles_by_lang", {}).get(secondary_lang, f"Chapter {idx}")

            zh_raw = zh_data.get("html_body") or zh_data.get("raw_body", "")
            en_raw = en_data.get("html_body") or en_data.get("raw_body", "")
            if not en_raw and ch.get("raw_body"):
                en_raw = zh_raw

            zh_clean = cls._sanitize_body(zh_raw, asset_map, zh_title)
            en_clean = cls._sanitize_body(en_raw, asset_map, en_title)

            # 2. 组装左页 (Verso / 原语)
            verso_html = cls._build_verso_page(
                idx=idx, ch_id=ch_id, title=zh_title, body_html=zh_clean,
                publisher=publisher, author=author, is_single=is_single
            )

            # 3. 组装右页 (Recto / 对译)
            recto_html = cls._build_recto_page(
                idx=idx, ch_id=ch_id, title=en_title, body_html=en_clean,
                publisher=publisher, author=author, is_single=is_single
            )

            sections.append(verso_html)
            sections.append(recto_html)

        return sections

    @classmethod
    def _sanitize_body(cls, html_or_md: str, asset_map: Dict[str, str], title_to_strip: str = "") -> str:
        """安全清洗 HTML 与剥离首行重复 H1，内联插图 Base64 并自愈锚点"""
        if not html_or_md:
            return "<p></p>"

        # 如果传入的是 Markdown，则转为标准 HTML
        if not html_or_md.strip().startswith("<"):
            import markdown
            from markdown.extensions.toc import slugify_unicode
            md = markdown.Markdown(extensions=['extra', 'codehilite', 'tables', 'toc'], extension_configs={'toc': {'slugify': slugify_unicode}})
            cleaned_md = HtmlSanitizer.sanitize_to_markdown(html_or_md)
            # 剥离首行与标题相同的 H1
            lines = cleaned_md.splitlines()
            if lines and lines[0].strip().startswith("# "):
                lines = lines[1:]
            html_body = md.convert("\n".join(lines))
        else:
            html_body = html_or_md

        # 剥离首行重复 <h1> 标签（若存在）
        html_body = re.sub(r'^\s*<h1\b[^>]*>.*?</h1>\s*', '', html_body, flags=re.DOTALL | re.IGNORECASE)

        # 内联图片为 Base64
        for t_n, b64_u in asset_map.items():
            html_body = html_body.replace(f"../images/{t_n}", b64_u)

        # 清洗可能导致无头 Chromium 打印死循环的内联样式
        html_body = re.sub(r"-webkit-text-fill-color:\s*transparent;?", "color: #0f172a;", html_body)
        html_body = re.sub(r"(-webkit-)?background-clip:\s*text;?", "", html_body)
        html_body = html_body.replace("border-collapse: collapse;", "border-collapse: separate; border-spacing: 0;")
        html_body = re.sub(r'display:\s*grid;?', 'display: block;', html_body)
        html_body = re.sub(r'var\(--border-color\)', '#cbd5e1', html_body)
        html_body = re.sub(r'var\(--bg-elevated\)', '#f8fafc', html_body)
        html_body = re.sub(r'var\(--[a-zA-Z0-9_-]+\)', 'inherit', html_body)
        html_body = re.sub(r'(<(?:table|thead|tbody|tr|th|td)\b[^>]*?)\s+style="[^"]*"', r'\1', html_body)

        # 链接自愈为 PDF 内部相对锚点
        html_body = re.sub(r'href=["\']ch_\d+\.xhtml#(.*?)["\']', r'href="#\1"', html_body)
        html_body = re.sub(r'href=["\'](ch_\d+)\.xhtml["\']', r'href="#\1"', html_body)
        def _heal_rel_href(m):
            tag, h = m.group(0), m.group(1).strip()
            return tag if h.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')) else tag.replace(f'href="{h}"', 'class="pdf-unlinked"').replace(f"href='{h}'", 'class="pdf-unlinked"')
        html_body = re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>', _heal_rel_href, html_body)

        return html_body

    @classmethod
    def _build_verso_page(
        cls,
        idx: int,
        ch_id: str,
        title: str,
        body_html: str,
        publisher: str,
        author: str,
        is_single: bool
    ) -> str:
        """构建左页（Verso / 偶数页 / 源语言原稿）"""
        esc_title = escape(title)
        esc_pub = escape(publisher)
        esc_author = escape(author)

        nav_hdr = (
            f'<div class="facing-nav-header facing-verso-hdr">'
            f'<span class="facing-brand">{esc_pub}</span>'
            f'<span class="facing-crumb">第 {idx} 章 · {esc_title}</span>'
            f'<span class="facing-badge badge-verso">ZH 原稿 (VERSO)</span>'
            f'</div>'
        )
        art_meta = (
            f'<div class="article-meta-header">'
            f'<span class="article-meta-item">✍️ <strong class="article-meta-badge">{esc_author}</strong></span>'
            f'<span class="article-meta-item">🏢 {esc_pub}</span>'
            f'</div>'
        ) if (is_single and idx == 1) else ""

        ch_table = (
            f'<table class="chapter-table"><thead><tr><th>{nav_hdr}</th></tr></thead>'
            f'<tbody><tr><td>'
            f'<h1 class="chapter-heading facing-heading"><span class="ch-idx-badge">第 {idx} 章</span> {esc_title}</h1>'
            f'{art_meta}<div class="chapter-body facing-body">{body_html}</div>'
            f'</td></tr></tbody></table>'
        )
        return f'<section class="chapter-page facing-page facing-verso" id="{ch_id}-zh">{ch_table}</section>'

    @classmethod
    def _build_recto_page(
        cls,
        idx: int,
        ch_id: str,
        title: str,
        body_html: str,
        publisher: str,
        author: str,
        is_single: bool
    ) -> str:
        """构建右页（Recto / 奇数页 / 目标语言译稿）"""
        esc_title = escape(title)
        esc_pub = escape(publisher)
        esc_author = escape(author)

        nav_hdr = (
            f'<div class="facing-nav-header facing-recto-hdr">'
            f'<span class="facing-badge badge-recto">EN CONCORDANCE (RECTO)</span>'
            f'<span class="facing-crumb">Chapter {idx} · {esc_title}</span>'
            f'<span class="facing-brand">{esc_pub}</span>'
            f'</div>'
        )
        art_meta = (
            f'<div class="article-meta-header" style="justify-content: flex-end;">'
            f'<span class="article-meta-item">✍️ <strong class="article-meta-badge">{esc_author}</strong></span>'
            f'<span class="article-meta-item">🏢 {esc_pub}</span>'
            f'</div>'
        ) if (is_single and idx == 1) else ""

        ch_table = (
            f'<table class="chapter-table"><thead><tr><th>{nav_hdr}</th></tr></thead>'
            f'<tbody><tr><td>'
            f'<h1 class="chapter-heading facing-heading"><span class="ch-idx-badge">Chapter {idx}</span> {esc_title}</h1>'
            f'{art_meta}<div class="chapter-body facing-body">{body_html}</div>'
            f'</td></tr></tbody></table>'
        )
        return f'<section class="chapter-page facing-page facing-recto" id="{ch_id}-en">{ch_table}</section>'
