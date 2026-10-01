# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Single-File Print-Ready PDF Book Adapter
模块职责：将文库全卷或单篇文稿编排导出为固定版式、印刷级出版物 (PDF)。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os, re, shutil, base64, tempfile, subprocess
from html import escape
from typing import Dict, Any, List, Optional

from core.adapters.egress.ebook.base import BaseEBookAdapter
from core.adapters.egress.ebook.colophon import ColophonBuilder
from core.adapters.egress.ebook.pdf_assets import PDFAssets
from core.utils.tracing import tlog

class PDFBookAdapter(BaseEBookAdapter):
    """📄 独立精致单文件 PDF 印本驱动（支持印刷级版式与纯 Python 优雅自愈）"""
    PLUGIN_ID = "pdf"
    DISPLAY_NAME = "PDF 精致印本"
    OUTPUT_EXTENSION = ".pdf"
    MIME_TYPE = "application/pdf"
    VERSION = "V1.0"
    DESCRIPTION = "固定版式印刷级出版物，包含精致扉页、统一页眉页脚与精准页码。"

    def bind_book(
        self,
        manuscript_tree: List[Dict[str, Any]],
        book_metadata: Dict[str, Any],
        cover_image_path: Optional[str] = None,
        target_lang: str = "zh",
        output_file_path: str = ""
    ) -> bool:
        """执行全卷或单篇排版，编译输出标准 PDF 实体"""
        if not output_file_path:
            tlog.error("❌ [PDF 装订] 未指定输出文件路径！")
            return False

        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)
            chrome_bin = self._find_chrome()

            # 1. 首选引擎：通过 Headless Chrome 与 CSS Paged Media 规范输出出版级精致印本
            if chrome_bin:
                try:
                    has_cov = bool(cover_image_path or book_metadata.get("cover_mode") != "none")
                    page_map = None
                    if len(manuscript_tree) > 1:
                        from core.adapters.egress.ebook.pdf_folio_stamp import PDFFolioStamp
                        probe_pdf = f"{output_file_path}.probe.pdf"
                        if self._render_via_headless(chrome_bin, manuscript_tree, book_metadata, cover_image_path, target_lang, probe_pdf):
                            ch_titles = [ch.get("title", "") for ch in manuscript_tree]
                            page_map = PDFFolioStamp.detect_chapter_pages(probe_pdf, len(manuscript_tree), has_cover=has_cov, chapter_titles=ch_titles)
                            try: os.remove(probe_pdf)
                            except OSError: pass

                    success = self._render_via_headless(chrome_bin, manuscript_tree, book_metadata, cover_image_path, target_lang, output_file_path, page_map=page_map)
                    if success and os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
                        from core.adapters.egress.ebook.pdf_folio_stamp import PDFFolioStamp
                        PDFFolioStamp.stamp_folios(output_file_path, has_cover=has_cov)
                        tlog.info(f"✨ [PDF 装订] 已通过印刷级渲染引擎成功导出: {os.path.basename(output_file_path)}")
                        return True
                except Exception as ce:
                    tlog.warning(f"⚠️ [PDF 装订] 印刷级无头渲染引擎异常，自动激活自愈引擎: {ce}")

            # 2. 备选自愈引擎：纯 Python 原生 ReportLab 排版兜底
            tlog.info("ℹ️ [PDF 装订] 启动原生 ReportLab 引擎执行安全装订...")
            return self._render_via_reportlab(manuscript_tree, book_metadata, cover_image_path, target_lang, output_file_path)

        except Exception as e:
            tlog.error(f"❌ [PDF 装订] 异常中断: {e}")
            return False

    def _render_via_headless(
        self,
        chrome_bin: str,
        manuscript_tree: List[Dict[str, Any]],
        meta: Dict[str, Any],
        cover_path: Optional[str],
        lang: str,
        out_pdf: str,
        page_map: Optional[Dict[int, int]] = None
    ) -> bool:
        """基于 W3C CSS Paged Media 规范构建高保真 HTML 并调用无头打印"""
        title = escape(meta.get("title", "数字出版物"))
        author = escape(meta.get("author", "制作团队"))
        publisher = escape(meta.get("publisher", "Illacme Press"))
        iso_lang = lang if lang != "zh" else "zh-CN"

        is_single = meta.get("is_single_article") or len(manuscript_tree) <= 1
        cover_mode = meta.get("cover_mode", "auto")

        # 🌐 多语对照版检测：3 语以上自动切换 A4 横版以确保每栏可读宽度
        polyglot_langs = meta.get("polyglot_langs") or []
        is_polyglot = bool(polyglot_langs and len(polyglot_langs) >= 2)
        polyglot_landscape_css = ""
        if is_polyglot and len(polyglot_langs) >= 3:
            polyglot_landscape_css = "@page { size: A4 landscape; }"

        cover_img_tag = ""
        if cover_mode != "none":
            # 1. 自定义上传封面 或 显式艺术大封面：优先直接渲染高保真封面大图
            has_valid_img = bool(cover_path and os.path.exists(cover_path))
            if has_valid_img and (cover_mode in ("custom", "generated") or meta.get("custom_cover_image")):
                with open(cover_path, "rb") as cf: b64 = base64.b64encode(cf.read()).decode("ascii")
                mime = "image/png" if cover_path.endswith(".png") else "image/jpeg"
                cover_img_tag = f'<section class="cover-page"><img src="data:{mime};base64,{b64}" class="cover-art" alt="Cover" /></section>'
            # 2. 智能自愈模式 (auto)：多语对照版默认采用全画幅双语对称排版文字封面
            elif is_polyglot and not is_single:
                titles_by_lang = meta.get("titles_by_lang", {})
                cover_cols = []
                for pl in polyglot_langs:
                    l_t = escape(titles_by_lang.get(pl, title))
                    cover_cols.append(f'<div class="wb-poly-column" style="text-align:center;"><div class="wb-poly-header" style="justify-content:center;"><span class="wb-lang-badge">{pl.upper()}</span></div><h1 class="cover-title">{l_t}</h1><div class="cover-author">{author}</div></div>')
                cover_footer = f'<div class="cover-author" style="margin-top:auto; font-size:8.5pt; opacity:0.65; letter-spacing:1px;">{publisher} · ALL RIGHTS RESERVED</div>'
                cover_img_tag = f'<section class="cover-page cover-fallback"><div class="cover-pub">{publisher}</div><div class="wb-polyglot-block wb-polyglot-columns">{chr(10).join(cover_cols)}</div>{cover_footer}</section>'
            # 3. 单语版有封面图时使用封面图
            elif has_valid_img:
                with open(cover_path, "rb") as cf: b64 = base64.b64encode(cf.read()).decode("ascii")
                mime = "image/png" if cover_path.endswith(".png") else "image/jpeg"
                cover_img_tag = f'<section class="cover-page"><img src="data:{mime};base64,{b64}" class="cover-art" alt="Cover" /></section>'
            # 4. 单语版无封面图 fallback
            elif not is_single:
                cover_footer = f'<div class="cover-author" style="margin-top:auto; font-size:8.5pt; opacity:0.65; letter-spacing:1px;">{publisher} · ALL RIGHTS RESERVED</div>'
                cover_img_tag = f'<section class="cover-page cover-fallback"><div class="cover-pub">{publisher}</div><div><h1 class="cover-title">{title}</h1><div class="cover-author">著 / {author}</div></div>{cover_footer}</section>'

        # 内联正文插图为 Base64，杜绝无头浏览器网络挂起
        asset_map = {}
        for ch in manuscript_tree:
            for a in ch.get("assets", []):
                t_n, s_p = a.get("target_name"), a.get("src_path") or a.get("abs_path")
                if t_n and s_p and t_n not in asset_map and os.path.exists(s_p):
                    m_tp = a.get("mime_type") or ("image/png" if s_p.endswith('.png') else "image/jpeg")
                    try:
                        with open(s_p, "rb") as af:
                            asset_map[t_n] = f"data:{m_tp};base64,{base64.b64encode(af.read()).decode('ascii')}"
                    except Exception: pass

        # 1. 前置目录索引页 (Print TOC)
        toc_tag = PDFAssets.render_toc_html(
            manuscript_tree,
            lang=lang,
            polyglot_langs=polyglot_langs if is_polyglot else None,
            page_map=page_map
        )

        # 2. 章节正文编排（默认 100% 呈现经典多栏并列对照研读矩阵，双开面对开作为扩展模式）
        facing_mode = meta.get("facing_pages_mode", False)
        if is_polyglot and len(polyglot_langs) == 2 and facing_mode:
            from core.adapters.egress.ebook.pdf_facing_pages import PDFFacingPagesBuilder
            ch_sections = PDFFacingPagesBuilder.render_facing_chapters(manuscript_tree, polyglot_langs, asset_map, publisher, author, is_single)
        else:
            ch_sections = []
            for idx, ch in enumerate(manuscript_tree):
                ch_id, ch_title, ch_body = f"ch_{idx + 1}", escape(ch.get("title", f"第 {idx + 1} 章")), ch.get("html_body", "<p></p>")
                for t_n, b64_u in asset_map.items(): ch_body = ch_body.replace(f"../images/{t_n}", b64_u)
                ch_body = re.sub(r"-webkit-text-fill-color:\s*transparent;?", "color: #0f172a;", ch_body)
                ch_body = re.sub(r"(-webkit-)?background-clip:\s*text;?", "", ch_body)
                ch_body = ch_body.replace("border-collapse: collapse;", "border-collapse: separate; border-spacing: 0;")
                ch_body = re.sub(r'(?<!polyglot["\s])display:\s*grid;?', 'display: block;', ch_body)
                ch_body = re.sub(r'var\(--border-color\)', '#cbd5e1', ch_body)
                ch_body = re.sub(r'var\(--bg-elevated\)', '#f8fafc', ch_body)
                ch_body = re.sub(r'var\(--[a-zA-Z0-9_-]+\)', 'inherit', ch_body)
                ch_body = re.sub(r'(<(?:table|thead|tbody|tr|th|td)\b[^>]*?)\s+style="[^"]*"', r'\1', ch_body)
                ch_body = re.sub(r'href=["\']ch_\d+\.xhtml#(.*?)["\']', r'href="#\1"', ch_body)
                ch_body = re.sub(r'href=["\'](ch_\d+)\.xhtml["\']', r'href="#\1"', ch_body)
                def _heal_rel_href(m):
                    tag, h = m.group(0), m.group(1).strip()
                    return tag if h.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')) else tag.replace(f'href="{h}"', 'class="pdf-unlinked"').replace(f"href='{h}'", 'class="pdf-unlinked"')
                ch_body = re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>', _heal_rel_href, ch_body)
                nav_hdr = f'<div class="chapter-nav-header"><span class="chapter-nav-brand">{publisher}</span><span class="chapter-nav-title">第 {idx + 1} 章 · {ch_title}</span></div>'
                art_meta = f'<div class="article-meta-header"><span class="article-meta-item">✍️ <strong class="article-meta-badge">{author}</strong></span><span class="article-meta-item">🏢 {publisher}</span></div>' if (is_single and not cover_img_tag and idx == 0) else ""
                heading_html = "" if is_polyglot else f'<h1 class="chapter-heading">{ch_title}</h1>'
                ch_table = (
                    f'<table class="chapter-table"><thead><tr><th>{nav_hdr}</th></tr></thead>'
                    f'<tfoot><tr><td style="height: 12mm; border: none !important; padding: 0 !important;"></td></tr></tfoot>'
                    f'<tbody><tr><td>{heading_html}{art_meta}<div class="chapter-body">{ch_body}</div></td></tr></tbody></table>'
                )
                ch_sections.append(f'<section class="chapter-page" id="{ch_id}">{ch_table}</section>')

        # 3. 末尾出版版权页 (Colophon，单篇文章导出自动抑制)
        colophon_tag = ""
        if not is_single:
            colophon_data = ColophonBuilder.build_colophon_data(manuscript_tree, meta, format_name="pdf")
            colophon_tag = PDFAssets.render_colophon_html(colophon_data, lang=lang, polyglot_langs=polyglot_langs if is_polyglot else None)

        head_html = f'<!DOCTYPE html><html lang="{iso_lang}"><head><meta charset="utf-8"><title>{title}</title><style>{PDFAssets.get_print_css()}\n{polyglot_landscape_css}</style></head><body>\n'
        tail_html = "\n</body></html>"

        all_sections = []
        if cover_img_tag: all_sections.append(cover_img_tag)
        if toc_tag: all_sections.append(toc_tag)
        all_sections.extend(ch_sections)
        if colophon_tag: all_sections.append(colophon_tag)

        # 剥离 4 字节 Emoji 防矢量流溢出
        clean_sections = [re.sub(r'[\U00010000-\U0010ffff]', '', s) for s in all_sections]

        from core.adapters.egress.ebook.pdf_chunk_printer import PDFChunkPrinter
        return PDFChunkPrinter.render_and_merge(
            chrome_bin=chrome_bin,
            head_html=head_html,
            sections=clean_sections,
            tail_html=tail_html,
            out_pdf=out_pdf
        )

    def _render_via_reportlab(
        self,
        manuscript_tree: List[Dict[str, Any]],
        meta: Dict[str, Any],
        cover_path: Optional[str],
        lang: str,
        out_pdf: str
    ) -> bool:
        """纯 Python ReportLab 兜底装订"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        except ImportError:
            tlog.warning("⚠️ [PDF 装订] 本机未预装 reportlab 依赖，已依赖主权无头浏览器引擎完成印刷排版。")
            return False

        font_name = "STSong-Light"
        try:
            pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        except Exception:
            font_name = "Helvetica"

        doc = SimpleDocTemplate(out_pdf, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("RTitle", parent=styles["Title"], fontName=font_name, fontSize=24, leading=30, alignment=1)
        sub_style = ParagraphStyle("RSub", parent=styles["Normal"], fontName=font_name, fontSize=12, leading=16, alignment=1, textColor="#666666")
        h1_style = ParagraphStyle("RH1", parent=styles["Heading1"], fontName=font_name, fontSize=16, leading=22, spaceAfter=12)
        body_style = ParagraphStyle("RBody", parent=styles["BodyText"], fontName=font_name, fontSize=10, leading=16, spaceAfter=8)

        story = []
        # 封面页
        if cover_path and os.path.exists(cover_path):
            try: story.append(RLImage(cover_path, width=400, height=533))
            except Exception: pass
            story.append(PageBreak())

        book_title = meta.get("title", "数字出版物")
        author = meta.get("author", "创作团队")
        story.append(Paragraph(escape(book_title), title_style))
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"著 / {escape(author)}", sub_style))
        story.append(Spacer(1, 30))

        for ch in manuscript_tree:
            story.append(PageBreak())
            ch_title = ch.get("title", "未命名章节")
            story.append(Paragraph(escape(ch_title), h1_style))
            # 过滤 HTML 标签提取纯净段落
            raw_html = ch.get("html_body", "")
            import re
            clean_text = re.sub(r'<[^>]+>', ' ', raw_html).strip()
            for p in clean_text.split('\n'):
                p = p.strip()
                if p: story.append(Paragraph(escape(p), body_style))

        def _add_page_num(canvas, doc_):
            canvas.saveState()
            canvas.setFont(font_name, 8)
            canvas.drawString(50, A4[1] - 35, escape(book_title))
            canvas.drawRightString(A4[0] - 50, A4[1] - 35, "Illacme Plenipes")
            canvas.drawCentredString(A4[0] / 2.0, 30, f"- {canvas.getPageNumber()} -")
            canvas.restoreState()

        doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=_add_page_num)
        return os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 0

    @staticmethod
    def _find_chrome() -> Optional[str]:
        """安全探测系统无头浏览器可执行二进制路径"""
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            shutil.which("google-chrome-stable") or shutil.which("google-chrome"),
            shutil.which("chromium") or shutil.which("chromium-browser"),
        ]
        for c in candidates:
            if c and os.path.exists(c) and os.access(c, os.X_OK):
                return c
        return None
