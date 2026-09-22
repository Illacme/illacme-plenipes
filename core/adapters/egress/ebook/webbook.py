# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Single-File Interactive WebBook Adapter
模块职责：将文库全卷编排导出为单个自包含、免阅读器依赖的高清离线网页书 (HTML)。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import base64
from html import escape
from typing import Dict, Any, List, Optional

from core.adapters.egress.ebook.base import BaseEBookAdapter
from core.adapters.egress.ebook.colophon import ColophonBuilder
from core.utils.tracing import tlog


class WebBookAdapter(BaseEBookAdapter):
    """🌐 单文件交互式网页书驱动（100% 离线自包含，零外部依赖）"""
    PLUGIN_ID = "webbook"
    DISPLAY_NAME = "单文件网页书 (WebBook)"
    OUTPUT_EXTENSION = ".html"
    MIME_TYPE = "text/html; charset=utf-8"
    VERSION = "V1.0"
    DESCRIPTION = "零阅读器依赖，单文件内置沉浸式侧边目录、三模主题与即时搜索的高清离线电子书。"

    def bind_book(
        self,
        manuscript_tree: List[Dict[str, Any]],
        book_metadata: Dict[str, Any],
        cover_image_path: Optional[str] = None,
        target_lang: str = "zh",
        output_file_path: str = ""
    ) -> bool:
        if not output_file_path:
            tlog.error("❌ [WebBook 装订] 未指定输出文件路径！")
            return False

        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)
            book_title = book_metadata.get("title", "未命名作品集")
            author = book_metadata.get("author", "极客创作者")
            iso_lang = target_lang if target_lang != "zh" else "zh-CN"

            # 1. 抽取并内联封面图片
            cover_data_uri = ""
            if cover_image_path and os.path.exists(cover_image_path):
                ext = os.path.splitext(cover_image_path)[1].lower()
                mime = "image/png" if ext == ".png" else ("image/svg+xml" if ext == ".svg" else "image/jpeg")
                with open(cover_image_path, "rb") as cf:
                    cover_data_uri = f"data:{mime};base64,{base64.b64encode(cf.read()).decode('utf-8')}"

            # 2. 预编译物理插图为 Base64 并构建快速查找表
            asset_map: Dict[str, str] = {}
            for ch in manuscript_tree:
                for asset in ch.get("assets", []):
                    t_name = asset.get("target_name")
                    s_path = asset.get("src_path") or asset.get("abs_path")
                    if t_name and s_path and t_name not in asset_map and os.path.exists(s_path):
                        m_type = asset.get("mime_type", "image/png")
                        with open(s_path, "rb") as af:
                            b64_str = base64.b64encode(af.read()).decode('utf-8')
                            asset_map[t_name] = f"data:{m_type};base64,{b64_str}"

            # 3. 组装各章节 HTML 与侧边栏目录
            toc_items = []
            chapters_html = []

            for idx, ch in enumerate(manuscript_tree):
                ch_id = f"ch_{idx + 1}"
                ch_title = escape(ch.get("title", f"第 {idx + 1} 节"))
                raw_body = ch.get("html_body", "<p></p>")

                # 内联插图 Data URI 替换
                def repl_img(m):
                    src = m.group(1).strip()
                    for t_name, b64_uri in asset_map.items():
                        if t_name in src:
                            return m.group(0).replace(f'src="{src}"', f'src="{b64_uri}"').replace(f"src='{src}'", f"src='{b64_uri}'")
                    return m.group(0)

                body_with_images = re.sub(r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>', repl_img, raw_body)
                # 自愈跨文件跳转为本单页锚点 (如 ch_2.xhtml#anchor -> #ch_2 或 #anchor)
                healed_body = re.sub(r'href="ch_\d+\.xhtml#(.*?)"', r'href="#\1"', body_with_images)
                healed_body = re.sub(r'href="(ch_\d+)\.xhtml"', r'href="#\1"', healed_body)

                toc_items.append(f'<a href="#{ch_id}" class="wb-toc-item" data-id="{ch_id}"><span class="wb-toc-num">{idx + 1}.</span> {ch_title}</a>')
                chapters_html.append(f"""
                <article id="{ch_id}" class="wb-chapter" data-title="{ch_title}">
                    <header class="wb-chapter-header">
                        <span class="wb-chapter-badge">Chapter {idx + 1}</span>
                        <h2 class="wb-chapter-title">{ch_title}</h2>
                    </header>
                    <div class="wb-chapter-body">{healed_body}</div>
                </article>""")

            # 4. 版记 Colophon 组装
            colophon_data = ColophonBuilder.build_colophon_data(manuscript_tree, book_metadata, "WebBook (单文件离线交互式典籍)")
            colophon_body = ColophonBuilder.render_xhtml(colophon_data, iso_lang=iso_lang)
            colophon_match = re.search(r'<body[^>]*>(.*?)</body>', colophon_body, flags=re.DOTALL)
            clean_colophon = colophon_match.group(1) if colophon_match else colophon_body
            toc_items.append('<a href="#colophon" class="wb-toc-item" data-id="colophon"><span class="wb-toc-num">✦</span> 版记 · Colophon</a>')
            chapters_html.append(f'<article id="colophon" class="wb-chapter">{clean_colophon}</article>')

            # 5. 渲染整卷完整自包含 WebBook
            full_html = self._render_full_document(book_title, author, iso_lang, cover_data_uri, ''.join(toc_items), ''.join(chapters_html))
            with open(output_file_path, "w", encoding="utf-8") as out_f:
                out_f.write(full_html)

            tlog.info(f"✨ [WebBook 装订成功] 离线网页书已落盘: {output_file_path} (共 {len(manuscript_tree)} 章节)")
            return True
        except Exception as e:
            tlog.error(f"❌ [WebBook 装订异常] 封包失败: {e}")
            return False

    def _render_full_document(self, title: str, author: str, lang: str, cover_uri: str, toc_html: str, content_html: str) -> str:
        cover_block = f'<div class="wb-cover-box"><img src="{cover_uri}" alt="Cover" class="wb-cover-img"/></div>' if cover_uri else ""
        return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="dark">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{escape(title)}</title>
<style>{self._get_embedded_css()}</style>
</head>
<body>
<div id="wb-progress" class="wb-progress-bar"></div>
<header class="wb-topbar">
    <div style="display:flex;align-items:center;gap:10px;">
        <button id="wb-toggle-sidebar" class="wb-btn" title="切换目录">☰</button>
        <span class="wb-book-title">{escape(title)}</span>
    </div>
    <div class="wb-controls">
        <button class="wb-theme-btn" data-theme="light" title="羊皮纸明亮">☀️</button>
        <button class="wb-theme-btn active" data-theme="dark" title="黑曜极夜">🌙</button>
        <button class="wb-theme-btn" data-theme="sepia" title="柔和护眼">☕</button>
        <button id="wb-font-dec" class="wb-btn" title="减小字号">A-</button>
        <button id="wb-font-inc" class="wb-btn" title="增大字号">A+</button>
    </div>
</header>
<div class="wb-layout">
    <aside id="wb-sidebar" class="wb-sidebar">
        {cover_block}
        <div class="wb-search-box"><input type="text" id="wb-search" placeholder="🔍 快速查找章节..." /></div>
        <nav class="wb-toc" id="wb-toc-nav">{toc_html}</nav>
        <div class="wb-sidebar-footer">© {escape(author)} · Illacme Press</div>
    </aside>
    <main class="wb-main" id="wb-main-container">
        <div class="wb-content-wrapper">{content_html}</div>
    </main>
</div>
<script>{self._get_embedded_js()}</script>
</body></html>"""

    @staticmethod
    def _get_embedded_css() -> str:
        return """:root {
  --bg-main: #0d1117; --bg-sidebar: #161b22; --bg-card: #1f242c; --text-main: #c9d1d9; --text-dim: #8b949e;
  --text-title: #f0f6fc; --accent: #10b981; --border: #30363d; --code-bg: #161b22; --font-size: 16px;
}
[data-theme="light"] {
  --bg-main: #ffffff; --bg-sidebar: #f6f8fa; --bg-card: #f8fafc; --text-main: #24292f; --text-dim: #57606a;
  --text-title: #0f172a; --accent: #059669; --border: #e1e4e8; --code-bg: #f6f8fa;
}
[data-theme="sepia"] {
  --bg-main: #fbf0d9; --bg-sidebar: #f4e3c1; --bg-card: #efe0bc; --text-main: #433422; --text-dim: #7f6e5d;
  --text-title: #2b1f14; --accent: #b45309; --border: #dfcaa7; --code-bg: #f5e7cd;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: var(--font-size); background: var(--bg-main); color: var(--text-main); line-height: 1.75; }
.wb-progress-bar { position: fixed; top: 0; left: 0; height: 3px; background: var(--accent); width: 0%; z-index: 1000; transition: width 0.1s; }
.wb-topbar { position: fixed; top: 0; left: 0; right: 0; height: 48px; background: var(--bg-sidebar); border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; padding: 0 16px; z-index: 900; }
.wb-book-title { font-weight: 700; font-size: 0.95rem; color: var(--text-title); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 50vw; }
.wb-btn { background: none; border: 1px solid var(--border); color: var(--text-main); border-radius: 4px; padding: 4px 8px; cursor: pointer; font-size: 0.85rem; }
.wb-controls { display: flex; gap: 6px; align-items: center; }
.wb-theme-btn { background: none; border: 1px solid var(--border); border-radius: 4px; padding: 3px 6px; cursor: pointer; }
.wb-theme-btn.active { border-color: var(--accent); background: rgba(16,185,129,0.15); }
.wb-layout { display: flex; margin-top: 48px; min-height: calc(100vh - 48px); }
.wb-sidebar { width: 300px; background: var(--bg-sidebar); border-right: 1px solid var(--border); position: fixed; top: 48px; bottom: 0; left: 0; display: flex; flex-direction: column; overflow: hidden; z-index: 800; transition: transform 0.3s; }
.wb-sidebar.collapsed { transform: translateX(-100%); }
.wb-cover-box { text-align: center; padding: 14px 10px 4px; }
.wb-cover-img { max-height: 140px; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); border: 1px solid var(--border); }
.wb-search-box { padding: 10px 14px; }
.wb-search-box input { width: 100%; padding: 6px 10px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; color: var(--text-main); font-size: 0.85rem; }
.wb-toc { flex: 1; overflow-y: auto; padding: 4px 10px; }
.wb-toc-item { display: block; padding: 7px 10px; text-decoration: none; color: var(--text-main); font-size: 0.88rem; border-radius: 6px; margin-bottom: 3px; }
.wb-toc-item:hover { background: rgba(16,185,129,0.1); color: var(--accent); }
.wb-toc-item.active { background: var(--accent); color: #fff; font-weight: 600; }
.wb-toc-num { opacity: 0.65; margin-right: 4px; }
.wb-sidebar-footer { font-size: 0.72rem; color: var(--text-dim); text-align: center; padding: 8px; border-top: 1px solid var(--border); }
.wb-main { flex: 1; margin-left: 300px; padding: 30px 40px 100px; transition: margin 0.3s; }
.wb-sidebar.collapsed ~ .wb-main { margin-left: 0; }
.wb-content-wrapper { max-width: 820px; margin: 0 auto; }
.wb-chapter { margin-bottom: 70px; padding-bottom: 40px; border-bottom: 1px solid var(--border); }
.wb-chapter-badge { font-size: 0.75rem; text-transform: uppercase; color: var(--accent); font-weight: 700; letter-spacing: 0.05em; }
.wb-chapter-title { font-size: 1.85rem; font-weight: 800; color: var(--text-title); margin: 6px 0 20px; }
.wb-chapter-body p { margin: 1em 0; }
.wb-chapter-body h1, .wb-chapter-body h2, .wb-chapter-body h3 { color: var(--text-title); margin: 1.4em 0 0.6em; }
.wb-chapter-body blockquote { border-left: 4px solid var(--accent); padding: 0.6em 1em; background: var(--bg-card); color: var(--text-dim); margin: 1.2em 0; }
.wb-chapter-body code { font-family: ui-monospace, Menlo, Consolas, monospace; background: var(--code-bg); padding: 2px 5px; border-radius: 4px; font-size: 0.9em; }
.wb-chapter-body pre { background: var(--code-bg); padding: 14px; border-radius: 6px; overflow-x: auto; border: 1px solid var(--border); margin: 1.2em 0; }
.wb-chapter-body pre code { background: transparent; padding: 0; }
.wb-chapter-body img { max-width: 100%; height: auto; display: block; margin: 1.5em auto; border-radius: 6px; border: 1px solid var(--border); }
.wb-chapter-body a { color: var(--accent); }
.codehilite { background: var(--code-bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; margin: 1.2em 0; overflow-x: auto; }
.math-block { display: flex; justify-content: center; margin: 1.4em 0; overflow-x: auto; }
math { font-size: 1.1em; color: var(--text-title); }
.colophon-card { border: 1px solid var(--border); background: var(--bg-card); padding: 20px; border-radius: 8px; margin: 20px 0; }
.colophon-grid { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.colophon-grid td { padding: 6px 8px; border-bottom: 1px dashed var(--border); }
@media (max-width: 768px) {
  .wb-sidebar { transform: translateX(-100%); }
  .wb-sidebar.open { transform: translateX(0); }
  .wb-main { margin-left: 0; padding: 20px 16px; }
}"""

    @staticmethod
    def _get_embedded_js() -> str:
        return """(function() {
  const sb = document.getElementById('wb-sidebar'), btn = document.getElementById('wb-toggle-sidebar');
  btn.onclick = () => { if (window.innerWidth <= 768) { sb.classList.toggle('open'); } else { sb.classList.toggle('collapsed'); } };
  document.querySelectorAll('.wb-theme-btn').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('.wb-theme-btn').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      document.documentElement.setAttribute('data-theme', b.getAttribute('data-theme'));
    };
  });
  let fs = 16;
  document.getElementById('wb-font-inc').onclick = () => { fs = Math.min(24, fs + 1); document.documentElement.style.setProperty('--font-size', fs + 'px'); };
  document.getElementById('wb-font-dec').onclick = () => { fs = Math.max(13, fs - 1); document.documentElement.style.setProperty('--font-size', fs + 'px'); };
  const search = document.getElementById('wb-search'), tocItems = document.querySelectorAll('.wb-toc-item');
  search.oninput = (e) => {
    const q = e.target.value.toLowerCase().trim();
    tocItems.forEach(item => { item.style.display = (!q || item.textContent.toLowerCase().includes(q)) ? 'block' : 'none'; });
  };
  window.onscroll = () => {
    const winScroll = document.documentElement.scrollTop, height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    document.getElementById('wb-progress').style.width = (height ? (winScroll / height * 100) : 0) + '%';
  };
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const id = e.target.id;
        tocItems.forEach(item => item.classList.toggle('active', item.getAttribute('data-id') === id));
      }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  document.querySelectorAll('.wb-chapter').forEach(ch => obs.observe(ch));
})();"""
