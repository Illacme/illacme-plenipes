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
html, body { overflow-x: hidden; max-width: 100vw; width: 100%; scroll-behavior: smooth; }
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
  white-space: nowrap !important; flex-shrink: 0;
}
.er-btn:hover { border-color: var(--accent); color: var(--accent); }
.er-controls { display: flex; gap: 6px; align-items: center; }
.er-theme-btn {
  background: none; border: 1px solid var(--border); border-radius: 5px;
  padding: 4px 8px; cursor: pointer; font-size: 0.85rem; transition: all 0.2s;
  white-space: nowrap !important; flex-shrink: 0;
}
.er-theme-btn.active { border-color: var(--accent); background: var(--accent-glow); }
.er-layout { display: flex; margin-top: 50px; min-height: calc(100vh - 50px); max-width: 100vw; overflow-x: hidden; }
.er-sidebar {
  width: 310px; background: var(--bg-sidebar); border-right: 1px solid var(--border);
  position: fixed; top: 50px; bottom: 0; left: 0; overflow-y: auto; padding: 18px 12px;
  transition: transform 0.25s cubic-bezier(0.4,0,0.2,1); z-index: 800;
}
.er-sidebar.collapsed { transform: translateX(-100%); }
.er-sidebar-title { font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-dim); margin: 0 0 12px 8px; }
.er-sidebar ol, .er-sidebar ul { list-style: none; padding-left: 0; margin: 0; }
.er-sidebar > ol > li, .er-sidebar > ul > li { margin-bottom: 6px; }
.er-sidebar a { display: block; padding: 6px 10px; border-radius: 6px; color: var(--text-main); text-decoration: none; font-size: 0.82rem; line-height: 1.4; transition: all 0.15s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.er-sidebar a:hover { background: var(--bg-card); color: var(--accent); }
.er-sidebar a.active { background: var(--accent-glow); color: var(--accent); font-weight: 700; }
.er-sidebar li > a { font-weight: 600; color: var(--text-title); }
.er-sidebar ol ol, .er-sidebar ul ul { padding-left: 14px; margin: 3px 0 6px; border-left: 1px solid var(--border); }
.er-sidebar ol ol a, .er-sidebar ul ul a { font-size: 0.78rem; font-weight: 400; color: var(--text-main); padding: 4px 8px; }
.er-sidebar ol ol ol, .er-sidebar ul ul ul { padding-left: 12px; border-left: 1px dashed var(--border); }
.er-sidebar ol ol ol a, .er-sidebar ul ul ol a { font-size: 0.74rem; color: var(--text-dim); }

.er-mode-btn { font-weight: 600; color: var(--accent); border-color: var(--accent); }
.er-viewport, .er-book-content { width: 100%; max-width: 100%; min-width: 0 !important; box-sizing: border-box; }
.er-viewport { position: relative; }
.er-page-arrow, .er-paginated-footer { display: none; }

.er-main {
  flex: 1; margin-left: 310px; padding: 36px 48px 100px; max-width: 920px;
  min-width: 0 !important; width: 100%; box-sizing: border-box;
  transition: margin-left 0.25s ease;
}
.er-sidebar.collapsed ~ .er-main { margin-left: auto; margin-right: auto; }
.er-backdrop {
  display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.55);
  backdrop-filter: blur(2px); z-index: 750;
}
.er-chapter-card {
  margin-bottom: 60px; padding-bottom: 40px; border-bottom: 1px dashed var(--border);
  min-width: 0 !important; max-width: 100% !important; box-sizing: border-box;
  overflow-wrap: break-word; word-break: break-word;
}
.er-chapter-card * { max-width: 100%; box-sizing: border-box; }
.er-chapter-card:last-child { border-bottom: none; }
.er-chapter-card h1 { font-size: 1.8rem; font-weight: 800; color: var(--text-title); margin: 24px 0 16px; line-height: 1.35; }
.er-chapter-card h2 { font-size: 1.35rem; font-weight: 700; color: var(--text-title); margin: 24px 0 12px; line-height: 1.4; }
.er-chapter-card h3 { font-size: 1.12rem; font-weight: 600; color: var(--text-title); margin: 20px 0 10px; }
.er-chapter-card p { margin-bottom: 14px; text-align: justify; word-break: break-word; }
.er-chapter-card a { color: var(--accent); text-decoration: none; border-bottom: 1px dotted var(--accent); }
.er-chapter-card a:hover { border-bottom-style: solid; }
.er-chapter-card img, .cover-image, .er-cover-img { max-width: 100% !important; height: auto !important; border-radius: 8px; margin: 16px auto; display: block; object-fit: contain; }
.er-chapter-card pre, .codehilite, .codehilite pre {
  background: var(--code-bg); border: 1px solid var(--border); border-radius: 8px;
  padding: 14px 16px; overflow-x: auto; margin: 16px 0; font-family: ui-monospace, SFMono-Regular, monospace; font-size: 0.85rem; max-width: 100% !important;
}
.er-chapter-card table { display: block; overflow-x: auto; max-width: 100%; width: 100%; border-collapse: collapse; margin: 16px 0; }
.er-chapter-card blockquote {
  border-left: 4px solid var(--accent); padding: 8px 16px; margin: 16px 0;
  background: var(--bg-card); border-radius: 0 6px 6px 0; color: var(--text-dim);
}
.er-cover-card { text-align: center; padding: 40px 0 60px; border-bottom: 2px solid var(--border); }
.er-cover-wrapper { display: inline-block; max-width: 380px; width: 100%; }
.er-cover-img { width: 100%; height: auto; border-radius: 12px; box-shadow: 0 12px 36px rgba(0,0,0,0.4); margin-bottom: 20px; }
.er-cover-title { font-size: 1.6rem; font-weight: 800; color: var(--text-title); margin-bottom: 8px; }
.er-cover-author { font-size: 0.95rem; color: var(--text-dim); font-weight: 500; }

