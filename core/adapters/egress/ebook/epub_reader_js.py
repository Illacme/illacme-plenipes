# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Runtime JavaScript
模块职责：提供 EPUB 浏览器流式阅读器的全局相对链接拦截、首视口段落锚定重排、目录联动与排版控制。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_reader_js() -> str:
    """获取整卷 EPUB 阅读器客户端交互 JavaScript 脚本"""
    return """(function() {
  'use strict';
  const sb = document.getElementById('er-sidebar'), btn = document.getElementById('er-toggle-sidebar'), bDrop = document.getElementById('er-backdrop');
  const vp = document.getElementById('er-viewport'), bContent = document.getElementById('er-book-content');
  const fChap = document.getElementById('er-footer-chapter'), fPage = document.getElementById('er-footer-page'), prevBtn = document.getElementById('er-page-prev'), nextBtn = document.getElementById('er-page-next');
  const modeBtn = document.getElementById('er-mode-toggle'), spreadBtn = document.getElementById('er-spread-toggle'), fontBtn = document.getElementById('er-font-family'), pBar = document.getElementById('er-progress-bar');
  let curPage = 0, totalPages = 1, spreadMode = localStorage.getItem('er_spread_mode') || 'auto', isSidebarAnimating = false;

  const triggerLayoutSync = () => { if (!isSidebarAnimating && document.documentElement.getAttribute('data-read-mode') === 'paginated') updatePagination(totalPages > 1 ? (curPage / (totalPages - 1)) : 0); };
  const setSidebar = (open) => {
    isSidebarAnimating = true; const ratio = totalPages > 1 ? (curPage / (totalPages - 1)) : 0;
    if (sb) { sb.classList.toggle('open', open); sb.classList.toggle('collapsed', !open); }
    if (bDrop) bDrop.style.display = open ? 'block' : 'none';
    setTimeout(() => { isSidebarAnimating = false; if (document.documentElement.getAttribute('data-read-mode') === 'paginated') updatePagination(ratio); }, 280);
  };
  const closeSidebar = () => setSidebar(false);
  function toggleSidebar() {
    if (window.innerWidth <= 900) setSidebar(!sb.classList.contains('open'));
    else if (sb) {
      isSidebarAnimating = true; const ratio = totalPages > 1 ? (curPage / (totalPages - 1)) : 0;
      sb.classList.toggle('collapsed');
      try { localStorage.setItem('er_sb_collapsed', sb.classList.contains('collapsed') ? '1' : '0'); } catch(e){}
      setTimeout(() => {
        isSidebarAnimating = false;
        if (document.documentElement.getAttribute('data-read-mode') === 'paginated') updatePagination(ratio);
      }, 280);
    }
  }
  window.toggleSidebar = toggleSidebar;
  if (btn) btn.onclick = toggleSidebar; if (bDrop) bDrop.onclick = closeSidebar;
  try { if (localStorage.getItem('er_sb_collapsed') === '1' && window.innerWidth > 900 && sb) sb.classList.add('collapsed'); } catch(e){}

  function isSpreadActive() {
    if (document.body && document.body.classList.contains('wb-concordance')) return false;
    if (document.documentElement.getAttribute('data-read-mode') !== 'paginated') return false;
    if (spreadMode === 'double') return window.innerWidth >= 900;
    if (spreadMode === 'single') return false;
    return window.innerWidth >= 1150;
  }

  function getStep() {
    if (!vp || !bContent) return window.innerWidth;
    const isSpread = isSpreadActive(), padL = parseFloat(window.getComputedStyle(vp).paddingLeft) || 0, padR = parseFloat(window.getComputedStyle(vp).paddingRight) || 0;
    const vpW = vp.clientWidth - padL - padR;
    const isPoly = document.body && document.body.classList.contains('wb-concordance');
    return isSpread ? vpW + 72 : (isPoly ? vpW : vpW + (parseFloat(window.getComputedStyle(bContent).columnGap) || 64));
  }

  function updatePagination(targetRatio) {
    if (document.documentElement.getAttribute('data-read-mode') !== 'paginated' || !bContent) return;
    const isSpread = isSpreadActive();
    if (vp) vp.classList.toggle('spread-active', isSpread);
    if (spreadBtn) spreadBtn.innerHTML = isSpread ? '📑<span class="er-btn-text"> 双页</span>' : '📄<span class="er-btn-text"> 单页</span>';
    const step = getStep();
    if (step <= 0) return;
    totalPages = Math.max(1, Math.ceil(bContent.scrollWidth / step));
    if (typeof targetRatio === 'number' && !isNaN(targetRatio)) {
      curPage = Math.max(0, Math.min(totalPages - 1, Math.round(targetRatio * (totalPages - 1))));
    } else {
      curPage = Math.max(0, Math.min(curPage, totalPages - 1));
    }
    renderPage();
  }

  function renderPage() {
    const step = getStep();
    bContent.style.transform = `translateX(-${curPage * step}px)`;
    const isSpread = isSpreadActive();
    if (fPage) fPage.textContent = isSpread ? `${curPage * 2 + 1}-${Math.min(totalPages * 2, curPage * 2 + 2)} / ${totalPages * 2}` : `${curPage + 1} / ${totalPages}`;
    if (pBar) pBar.style.width = `${Math.min(100, Math.max(0, ((curPage + 1) / totalPages) * 100))}%`;
    syncActiveSection(curPage * step + step * 0.4);
    if (window.onPolyglotRenderPage) window.onPolyglotRenderPage(curPage, totalPages);
  }

  function goToPage(target) {
    if (document.documentElement.getAttribute('data-read-mode') !== 'paginated') return;
    const isSpread = isSpreadActive(), maxP = isSpread ? totalPages * 2 : totalPages;
    let p = parseInt(target, 10);
    if (isNaN(p) || p < 1) p = 1;
    if (p > maxP) p = maxP;
    if (window.handlePolyglotGoToPage && window.handlePolyglotGoToPage(p, maxP)) return;
    curPage = isSpread ? Math.floor((p - 1) / 2) : (p - 1);
    curPage = Math.max(0, Math.min(curPage, totalPages - 1));
    renderPage();
  }
  function nextPage() { if (window.handlePolyglotPaging && window.handlePolyglotPaging(true)) return; if (curPage < totalPages - 1) { curPage++; renderPage(); } }
  function prevPage() { if (window.handlePolyglotPaging && window.handlePolyglotPaging(false)) return; if (curPage > 0) { curPage--; renderPage(); } }
  window.getReaderCurPage = () => curPage;
  window.getReaderTotalPages = () => totalPages;
  window.selectChapterByIndex = (idx) => { curPage = Math.max(0, Math.min(totalPages - 1, idx)); renderPage(); };
  window.goToPage = goToPage;
  window.goToFirstPage = () => goToPage(1);
  window.goToLastPage = () => { const isSpread = isSpreadActive(); goToPage(isSpread ? totalPages * 2 : totalPages); };
  window.nextPage = nextPage;
  window.prevPage = prevPage;
  if (prevBtn) prevBtn.onclick = prevPage;
  if (nextBtn) nextBtn.onclick = nextPage;

  function withContentAnchoring(fn) {
    if (document.documentElement.getAttribute('data-read-mode') === 'paginated') {
      const ratio = totalPages > 1 ? (curPage / (totalPages - 1)) : 0;
      fn(); updatePagination(ratio);
    } else { fn(); }
  }
  window.withContentAnchoring = withContentAnchoring;
  window.updatePagination = updatePagination;

  function applyReadMode(mode) {
    withContentAnchoring(() => {
      document.documentElement.setAttribute('data-read-mode', mode);
      if (modeBtn) {
        modeBtn.innerHTML = mode === 'paginated' ? '📖<span class="er-btn-text"> 翻页</span>' : '📜<span class="er-btn-text"> 卷轴</span>';
        modeBtn.title = mode === 'paginated' ? '当前：左右翻页模式 (点击切换为卷轴)' : '当前：连续卷轴模式 (点击切换为翻页)';
      }
      if (spreadBtn) spreadBtn.style.display = mode === 'paginated' ? 'inline-flex' : 'none';
      try { localStorage.setItem('er_read_mode', mode); } catch(e){}
      if (mode === 'paginated') window.scrollTo({ top: 0 });
      else { if (vp) vp.classList.remove('spread-active'); if (bContent) bContent.style.transform = ''; if (pBar) pBar.style.width = '0%'; }
    });
  }
  if (modeBtn) modeBtn.onclick = () => applyReadMode((document.documentElement.getAttribute('data-read-mode') || 'paginated') === 'paginated' ? 'scroll' : 'paginated');
  if (spreadBtn) spreadBtn.onclick = () => { withContentAnchoring(() => { spreadMode = isSpreadActive() ? 'single' : 'double'; try { localStorage.setItem('er_spread_mode', spreadMode); } catch(e){} }); };

  const FONTS = [{k:'sans', i:'🔤', n:'黑体'}, {k:'serif', i:'📖', n:'宋体'}, {k:'kai', i:'✍️', n:'楷体'}];
  let fontIdx = Math.max(0, FONTS.findIndex(x => x.k === (localStorage.getItem('er_font') || 'sans')));
  function applyFont(idx, skipAnchor = false) {
    fontIdx = idx % FONTS.length; const f = FONTS[fontIdx];
    const doChange = () => {
      document.documentElement.setAttribute('data-font', f.k);
      if (fontBtn) fontBtn.innerHTML = `${f.i}<span class="er-btn-text"> ${f.n}</span>`;
      try { localStorage.setItem('er_font', f.k); } catch(e){}
    };
    if (skipAnchor) { doChange(); setTimeout(updatePagination, 50); } else withContentAnchoring(doChange);
  }
  if (fontBtn) fontBtn.onclick = () => applyFont(fontIdx + 1);
  applyFont(fontIdx, true);

  function syncActiveSection(offsetOrScrollY) {
    let actId = '', actTitle = '';
    const isPag = document.documentElement.getAttribute('data-read-mode') === 'paginated';
    document.querySelectorAll('.er-chapter-card').forEach(c => {
      const pos = isPag ? c.offsetLeft : (c.getBoundingClientRect().top + window.scrollY);
      if (pos <= offsetOrScrollY + (isPag ? 40 : 140)) {
        actId = c.id; const h = c.querySelector('h1, h2, h3'), cid = (c.id || '').toLowerCase();
        actTitle = h ? h.textContent.trim() : (c.classList.contains('er-cover-card') || cid.includes('cover') ? '典籍封面与扉页' : (cid.includes('colophon') ? '出版版权与版记' : (cid.includes('nav') ? '全书目录索引' : '')));
      }
    });
    if (fChap && actTitle) fChap.textContent = actTitle;
    if (actId) document.querySelectorAll('.er-sidebar a').forEach(link => { const h = link.getAttribute('href') || ''; link.classList.toggle('active', h === '#' + actId || h.endsWith(actId)); });
  }

  function showJumpCue(el, wasSamePage) {
    if (!el) return;
    document.querySelectorAll('.er-jump-target').forEach(x => x.classList.remove('er-jump-target'));
    void el.offsetWidth; el.classList.add('er-jump-target');
    setTimeout(() => el.classList.remove('er-jump-target'), 2200);
    const title = (el.tagName && /^H[1-6]$/i.test(el.tagName)) ? el.textContent.trim() : (el.querySelector('h1, h2, h3, h4')?.textContent.trim() || el.textContent.trim().slice(0, 18) || '指定章节');
    const old = document.querySelector('.er-jump-toast'); if (old) old.remove();
    const toast = document.createElement('div'); toast.className = 'er-jump-toast';
    toast.innerHTML = wasSamePage ? `<span style="font-size:1.1rem">📍</span> 已在当前页呈现：<b>${title}</b>` : `<span style="font-size:1.1rem">🎯</span> 定位到：<b>${title}</b>`;
    document.body.appendChild(toast); setTimeout(() => toast.remove(), 1800);
  }
  function showTurnCue(isNext, cx, cy) {
    const t = document.createElement('div');
    t.className = 'er-turn-cue ' + (isNext ? 'er-turn-next' : 'er-turn-prev');
    t.innerHTML = isNext ? '<span class="er-cue-icon">›</span> 下一页' : '<span class="er-cue-icon">‹</span> 上一页';
    t.style.whiteSpace = 'nowrap'; t.style.wordBreak = 'keep-all'; t.style.minWidth = 'max-content';
    const hw = 58, sx = Math.max(hw + 10, Math.min(window.innerWidth - hw - 16, cx || (isNext ? window.innerWidth - 75 : 75)));
    const sy = Math.max(36, Math.min(window.innerHeight - 45, cy || window.innerHeight / 2));
    t.style.left = sx + 'px'; t.style.top = sy + 'px';
    document.body.appendChild(t); setTimeout(() => t.remove(), 380);
  }
  window.showTurnCue = showTurnCue;

  function navigateToTarget(rawTarget, opts = {}) {
    if (!rawTarget) return;
    let targetEl = null;
    if (typeof rawTarget === 'object' && rawTarget.nodeType) targetEl = rawTarget;
    else if (typeof rawTarget === 'string') {
      let t = rawTarget.trim();
      while (t.startsWith('#')) t = t.substring(1);
      const parts = t.split('#');
      let basePart = parts[0] || '', hashId = parts.length > 1 ? parts.slice(1).join('#') : '';
      if (!hashId && basePart && !basePart.startsWith('er-doc-') && !basePart.includes('.')) { hashId = basePart; basePart = ''; }
      try { if (hashId) hashId = decodeURIComponent(hashId); } catch(e){}
      if (hashId) { targetEl = document.getElementById(hashId); if (!targetEl) { try { targetEl = document.querySelector(`[id="${CSS.escape(hashId)}"]`); } catch(e){} } }
      if (!targetEl && basePart) {
        const baseId = basePart.startsWith('er-doc-') ? basePart : ('er-doc-' + basePart.split('/').pop().replace(/[^a-zA-Z0-9_-]/g, '_'));
        targetEl = document.getElementById(baseId);
      }
    }
    if (targetEl) {
      let wasSamePage = false;
      const isPag = document.documentElement.getAttribute('data-read-mode') === 'paginated';
      if (isPag) {
        const step = getStep();
        if (step > 0) {
          const parentCard = targetEl.closest('.er-chapter-card');
          const off = (typeof targetEl.offsetLeft === 'number' && targetEl.offsetLeft > 0) ? targetEl.offsetLeft : (parentCard ? parentCard.offsetLeft : 0);
          const targetPage = Math.max(0, Math.min(totalPages - 1, Math.floor((off + 15) / step)));
          wasSamePage = (targetPage === curPage); curPage = targetPage; renderPage();
        }
      } else {
        const topOffset = targetEl.getBoundingClientRect().top + window.scrollY - 65;
        window.scrollTo({ top: Math.max(0, topOffset), behavior: opts.instant ? 'instant' : 'smooth' });
      }
      if (window.innerWidth <= 900) closeSidebar();
      if (!opts.silent) showJumpCue(targetEl, wasSamePage);
    }
  }
  window.navigateToTarget = navigateToTarget;

  document.addEventListener('click', function(e) {
    const a = e.target.closest('a'); if (!a) return;
    const href = a.getAttribute('href'); if (!href) return;
    if (href.startsWith('http://') || href.startsWith('https://') || href.startsWith('mailto:') || href.startsWith('data:')) {
      a.setAttribute('target', '_blank'); a.setAttribute('rel', 'noopener noreferrer'); return;
    }
    e.preventDefault(); navigateToTarget(href);
    if (window.innerWidth <= 900 && a.closest('#er-sidebar')) closeSidebar();
  });

  if (vp) {
    let downX = 0, downY = 0, downTime = 0, hasDragged = false;
    vp.addEventListener('mousedown', (e) => { downX = e.clientX; downY = e.clientY; downTime = Date.now(); hasDragged = false; });
    vp.addEventListener('mousemove', (e) => { if (downTime && !hasDragged && Math.hypot(e.clientX - downX, e.clientY - downY) > 8) hasDragged = true; });
    vp.addEventListener('click', (e) => {
      if (document.documentElement.getAttribute('data-read-mode') !== 'paginated') return;
      if (e.target.closest('a, button, pre, code, .er-floating-bar, .er-mark-popover, .er-card-modal')) return;
      const sel = window.getSelection();
      if (sel && !sel.isCollapsed && sel.toString().trim().length > 0) return;
      if (hasDragged) { hasDragged = false; return; }
      if (Date.now() - downTime > 400) return;
      const rect = vp.getBoundingClientRect(), x = e.clientX - rect.left;
      if (x < rect.width * 0.28) { showTurnCue(false, e.clientX, e.clientY); prevPage(); }
      else if (x > rect.width * 0.72) { showTurnCue(true, e.clientX, e.clientY); nextPage(); }
    });
  }

  let touchStartX = 0, touchStartY = 0;
  window.addEventListener('touchstart', (e) => { if (e.touches.length === 1) { touchStartX = e.touches[0].clientX; touchStartY = e.touches[0].clientY; } }, { passive: true });
  window.addEventListener('touchend', (e) => {
    if (document.documentElement.getAttribute('data-read-mode') !== 'paginated' || e.changedTouches.length !== 1) return;
    const dx = e.changedTouches[0].clientX - touchStartX, dy = e.changedTouches[0].clientY - touchStartY;
    if (Math.abs(dx) > 42 && Math.abs(dx) > Math.abs(dy) * 1.4) { if (dx < 0) { showTurnCue(true); nextPage(); } else { showTurnCue(false); prevPage(); } }
  }, { passive: true });

  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    const isPag = document.documentElement.getAttribute('data-read-mode') === 'paginated';
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') { if (isPag) { showTurnCue(true); nextPage(); } else window.scrollBy({ top: window.innerHeight * 0.85, behavior: 'smooth' }); }
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { if (isPag) { showTurnCue(false); prevPage(); } else window.scrollBy({ top: -window.innerHeight * 0.85, behavior: 'smooth' }); }
    else if (e.key === 'Home') { if (isPag) { e.preventDefault(); goToFirstPage(); } }
    else if (e.key === 'End') { if (isPag) { e.preventDefault(); goToLastPage(); } }
    else if (e.key === 'm' || e.key === 'M' || e.code === 'KeyM') { e.preventDefault(); toggleSidebar(); }
  });

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (document.documentElement.getAttribute('data-read-mode') === 'paginated' || ticking) return;
    window.requestAnimationFrame(() => {
      const h = document.documentElement.scrollHeight - window.innerHeight;
      if (pBar && h > 0) pBar.style.width = Math.min(100, Math.max(0, (window.scrollY / h) * 100)) + '%';
      syncActiveSection(window.scrollY); ticking = false;
    });
    ticking = true;
  }, { passive: true });

  const themeBtns = document.querySelectorAll('.er-theme-btn');
  const applyTheme = (th) => { document.documentElement.setAttribute('data-theme', th); themeBtns.forEach(x => x.classList.toggle('active', x.getAttribute('data-theme') === th)); try { localStorage.setItem('er_theme', th); } catch(e){} };
  themeBtns.forEach(b => { b.onclick = () => applyTheme(b.getAttribute('data-theme')); });
  try { const savedTh = localStorage.getItem('er_theme'); if (savedTh) applyTheme(savedTh); } catch(e){}

  let fs = 16;
  const inc = document.getElementById('er-font-inc'), dec = document.getElementById('er-font-dec');
  const setFs = (val) => { withContentAnchoring(() => { fs = Math.max(13, Math.min(24, val)); document.documentElement.style.setProperty('--font-size', fs + 'px'); try { localStorage.setItem('er_fs', fs); } catch(e){} const lbl = document.getElementById('er-pfs-val'); if (lbl) lbl.textContent = fs + 'px'; }); };
  window.setReaderFontSize = setFs;
  try { const sfs = parseInt(localStorage.getItem('er_fs'), 10); if (sfs >= 13 && sfs <= 24) fs = sfs; document.documentElement.style.setProperty('--font-size', fs + 'px'); } catch(e){}
  if (inc) inc.onclick = () => setFs(fs + 1); if (dec) dec.onclick = () => setFs(fs - 1);
  window.addEventListener('resize', triggerLayoutSync);
  if (window.ResizeObserver && vp) {
    let rTimer = null;
    new ResizeObserver(() => { if (!isSidebarAnimating) { clearTimeout(rTimer); rTimer = setTimeout(triggerLayoutSync, 60); } }).observe(vp);
  }
  applyReadMode(localStorage.getItem('er_read_mode') || 'paginated');
  setTimeout(updatePagination, 100);
})();
"""
