# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Engine
模块职责：将已编译的 EPUB 3.0 电子书在内存中以流式方式重构为多级树状目录与高质感网页书卷阅读器。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import zipfile
import html
import xml.etree.ElementTree as ET
from typing import Dict, List, Any

from .epub_reader_css import get_epub_reader_css
from .epub_reader_js import get_epub_reader_js
from .epub_reader_annotator import get_epub_annotator_css, get_epub_annotator_js
from .epub_reader_search import get_epub_search_css, get_epub_search_js
from .epub_reader_parser import (
    extract_body_html,
    resolve_zip_images,
    rewrite_internal_links,
    parse_hierarchical_toc,
)


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

        manifest: Dict[str, Dict[str, str]] = {}
        for item in opf_root.findall(".//opf:manifest/opf:item", ns):
            i_id = item.attrib["id"]
            i_href = os.path.normpath(os.path.join(opf_dir, item.attrib["href"])).replace("\\", "/")
            manifest[i_id] = {"href": i_href, "media-type": item.attrib.get("media-type", ""), "properties": item.attrib.get("properties", "")}

        spine_ids = [ref.attrib["idref"] for ref in opf_root.findall(".//opf:spine/opf:itemref", ns)]
        toc_tree_html = parse_hierarchical_toc(z, manifest)

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
            processed_html = resolve_zip_images(z, os.path.dirname(href), raw_content)
            body_html = extract_body_html(processed_html)
            body_html = rewrite_internal_links(body_html)

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
<html lang="zh-CN" data-theme="dark" data-read-mode="paginated" data-spread="auto" data-font="sans">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0"/>
  <title>{html.escape(book_title)} - EPUB 在线翻阅</title>
  <style>{get_epub_reader_css()}\n{get_epub_annotator_css()}\n{get_epub_search_css()}</style>
