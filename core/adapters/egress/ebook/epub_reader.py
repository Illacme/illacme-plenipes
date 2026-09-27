# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Engine
模块职责：调度 EPUB 电子书翻阅内核，支持 Python 服务端预解析与纯客户端 JS 离线解包双模。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import zipfile
import html
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional

from .epub_reader_template import build_epub_reader_shell
from .epub_reader_client_js import get_epub_client_loader_css, get_epub_client_engine_js
from .epub_reader_parser import (
    extract_body_html,
    resolve_zip_images,
    rewrite_internal_links,
    parse_hierarchical_toc,
)


def _get_qr_metadata(epub_path: str) -> Dict[str, str]:
    """安全解析自适应二维码元数据"""
    try:
        from core.bindery.qr_sync import resolve_adaptive_qr_payload
        qr_info = resolve_adaptive_qr_payload(os.path.basename(epub_path), action="view")
        return {
            "qr_data_uri": qr_info.get("qr_data_uri", ""),
            "qr_url": qr_info.get("url", ""),
            "qr_tier": qr_info.get("tier", "lan"),
            "qr_tip": qr_info.get("tip_text", "📱 手机扫码直达翻阅"),
        }
    except Exception:
        return {
            "qr_data_uri": "", "qr_url": "", "qr_tier": "lan",
            "qr_tip": "📱 手机扫码直达翻阅"
        }


def _render_client_js_mode(epub_path: str, base_fn: str, qr_meta: Dict[str, str]) -> str:
    """🌐 [Client-Side JS Engine] 纯前端离线客户端解析阅读器渲染"""
    book_title = os.path.splitext(base_fn)[0]
    try:
        with zipfile.ZipFile(epub_path, "r") as z:
            c_xml = z.read("META-INF/container.xml")
            rf = ET.fromstring(c_xml).find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile")
            if rf is not None and "full-path" in rf.attrib:
                opf_data = z.read(rf.attrib["full-path"])
                t_el = ET.fromstring(opf_data).find(".//{http://purl.org/dc/elements/1.1/}title")
                if t_el is not None and t_el.text:
                    book_title = t_el.text.strip()
    except Exception:
        pass
    enc_fn = urllib.parse.quote(base_fn)
    source_url = f"/api/bindery/download?file={enc_fn}"

    # 读取本地化的 JSZip 核心库 (严格遵循 SOP-03 供应链本土化)
    jszip_vendor_path = os.path.abspath("web/dashboard/vendor/jszip.min.js")
    jszip_script = ""
    if os.path.isfile(jszip_vendor_path):
        try:
            with open(jszip_vendor_path, "r", encoding="utf-8") as f:
                jszip_script = f"<script>{f.read()}</script>\n"
        except Exception:
            jszip_script = '<script src="/dashboard/vendor/jszip.min.js"></script>\n'
    else:
        jszip_script = '<script src="/dashboard/vendor/jszip.min.js"></script>\n'

    client_scripts = f"{jszip_script}<script>{get_epub_client_engine_js()}</script>"

    loader_html = """
    <div class="er-client-loader" id="er-client-loader">
      <div class="er-loader-spinner">⏳</div>
      <div class="er-loader-title">正在载入纯 JS 典籍引擎...</div>
      <div class="er-loader-desc">100% 浏览器前端内存解包，脱离 Python 服务端运行。</div>
    </div>
    """

    return build_epub_reader_shell(
        book_title=book_title,
        toc_html="",
        content_html=loader_html,
        qr_data_uri=qr_meta["qr_data_uri"],
        qr_url=qr_meta["qr_url"],
        qr_tier=qr_meta["qr_tier"],
        qr_tip=qr_meta["qr_tip"],
        source_url=source_url,
        client_scripts_html=client_scripts,
        extra_css=get_epub_client_loader_css()
    )


def _render_python_mode(epub_path: str, qr_meta: Dict[str, str]) -> str:
    """⚡ [Python Server-Side Engine] 服务端极速预解析直出 HTML 渲染"""
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

    cover_item = next((c for c in chapters if "cover" in c["id"]), None)
    cover_nav_html = f'<li class="er-toc-cover"><a href="#{cover_item["id"]}" class="er-toc-link">📕 典籍封面与扉页</a></li>\n' if cover_item else ''
    if toc_tree_html:
        final_toc_html = toc_tree_html.replace('<ol class="er-toc-tree">', f'<ol class="er-toc-tree">\n  {cover_nav_html}', 1) if ('<ol class="er-toc-tree">' in toc_tree_html and cover_nav_html) else (f'<ol class="er-toc-tree">\n{cover_nav_html}</ol>\n{toc_tree_html}' if cover_nav_html else toc_tree_html)
    else:
        final_toc_html = f'<ol class="er-toc-tree">\n{cover_nav_html}' + "\n".join([f'  <li><a href="#{c["id"]}" class="er-toc-link">📖 {html.escape(c["title"])}</a></li>' for c in fallback_toc if "cover" not in c["id"]]) + '\n</ol>'

    chapters_html = "\n".join([f'<article class="{c["class"]}" id="{c["id"]}">{c["content"]}</article>' for c in chapters])

    return build_epub_reader_shell(
        book_title=book_title,
        toc_html=final_toc_html,
        content_html=chapters_html,
        qr_data_uri=qr_meta["qr_data_uri"],
        qr_url=qr_meta["qr_url"],
        qr_tier=qr_meta["qr_tier"],
        qr_tip=qr_meta["qr_tip"]
    )


def render_epub_reader_html(epub_path: str, engine: Optional[str] = None) -> str:
    """🎯 双模智能调度：将物理 EPUB 渲染为在线翻阅 HTML 视界 (Python / Client-Side JS)"""
    if not os.path.isfile(epub_path):
        raise FileNotFoundError(f"EPUB 文件不存在: {epub_path}")

    # 1. 解析活跃翻阅引擎 (优先显式入参，次选全局配置，默认 python)
    active_engine = (engine or "").strip().lower()
    if not active_engine:
        try:
            from core.config.config import load_config
            cfg = load_config()
            active_engine = getattr(cfg, "epub_reader_engine", "python") or "python"
        except Exception:
            active_engine = "python"

    qr_meta = _get_qr_metadata(epub_path)
    base_fn = os.path.basename(epub_path)

    if active_engine == "client_js":
        return _render_client_js_mode(epub_path, base_fn, qr_meta)
    return _render_python_mode(epub_path, qr_meta)
