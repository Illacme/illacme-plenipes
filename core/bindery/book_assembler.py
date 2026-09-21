# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Book Assembler (全卷文稿合订编排器)
模块职责：从文库中提取结构化章节树，构建多语言全卷版权页与目录，调度装订插件导出电子书。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import yaml
import markdown
from typing import Dict, Any, List, Optional

from core.adapters.egress.ebook import EBookRegistry
from .cover_generator import CoverGenerator
from core.utils.tracing import tlog


class BookAssembler:
    """📚 数字出版物全卷合订编排器"""

    def __init__(self, engine: Any = None, vault_dir: str = "vault"):
        self.engine = engine
        self.vault_dir = vault_dir

    def assemble_and_bind(
        self,
        category: str = "Docs",
        format_type: str = "epub",
        target_lang: str = "zh",
        custom_title: Optional[str] = None,
        custom_author: Optional[str] = None,
        cover_mode: str = "auto",
        cover_style: str = "dark_emerald",
        output_dir: str = "dist/books"
    ) -> Optional[str]:
        """执行装订全流程：收集章节、渲染转换、装订封包"""
        adapter_cls = EBookRegistry.get_adapter(format_type)
        if not adapter_cls:
            tlog.error(f"❌ [数字装订] 未找到格式驱动: {format_type}")
            return None

        # 1. 勘测提取章节
        chapters = self._collect_chapters(category, target_lang)
        if not chapters:
            tlog.warning(f"⚠️ [数字装订] 栏目 '{category}' 下无可用 Markdown 章节稿件。")
            return None

        # 2. 组装出版元数据
        site_name = "Illacme Plenipes"
        if self.engine and hasattr(self.engine, "config"):
            site_name = getattr(self.engine.config, "site_name", site_name)

        cat_label = category if category else "全集"
        book_title = custom_title or f"{site_name} · {cat_label}"
        if target_lang != "zh":
            book_title += f" ({target_lang.upper()} Edition)"

        author = custom_author or "Illacme Editorial Team"
        publisher_name = f"{site_name} Global Private Press"
        book_meta = {
            "title": book_title,
            "author": author,
            "publisher": publisher_name,
            "description": f"由 {site_name} 自动化装订中枢出版的数字出版物。",
            "date": None,
            "language": target_lang
        }

        # 3. 确定输出路径与封面解析
        slug_prefix = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fa5]+', '-', book_title).strip('-').lower()
        ext = getattr(adapter_cls, "OUTPUT_EXTENSION", ".epub")
        os.makedirs(output_dir, exist_ok=True)
        out_filename = f"{slug_prefix}_{target_lang}{ext}"
        out_path = os.path.abspath(os.path.join(output_dir, out_filename))

        cover_path = None
        if cover_mode != "none":
            if cover_mode == "auto":
                cover_path = CoverGenerator.discover_cover(
                    vault_dir=self.vault_dir,
                    category=category,
                    chapters=chapters
                )
            # 若 auto 未找到，或显式指定 generated，则自动派生高雅排版艺术封面
            if not cover_path and cover_mode in ("auto", "generated"):
                gen_cover_name = f"cover_{slug_prefix}_{cover_style}.png"
                gen_cover_path = os.path.join(output_dir, gen_cover_name)
                cover_path = CoverGenerator.render_cover_image(
                    output_path=gen_cover_path,
                    title=book_title,
                    author=author,
                    publisher=publisher_name,
                    style_key=cover_style,
                    lang=target_lang
                )

        # 4. 调用适配驱动执行装订封包
        adapter = adapter_cls(engine=self.engine)
        success = adapter.bind_book(
            manuscript_tree=chapters,
            book_metadata=book_meta,
            cover_image_path=cover_path,
            target_lang=target_lang,
            output_file_path=out_path
        )

        return out_path if success else None

    def _collect_chapters(self, category: str, target_lang: str) -> List[Dict[str, Any]]:
        """遍历文库提取按文件名与元数据排序的章节列表"""
        target_dir = os.path.join(self.vault_dir, category) if category else self.vault_dir
        if not os.path.exists(target_dir):
            return []

        # 建立 slug 到章节索引的映射表，便于双链内链重写
        doc_entries = []
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in sorted(files):
                if f.endswith('.md') and not f.startswith('.'):
                    full_p = os.path.join(root, f)
                    doc_entries.append(full_p)

        # 排序：优先 index.md / quick-start.md，其余字母排序
        def sort_key(p):
            fn = os.path.basename(p).lower()
            if fn in ('index.md', 'readme.md'): return '00_index'
            if 'quick-start' in fn or 'start' in fn: return '01_start'
            return fn

        doc_entries.sort(key=sort_key)

        chapters = []
        # 第一阶段：解析所有文件，预建映射
        slug_to_id = {}
        for idx, p in enumerate(doc_entries):
            ch_id = f"ch_{idx + 1}"
            slug = os.path.splitext(os.path.basename(p))[0].lower()
            slug_to_id[slug] = ch_id

        # 第二阶段：编译内容与重写内链
        md_converter = markdown.Markdown(extensions=['extra', 'codehilite', 'tables', 'toc'])

        for idx, p in enumerate(doc_entries):
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                raw_text = fp.read()

            fm, body = self._extract_frontmatter(raw_text)
            title = fm.get("title") or os.path.splitext(os.path.basename(p))[0].replace('-', ' ').title()
            slug = fm.get("slug") or os.path.splitext(os.path.basename(p))[0]

            # 跨语言处理：如果是非中文，尝试获取译文
            if target_lang != "zh":
                body = self._try_get_translation(p, target_lang) or body

            # 链接自愈：将 Obsidian 双链 [[target|alias]] 重写为电子书相对跳转 <a href="ch_xxx.xhtml">alias</a>
            healed_body = self._rewrite_wikilinks_to_chapters(body, slug_to_id)

            md_converter.reset()
            html_content = md_converter.convert(healed_body)

            chapters.append({
                "order": idx + 1,
                "title": str(title),
                "slug": str(slug),
                "html_body": html_content,
                "file_path": p
            })

        return chapters

    def _rewrite_wikilinks_to_chapters(self, body: str, slug_to_id: Dict[str, str]) -> str:
        """将 Markdown 中的 [[target|alias]] 双链转换为电子书内部相对链接"""
        def repl(match):
            target = match.group(1).strip().lower()
            alias = (match.group(2) or match.group(1)).strip()
            target_slug = os.path.splitext(os.path.basename(target))[0]
            if target_slug in slug_to_id:
                target_file = f"{slug_to_id[target_slug]}.xhtml"
                return f"[{alias}]({target_file})"
            return alias

        return re.sub(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', repl, body)

    def _extract_frontmatter(self, text: str):
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', text, re.DOTALL)
        if m:
            try:
                fm = yaml.safe_load(m.group(1)) or {}
                return fm, m.group(2)
            except Exception:
                pass
        return {}, text

    def _try_get_translation(self, file_path: str, lang: str) -> Optional[str]:
        """从 SQLite 账本或缓存提取已翻译正文"""
        try:
            import sqlite3
            import json
            db_path = os.path.join(self.vault_dir, ".plenipes/cache/ledger.db")
            if not os.path.exists(db_path): return None
            rel_p = os.path.relpath(file_path, self.vault_dir).replace('\\', '/')
            with sqlite3.connect(db_path) as conn:
                row = conn.execute(
                    "SELECT result_json FROM translations WHERE rel_path = ? AND lang_code = ? AND status = 'DONE'",
                    (rel_p, lang)
                ).fetchone()
                if row and row[0]:
                    data = json.loads(row[0])
                    return data.get("translated_content") or data.get("content")
        except Exception:
            pass
        return None