</head>
<body>
  <div class="er-progress-bar" id="er-progress-bar"></div>
  <header class="er-topbar">
    <div class="er-topbar-left">
      <button type="button" class="er-btn" id="er-toggle-sidebar" title="展开/收起侧边栏">☰<span class="er-btn-text"> 目录/检索</span></button>
      <div class="er-book-title" title="{html.escape(book_title)}">{html.escape(book_title)}</div>
    </div>
    <div class="er-controls">
      <button type="button" class="er-btn" id="er-spread-toggle" title="切换排版：单页 / 双页对开">📑<span class="er-btn-text"> 双页</span></button>
      <button type="button" class="er-btn" id="er-font-family" title="切换字体：黑体 / 宋体 / 楷体">🔤<span class="er-btn-text"> 黑体</span></button>
      <button type="button" class="er-btn er-mode-btn" id="er-mode-toggle" title="切换阅读模式：左右翻页 / 连续卷轴">📖<span class="er-btn-text"> 翻页</span></button>
      <button type="button" class="er-btn" id="er-font-dec" title="缩小字号">A-</button>
      <button type="button" class="er-btn" id="er-font-inc" title="放大字号">A+</button>
      <button type="button" class="er-theme-btn active" data-theme="dark" title="暗黑翠玉">🌙</button>
      <button type="button" class="er-theme-btn" data-theme="light" title="高亮纯净">☀️</button>
      <button type="button" class="er-theme-btn" data-theme="sepia" title="复古羊皮纸">📜</button>
      <button type="button" class="er-btn" id="er-fullscreen" title="全屏沉浸阅读 (快捷键 F)">⛶</button>
    </div>
  </header>

  <div class="er-layout">
    <aside class="er-sidebar" id="er-sidebar">
      <div class="er-sidebar-tabs">
        <button type="button" class="er-stab-btn active" id="er-stab-toc" data-tab="er-pane-toc">📑 目录</button>
        <button type="button" class="er-stab-btn" id="er-stab-notes" data-tab="er-pane-notes">🔖 划线 <span class="er-badge" id="er-notes-count">0</span></button>
        <button type="button" class="er-stab-btn" id="er-stab-search" data-tab="er-pane-search">🔍 检索 <span class="er-badge" id="er-search-count">0</span></button>
      </div>
      <div class="er-sidebar-pane active" id="er-pane-toc">
        {final_toc_html}
      </div>
      <div class="er-sidebar-pane" id="er-pane-notes">
        <div class="er-notes-toolbar">
          <button type="button" class="er-btn er-btn-sm er-btn-primary" id="er-export-notes-btn">📥 导出笔记</button>
          <button type="button" class="er-btn er-btn-sm" id="er-clear-notes-btn">🗑️ 清空</button>
        </div>
        <div class="er-notes-list" id="er-notes-list"></div>
      </div>
      <div class="er-sidebar-pane" id="er-pane-search">
        <div class="er-search-box">
          <span class="er-search-icon">🔍</span>
          <input type="text" class="er-search-input" id="er-search-input" placeholder="输入关键词检索全书..." autocomplete="off"/>
          <span class="er-search-kbd">⌘K</span>
        </div>
        <div class="er-search-meta" id="er-search-meta">输入关键词检索全书典籍</div>
        <div class="er-search-results" id="er-search-results">
          <div class="er-search-empty">输入关键词，即可秒级全文检索所有章节与段落。</div>
        </div>
      </div>
    </aside>
    <div class="er-backdrop" id="er-backdrop"></div>
    <main class="er-main" id="er-main">
      <button type="button" class="er-page-arrow er-page-prev" id="er-page-prev" title="上一页 (←)">‹</button>
      <button type="button" class="er-page-arrow er-page-next" id="er-page-next" title="下一页 (→)">›</button>
      
      <div class="er-viewport" id="er-viewport">
        <div class="er-book-content" id="er-book-content">
          {chapters_html}
        </div>
      </div>

      <footer class="er-paginated-footer" id="er-paginated-footer">
        <div class="er-footer-chapter" id="er-footer-chapter"></div>
        <div class="er-footer-page" id="er-footer-page">1 / 1</div>
      </footer>
    </main>
  </div>

  <!-- 🎈 划选浮动工具栏 -->
  <div class="er-floating-bar" id="er-floating-bar">
    <button type="button" class="er-fbtn" data-color="yellow" title="黄荧光划线"><span class="er-fdot dot-yellow"></span> 划线</button>
    <button type="button" class="er-fbtn" data-color="emerald" title="翠绿高亮"><span class="er-fdot dot-emerald"></span></button>
    <button type="button" class="er-fbtn" data-color="pink" title="胭脂粉高亮"><span class="er-fdot dot-pink"></span></button>
    <div class="er-fsep"></div>
    <button type="button" class="er-fbtn" id="er-fbtn-note" title="随手批注">💭 批注</button>
    <button type="button" class="er-fbtn" id="er-fbtn-card" title="生成金句卡片">🖼️ 金句卡片</button>
    <button type="button" class="er-fbtn" id="er-fbtn-copy" title="复制纯文本">📋 复制</button>
  </div>

  <!-- 🖼️ 金句卡片模态窗 -->
  <div class="er-modal-backdrop" id="er-card-modal">
    <div class="er-card-box">
      <div class="er-quote-card" id="er-quote-card">
        <div class="er-card-quote-mark">“</div>
        <div class="er-card-quote-text" id="er-card-text"></div>
        <div class="er-card-quote-mark-end">”</div>
        <div class="er-card-meta">
          <div>
            <div class="er-card-book-title" id="er-card-book"></div>
            <div class="er-card-chapter" id="er-card-chap"></div>
          </div>
          <div class="er-card-brand">Illacme Plenipes</div>
        </div>
      </div>
      <div class="er-card-actions">
        <button type="button" class="er-btn" id="er-card-close-btn">关闭</button>
        <button type="button" class="er-btn" id="er-card-copy-btn">📋 复制金句文本</button>
        <button type="button" class="er-btn er-btn-primary" id="er-card-save-btn">🖼️ 保存卡片海报</button>
      </div>
    </div>
  </div>

  <!-- ✍️ 随手批注模态窗 -->
  <div class="er-modal-backdrop" id="er-note-modal">
    <div class="er-note-box">
      <div class="er-note-box-title">✍️ 记录随笔思考</div>
      <div class="er-note-target-text" id="er-note-target-text"></div>
      <textarea class="er-note-input" id="er-note-input" rows="3" placeholder="在此写下对本段文字的灵感、考据或思考..."></textarea>
      <div class="er-note-actions">
        <button type="button" class="er-btn" id="er-note-cancel-btn">取消</button>
        <button type="button" class="er-btn er-btn-primary" id="er-note-save-btn">保存批注</button>
      </div>
    </div>
  </div>

  <script>{get_epub_reader_js()}</script>
  <script>{get_epub_annotator_js()}</script>
  <script>{get_epub_search_js()}</script>
</body>
</html>"""
