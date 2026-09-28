# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Reader Pager & Quick Jump CSS
模块职责：提供 EPUB 阅读器底部翻页控制器、首页/尾页快捷按钮、微光跳转输入框样式。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_pager_css() -> str:
    """获取底部页码导航与快捷跳转组件 CSS 样式表"""
    return """
/* ============================================================
   📖 EPUB 阅读器底部翻页快捷跳转中枢 (Pager & Quick Jump)
   ============================================================ */

.er-footer-nav {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  user-select: none;
}

.er-footer-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border, rgba(255, 255, 255, 0.12));
  color: var(--text-dim, #94a3b8);
  border-radius: 5px;
  padding: 3px 8px;
  font-size: 0.72rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  line-height: 1;
  transition: all 0.16s ease;
}

.er-footer-btn:hover {
  color: var(--text-title, #ffffff);
  background: rgba(255, 255, 255, 0.12);
  border-color: var(--accent, #00f2fe);
  box-shadow: 0 0 8px var(--accent-glow, rgba(0, 242, 254, 0.25));
}

.er-footer-btn:active {
  transform: scale(0.96);
}

.er-footer-btn-nav {
  padding: 3px 6px;
  font-size: 0.7rem;
}

.er-footer-page-box {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  padding: 2px 8px;
  border-radius: 5px;
  border: 1px dashed transparent;
  transition: all 0.16s ease;
  position: relative;
}

.er-footer-page-box:hover {
  border-color: var(--accent, #00f2fe);
  background: rgba(0, 242, 254, 0.08);
}

.er-footer-page-box:hover .er-footer-page-text {
  color: var(--accent, #00f2fe);
}

.er-footer-page-text {
  font-variant-numeric: tabular-nums;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.78rem;
  color: var(--text-dim, #94a3b8);
  letter-spacing: 0.5px;
}

.er-footer-page-jump {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.er-page-jump-input {
  width: 48px;
  height: 22px;
  padding: 0 4px;
  text-align: center;
  border-radius: 4px;
  border: 1px solid var(--accent, #00f2fe);
  background: var(--bg-card, #0f172a);
  color: var(--text-title, #ffffff);
  font-size: 0.76rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  outline: none;
  box-shadow: 0 0 8px var(--accent-glow, rgba(0, 242, 254, 0.3));
}

.er-page-jump-input::-webkit-inner-spin-button,
.er-page-jump-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.er-page-jump-total {
  font-size: 0.76rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  color: var(--text-dim, #94a3b8);
}

@media (max-width: 680px) {
  .er-footer-btn-edge span.lbl { display: none !important; }
  .er-footer-btn { padding: 3px 5px; }
  .er-footer-chapter { max-width: 35% !important; }
}
"""
