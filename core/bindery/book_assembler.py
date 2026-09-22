# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Book Assembler (全卷文稿合订编排器)
模块职责：从文库中提取结构化章节树，构建多语言全卷版权页与目录，调度装订插件导出电子书。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import yaml
from typing import Dict, Any, List, Optional

from core.adapters.egress.ebook import EBookRegistry
from .cover_generator import CoverGenerator
from .image_packager import ImagePackager
from .math_packager import MathPackager
from .toc_builder import TocBuilder
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

        book_title = custom_title or f"{site_name} · {category or '全集'}"
        if target_lang != "zh": book_title += f" ({target_lang.upper()} Edition)"

        author = custom_author or "Illacme Editorial Team"
        publisher_name = f"{site_name} Global Private Press"
        license_decl = "保留所有权利 · All Rights Reserved (基于 Illacme Plenipes 出版体系规范装订)"
        if self.engine and hasattr(self.engine, "config"):
            license_decl = getattr(self.engine.config, "license", None) or getattr(self.engine.config, "copyright", license_decl)

        book_meta = {
            "title": book_title,
            "author": author,
            "publisher": publisher_name,
            "description": f"由 {site_name} 自动化装订中枢出版的数字出版物。",
            "date": None,
            "language": target_lang,
            "license": license_decl
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
                cover_path = CoverGenerator.discover_cover(vault_dir=self.vault_dir, category=category, chapters=chapters)
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
        parsed_docs = []
        route_map = {}
        for idx, p in enumerate(doc_entries):
            ch_id = f"ch_{idx + 1}"
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                raw_text = fp.read()
            fm, body = self._extract_frontmatter(raw_text)
            title = fm.get("title") or os.path.splitext(os.path.basename(p))[0].replace('-', ' ').title()
            slug = fm.get("slug") or os.path.splitext(os.path.basename(p))[0]
            stem = os.path.splitext(os.path.basename(p))[0]
            rel_p = os.path.relpath(p, target_dir).replace('\\', '/')
            rel_no_ext = os.path.splitext(rel_p)[0]
            parsed_docs.append({"ch_id": ch_id, "title": str(title), "slug": str(slug), "file_path": p, "raw_body": body})
            for key in (stem.lower(), stem, slug.lower(), slug, str(title).lower(), str(title), rel_p.lower(), rel_no_ext.lower()):
                if key and key not in route_map: route_map[key] = ch_id
            for raw_k in (stem, str(title), slug, rel_no_ext):
                norm_k = re.sub(r'[^\w\u4e00-\u9fa5]+', '', str(raw_k)).lower()
                if norm_k and norm_k not in route_map: route_map[norm_k] = ch_id
            parent_dir = os.path.dirname(rel_no_ext).lower()
            if parent_dir and f"{parent_dir}/index" not in route_map:
                route_map[f"{parent_dir}/index"] = ch_id
                route_map[parent_dir] = ch_id

        # 第二阶段：编译内容与重写内链锚点
        import markdown
        from markdown.extensions.toc import slugify_unicode
        md_converter = markdown.Markdown(
            extensions=['extra', 'codehilite', 'tables', 'toc'],
            extension_configs={'toc': {'slugify': slugify_unicode}}
        )

        chapters = []
        for entry in parsed_docs:
            p, body, ch_id = entry["file_path"], entry["raw_body"], entry["ch_id"]
            if target_lang != "zh":
                body = self._try_get_translation(p, target_lang) or body

            # 排版自愈：数学公式转译 -> Obsidian 插图转译 -> 跨章内链锚点重写
            body = MathPackager.heal_latex_formulas(body)
            body = ImagePackager.heal_obsidian_embedded_images(body)
            healed_body = self._rewrite_wikilinks_to_chapters(body, route_map, curr_ch_id=ch_id)
            md_converter.reset()
            html_content = md_converter.convert(healed_body)
            raw_toc_tokens = getattr(md_converter, "toc_tokens", [])
            headings = TocBuilder.extract_heading_tree(raw_toc_tokens, chapter_title=entry["title"])
            html_content = self._heal_html_hrefs(html_content, route_map, curr_ch_id=ch_id)
            html_content, assets = ImagePackager.extract_and_heal_images(html_content, p, self.vault_dir)

            # Callout 优化：将 > [!TIP] 结构美化为标准的 callout 块
            html_content = re.sub(
                r'<blockquote>\s*<p>\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][+-]?\s*(.*?)(</p>.*?)</blockquote>',
                r'<div class="callout callout-\1"><div class="callout-title">💡 \1</div><p>\2\3</div>',
                html_content,
                flags=re.DOTALL | re.IGNORECASE
            )

            chapters.append({
                "order": int(ch_id.split('_')[1]),
                "title": entry["title"],
                "slug": entry["slug"],
                "html_body": html_content,
                "file_path": p,
                "assets": assets,
                "headings": headings
            })

        return chapters

    @staticmethod
    def _heal_html_hrefs(html: str, route_map: Dict[str, str], curr_ch_id: str = "") -> str:
        """统一自愈 HTML 中的原生 <a> 超链接与静态站点相对路径 (如 ./docs/quick-start.html)"""
        def repl(m):
            tag, href = m.group(0), m.group(1).strip()
            if not href or href.startswith(('http://', 'https://', 'mailto:', 'tel:', 'data:', 'javascript:', '#')):
                return tag
            path_part, anchor = href.split('#', 1) if '#' in href else (href, "")
            clean_path = path_part.replace('\\', '/').lstrip('./').rstrip('/')
            norm_rel, stem = os.path.splitext(clean_path)[0], os.path.splitext(os.path.basename(clean_path))[0]
            target_ch = route_map.get(norm_rel.lower()) or route_map.get(norm_rel) or route_map.get(stem.lower()) or route_map.get(stem)
            if not target_ch and stem:
                norm_stem = re.sub(r'[^\w\u4e00-\u9fa5]+', '', stem).lower()
                target_ch = route_map.get(norm_stem)
                if not target_ch:
                    for k, v in route_map.items():
                        if norm_stem and (norm_stem in k or k in norm_stem):
                            target_ch = v
                            break
            if target_ch:
                new_href = f"#{anchor}" if (target_ch == curr_ch_id and anchor) else f"{target_ch}.xhtml#{anchor or target_ch}"
                return tag.replace(f'href="{href}"', f'href="{new_href}"').replace(f"href='{href}'", f"href='{new_href}'")
            return tag

        return re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>', repl, html)

    @staticmethod
    def _rewrite_wikilinks_to_chapters(body: str, route_map: Dict[str, str], curr_ch_id: str = "") -> str:
        """将 Markdown 中的 [[target#anchor|alias]] 双链转换为电子书相对跳转锚点"""
        from markdown.extensions.toc import slugify_unicode
        def repl(match):
            raw_target = match.group(1).strip()
            alias = (match.group(2) or "").strip()
            doc_part, anchor_part = raw_target.split('#', 1) if '#' in raw_target else (raw_target, "")
            doc_part, anchor_part = doc_part.strip(), anchor_part.strip()
            anchor_slug = slugify_unicode(anchor_part, '-') if anchor_part else ""

            # 1. 本章内部锚点跳转：[[#小节标题]] 或 [[#小节标题|别名]]
            if not doc_part:
                return f"[{alias or anchor_part}](#{anchor_slug})" if anchor_slug else (alias or raw_target)

            # 2. 查找跨章节目标（支持精确匹配与归一化模糊容错）
            clean_doc = re.sub(r'[^\w\u4e00-\u9fa5]+', '', os.path.splitext(os.path.basename(doc_part))[0]).lower()
            target_ch = route_map.get(doc_part) or route_map.get(doc_part.lower()) or route_map.get(clean_doc)
            if not target_ch and clean_doc:
                for k, v in route_map.items():
                    if clean_doc in k or k in clean_doc:
                        target_ch = v
                        break

            if target_ch:
                if target_ch == curr_ch_id and anchor_slug:
                    target_url = f"#{anchor_slug}"
                else:
                    # 关键：即使未带特定小节，也附加 #{target_ch} 确保 Apple Books 等阅读器能够触发翻章与定位
                    target_url = f"{target_ch}.xhtml#{anchor_slug or target_ch}"
                display = alias or (f"{doc_part} · {anchor_part}" if anchor_part else doc_part)
                return f"[{display}]({target_url})"

            # 3. 外部未导出文档降级为纯文本，杜绝 404 死链
            return alias or raw_target

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


