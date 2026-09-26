# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Preferences & Immersive Runtime JS
模块职责：提供沉浸全屏阅读手势中枢、Aa 排版定制抽屉、5色护眼主题切换与阅读进度自动记忆断点续读。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_prefs_js() -> str:
    """获取排版抽屉交互、沉浸全屏手势与阅读进度断点续读 JavaScript"""
    return """(function() {
  'use strict';

  // 1. 沉浸全屏模式中枢 (Immersive Reading Central)
  let isImmersive = false;
  function toggleImmersive(force) {
    isImmersive = typeof force === 'boolean' ? force : !isImmersive;
    document.body.classList.toggle('er-immersive', isImmersive);
    if (isImmersive) {
      const drawer = document.getElementById('er-prefs-drawer');
      if (drawer) drawer.classList.remove('open');
      showImmersiveTip('✨ 已开启沉浸阅读 · 轻触中央唤回');
    }
  }
  window.toggleImmersive = toggleImmersive;

  function showImmersiveTip(text) {
    if (typeof document.querySelector === 'function') {
      const old = document.querySelector('.er-imm-tip');
      if (old) old.remove();
    }
    if (typeof document.createElement !== 'function') return;
    const tip = document.createElement('div');
    tip.className = 'er-imm-tip';
    tip.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,0.68);border:1px solid rgba(255,255,255,0.18);backdrop-filter:blur(10px);color:#fff;padding:5px 14px;border-radius:20px;font-size:0.75rem;z-index:995;pointer-events:none;transition:opacity 0.4s;';
    tip.textContent = text;
    document.body.appendChild(tip);
    setTimeout(() => { tip.style.opacity = '0'; setTimeout(() => tip.remove(), 400); }, 1300);
  }

  // 视口正中央黄金区域轻触监听 (唤出/退出沉浸模式)
  const vp = document.getElementById('er-viewport');
  if (vp) {
    vp.addEventListener('click', function(e) {
      if (e.target.closest('a, button, pre, code, input, textarea, .er-prefs-drawer')) return;
      if (window.getSelection && window.getSelection().toString().trim().length > 0) return;
      const rect = vp.getBoundingClientRect();
      const relX = (e.clientX - rect.left) / rect.width;
      const relY = (e.clientY - rect.top) / rect.height;
      // 位于屏幕正中央 34% ~ 66% 水平区间，且不在极端顶部/底部
      if (relX >= 0.34 && relX <= 0.66 && relY >= 0.15 && relY <= 0.85) {
        toggleImmersive();
      }
    });
  }

  // 2. Aa 排版定制抽屉中枢 (Typography & Themes Drawer)
  const pDrawer = document.getElementById('er-prefs-drawer');
  const pBtn = document.getElementById('er-btn-prefs');
  const pClose = document.getElementById('er-prefs-close');

  function openPrefsDrawer() {
    if (!pDrawer) return;
    if (isImmersive) toggleImmersive(false);
    pDrawer.classList.add('open');
    syncPrefsUI();
  }
  function closePrefsDrawer() {
    if (pDrawer) pDrawer.classList.remove('open');
  }
  if (pBtn) pBtn.onclick = () => {
    if (pDrawer && pDrawer.classList.contains('open')) closePrefsDrawer();
    else openPrefsDrawer();
  };
  if (pClose) pClose.onclick = closePrefsDrawer;

  document.addEventListener('click', (e) => {
    if (pDrawer && pDrawer.classList.contains('open') && !pDrawer.contains(e.target) && (!pBtn || !pBtn.contains(e.target))) {
      closePrefsDrawer();
    }
  });

  // 字号与行距
  const fsLabel = document.getElementById('er-pfs-val');
  const pDec = document.getElementById('er-pfs-dec'), pInc = document.getElementById('er-pfs-inc');
  function updateFsUI(val) {
    if (fsLabel) fsLabel.textContent = val + 'px';
  }
  if (pDec) pDec.onclick = () => {
    const cur = parseInt(localStorage.getItem('er_fs') || '16', 10);
    const n = Math.max(13, cur - 1);
    document.getElementById('er-font-dec')?.click();
    updateFsUI(n);
  };
  if (pInc) pInc.onclick = () => {
    const cur = parseInt(localStorage.getItem('er_fs') || '16', 10);
    const n = Math.min(24, cur + 1);
    document.getElementById('er-font-inc')?.click();
    updateFsUI(n);
  };

  // 行距切换
  const lhBtns = document.querySelectorAll('.er-lh-btn');
  function applyLineHeight(lh) {
    document.documentElement.setAttribute('data-line-height', lh);
    lhBtns.forEach(b => b.classList.toggle('active', b.getAttribute('data-lh') === lh));
    try { localStorage.setItem('er_lh', lh); } catch(e){}
  }
  lhBtns.forEach(b => {
    b.onclick = () => applyLineHeight(b.getAttribute('data-lh'));
  });
  const savedLh = localStorage.getItem('er_lh') || 'normal';
  applyLineHeight(savedLh);

  // 5色护眼主题切换
  const swatches = document.querySelectorAll('.er-swatch-btn');
  function applyExtendedTheme(th) {
    document.documentElement.setAttribute('data-theme', th);
    swatches.forEach(s => s.classList.toggle('active', s.getAttribute('data-th') === th));
    document.querySelectorAll('.er-theme-btn').forEach(tb => tb.classList.toggle('active', tb.getAttribute('data-theme') === th));
    try { localStorage.setItem('er_theme', th); } catch(e){}
  }
  swatches.forEach(s => {
    s.onclick = () => applyExtendedTheme(s.getAttribute('data-th'));
  });

  // 同步当前 UI 状态
  function syncPrefsUI() {
    const curFs = localStorage.getItem('er_fs') || '16';
    updateFsUI(curFs);
    const curTh = document.documentElement.getAttribute('data-theme') || 'dark';
    swatches.forEach(s => s.classList.toggle('active', s.getAttribute('data-th') === curTh));
    const curLh = document.documentElement.getAttribute('data-line-height') || 'normal';
    lhBtns.forEach(b => b.classList.toggle('active', b.getAttribute('data-lh') === curLh));
  }

  // 3. 阅读进度记忆与断点续读中枢 (Reading Progress Persistence)
  const bookKey = 'er_prog_' + (document.title || 'default').replace(/[^a-zA-Z0-9_\u4e00-\u9fa5]/g, '');
  let saveTimer = null;
  function saveReadingProgress() {
    if (saveTimer) clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      try {
        const isPag = document.documentElement.getAttribute('data-read-mode') === 'paginated';
        const pageText = document.getElementById('er-footer-page')?.textContent || '1 / 1';
        const chapText = document.getElementById('er-footer-chapter')?.textContent || '';
        const curPage = parseInt(pageText.split('/')[0], 10) - 1 || 0;
        const prog = {
          mode: isPag ? 'paginated' : 'scroll',
          page: curPage,
          scrollY: window.scrollY,
          chapter: chapText,
          time: Date.now()
        };
        localStorage.setItem(bookKey, JSON.stringify(prog));
      } catch(e){}
    }, 400);
  }

  // 监听翻页与滚动更新进度
  window.addEventListener('scroll', saveReadingProgress, { passive: true });
  const pObserver = new MutationObserver(saveReadingProgress);
  const fPageEl = document.getElementById('er-footer-page');
  if (fPageEl) pObserver.observe(fPageEl, { childList: true, characterData: true, subtree: true });

  // 恢复阅读历史断点
  function tryResumeProgress() {
    try {
      const raw = localStorage.getItem(bookKey);
      if (!raw) return;
      const prog = JSON.parse(raw);
      if (!prog || (prog.page === 0 && !prog.scrollY)) return;
      // 检查是否在 30 天内
      if (Date.now() - (prog.time || 0) > 30 * 86400 * 1000) return;

      setTimeout(() => {
        if (prog.mode === 'paginated' && prog.page > 0) {
          const step = (typeof window.getStep === 'function') ? window.getStep() : window.innerWidth;
          const nextBtn = document.getElementById('er-page-next');
          // 优雅定位到页码
          for (let i = 0; i < prog.page; i++) {
            if (nextBtn) nextBtn.click();
          }
          showResumeToast(prog.chapter, prog.page + 1);
        } else if (prog.mode === 'scroll' && prog.scrollY > 100) {
          window.scrollTo({ top: prog.scrollY, behavior: 'smooth' });
          showResumeToast(prog.chapter);
        }
      }, 350);
    } catch(e){}
  }

  function showResumeToast(chapName, pageNum) {
    const toast = document.createElement('div');
    toast.className = 'er-resume-toast';
    const desc = pageNum ? `已恢复上次阅读：第 ${pageNum} 页` : (chapName ? `已恢复至：${chapName}` : '已恢复上次阅读进度');
    toast.innerHTML = `<span>🔖 ${desc}</span><button type="button" class="er-resume-btn" onclick="window.scrollTo(0,0); document.querySelector('.er-resume-toast')?.remove();">从头开始</button>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2600);
  }

  // 键盘快捷键扩展 (i: 沉浸模式, p: 打开排版)
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'i' || e.key === 'I') toggleImmersive();
    else if (e.key === 'p' || e.key === 'P') openPrefsDrawer();
    else if (e.key === 'Escape') {
      if (pDrawer && pDrawer.classList.contains('open')) closePrefsDrawer();
      else if (isImmersive) toggleImmersive(false);
    }
  });

  // 启动时延迟尝试恢复
  setTimeout(tryResumeProgress, 250);
})();
"""
