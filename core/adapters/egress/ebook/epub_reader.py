# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Engine
模块职责：将已编译的 EPUB 3.0 电子书在内存中以流式方式重构为多级树状目录与高质感网页书卷阅读器。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import base64
import mimetypes
import zipfile
import html
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional

from .epub_reader_css import get_epub_reader_css
from .epub_reader_js import get_epub_reader_js


def _extract_body_html(xhtml_content: str) -> str:
    """提取 XHTML 中的 body 内部 HTML 节点"""
    body_match = re.search(r"<body[^>]*>(.*?)</body>", xhtml_content, re.DOTALL | re.IGNORECASE)
    return body_match.group(1).strip() if body_match else xhtml_content.strip()


def _resolve_zip_images(z: zipfile.ZipFile, chapter_dir: str, content: str) -> str:
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


def _rewrite_internal_links(content: str) -> str:
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


def _parse_hierarchical_toc(z: zipfile.ZipFile, manifest: Dict[str, Dict[str, str]]) -> str:
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


def render_epub_reader_html(epub_path: str) -> str:
    """将物理 EPUB 文件渲染为高质感自包含在线翻阅 HTML 视界"""
    if not os.path.isfile(epub_path):
        raise FileNotFoundError(f"EPUB 文件不存在: {epub_path}")

    with zipfile.ZipFile(epub_path, "r") as z:
        container_xml = z.read("META-INF/container.xml")
        rootfile = ET.fromstring(container_xml).find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile")
        if rootfile is None or "full-path" not in rootfile.attrib:
            raise ValueError("非法的 EPUB：未找到 rootfile 定义")
        
        opf_path = rootfile.attrib["full-path"]
        opf_dir = os.path.dirname(opf_path)
        opf_root = ET.fromstring(z.read(opf_path))
        ns = {"opf": "http://www.idpf.org/2007/opf", "dc": "http://purl.org/dc/elements/1.1/"}

        title_el = opf_root.find(".//dc:title", ns)
        book_title = title_el.text if title_el is not None and title_el.text else os.path.splitext(os.path.basename(epub_path))[0]
        creator_el = opf_root.find(".//dc:creator", ns)
        book_author = creator_el.text if creator_el is not None and creator_el.text else "佚名"

        manifest: Dict[str, Dict[str, str]] = {}
        for item in opf_root.findall(".//opf:manifest/opf:item", ns):
            i_id = item.attrib["id"]
            i_href = os.path.normpath(os.path.join(opf_dir, item.attrib["href"])).replace("\\", "/")
            manifest[i_id] = {"href": i_href, "media-type": item.attrib.get("media-type", ""), "properties": item.attrib.get("properties", "")}

        spine_ids = [ref.attrib["idref"] for ref in opf_root.findall(".//opf:spine/opf:itemref", ns)]
        toc_tree_html = _parse_hierarchical_toc(z, manifest)

        chapters: List[Dict[str, Any]] = []
        fallback_toc: List[Dict[str, str]] = []

        for idx, sid in enumerate(spine_ids):
            item = manifest.get(sid)
            if not item or item["href"] not in z.namelist():
                continue
            href = item["href"]
            base_fn = os.path.basename(href)
            clean_base = re.sub(r"[^a-zA-Z0-9_-]", "_", base_fn)
            card_id = f"er-doc-{clean_base}"

            raw_content = z.read(href).decode("utf-8", errors="replace")
            processed_html = _resolve_zip_images(z, os.path.dirname(href), raw_content)
            body_html = _extract_body_html(processed_html)
            body_html = _rewrite_internal_links(body_html)

            is_cover = "cover" in base_fn.lower() or "cover-image" in item.get("properties", "")
            if is_cover:
                chap_title = "封面扉页"
                card_class = "er-chapter-card er-cover-card"
            else:
                t_match = re.search(r"<h[1-3][^>]*>(.*?)</h[1-3]>", body_html, re.DOTALL | re.IGNORECASE)
                chap_title = re.sub(r"<[^>]+>", "", t_match.group(1)).strip() if t_match else f"第 {idx + 1} 卷"
                card_class = "er-chapter-card"

            chapters.append({"id": card_id, "title": chap_title, "content": body_html, "class": card_class})
            fallback_toc.append({"id": card_id, "title": chap_title})

    # 目录拼接：优先采用从 nav.xhtml 提取的完整分级树，并在最顶部置顶封面
    cover_item = next((c for c in chapters if "cover" in c["id"]), None)
    cover_nav_html = f'<li class="er-toc-cover"><a href="#{cover_item["id"]}" class="er-toc-link">📕 典籍封面与扉页</a></li>\n' if cover_item else ''
    
    if toc_tree_html:
        if '<ol class="er-toc-tree">' in toc_tree_html and cover_nav_html:
            final_toc_html = toc_tree_html.replace('<ol class="er-toc-tree">', f'<ol class="er-toc-tree">\n  {cover_nav_html}', 1)
        else:
            final_toc_html = f'<ol class="er-toc-tree">\n{cover_nav_html}</ol>\n{toc_tree_html}' if cover_nav_html else toc_tree_html
    else:
        final_toc_html = f'<ol class="er-toc-tree">\n{cover_nav_html}' + "\n".join([f'  <li><a href="#{c["id"]}" class="er-toc-link">📖 {html.escape(c["title"])}</a></li>' for c in fallback_toc if "cover" not in c["id"]]) + '\n</ol>'

    chapters_html = "\n".join([
        f'<article class="{c["class"]}" id="{c["id"]}">{c["content"]}</article>'
        for c in chapters
    ])

    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0"/>
  <title>{html.escape(book_title)} - EPUB 在线翻阅</title>
  <style>{get_epub_reader_css()}</style>
</head>
<body>
  <div class="er-progress-bar" id="er-progress-bar"></div>
  <header class="er-topbar">
    <div class="er-topbar-left">
      <button type="button" class="er-btn" id="er-toggle-sidebar" title="展开/收起目录">☰ 目录</button>
      <div class="er-book-title" title="{html.escape(book_title)}">{html.escape(book_title)}</div>
    </div>
    <div class="er-controls">
      <button type="button" class="er-btn" id="er-font-dec" title="缩小字号">A-</button>
      <button type="button" class="er-btn" id="er-font-inc" title="放大字号">A+</button>
      <button type="button" class="er-theme-btn active" data-theme="dark" title="暗黑翠玉">🌙</button>
      <button type="button" class="er-theme-btn" data-theme="light" title="高亮纯净">☀️</button>
      <button type="button" class="er-theme-btn" data-theme="sepia" title="复古羊皮纸">📜</button>
    </div>
  </header>

  <div class="er-layout">
    <aside class="er-sidebar" id="er-sidebar">
      <div class="er-sidebar-title">典籍分级目录</div>
      {final_toc_html}
    </aside>
    <div class="er-backdrop" id="er-backdrop"></div>
    <main class="er-main">
      {chapters_html}
    </main>
  </div>

  <script>{get_epub_reader_js()}</script>
</body>
</html>"""
