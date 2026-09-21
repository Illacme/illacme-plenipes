# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Native EPUB 3.0 Adapter (原生流式电子书装订驱动)
模块职责：将多章节原稿装订封包为符合 W3C / IDPF 标准的 EPUB 3.0 电子书。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import uuid
import html as py_html
import zipfile
import datetime
from typing import Dict, Any, List, Optional
from xml.sax.saxutils import escape

from .base import BaseEBookAdapter
from .colophon import ColophonBuilder
from core.utils.tracing import tlog


class EpubAdapter(BaseEBookAdapter):
    """🚀 原生 EPUB 3.0 流式装帧驱动（纯 Python 零重型黑盒依赖）"""
    PLUGIN_ID = "epub"
    DISPLAY_NAME = "EPUB 3.0 流式电子书"
    OUTPUT_EXTENSION = ".epub"
    MIME_TYPE = "application/epub+zip"
    VERSION = "V1.0"
    DESCRIPTION = "符合 W3C EPUB 3.0 国际规范的标准流式电子书驱动，深度适配主流阅读器。"

    DEFAULT_CSS = """
@charset "utf-8";
body { font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; line-height: 1.75; margin: 1em 1.2em; color: #222; }
h1, h2, h3, h4 { font-weight: 700; line-height: 1.3; margin-top: 1.4em; margin-bottom: 0.6em; }
h1 { font-size: 1.75em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
h2 { font-size: 1.4em; border-bottom: 1px solid #eaecef; padding-bottom: 0.25em; }
h3 { font-size: 1.2em; }
p { margin: 0.8em 0; text-align: justify; }
blockquote { margin: 1em 0; padding: 0.5em 1em; color: #555; border-left: 4px solid #00f2fe; background-color: #f8f9fa; }
code { font-family: "Courier New", Courier, monospace; font-size: 0.9em; background-color: #f1f3f5; padding: 0.2em 0.4em; border-radius: 3px; }
pre { background-color: #f6f8fa; padding: 1em; overflow-x: auto; border-radius: 6px; }
pre code { background-color: transparent; padding: 0; }
img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
.cover-container { text-align: center; margin: 0; padding: 0; }
.cover-image { max-width: 100%; max-height: 100vh; margin: auto; }
.colophon-page { padding: 1.5em 0.8em; }
.colophon-card { border: 1px solid #e1e4e8; background-color: #fafbfc; padding: 1.5em; border-radius: 8px; margin: 1.5em auto; }
.colophon-header { font-size: 1.25em; font-weight: 700; border-bottom: 2px solid #00f2fe; padding-bottom: 0.4em; margin-bottom: 1em; text-align: center; }
.colophon-grid { width: 100%; border-collapse: collapse; font-size: 0.88em; }
.colophon-grid td { padding: 0.4em 0.5em; border-bottom: 1px dashed #e1e4e8; }
.colophon-grid td.k { font-weight: 600; color: #555555; width: 32%; }
.colophon-grid td.v { color: #222222; }
.colophon-footer { font-size: 0.75em; color: #666666; margin-top: 1.2em; text-align: center; line-height: 1.5; }
nav ol { list-style-type: decimal; padding-left: 1.5em; }
nav li { margin: 0.4em 0; }
a { color: #0284c7; text-decoration: underline; text-decoration-color: rgba(2, 132, 199, 0.35); text-underline-offset: 3px; }
nav a { text-decoration: none; color: #0366d6; }
.callout { margin: 1em 0; padding: 0.8em 1.2em; border-left: 4px solid #00f2fe; background-color: #f8fafc; border-radius: 4px; }
.callout-tip { border-left-color: #10b981; background-color: #f0fdf4; }
.callout-note, .callout-info { border-left-color: #0284c7; background-color: #f0f9ff; }
.callout-warning { border-left-color: #f59e0b; background-color: #fffbeb; }
.callout-danger { border-left-color: #ef4444; background-color: #fef2f2; }
.callout-title { font-weight: 700; margin-bottom: 0.3em; }
.codehilite { background-color: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 6px; padding: 0.8em 1em; margin: 1.2em 0; overflow-x: auto; }
.codehilite pre { margin: 0; padding: 0; background: transparent; border: none; }
.codehilite .k, .codehilite .o { color: #d73a49; font-weight: 600; }
.codehilite .s, .codehilite .s1, .codehilite .s2 { color: #032f62; }
.codehilite .nf, .codehilite .nc { color: #6f42c1; }
.codehilite .c, .codehilite .c1 { color: #6a737d; font-style: italic; }
.codehilite .mi, .codehilite .mf { color: #005cc5; }
.math-block { display: flex; justify-content: center; align-items: center; margin: 1.2em auto; overflow-x: auto; }
math { font-size: 1.1em; }
@media (prefers-color-scheme: dark) {
    body { background-color: #121212; color: #e0e0e0; }
    a { color: #38bdf8; text-decoration-color: rgba(56, 189, 248, 0.4); }
    h1, h2 { border-bottom-color: #333; }
    blockquote { background-color: #1e1e1e; color: #aaa; }
    code { background-color: #2d2d2d; color: #f8f8f2; }
    pre { background-color: #1a1a1a; }
    .colophon-card { border-color: #333; background-color: #1a1a1a; }
    .colophon-grid td { border-bottom-color: #2a2a2a; }
    .colophon-grid td.k { color: #888; }
    .colophon-grid td.v { color: #ccc; }
    .colophon-footer { color: #777; }
    .codehilite { background-color: #161b22; border-color: #30363d; }
    .codehilite .k, .codehilite .o { color: #ff7b72; }
    .codehilite .s, .codehilite .s1, .codehilite .s2 { color: #a5d6ff; }
    .codehilite .nf, .codehilite .nc { color: #d2a8ff; }
    .codehilite .c, .codehilite .c1 { color: #8b949e; }
    .codehilite .mi, .codehilite .mf { color: #79c0ff; }
    .math-block math { color: #e6edf3; fill: #e6edf3; }
}
"""

    def bind_book(
        self,
        manuscript_tree: List[Dict[str, Any]],
        book_metadata: Dict[str, Any],
        cover_image_path: Optional[str] = None,
        target_lang: str = "zh",
        output_file_path: str = ""
    ) -> bool:
        if not output_file_path:
            tlog.error("❌ [EPUB 装订] 未指定输出文件路径！")
            return False

        os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)
        book_uuid = book_metadata.get("uuid") or str(uuid.uuid4())
        book_title = book_metadata.get("title", "未命名作品集")
        author = book_metadata.get("author", "极客创作者")
        publisher = book_metadata.get("publisher", "Illacme Plenipes Global Private Press")
        desc = book_metadata.get("description", "")
        pub_date = book_metadata.get("date") or datetime.date.today().isoformat()
        iso_lang = target_lang if target_lang != "zh" else "zh-CN"

        has_cover = bool(cover_image_path and os.path.exists(cover_image_path))
        cover_ext = os.path.splitext(cover_image_path)[1].lower() if has_cover else ".jpg"
        cover_mime = "image/png" if cover_ext == ".png" else "image/jpeg"

        try:
            with zipfile.ZipFile(output_file_path, "w") as zf:
                # 1. 写入 mimetype (必须未压缩保存在包头)
                zf.writestr("mimetype", b"application/epub+zip", compress_type=zipfile.ZIP_STORED)

                # 2. 写入 META-INF/container.xml
                container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
                zf.writestr("META-INF/container.xml", container_xml)

                # 3. 写入 CSS 样式
                zf.writestr("OEBPS/styles/epub.css", self.DEFAULT_CSS)

                # 4. 写入封面图片与封面页 (若有)
                if has_cover:
                    with open(cover_image_path, "rb") as cf:
                        zf.writestr(f"OEBPS/images/cover{cover_ext}", cf.read())
                    cover_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{iso_lang}">
