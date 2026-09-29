# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Full-Text Single Markdown Book Adapter
模块职责：将文库全卷或单篇文稿编排合并为自包含长篇 Markdown 合卷典籍。
适用场景：大模型投喂 (RAG / NotebookLM)、长篇阅读、Obsidian/Notion 归档。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional

from core.adapters.egress.ebook.base import BaseEBookAdapter
from core.adapters.egress.ebook.colophon import ColophonBuilder
from core.utils.tracing import tlog


class MarkdownBundleAdapter(BaseEBookAdapter):
    """📝 长篇 Markdown 合卷驱动（标题层级自适应顺延、TOC 大纲聚合与元数据封包）"""
    PLUGIN_ID = "markdown"
    DISPLAY_NAME = "Markdown 合集"
    OUTPUT_EXTENSION = ".md"
    MIME_TYPE = "text/markdown"
    VERSION = "V1.0"
    DESCRIPTION = "长篇 Markdown 合集：全书标题降级折叠、目录 TOC 聚合、元数据 Frontmatter 封装，专供知识库 RAG 与长文研读。"

    def bind_book(
        self,
        manuscript_tree: List[Dict[str, Any]],
        book_metadata: Dict[str, Any],
        cover_image_path: Optional[str] = None,
        target_lang: str = "zh",
        output_file_path: str = ""
    ) -> bool:
        """执行全书合并编排，编译输出标准自包含 Markdown 实体文件"""
        if not output_file_path:
            tlog.error("❌ [Markdown 合卷] 未指定输出文件路径！")
            return False

        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)
            doc_lines: List[str] = []

            # 1. 组装整书 YAML Frontmatter
            frontmatter_data = self._build_frontmatter(book_metadata, target_lang, len(manuscript_tree))
            doc_lines.append("---")
            doc_lines.append(yaml.dump(frontmatter_data, allow_unicode=True, default_flow_style=False).strip())
            doc_lines.append("---\n")

            # 2. 卷首封面与出版主标题
            title = book_metadata.get("title", "数字出版集")
            author = book_metadata.get("author", "Illacme Editorial Team")
            doc_lines.append(f"# {title}\n")
            doc_lines.append(f"> **著/编**：{author}  ")
            doc_lines.append(f"> **出品品牌**：{book_metadata.get('publisher', 'Illacme Plenipes Press')}  ")
            doc_lines.append(f"> **装订日期**：{datetime.now().strftime('%Y-%m-%d')}  ")
            doc_lines.append(f"> **语种规格**：{target_lang.upper()}  \n")

            if book_metadata.get("description"):
                doc_lines.append(f"*{book_metadata['description']}*\n")
            doc_lines.append("---\n")

            # 3. 构造全书目录大纲 (Table of Contents)
            doc_lines.append("## 📖 目录大纲 (Contents)\n")
            for idx, ch in enumerate(manuscript_tree, 1):
                ch_title = ch.get("title", f"第 {idx} 章")
                anchor = self._slugify(f"ch-{idx}-{ch_title}")
                doc_lines.append(f"- [{idx}. {ch_title}](#{anchor})")
                headings = ch.get("headings", [])
                if isinstance(headings, list):
                    for h in headings:
                        sub_title = h.get("title") or h.get("text", "")
                        if sub_title and sub_title != ch_title:
                            sub_anchor = self._slugify(sub_title)
                            doc_lines.append(f"  - [{sub_title}](#{sub_anchor})")
            doc_lines.append("\n---\n")

            # 4. 正文编排（标题顺延与内嵌排版）
            for idx, ch in enumerate(manuscript_tree, 1):
                ch_title = ch.get("title", f"第 {idx} 章")
                anchor = self._slugify(f"ch-{idx}-{ch_title}")
                doc_lines.append(f'<a id="{anchor}"></a>')
                doc_lines.append(f"## {idx}. {ch_title}\n")

                body = ch.get("raw_body") or ""
                if not body and ch.get("content"):
                    # 备用：从 HTML 转纯文本兜底
                    body = re.sub(r'<[^>]+>', '', ch["content"])

                # 智能降级正文内标题，确保文档拓扑严格遵循 H2 章节 -> H3/H4 小节
                demoted_body = self._demote_headings(body)
                doc_lines.append(demoted_body.strip())
                doc_lines.append("\n\n---\n")

            # 5. 卷尾版权声明 (Colophon)
            colophon_dict = ColophonBuilder.build_colophon_data(
                manuscript_tree=manuscript_tree,
                book_metadata=book_metadata,
                format_name="markdown"
            )
            doc_lines.append("## 📜 版权声明 (Colophon)\n")
            doc_lines.append(f"- **出版典籍**：{colophon_dict.get('title', title)}")
            doc_lines.append(f"- **责任作者**：{colophon_dict.get('author', author)}")
            doc_lines.append(f"- **出版机构**：{colophon_dict.get('publisher', '')}")
            doc_lines.append("- **技术引擎**：Illacme Plenipes Sovereign Digital Bindery Hub")
            doc_lines.append(f"- **版权规范**：{colophon_dict.get('license', 'All Rights Reserved')}\n")

            full_content = "\n".join(doc_lines)
            with open(output_file_path, "w", encoding="utf-8") as fp:
                fp.write(full_content)

            tlog.info(f"✨ [Markdown 合卷] 已成功导出合卷典籍: {os.path.basename(output_file_path)} ({len(full_content)} chars)")
            return True

        except Exception as e:
            tlog.error(f"❌ [Markdown 合卷] 装订中断: {e}")
            return False

    def _build_frontmatter(self, meta: Dict[str, Any], lang: str, chapter_count: int) -> Dict[str, Any]:
        """构建整卷 YAML Frontmatter 字典"""
        return {
            "title": meta.get("title", "数字出版集"),
            "author": meta.get("author", "Illacme Editorial Team"),
            "publisher": meta.get("publisher", "Illacme Plenipes Global Press"),
            "language": lang,
            "chapters_count": chapter_count,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "generator": "Illacme Plenipes Digital Bindery Hub",
            "format": "Markdown Bundle (.md)"
        }

    def _demote_headings(self, markdown_text: str) -> str:
        """
        正文标题层级智能顺延降级：
        章节作为二级标题 (##)，正文原本的一级 (# ) 顺延为三级 (### )，二级 (## ) 顺延为四级 (#### )。
        必须避开代码块 (```) 中的注释行以防误伤。
        """
        lines = markdown_text.splitlines()
        demoted = []
        in_code_block = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                demoted.append(line)
                continue

            if not in_code_block:
                m = re.match(r'^(#{1,5})\s+(.*)$', line)
                if m:
                    current_hashes, heading_text = m.group(1), m.group(2)
                    # 统一后移 2 级 (H1 -> H3, H2 -> H4, 最大限制为 H6)
                    new_level = min(6, len(current_hashes) + 2)
                    demoted.append(f"{'#' * new_level} {heading_text}")
                    continue

            demoted.append(line)

        return "\n".join(demoted)

    def _slugify(self, text: str) -> str:
        """生成 Markdown 合规锚点 ID"""
        s = re.sub(r'[^\w\u4e00-\u9fa5\-]+', '-', str(text).lower()).strip('-')
        return s or "section"
