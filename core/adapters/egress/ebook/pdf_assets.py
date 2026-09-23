# -*- coding: utf-8 -*-
"""
📚 [V125.0] Illacme Plenipes - Print-Ready PDF Assets & TOC / Colophon Shard
职责：集中管理 PDF 固定版式印刷级 CSS 样式、前置目录索引页与末尾版记卡片生成器。
规范：遵循 SOP-01 规范，单文件行数严格 ≤ 300 行。
"""

import os
import re
from html import escape
from typing import Dict, Any, List


class PDFAssets:
    """📄 PDF 印刷级版式与结构渲染组件"""

    TOC_TITLES = {
        "zh": "目  录",
        "en": "TABLE OF CONTENTS",
        "ja": "目  次"
    }

    @classmethod
    def get_print_css(cls) -> str:
        """获取经长文档跨页深度优化与 Chromium Blink 分页安全的纯净印刷级 CSS"""
        return """
@page {
    size: A4 portrait;
    margin: 20mm 16mm 20mm 16mm;
}
*, *::before, *::after { box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    line-height: 1.75;
    color: #1e293b;
    background: #ffffff;
    margin: 0;
    padding: 0;
}
a { color: #0284c7; text-decoration: none; }
a:hover { text-decoration: underline; }
a.pdf-unlinked { color: inherit; text-decoration: none; pointer-events: none; }

/* 封面页 - 严格约束高度在 A4 打印区域内 (235mm)，杜绝跨页换行死锁 */
.cover-page { text-align: center; margin: 0; padding: 0; max-height: 235mm; overflow: hidden; }
.cover-art { max-width: 100%; max-height: 225mm; display: block; margin: 0 auto; object-fit: contain; }
.cover-fallback { background: #0b1219; color: #fff; text-align: center; padding: 25mm 15mm; border-radius: 6px; }
.cover-pub { font-size: 11pt; letter-spacing: 2px; text-transform: uppercase; color: #10b981; margin-bottom: 25mm; }
.cover-title { font-size: 24pt; font-weight: 800; line-height: 1.3; margin-bottom: 12mm; }
.cover-author { font-size: 12pt; color: #94a3b8; }

/* 目录索引页 (Print TOC) - 块级安全流，支持长目录自然跨页断行与点状引线 */
.toc-page { break-before: page; padding: 6mm 4mm 10mm; }
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

/* 章节正文与章眉章脚 */
.chapter-page { break-before: page; padding-top: 2mm; margin-bottom: 10mm; }
body > .chapter-page:first-of-type { break-before: auto; }
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
.callout { border-left: 3.5pt solid #10b981; background: #f0fdf4; padding: 8px 14px; margin: 1em 0; border-radius: 0 4px 4px 0; }
.callout-title { font-weight: 700; color: #065f46; margin-bottom: 4px; }

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
    def render_toc_html(cls, manuscript_tree: List[Dict[str, Any]], lang: str = "zh") -> str:
        """渲染高质感前置目录索引页 (Print TOC)，带点状引线与同文档内部跳转"""
        if not manuscript_tree or len(manuscript_tree) < 2:
            return ""

        code = (lang or "zh").lower().split("-")[0].split("_")[0]
        toc_title = cls.TOC_TITLES.get(code, cls.TOC_TITLES["zh"])

        items = []
        for idx, ch in enumerate(manuscript_tree):
            ch_id = f"ch_{idx + 1}"
            raw_title = ch.get("title") or f"Chapter {idx + 1}"
            title_escaped = escape(str(raw_title))
            num_str = f"{idx + 1:02d}"

            items.append(f"""
            <li class="toc-item">
                <a href="#{ch_id}" class="toc-row">
                    <span class="toc-ch-num">{num_str}.</span>
                    <span class="toc-ch-title">{title_escaped}</span>
                    <span class="toc-leader"></span>
                    <span class="toc-target">CH {idx + 1} &rarr;</span>
                </a>
            </li>""")

        return f"""
        <section class="toc-page" id="print-toc">
            <header class="toc-header">
                <h1 class="toc-heading">{toc_title}</h1>
                <div class="toc-divider"></div>
            </header>
            <ul class="toc-list">
                {''.join(items)}
            </ul>
        </section>"""

    @classmethod
    def render_colophon_html(cls, colophon_data: Dict[str, Any], lang: str = "zh") -> str:
        """渲染末尾正式出版版权页 (Colophon) HTML"""
        from core.adapters.egress.ebook.colophon import ColophonBuilder
        xhtml = ColophonBuilder.render_xhtml(colophon_data, iso_lang=lang)
        m = re.search(r'<body[^>]*>(.*?)</body>', xhtml, flags=re.DOTALL)
        body_content = m.group(1) if m else xhtml
        return f'<section class="colophon-section" id="print-colophon">{body_content}</section>'
