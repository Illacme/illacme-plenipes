# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Runtime JavaScript
模块职责：提供 EPUB 浏览器流式阅读器的全局相对链接拦截、平滑定位、目录联动与主题字号控制。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_reader_js() -> str:
    """获取整卷 EPUB 阅读器客户端交互 JavaScript 脚本"""
    return """(function() {
  'use strict';
  const sb = document.getElementById('er-sidebar'), btn = document.getElementById('er-toggle-sidebar'), bDrop = document.getElementById('er-backdrop');
  function closeSidebar() {
    if (sb) { sb.classList.remove('open'); sb.classList.add('collapsed'); }
    if (bDrop) bDrop.style.display = 'none';
  }
  function openSidebar() {
    if (sb) { sb.classList.add('open'); sb.classList.remove('collapsed'); }
    if (bDrop) bDrop.style.display = 'block';
  }
  function toggleSidebar() {
    const isMob = window.innerWidth <= 900;
    if (isMob) { if (sb && sb.classList.contains('open')) closeSidebar(); else openSidebar(); }
    else if (sb) { sb.classList.toggle('collapsed'); try { localStorage.setItem('er_sb_collapsed', sb.classList.contains('collapsed') ? '1' : '0'); } catch(e){} }
  }
  if (btn) btn.onclick = toggleSidebar;
  if (bDrop) bDrop.onclick = closeSidebar;
  try { if (localStorage.getItem('er_sb_collapsed') === '1' && window.innerWidth > 900 && sb) sb.classList.add('collapsed'); } catch(e){}

  const vp = document.getElementById('er-viewport');
  const bContent = document.getElementById('er-book-content');
  const fChap = document.getElementById('er-footer-chapter');
  const fPage = document.getElementById('er-footer-page');
  const prevBtn = document.getElementById('er-page-prev');
  const nextBtn = document.getElementById('er-page-next');
  const modeBtn = document.getElementById('er-mode-toggle');
  const pBar = document.getElementById('er-progress-bar');
  const chapters = document.querySelectorAll('.er-chapter-card');
  const tocLinks = document.querySelectorAll('.er-sidebar a');

  let curPage = 0, totalPages = 1;

  function getStep() {
    if (!vp || !bContent) return window.innerWidth;
    const style = window.getComputedStyle(bContent);
    const gap = parseFloat(style.columnGap) || 64;
    const padL = parseFloat(window.getComputedStyle(vp).paddingLeft) || 0;
    const padR = parseFloat(window.getComputedStyle(vp).paddingRight) || 0;
    return (vp.clientWidth - padL - padR) + gap;
  }

  function updatePagination() {
    if (document.documentElement.getAttribute('data-read-mode') !== 'paginated' || !bContent) return;
    const step = getStep();
    if (step <= 0) return;
    totalPages = Math.max(1, Math.ceil(bContent.scrollWidth / step));
    curPage = Math.max(0, Math.min(curPage, totalPages - 1));
    renderPage();
  }

  function renderPage() {
    const step = getStep();
    bContent.style.transform = `translateX(-${curPage * step}px)`;
    if (fPage) fPage.textContent = `${curPage + 1} / ${totalPages}`;
    if (pBar) pBar.style.width = `${Math.min(100, Math.max(0, ((curPage + 1) / totalPages) * 100))}%`;
    syncActiveSection(curPage * step + step * 0.4);
  }

  function nextPage() { if (curPage < totalPages - 1) { curPage++; renderPage(); } }
  function prevPage() { if (curPage > 0) { curPage--; renderPage(); } }

  if (prevBtn) prevBtn.onclick = prevPage;
  if (nextBtn) nextBtn.onclick = nextPage;

  function applyReadMode(mode) {
    document.documentElement.setAttribute('data-read-mode', mode);
    if (modeBtn) {
      modeBtn.textContent = mode === 'paginated' ? '📖 翻页' : '📜 卷轴';
      modeBtn.title = mode === 'paginated' ? '当前：左右翻页模式 (点击切换为卷轴)' : '当前：连续卷轴模式 (点击切换为翻页)';
    }
    try { localStorage.setItem('er_read_mode', mode); } catch(e){}
    if (mode === 'paginated') {
      window.scrollTo({ top: 0 });
      setTimeout(updatePagination, 60);
    } else {
      if (bContent) bContent.style.transform = '';
      if (pBar) pBar.style.width = '0%';
    }
  }

  if (modeBtn) {
    modeBtn.onclick = () => {
      const cur = document.documentElement.getAttribute('data-read-mode') || 'paginated';
      applyReadMode(cur === 'paginated' ? 'scroll' : 'paginated');
    };
  }

  function syncActiveSection(offsetOrScrollY) {
    let actId = '', actTitle = '';
    const isPag = document.documentElement.getAttribute('data-read-mode') === 'paginated';
    chapters.forEach(c => {
      const pos = isPag ? c.offsetLeft : (c.getBoundingClientRect().top + window.scrollY);
      if (pos <= offsetOrScrollY + (isPag ? 40 : 140)) {
        actId = c.id;
        const h = c.querySelector('h1, h2, h3');
        actTitle = h ? h.textContent.trim() : (c.classList.contains('er-cover-card') ? '典籍封面与扉页' : '');
      }
    });
    if (fChap && actTitle) fChap.textContent = actTitle;
    if (actId) {
      tocLinks.forEach(link => {
        const h = link.getAttribute('href') || '';
        link.classList.toggle('active', h === '#' + actId || h.endsWith(actId));
      });
    }
  }

  // 1. 全局内部链接无缝拦截器 (彻底拦截 404 Not Found)
  function navigateToTarget(rawTarget) {
    if (!rawTarget) return;
    let targetEl = null;
    let anchor = rawTarget;
    if (anchor.includes('#')) {
      const parts = anchor.split('#');
      const hashId = parts[1];
      targetEl = document.getElementById(hashId) || document.querySelector(`[id="${CSS.escape(hashId)}"]`);
      if (!targetEl && parts[0]) {
        const base = parts[0].split('/').pop().replace(/[^a-zA-Z0-9_-]/g, '_');
        targetEl = document.getElementById('er-doc-' + base);
      }
    } else {
      const base = anchor.split('/').pop().replace(/[^a-zA-Z0-9_-]/g, '_');
      targetEl = document.getElementById('er-doc-' + base);
    }

    if (targetEl) {
      const isPag = document.documentElement.getAttribute('data-read-mode') === 'paginated';
      if (isPag) {
        const step = getStep();
        if (step > 0) {
          curPage = Math.max(0, Math.min(totalPages - 1, Math.floor(targetEl.offsetLeft / step)));
          renderPage();
        }
      } else {
        const topOffset = targetEl.getBoundingClientRect().top + window.scrollY - 65;
        window.scrollTo({ top: Math.max(0, topOffset), behavior: 'smooth' });
      }
      if (window.innerWidth <= 900) closeSidebar();
    }
  }

  document.addEventListener('click', function(e) {
    const a = e.target.closest('a');
    if (!a) return;
    const href = a.getAttribute('href');
    if (!href) return;
    if (href.startsWith('http://') || href.startsWith('https://') || href.startsWith('mailto:') || href.startsWith('data:')) {
      a.setAttribute('target', '_blank');
      a.setAttribute('rel', 'noopener noreferrer');
      return;
    }
    e.preventDefault();
    navigateToTarget(href);
  });

  // 2. 视口点击与触控手势翻页
  if (vp) {
    vp.addEventListener('click', (e) => {
      if (document.documentElement.getAttribute('data-read-mode') !== 'paginated') return;
      if (e.target.closest('a, button, pre, code')) return;
      const rect = vp.getBoundingClientRect();
      const x = e.clientX - rect.left;
      if (x < rect.width * 0.28) prevPage();
      else if (x > rect.width * 0.72) nextPage();
    });
  }

  let touchStartX = 0, touchStartY = 0;
  window.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
    }
  }, { passive: true });
  window.addEventListener('touchend', (e) => {
    if (document.documentElement.getAttribute('data-read-mode') !== 'paginated') return;
    if (e.changedTouches.length === 1) {
      const dx = e.changedTouches[0].clientX - touchStartX;
      const dy = e.changedTouches[0].clientY - touchStartY;
      if (Math.abs(dx) > 42 && Math.abs(dx) > Math.abs(dy) * 1.4) {
        if (dx < 0) nextPage();
        else prevPage();
      }
    }
  }, { passive: true });

  // 3. 键盘按键监听
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    const isPag = document.documentElement.getAttribute('data-read-mode') === 'paginated';
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
      if (isPag) nextPage();
      else window.scrollBy({ top: window.innerHeight * 0.85, behavior: 'smooth' });
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      if (isPag) prevPage();
      else window.scrollBy({ top: -window.innerHeight * 0.85, behavior: 'smooth' });
    }
  });

  // 4. 连续卷轴滚动高亮监听
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (document.documentElement.getAttribute('data-read-mode') === 'paginated') return;
    if (!ticking) {
      window.requestAnimationFrame(() => {
        const h = document.documentElement.scrollHeight - window.innerHeight;
        if (pBar && h > 0) pBar.style.width = Math.min(100, Math.max(0, (window.scrollY / h) * 100)) + '%';
        syncActiveSection(window.scrollY);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  // 5. 主题与字号
  const themeBtns = document.querySelectorAll('.er-theme-btn');
  const applyTheme = (th) => {
    document.documentElement.setAttribute('data-theme', th);
    themeBtns.forEach(x => x.classList.toggle('active', x.getAttribute('data-theme') === th));
    try { localStorage.setItem('er_theme', th); } catch(e){}
  };
  themeBtns.forEach(b => { b.onclick = () => applyTheme(b.getAttribute('data-theme')); });
  try { const savedTh = localStorage.getItem('er_theme'); if (savedTh) applyTheme(savedTh); } catch(e){}

  let fs = 16;
  const inc = document.getElementById('er-font-inc'), dec = document.getElementById('er-font-dec');
  const setFs = (val) => {
    fs = val;
    document.documentElement.style.setProperty('--font-size', fs + 'px');
    try { localStorage.setItem('er_fs', fs); } catch(e){}
    setTimeout(updatePagination, 50);
  };
  try { const sfs = parseInt(localStorage.getItem('er_fs'), 10); if (sfs >= 13 && sfs <= 24) setFs(sfs); } catch(e){}
  if (inc) inc.onclick = () => setFs(Math.min(24, fs + 1));
  if (dec) dec.onclick = () => setFs(Math.max(13, fs - 1));

  window.addEventListener('resize', () => {
    if (document.documentElement.getAttribute('data-read-mode') === 'paginated') updatePagination();
  });

  // 启动模式初始化
  const savedMode = localStorage.getItem('er_read_mode') || 'paginated';
  applyReadMode(savedMode);
  setTimeout(updatePagination, 100);
})();
"""
