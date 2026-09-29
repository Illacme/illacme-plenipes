# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Plain Text (.txt) Book Adapter
模块职责：将文库全卷或单篇文稿编排导出为出版规范、结构清晰的纯文本便携书 (.txt)。
适用场景：古董墨水屏阅读器、Kindle 纯文本模式、掌上设备、终端 Pager 与低资源离线阅读。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from core.adapters.egress.ebook.base import BaseEBookAdapter
from core.adapters.egress.ebook.colophon import ColophonBuilder
from core.utils.tracing import tlog


class TxtBookAdapter(BaseEBookAdapter):
    """📜 纯文本便携书驱动（UTF-8 编码、ASCII 出版框线、目录大纲与出版版记）"""
    PLUGIN_ID = "txt"
    DISPLAY_NAME = "TXT 便携书"
    OUTPUT_EXTENSION = ".txt"
    MIME_TYPE = "text/plain; charset=utf-8"
    VERSION = "V1.0"
    DESCRIPTION = "纯文本便携出版物：UTF-8 编码，包含目录大纲、章节标线与版记，适于墨水屏、阅读器与终端离线翻阅。"

    LINE_WIDTH = 76

    def bind_book(
        self,
        manuscript_tree: List[Dict[str, Any]],
        book_metadata: Dict[str, Any],
        cover_image_path: Optional[str] = None,
        target_lang: str = "zh",
        output_file_path: str = ""
    ) -> bool:
        """执行纯文本排版编译，生成标准 .txt 实体文件"""
        if not output_file_path:
            tlog.error("❌ [TXT 装订] 未指定输出文件路径！")
            return False

        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)

            title = book_metadata.get("title", "数字出版集")
            author = book_metadata.get("author", "Illacme Editorial Team")
            publisher = book_metadata.get("publisher", "Illacme Plenipes Global Press")
            desc = book_metadata.get("description", "")

            sections: List[str] = []

            # 1. 卷首扉页 (Cover Page)
            sections.append(self._build_cover_banner(title, author, publisher, desc, target_lang))

            # 2. 目录大纲 (Table of Contents)
            sections.append(self._build_toc(manuscript_tree))

            # 3. 逐章编排正文
            for idx, ch in enumerate(manuscript_tree, 1):
                ch_title = ch.get("title", f"第 {idx} 章")
                raw_body = ch.get("raw_body") or ""
                if not raw_body and ch.get("content"):
                    raw_body = re.sub(r'<[^>]+>', '', ch["content"])

                ch_text = self._format_chapter(idx, ch_title, raw_body)
                sections.append(ch_text)

            # 4. 卷尾版权声明页 (Colophon)
            colophon_dict = ColophonBuilder.build_colophon_data(
                manuscript_tree=manuscript_tree,
                book_metadata=book_metadata,
                format_name="txt"
            )
            sections.append(self._build_colophon(colophon_dict))

            full_content = "\n\n".join(sections) + "\n"
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(full_content)

            tlog.info(f"✨ [TXT 装订] 已成功导出纯文本便携书: {os.path.basename(output_file_path)}")
            return True

        except Exception as e:
            tlog.error(f"❌ [TXT 装订] 异常中断: {e}")
            return False

    def _build_cover_banner(self, title: str, author: str, publisher: str, desc: str, lang: str) -> str:
        sep = "=" * self.LINE_WIDTH
        sub_sep = "-" * self.LINE_WIDTH
        date_str = datetime.now().strftime("%Y-%m-%d")
        lines = [
            sep,
            f"《 {title} 》",
            sub_sep,
            f"著 / 编  ：{author}",
            f"出  品   ：{publisher}",
            f"装订日期 ：{date_str}   规格：{lang.upper()}",
        ]
        if desc:
            lines.extend([sub_sep, f"卷首题记 ：{desc}"])
        lines.append(sep)
        return "\n".join(lines)

    def _build_toc(self, manuscript_tree: List[Dict[str, Any]]) -> str:
        sep = "=" * self.LINE_WIDTH
        sub_sep = "-" * self.LINE_WIDTH
        lines = [
            "【 目 录 大 纲 】",
            sub_sep
        ]
        for idx, ch in enumerate(manuscript_tree, 1):
            ch_title = ch.get("title", f"第 {idx} 章")
            lines.append(f"  {idx:02d}. {ch_title}")
            headings = ch.get("headings", [])
            if isinstance(headings, list):
                for h in headings:
                    sub_t = h.get("title") or h.get("text", "")
                    if sub_t and sub_t != ch_title:
                        lines.append(f"       · {sub_t}")
        lines.append(sep)
        return "\n".join(lines)

    def _format_chapter(self, idx: int, title: str, raw_markdown: str) -> str:
        sep = "=" * self.LINE_WIDTH
        header = f"\n{sep}\n第 {idx:02d} 章  {title}\n{sep}\n"
        cleaned_body = self._clean_markdown_to_plain_text(raw_markdown)
        return f"{header}\n{cleaned_body}"

    def _clean_markdown_to_plain_text(self, markdown_text: str) -> str:
        """将 Markdown 转换为清晰纯正的离线纯文本"""
        lines = markdown_text.splitlines()
        result_lines: List[str] = []
        in_code_block = False

        for line in lines:
            stripped = line.strip()

            # 代码块
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                marker = "--- [代码开始] ---" if in_code_block else "--- [代码结束] ---"
                result_lines.append(marker)
                continue

            if in_code_block:
                result_lines.append(f"    {line}")
                continue

            if not stripped:
                result_lines.append("")
                continue

            # 标题映射
            m_h = re.match(r'^(#{1,6})\s+(.*)$', stripped)
            if m_h:
                lvl = len(m_h.group(1))
                h_text = m_h.group(2).strip()
                prefix = "■ " if lvl <= 2 else "  ▲ "
                result_lines.append(f"\n{prefix}{h_text}\n")
                continue

            # 引用块 Callout
            if stripped.startswith(">"):
                quote_text = re.sub(r'^>\s*(\[!.*\])?\s*', '', stripped).strip()
                result_lines.append(f"    | {quote_text}")
                continue

            # 列表项
            if stripped.startswith(("- ", "* ", "+ ")):
                result_lines.append(f"  • {stripped[2:].strip()}")
                continue

            m_num = re.match(r'^(\d+\.)\s+(.*)$', stripped)
            if m_num:
                result_lines.append(f"  {m_num.group(1)} {m_num.group(2).strip()}")
                continue

            # 去除 Markdown 格式符
            cleaned = re.sub(r'[*_`]', '', stripped)
            result_lines.append(cleaned)

        return "\n".join(result_lines)

    def _build_colophon(self, colophon_dict: Dict[str, Any]) -> str:
        sep = "=" * self.LINE_WIDTH
        sub_sep = "-" * self.LINE_WIDTH
        lines = [
            sep,
            "【 出 版 版 记 (Colophon) 】",
            sub_sep,
            f"典籍名称 ：{colophon_dict.get('title', '数字出版物')}",
            f"责任作者 ：{colophon_dict.get('author', 'Illacme Editorial Team')}",
            f"出版机构 ：{colophon_dict.get('publisher', 'Illacme Plenipes Global Press')}",
            "技术驱动 ：Illacme Plenipes Sovereign Digital Bindery Hub",
            f"版权规范 ：{colophon_dict.get('license', 'All Rights Reserved')}",
            sep
        ]
        return "\n".join(lines)
