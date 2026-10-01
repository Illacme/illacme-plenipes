# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Word Document (.docx) Book Adapter
模块职责：将文库全卷或单篇文稿编排导出为出版规范、结构清晰的 Word 审校本 (.docx)。
适用场景：传统出版社审校、期刊论文投稿、Office 桌面协同与批注审阅。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from core.adapters.egress.ebook.base import BaseEBookAdapter
from core.adapters.egress.ebook.colophon import ColophonBuilder
from core.utils.tracing import tlog


class DocxBookAdapter(BaseEBookAdapter):
    """📑 出版级 Word 审校印本驱动（多级标题映射、扉页元数据排版与出版版权页）"""
    PLUGIN_ID = "docx"
    DISPLAY_NAME = "Word 文档"
    OUTPUT_EXTENSION = ".docx"
    MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    VERSION = "V1.0"
    DESCRIPTION = "出版级 Word 文档：排版规范、样式分级、封面与目录、审校页眉页脚，面向出版社审校与学术投稿。"

    def bind_book(
        self,
        manuscript_tree: List[Dict[str, Any]],
        book_metadata: Dict[str, Any],
        cover_image_path: Optional[str] = None,
        target_lang: str = "zh",
        output_file_path: str = ""
    ) -> bool:
        """执行 Word 排版编译，生成标准 .docx 实体文件"""
        if not output_file_path:
            tlog.error("❌ [Word 装订] 未指定输出文件路径！")
            return False

        try:
            from docx import Document
            from docx.shared import Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
        except ImportError:
            tlog.error("❌ [Word 装订] 缺少 python-docx 核心依赖，请先运行: pip install python-docx")
            return False

        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)
            doc = Document()

            # 1. 卷首扉页 (Cover Page)
            title = book_metadata.get("title", "数字出版集")
            author = book_metadata.get("author", "Illacme Editorial Team")
            publisher = book_metadata.get("publisher", "Illacme Plenipes Global Press")
            poly_langs = book_metadata.get("polyglot_langs") or (manuscript_tree[0].get("languages") if manuscript_tree else None) or []
            is_poly = bool(poly_langs and len(poly_langs) >= 2)

            if is_poly:
                from core.bindery.docx_polyglot_scaffold import DocxPolyglotScaffold
                DocxPolyglotScaffold.render_polyglot_cover(doc, book_metadata, poly_langs, title, author, publisher)
            else:
                p_title = doc.add_paragraph()
                p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_title.paragraph_format.space_before, p_title.paragraph_format.space_after = Pt(90), Pt(16)
                r_title = p_title.add_run(title)
                r_title.font.size, r_title.bold, r_title.font.color.rgb = Pt(26), True, RGBColor(16, 185, 129)
                if book_metadata.get("description"):
                    p_desc = doc.add_paragraph()
                    p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_desc.paragraph_format.space_after = Pt(110)
                    r_desc = p_desc.add_run(book_metadata['description'])
                    r_desc.font.size, r_desc.italic, r_desc.font.color.rgb = Pt(11), True, RGBColor(100, 116, 139)
                p_meta = doc.add_paragraph()
                p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_meta.paragraph_format.space_before = Pt(60)
                r_meta = p_meta.add_run(f"著/编：{author}\n出品：{publisher}\n装订日期：{datetime.now().strftime('%Y-%m-%d')} · 规格：{target_lang.upper()}")
                r_meta.font.size = Pt(10)
                r_meta.font.color.rgb = RGBColor(71, 85, 105)
                doc.add_page_break()

            # 2. 目录大纲清单
            if is_poly:
                from core.bindery.docx_polyglot_scaffold import DocxPolyglotScaffold
                DocxPolyglotScaffold.render_polyglot_toc(doc, manuscript_tree, poly_langs)
            else:
                doc.add_heading("📖 目录大纲 (Contents)", level=1)
                from core.bindery.docx_text_parser import DocxTextParser
                for idx, ch in enumerate(manuscript_tree, 1):
                    ch_title, ch_id = ch.get("title", f"第 {idx} 章"), ch.get("id") or f"ch_{idx}"
                    p_ch = doc.add_paragraph()
                    p_ch.paragraph_format.space_before, p_ch.paragraph_format.space_after = Pt(5), Pt(2)
                    DocxTextParser.add_hyperlink(p_ch, f"#{ch_id}", f"{idx}. {ch_title}", color="1e293b", underline=False, bold=True, font_size_pt=11)
                    headings = ch.get("headings", [])
                    if isinstance(headings, list):
                        for h in headings:
                            sub_t = h.get("title") or h.get("text", "")
                            if sub_t and sub_t != ch_title:
                                p_sub = doc.add_paragraph()
                                p_sub.paragraph_format.left_indent, p_sub.paragraph_format.space_before, p_sub.paragraph_format.space_after = Pt(18), Pt(1), Pt(1)
                                DocxTextParser.add_hyperlink(p_sub, f"#{ch_id}", f"·  {sub_t}", color="64748b", underline=False, font_size_pt=9.5)
                doc.add_page_break()

            # 3. 逐章编排正文
            for idx, ch in enumerate(manuscript_tree, 1):
                ch_title, ch_id = ch.get("title", f"第 {idx} 章"), ch.get("id") or f"ch_{idx}"
                h_ch = doc.add_paragraph(style="Heading 1")
                try:
                    from docx.oxml import parse_xml
                    h_ch._p.append(parse_xml(f'<w:bookmarkStart xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:id="{idx}" w:name="{ch_id}"/>'))
                    h_ch.add_run(f"第 {idx} 章 {ch_title}")
                    h_ch._p.append(parse_xml(f'<w:bookmarkEnd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:id="{idx}"/>'))
                except Exception:
                    h_ch.add_run(f"第 {idx} 章 {ch_title}")

                if is_poly:
                    t_by_l = ch.get("titles_by_lang", {})
                    sub_items = [f"Chapter {idx} · {t_by_l[l]}" if l == "en" else f"[{l.upper()}] {t_by_l[l]}" for l in poly_langs[1:] if l in t_by_l and t_by_l[l] != ch_title]
                    if sub_items:
                        p_sub = doc.add_paragraph()
                        p_sub.paragraph_format.space_before, p_sub.paragraph_format.space_after = Pt(2), Pt(6)
                        r_sub = p_sub.add_run("   |   ".join(sub_items))
                        r_sub.font.size, r_sub.italic = Pt(10.5), True
                        try: r_sub.font.color.rgb = RGBColor(71, 85, 105)
                        except Exception: pass
                    from core.bindery.docx_polyglot_builder import DocxPolyglotBuilder
                    DocxPolyglotBuilder.render_polyglot_chapter(doc, ch, poly_langs)
                else:
                    raw_body = ch.get("raw_body") or ch.get("content") or ch.get("html_body") or ""
                    from core.bindery.html_sanitizer import HtmlSanitizer
                    raw_body = HtmlSanitizer.sanitize_to_markdown(raw_body)
                    self._render_markdown_to_docx(doc, raw_body)

                if idx < len(manuscript_tree): doc.add_page_break()

            # 4. 卷尾版权声明页 (Colophon)
            if is_poly:
                from core.bindery.docx_polyglot_scaffold import DocxPolyglotScaffold
                DocxPolyglotScaffold.render_polyglot_colophon(doc, manuscript_tree, book_metadata, poly_langs)
            else:
                doc.add_page_break()
                doc.add_heading("📜 版权声明 (Colophon)", level=1)
                c_dict = ColophonBuilder.build_colophon_data(manuscript_tree=manuscript_tree, book_metadata=book_metadata, format_name="docx")
                for line in [f"出版典籍：{c_dict.get('title', title)}", f"责任作者：{c_dict.get('author', author)}", f"出版机构：{c_dict.get('publisher', publisher)}", "技术驱动：Illacme Plenipes Sovereign Digital Bindery Hub", f"版权规范：{c_dict.get('license', 'All Rights Reserved')}"]: doc.add_paragraph(line)

            doc.save(output_file_path)
            tlog.info(f"✨ [Word 装订] 已成功导出审校印本: {os.path.basename(output_file_path)}")
            return True

        except Exception as e:
            tlog.error(f"❌ [Word 装订] 异常中断: {e}")
            return False


    def _render_markdown_to_docx(self, doc: Any, markdown_text: str):
        """将 Markdown 语法解析并映射为 Word 段落、原生层级与可编辑数学公式"""
        lines = markdown_text.splitlines()
        in_code_block, in_math_block, code_lang = False, False, ""
        code_lines: List[str] = []
        math_lines: List[str] = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # 1. 多行代码块处理
            if stripped.startswith("```"):
                if in_code_block:
                    in_code_block = False
                    from core.bindery.docx_text_parser import DocxTextParser
                    if code_lang.lower() in ("mermaid", "flowchart"):
                        if not DocxTextParser.create_mermaid_figure(doc, code_lines):
                            DocxTextParser.create_code_block_card(doc, code_lines, lang=code_lang)
                    else:
                        DocxTextParser.create_code_block_card(doc, code_lines, lang=code_lang)
                    code_lines.clear()
                else:
                    in_code_block = True
                    code_lang = stripped.lstrip("`").strip()
                    code_lines.clear()
                i += 1
                continue
            if in_code_block:
                code_lines.append(line)
                i += 1
                continue

            # 2. 块级数学公式处理 ($$...$$)
            if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 2:
                self._add_block_formula(doc, stripped[2:-2].strip())
                i += 1
                continue
            if stripped == "$$" or stripped.startswith("$$"):
                if in_math_block:
                    in_math_block = False
                    if stripped != "$$": math_lines.append(stripped[:-2])
                    self._add_block_formula(doc, "\n".join(math_lines).strip())
                    math_lines.clear()
                else:
                    in_math_block = True
                    math_lines.clear()
                    if len(stripped) > 2: math_lines.append(stripped[2:])
                i += 1
                continue
            if in_math_block:
                if stripped.endswith("$$"):
                    in_math_block = False
                    math_lines.append(stripped[:-2])
                    self._add_block_formula(doc, "\n".join(math_lines).strip())
                    math_lines.clear()
                else:
                    math_lines.append(line)
                i += 1
                continue

            if not stripped:
                i += 1
                continue

            # 3. 原生 Markdown 表格映射
            if stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 2:
                tbl_lines = []
                while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                    tbl_lines.append(lines[i].strip())
                    i += 1
                from core.bindery.docx_text_parser import DocxTextParser
                DocxTextParser.parse_markdown_table(doc, tbl_lines)
                continue

            # 4. 原生水平分割线映射 (---, ***)
            if re.match(r'^(-{3,}|\*{3,}|_{3,})$', stripped):
                from core.bindery.docx_text_parser import DocxTextParser
                DocxTextParser.add_horizontal_rule(doc)
                i += 1
                continue

            # 5. 标题映射
            m_h = re.match(r'^(#{1,6})\s+(.*)$', stripped)
            if m_h:
                level = min(4, len(m_h.group(1)) + 1)
                doc.add_heading(m_h.group(2).strip(), level=level)
                i += 1
                continue

            # 6. 引用块 Callout 映射
            if stripped.startswith(">"):
                quote_text = re.sub(r'^>\s*(\[!.*\])?\s*', '', stripped).strip()
                p_quote = doc.add_paragraph()
                p_quote.paragraph_format.left_indent = 180000
                self._append_runs_with_math(p_quote, quote_text, is_italic=True)
                i += 1
                continue

            # 7. 列表项映射
            if stripped.startswith(("- ", "* ", "+ ")):
                p_item = doc.add_paragraph(style='List Bullet' if 'List Bullet' in doc.styles else None)
                self._append_runs_with_math(p_item, stripped[2:].strip())
                i += 1
                continue

            m_num = re.match(r'^\d+\.\s+(.*)$', stripped)
            if m_num:
                p_item = doc.add_paragraph(style='List Number' if 'List Number' in doc.styles else None)
                self._append_runs_with_math(p_item, m_num.group(1).strip())
                i += 1
                continue

            # 8. 普通段落
            p_para = doc.add_paragraph()
            self._append_runs_with_math(p_para, stripped)
            i += 1


    def _add_block_formula(self, doc: Any, latex: str):
        """将块级 LaTeX 公式编译为 Word 原生居中 OMML 数学对象"""
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from core.bindery.math_packager import MathPackager
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        omml = MathPackager.latex_to_omml(latex, display="block")
        if omml:
            try:
                from docx.oxml import parse_xml
                p._p.append(parse_xml(omml))
                return
            except Exception as e:
                tlog.debug(f"⚠️ [Word 公式] 块级 OMML XML 解析降级: {e}")
        r = p.add_run(f"$${latex}$$")
        r.font.name = 'Cambria Math'
        r.font.italic = True

    def _append_runs_with_math(self, p: Any, text: str, is_italic: bool = False):
        """将文本按行内公式、超链接与加粗切分，生成 Word 原生富文本与可交互超链接"""
        from core.bindery.docx_text_parser import DocxTextParser
        DocxTextParser.append_rich_runs(p, text, is_italic=is_italic)


