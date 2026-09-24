# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader CSS
模块职责：提供 EPUB 浏览器流式解包阅读器的高质感印刷级排版、三模主题与多级目录样式。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_reader_css() -> str:
    """获取整卷 EPUB 阅读器响应式 CSS 样式表"""
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
html, body { overflow-x: hidden; max-width: 100vw; scroll-behavior: smooth; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  font-size: var(--font-size); background: var(--bg-main); color: var(--text-main);
  line-height: 1.85; -webkit-font-smoothing: antialiased;
}
.er-progress-bar { position: fixed; top: 0; left: 0; height: 3px; background: var(--accent); width: 0%; z-index: 1000; transition: width 0.1s; }
.er-topbar {
  position: fixed; top: 0; left: 0; right: 0; height: 50px;
  background: var(--bg-sidebar); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;
  padding: 0 16px; z-index: 900; transition: transform 0.25s ease;
}
.er-topbar-left { display: flex; align-items: center; gap: 10px; min-width: 0; }
.er-book-title {
  font-weight: 700; font-size: 0.88rem; color: var(--text-title);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 32vw;
}
.er-btn {
  background: var(--bg-card); border: 1px solid var(--border); color: var(--text-main);
  border-radius: 6px; padding: 5px 10px; cursor: pointer; font-size: 0.82rem; transition: all 0.2s;
  display: inline-flex; align-items: center; justify-content: center;
  touch-action: manipulation; -webkit-tap-highlight-color: transparent; user-select: none;
}
.er-btn:hover { border-color: var(--accent); color: var(--accent); }
.er-controls { display: flex; gap: 6px; align-items: center; }
.er-theme-btn {
  background: none; border: 1px solid var(--border); border-radius: 5px;
  padding: 4px 8px; cursor: pointer; font-size: 0.85rem; transition: all 0.2s;
}
.er-theme-btn.active { border-color: var(--accent); background: var(--accent-glow); }
.er-layout { display: flex; margin-top: 50px; min-height: calc(100vh - 50px); }
.er-sidebar {
  width: 310px; background: var(--bg-sidebar); border-right: 1px solid var(--border);
  position: fixed; top: 50px; bottom: 0; left: 0; overflow-y: auto; padding: 18px 12px;
  transition: transform 0.25s cubic-bezier(0.4,0,0.2,1); z-index: 800;
}
.er-sidebar.collapsed { transform: translateX(-100%); }
.er-sidebar-title {
  font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
  color: var(--text-dim); margin: 0 0 12px 8px;
}

/* 多级分级目录树核心排版 */
.er-sidebar ol, .er-sidebar ul { list-style: none; padding-left: 0; margin: 0; }
.er-sidebar > ol > li, .er-sidebar > ul > li { margin-bottom: 6px; }
.er-sidebar a {
  display: block; padding: 6px 10px; border-radius: 6px; color: var(--text-main);
  text-decoration: none; font-size: 0.82rem; line-height: 1.4; transition: all 0.15s;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.er-sidebar a:hover { background: var(--bg-card); color: var(--accent); }
.er-sidebar a.active { background: var(--accent-glow); color: var(--accent); font-weight: 700; }
.er-sidebar li > a { font-weight: 600; color: var(--text-title); }
.er-sidebar ol ol, .er-sidebar ul ul {
  padding-left: 14px; margin: 3px 0 6px; border-left: 1px solid var(--border);
}
.er-sidebar ol ol a, .er-sidebar ul ul a {
  font-size: 0.78rem; font-weight: 400; color: var(--text-main); padding: 4px 8px;
}
.er-sidebar ol ol ol, .er-sidebar ul ul ul {
  padding-left: 12px; border-left: 1px dashed var(--border);
}
.er-sidebar ol ol ol a, .er-sidebar ul ul ul a {
  font-size: 0.74rem; color: var(--text-dim);
}

.er-main {
  flex: 1; margin-left: 310px; padding: 36px 48px 100px; max-width: 920px;
  transition: margin-left 0.25s ease;
}
.er-sidebar.collapsed ~ .er-main { margin-left: auto; margin-right: auto; }
.er-backdrop {
  display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.55);
  backdrop-filter: blur(2px); z-index: 750;
}
.er-chapter-card {
  margin-bottom: 60px; padding-bottom: 40px; border-bottom: 1px dashed var(--border);
}
.er-chapter-card:last-child { border-bottom: none; }
.er-chapter-card h1 { font-size: 1.8rem; font-weight: 800; color: var(--text-title); margin: 24px 0 16px; }
.er-chapter-card h2 { font-size: 1.35rem; font-weight: 700; color: var(--text-title); margin: 24px 0 12px; }
.er-chapter-card h3 { font-size: 1.12rem; font-weight: 600; color: var(--text-title); margin: 20px 0 10px; }
.er-chapter-card p { margin-bottom: 14px; text-align: justify; word-break: break-word; }
.er-chapter-card a { color: var(--accent); text-decoration: none; border-bottom: 1px dotted var(--accent); }
.er-chapter-card a:hover { border-bottom-style: solid; }
.er-chapter-card img { max-width: 100%; height: auto; border-radius: 8px; margin: 16px auto; display: block; }
.er-chapter-card pre {
  background: var(--code-bg); border: 1px solid var(--border); border-radius: 8px;
  padding: 14px 16px; overflow-x: auto; margin: 16px 0; font-family: ui-monospace, SFMono-Regular, monospace; font-size: 0.85rem;
}
.er-chapter-card blockquote {
  border-left: 4px solid var(--accent); padding: 8px 16px; margin: 16px 0;
  background: var(--bg-card); border-radius: 0 6px 6px 0; color: var(--text-dim);
}
.er-cover-card { text-align: center; padding: 40px 0 60px; border-bottom: 2px solid var(--border); }
.er-cover-wrapper { display: inline-block; max-width: 380px; }
.er-cover-img { width: 100%; height: auto; border-radius: 12px; box-shadow: 0 12px 36px rgba(0,0,0,0.4); margin-bottom: 20px; }
.er-cover-title { font-size: 1.6rem; font-weight: 800; color: var(--text-title); margin-bottom: 8px; }
.er-cover-author { font-size: 0.95rem; color: var(--text-dim); font-weight: 500; }

@media (max-width: 900px) {
  .er-sidebar { width: 85vw; max-width: 320px; }
  .er-sidebar:not(.open) { transform: translateX(-100%); }
  .er-sidebar.open { transform: translateX(0); }
  .er-sidebar.open ~ .er-backdrop { display: block; }
  .er-main { margin-left: 0 !important; padding: 20px 16px 80px; }
  .er-book-title { max-width: 50vw; }
}
"""
