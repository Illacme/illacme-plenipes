# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB 3.0 Assets & Template Builders
模块职责：提供 EPUB 默认样式表、多语对照封面双栏 XHTML 及多语对照导航目录 (nav.xhtml) 结构生成。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import re
import html as py_html
from xml.sax.saxutils import escape
from typing import Dict, Any, List, Optional
from core.bindery.toc_builder import TocBuilder
from .colophon import ColophonBuilder

LANG_NAMES: Dict[str, str] = {
    "zh": "🇨🇳 简体中文", "zh-hans": "🇨🇳 简体中文", "zh-hant": "🇭🇰 繁体中文",
    "en": "🇬🇧 English", "ja": "🇯🇵 日本語", "fr": "🇫🇷 Français",
    "de": "🇩🇪 Deutsch", "es": "🇪🇸 Español", "ru": "🇷🇺 Русский"
}

DEFAULT_EPUB_CSS = """
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
.callout-tip { border-left-color: #10b981; background-color: #f0fdf4; } .callout-warning { border-left-color: #f59e0b; background-color: #fffbeb; }
.callout-note, .callout-info { border-left-color: #0284c7; background-color: #f0f9ff; } .callout-danger { border-left-color: #ef4444; background-color: #fef2f2; }
.callout-title { font-weight: 700; margin-bottom: 0.3em; }
.codehilite { background-color: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 6px; padding: 0.8em 1em; margin: 1.2em 0; overflow-x: auto; }
.codehilite pre { margin: 0; padding: 0; background: transparent; border: none; }
.codehilite .k, .codehilite .o { color: #d73a49; font-weight: 600; } .codehilite .s, .codehilite .s1, .codehilite .s2 { color: #032f62; }
.codehilite .nf, .codehilite .nc { color: #6f42c1; } .codehilite .c, .codehilite .c1 { color: #6a737d; font-style: italic; } .codehilite .mi, .codehilite .mf { color: #005cc5; }
.math-block { display: flex; justify-content: center; align-items: center; margin: 1.2em auto; overflow-x: auto; } math { font-size: 1.1em; }
.wb-polyglot-block { display: flex; flex-direction: row; gap: 14px; margin: 1.2em 0; width: 100%; box-sizing: border-box; }
.wb-poly-item, .wb-poly-column { flex: 1 1 0; min-width: 0; background: #fafbfc; border: 1px solid #e1e4e8; border-radius: 8px; padding: 12px 14px; box-sizing: border-box; }
.wb-poly-header { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; padding-bottom: 5px; border-bottom: 2px solid #00f2fe; }
.wb-lang-badge { font-size: 0.72em; font-weight: 700; color: #fff; background: #0284c7; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; }
.wb-poly-lang-name { font-size: 0.85em; font-weight: 600; color: #333; }
.wb-poly-pending { background: #fffbeb; border: 1px dashed #f59e0b; border-radius: 6px; padding: 6px 10px; font-size: 0.8em; color: #b45309; margin-bottom: 8px; }
@media (max-width: 600px) { .wb-polyglot-block { flex-direction: column; gap: 10px; } }
@media (prefers-color-scheme: dark) {
    body { background-color: #121212; color: #e0e0e0; } a { color: #38bdf8; text-decoration-color: rgba(56, 189, 248, 0.4); }
    h1, h2 { border-bottom-color: #333; } blockquote { background-color: #1e1e1e; color: #aaa; } code { background-color: #2d2d2d; color: #f8f8f2; } pre { background-color: #1a1a1a; }
    .colophon-card { border-color: #333; background-color: #1a1a1a; } .colophon-grid td { border-bottom-color: #2a2a2a; } .colophon-grid td.k { color: #888; } .colophon-grid td.v { color: #ccc; } .colophon-footer { color: #777; }
    .codehilite { background-color: #161b22; border-color: #30363d; } .codehilite .k, .codehilite .o { color: #ff7b72; } .codehilite .s, .codehilite .s1, .codehilite .s2 { color: #a5d6ff; }
    .codehilite .nf, .codehilite .nc { color: #d2a8ff; } .codehilite .c, .codehilite .c1 { color: #8b949e; } .codehilite .mi, .codehilite .mf { color: #79c0ff; }
    .math-block math { color: #e6edf3; fill: #e6edf3; }
    .wb-poly-column { background: #161b22; border-color: #30363d; color: #c9d1d9; } .wb-poly-lang-name { color: #f0f6fc; }
    .wb-poly-pending { background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.35); color: #fbbf24; }
}
"""


