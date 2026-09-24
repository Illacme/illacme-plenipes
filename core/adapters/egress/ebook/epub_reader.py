# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Engine
模块职责：将已编译的 EPUB 3.0 电子书在内存中以流式方式重构为高质感自包含网页书卷阅读器。
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
    if body_match:
        return body_match.group(1).strip()
    return xhtml_content.strip()


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
            data_uri = f"data:{mime};base64,{b64_data}"
            return orig_tag.replace(src, data_uri)
        return orig_tag

    return re.sub(r'<img[^>]+src=["\']([^"\']+)["\']', replacer, content, flags=re.IGNORECASE)


def render_epub_reader_html(epub_path: str) -> str:
    """将物理 EPUB 文件渲染为高质感自包含在线翻阅 HTML 视界"""
    if not os.path.isfile(epub_path):
        raise FileNotFoundError(f"EPUB 文件不存在: {epub_path}")

    with zipfile.ZipFile(epub_path, "r") as z:
        # 1. 解析容器入口
        container_xml = z.read("META-INF/container.xml")
        root = ET.fromstring(container_xml)
        rootfile = root.find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile")
        if rootfile is None or "full-path" not in rootfile.attrib:
            raise ValueError("非法的 EPUB：未找到 rootfile 定义")
        
        opf_path = rootfile.attrib["full-path"]
        opf_dir = os.path.dirname(opf_path)

        # 2. 解析 OPF 元数据与资源清单
        opf_xml = z.read(opf_path)
        opf_root = ET.fromstring(opf_xml)
        ns = {"opf": "http://www.idpf.org/2007/opf", "dc": "http://purl.org/dc/elements/1.1/"}

        title_el = opf_root.find(".//dc:title", ns)
        book_title = title_el.text if title_el is not None and title_el.text else os.path.splitext(os.path.basename(epub_path))[0]
        creator_el = opf_root.find(".//dc:creator", ns)
        book_author = creator_el.text if creator_el is not None and creator_el.text else "佚名"

        manifest: Dict[str, Dict[str, str]] = {}
        cover_id = None
        for item in opf_root.findall(".//opf:manifest/opf:item", ns):
            i_id = item.attrib["id"]
            i_href = os.path.normpath(os.path.join(opf_dir, item.attrib["href"])).replace("\\", "/")
            i_props = item.attrib.get("properties", "")
            manifest[i_id] = {"href": i_href, "media-type": item.attrib.get("media-type", "")}
            if "cover-image" in i_props or i_id in ("cover-img", "cover", "cover-image"):
                cover_id = i_id

        # 3. 提取 Spine 章节顺序
        spine_ids: List[str] = []
        for itemref in opf_root.findall(".//opf:spine/opf:itemref", ns):
            spine_ids.append(itemref.attrib["idref"])

        # 4. 读取并构建各章节内容与目录列表
        chapters: List[Dict[str, Any]] = []
        toc_items: List[Dict[str, str]] = []

        for idx, sid in enumerate(spine_ids):
            item = manifest.get(sid)
            if not item:
                continue
            href = item["href"]
            if href not in z.namelist():
                continue

            raw_content = z.read(href).decode("utf-8", errors="replace")
            chapter_dir = os.path.dirname(href)
            processed_html = _resolve_zip_images(z, chapter_dir, raw_content)
            body_html = _extract_body_html(processed_html)

            # 提取章节名
            t_match = re.search(r"<h[1-3][^>]*>(.*?)</h[1-3]>", body_html, re.DOTALL | re.IGNORECASE)
            if t_match:
                chap_title = re.sub(r"<[^>]+>", "", t_match.group(1)).strip()
            else:
                chap_title = f"第 {idx + 1} 卷"

            chap_id = f"chap_{idx + 1}"
            chapters.append({"id": chap_id, "title": chap_title, "content": body_html})
            toc_items.append({"id": chap_id, "title": chap_title})

    # 5. 拼装 TOC 侧边栏与正文卡片 HTML
    toc_html = "\n".join([
        f'<li class="er-toc-item"><a href="#{c["id"]}">📖 {html.escape(c["title"])}</a></li>'
        for c in toc_items
    ])

    chapters_html = "\n".join([
        f'<article class="er-chapter-card" id="{c["id"]}">{c["content"]}</article>'
        for c in chapters
    ])

    css_code = get_epub_reader_css()
    js_code = get_epub_reader_js()

    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0"/>
  <title>{html.escape(book_title)} - EPUB 在线翻阅</title>
  <style>{css_code}</style>
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
      <div class="er-sidebar-title">典籍卷册目录</div>
      <ul class="er-toc-list">{toc_html}</ul>
    </aside>
    <div class="er-backdrop" id="er-backdrop"></div>
    <main class="er-main">
      {chapters_html}
    </main>
  </div>

  <script>{js_code}</script>
</body>
</html>"""