<head><title>封面</title><link rel="stylesheet" href="../styles/epub.css"/></head>
<body class="cover-container">
  <img src="../images/cover{cover_ext}" alt="Cover" class="cover-image"/>
</body>
</html>"""
                    zf.writestr("OEBPS/text/cover.xhtml", cover_xhtml)

                # 5. 写入各章节 XHTML
                manifest_items = []
                spine_items = []

                if has_cover:
                    manifest_items.append(f'<item id="cover-img" href="images/cover{cover_ext}" media-type="{cover_mime}" properties="cover-image"/>')
                    manifest_items.append('<item id="cover-page" href="text/cover.xhtml" media-type="application/xhtml+xml"/>')
                    spine_items.append('<itemref idref="cover-page"/>')

                manifest_items.append('<item id="css" href="styles/epub.css" media-type="text/css"/>')
                manifest_items.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
                manifest_items.append('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
                spine_items.append('<itemref idref="nav"/>')

                toc_nav_points = []
                nav_ol_items = []
                packaged_assets = set()

                for idx, ch in enumerate(manuscript_tree):
                    ch_id = f"ch_{idx + 1}"
                    ch_filename = f"text/{ch_id}.xhtml"
                    ch_title = escape(ch.get("title", f"第 {idx + 1} 节"))
                    raw_html = ch.get("html_body", "<p></p>")

                    # 打包章节内引用的离线物理插图
                    for asset in ch.get("assets", []):
                        t_name = asset.get("target_name")
                        s_path = asset.get("src_path") or asset.get("abs_path")
                        if t_name and s_path and t_name not in packaged_assets and os.path.exists(s_path):
                            with open(s_path, "rb") as af:
                                zf.writestr(f"OEBPS/images/{t_name}", af.read())
                            m_type = asset.get("mime_type", "image/png")
                            manifest_items.append(f'<item id="img_{len(packaged_assets) + 1}" href="images/{t_name}" media-type="{m_type}"/>')
                            packaged_assets.add(t_name)

                    # 规范化 XHTML 闭合标签并探测 MathML 规范声明
                    clean_body = self._normalize_xhtml(raw_html)
                    m_prop = ' properties="mathml"' if '<math' in clean_body else ''

                    ch_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{iso_lang}">
<head><title>{ch_title}</title><link rel="stylesheet" href="../styles/epub.css"/></head>
<body>
  <div id="{ch_id}" class="chapter-container">
    <h1 id="{ch_id}_title">{ch_title}</h1>
    {clean_body}
  </div>
</body>
</html>"""
                    zf.writestr(f"OEBPS/{ch_filename}", ch_xhtml)
                    manifest_items.append(f'<item id="{ch_id}" href="{ch_filename}" media-type="application/xhtml+xml"{m_prop}/>')
                    spine_items.append(f'<itemref idref="{ch_id}"/>')

                    nav_ol_items.append(f'<li><a href="{ch_filename}">{ch_title}</a></li>')
                    toc_nav_points.append(f"""    <navPoint id="navPoint-{idx + 1}" playOrder="{idx + 1}">
      <navLabel><text>{ch_title}</text></navLabel>
      <content src="{ch_filename}"/>
    </navPoint>""")

                # 6. 写入出版版权页与物权指纹 (Colophon)
                colophon_data = ColophonBuilder.build_colophon_data(manuscript_tree, book_metadata, "EPUB 3.0 (IDPF / W3C 标准流式版式)")
                colophon_xhtml = ColophonBuilder.render_xhtml(colophon_data, iso_lang=iso_lang)
                zf.writestr("OEBPS/text/colophon.xhtml", colophon_xhtml)

                manifest_items.append('<item id="colophon" href="text/colophon.xhtml" media-type="application/xhtml+xml"/>')
                spine_items.append('<itemref idref="colophon"/>')
                nav_ol_items.append('<li><a href="text/colophon.xhtml">版记 · Colophon</a></li>')
                toc_nav_points.append(f"""    <navPoint id="navPoint-{len(manuscript_tree) + 1}" playOrder="{len(manuscript_tree) + 1}">
      <navLabel><text>版记 · Colophon</text></navLabel>
      <content src="text/colophon.xhtml"/>
    </navPoint>""")

                # 7. 写入 OEBPS/nav.xhtml (EPUB 3 原生目录)
                nav_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{iso_lang}">
