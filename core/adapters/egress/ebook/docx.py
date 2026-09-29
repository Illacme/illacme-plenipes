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
    DISPLAY_NAME = "Word 审校本"
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

            p_title = doc.add_paragraph()
            p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_title = p_title.add_run(f"\n\n\n{title}\n")
            run_title.font.size = Pt(26)
            run_title.font.bold = True
            run_title.font.color.rgb = RGBColor(16, 185, 129)

            if book_metadata.get("description"):
                p_desc = doc.add_paragraph()
                p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run_desc = p_desc.add_run(f"{book_metadata['description']}\n")
                run_desc.font.size = Pt(12)
                run_desc.font.italic = True
                run_desc.font.color.rgb = RGBColor(100, 116, 139)

            p_meta = doc.add_paragraph()
            p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_meta = p_meta.add_run(
                f"\n著/编：{author}\n出品：{publisher}\n"
                f"装订日期：{datetime.now().strftime('%Y-%m-%d')} · 规格：{target_lang.upper()}\n"
            )
            run_meta.font.size = Pt(10.5)
            run_meta.font.color.rgb = RGBColor(71, 85, 105)

            # 分页符：进入目录与正文
            doc.add_page_break()

            # 2. 目录大纲清单
            doc.add_heading("📖 目录大纲 (Contents)", level=1)
            for idx, ch in enumerate(manuscript_tree, 1):
                ch_title = ch.get("title", f"第 {idx} 章")
                doc.add_paragraph(f"{idx}. {ch_title}", style='List Number' if 'List Number' in doc.styles else None)
                headings = ch.get("headings", [])
                if isinstance(headings, list):
                    for h in headings:
                        sub_t = h.get("title") or h.get("text", "")
                        if sub_t and sub_t != ch_title:
                            p_sub = doc.add_paragraph(f"    · {sub_t}")
                            p_sub.paragraph_format.left_indent = Pt(18)

            doc.add_page_break()

            # 3. 逐章编排正文
            for idx, ch in enumerate(manuscript_tree, 1):
                ch_title = ch.get("title", f"第 {idx} 章")
                doc.add_heading(f"第 {idx} 章 {ch_title}", level=1)

                raw_body = ch.get("raw_body") or ""
                if not raw_body and ch.get("content"):
                    raw_body = re.sub(r'<[^>]+>', '', ch["content"])

                self._render_markdown_to_docx(doc, raw_body)

                # 章末分页（最后一章除外）
                if idx < len(manuscript_tree):
                    doc.add_page_break()

            # 4. 卷尾版权声明页 (Colophon)
            doc.add_page_break()
            doc.add_heading("📜 版权声明 (Colophon)", level=1)
            colophon_dict = ColophonBuilder.build_colophon_data(
                manuscript_tree=manuscript_tree,
                book_metadata=book_metadata,
                format_name="docx"
            )
            doc.add_paragraph(f"出版典籍：{colophon_dict.get('title', title)}")
            doc.add_paragraph(f"责任作者：{colophon_dict.get('author', author)}")
            doc.add_paragraph(f"出版机构：{colophon_dict.get('publisher', publisher)}")
            doc.add_paragraph("技术驱动：Illacme Plenipes Sovereign Digital Bindery Hub")
            doc.add_paragraph(f"版权规范：{colophon_dict.get('license', 'All Rights Reserved')}")

            doc.save(output_file_path)
            tlog.info(f"✨ [Word 装订] 已成功导出审校印本: {os.path.basename(output_file_path)}")
            return True

        except Exception as e:
            tlog.error(f"❌ [Word 装订] 异常中断: {e}")
            return False

    def _render_markdown_to_docx(self, doc: Any, markdown_text: str):
        """将 Markdown 语法解析并映射为 Word 段落、原生层级与可编辑数学公式"""
        lines = markdown_text.splitlines()
        in_code_block, in_math_block = False, False
        code_lines: List[str] = []
        math_lines: List[str] = []

        for line in lines:
            stripped = line.strip()

            # 1. 多行代码块处理
            if stripped.startswith("```"):
                if in_code_block:
                    in_code_block = False
                    p_code = doc.add_paragraph("\n".join(code_lines))
                    p_code.paragraph_format.left_indent = 180000  # EMU
                    for r in p_code.runs: r.font.name = 'Courier New'
                    code_lines.clear()
                else:
                    in_code_block = True
                    code_lines.clear()
                continue
            if in_code_block:
                code_lines.append(line)
                continue

            # 2. 块级独立数学公式处理 ($$...$$)
            if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 2:
                formula = stripped[2:-2].strip()
                self._add_block_formula(doc, formula)
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
                continue
            if in_math_block:
                if stripped.endswith("$$"):
                    in_math_block = False
                    math_lines.append(stripped[:-2])
                    self._add_block_formula(doc, "\n".join(math_lines).strip())
                    math_lines.clear()
                else:
                    math_lines.append(line)
                continue

            if not stripped:
                continue

            # 3. 标题映射
            m_h = re.match(r'^(#{1,6})\s+(.*)$', stripped)
            if m_h:
                level = min(4, len(m_h.group(1)) + 1)
                doc.add_heading(m_h.group(2).strip(), level=level)
                continue

            # 4. 引用块 Callout 映射
            if stripped.startswith(">"):
                quote_text = re.sub(r'^>\s*(\[!.*\])?\s*', '', stripped).strip()
                p_quote = doc.add_paragraph()
                p_quote.paragraph_format.left_indent = 180000  # 约 14.1 pt
                self._append_runs_with_math(p_quote, quote_text, is_italic=True)
                continue

            # 5. 列表项映射
            if stripped.startswith(("- ", "* ", "+ ")):
                p_item = doc.add_paragraph(style='List Bullet' if 'List Bullet' in doc.styles else None)
                self._append_runs_with_math(p_item, stripped[2:].strip())
                continue

            m_num = re.match(r'^\d+\.\s+(.*)$', stripped)
            if m_num:
                p_item = doc.add_paragraph(style='List Number' if 'List Number' in doc.styles else None)
                self._append_runs_with_math(p_item, m_num.group(1).strip())
                continue

            # 6. 普通段落（支持行内 LaTeX 数学公式原生转译）
            p_para = doc.add_paragraph()
            self._append_runs_with_math(p_para, stripped)

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
        """将文本按行内公式切分，普通文本加 Run，公式转译为 OMML 嵌入"""
        if '$' not in text:
            clean = re.sub(r'[*_`]', '', text)
            if clean:
                r = p.add_run(clean)
                if is_italic: r.font.italic = True
            return

        from core.bindery.math_packager import MathPackager
        parts = re.split(r'((?<![\w\\\$])\$(?!\s|\d)[^\$\n]+?(?<!\s)\$(?![\w\$]))', text)
        for part in parts:
            if not part: continue
            if part.startswith("$") and part.endswith("$") and len(part) > 2 and not re.match(r'^\$\s*[\d,]+(?:\.\d+)?\s*\$$', part):
                latex = part[1:-1].strip()
                omml = MathPackager.latex_to_omml(latex, display="inline")
                if omml:
                    try:
                        from docx.oxml import parse_xml
                        p._p.append(parse_xml(omml))
                        continue
                    except Exception: pass
                r = p.add_run(part)
                if is_italic: r.font.italic = True
            else:
                clean = re.sub(r'[*_`]', '', part)
                if clean:
                    r = p.add_run(clean)
                    if is_italic: r.font.italic = True

