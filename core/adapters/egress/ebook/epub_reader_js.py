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
  function triggerLayoutSync() { if (document.documentElement.getAttribute('data-read-mode') === 'paginated') withContentAnchoring(updatePagination); }
  const setSidebar = (open) => {
    withContentAnchoring(() => { if (sb) { sb.classList.toggle('open', open); sb.classList.toggle('collapsed', !open); } if (bDrop) bDrop.style.display = open ? 'block' : 'none'; });
    setTimeout(triggerLayoutSync, 280);
  };
  const closeSidebar = () => setSidebar(false);
  function toggleSidebar() {
    withContentAnchoring(() => {
      if (window.innerWidth <= 900) setSidebar(!sb.classList.contains('open'));
      else if (sb) { sb.classList.toggle('collapsed'); try { localStorage.setItem('er_sb_collapsed', sb.classList.contains('collapsed') ? '1' : '0'); } catch(e){} }
    });
    setTimeout(triggerLayoutSync, 280);
  }
  if (btn) btn.onclick = toggleSidebar; if (bDrop) bDrop.onclick = closeSidebar;
  if (sb) sb.addEventListener('transitionend', (e) => { if (e.propertyName === 'transform') triggerLayoutSync(); });
  try { if (localStorage.getItem('er_sb_collapsed') === '1' && window.innerWidth > 900 && sb) sb.classList.add('collapsed'); } catch(e){}

  const vp = document.getElementById('er-viewport'), bContent = document.getElementById('er-book-content');
  const fChap = document.getElementById('er-footer-chapter'), fPage = document.getElementById('er-footer-page'), prevBtn = document.getElementById('er-page-prev'), nextBtn = document.getElementById('er-page-next');
  const modeBtn = document.getElementById('er-mode-toggle'), spreadBtn = document.getElementById('er-spread-toggle'), fontBtn = document.getElementById('er-font-family'), pBar = document.getElementById('er-progress-bar');
  const chapters = document.querySelectorAll('.er-chapter-card'), tocLinks = document.querySelectorAll('.er-sidebar a');

  let curPage = 0, totalPages = 1, spreadMode = localStorage.getItem('er_spread_mode') || 'auto';
  function isSpreadActive() {
    if (document.documentElement.getAttribute('data-read-mode') !== 'paginated') return false;
    if (spreadMode === 'double') return window.innerWidth >= 900;
    if (spreadMode === 'single') return false;
    return window.innerWidth >= 1150;
  }

  function getStep() {
    if (!vp || !bContent) return window.innerWidth;
    const isSpread = isSpreadActive(), padL = parseFloat(window.getComputedStyle(vp).paddingLeft) || 0, padR = parseFloat(window.getComputedStyle(vp).paddingRight) || 0;
    const vpW = vp.clientWidth - padL - padR;
    return isSpread ? vpW + 72 : vpW + (parseFloat(window.getComputedStyle(bContent).columnGap) || 64);
  }

  function updatePagination() {
    if (document.documentElement.getAttribute('data-read-mode') !== 'paginated' || !bContent) return;
    const isSpread = isSpreadActive();
    if (vp) vp.classList.toggle('spread-active', isSpread);
    if (spreadBtn) spreadBtn.innerHTML = isSpread ? '📑<span class="er-btn-text"> 双页</span>' : '📄<span class="er-btn-text"> 单页</span>';
    const step = getStep();
    if (step <= 0) return;
    totalPages = Math.max(1, Math.ceil(bContent.scrollWidth / step));
    curPage = Math.max(0, Math.min(curPage, totalPages - 1));
    renderPage();
  }

  function renderPage() {
    const step = getStep();
    bContent.style.transform = `translateX(-${curPage * step}px)`;
    const isSpread = isSpreadActive();
    if (fPage) fPage.textContent = isSpread ? `${curPage * 2 + 1}-${Math.min(totalPages * 2, curPage * 2 + 2)} / ${totalPages * 2}` : `${curPage + 1} / ${totalPages}`;
    if (pBar) pBar.style.width = `${Math.min(100, Math.max(0, ((curPage + 1) / totalPages) * 100))}%`;
    syncActiveSection(curPage * step + step * 0.4);
  }

  function nextPage() { if (curPage < totalPages - 1) { curPage++; renderPage(); } }
  function prevPage() { if (curPage > 0) { curPage--; renderPage(); } }
  if (prevBtn) prevBtn.onclick = prevPage;
  if (nextBtn) nextBtn.onclick = nextPage;

  // 🎯 首视口段落锚定引擎 (First Visible Element Anchoring · 微信读书方案)
  function getFirstVisibleBlock() {
    if (!vp || !bContent) return null;
    const vpRect = vp.getBoundingClientRect();
    const pts = [{ x: vpRect.left + 50, y: vpRect.top + 60 }, { x: vpRect.left + 50, y: vpRect.top + 140 }, { x: vpRect.left + 80, y: vpRect.top + 200 }];
    for (const pt of pts) {
      const el = document.elementFromPoint(pt.x, pt.y);
      const b = el ? el.closest('p, h1, h2, h3, h4, h5, li, blockquote') : null;
      if (b && bContent.contains(b)) return b;
    }
    const isPag = document.documentElement.getAttribute('data-read-mode') === 'paginated';
    const blocks = bContent.querySelectorAll('p, h1, h2, h3, h4, li, blockquote');
    for (let i = 0; i < blocks.length; i++) {
      const b = blocks[i], r = b.getBoundingClientRect();
      if (isPag ? (r.right > vpRect.left + 15 && r.left < vpRect.right - 15 && r.bottom > vpRect.top) : (r.bottom > 80 && r.top < window.innerHeight)) return b;
    }
    return null;
  }

  function withContentAnchoring(fn) {
    const anchor = getFirstVisibleBlock();
    fn();
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        updatePagination();
        if (anchor) navigateToTarget(anchor, { silent: true, instant: true });
      });
    });
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

  // 🔤 字体库切换引擎
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
    chapters.forEach(c => {
      const pos = isPag ? c.offsetLeft : (c.getBoundingClientRect().top + window.scrollY);
      if (pos <= offsetOrScrollY + (isPag ? 40 : 140)) {
        actId = c.id;
        const h = c.querySelector('h1, h2, h3');
        actTitle = h ? h.textContent.trim() : (c.classList.contains('er-cover-card') ? '典籍封面与扉页' : '');
      }
    });
    if (fChap && actTitle) fChap.textContent = actTitle;
    if (actId) tocLinks.forEach(link => { const h = link.getAttribute('href') || ''; link.classList.toggle('active', h === '#' + actId || h.endsWith(actId)); });
  }

  // 🎯 链接跳转与翻页反馈
  function showJumpCue(el) {
    if (!el) return;
    document.querySelectorAll('.er-jump-target').forEach(x => x.classList.remove('er-jump-target'));
    el.classList.add('er-jump-target'); setTimeout(() => el.classList.remove('er-jump-target'), 2000);
    const title = el.querySelector('h1, h2, h3')?.textContent.trim() || el.textContent.trim().slice(0, 18) || '指定章节';
    const old = document.querySelector('.er-jump-toast'); if (old) old.remove();
    const toast = document.createElement('div'); toast.className = 'er-jump-toast';
    toast.innerHTML = `<span style="font-size:1.1rem">🎯</span> 定位到：<b>${title}</b>`;
    document.body.appendChild(toast); setTimeout(() => toast.remove(), 1600);
  }
  function showTurnCue(isNext, cx, cy) {
    const t = document.createElement('div');
    t.className = 'er-turn-cue ' + (isNext ? 'er-turn-next' : 'er-turn-prev');
    t.innerHTML = isNext ? '<span class="er-cue-icon">›</span> 下一页' : '<span class="er-cue-icon">‹</span> 上一页';
    t.style.left = (cx || (isNext ? window.innerWidth - 65 : 65)) + 'px'; t.style.top = (cy || window.innerHeight / 2) + 'px';
    document.body.appendChild(t); setTimeout(() => t.remove(), 380);
  }

  // 全局内部链接与锚点定位引擎 (支持 silent 模式供重排无感归位)
  function navigateToTarget(rawTarget, opts = {}) {
    if (!rawTarget) return;
    let targetEl = null;
    if (typeof rawTarget === 'object' && rawTarget.nodeType) targetEl = rawTarget;
    else if (typeof rawTarget === 'string') {
      const p = rawTarget.split('#'), hashId = p[1], baseId = p[0] ? ('er-doc-' + p[0].split('/').pop().replace(/[^a-zA-Z0-9_-]/g, '_')) : '';
      if (hashId) targetEl = document.getElementById(hashId) || document.querySelector(`[id="${CSS.escape(hashId)}"]`) || (baseId ? document.getElementById(baseId) : null);
      else if (baseId) targetEl = document.getElementById(baseId);
    }
    if (targetEl) {
      const isPag = document.documentElement.getAttribute('data-read-mode') === 'paginated';
      if (isPag) {
        const step = getStep();
        if (step > 0) {
          const tRect = targetEl.getBoundingClientRect(), bRect = bContent.getBoundingClientRect();
          const dist = (tRect && bRect) ? (tRect.left - bRect.left) : (targetEl.offsetLeft || 0);
          curPage = Math.max(0, Math.min(totalPages - 1, Math.floor((dist + 10) / step)));
          renderPage();
        }
      } else {
        const topOffset = targetEl.getBoundingClientRect().top + window.scrollY - 65;
        window.scrollTo({ top: Math.max(0, topOffset), behavior: opts.instant ? 'instant' : 'smooth' });
      }
      if (window.innerWidth <= 900) closeSidebar();
      if (!opts.silent) showJumpCue(targetEl);
    }
  }
  window.navigateToTarget = navigateToTarget;

  document.addEventListener('click', function(e) {
    const a = e.target.closest('a');
    if (!a) return;
    const href = a.getAttribute('href');
    if (!href) return;
    if (href.startsWith('http://') || href.startsWith('https://') || href.startsWith('mailto:') || href.startsWith('data:')) {
      a.setAttribute('target', '_blank'); a.setAttribute('rel', 'noopener noreferrer'); return;
    }
    e.preventDefault(); navigateToTarget(href);
    if (window.innerWidth <= 900 && a.closest('#er-sidebar')) closeSidebar();
  });

  // 🛡️ 翻页防误触中枢：三重防御拦截选词圈选与拖拽引发的误翻页
  if (vp) {
    let downX = 0, downY = 0, downTime = 0, hasDragged = false;
    vp.addEventListener('mousedown', (e) => {
      downX = e.clientX; downY = e.clientY; downTime = Date.now(); hasDragged = false;
    });
    vp.addEventListener('mousemove', (e) => {
      if (downTime && !hasDragged && Math.hypot(e.clientX - downX, e.clientY - downY) > 8) hasDragged = true;
    });
    vp.addEventListener('click', (e) => {
      if (document.documentElement.getAttribute('data-read-mode') !== 'paginated') return;
      if (e.target.closest('a, button, pre, code, .er-floating-bar, .er-mark-popover, .er-card-modal')) return;
      const sel = window.getSelection();
      if (sel && !sel.isCollapsed && sel.toString().trim().length > 0) return; // 1. 选区拦截
      if (hasDragged) { hasDragged = false; return; } // 2. 拖拽位移拦截 (>8px)
      if (Date.now() - downTime > 400) return; // 3. 长按时间窗拦截 (>400ms)
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
    if (Math.abs(dx) > 42 && Math.abs(dx) > Math.abs(dy) * 1.4) {
      if (dx < 0) { showTurnCue(true); nextPage(); } else { showTurnCue(false); prevPage(); }
    }
  }, { passive: true });

  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    const isPag = document.documentElement.getAttribute('data-read-mode') === 'paginated';
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
      if (isPag) { showTurnCue(true); nextPage(); } else window.scrollBy({ top: window.innerHeight * 0.85, behavior: 'smooth' });
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      if (isPag) { showTurnCue(false); prevPage(); } else window.scrollBy({ top: -window.innerHeight * 0.85, behavior: 'smooth' });
    }
  });

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

  const themeBtns = document.querySelectorAll('.er-theme-btn');
  const applyTheme = (th) => { document.documentElement.setAttribute('data-theme', th); themeBtns.forEach(x => x.classList.toggle('active', x.getAttribute('data-theme') === th)); try { localStorage.setItem('er_theme', th); } catch(e){} };
  themeBtns.forEach(b => { b.onclick = () => applyTheme(b.getAttribute('data-theme')); });
  try { const savedTh = localStorage.getItem('er_theme'); if (savedTh) applyTheme(savedTh); } catch(e){}

  let fs = 16;
  const inc = document.getElementById('er-font-inc'), dec = document.getElementById('er-font-dec');
  const setFs = (val) => {
    withContentAnchoring(() => {
      fs = Math.max(13, Math.min(24, val));
      document.documentElement.style.setProperty('--font-size', fs + 'px');
      try { localStorage.setItem('er_fs', fs); } catch(e){}
      const lbl = document.getElementById('er-pfs-val'); if (lbl) lbl.textContent = fs + 'px';
    });
  };
  window.setReaderFontSize = setFs;
  try { const sfs = parseInt(localStorage.getItem('er_fs'), 10); if (sfs >= 13 && sfs <= 24) fs = sfs; document.documentElement.style.setProperty('--font-size', fs + 'px'); } catch(e){}
  if (inc) inc.onclick = () => setFs(fs + 1); if (dec) dec.onclick = () => setFs(fs - 1);
  window.addEventListener('resize', triggerLayoutSync);
  if (window.ResizeObserver && vp) {
    let rTimer = null;
    new ResizeObserver(() => { clearTimeout(rTimer); rTimer = setTimeout(triggerLayoutSync, 60); }).observe(vp);
  }
  applyReadMode(localStorage.getItem('er_read_mode') || 'paginated');
  setTimeout(updatePagination, 100);
})();
"""
