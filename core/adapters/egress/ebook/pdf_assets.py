# -*- coding: utf-8 -*-
"""
📚 [V125.0] Illacme Plenipes - Print-Ready PDF Assets & TOC / Colophon Shard
职责：集中管理 PDF 固定版式印刷级 CSS 样式、前置目录索引页与末尾版记卡片生成器。
规范：遵循 SOP-01 规范，单文件行数严格 ≤ 300 行。
"""

import os
import re
from html import escape
from typing import Dict, Any, List, Optional


class PDFAssets:
    """📄 PDF 印刷级版式与结构渲染组件"""

    LANG_NAMES = {
        "zh": "简体中文", "en": "English", "ja": "日本語",
        "fr": "Français", "de": "Deutsch", "es": "Español", "ru": "Русский"
    }
    TOC_TITLES = {
        "zh": "目  录", "en": "TABLE OF CONTENTS", "ja": "目  次",
        "fr": "TABLE DES MATIÈRES", "de": "INHALTSVERZEICHNIS"
    }

    @classmethod
    def get_print_css(cls) -> str:
        """获取经长文档跨页深度优化与 Chromium Blink 分页安全的纯净印刷级 CSS"""
        return """
@page {
    size: A4 portrait;
    margin: 0;
}
@page :first { margin: 0; }
/* 工业印厂装订线规范参考 (Gutter Margin): @page :left { margin: 20mm 20mm 20mm 14mm; } @page :right { margin: 20mm 14mm 20mm 20mm; } */
*, *::before, *::after { box-sizing: border-box; }
html, body {
    margin: 0;
    padding: 0;
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    line-height: 1.75;
    color: #1e293b;
}
p, li { orphans: 3; widows: 3; }
h1, h2, h3, h4, h5, h6, .chapter-heading, .toc-heading { break-after: avoid; page-break-after: avoid; }
pre, blockquote, tr, .toc-item, .callout { break-inside: avoid; page-break-inside: avoid; }
a { color: #0284c7; text-decoration: none; }
a:hover { text-decoration: underline; }
a.pdf-unlinked { color: inherit; text-decoration: none; pointer-events: none; }

/* 封面页 - 100% 满版全画幅铺满 A4 视口，彻底消除 210mm 换算舍入差导致的右下白边 */
.cover-page { text-align: center; margin: 0; padding: 0; width: 100vw; min-width: 100%; height: 100vh; min-height: 100%; max-height: 100vh; overflow: hidden; page-break-after: always; break-after: page; box-sizing: border-box; }
.cover-art { width: 100vw; height: 100vh; display: block; margin: 0 auto; object-fit: cover; }
.cover-fallback { background: radial-gradient(circle at 50% 25%, #0f2520 0%, #070e13 100%); color: #fff; text-align: center; padding: 35mm 16mm 25mm; display: flex; flex-direction: column; justify-content: space-between; border-radius: 0; }
.cover-pub { font-size: 11pt; letter-spacing: 3px; font-weight: 700; text-transform: uppercase; color: #10b981; margin-bottom: 12mm; }
.cover-title { font-size: 24pt; font-weight: 800; line-height: 1.35; margin-bottom: 10mm; color: #ffffff; text-shadow: 0 2px 8px rgba(0,0,0,0.6); }
.cover-author { font-size: 11pt; color: #94a3b8; letter-spacing: 0.5px; }

/* 多语对照封面卡片 - 告别刺眼白块，打造通透墨玉微光磨砂玻璃 */
.cover-fallback .wb-polyglot-columns { display: flex; gap: 6mm; width: 100%; margin: auto 0; }
.cover-fallback .wb-poly-column {
    flex: 1 1 0;
    background: rgba(255, 255, 255, 0.05);
    border: 1pt solid rgba(16, 185, 129, 0.35);
    border-radius: 8px;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.45);
    color: #f8fafc;
    padding: 14mm 8mm;
    box-sizing: border-box;
}
.cover-fallback .wb-poly-column .cover-title { font-size: 15pt; font-weight: 800; color: #ffffff; line-height: 1.35; margin-bottom: 8mm; text-shadow: 0 2px 6px rgba(0,0,0,0.6); }
.cover-fallback .wb-poly-column .cover-author { font-size: 10pt; color: #cbd5e1; }

/* 目录索引页 (Print TOC) - 块级安全流，支持长目录自然跨页断行与点状引线 */
.toc-page {
    break-before: page;
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
    padding: 18mm 16mm 28mm;
    box-sizing: border-box;
}
.toc-header { text-align: center; margin-bottom: 8mm; }
.toc-heading { font-size: 20pt; font-weight: 800; letter-spacing: 4px; color: #0f172a; margin: 0 0 3mm; }
.toc-divider { width: 36mm; height: 2pt; background: #10b981; margin: 0 auto 6mm; border-radius: 2px; }
.toc-list { list-style: none; padding: 0; margin: 0; display: block; }
.toc-item { display: block; margin-bottom: 2mm; break-inside: avoid; }
.toc-row { display: flex; align-items: center; width: 100%; font-size: 9pt; line-height: 1.5; padding: 1.5mm 0; border-bottom: 0.5pt solid #f1f5f9; text-decoration: none; color: inherit; }
.toc-ch-num { color: #10b981; font-weight: 700; margin-right: 8px; font-variant-numeric: tabular-nums; flex-shrink: 0; }
.toc-ch-title { font-weight: 600; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-shrink: 1; }
.toc-leader { flex: 1; border-bottom: 1pt dotted #cbd5e1; margin: 0 10px; min-width: 20px; }
.toc-target { color: #64748b; font-size: 8.5pt; font-weight: 500; flex-shrink: 0; font-family: -apple-system, sans-serif; }

/* 章节正文与章眉章脚 (W3C thead 跨页 Running Header 自动克隆与 tfoot 安全留白) */
.chapter-page {
    break-before: page;
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
    padding: 16mm 16mm 26mm;
    margin-bottom: 0;
    box-sizing: border-box;
}
body > .chapter-page:first-of-type { break-before: auto; }
.chapter-table { table-layout: fixed !important; width: 100% !important; max-width: 100% !important; border: none !important; border-collapse: collapse !important; margin: 0; padding: 0; }
.chapter-table thead { display: table-header-group; }
.chapter-table tfoot { display: table-footer-group; }
.chapter-table tbody { display: table-row-group; }
.chapter-table tr, .chapter-table td, .chapter-table th { border: none !important; padding: 0 !important; margin: 0 !important; text-align: left; vertical-align: top; }
.chapter-nav-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 0.5pt solid #e2e8f0; padding-bottom: 2mm; margin-bottom: 8mm; font-size: 8pt; color: #94a3b8; letter-spacing: 0.5px; }
.chapter-nav-brand { font-weight: 600; color: #059669; }
.chapter-nav-title { font-weight: 500; }
.chapter-heading { font-size: 18pt; font-weight: 800; color: #0f172a; border-bottom: 1.5pt solid #10b981; padding-bottom: 4mm; margin-bottom: 6mm; }
.article-meta-header { display: flex; align-items: center; gap: 14px; font-size: 8.5pt; color: #64748b; margin-top: -3mm; margin-bottom: 7mm; padding-bottom: 3mm; border-bottom: 0.5pt solid #f1f5f9; }
.article-meta-item { display: inline-flex; align-items: center; gap: 4px; }
.article-meta-badge { font-weight: 600; color: #059669; }
.chapter-body p { margin: 0 0 1em; line-height: 1.7; }
.chapter-body img { max-width: 100%; height: auto; display: block; margin: 6mm auto; border-radius: 4px; }

/* 打印排版安全保护：压制复杂弹性网格与透明渐变文字，杜绝分页计算死循环 */
* { -webkit-text-fill-color: initial !important; }
div[style*="grid"], .stats-matrix, .features-grid { display: block !important; }
div[style*="grid"] > div, .stats-matrix > div, .features-grid > div { margin-bottom: 4mm !important; break-inside: avoid !important; }

/* 表格跨页安全：自然折叠边框与流式宽度，杜绝字号浮点死锁 */
table { margin: 1em 0; border: 1px solid #cbd5e1; border-collapse: collapse !important; width: 100%; }
th, td { border: 0.5pt solid #cbd5e1; padding: 6px 10px; text-align: left; }
th { background: #f8fafc; font-weight: 700; color: #0f172a; }

/* 代码与引用 */
.chapter-body pre, .chapter-body code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 8.5pt; }
.chapter-body pre { background: #f8fafc; border: 0.5pt solid #e2e8f0; border-radius: 4px; padding: 10px 14px; overflow-x: auto; margin: 4mm 0; }
.codehilite { background: #f8fafc; border: 0.5pt solid #e2e8f0; border-left: 2.5pt solid #0284c7; border-radius: 4px; padding: 8px 12px; margin: 4mm 0; break-inside: avoid; }
.codehilite pre { background: transparent !important; border: none !important; padding: 0 !important; margin: 0 !important; }
.codehilite .k, .codehilite .kc, .codehilite .kd, .codehilite .kn, .codehilite .kr { color: #7c3aed; font-weight: 700; }
.codehilite .nf, .codehilite .nc, .codehilite .nn { color: #0284c7; font-weight: 600; }
.codehilite .s, .codehilite .s1, .codehilite .s2, .codehilite .sd, .codehilite .se { color: #15803d; }
.codehilite .c, .codehilite .c1, .codehilite .cm { color: #64748b; font-style: italic; }
.codehilite .mi, .codehilite .mf, .codehilite .mh, .codehilite .m { color: #d97706; }
.codehilite .nb, .codehilite .bp { color: #8250df; }
.codehilite .o, .codehilite .ow { color: #334155; }
.callout { border-left: 3.5pt solid #10b981; background: #f0fdf4; padding: 8px 14px; margin: 1em 0; border-radius: 0 4px 4px 0; }
.callout-title { font-weight: 700; color: #065f46; margin-bottom: 4px; }

/* 多语言对照版式 (Polyglot Concordance) - 印刷级并列双栏/多栏布局 */
.wb-polyglot-block { display: flex; flex-direction: row; gap: 12px; margin: 1em 0; width: 100%; box-sizing: border-box; }
.wb-poly-item, .wb-poly-column { flex: 1 1 0; min-width: 0; background: #fafbfc; border: 0.5pt solid #d1d5db; border-radius: 5px; padding: 8px 10px; box-sizing: border-box; }
.wb-poly-header { display: flex; align-items: center; gap: 5px; margin-bottom: 6px; padding-bottom: 4px; border-bottom: 1.5pt solid #10b981; }
.wb-poly-col-title { font-size: 14pt; font-weight: 800; color: #0f172a; line-height: 1.35; margin: 3mm 0 5mm; padding-bottom: 2.5mm; border-bottom: 0.5pt solid #e2e8f0; }
.wb-lang-badge { font-size: 7pt; font-weight: 700; color: #fff; background: #0284c7; padding: 1px 5px; border-radius: 3px; text-transform: uppercase; }
.wb-poly-lang-name { font-size: 7.5pt; font-weight: 600; color: #334155; }
.wb-poly-content { font-size: 9pt; line-height: 1.65; }
.wb-poly-content p { margin: 0 0 0.6em; }
.wb-poly-pending { background: #fffbeb; border: 0.5pt dashed #f59e0b; border-radius: 4px; padding: 4px 8px; font-size: 7.5pt; color: #92400e; margin-bottom: 6px; }
.wb-poly-subtitle { display: inline-block; font-size: 8pt; color: #64748b; margin-left: 8px; }
.pdf-poly-subtitles { margin: -2mm 0 3mm; font-size: 9pt; color: #475569; }

/* 经典双开面对照 (Facing Pages / Verso & Recto Spreads) */
.facing-page { break-after: page; page-break-after: always; padding-top: 2mm; margin-bottom: 10mm; }
.facing-verso { break-before: left; page-break-before: left; }
.facing-recto { break-before: right; page-break-before: right; }
.facing-nav-header { display: flex; align-items: center; border-bottom: 0.5pt solid #cbd5e1; padding-bottom: 2.5mm; margin-bottom: 6mm; font-size: 8pt; letter-spacing: 0.5px; }
.facing-verso-hdr { justify-content: space-between; }
.facing-recto-hdr { justify-content: space-between; flex-direction: row-reverse; }
.facing-brand { font-weight: 700; color: #059669; }
.facing-crumb { font-weight: 600; color: #475569; }
.facing-badge { font-size: 7pt; font-weight: 700; padding: 2px 7px; border-radius: 3px; letter-spacing: 0.5px; }
.badge-verso { background: #10b981; color: #ffffff; }
.badge-recto { background: #0284c7; color: #ffffff; }
.facing-heading { display: flex; align-items: baseline; gap: 10px; font-size: 16pt; font-weight: 800; color: #0f172a; border-bottom: 1.5pt solid #10b981; padding-bottom: 4mm; margin-bottom: 6mm; }
.ch-idx-badge { font-size: 9.5pt; font-weight: 700; color: #059669; background: rgba(16, 185, 129, 0.1); padding: 2px 8px; border-radius: 4px; }
.facing-body { font-size: 9.5pt; line-height: 1.75; text-align: justify; }

/* 出版物版记页 (Colophon) - 纯净块级安全排版与 separate 边框 */
.colophon-section { break-before: page; padding: 15mm 10mm; }
.colophon-card { border: 1pt solid #cbd5e1; border-radius: 8px; padding: 10mm 12mm; background: #fafafa; margin: 0; }
.colophon-header { font-size: 14pt; font-weight: 800; color: #0f172a; text-align: center; border-bottom: 1pt solid #10b981; padding-bottom: 4mm; margin-bottom: 6mm; letter-spacing: 1px; }
.colophon-grid { width: 100%; border: none; border-collapse: separate !important; border-spacing: 0 !important; font-size: 9pt; margin-bottom: 6mm; }
.colophon-grid td { border: none; padding: 5px 8px; }
.colophon-grid .k { width: 35%; color: #64748b; font-weight: 600; text-align: right; padding-right: 12px; }
.colophon-grid .v { color: #0f172a; }
.colophon-footer { text-align: center; font-size: 8pt; color: #64748b; border-top: 0.5pt solid #e2e8f0; padding-top: 4mm; line-height: 1.5; }
"""

    @classmethod
    def _build_toc_items(cls, manuscript_tree: List[Dict[str, Any]], lang: str = "zh",
                         page_map: Optional[Dict[int, int]] = None) -> str:
        """构建单语种目录条目 HTML，支持注入精准物理页码"""
        items = []
        for idx, ch in enumerate(manuscript_tree):
            ch_id = f"ch_{idx + 1}"
            t_map = ch.get("titles_by_lang", {})
            raw_title = t_map.get(lang) or ch.get("title") or f"Chapter {idx + 1}"
            title_escaped = escape(str(raw_title))
            num_str = f"{idx + 1:02d}"
            p_val = page_map.get(idx) if (page_map and idx in page_map) else (page_map.get(idx + 1) if page_map else None)
            target_str = f"P. {p_val}" if p_val is not None else f"CH {idx + 1} &rarr;"
            items.append(f'<li class="toc-item"><a href="#{ch_id}" class="toc-row">'
                         f'<span class="toc-ch-num">{num_str}.</span>'
                         f'<span class="toc-ch-title">{title_escaped}</span>'
                         f'<span class="toc-leader"></span>'
                         f'<span class="toc-target">{target_str}</span></a></li>')
        return ''.join(items)

    @classmethod
    def render_toc_html(cls, manuscript_tree: List[Dict[str, Any]], lang: str = "zh",
                        polyglot_langs: Optional[List[str]] = None,
                        page_map: Optional[Dict[int, int]] = None) -> str:
        """渲染高质感前置目录索引页 (Print TOC)，多语对照模式自动分栏，支持真实物理页码"""
        if not manuscript_tree or len(manuscript_tree) < 2:
            return ""

        is_polyglot = bool(polyglot_langs and len(polyglot_langs) >= 2)
        if not is_polyglot:
            code = (lang or "zh").lower().split("-")[0].split("_")[0]
            toc_title = cls.TOC_TITLES.get(code, cls.TOC_TITLES["zh"])
            return f"""
            <section class="toc-page" id="print-toc"><header class="toc-header">
                <h1 class="toc-heading">{toc_title}</h1><div class="toc-divider"></div>
            </header><ul class="toc-list">{cls._build_toc_items(manuscript_tree, lang, page_map=page_map)}</ul></section>"""

        # 多语对照分栏目录
        cols = []
        for pl in polyglot_langs:
            l_name = cls.LANG_NAMES.get(pl, pl.upper())
            l_toc_title = cls.TOC_TITLES.get(pl, cls.TOC_TITLES.get("en", "CONTENTS"))
            col_items = cls._build_toc_items(manuscript_tree, pl, page_map=page_map)
            cols.append(
                f'<div class="wb-poly-column" data-lang="{pl}">'
                f'<div class="wb-poly-header"><span class="wb-lang-badge">{pl.upper()}</span>'
                f'<span class="wb-poly-lang-name">{l_name} {l_toc_title}</span></div>'
                f'<div class="wb-poly-content"><ul class="toc-list">{col_items}</ul></div></div>'
            )
        return (f'<section class="toc-page" id="print-toc"><header class="toc-header">'
                f'<h1 class="toc-heading">{cls.TOC_TITLES.get("zh")} · {cls.TOC_TITLES.get("en")}</h1>'
                f'<div class="toc-divider"></div></header>'
                f'<div class="wb-polyglot-block wb-polyglot-columns">{chr(10).join(cols)}</div></section>')

    @classmethod
    def render_colophon_html(cls, colophon_data: Dict[str, Any], lang: str = "zh",
                             polyglot_langs: Optional[List[str]] = None) -> str:
        """渲染末尾正式出版版权页 (Colophon) HTML，多语对照模式自动分栏"""
        from core.adapters.egress.ebook.colophon import ColophonBuilder
        is_polyglot = bool(polyglot_langs and len(polyglot_langs) >= 2)
        if not is_polyglot:
            xhtml = ColophonBuilder.render_xhtml(colophon_data, iso_lang=lang)
            m = re.search(r'<body[^>]*>(.*?)</body>', xhtml, flags=re.DOTALL)
            body_content = m.group(1) if m else xhtml
            return f'<section class="colophon-section" id="print-colophon">{body_content}</section>'

        cols = []
        for pl in polyglot_langs:
            l_name = cls.LANG_NAMES.get(pl, pl.upper())
            c_iso = pl if pl != "zh" else "zh-CN"
            c_lbl = ColophonBuilder.get_nav_label(pl)
            raw = ColophonBuilder.render_xhtml(colophon_data, iso_lang=c_iso)
            m = re.search(r'<body[^>]*>(.*?)</body>', raw, flags=re.DOTALL)
            inner = m.group(1).strip() if m else raw.strip()
            cols.append(
                f'<div class="wb-poly-column" data-lang="{pl}">'
                f'<div class="wb-poly-header"><span class="wb-lang-badge">{pl.upper()}</span>'
                f'<span class="wb-poly-lang-name">{l_name} {c_lbl}</span></div>'
                f'<div class="wb-poly-content">{inner}</div></div>'
            )
        return (f'<section class="colophon-section" id="print-colophon">'
                f'<div class="wb-polyglot-block wb-polyglot-columns">{chr(10).join(cols)}</div></section>')