def build_cover_xhtml(
    iso_lang: str,
    cover_ext: str,
    is_polyglot: bool = False,
    polyglot_langs: Optional[List[str]] = None,
    book_metadata: Optional[Dict[str, Any]] = None
) -> str:
    """构建单语/多语对照版封面 XHTML 骨架"""
    if not is_polyglot or not polyglot_langs or len(polyglot_langs) < 2:
        return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{iso_lang}">
<head><title>封面</title><link rel="stylesheet" href="../styles/epub.css"/></head>
<body class="cover-container">
  <img src="../images/cover{cover_ext}" alt="Cover" class="cover-image"/>
</body>
</html>"""

    meta = book_metadata or {}
    primary_lang = polyglot_langs[0]
    p_name = LANG_NAMES.get(primary_lang, primary_lang.upper())
    book_title = meta.get("title", "多语对照典籍")
    publisher = meta.get("publisher", "Illacme Plenipes Global Private Press")
    author = meta.get("author", "极客创作者")
    pub_date = meta.get("date") or "2026"
    matrix_str = " · ".join([l.upper() for l in polyglot_langs])

    cols_html = [f"""    <div class="wb-poly-column" data-lang="{primary_lang}">
      <div class="wb-poly-header"><span class="wb-lang-badge">{primary_lang.upper()}</span><span class="wb-poly-lang-name">{p_name} (原著封面)</span></div>
      <div class="wb-poly-content cover-container">
        <img src="../images/cover{cover_ext}" alt="Cover" class="cover-image"/>
      </div>
    </div>"""]

    for clang in polyglot_langs[1:]:
        c_name = LANG_NAMES.get(clang, clang.upper())
        cols_html.append(f"""    <div class="wb-poly-column" data-lang="{clang}">
      <div class="wb-poly-header"><span class="wb-lang-badge">{clang.upper()}</span><span class="wb-poly-lang-name">{c_name} (对照封面)</span></div>
      <div class="wb-poly-content cover-container">
        <img src="../images/cover_{clang}.svg" alt="{c_name} 封面" class="cover-image"/>
      </div>
    </div>""")

    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{iso_lang}">
<head><title>封面 · Cover</title><link rel="stylesheet" href="../styles/epub.css"/></head>
<body class="chapter-container">
  <div class="wb-polyglot-block wb-polyglot-columns">
{chr(10).join(cols_html)}
  </div>
</body>
</html>"""


def build_nav_xhtml(
    iso_lang: str,
    target_lang: str,
    is_polyglot: bool,
    polyglot_langs: List[str],
    manuscript_tree: List[Dict[str, Any]],
    nav_ol_items: List[str],
    has_colophon: bool,
    colophon_lbl: str
) -> str:
    """构建单语或多语对照版 nav.xhtml 导航大纲"""
    toc_title = "Table of Contents" if target_lang == "en" else ("目次 · Table of Contents" if target_lang == "ja" else "目录 · Table of Contents")
    if not is_polyglot or not polyglot_langs or len(polyglot_langs) < 2:
        return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{iso_lang}">
<head><title>{toc_title}</title><link rel="stylesheet" href="styles/epub.css"/></head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>{toc_title}</h1>
    <ol>
      {''.join(nav_ol_items)}
    </ol>
  </nav>
