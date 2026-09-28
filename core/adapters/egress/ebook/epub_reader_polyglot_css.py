# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Polyglot CSS
模块职责：提供 EPUB 阅读器多语言平行对照（卷轴模式 + 翻页模式双模）印刷级分栏排版与控制条样式。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_polyglot_css() -> str:
    """获取多语对照分栏（卷轴 + 翻页双模）CSS 样式表"""
    return """
/* ============================================================
   🌍 [WebBook 对齐] EPUB 在线阅读器多语言平行对照与分栏中枢
   ============================================================ */

/* 1. 默认分栏保底 (零堆叠铁律：无论是否开启 JS，多语必定平行分栏) */
.wb-polyglot-block {
  display: flex !important; flex-direction: row !important;
  gap: 24px !important; align-items: stretch !important;
  width: 100% !important; box-sizing: border-box !important;
  margin: 1.2em 0 2.5em !important;
}
.wb-poly-item, .wb-poly-column {
  flex: 1 1 0 !important; min-width: 0 !important;
  display: flex !important; flex-direction: column !important;
  padding: 0 !important; box-sizing: border-box !important;
  position: relative !important; background: transparent !important;
  border: none !important;
}
.wb-poly-item:not(:last-child), .wb-poly-column:not(:last-child) {
  border-right: 1px dashed var(--border) !important;
  padding-right: 24px !important;
}
.wb-poly-header {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 12px; margin-bottom: 14px;
  background: var(--bg-card);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border); border-radius: 8px;
  font-weight: 700; font-size: 0.82rem; color: var(--text-title);
  user-select: none; box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}
.wb-lang-badge {
  display: inline-block; font-size: 0.68rem; font-weight: 700;
  color: var(--accent); background: var(--accent-glow); padding: 2px 8px;
  border-radius: 4px; letter-spacing: 0.5px; text-transform: uppercase;
}
.wb-poly-lang-name { font-size: 0.82rem; font-weight: 600; color: var(--text-title); }
.wb-poly-content {
  flex: 1; min-width: 0; word-break: break-word; line-height: 1.85;
  font-size: var(--font-size); color: var(--text-main);
}
.wb-poly-pending {
  background: rgba(245, 158, 11, 0.1); border: 1px dashed rgba(245, 158, 11, 0.4);
  border-radius: 6px; padding: 8px 12px; font-size: 0.8rem; color: #fbbf24; margin-bottom: 12px;
}
.wb-poly-hidden,
body .wb-poly-item.wb-poly-hidden,
body .wb-poly-column.wb-poly-hidden,
[data-read-mode="paginated"] body.wb-concordance .wb-poly-column.wb-poly-hidden,
[data-read-mode="paginated"] body.wb-concordance .wb-poly-item.wb-poly-hidden,
[data-read-mode="scroll"] body.wb-concordance .wb-poly-column.wb-poly-hidden,
[data-read-mode="scroll"] body.wb-concordance .wb-poly-item.wb-poly-hidden {
  display: none !important;
}

/* 单语言模式下隐藏对照头部与分隔线并居中展示 */
body:not(.wb-concordance) .wb-poly-header { display: none !important; }
body:not(.wb-concordance) .wb-polyglot-block { display: block !important; }
body:not(.wb-concordance) .wb-poly-item:not(.wb-poly-hidden),
body:not(.wb-concordance) .wb-poly-column:not(.wb-poly-hidden) {
  width: 100% !important; max-width: 820px !important; margin: 0 auto !important;
  border-right: none !important; padding-right: 0 !important;
}

/* 2. 顶栏嵌入式多语言控制条 (精致毛玻璃胶囊，杜绝挤占折行) */
.er-topbar-polyglot {
  display: flex; align-items: center; justify-content: center;
  flex: 1 1 auto; min-width: 0; padding: 0 6px;
}
.er-polyglot-bar {
  display: none; align-items: center; gap: 6px; flex-wrap: nowrap;
  background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border);
  padding: 3px 8px; border-radius: 20px;
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}
.er-poly-group { display: flex; align-items: center; gap: 4px; }
.er-poly-label { font-size: 0.68rem; font-weight: 700; color: var(--text-dim); text-transform: uppercase; white-space: nowrap; user-select: none; }
.er-poly-sep { color: var(--border); font-size: 0.72rem; user-select: none; margin: 0 2px; }
.er-poly-capsule { display: inline-flex; background: rgba(0, 0, 0, 0.2); padding: 2px; border-radius: 12px; border: 1px solid var(--border); gap: 2px; }
.er-poly-pitem {
  background: none; border: none; color: var(--text-dim); font-size: 0.72rem; font-weight: 600;
  padding: 2px 7px; border-radius: 10px; cursor: pointer; transition: all 0.18s; white-space: nowrap;
}
.er-poly-pitem:hover { color: var(--text-title); background: rgba(255,255,255,0.06); }
.er-poly-pitem.active { background: var(--accent) !important; color: #ffffff !important; box-shadow: 0 1px 6px rgba(16,185,129,0.35); font-weight: 700; }
.er-poly-chips { display: flex; align-items: center; gap: 4px; }
.er-poly-cchip {
  background: rgba(0, 0, 0, 0.2); border: 1px solid var(--border); color: var(--text-dim);
  font-size: 0.7rem; font-weight: 600; padding: 2px 6px; border-radius: 10px;
  cursor: pointer; display: inline-flex; align-items: center; gap: 3px; transition: all 0.18s; user-select: none; white-space: nowrap;
}
.er-poly-cchip:hover { border-color: var(--accent); color: var(--text-title); }
.er-poly-cchip.active {
  background: var(--accent-glow) !important; border-color: var(--accent) !important; color: var(--accent) !important;
  font-weight: 700; box-shadow: 0 0 6px rgba(16,185,129,0.25);
}

/* 3. 对照模式下主视口自适应拓宽与顶栏防挤占 */
body.wb-concordance .er-main,
body.wb-concordance .er-viewport {
  max-width: min(97vw, 1800px) !important; width: 100% !important;
}
body.wb-concordance .er-book-title { max-width: 170px !important; }
body.wb-concordance #er-spread-toggle,
body.wb-concordance #er-font-family,
body.wb-concordance #er-font-dec,
body.wb-concordance #er-font-inc {
  display: none !important;
}

/* 4. 📜 卷轴模式（Scroll 模式）：长卷轴连续分栏与悬浮吸顶栏头 */
[data-read-mode="scroll"] body.wb-concordance .wb-polyglot-block {
  display: flex !important; flex-direction: row !important;
  gap: 28px !important; align-items: stretch !important;
}
[data-read-mode="scroll"] body.wb-concordance .wb-poly-header {
  position: sticky !important; top: 58px !important; z-index: 25 !important;
}

/* 5. 📖 翻页模式（Paginated 模式）：左右分栏视口分页，杜绝任何折断堆叠 */
body.wb-concordance #er-spread-toggle { display: none !important; }
[data-read-mode="paginated"] body.wb-concordance .er-viewport {
  max-width: min(97vw, 1800px) !important; width: 100% !important;
  height: calc(100% - 36px) !important; padding: 8px 0 !important;
  overflow: hidden !important;
}
[data-read-mode="paginated"] body.wb-concordance .er-book-content {
  column-width: auto !important; column-count: auto !important; column-gap: 0 !important;
  display: flex !important; flex-direction: row !important;
  height: 100% !important; width: 100% !important;
  transition: transform 0.28s cubic-bezier(0.25, 1, 0.5, 1);
}
[data-read-mode="paginated"] body.wb-concordance .er-chapter-card {
  flex: 0 0 100% !important; min-width: 100% !important; max-width: 100% !important; width: 100% !important;
  height: 100% !important; overflow: hidden !important; display: flex !important; flex-direction: column !important;
  box-sizing: border-box !important; padding: 0 24px 12px !important;
  margin: 0 !important; border-bottom: none !important;
}
/* 隐藏语言分栏顶部的冗余卷大标题，释放全部垂直视口空间给正文多语对照 */
body.wb-concordance .er-chapter-card > .er-chapter-inner > h1,
body.wb-concordance .er-chapter-card .chapter-container > h1,
body.wb-concordance .er-chapter-card h1:first-child,
body.wb-concordance .wb-poly-toc-comp > h1,
body.wb-concordance nav#toc > h1 {
  display: none !important;
}
[data-read-mode="paginated"] body.wb-concordance .er-chapter-inner,
[data-read-mode="paginated"] body.wb-concordance .chapter-container {
  height: 100% !important; flex: 1 1 0 !important;
  display: flex !important; flex-direction: column !important; overflow: hidden !important;
}
[data-read-mode="paginated"] body.wb-concordance .wb-polyglot-block {
  display: flex !important; flex-direction: row !important;
  gap: 24px !important; flex: 1 1 0 !important; height: 100% !important;
  width: 100% !important; overflow: hidden !important; margin: 0 !important;
}
[data-read-mode="paginated"] body.wb-concordance .wb-poly-item,
[data-read-mode="paginated"] body.wb-concordance .wb-poly-column {
  flex: 1 1 0 !important; min-width: 0 !important; height: 100% !important;
  display: flex !important; flex-direction: column !important;
  overflow: hidden !important; box-sizing: border-box !important;
}
[data-read-mode="paginated"] body.wb-concordance .wb-poly-header {
  position: static !important; flex-shrink: 0 !important;
  margin-bottom: 8px !important; padding: 6px 10px !important;
}
[data-read-mode="paginated"] body.wb-concordance,
[data-read-mode="paginated"] body.wb-concordance .er-main,
[data-read-mode="paginated"] body.wb-concordance .er-layout,
[data-read-mode="paginated"] body.wb-concordance .er-viewport {
  overflow: hidden !important; overflow-y: hidden !important;
}
[data-read-mode="paginated"] body.wb-concordance .wb-poly-content {
  flex: 1 1 0 !important; height: 100% !important; max-height: 100% !important;
  overflow: hidden !important; overflow-y: hidden !important;
  padding-right: 4px !important; scrollbar-width: none; -ms-overflow-style: none;
  scroll-behavior: auto !important;
}
[data-read-mode="paginated"] body.wb-concordance .wb-poly-content::-webkit-scrollbar {
  display: none !important;
}
body.wb-concordance .cover-container {
  display: flex !important; align-items: center !important; justify-content: center !important;
  width: 100% !important; height: 100% !important; margin: 0 !important; padding: 0 !important;
}
body.wb-concordance .cover-container img.cover-image {
  max-width: 100% !important; max-height: calc(100vh - 140px) !important;
  object-fit: contain !important; border-radius: 8px !important;
  box-shadow: 0 8px 24px rgba(0,0,0,0.22) !important;
}
.wb-flip-slide-out-left { animation: wbFlipOutLeft 0.14s cubic-bezier(0.4, 0, 1, 1) forwards !important; }
.wb-flip-slide-in-right { animation: wbFlipInRight 0.16s cubic-bezier(0, 0, 0.2, 1) forwards !important; }
.wb-flip-slide-out-right { animation: wbFlipOutRight 0.14s cubic-bezier(0.4, 0, 1, 1) forwards !important; }
.wb-flip-slide-in-left { animation: wbFlipInLeft 0.16s cubic-bezier(0, 0, 0.2, 1) forwards !important; }
@keyframes wbFlipOutLeft { 0% { transform: translateX(0) scale(1); opacity: 1; } 100% { transform: translateX(-48px) scale(0.97); opacity: 0.15; } }
@keyframes wbFlipInRight { 0% { transform: translateX(48px) scale(0.97); opacity: 0.15; } 100% { transform: translateX(0) scale(1); opacity: 1; } }
@keyframes wbFlipOutRight { 0% { transform: translateX(0) scale(1); opacity: 1; } 100% { transform: translateX(48px) scale(0.97); opacity: 0.15; } }
@keyframes wbFlipInLeft { 0% { transform: translateX(-48px) scale(0.97); opacity: 0.15; } 100% { transform: translateX(0) scale(1); opacity: 1; } }
.wb-poly-column nav#toc ol, .wb-poly-column nav ol, .wb-poly-toc-comp ol { list-style-type: decimal !important; padding-left: 1.5em !important; margin: 0.35em 0 !important; }
.wb-poly-column nav#toc ol ol, .wb-poly-column nav ol ol, .wb-poly-toc-comp ol ol { list-style-type: decimal !important; padding-left: 1.6em !important; margin: 0.25em 0 !important; }
.wb-poly-column nav#toc li, .wb-poly-toc-comp li { margin: 0.45em 0 !important; line-height: 1.65 !important; }
.wb-poly-column nav#toc a, .wb-poly-toc-comp a { text-decoration: none !important; color: var(--accent, #0284c7) !important; }
.wb-poly-column .colophon-card { margin: 0.5em 0 !important; max-width: 100% !important; box-sizing: border-box !important; }
.wb-poly-column .colophon-grid { width: 100% !important; table-layout: fixed !important; }
.wb-poly-column .colophon-grid td.k { width: 38% !important; word-break: break-word !important; }
.wb-poly-column .colophon-grid td.v { width: 62% !important; word-break: break-all !important; }


/* 6. 跨语种段落级高亮微光联动与聚焦 */
.wb-para-target {
  cursor: pointer; transition: background 0.18s ease, box-shadow 0.18s ease;
  border-radius: 4px; padding: 2px 4px; margin: -2px -4px;
}
.wb-para-target:hover { background: rgba(255, 255, 255, 0.04); }
.wb-para-active {
  background: var(--accent-glow, rgba(16, 185, 129, 0.14)) !important;
  box-shadow: 0 0 0 1px var(--accent, #10b981), 0 2px 8px rgba(16, 185, 129, 0.2) !important;
  border-radius: 4px !important;
}

/* 7. 移动端与窄屏响应式自适应 (Responsive Concordance) */
@media (max-width: 900px) {
  .er-topbar-polyglot { display: flex !important; max-width: 55vw; }
  .er-polyglot-bar { padding: 2px 6px; gap: 4px; }
  .er-poly-label, .er-poly-sep { display: none !important; }
  .er-poly-pitem, .er-poly-cchip { font-size: 0.68rem !important; padding: 2px 5px !important; }
}

@media (max-width: 680px) {
  body.wb-concordance .er-topbar-left { gap: 4px; }
  body.wb-concordance #er-toggle-sidebar { min-width: 28px !important; padding: 0 4px !important; }
  body.wb-concordance .er-topbar-polyglot { max-width: 64vw; justify-content: center; }
  body.wb-concordance .er-poly-capsule, body.wb-concordance .er-poly-chips { gap: 1px; }
  body.wb-concordance .er-poly-pitem, body.wb-concordance .er-poly-cchip {
    font-size: 0.65rem !important; padding: 1px 4px !important; min-width: auto;
  }
  [data-read-mode="paginated"] body.wb-concordance .er-viewport { padding: 6px 4px !important; }
  [data-read-mode="paginated"] body.wb-concordance .er-chapter-card { padding: 0 8px 6px !important; }
  [data-read-mode="paginated"] body.wb-concordance .wb-polyglot-block {
    display: flex !important; flex-direction: row !important;
    gap: 8px !important; height: 100% !important;
  }
  [data-read-mode="paginated"] body.wb-concordance .wb-poly-item:not(:last-child),
  [data-read-mode="paginated"] body.wb-concordance .wb-poly-column:not(:last-child) {
    border-right: 1px dashed var(--border) !important; padding-right: 8px !important;
    border-bottom: none !important; padding-bottom: 0 !important;
  }
  [data-read-mode="paginated"] body.wb-concordance .wb-poly-header {
    padding: 3px 6px !important; margin-bottom: 4px !important; font-size: 0.72rem !important;
  }
  [data-read-mode="paginated"] body.wb-concordance .wb-poly-content {
    font-size: clamp(0.82rem, 3.2vw, 0.95rem) !important; line-height: 1.65 !important;
  }
  [data-read-mode="scroll"] body.wb-concordance .wb-polyglot-block {
    flex-direction: column !important; gap: 16px !important; margin: 0.8em 0 1.6em !important;
  }
  [data-read-mode="scroll"] body.wb-concordance .wb-poly-item:not(:last-child),
  [data-read-mode="scroll"] body.wb-concordance .wb-poly-column:not(:last-child) {
    border-right: none !important; border-bottom: 1px dashed var(--border) !important;
    padding-right: 0 !important; padding-bottom: 16px !important;
  }
  [data-read-mode="scroll"] body.wb-concordance .wb-poly-header { position: static !important; }
}
"""
