# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Annotator & Quote Card CSS
模块职责：提供划词高亮荧光、悬浮气泡、侧边栏笔记面板与金句卡片样式表。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_annotator_css() -> str:
    """获取划词高亮、侧边栏笔记面板与金句卡片 CSS 样式表"""
    return """/* 🖍️ 划词高亮与荧光笔样式 */
mark.er-hl {
  border-radius: 3px; padding: 1px 3px; cursor: pointer; transition: all 0.2s;
  text-decoration: underline; text-underline-offset: 3px;
}
mark.er-hl-yellow { background: rgba(245,158,11,0.28); color: inherit; text-decoration-color: #f59e0b; }
mark.er-hl-emerald { background: rgba(16,185,129,0.28); color: inherit; text-decoration-color: #10b981; }
mark.er-hl-pink { background: rgba(236,72,153,0.28); color: inherit; text-decoration-color: #ec4899; }
mark.er-hl:hover { filter: brightness(1.15); box-shadow: 0 0 8px rgba(245,158,11,0.4); }

/* 🎈 悬浮划词气泡工具栏 */
.er-floating-bar {
  position: fixed; display: none; z-index: 1000;
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 30px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.35); padding: 4px 8px; align-items: center; gap: 4px;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  transform: translate(-50%, -100%); margin-top: -10px; animation: erPop 0.15s ease-out;
}
@keyframes erPop { from { opacity: 0; transform: translate(-50%, -85%); } to { opacity: 1; transform: translate(-50%, -100%); } }
.er-fbtn {
  background: none; border: none; color: var(--text-main); font-size: 0.8rem;
  padding: 4px 8px; border-radius: 16px; cursor: pointer; display: inline-flex;
  align-items: center; gap: 4px; transition: all 0.15s; user-select: none;
}
.er-fbtn:hover { background: var(--bg-sidebar); color: var(--accent); }
.er-fdot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
.dot-yellow { background: #f59e0b; }
.dot-emerald { background: #10b981; }
.dot-pink { background: #ec4899; }
.er-fsep { width: 1px; height: 16px; background: var(--border); margin: 0 2px; }

/* 📑 侧边栏双 Tab 与笔记列表 */
.er-sidebar-tabs { display: flex; gap: 6px; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 12px; }
.er-stab-btn {
  flex: 1; background: none; border: none; font-size: 0.82rem; font-weight: 600;
  color: var(--text-dim); padding: 6px 4px; border-radius: 6px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s;
}
.er-stab-btn.active { background: var(--bg-card); color: var(--accent); }
.er-badge { background: var(--accent-glow); color: var(--accent); font-size: 0.7rem; padding: 1px 6px; border-radius: 10px; }
.er-sidebar-pane { display: none; }
.er-sidebar-pane.active { display: block; }
.er-notes-toolbar { display: flex; justify-content: space-between; margin-bottom: 12px; }
.er-btn-sm { font-size: 0.75rem; padding: 3px 8px; }
.er-btn-primary { background: var(--accent); color: #fff !important; border-color: var(--accent); }
.er-note-item {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px;
  padding: 10px 12px; margin-bottom: 10px; font-size: 0.8rem; cursor: pointer; transition: all 0.2s;
}
.er-note-item:hover { border-color: var(--accent); transform: translateY(-1px); }
.er-note-quote {
  border-left: 3px solid var(--accent); padding-left: 8px; color: var(--text-title);
  margin-bottom: 6px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.er-note-comment { background: var(--bg-sidebar); border-radius: 4px; padding: 6px 8px; color: var(--text-main); margin-bottom: 6px; }
.er-note-footer { display: flex; justify-content: space-between; align-items: center; font-size: 0.72rem; color: var(--text-dim); }
.er-note-del { color: #ef4444; background: none; border: none; cursor: pointer; font-size: 0.72rem; }
.er-empty-notes { text-align: center; color: var(--text-dim); font-size: 0.8rem; padding: 36px 12px; line-height: 1.6; }

/* 🖼️ 金句卡片与批注模态窗 */
.er-modal-backdrop {
  display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.65);
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  z-index: 1200; align-items: center; justify-content: center; padding: 20px;
}
.er-modal-backdrop.open { display: flex; }
.er-card-box, .er-note-box {
  background: var(--bg-sidebar); border: 1px solid var(--border); border-radius: 16px;
  width: 100%; max-width: 520px; padding: 24px; box-shadow: 0 16px 48px rgba(0,0,0,0.5);
  animation: erModalPop 0.2s ease-out;
}
@keyframes erModalPop { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
.er-quote-card {
  background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-sidebar) 100%);
  border: 1px solid var(--border); border-radius: 12px; padding: 32px 28px;
  position: relative; box-shadow: inset 0 1px 0 rgba(255,255,255,0.05); margin-bottom: 20px;
}
.er-card-quote-mark { font-family: Georgia, serif; font-size: 48px; color: var(--accent); line-height: 1; opacity: 0.6; margin-bottom: -10px; }
.er-card-quote-mark-end { font-family: Georgia, serif; font-size: 48px; color: var(--accent); line-height: 1; opacity: 0.6; text-align: right; margin-top: -10px; }
.er-card-quote-text {
  font-size: 1.05rem; line-height: 1.8; color: var(--text-title); text-align: justify;
  font-weight: 500; margin: 12px 0; word-break: break-word;
}
.er-card-meta { border-top: 1px dashed var(--border); padding-top: 14px; display: flex; justify-content: space-between; align-items: flex-end; }
.er-card-book-title { font-weight: 700; font-size: 0.88rem; color: var(--text-title); }
.er-card-chapter { font-size: 0.76rem; color: var(--text-dim); margin-top: 2px; }
.er-card-brand { font-size: 0.72rem; color: var(--accent); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.er-card-actions, .er-note-actions { display: flex; justify-content: flex-end; gap: 10px; }
.er-note-box-title { font-weight: 700; font-size: 1rem; color: var(--text-title); margin-bottom: 12px; }
.er-note-target-text {
  border-left: 3px solid var(--accent); padding: 6px 10px; font-size: 0.8rem;
  color: var(--text-dim); background: var(--bg-card); border-radius: 0 4px 4px 0; margin-bottom: 14px;
}
.er-note-input {
  width: 100%; box-sizing: border-box; background: var(--bg-main); border: 1px solid var(--border);
  border-radius: 8px; padding: 10px 12px; color: var(--text-main); font-size: 0.85rem;
  resize: vertical; margin-bottom: 16px; outline: none; font-family: inherit;
}
.er-note-input:focus { border-color: var(--accent); }
"""
