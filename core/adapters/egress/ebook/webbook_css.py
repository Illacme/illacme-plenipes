# -*- coding: utf-8 -*-
"""
Illacme Plenipes - WebBook Embedded Responsive CSS
模块职责：提供单文件离线网页书 (WebBook) 的高质感印刷级排版、三模主题与移动端触屏沉浸式样式。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_webbook_css() -> str:
    """获取整卷 WebBook 高清响应式 CSS 样式表"""
    return """:root {
  --bg-main: #0d1117; --bg-sidebar: #161b22; --bg-card: #1f242c;
  --text-main: #c9d1d9; --text-dim: #8b949e; --text-title: #f0f6fc;
  --accent: #10b981; --accent-glow: rgba(16,185,129,0.25);
  --border: #30363d; --code-bg: #161b22; --font-size: 16px;
}
[data-theme="light"] {
  --bg-main: #f8fafc; --bg-sidebar: #ffffff; --bg-card: #f1f5f9;
  --text-main: #1e293b; --text-dim: #64748b; --text-title: #0f172a;
  --accent: #059669; --accent-glow: rgba(5,150,105,0.2);
  --border: #e2e8f0; --code-bg: #f8fafc;
}
[data-theme="sepia"] {
  --bg-main: #fbf0d9; --bg-sidebar: #f4e3c1; --bg-card: #efe0bc;
  --text-main: #433422; --text-dim: #7f6e5d; --text-title: #2b1f14;
  --accent: #b45309; --accent-glow: rgba(180,83,9,0.2);
  --border: #dfcaa7; --code-bg: #f5e7cd;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { overflow-x: hidden; max-width: 100vw; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  font-size: var(--font-size); background: var(--bg-main); color: var(--text-main);
  line-height: 1.85; -webkit-font-smoothing: antialiased;
}
.wb-progress-bar { position: fixed; top: 0; left: 0; height: 3px; background: var(--accent); width: 0%; z-index: 1000; transition: width 0.1s; }
.wb-topbar {
  position: fixed; top: 0; left: 0; right: 0; height: 50px;
  background: var(--bg-sidebar); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;
  padding: 0 16px; z-index: 900; transition: transform 0.25s ease;
}
.wb-topbar-left { display: flex; align-items: center; gap: 10px; min-width: 0; }
.wb-book-title {
  font-weight: 700; font-size: 0.88rem; color: var(--text-title);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 28vw;
}
.wb-btn {
  background: var(--bg-card); border: 1px solid var(--border); color: var(--text-main);
  border-radius: 6px; padding: 5px 10px; cursor: pointer; font-size: 0.82rem; transition: all 0.2s;
  display: inline-flex; align-items: center; justify-content: center;
  touch-action: manipulation; -webkit-tap-highlight-color: transparent; user-select: none;
}
.wb-btn:hover { border-color: var(--accent); color: var(--accent); }
.wb-controls { display: flex; gap: 6px; align-items: center; }
.wb-theme-btn {
  background: none; border: 1px solid var(--border); border-radius: 5px;
  padding: 4px 8px; cursor: pointer; font-size: 0.85rem; transition: all 0.2s;
}
.wb-theme-btn.active { border-color: var(--accent); background: var(--accent-glow); }
.wb-layout { display: flex; margin-top: 50px; min-height: calc(100vh - 50px); position: relative; width: 100%; max-width: 100vw; overflow-x: hidden; }
.wb-backdrop {
  position: fixed; inset: 0; background: rgba(0, 0, 0, 0.55); backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px); z-index: 850; opacity: 0; pointer-events: none; transition: opacity 0.25s ease;
}
.wb-backdrop.active { opacity: 1; pointer-events: auto; }
.wb-sidebar {
  width: 290px; background: var(--bg-sidebar); border-right: 1px solid var(--border);
  position: fixed; top: 50px; bottom: 0; left: 0; display: flex; flex-direction: column;
  overflow: hidden; z-index: 860; transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.wb-sidebar.collapsed { transform: translateX(-100%); }
.wb-cover-box { text-align: center; padding: 14px 10px 4px; }
.wb-cover-img { max-height: 135px; border-radius: 6px; box-shadow: 0 4px 14px rgba(0,0,0,0.25); border: 1px solid var(--border); }
.wb-search-box { padding: 10px 14px; }
.wb-search-box input {
  width: 100%; padding: 7px 12px; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text-main); font-size: 0.84rem; outline: none; transition: border-color 0.2s;
}
.wb-search-box input:focus { border-color: var(--accent); }
.wb-toc { flex: 1; overflow-y: auto; padding: 4px 8px; -webkit-overflow-scrolling: touch; }
.wb-toc-row { display: flex; align-items: center; justify-content: space-between; border-radius: 6px; margin-bottom: 2px; }
.wb-toc-row:hover { background: rgba(16,185,129,0.08); }
.wb-toc-item { flex: 1; display: block; padding: 7px 9px; text-decoration: none; color: var(--text-main); font-size: 0.86rem; border-radius: 6px; transition: color 0.15s; }
.wb-toc-item:hover { color: var(--accent); }
.wb-toc-item.active { background: var(--accent); color: #fff; font-weight: 600; }
.wb-toc-item.active-ch { color: var(--accent); font-weight: 600; }
.wb-toc-toggle { background: none; border: none; color: var(--text-dim); cursor: pointer; padding: 5px 8px; font-size: 0.8rem; transition: transform 0.2s; border-radius: 4px; }
.wb-toc-group.collapsed .wb-toc-toggle { transform: rotate(-90deg); }
.wb-toc-group.collapsed .wb-toc-sub { display: none; }
.wb-toc-sub { margin-left: 10px; padding-left: 8px; border-left: 1px solid var(--border); margin-top: 1px; margin-bottom: 3px; }
.wb-toc-subitem { display: block; padding: 4px 8px; text-decoration: none; color: var(--text-dim); font-size: 0.81rem; border-radius: 4px; }
.wb-toc-subitem:hover { color: var(--accent); background: rgba(16,185,129,0.06); }
.wb-toc-subitem.active { color: var(--accent); font-weight: 600; background: rgba(16,185,129,0.12); }
.wb-toc-h3 { margin-left: 8px; font-size: 0.76rem; opacity: 0.88; }
.wb-toc-bullet { opacity: 0.5; margin-right: 4px; font-size: 0.7rem; }
.wb-toc-num { opacity: 0.65; margin-right: 4px; }
.wb-sidebar-footer { font-size: 0.72rem; color: var(--text-dim); text-align: center; padding: 10px; border-top: 1px solid var(--border); }
.wb-main {
  flex: 1 1 auto; min-width: 0; margin-left: 290px;
  width: calc(100% - 290px); max-width: calc(100% - 290px);
  padding: 30px 40px 100px; transition: margin 0.3s, width 0.3s, max-width 0.3s;
  box-sizing: border-box;
}
.wb-sidebar.collapsed ~ .wb-main { margin-left: 0; width: 100%; max-width: 100%; }
.wb-content-wrapper { max-width: 860px; width: 100%; min-width: 0; margin: 0 auto; box-sizing: border-box; transition: max-width 0.3s, opacity 0.18s ease-in-out; }
.wb-crossfade { opacity: 0; transform: translateY(4px); }
.wb-layout-wide .wb-content-wrapper { max-width: 1360px; }
.home-hero-container, [class*="hero"] { max-width: 100% !important; box-sizing: border-box !important; }
.wb-chapter { margin-bottom: 70px; padding-bottom: 40px; border-bottom: 1px solid var(--border); scroll-margin-top: 75px; }
.wb-chapter-badge { font-size: 0.75rem; text-transform: uppercase; color: var(--accent); font-weight: 700; letter-spacing: 0.05em; }
.wb-chapter-title { font-size: 1.85rem; font-weight: 800; color: var(--text-title); margin: 6px 0 20px; transition: color 0.2s; scroll-margin-top: 75px; }
.wb-chapter-body p { margin: 1em 0; }
.wb-chapter-body h1, .wb-chapter-body h2, .wb-chapter-body h3, .wb-chapter-body h4 { color: var(--text-title); margin: 1.5em 0 0.6em; scroll-margin-top: 75px; }
.wb-chapter-body blockquote { border-left: 4px solid var(--accent); padding: 0.6em 1.1em; background: var(--bg-card); color: var(--text-dim); margin: 1.3em 0; border-radius: 0 6px 6px 0; }
.wb-chapter-body code { font-family: ui-monospace, Menlo, Monaco, Consolas, monospace; background: var(--code-bg); padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
.wb-code-wrapper { position: relative; margin: 1.3em 0; }
.wb-code-wrapper pre { background: var(--code-bg); padding: 28px 16px 16px; border-radius: 6px; overflow-x: auto; border: 1px solid var(--border); margin: 0; -webkit-overflow-scrolling: touch; }
.wb-copy-btn { position: absolute; top: 6px; right: 8px; font-size: 0.72rem; padding: 2px 8px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px; color: var(--text-dim); cursor: pointer; transition: all 0.2s; user-select: none; z-index: 5; }
.wb-copy-btn:hover { color: var(--accent); border-color: var(--accent); background: var(--accent-glow); }
.wb-copy-btn.copied { color: var(--accent); border-color: var(--accent); font-weight: 700; }
.wb-table-wrapper { width: 100%; overflow-x: auto; margin: 1.4em 0; -webkit-overflow-scrolling: touch; border-radius: 6px; border: 1px solid var(--border); }
table { width: 100%; border-collapse: collapse; font-size: 0.88rem; text-align: left; }
th, td { padding: 9px 12px; border-bottom: 1px solid var(--border); }
th { background: var(--bg-card); color: var(--text-title); font-weight: 600; }
tr:nth-child(even) td { background: rgba(255,255,255,0.015); }
tr:hover td { background: rgba(16,185,129,0.04); }
.wb-chapter-body img { max-width: 100%; height: auto; display: block; margin: 1.6em auto; border-radius: 6px; border: 1px solid var(--border); }
.wb-chapter-body a { color: var(--accent); text-decoration: none; border-bottom: 1px dotted var(--accent); }
.wb-chapter-body a:hover { border-bottom-style: solid; }
.wb-chapter-footer { margin-top: 40px; padding-top: 24px; border-top: 1px dashed var(--border); }
.wb-ch-nav { display: flex; justify-content: space-between; gap: 12px; width: 100%; }
.wb-nav-card {
  flex: 1 1 0; min-width: 0; padding: 12px 16px; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 8px; text-decoration: none !important; color: var(--text-main); font-size: 0.84rem;
  display: flex; flex-direction: column; gap: 4px; transition: all 0.2s ease; box-sizing: border-box;
}
.wb-nav-card:hover { border-color: var(--accent); background: var(--accent-glow); color: var(--text-title); }
.wb-nav-card.next { text-align: right; margin-left: auto; }
.wb-nav-tag { font-size: 0.7rem; color: var(--accent); font-weight: 700; text-transform: uppercase; }
.wb-nav-name { font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.wb-toast-capsule {
  position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%) translateY(20px);
  background: rgba(16,185,129,0.92); color: #ffffff; padding: 7px 16px; border-radius: 20px;
  font-size: 0.82rem; font-weight: 600; box-shadow: 0 4px 16px rgba(0,0,0,0.3); z-index: 2000;
  opacity: 0; pointer-events: none; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.wb-toast-capsule.show { opacity: 1; transform: translateX(-50%) translateY(0); }
.colophon-card { border: 1px solid var(--border); background: var(--bg-card); padding: 22px; border-radius: 8px; margin: 20px 0; }
.colophon-grid { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.colophon-grid td { padding: 6px 8px; border-bottom: 1px dashed var(--border); }
.wb-polyglot-bar { display: flex; align-items: center; gap: 8px; }
.wb-poly-switcher-group { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.wb-primary-group, .wb-compare-group { display: flex; align-items: center; gap: 6px; }
.wb-bar-label { font-size: 0.75rem; color: var(--text-dim); font-weight: 600; white-space: nowrap; }
.wb-bar-sep { color: var(--border); font-size: 0.8rem; user-select: none; }
.wb-segmented-capsule { display: flex; background: var(--bg-card); padding: 2px; border-radius: 8px; border: 1px solid var(--border); }
.wb-primary-item { background: none; border: none; color: var(--text-dim); font-size: 0.78rem; font-weight: 600; padding: 4px 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.wb-primary-item:hover { color: var(--text-title); }
.wb-primary-item.active { background: var(--accent); color: #ffffff; box-shadow: 0 2px 6px rgba(16,185,129,0.3); }
.wb-compare-chips { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.wb-compare-chip { background: var(--bg-card); border: 1px solid var(--border); color: var(--text-dim); font-size: 0.74rem; font-weight: 600; padding: 3px 8px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 4px; transition: all 0.2s; user-select: none; }
.wb-compare-chip:hover { border-color: var(--accent); color: var(--text-title); }
.wb-compare-chip.active { background: var(--accent-glow); border-color: var(--accent); color: var(--accent); font-weight: 700; box-shadow: 0 0 8px rgba(16,185,129,0.2); }
body:not(.wb-concordance) .wb-poly-header, body:not(.wb-concordance) .wb-poly-subtitles { display: none !important; }
body:not(.wb-concordance) .wb-polyglot-block { margin: 0.6em 0; }
body:not(.wb-concordance) .wb-poly-item { width: 100%; border: none !important; background: transparent !important; padding: 0 !important; box-shadow: none !important; }
body.wb-concordance .wb-polyglot-block { display: flex !important; flex-direction: row !important; gap: 32px !important; align-items: stretch !important; margin: 1.2em 0 2.5em; padding: 0 !important; width: 100%; box-sizing: border-box; }
body.wb-concordance .wb-poly-item { flex: 1 1 0; min-width: 0 !important; display: flex; flex-direction: column; padding: 0; box-sizing: border-box; position: relative; }
body.wb-concordance .wb-poly-item:not(:last-child) { border-right: 1px dashed var(--border) !important; padding-right: 32px; }
body.wb-concordance .wb-poly-header { position: sticky; top: 48px; z-index: 15; display: flex; align-items: center; gap: 8px; padding: 8px 12px; margin-bottom: 18px; background: var(--bg-card); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid var(--border); border-radius: 8px; font-weight: 700; font-size: 0.82rem; color: var(--text-title); user-select: none; box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
body.wb-concordance .wb-lang-badge { display: inline-block; font-size: 0.68rem; font-weight: 700; color: var(--accent); background: rgba(16,185,129,0.14); padding: 2px 8px; border-radius: 4px; letter-spacing: 0.5px; }
body.wb-concordance .wb-poly-content { flex: 1; min-width: 0; word-break: break-word; line-height: 1.85; font-size: var(--font-size); color: var(--text-main); }
.wb-poly-hidden { display: none !important; }
@media (max-width: 900px) {
  html { overflow-x: hidden !important; max-width: 100vw !important; }
  body { overflow-x: hidden !important; max-width: 100vw !important; width: 100vw !important; }
  .wb-layout { max-width: 100vw; overflow-x: hidden; }
  .wb-content-wrapper { max-width: 100% !important; overflow-x: hidden; width: 100%; }
  .home-hero-container, [class*="hero"] { max-width: 100vw !important; overflow-x: hidden; box-sizing: border-box !important; padding-left: 12px !important; padding-right: 12px !important; }
  [style*="grid-template-columns"] { grid-template-columns: 1fr !important; max-width: 100% !important; }
  .wb-chapter-body pre { max-width: calc(100vw - 28px); overflow-x: auto; }
  .wb-topbar { padding: 0 8px; width: 100vw; max-width: 100vw; box-sizing: border-box; overflow: hidden; z-index: 970; }
  .wb-topbar-left { min-width: 0; flex: 1 1 auto; overflow: hidden; margin-right: 6px; gap: 6px; }
  .wb-book-title { flex: 1 1 auto; min-width: 0; max-width: 100%; font-size: 0.82rem; }
  .wb-btn { min-width: 32px; min-height: 32px; padding: 4px; }
  #wb-toggle-sidebar { min-width: 38px; min-height: 38px; font-size: 1.15rem; cursor: pointer; position: relative; z-index: 971; flex-shrink: 0; }
  .wb-controls { flex-shrink: 0; gap: 4px; }
  .wb-theme-btn { min-width: 28px; min-height: 28px; padding: 2px 3px; font-size: 0.82rem; }
  #wb-font-dec, #wb-font-inc { min-width: 28px; min-height: 28px; padding: 2px 4px; font-size: 0.78rem; font-weight: 600; }
  #wb-print-btn { display: none !important; }
  .wb-backdrop { z-index: 950 !important; }
  .wb-sidebar {
    transform: translateX(-100%); width: 84vw; max-width: 320px; box-shadow: 12px 0 35px rgba(0,0,0,0.6);
    z-index: 960 !important; top: 50px; bottom: 0;
  }
  .wb-sidebar.open { transform: translateX(0) !important; }
  .wb-main { margin-left: 0 !important; width: 100% !important; max-width: 100% !important; padding: 18px 14px calc(70px + env(safe-area-inset-bottom, 20px)); }
  .wb-ch-nav { flex-direction: column; gap: 10px; width: 100%; }
  .wb-nav-card { width: 100%; box-sizing: border-box; }
  .wb-nav-card.next { margin-left: 0; text-align: right; }
  body.wb-concordance .wb-polyglot-block { flex-direction: column !important; gap: 24px !important; }
  body.wb-concordance .wb-poly-item:not(:last-child) { border-right: none !important; border-bottom: 1px dashed var(--border) !important; padding-right: 0; padding-bottom: 24px; }
}
@media print {
  .wb-topbar, .wb-sidebar, .wb-progress-bar, .wb-controls, .wb-polyglot-bar, .wb-btn, .wb-theme-btn, .wb-search-box, .wb-copy-btn, .wb-chapter-footer, .wb-toast-capsule, .wb-backdrop { display: none !important; }
  @page { margin: 20mm 15mm; size: auto; }
  body { background: #fff !important; color: #111 !important; font-size: 11pt !important; line-height: 1.6 !important; }
  .wb-main, .wb-layout { margin: 0 !important; padding: 0 !important; width: 100% !important; }
  .wb-content-wrapper { max-width: 100% !important; }
  .wb-chapter { page-break-before: always !important; break-before: page !important; margin-bottom: 0 !important; padding-bottom: 24pt !important; border-bottom: none !important; }
  .wb-chapter:first-of-type { page-break-before: avoid !important; break-before: avoid !important; }
  h1, h2, h3, h4, .wb-chapter-header { page-break-after: avoid !important; break-after: avoid !important; color: #000 !important; }
  p, blockquote { orphans: 3 !important; widows: 3 !important; }
  blockquote { border-left: 3pt solid #666 !important; background: #f8f8f8 !important; color: #333 !important; page-break-inside: avoid !important; break-inside: avoid !important; }
  pre, code { background: #f5f5f5 !important; color: #111 !important; border: 1px solid #ddd !important; page-break-inside: avoid !important; break-inside: avoid !important; }
  img { max-width: 90% !important; max-height: 200mm !important; page-break-inside: avoid !important; break-inside: avoid !important; }
  body.wb-concordance .wb-polyglot-block { display: flex !important; gap: 14pt !important; page-break-inside: avoid !important; break-inside: avoid !important; }
  body.wb-concordance .wb-poly-header { position: static !important; box-shadow: none !important; border: 1px solid #ccc !important; }
  .colophon-card { page-break-before: always !important; break-before: page !important; background: #fafafa !important; }
  .wb-table-wrapper { border: none !important; overflow: visible !important; }
  th, td { border: 1px solid #ccc !important; color: #000 !important; }
  th { background: #f0f0f0 !important; }
}"""
