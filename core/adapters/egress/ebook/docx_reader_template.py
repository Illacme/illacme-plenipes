# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Word Document (.docx) Interactive Web Reviewer Template
模块职责：提供拟真 A4 多页物理装订审阅 HTML 骨架、样式、分页中枢与移动端自适应。
🛡️ [SOP-01 规范]：单文件严格 <= 300 行。
"""

import html


def assemble_docx_template(fn: str, size_kb: float, total_pages: int, content: str, dl_url: str) -> str:
    """组装拟真 A4 Word 审阅网页（支持脱机 Mermaid 图码切换、内部锚点平滑滚动、移动端响应式与快速翻页）"""
    esc_fn = html.escape(fn)
    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="paper">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>📑 审校在线阅览 - {esc_fn}</title>
  <style>
    :root {{ --bg-canvas: #f1f5f9; --page-bg: #ffffff; --text-main: #1e293b; --text-muted: #64748b; --border-color: #cbd5e1; --accent: #10b981; --link-color: #2563eb; --page-shadow: 0 4px 6px -1px rgba(0,0,0,0.06), 0 20px 25px -5px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04); --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif; }}
    [data-theme="warm"] {{ --bg-canvas: #eee8d5; --page-bg: #fdf6e3; --text-main: #2b2b2b; --text-muted: #78716c; --border-color: #d3cbb7; --accent: #d97706; --link-color: #b45309; --page-shadow: 0 4px 15px rgba(0,0,0,0.06); }}
    [data-theme="dark"] {{ --bg-canvas: #090d16; --page-bg: #141c2e; --text-main: #f1f5f9; --text-muted: #94a3b8; --border-color: #27354f; --accent: #34d399; --link-color: #38bdf8; --page-shadow: 0 8px 30px rgba(0,0,0,0.6); }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg-canvas); color: var(--text-main); font-family: var(--font-family); min-height: 100vh; display: flex; flex-direction: column; transition: background 0.2s ease; scroll-behavior: smooth; }}
    .viewer-navbar {{ position: sticky; top: 0; z-index: 50; display: flex; justify-content: space-between; align-items: center; padding: 8px 18px; background: rgba(255, 255, 255, 0.92); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-bottom: 1px solid var(--border-color); box-shadow: 0 2px 8px rgba(0,0,0,0.04); gap: 10px; }}
    [data-theme="dark"] .viewer-navbar {{ background: rgba(15, 23, 42, 0.92); }} [data-theme="warm"] .viewer-navbar {{ background: rgba(253, 246, 227, 0.92); }}
    .viewer-title {{ display: flex; align-items: center; gap: 8px; font-size: 0.92rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 260px; }}
    .viewer-title-text {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .viewer-badge {{ font-size: 0.68rem; padding: 2px 7px; border-radius: 4px; background: rgba(16, 185, 129, 0.12); color: #059669; border: 1px solid rgba(16, 185, 129, 0.25); font-weight: 600; white-space: nowrap; }}
    .viewer-pagination {{ display: inline-flex; align-items: center; gap: 3px; background: rgba(0,0,0,0.04); border: 1px solid var(--border-color); padding: 3px 6px; border-radius: 6px; }}
    [data-theme="dark"] .viewer-pagination {{ background: rgba(255,255,255,0.06); }}
    .nav-btn {{ padding: 4px 7px; font-size: 0.76rem; border: 1px solid transparent; border-radius: 4px; background: transparent; color: var(--text-main); cursor: pointer; display: inline-flex; align-items: center; gap: 3px; font-weight: 500; transition: all 0.15s ease; white-space: nowrap; }}
    .nav-btn:hover {{ background: var(--page-bg); border-color: var(--border-color); color: var(--accent); }}
    .page-input-wrap {{ display: flex; align-items: center; gap: 3px; font-size: 0.78rem; color: var(--text-muted); padding: 0 4px; }}
    .page-jump-input {{ width: 44px; height: 24px; text-align: center; font-size: 0.8rem; font-weight: 700; border: 1px solid var(--border-color); border-radius: 4px; background: var(--page-bg); color: var(--text-main); outline: none; padding: 0 2px; -moz-appearance: textfield; }}
    .page-jump-input::-webkit-outer-spin-button, .page-jump-input::-webkit-inner-spin-button {{ -webkit-appearance: none; margin: 0; }}
    .page-jump-input:focus {{ border-color: var(--accent); box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2); }}
    .viewer-actions {{ display: flex; align-items: center; gap: 6px; }}
    .action-btn {{ padding: 5px 10px; font-size: 0.78rem; border-radius: 6px; border: 1px solid var(--border-color); background: var(--page-bg); color: var(--text-main); cursor: pointer; display: inline-flex; align-items: center; gap: 4px; text-decoration: none; font-weight: 500; transition: all 0.15s ease; white-space: nowrap; }}
    .action-btn:hover {{ border-color: var(--accent); color: var(--accent); }}
    .action-btn.primary {{ background: #10b981; color: #fff; border-color: #10b981; font-weight: 600; }} .action-btn.primary:hover {{ background: #059669; }}
    .doc-stage {{ flex: 1; padding: 32px 16px 80px; display: flex; justify-content: center; }}
    .doc-pages-container {{ width: 100%; max-width: 794px; display: flex; flex-direction: column; align-items: center; transition: transform 0.2s ease; transform-origin: top center; }}
    .doc-page {{ width: 100%; min-height: 1123px; background: var(--page-bg); border-radius: 2px; box-shadow: var(--page-shadow); padding: 60px 64px 60px; margin-bottom: 36px; border: 1px solid var(--border-color); font-size: 1rem; line-height: 1.8; position: relative; display: flex; flex-direction: column; justify-content: space-between; scroll-margin-top: 70px; }}
    .doc-page-content {{ flex: 1; overflow-wrap: break-word; }}
    .doc-cover-inner {{ display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 100%; padding: 140px 20px 80px; }}
    .doc-cover-brand {{ font-size: 0.72rem; letter-spacing: 2px; font-weight: 700; color: #10b981; margin-bottom: 24px; }}
    .doc-cover-title {{ font-size: 2.2rem; font-weight: 800; color: #10b981; margin-bottom: 20px; line-height: 1.3; max-width: 90%; }}
    .doc-cover-desc {{ font-size: 1.05rem; color: var(--text-muted); font-style: italic; max-width: 80%; line-height: 1.6; margin-bottom: 36px; }}
    .doc-cover-divider {{ width: 64px; height: 3px; background: #10b981; border-radius: 2px; margin: 20px 0 36px; opacity: 0.7; }}
    .doc-cover-meta {{ font-size: 0.9rem; color: var(--text-muted); line-height: 2; }}
    .doc-cover-poly-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; width: 100%; margin: 24px 0 30px; text-align: left; }}
    .doc-cover-col {{ padding: 14px 18px; border-radius: 8px; background: rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.05); display: flex; flex-direction: column; gap: 8px; }}
    [data-theme="dark"] .doc-cover-col {{ background: rgba(255,255,255,0.03); border-color: rgba(255,255,255,0.07); }}
    .doc-cover-badge {{ display: inline-block; font-size: 0.76rem; font-weight: 700; color: #0284c7; background: rgba(2, 132, 199, 0.1); padding: 2px 8px; border-radius: 4px; width: fit-content; }}
    .doc-cover-col-title {{ font-size: 1.35rem; font-weight: 800; color: #10b981; line-height: 1.35; margin: 2px 0; }}
    .doc-cover-col-desc {{ font-size: 0.9rem; color: var(--text-muted); font-style: italic; line-height: 1.5; }}
    .doc-h1 {{ font-size: 1.55rem; font-weight: 800; margin: 20px 0 14px; border-bottom: 2px solid rgba(16, 185, 129, 0.25); padding-bottom: 8px; color: var(--text-main); scroll-margin-top: 80px; }}
    .doc-h2 {{ font-size: 1.25rem; font-weight: 700; margin: 18px 0 10px; color: var(--text-main); scroll-margin-top: 80px; }}
    .doc-h3 {{ font-size: 1.05rem; font-weight: 600; margin: 14px 0 8px; color: var(--text-muted); }}
    .doc-para {{ margin-bottom: 12px; text-align: justify; word-break: break-word; }}
    .doc-link {{ color: var(--link-color); text-decoration: underline; text-underline-offset: 3px; cursor: pointer; transition: opacity 0.15s; }} .doc-link:hover {{ opacity: 0.8; }}
    .doc-toc-link {{ color: var(--text-main); text-decoration: none; display: inline-block; width: 100%; transition: color 0.15s; }} .doc-toc-link:hover {{ color: var(--accent); }}
    .doc-list-item {{ margin-bottom: 4px; font-size: 0.95rem; line-height: 1.5; }}
    .doc-sub-item {{ padding-left: 24px; color: var(--text-muted); font-size: 0.88rem; }}
    .doc-main-item {{ font-weight: 700; color: var(--text-main); margin-top: 8px; margin-bottom: 2px; }}
    .doc-quote {{ border-left: 3px solid #10b981; padding: 6px 14px; margin: 12px 0; background: rgba(16, 185, 129, 0.05); color: var(--text-muted); font-size: 0.92rem; }}
    .doc-caption {{ font-size: 0.82rem; color: var(--text-muted); text-align: center; margin: 8px 0 16px; }}
    .doc-hr {{ border: none; border-top: 1px solid var(--border-color); margin: 20px 0; }}
    .doc-table-wrap {{ width: 100%; overflow-x: auto; margin: 16px 0; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 8px; font-size: 0.9rem; }}
    th, td {{ border: 1px solid var(--border-color); padding: 8px 12px; text-align: left; vertical-align: top; }}
    th {{ background: rgba(0,0,0,0.03); font-weight: 700; }}
    table.doc-polyglot-grid {{ border-collapse: separate; border-spacing: 0; width: 100%; border: none; margin: 14px 0; }}
    table.doc-polyglot-grid th, table.doc-polyglot-grid td {{ border: none; border-bottom: 1px solid rgba(0,0,0,0.06); padding: 10px 14px; vertical-align: top; }}
    [data-theme="dark"] table.doc-polyglot-grid th, [data-theme="dark"] table.doc-polyglot-grid td {{ border-bottom: 1px solid rgba(255,255,255,0.08); }}
    table.doc-polyglot-grid th {{ background: rgba(2, 132, 199, 0.06); color: #0284c7; font-weight: 700; border-bottom: 2px solid #0284c7; font-size: 0.88rem; }}
    table.doc-polyglot-grid td {{ font-size: 0.94rem; line-height: 1.6; }}
    table.doc-polyglot-grid td:first-child {{ border-right: 1px dashed rgba(0,0,0,0.08); }}
    [data-theme="dark"] table.doc-polyglot-grid td:first-child {{ border-right: 1px dashed rgba(255,255,255,0.1); }}
    .doc-code-block {{ margin: 12px 0; border: 1px solid var(--border-color); border-left: 3px solid #10b981; border-radius: 4px; background: rgba(0,0,0,0.02); overflow: hidden; }}
    .doc-code-header {{ display: flex; justify-content: space-between; align-items: center; padding: 4px 10px; background: rgba(0,0,0,0.03); border-bottom: 1px solid var(--border-color); font-size: 0.72rem; font-weight: 700; color: var(--text-muted); }}
    .doc-code-copy {{ font-size: 0.7rem; padding: 1px 6px; border: 1px solid var(--border-color); border-radius: 3px; background: transparent; color: var(--text-muted); cursor: pointer; }}
    .doc-code-copy:hover {{ color: var(--accent); border-color: var(--accent); }}
    .doc-code-block pre {{ padding: 8px 12px; margin: 0; overflow-x: auto; font-size: 0.85rem; line-height: 1.45; color: var(--text-main); font-family: "Consolas", monospace; }}
    code.doc-inline-code {{ font-family: "Consolas", monospace; font-size: 0.88em; background: rgba(0,0,0,0.05); padding: 1px 4px; border-radius: 3px; color: #0f172a; }}
    .doc-mermaid-tabs {{ display: flex; align-items: center; gap: 4px; }}
    .doc-mermaid-tab {{ font-size: 0.7rem; padding: 2px 7px; border: 1px solid var(--border-color); border-radius: 3px; background: var(--page-bg); color: var(--text-muted); cursor: pointer; font-weight: 600; transition: all 0.15s ease; }}
    .doc-mermaid-tab.active {{ background: #10b981; color: #ffffff; border-color: #10b981; }}
    .doc-mermaid-tab:hover:not(.active) {{ color: var(--accent); border-color: var(--accent); }}
    .doc-mermaid-diagram-wrap {{ padding: 16px 12px; display: flex; justify-content: center; align-items: center; overflow-x: auto; background: rgba(255,255,255,0.7); min-height: 60px; }}
    [data-theme="dark"] .doc-mermaid-diagram-wrap {{ background: rgba(15,23,42,0.4); }}
    .doc-mermaid-diagram-wrap svg {{ max-width: 100% !important; height: auto !important; }}
    .doc-page-footer {{ position: absolute; bottom: 20px; left: 0; right: 0; font-size: 0.75rem; color: var(--text-muted); text-align: center; }}
    .doc-target-active {{ animation: targetGlow 1.8s ease; }}
    @keyframes targetGlow {{ 0% {{ background-color: rgba(16, 185, 129, 0.25); }} 100% {{ background-color: transparent; }} }}
    @media print {{ .viewer-navbar {{ display: none; }} .doc-stage {{ padding: 0; }} .doc-pages-container {{ max-width: 100%; transform: none !important; }} .doc-page {{ box-shadow: none; border: none; margin: 0; page-break-after: always; min-height: 100vh; padding: 40px; }} }}
    @media (max-width: 768px) {{
      .desktop-only {{ display: none !important; }}
      .viewer-navbar {{ flex-wrap: wrap; padding: 8px 12px; gap: 6px; justify-content: space-between; }}
      .viewer-title {{ max-width: 58%; font-size: 0.85rem; }}
      .viewer-actions {{ gap: 5px; }}
      .action-btn {{ padding: 4px 8px; font-size: 0.74rem; }}
      .viewer-pagination {{ order: 3; width: 100%; justify-content: center; margin-top: 2px; }}
      .doc-stage {{ padding: 12px 8px 60px; }}
      .doc-pages-container {{ max-width: 100%; transform: none !important; }}
      .doc-page {{ padding: 26px 14px 20px; min-height: auto; margin-bottom: 16px; border-radius: 6px; }}
      .doc-cover-inner {{ padding: 40px 10px 24px; }}
      .doc-cover-title {{ font-size: 1.5rem; }}
      .doc-cover-desc {{ font-size: 0.95rem; }}
      .doc-h1 {{ font-size: 1.3rem; margin: 14px 0 10px; }}
      .doc-h2 {{ font-size: 1.15rem; margin: 12px 0 8px; }}
      .doc-h3 {{ font-size: 1.0rem; }}
      .doc-para {{ font-size: 0.95rem; line-height: 1.65; }}
      .doc-table-wrap, .doc-code-block pre, .doc-mermaid-diagram-wrap {{ -webkit-overflow-scrolling: touch; }}
      img.doc-embedded-img {{ max-width: 100% !important; height: auto !important; }}
    }}
    @media (max-width: 480px) {{
      .nav-btn-text {{ display: none; }}
      .nav-btn {{ padding: 4px 6px; font-size: 0.8rem; }}
      .page-jump-input {{ width: 38px; height: 22px; font-size: 0.75rem; }}
      .page-input-wrap {{ font-size: 0.72rem; }}
      .doc-page {{ padding: 20px 12px 16px; }}
      .viewer-title {{ max-width: 50%; }}
    }}
  </style>
  <script src="/dashboard/vendor/mermaid.min.js"></script>
</head>
<body>
  <header class="viewer-navbar">
    <div class="viewer-title" title="{esc_fn}">
      <span>📑</span><span class="viewer-title-text">{esc_fn}</span>
      <span class="viewer-badge desktop-only">A4 审校装订</span>
    </div>
    <div class="viewer-pagination">
      <button class="nav-btn" onclick="goToPage(1)" title="快速跳转到首页 (Home)" aria-label="首页"><span>⏮️</span><span class="nav-btn-text"> 首页</span></button>
      <button class="nav-btn" onclick="prevPage()" title="上一页" aria-label="上一页">◀</button>
      <div class="page-input-wrap">
        <span class="page-label">第</span>
        <input type="number" id="page-jump-input" class="page-jump-input" min="1" max="{total_pages}" value="1" onkeydown="if(event.key==='Enter'){{goToPage(this.value);this.blur();}}" onchange="goToPage(this.value)" title="输入页码并按回车跳转">
        <span class="page-total">/ {total_pages} 页</span>
      </div>
      <button class="nav-btn" onclick="nextPage()" title="下一页" aria-label="下一页">▶</button>
      <button class="nav-btn" onclick="goToPage({total_pages})" title="快速跳转到尾页 (End)" aria-label="尾页"><span>⏭️</span><span class="nav-btn-text"> 尾页</span></button>
    </div>
    <div class="viewer-actions">
      <button class="action-btn" onclick="toggleTheme()" id="theme-btn" title="切换背景色">🎨 羊皮纸</button>
      <button class="action-btn desktop-only" onclick="adjustZoom(-0.1)" title="缩小视图">🔍 -</button>
      <button class="action-btn desktop-only" onclick="adjustZoom(0.1)" title="放大视图">🔍 +</button>
      <button class="action-btn desktop-only" onclick="window.print()" title="打印文档">🖨️ 打印</button>
      <a href="{dl_url}" download="{esc_fn}" class="action-btn primary" title="下载 .docx 原件">⬇️ 下载原件</a>
    </div>
  </header>
  <main class="doc-stage"><div class="doc-pages-container" id="pages-container">{content}</div></main>
  <script>
    let curTheme = 0; const themes = ["paper", "warm", "dark"]; const themeLabels = ["🎨 羊皮纸", "🎨 极简黑", "🎨 纯白 A4"];
    function toggleTheme() {{
      curTheme = (curTheme + 1) % themes.length;
      document.documentElement.setAttribute("data-theme", themes[curTheme]);
      document.getElementById("theme-btn").textContent = themeLabels[curTheme];
    }}
    let curZoom = 1.0;
    function adjustZoom(delta) {{
      curZoom = Math.min(1.5, Math.max(0.6, Math.round((curZoom + delta) * 10) / 10));
      document.getElementById("pages-container").style.transform = `scale(${{curZoom}})`;
    }}
    const totalPages = {total_pages};
    function goToPage(targetPage) {{
      let p = parseInt(targetPage);
      if (isNaN(p)) return;
      p = Math.max(1, Math.min(totalPages, p));
      const target = document.getElementById("page-" + p);
      if (target) {{
        target.scrollIntoView({{ behavior: "smooth", block: "start" }});
        target.classList.add("doc-target-active");
        setTimeout(() => target.classList.remove("doc-target-active"), 1400);
        const input = document.getElementById("page-jump-input");
        if (input) input.value = p;
      }}
    }}
    function prevPage() {{
      const input = document.getElementById("page-jump-input");
      const cur = parseInt(input ? input.value : 1) || 1;
      goToPage(cur - 1);
    }}
    function nextPage() {{
      const input = document.getElementById("page-jump-input");
      const cur = parseInt(input ? input.value : 1) || 1;
      goToPage(cur + 1);
    }}
    if ("IntersectionObserver" in window) {{
      const observer = new IntersectionObserver((entries) => {{
        entries.forEach(entry => {{
          if (entry.isIntersecting) {{
            const match = entry.target.id.match(/^page-(\\d+)$/);
            if (match) {{
              const curPage = parseInt(match[1]);
              const input = document.getElementById("page-jump-input");
              if (input && document.activeElement !== input) {{
                input.value = curPage;
              }}
            }}
          }}
        }});
      }}, {{ rootMargin: "-20% 0px -55% 0px", threshold: 0 }});
      document.querySelectorAll(".doc-page").forEach(page => observer.observe(page));
    }}
    document.addEventListener("keydown", function(e) {{
      if (["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) return;
      if (e.key === "Home") {{ e.preventDefault(); goToPage(1); }}
      else if (e.key === "End") {{ e.preventDefault(); goToPage(totalPages); }}
      else if (e.key === "ArrowLeft" || e.key === "PageUp") {{ e.preventDefault(); prevPage(); }}
      else if (e.key === "ArrowRight" || e.key === "PageDown") {{ e.preventDefault(); nextPage(); }}
    }});
    function switchMermaidView(btn, mode) {{
      const block = btn.closest(".doc-mermaid-block");
      if (!block) return;
      block.querySelectorAll(".doc-mermaid-tab").forEach(t => t.classList.remove("active"));
      btn.classList.add("active");
      const diag = block.querySelector(".doc-mermaid-diagram-wrap");
      const code = block.querySelector(".doc-mermaid-code-wrap");
      if (mode === "diagram") {{ diag.style.display = "flex"; code.style.display = "none"; }}
      else {{ diag.style.display = "none"; code.style.display = "block"; }}
    }}
    function copyMermaidCode(btn) {{
      const block = btn.closest(".doc-mermaid-block");
      const raw = block ? block.getAttribute("data-raw-code") : "";
      navigator.clipboard.writeText(raw || "").then(() => {{
        btn.textContent = "已复制";
        setTimeout(() => btn.textContent = "复制", 1500);
      }});
    }}
    document.addEventListener("DOMContentLoaded", function() {{
      if (window.mermaid) {{
        mermaid.initialize({{
          startOnLoad: true,
          theme: "default",
          securityLevel: "loose",
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }});
      }}
    }});
    document.addEventListener("click", function(e) {{
      const link = e.target.closest("a.doc-anchor-link, a.doc-toc-link, a[data-anchor]");
      if (!link) return;
      const anc = link.getAttribute("data-anchor") || (link.getAttribute("href") || "").replace(/^#/, "");
      if (!anc) return;
      e.preventDefault();
      const target = document.getElementById(anc) || document.querySelector(`[data-anchor="${{anc}}"]`) || document.querySelector(`[id*="${{anc}}"]`);
      if (target) {{
        target.scrollIntoView({{ behavior: "smooth", block: "start" }});
        target.classList.add("doc-target-active");
        setTimeout(() => target.classList.remove("doc-target-active"), 1800);
      }}
    }});
  </script>
</body>
</html>"""
