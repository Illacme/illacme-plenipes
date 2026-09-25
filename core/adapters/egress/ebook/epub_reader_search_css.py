# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Search CSS
模块职责：提供全书检索输入框、结果流、上下文高亮及脉冲聚焦 CSS 样式表。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_search_css() -> str:
    """获取 EPUB 全书全文检索与高亮穿透 CSS 样式表"""
    return """/* 🔍 全书全文检索面板 */
.er-search-box {
  display: flex; align-items: center; gap: 8px; background: var(--bg-card);
  border: 1px solid var(--border); border-radius: 8px; padding: 6px 10px; margin-bottom: 12px;
  transition: all 0.2s;
}
.er-search-box:focus-within { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-glow); }
.er-search-icon { color: var(--text-dim); font-size: 0.85rem; }
.er-search-input {
  flex: 1; background: none; border: none; outline: none; font-size: 0.82rem;
  color: var(--text-main); font-family: inherit;
}
.er-search-kbd {
  font-size: 0.68rem; background: var(--bg-sidebar); border: 1px solid var(--border);
  border-radius: 4px; padding: 1px 5px; color: var(--text-dim); user-select: none;
}
.er-search-meta {
  font-size: 0.72rem; color: var(--text-dim); display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 10px; padding: 0 2px;
}
.er-search-results { display: flex; flex-direction: column; gap: 8px; }
.er-search-item {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px;
  padding: 8px 10px; font-size: 0.78rem; cursor: pointer; transition: all 0.2s;
}
.er-search-item:hover { border-color: var(--accent); transform: translateY(-1px); }
.er-search-item-chap {
  font-weight: 600; font-size: 0.75rem; color: var(--accent); margin-bottom: 4px;
  display: flex; align-items: center; gap: 4px;
}
.er-search-item-snippet { color: var(--text-main); line-height: 1.45; word-break: break-word; }
.er-search-match { background: rgba(245, 158, 11, 0.4); color: inherit; border-radius: 2px; padding: 0 2px; font-weight: 600; }
.er-search-empty { text-align: center; color: var(--text-dim); font-size: 0.8rem; padding: 36px 12px; line-height: 1.6; }

/* 🌟 正文穿透聚焦脉冲动画 */
mark.er-search-focus {
  background: rgba(245, 158, 11, 0.55);
  box-shadow: 0 0 16px rgba(245, 158, 11, 0.8);
  border-radius: 3px; padding: 1px 4px; color: inherit;
  animation: erPulseGlow 1.5s infinite alternate ease-in-out;
}
@keyframes erPulseGlow {
  0% { box-shadow: 0 0 6px rgba(245, 158, 11, 0.4); }
  100% { box-shadow: 0 0 20px rgba(245, 158, 11, 0.95); }
}
"""
