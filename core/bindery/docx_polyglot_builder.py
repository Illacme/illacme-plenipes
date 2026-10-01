# -*- coding: utf-8 -*-
"""
Illacme Plenipes - DOCX Polyglot Parallel Table Grid Builder
模块职责：将多语言章节对齐并编排为 Word 原生无边框水平锁定对照表格。
适用场景：Word (.docx) 审校本多语种对照排版，确保段落级严格水平对齐与无边框出版美学。
🛡️ [SOP-01 规范]：单文件严格 <= 300 行。
"""

import re
import html
from typing import Any, Dict, List, Optional
from docx.oxml import parse_xml
from docx.shared import Pt, Inches, RGBColor


class DocxPolyglotBuilder:
    """🌐 Word 多语言水平锁定对照表格排版构建器"""

    LANG_META = {
        "zh": ("🇨🇳 简体中文", "ZH"),
        "en": ("🇬🇧 English Translation", "EN"),
        "ja": ("🇯🇵 日本語訳", "JA"),
        "fr": ("🇫🇷 Traduction Française", "FR"),
        "de": ("🇩🇪 Deutsche Übersetzung", "DE"),
        "es": ("🇪🇸 Traducción Española", "ES"),
        "ru": ("🇷🇺 Русский перевод", "RU")
    }

    @classmethod
    def split_markdown_blocks(cls, markdown_text: str) -> List[str]:
        """将 Markdown 文本切分为自闭合的语义块列表（标题、代码卡片、表格、普通段落）"""
        if not markdown_text or not markdown_text.strip():
            return []

        lines = markdown_text.strip().splitlines()
        blocks: List[str] = []
        curr_lines: List[str] = []
        in_code = False

        for line in lines:
            stripped = line.strip()

            # 1. 代码块状态机
            if stripped.startswith("```"):
                if in_code:
                    curr_lines.append(line)
                    blocks.append("\n".join(curr_lines))
                    curr_lines = []
                    in_code = False
                    continue
                else:
                    if curr_lines:
                        blocks.append("\n".join(curr_lines))
                        curr_lines = []
                    in_code = True
                    curr_lines.append(line)
                    continue

            if in_code:
                curr_lines.append(line)
                continue

            # 2. 标题独立成块
            if stripped.startswith("#"):
                if curr_lines:
                    blocks.append("\n".join(curr_lines))
                    curr_lines = []
                blocks.append(stripped)
                continue

            # 2.5 纯分割线（---, ***, ___）作为视觉断点收敛前文，但自身不入对照单元格避免串行
            if stripped in ("---", "***", "___"):
                if curr_lines:
                    blocks.append("\n".join(curr_lines))
                    curr_lines = []
                continue

            # 3. 空行触发普通段落收敛
            if not stripped:
                if curr_lines:
                    blocks.append("\n".join(curr_lines))
                    curr_lines = []
                continue

            curr_lines.append(line)

        if curr_lines:
            blocks.append("\n".join(curr_lines))

        return [b for b in blocks if b.strip()]

    @classmethod
    def render_polyglot_chapter(
        cls,
        doc: Any,
        ch: Dict[str, Any],
        polyglot_langs: List[str]
    ) -> None:
        """为单章节构建出版级多语言水平锁定对照网格"""
        from core.bindery.docx_text_parser import DocxTextParser

        cols_count = len(polyglot_langs)
        if cols_count < 2:
            return

        # 1. 提取各语种正文并分块
        blocks_by_lang: Dict[str, List[str]] = {}
        ch_by_lang = ch.get("chapter_by_lang") or {}

        from core.bindery.html_sanitizer import HtmlSanitizer

        for l in polyglot_langs:
            raw = ""
            if l in ch_by_lang:
                sub = ch_by_lang[l]
                raw = sub.get("raw_body") or sub.get("content") or sub.get("html_body") or ""
            if not raw and l == polyglot_langs[0]:
                raw = ch.get("raw_body") or ch.get("content") or ch.get("html_body") or ""
            if not raw:
                # 尝试从 HTML 提取
                h_body = ch.get("html_body", "")
                m = re.search(rf'data-lang=["\']?{l}["\']?[^>]*>(.*?)</div>\s*(?:<div class="wb-poly-item|\Z)', h_body, re.DOTALL)
                if m:
                    raw = m.group(1)

            # 🛡️ 关键安全过滤：彻底剥离前端容器标签 (div, span 等)，还原纯净语义
            cleaned_raw = HtmlSanitizer.sanitize_to_markdown(raw)
            blocks = cls.split_markdown_blocks(cleaned_raw)
            # 🛡️ 核心对齐守护：若正文首个语义块为 Markdown 一级标题 (# 标题)，因该标题已在章节外部由双语章题头统一呈现，将其剥离，彻底消灭标题二次重复与正文整列错位串行！
            if blocks and blocks[0].strip().startswith("# "):
                blocks = blocks[1:]
            blocks_by_lang[l] = blocks

        max_rows = max((len(blocks_by_lang[l]) for l in polyglot_langs), default=0)
        if max_rows == 0:
            return

        # 2. 创建 Word 原生对照表格 (1 行表头 + N 行对照内容)
        tbl = doc.add_table(rows=max_rows + 1, cols=cols_count)
        tbl.style = "Table Grid"

        # 3. 渲染表头行：语言标签徽章
        header_row = tbl.rows[0]
        # 表头跨页自动重复
        try:
            header_row._tr.get_or_add_trPr().append(parse_xml('<w:tblHeader xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
        except Exception:
            pass

        for c_idx, l in enumerate(polyglot_langs):
            cell = header_row.cells[c_idx]
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = 50800  # 4pt
            p.paragraph_format.space_after = 50800   # 4pt

            lang_name, tag = cls.LANG_META.get(l, (l.upper(), l.upper()))
            r_tag = p.add_run(f"[{tag}] ")
            r_tag.bold = True
            r_tag.font.size = Pt(9.0)
            try: r_tag.font.color.rgb = RGBColor(2, 132, 199)
            except Exception: pass

            r_name = p.add_run(lang_name)
            r_name.bold = True
            r_name.font.size = Pt(9.5)
            try: r_name.font.color.rgb = RGBColor(15, 23, 42)
            except Exception: pass

            # 浅蓝底色与底边框
            try:
                tcPr = cell._tc.get_or_add_tcPr()
                tcPr.append(parse_xml('<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:fill="F1F5F9"/>'))
                tcPr.append(parse_xml(
                    '<w:tcBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    '<w:top w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
                    '<w:bottom w:val="single" w:sz="12" w:space="0" w:color="0284C7"/>'
                    '</w:tcBorders>'
                ))
            except Exception:
                pass

        # 4. 渲染表体各行：段落级水平锁定
        for r_idx in range(max_rows):
            row = tbl.rows[r_idx + 1]
            # 允许行内跨页自然拆分，防止超长单元格死锁
            try:
                row._tr.get_or_add_trPr().append(parse_xml('<w:cantSplit xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
            except Exception:
                pass

            for c_idx, l in enumerate(polyglot_langs):
                cell = row.cells[c_idx]
                cell.text = ""
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = 38100  # 3pt
                p.paragraph_format.space_after = 38100   # 3pt
                p.paragraph_format.line_spacing = 1.25

                # 隐藏表格内竖线与外边框，保留行间微淡底线
                try:
                    tcPr = cell._tc.get_or_add_tcPr()
                    tcPr.append(parse_xml(
                        '<w:tcBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                        '<w:top w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
                        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="F1F5F9"/>'
                        '</w:tcBorders>'
                    ))
                    tcPr.append(parse_xml(
                        '<w:tcMar xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                        '<w:top w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/>'
                        '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="120" w:type="dxa"/>'
                        '</w:tcMar>'
                    ))
                except Exception:
                    pass

                blist = blocks_by_lang[l]
                if r_idx < len(blist):
                    block = blist[r_idx]
                    cls._render_cell_block(cell, p, block)
                else:
                    # 缺少对照段落时的优雅提示
                    r_empty = p.add_run("*(待对照文本)*")
                    r_empty.italic = True
                    try: r_empty.font.color.rgb = RGBColor(148, 163, 184)
                    except Exception: pass

        # 表格下方安全留白
        p_gap = doc.add_paragraph()
        p_gap.paragraph_format.space_before = 0
        p_gap.paragraph_format.space_after = 50800

    @classmethod
    def _render_cell_block(cls, cell: Any, paragraph: Any, block: str) -> None:
        """在表格单元格中将单个 Markdown 语义块渲染为富文本节点"""
        from core.bindery.docx_text_parser import DocxTextParser

        stripped = block.strip()
        if stripped.startswith("#"):
            # 标题处理
            m_h = re.match(r"^(#+)\s*(.*)", stripped)
            lvl = len(m_h.group(1)) if m_h else 1
            t_text = m_h.group(2) if m_h else stripped
            sz = 12.0 if lvl == 1 else (11.0 if lvl == 2 else 10.0)
            paragraph.paragraph_format.space_before = 50800
            paragraph.paragraph_format.space_after = 25400
            DocxTextParser.append_rich_runs(paragraph, t_text, is_bold=True)
            for r in paragraph.runs:
                r.font.size = Pt(sz)
                try: r.font.color.rgb = RGBColor(15, 23, 42)
                except Exception: pass
            return

        if stripped.startswith("```"):
            # 代码块处理
            lines = stripped.splitlines()
            lang = lines[0].lstrip("`").strip() if len(lines) > 0 else ""
            code_lines = lines[1:-1] if len(lines) >= 2 and lines[-1].strip().startswith("```") else lines[1:]
            paragraph.paragraph_format.space_before = 25400
            paragraph.paragraph_format.space_after = 25400
            from core.bindery.docx_syntax_highlighter import DocxSyntaxHighlighter
            DocxSyntaxHighlighter.highlight_code_block(paragraph, "\n".join(code_lines), lang=lang, font_size_pt=8.5)
            return

        # 普通段落：二次防线脱壳
        from core.bindery.html_sanitizer import HtmlSanitizer
        clean_text = HtmlSanitizer.sanitize_to_markdown(stripped) if ("<" in stripped and ">" in stripped) else stripped
        if not clean_text:
            return
        DocxTextParser.append_rich_runs(paragraph, clean_text)
        for r in paragraph.runs:
            if not r.font.size:
                r.font.size = Pt(9.5)
