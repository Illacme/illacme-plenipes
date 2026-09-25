# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Parser Helpers
模块职责：提供 EPUB 解包流式解析、相对图片 Base64 嵌入、章节内链重写及多级目录树构建。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import base64
import mimetypes
import zipfile
from typing import Dict


def extract_body_html(xhtml_content: str) -> str:
    """提取 XHTML 中的 body 内部 HTML 节点"""
    body_match = re.search(r"<body[^>]*>(.*?)</body>", xhtml_content, re.DOTALL | re.IGNORECASE)
    return body_match.group(1).strip() if body_match else xhtml_content.strip()


def resolve_zip_images(z: zipfile.ZipFile, chapter_dir: str, content: str) -> str:
    """将 XHTML 中的相对图片路径自动替换为 base64 DataURL"""
    def replacer(match):
        orig_tag = match.group(0)
        src = match.group(1)
        if src.startswith(("data:", "http://", "https://")):
            return orig_tag
        rel_path = os.path.normpath(os.path.join(chapter_dir, src)).replace("\\", "/")
        if rel_path in z.namelist():
            img_bytes = z.read(rel_path)
            mime = mimetypes.guess_type(rel_path)[0] or "image/png"
            b64_data = base64.b64encode(img_bytes).decode("ascii")
            return orig_tag.replace(src, f"data:{mime};base64,{b64_data}")
        return orig_tag

    return re.sub(r'<img[^>]+src=["\']([^"\']+)["\']', replacer, content, flags=re.IGNORECASE)


def rewrite_internal_links(content: str) -> str:
    """重写正文内的相对章节跳转，杜绝 404 Not Found"""
    def replacer(m):
        full_tag = m.group(0)
        raw_href = m.group(1)
        if raw_href.startswith(("http://", "https://", "mailto:", "data:", "#")):
            return full_tag
        if "#" in raw_href:
            target = "#" + raw_href.split("#", 1)[1]
        else:
            base = os.path.basename(raw_href)
            target = "#er-doc-" + re.sub(r"[^a-zA-Z0-9_-]", "_", base)
        return full_tag.replace(f'href="{raw_href}"', f'href="{target}" data-epub-href="{raw_href}"').replace(f"href='{raw_href}'", f'href="{target}" data-epub-href="{raw_href}"')

    return re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\']', replacer, content, flags=re.IGNORECASE)


def parse_hierarchical_toc(z: zipfile.ZipFile, manifest: Dict[str, Dict[str, str]]) -> str:
    """从 nav.xhtml 或 toc.ncx 中解析具有完整缩进层次的多级目录树"""
    nav_item = next((v for v in manifest.values() if "nav" in v.get("properties", "") or v["href"].endswith(("nav.xhtml", "nav.html"))), None)
    if nav_item and nav_item["href"] in z.namelist():
        nav_xml = z.read(nav_item["href"]).decode("utf-8", errors="ignore")
        match = re.search(r"<nav[^>]*epub:type=[\"']toc[\"'][^>]*>(.*?)</nav>", nav_xml, re.DOTALL | re.IGNORECASE)
        if not match:
            match = re.search(r"<nav[^>]*>(.*?)</nav>", nav_xml, re.DOTALL | re.IGNORECASE)
        if match:
            inner = re.sub(r"<h[1-6][^>]*>.*?</h[1-6]>", "", match.group(1), flags=re.DOTALL | re.IGNORECASE)
            
            def link_sub(m):
                raw_href = m.group(1)
                text = m.group(2)
                if "#" in raw_href:
                    target = "#" + raw_href.split("#", 1)[1]
                else:
                    base = os.path.basename(raw_href)
                    target = "#er-doc-" + re.sub(r"[^a-zA-Z0-9_-]", "_", base)
                return f'<a href="{target}" data-epub-href="{raw_href}">{text}</a>'

            res = re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', link_sub, inner, flags=re.DOTALL | re.IGNORECASE).strip()
            if re.search(r"^<ol\b", res, re.IGNORECASE):
                res = re.sub(r"^<ol\b[^>]*>", '<ol class="er-toc-tree">', res, count=1, flags=re.IGNORECASE)
            else:
                res = f'<ol class="er-toc-tree">{res}</ol>'
            return res

    return ""