/* 🎯 链接点击与精准跳转呼吸脉冲反馈 */
.er-chapter-card a:active, .er-sidebar a:active { transform: scale(0.97); opacity: 0.85; transition: transform 0.1s; }
.er-jump-target {
  animation: erTargetPulse 1.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
  outline: 2px solid var(--accent); outline-offset: 4px; border-radius: 6px;
}
@keyframes erTargetPulse {
  0% { background: var(--accent-glow); box-shadow: 0 0 20px var(--accent-glow); }
  60% { background: var(--accent-glow); }
  100% { background: transparent; outline-color: transparent; }
}

/* 🎯 顶部跳转感知胶囊 Toast */
.er-jump-toast {
  position: fixed; top: 60px; left: 50%; transform: translateX(-50%);
  background: var(--bg-card); border: 1px solid var(--accent);
  box-shadow: 0 8px 24px rgba(0,0,0,0.35), 0 0 12px var(--accent-glow);
  color: var(--text-title); padding: 6px 16px; border-radius: 20px;
  font-size: 0.82rem; font-weight: 500; display: inline-flex; align-items: center; gap: 8px;
  z-index: 950; pointer-events: none; animation: erToastAnim 1.6s ease forwards;
  white-space: nowrap; max-width: 90vw; overflow: hidden; text-overflow: ellipsis;
}
.er-jump-toast b { color: var(--accent); font-weight: 700; }
@keyframes erToastAnim {
  0% { opacity: 0; transform: translateX(-50%) translateY(-10px) scale(0.9); }
  15% { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
  80% { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
  100% { opacity: 0; transform: translateX(-50%) translateY(-6px) scale(0.95); }
}

/* 📖 页面点击翻页方向性微波纹反馈 */
.er-turn-cue {
  position: fixed; pointer-events: none; z-index: 999;
  transform: translate(-50%, -50%) scale(0.85);
  background: rgba(16, 185, 129, 0.22); border: 1px solid var(--accent);
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  color: var(--text-title); padding: 6px 14px; border-radius: 20px;
  font-size: 0.8rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;
  animation: erCueFade 0.38s ease-out forwards;
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}
.er-turn-cue .er-cue-icon { font-size: 1.2rem; line-height: 1; color: var(--accent); }
@keyframes erCueFade {
  0% { opacity: 0; transform: translate(-50%, -50%) scale(0.7); }
  35% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(1.08); }
}

/* 🔤 印刷级排版字体库切换 */
[data-font="sans"] body, [data-font="sans"] .er-main {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}
[data-font="serif"] body, [data-font="serif"] .er-main {
  font-family: "Songti SC", "Source Han Serif SC", "Noto Serif CJK SC", SimSun, "STSong", "Georgia", serif;
}
[data-font="kai"] body, [data-font="kai"] .er-main {
  font-family: "Kaiti SC", "STKaiti", "KaiTi", "BiauKai", "FZKai-Z03S", serif;
}

/* 📖 仿真左右分页模式核心样式 */
html[data-read-mode="paginated"], body[data-read-mode="paginated"] { height: 100vh; overflow: hidden; }
[data-read-mode="paginated"] .er-layout { height: calc(100vh - 50px); margin-top: 50px; overflow: hidden; min-height: 0; }
[data-read-mode="paginated"] .er-main {
  height: 100%; padding: 0; margin-left: 310px; display: flex; flex-direction: column;
  overflow: hidden; position: relative; max-width: none;
}
[data-read-mode="paginated"] .er-sidebar.collapsed ~ .er-main { margin-left: 0; }
[data-read-mode="paginated"] .er-viewport {
  flex: 1; height: calc(100% - 36px); overflow: hidden; position: relative; width: 100%;
  padding: 14px 54px; box-sizing: border-box; cursor: pointer; max-width: 1440px; margin: 0 auto;
}

/* 📑 宽屏仿真双页对开与书脊阴影折痕 (仅在翻页仿真模式下呈现) */
[data-read-mode="paginated"] .er-viewport.spread-active::after {
  content: ""; position: absolute; top: 0; bottom: 0; left: 50%; width: 44px;
  transform: translateX(-50%); pointer-events: none; z-index: 550;
  background: linear-gradient(to right, rgba(0,0,0,0) 0%, rgba(0,0,0,0.18) 50%, rgba(0,0,0,0) 100%);
}
[data-read-mode="paginated"][data-theme="sepia"] .er-viewport.spread-active::after {
  background: linear-gradient(to right, rgba(67,52,34,0) 0%, rgba(67,52,34,0.22) 50%, rgba(67,52,34,0) 100%);
}
[data-read-mode="paginated"][data-theme="light"] .er-viewport.spread-active::after {
  background: linear-gradient(to right, rgba(0,0,0,0) 0%, rgba(0,0,0,0.08) 50%, rgba(0,0,0,0) 100%);
}
[data-read-mode="scroll"] .er-viewport::after { display: none !important; }

[data-read-mode="paginated"] .er-book-content {
  height: 100%;
  column-width: var(--page-width, 760px);
  column-gap: var(--page-gap, 64px);
  column-fill: auto;
  box-sizing: border-box;
  transition: transform 0.28s cubic-bezier(0.25, 1, 0.5, 1);
  will-change: transform;
}
[data-read-mode="paginated"] .er-viewport.spread-active .er-book-content {
  column-count: 2;
  column-width: auto;
  column-gap: 72px;
}
[data-read-mode="paginated"] .er-chapter-card { break-inside: auto; margin-bottom: 0; padding-bottom: 20px; }
[data-read-mode="paginated"] .er-chapter-card + .er-chapter-card { break-before: column; }
[data-read-mode="paginated"] .er-cover-card { padding: 0; border-bottom: none; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; box-sizing: border-box; }
[data-read-mode="paginated"] .er-cover-card img, [data-read-mode="paginated"] img.cover-image, [data-read-mode="paginated"] .er-cover-img { max-height: calc(100vh - 160px); width: auto; max-width: 95%; object-fit: contain; margin: auto; display: block; border-radius: 8px; }
[data-read-mode="paginated"] .er-cover-wrapper { max-width: 90%; margin: auto; }
[data-read-mode="paginated"] .er-cover-title { font-size: 1.35rem; }
[data-read-mode="paginated"] .er-chapter-card img { max-height: calc(100vh - 160px); width: auto; max-width: 100%; object-fit: contain; }
[data-read-mode="paginated"] .er-chapter-card h1, [data-read-mode="paginated"] .er-chapter-card h2 { break-after: avoid-column; }
[data-read-mode="paginated"] .er-chapter-card pre, [data-read-mode="paginated"] .er-chapter-card blockquote { break-inside: avoid-column; }
[data-read-mode="paginated"] .er-page-arrow {
  display: flex; position: absolute; top: calc(50% - 18px); transform: translateY(-50%);
  z-index: 600; width: 40px; height: 72px; background: rgba(0,0,0,0.25); backdrop-filter: blur(8px);
  border: 1px solid var(--border); border-radius: 8px; font-size: 28px; line-height: 1;
  color: var(--text-dim); align-items: center; justify-content: center; cursor: pointer;
  opacity: 0.35; transition: all 0.2s; user-select: none;
}
[data-read-mode="paginated"] .er-page-arrow:hover {
  opacity: 1; color: var(--accent); background: var(--bg-card); border-color: var(--accent);
}
[data-read-mode="paginated"] .er-page-prev { left: 8px; }
[data-read-mode="paginated"] .er-page-next { right: 8px; }
[data-read-mode="paginated"] .er-paginated-footer {
  height: 36px; background: var(--bg-sidebar); border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center; padding: 0 20px;
  font-size: 0.78rem; color: var(--text-dim); user-select: none; z-index: 650;
}
[data-read-mode="paginated"] .er-footer-chapter {
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 60%;
  color: var(--text-title); font-weight: 600;
}
[data-read-mode="paginated"] .er-footer-page {
  font-variant-numeric: tabular-nums; font-family: ui-monospace, SFMono-Regular, monospace;
}

@media (max-width: 900px) {
  .er-sidebar { width: 85vw; max-width: 320px; }
  .er-sidebar:not(.open) { transform: translateX(-100%); }
  .er-sidebar.open { transform: translateX(0); }
  .er-sidebar.open ~ .er-backdrop { display: block; }
  .er-main { margin-left: 0 !important; padding: 20px 16px 80px; }
  .er-book-title { max-width: 35vw; }
  [data-read-mode="paginated"] .er-main { margin-left: 0 !important; padding: 0; }
  [data-read-mode="paginated"] .er-viewport { padding: 12px 14px; }
  [data-read-mode="paginated"] .er-page-arrow { display: none; }
}

@media (max-width: 680px) {
  .er-topbar { padding: 0 8px; height: 44px; }
  .er-topbar-left { gap: 6px; }
  .er-book-title, #er-spread-toggle { display: none !important; }
  .er-btn-text { display: none !important; }
  .er-controls { gap: 4px; }
  .er-btn, .er-theme-btn {
    padding: 0 6px !important; min-width: 32px !important; height: 32px !important;
    font-size: 0.82rem !important; border-radius: 6px !important;
  }
  .er-theme-btn { min-width: 28px !important; height: 28px !important; font-size: 0.74rem !important; }
  .er-layout { margin-top: 44px; min-height: calc(100vh - 44px); }
  .er-sidebar { top: 44px; }
  .er-main { padding: 16px 12px 60px !important; margin: 0 !important; max-width: 100vw !important; width: 100% !important; }
  .er-cover-card { padding: 16px 0 24px !important; }
  .cover-image, .er-cover-img { max-height: 65vh !important; }
  .er-chapter-card h1, .hero-main-title { font-size: 1.55rem !important; line-height: 1.3 !important; }
  .er-chapter-card h2 { font-size: 1.25rem !important; }
  .hero-subtext { font-size: 0.95rem !important; }
  .stats-matrix, .features-grid, [style*="grid-template-columns"] { grid-template-columns: 1fr !important; gap: 12px !important; }
  .hero-cta-group { flex-direction: column !important; align-items: stretch !important; gap: 8px !important; }
  .hero-cta-group a, .hero-cta-group button { justify-content: center !important; width: 100% !important; }
}
"""
