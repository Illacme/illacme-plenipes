# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Print-Ready PDF Running Footer & Folio Stamp Engine
模块职责：为固定版式 PDF 注入出版级居中微光页码（Folio）与运行页脚。
规范：
  - 封面页（Cover）：100% 纯净，严禁任何页眉页脚；
  - 前置目录索引（TOC）：小写罗马数字（i, ii）；
  - 章节正文（Body）：居中精致短横线页码（- 1 -, - 2 -...），字号 8.5pt，颜色 #94a3b8；
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
from typing import List, Tuple, Optional, Any, Dict
from core.utils.tracing import tlog


class PDFFolioStamp:
    """📄 印刷级 PDF 矢量页脚与微光页码印章驱动"""

    FONT_NAME = "helv"
    FONT_SIZE = 8.5
    COLOR_MUTED = (0.58, 0.64, 0.72)  # #94a3b8
    BOTTOM_OFFSET_PT = 36.0  # 距离页面底边约 12.7mm，完美居于 24-28mm 下留白中央安全区

    ROMAN_NUMERALS = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]

    @staticmethod
    def _get_fitz():
        """自适应加载 PyMuPDF 核心模块 (优先官方标准 pymupdf 杜绝废弃警告，兼容旧版 fitz)"""
        try:
            import pymupdf as fitz
            return fitz
        except ImportError:
            try:
                import fitz
                return fitz
            except ImportError:
                return None

    @classmethod
    def stamp_folios(cls, pdf_path: str, has_cover: bool = True) -> bool:
        """为已生成的 PDF 注入出版级标准矢量物理页码"""
        if not pdf_path or not os.path.exists(pdf_path):
            return False

        fitz = cls._get_fitz()
        if not fitz:
            tlog.warning("⚠️ [PDF 页码] 环境未安装 PyMuPDF (fitz)，跳过矢量页码注入。")
            return False

        try:
            doc = fitz.open(pdf_path)
            if len(doc) <= 1 and has_cover:
                doc.close()
                return True

            plan = cls._classify_pages(doc, has_cover=has_cover)

            for idx, p_type, folio_text in plan:
                if not folio_text:
                    continue

                page = doc[idx]
                w, h = page.rect.width, page.rect.height
                text_len = fitz.get_text_length(folio_text, fontname=cls.FONT_NAME, fontsize=cls.FONT_SIZE)
                x = (w - text_len) / 2.0
                y = h - cls.BOTTOM_OFFSET_PT

                page.insert_text(
                    (x, y),
                    folio_text,
                    fontname=cls.FONT_NAME,
                    fontsize=cls.FONT_SIZE,
                    color=cls.COLOR_MUTED
                )

            # 增量安全重写
            tmp_out = f"{pdf_path}.tmp_folio.pdf"
            doc.save(tmp_out, deflate=True)
            doc.close()

            if os.path.exists(tmp_out) and os.path.getsize(tmp_out) > 200:
                os.replace(tmp_out, pdf_path)
                tlog.info(f"✨ [PDF 页码] 已成功为出版物注入标准微光物理页码: {os.path.basename(pdf_path)}")
                return True
            return False

        except Exception as e:
            tlog.error(f"❌ [PDF 页码] 注入页码异常中断: {e}")
            return False

    @classmethod
    def detect_chapter_pages(
        cls,
        pdf_path: str,
        chapter_count: int,
        has_cover: bool = True,
        chapter_titles: Optional[List[str]] = None
    ) -> Dict[int, int]:
        """探测各章节在物理 PDF 中的正文逻辑起始页码（从 1 开始编号）"""
        if not pdf_path or not os.path.exists(pdf_path) or chapter_count <= 0:
            return {}

        fitz = cls._get_fitz()
        if not fitz:
            return {}

        try:
            doc = fitz.open(pdf_path)
            first_body_idx = None
            for i, page in enumerate(doc):
                txt = page.get_text()
                if ("第 1 章" in txt or "Chapter 1" in txt or "第 01 章" in txt or (chapter_titles and chapter_titles[0] in txt)) and (
                    "CH 1 →" not in txt and "CH 1 &rarr;" not in txt and "TABLE OF CONTENTS" not in txt and "目 录" not in txt
                ):
                    first_body_idx = i
                    break

            if first_body_idx is None:
                first_body_idx = 1 if has_cover else 0

            page_map = {}
            last_found_page = first_body_idx

            for ch_idx in range(chapter_count):
                ch_num = ch_idx + 1
                patterns = [f"第 {ch_num} 章", f"Chapter {ch_num}", f"第 {ch_num:02d} 章", f"CH {ch_num}"]
                if chapter_titles and ch_idx < len(chapter_titles):
                    t_clean = chapter_titles[ch_idx].strip()
                    if t_clean and len(t_clean) >= 2:
                        patterns.append(t_clean)

                found = False
                for pno in range(last_found_page, len(doc)):
                    txt = doc[pno].get_text()
                    if any(p in txt for p in patterns):
                        page_map[ch_idx] = (pno - first_body_idx) + 1
                        last_found_page = pno
                        found = True
                        break

                if not found:
                    prev_p = page_map.get(ch_idx - 1, 1)
                    page_map[ch_idx] = prev_p + 1

            doc.close()
            return page_map
        except Exception as e:
            tlog.warning(f"⚠️ [PDF 页码] 探测章节物理页码异常: {e}")
            return {}

    @classmethod
    def _classify_pages(cls, doc: Any, has_cover: bool = True) -> List[Tuple[int, str, Optional[str]]]:
        """智能探测封面、前置目录与正文物理页并分配标准书号"""
        first_body_idx = None
        for i, page in enumerate(doc):
            txt = page.get_text()
            # 通过章节标识或正文标志精准识别首个章节页面
            if ("第 1 章" in txt or "Chapter 1" in txt or "第 01 章" in txt) and (
                "CH 1 →" not in txt and "CH 1 &rarr;" not in txt and "TABLE OF CONTENTS" not in txt
            ):
                first_body_idx = i
                break

        if first_body_idx is None:
            first_body_idx = 1 if has_cover else 0

        plan = []
        body_counter = 1
        toc_counter = 1

        for i in range(len(doc)):
            if i == 0 and has_cover:
                plan.append((i, "COVER", None))
            elif i < first_body_idx:
                r_num = cls.ROMAN_NUMERALS[toc_counter - 1] if toc_counter <= len(cls.ROMAN_NUMERALS) else str(toc_counter)
                plan.append((i, "TOC", r_num))
                toc_counter += 1
            else:
                plan.append((i, "BODY", f"- {body_counter} -"))
                body_counter += 1

        return plan

