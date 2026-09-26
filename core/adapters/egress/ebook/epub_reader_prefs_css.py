# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Preferences & Immersive CSS
模块职责：提供沉浸全屏阅读手势过渡、Aa 排版定制抽屉、5色护眼主题与断点续读提示样式。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_prefs_css() -> str:
    """获取排版抽屉、沉浸阅读及五重主题扩展 CSS 样式"""
    return """/* 🌿 五色护眼底色扩展 (Mint 薄荷绿 & OLED 深空纯黑) */
[data-theme="mint"] {
  --bg-main: #eaf3eb; --bg-sidebar: #dbebdc; --bg-card: #d2e5d4;
  --text-main: #183321; --text-dim: #45694e; --text-title: #0e2415;
  --accent: #15803d; --accent-glow: rgba(21,128,61,0.22);
  --border: #c3d9c5; --code-bg: #dbebdc;
}
[data-theme="oled"] {
  --bg-main: #000000; --bg-sidebar: #050505; --bg-card: #0e0e0e;
  --text-main: #d1d5db; --text-dim: #6b7280; --text-title: #f9fafb;
  --accent: #10b981; --accent-glow: rgba(16,185,129,0.32);
  --border: #222222; --code-bg: #0a0a0a;
}

/* 📏 行距三档控制 */
:root { --line-height: 1.85; }
[data-line-height="compact"] { --line-height: 1.52; }
[data-line-height="normal"] { --line-height: 1.85; }
[data-line-height="relaxed"] { --line-height: 2.22; }
body, .er-chapter-card { line-height: var(--line-height); }

/* ✨ 沉浸全屏模式 (Immersive Reading View) */
body.er-immersive .er-topbar {
  transform: translateY(-100%) !important;
  pointer-events: none;
}
body.er-immersive .er-paginated-footer {
  transform: translateY(100%) !important;
  pointer-events: none;
}
body.er-immersive .er-page-arrow {
  opacity: 0 !important;
  pointer-events: none !important;
}
body.er-immersive .er-progress-bar {
  top: 0;
  height: 2px;
  opacity: 0.65;
}
body.er-immersive .er-viewport {
  height: 100vh !important;
  padding-top: 16px !important;
  padding-bottom: 16px !important;
}

/* 🎨 排版定制抽屉 (Aa Typography & Theme Drawer) */
.er-prefs-drawer {
  position: fixed; bottom: 0; left: 0; right: 0;
  max-width: 500px; margin: 0 auto;
  background: var(--bg-sidebar);
  border: 1px solid var(--border); border-bottom: none;
  border-radius: 18px 18px 0 0;
  padding: 16px 20px 22px;
  box-shadow: 0 -12px 40px rgba(0, 0, 0, 0.45);
  z-index: 980;
  transform: translateY(105%);
  transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
  color: var(--text-main);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
}
.er-prefs-drawer.open {
  transform: translateY(0);
}
.er-prefs-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 14px; padding-bottom: 8px; border-bottom: 1px solid var(--border);
}
.er-prefs-title {
  font-size: 0.92rem; font-weight: 700; color: var(--text-title);
  display: flex; align-items: center; gap: 6px;
}
.er-prefs-close {
  background: none; border: none; font-size: 1.25rem; color: var(--text-dim);
  cursor: pointer; padding: 2px 6px; line-height: 1; border-radius: 4px;
}
.er-prefs-close:hover { color: var(--text-title); }

.er-prefs-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px; gap: 10px; font-size: 0.82rem;
}
.er-prefs-label {
  color: var(--text-dim); font-size: 0.78rem; font-weight: 600;
  white-space: nowrap; min-width: 60px;
}
.er-prefs-group {
  display: inline-flex; align-items: center; gap: 4px;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 8px; padding: 2px;
}
.er-pbtn {
  background: transparent; border: none; color: var(--text-main);
  padding: 4px 10px; font-size: 0.76rem; font-weight: 500;
  border-radius: 6px; cursor: pointer; transition: all 0.15s;
  white-space: nowrap; user-select: none;
}
.er-pbtn.active {
  background: var(--accent); color: #ffffff !important; font-weight: 700;
}
.er-pbtn:hover:not(.active) {
  background: rgba(255, 255, 255, 0.06);
}

/* 🎨 主题色盘圆形选择器 */
.er-theme-swatches {
  display: flex; gap: 8px; align-items: center;
}
.er-swatch-btn {
  width: 28px; height: 28px; border-radius: 50%;
  border: 2px solid transparent; cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 0.72rem; transition: transform 0.15s, border-color 0.15s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.18);
}
.er-swatch-btn:hover { transform: scale(1.1); }
.er-swatch-btn.active {
  border-color: var(--accent); transform: scale(1.12);
  box-shadow: 0 0 10px var(--accent-glow);
}
.swatch-dark { background: #0d1117; color: #f0f6fc; }
.swatch-light { background: #f8fafc; color: #1e293b; border: 1px solid #cbd5e1; }
.swatch-sepia { background: #fbf0d9; color: #433422; border: 1px solid #dfcaa7; }
.swatch-mint { background: #eaf3eb; color: #183321; border: 1px solid #c3d9c5; }
.swatch-oled { background: #000000; color: #ffffff; border: 1px solid #333333; }

/* 🔖 断点续读微胶囊 Toast */
.er-resume-toast {
  position: fixed; top: 62px; left: 50%; transform: translateX(-50%);
  background: var(--bg-card); border: 1px solid var(--accent);
  box-shadow: 0 8px 24px rgba(0,0,0,0.38), 0 0 12px var(--accent-glow);
  color: var(--text-title); padding: 6px 14px; border-radius: 20px;
  font-size: 0.78rem; font-weight: 500; display: inline-flex;
  align-items: center; gap: 10px; z-index: 955;
  animation: erResumeAnim 2.2s ease forwards;
  white-space: nowrap; max-width: 92vw;
}
.er-resume-btn {
  background: none; border: 1px solid var(--border); color: var(--accent);
  padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; cursor: pointer;
}
.er-resume-btn:hover { background: var(--accent); color: #fff; }
@keyframes erResumeAnim {
  0% { opacity: 0; transform: translateX(-50%) translateY(-10px); }
  12% { opacity: 1; transform: translateX(-50%) translateY(0); }
  85% { opacity: 1; transform: translateX(-50%) translateY(0); }
  100% { opacity: 0; transform: translateX(-50%) translateY(-6px); pointer-events: none; }
}

/* 💡 沉浸模式下鼠标移至顶部区域平滑唤出顶栏供读者操作 */
body.er-immersive.er-topbar-hover .er-topbar,
body.er-immersive .er-topbar:hover {
  transform: translateY(0) !important;
  pointer-events: auto !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
}
"""