<head><title>目录</title><link rel="stylesheet" href="styles/epub.css"/></head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>目录 · Table of Contents</h1>
    <ol>
      {''.join(nav_ol_items)}
    </ol>
  </nav>
</body>
</html>"""
                zf.writestr("OEBPS/nav.xhtml", nav_xhtml)

                # 7. 写入 OEBPS/toc.ncx (EPUB 2 兼容目录)
                toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:{book_uuid}"/>
    <meta name="dtb:depth" content="2"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{escape(book_title)}</text></docTitle>
  <docAuthor><text>{escape(author)}</text></docAuthor>
  <navMap>
{''.join(toc_nav_points)}
  </navMap>
</ncx>"""
                zf.writestr("OEBPS/toc.ncx", toc_ncx)

                # 8. 写入 OEBPS/content.opf (总包清单与骨架)
                content_opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="BookId">urn:uuid:{book_uuid}</dc:identifier>
    <dc:title>{escape(book_title)}</dc:title>
    <dc:creator>{escape(author)}</dc:creator>
    <dc:publisher>{escape(publisher)}</dc:publisher>
    <dc:language>{iso_lang}</dc:language>
    <dc:date>{pub_date}</dc:date>
    <dc:description>{escape(desc)}</dc:description>
    <meta property="dcterms:modified">{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}</meta>
  </metadata>
  <manifest>
    {chr(10).join(manifest_items)}
  </manifest>
  <spine toc="ncx">
    {chr(10).join(spine_items)}
  </spine>
</package>"""
                zf.writestr("OEBPS/content.opf", content_opf)

            tlog.info(f"✨ [EPUB 装订成功] 电子书已落盘: {output_file_path} (共 {len(manuscript_tree)} 章节)")
            return True
        except Exception as e:
            tlog.error(f"❌ [EPUB 装订异常] 封包失败: {e}")
            return False

    def _normalize_xhtml(self, html: str) -> str:
        """确保 HTML 片段符合严格的 XML 自闭合标准并剔除未声明实体"""
        def unescape_non_xml(m):
            ent = m.group(0)
            return ent if ent in ("&amp;", "&lt;", "&gt;", "&quot;", "&apos;") else py_html.unescape(ent)

        clean = re.sub(r"&[a-zA-Z0-9#x]+;", unescape_non_xml, html)
        for tag in ["img", "br", "hr", "input", "meta", "link"]:
            clean = re.sub(rf'<({tag}[^>/]*)(?<!/)>', r'<\1 />', clean, flags=re.IGNORECASE)
        clean = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', clean)
        clean = re.sub(r'<(?![a-zA-Z/!?])', '&lt;', clean)
        return clean