</body>
</html>"""

    primary_lang = polyglot_langs[0]
    p_name = LANG_NAMES.get(primary_lang, primary_lang.upper())

    cols_html = [f"""    <div class="wb-poly-column" data-lang="{primary_lang}">
      <div class="wb-poly-header"><span class="wb-lang-badge">{primary_lang.upper()}</span><span class="wb-poly-lang-name">{p_name} 目录</span></div>
      <div class="wb-poly-content">
        <nav epub:type="toc" id="toc">
          <h1>{toc_title}</h1>
          <ol>
            {''.join(nav_ol_items)}
          </ol>
        </nav>
      </div>
    </div>"""]

    for clang in polyglot_langs[1:]:
        c_name = LANG_NAMES.get(clang, clang.upper())
        comp_items = []
        for idx, ch in enumerate(manuscript_tree):
            ch_filename = f"text/ch_{idx + 1}.xhtml"
            t_map = ch.get("titles_by_lang", {})
            comp_t = escape(t_map.get(clang) or ch.get("title", f"Section {idx + 1}"))
            comp_h = ch.get("headings_by_lang", {}).get(clang) if ch.get("headings_by_lang") else TocBuilder.get_or_extract_headings(ch)
            comp_sub_ol = TocBuilder.render_epub_nav_ol(comp_h, ch_filename)
            comp_items.append(f'<li><a href="{ch_filename}">{comp_t}</a>{comp_sub_ol}</li>')

        if has_colophon:
            c_lbl = ColophonBuilder.get_nav_label(clang)
            comp_items.append(f'<li><a href="text/colophon.xhtml">{c_lbl}</a></li>')

        comp_toc_h1 = "Table of Contents" if clang == "en" else ("目次" if clang == "ja" else f"目录 ({clang.upper()})")
        cols_html.append(f"""    <div class="wb-poly-column" data-lang="{clang}">
      <div class="wb-poly-header"><span class="wb-lang-badge">{clang.upper()}</span><span class="wb-poly-lang-name">{c_name} 目录</span></div>
      <div class="wb-poly-content">
        <div class="wb-poly-toc-comp">
          <h1>{comp_toc_h1}</h1>
          <ol>
            {''.join(comp_items)}
          </ol>
        </div>
      </div>
    </div>""")

    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{iso_lang}">
<head><title>{toc_title}</title><link rel="stylesheet" href="styles/epub.css"/></head>
<body class="chapter-container">
  <div class="wb-polyglot-block wb-polyglot-columns">
{chr(10).join(cols_html)}
  </div>
</body>
</html>"""


def build_colophon_xhtml(
    colophon_data: Dict[str, Any],
    iso_lang: str,
    is_polyglot: bool,
    polyglot_langs: List[str],
    colophon_lbl: str
) -> str:
    """构建单语或多语对照版 colophon.xhtml 版记与物权指纹页面"""
    if not is_polyglot or not polyglot_langs or len(polyglot_langs) < 2:
        return ColophonBuilder.render_xhtml(colophon_data, iso_lang=iso_lang)

    cols_html = []
    for clang in polyglot_langs:
        c_name = LANG_NAMES.get(clang, clang.upper())
        c_iso = clang if clang != "zh" else "zh-CN"
        c_raw = ColophonBuilder.render_xhtml(colophon_data, iso_lang=c_iso)
        c_match = re.search(r'<body[^>]*>(.*?)</body>', c_raw, flags=re.DOTALL)
        inner_content = c_match.group(1).strip() if c_match else c_raw.strip()
        c_sub_lbl = ColophonBuilder.get_nav_label(clang)

        cols_html.append(f"""    <div class="wb-poly-column" data-lang="{clang}">
      <div class="wb-poly-header"><span class="wb-lang-badge">{clang.upper()}</span><span class="wb-poly-lang-name">{c_name} {c_sub_lbl}</span></div>
      <div class="wb-poly-content">
        {inner_content}
      </div>
    </div>""")

    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{iso_lang}">
<head>
  <title>{escape(colophon_lbl)}</title>
  <link rel="stylesheet" href="../styles/epub.css"/>
</head>
<body class="colophon-page chapter-container">
  <div class="wb-polyglot-block wb-polyglot-columns">
{chr(10).join(cols_html)}
  </div>
</body>
</html>"""

