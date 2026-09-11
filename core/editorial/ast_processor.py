#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Editorial AST Processor (文稿格式与资产门面处理器)
职责：对文稿进行分发前格式规约，处理相对路径资产上云、整页外壳清洗与全渠道排版降级。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import os
import re
from typing import Callable, Dict, Any, Optional
from core.utils.tracing import tlog
from .ast_shards import HtmlSanitizer, GfmNormalizer, MetadataSanitizer, LandingPageTransformer

class MarkdownASTProcessor:
    def __init__(self):
        # 匹配本地相对路径图片 ![alt](path)
        self.img_pattern = re.compile(r'!\[(.*?)\]\(((?!https?://)(.*?))\)')
        # 匹配 HTML img src="path" 相对路径图片
        self.html_img_pattern = re.compile(r'<img[^>]+src=["\']((?!https?://)([^"\']+))["\']')
        # 匹配 Obsidian 嵌入式图片语法 ![[image.png]] 或 ![[assets/pic.png|300]]
        self.wiki_img_pattern = re.compile(r'!\[\[((?!https?://)([^\]|]+?))(?:\s*\|\s*([^\]]*))?\]\]')

    def _locate_image(self, doc_dir: str, clean_path: str) -> Optional[str]:
        """多级鲁棒寻址：在当前目录、文库根目录与全局资产目录中查找物理图片"""
        stripped = clean_path.lstrip('/')
        candidates = [
            os.path.normpath(os.path.join(doc_dir, clean_path)),
            os.path.normpath(os.path.join(doc_dir, stripped)),
            os.path.normpath(os.path.join(doc_dir, "assets", os.path.basename(clean_path)))
        ]
        # 向上寻找文库根目录 (含有 .obsidian 或名为 vault)
        cur = os.path.abspath(doc_dir)
        vault_root = None
        while cur and cur != os.path.dirname(cur):
            if os.path.exists(os.path.join(cur, ".obsidian")) or os.path.basename(cur).lower() == "vault":
                vault_root = cur
                break
            cur = os.path.dirname(cur)

        if vault_root:
            candidates.extend([
                os.path.normpath(os.path.join(vault_root, stripped)),
                os.path.normpath(os.path.join(vault_root, "assets", os.path.basename(clean_path))),
                os.path.normpath(os.path.join(vault_root, "static", os.path.basename(clean_path)))
            ])

        for c in candidates:
            if os.path.isfile(c):
                return c
        return None

    def process_images(self, content: str, doc_dir: str, upload_fn: Callable[[str], str]) -> str:
        """
        提取正文中的相对路径图片与 Obsidian 嵌入图片，物理寻址后调用 upload_fn 回调上传并原地替换链接。
        """
        if not content:
            return content

        # 1. 处理标准 Markdown 图片语法 ![alt](rel_path)
        def replace_img(match):
            alt_text = match.group(1)
            rel_path = match.group(2).strip()
            clean_path = rel_path.split('?')[0]
            abs_path = self._locate_image(doc_dir, clean_path)
            if abs_path:
                try:
                    public_url = upload_fn(abs_path)
                    if public_url:
                        query = rel_path.split('?')[1] if '?' in rel_path else ''
                        final_url = f"{public_url}?{query}" if query else public_url
                        return f"![{alt_text}]({final_url})"
                except Exception:
                    pass
            return match.group(0)

        content = self.img_pattern.sub(replace_img, content)

        # 2. 处理 HTML 格式 <img> 标签
        def replace_html_img(match):
            full_tag = match.group(0)
            rel_path = match.group(1).strip()
            clean_path = rel_path.split('?')[0]
            abs_path = self._locate_image(doc_dir, clean_path)
            if abs_path:
                try:
                    public_url = upload_fn(abs_path)
                    if public_url:
                        query = rel_path.split('?')[1] if '?' in rel_path else ''
                        final_url = f"{public_url}?{query}" if query else public_url
                        return full_tag.replace(rel_path, final_url)
                except Exception:
                    pass
            return full_tag

        content = self.html_img_pattern.sub(replace_html_img, content)

        # 3. 🚀 [V114.0] 处理 Obsidian Wiki 嵌入图片语法 ![[image.png]]
        def replace_wiki_img(match):
            full_tag = match.group(0)
            rel_path = match.group(1).strip()
            caption = match.group(3) or os.path.basename(rel_path)
            clean_path = rel_path.split('?')[0]
            abs_path = self._locate_image(doc_dir, clean_path)
            if abs_path:
                try:
                    public_url = upload_fn(abs_path)
                    if public_url:
                        query = rel_path.split('?')[1] if '?' in rel_path else ''
                        final_url = f"{public_url}?{query}" if query else public_url
                        return f"![{caption.strip()}]({final_url})"
                except Exception:
                    pass
            return full_tag

        content = self.wiki_img_pattern.sub(replace_wiki_img, content)
        return content

    def adapt_format(
        self,
        content: str,
        target_platform: str,
        site_url: str = "",
        slug: str = "",
        fm: Dict[str, Any] = None
    ) -> str:
        """
        多平台版式深度规范化：
        1. 针对整页 HTML 产物执行全页外壳剥离 (剔除 DOCTYPE, script, style, header, nav)；
        2. 针对首页 (Landing Page) 执行营销组件 GFM 通告化转换；
        3. 补全相对超链接为官方站点 Canonical 绝对 URL (消除 404，提升 SEO)；
        4. 针对特定发布平台 (如 Medium 标题降级) 执行方言自适应。
        """
        if not content:
            return content

        platform = (target_platform or "").lower()

        # 1. 🚀 [外壳剥离] 侦测到整页网页骨架时，实时剥离
        if HtmlSanitizer.is_full_html_page(content):
            stripped_body, stripped_lines = HtmlSanitizer.strip_html_boilerplate(content)
            if stripped_lines > 0:
                tlog.info(f"🧹 [AST 语义净化] 侦测到整页网页外壳，已自动剔除脚本与全站导航 ({stripped_lines} 行)")
            content = stripped_body

        # 2. 🚀 [首页通告化] 针对首页布局执行结构化 GFM 转换
        if LandingPageTransformer.is_landing_page(slug, fm):
            title = (fm or {}).get("title", "")
            content = LandingPageTransformer.transform_hero_components(content, title=title, site_url=site_url)

        # 3. 🚀 [HTML 语义转换] 将零散 HTML 标签规范化为 GFM (保留 details/summary 等合法标签)
        content = GfmNormalizer.html_to_clean_markdown(content)

        # 4. 🚀 [外链绝对化] 补全超链接为官方 Canonical 绝对路径
        if site_url:
            content, link_count = GfmNormalizer.absolutize_links(content, site_url=site_url)
            if link_count > 0:
                tlog.info(f"🔗 [外链对正] 成功将 {link_count} 个相对链接对齐为官方站点 Canonical 绝对路径")

        # 5. 🚀 [平台定制方言]
        if "medium" in platform:
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith('# '):
                    line = '### ' + line[2:]
                elif line.startswith('## '):
                    line = '### ' + line[3:]
                new_lines.append(line)
            content = '\n'.join(new_lines)

        return content

    def sanitize_metadata(
        self,
        metadata: Dict[str, Any],
        target_platform: str,
        site_url: str = "",
        slug: str = "",
        doc_id: str = "",
        lang_code: str = ""
    ) -> Dict[str, Any]:
        """
        清洗并规范化社媒元数据：
        - 标签合规化 (去特殊符号，截断)
        - 封面图绝对化与公网验证 (防 422 报错)
        - 注入 Canonical URL 原创物权声明
        """
        clean_fm = dict(metadata) if metadata else {}

        # 1. 规范化标签
        raw_tags = clean_fm.get("tags") or clean_fm.get("keywords") or []
        clean_tags = MetadataSanitizer.sanitize_tags(raw_tags, max_tags=4, target_platform=target_platform)
        clean_fm["tags"] = clean_tags

        # 2. 规范化封面图
        cover = MetadataSanitizer.resolve_cover_image(clean_fm, site_url=site_url)
        if cover:
            clean_fm["main_image"] = cover
            clean_fm["cover_image"] = cover
        elif "main_image" in clean_fm:
            clean_fm.pop("main_image", None)

        # 3. 注入 Canonical URL 原创声明
        canonical = MetadataSanitizer.build_canonical_url(doc_id, slug, lang_code, site_url=site_url)
        if canonical:
            clean_fm["canonical_url"] = canonical
            clean_fm["original_article_url"] = canonical

        return clean_fm
