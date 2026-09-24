# -*- coding: utf-8 -*-
"""
Illacme Plenipes - WebBook Embedded Runtime JavaScript
模块职责：提供单文件离线网页书 (WebBook) 的移动端手势翻页、阅读进度记忆、多语种对照矩阵等客户端逻辑。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_webbook_js() -> str:
    """获取整卷 WebBook 客户端交互 JavaScript 脚本"""
    return """(function() {
  'use strict';
  const sb = document.getElementById('wb-sidebar'), btn = document.getElementById('wb-toggle-sidebar'), bDrop = document.getElementById('wb-backdrop');
  function closeSidebar() {
    if (sb) { sb.classList.remove('open'); sb.classList.add('collapsed'); }
    if (bDrop) bDrop.classList.remove('active');
  }
  function openSidebar() {
    if (sb) { sb.classList.add('open'); sb.classList.remove('collapsed'); }
    if (bDrop) bDrop.classList.add('active');
  }
  function toggleSidebar() {
    const isMob = window.innerWidth <= 900;
    if (isMob) { if (sb && sb.classList.contains('open')) closeSidebar(); else openSidebar(); }
    else if (sb) { sb.classList.toggle('collapsed'); try { localStorage.setItem('wb_sb_collapsed', sb.classList.contains('collapsed') ? '1' : '0'); } catch(e){} }
  }
  let lastToggleTime = 0;
  function onToggleTrigger(e) {
    const now = Date.now();
    if (now - lastToggleTime < 350) { if (e && e.cancelable) e.preventDefault(); return; }
    lastToggleTime = now;
    if (e && e.type === 'touchend' && e.cancelable) e.preventDefault();
    toggleSidebar();
  }
  if (btn && sb) {
    btn.addEventListener('click', onToggleTrigger);
    btn.addEventListener('touchend', onToggleTrigger, { passive: false });
    if (bDrop) {
      bDrop.addEventListener('click', closeSidebar);
      bDrop.addEventListener('touchend', (e) => { if (e.cancelable) e.preventDefault(); closeSidebar(); }, { passive: false });
    }
    try { if (localStorage.getItem('wb_sb_collapsed') === '1' && window.innerWidth > 900) sb.classList.add('collapsed'); } catch(e){}
  }

  // 1. 三模主题切换
  const themeBtns = document.querySelectorAll('.wb-theme-btn');
  const applyTheme = (th) => {
    document.documentElement.setAttribute('data-theme', th);
    themeBtns.forEach(x => x.classList.toggle('active', x.getAttribute('data-theme') === th));
    try { localStorage.setItem('wb_theme', th); } catch(e){}
  };
  themeBtns.forEach(b => { b.onclick = () => applyTheme(b.getAttribute('data-theme')); });
  try { const savedTh = localStorage.getItem('wb_theme'); if (savedTh) applyTheme(savedTh); } catch(e){}

  // 2. 字号缩放
  let fs = 16;
  const inc = document.getElementById('wb-font-inc'), dec = document.getElementById('wb-font-dec'), prBtn = document.getElementById('wb-print-btn');
  const setFs = (val) => { fs = val; document.documentElement.style.setProperty('--font-size', fs + 'px'); try { localStorage.setItem('wb_fs', fs); } catch(e){} };
  try { const sfs = parseInt(localStorage.getItem('wb_fs'), 10); if (sfs >= 13 && sfs <= 24) setFs(sfs); } catch(e){}
  if (inc) inc.onclick = () => setFs(Math.min(24, fs + 1));
  if (dec) dec.onclick = () => setFs(Math.max(13, fs - 1));
  if (prBtn) prBtn.onclick = () => window.print();

  let toastTimer = null;
  function showToast(msg) {
    let t = document.getElementById('wb-toast-capsule');
    if (!t) { t = document.createElement('div'); t.id = 'wb-toast-capsule'; t.className = 'wb-toast-capsule'; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => { if (t) t.classList.remove('show'); }, 1400);
  }
  function scrollToChapter(idx, showCapsule = false) {
    const chs = Array.from(document.querySelectorAll('.wb-chapter'));
    if (idx >= 0 && idx < chs.length && chs[idx]) {
      const top = window.pageYOffset + chs[idx].getBoundingClientRect().top - 70;
      window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
      if (showCapsule) { const title = chs[idx].getAttribute('data-title') || `第 ${idx + 1} 节`; showToast(`📖 ${title}`); }
    }
  }

  // 4. 键盘与触屏手势翻页 (Touch Swipe)
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'j' || e.key === 'k') {
      const chs = Array.from(document.querySelectorAll('.wb-chapter'));
      if (!chs.length) return;
      const cur = chs.findIndex(c => c.getBoundingClientRect().bottom > 130);
      const next = (e.key === 'ArrowLeft' || e.key === 'k') ? Math.max(0, cur - 1) : Math.min(chs.length - 1, cur + 1);
      scrollToChapter(next, true);
    }
  });

  let touchStartX = 0, touchStartY = 0, touchStartTime = 0;
  window.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) { touchStartX = e.touches[0].clientX; touchStartY = e.touches[0].clientY; touchStartTime = Date.now(); }
  }, { passive: true });
  window.addEventListener('touchend', (e) => {
    if (e.changedTouches.length === 1) {
      const dx = e.changedTouches[0].clientX - touchStartX, dy = e.changedTouches[0].clientY - touchStartY, dt = Date.now() - touchStartTime;
      if (dt < 500 && Math.abs(dx) > 65 && Math.abs(dy) < 50) {
        const chs = Array.from(document.querySelectorAll('.wb-chapter'));
        if (!chs.length) return;
        const cur = chs.findIndex(c => c.getBoundingClientRect().bottom > 130);
        if (dx < 0 && cur < chs.length - 1) scrollToChapter(cur + 1, true);
        else if (dx > 0 && cur > 0) scrollToChapter(cur - 1, true);
      }
    }
  }, { passive: true });

  // 5. 目录过滤与折叠
  document.querySelectorAll('.wb-toc-toggle').forEach(t => {
    t.onclick = (e) => { e.stopPropagation(); const g = t.closest('.wb-toc-group'); if (g) g.classList.toggle('collapsed'); };
  });
  const search = document.getElementById('wb-search'), groups = document.querySelectorAll('.wb-toc-group');
  if (search) {
    search.oninput = (e) => {
      const q = e.target.value.toLowerCase().trim();
      groups.forEach(g => {
        if (!q) { g.style.display = ''; g.querySelectorAll('.wb-toc-subitem').forEach(s => s.style.display = ''); return; }
        const ch = g.querySelector('.wb-toc-chapter'), subs = g.querySelectorAll('.wb-toc-subitem');
        let chM = ch && ch.textContent.toLowerCase().includes(q), subM = 0;
        subs.forEach(s => { const m = s.textContent.toLowerCase().includes(q); s.style.display = m ? '' : 'none'; if (m) subM++; });
        if (chM || subM > 0) { g.style.display = ''; g.classList.remove('collapsed'); } else { g.style.display = 'none'; }
      });
    };
  }

  // 6. 进度条与位置记忆
  let scrollTimer = null;
  window.onscroll = () => {
    const s = document.documentElement.scrollTop, h = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const bar = document.getElementById('wb-progress');
    if (bar) bar.style.width = (h ? (s / h * 100) : 0) + '%';
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(() => { try { localStorage.setItem('wb_scroll_pos', String(window.pageYOffset || 0)); } catch(e){} }, 200);
  };
  try {
    if (!window.location.hash) {
      const savedPos = parseInt(localStorage.getItem('wb_scroll_pos') || '0', 10);
      if (savedPos > 80) setTimeout(() => window.scrollTo({ top: savedPos, behavior: 'instant' }), 50);
    }
  } catch(e){}

  // 7. 滚动与目录联动高亮
  const targets = document.querySelectorAll('.wb-chapter, .wb-chapter-body h2[id], .wb-chapter-body h3[id]');
  const allLinks = document.querySelectorAll('.wb-toc-item, .wb-toc-subitem');
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const id = e.target.id;
        const matched = document.querySelector(`.wb-toc-subitem[data-id="${id}"], .wb-toc-item[data-id="${id}"]`);
        if (matched) {
          allLinks.forEach(l => l.classList.remove('active', 'active-ch'));
          matched.classList.add('active');
          const grp = matched.closest('.wb-toc-group');
          if (grp) {
            grp.classList.remove('collapsed');
            const chLink = grp.querySelector('.wb-toc-chapter');
            if (chLink && chLink !== matched) chLink.classList.add('active-ch');
          }
        }
      }
    });
  }, { rootMargin: '-10% 0px -75% 0px' });
  targets.forEach(t => obs.observe(t));

  // 8. 目录点击跳转 (移动端自动收起抽屉)
  allLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      if (window.innerWidth <= 900) closeSidebar();
      const chId = link.getAttribute('data-ch-id') || link.getAttribute('data-id'), lvl = link.getAttribute('data-level');
      const hIdx = link.getAttribute('data-h-idx'), sIdx = link.getAttribute('data-s-idx');
      const langId = link.getAttribute('data-id-' + primaryLang) || link.getAttribute('data-id');
      let targetEl = langId ? document.getElementById(langId) : null;
      if (!targetEl || targetEl.closest('.wb-poly-hidden')) {
        const chEl = chId ? document.getElementById(chId) : link.closest('.wb-chapter');
        if (chEl) {
          const col = chEl.querySelector(`.wb-poly-item[data-lang="${primaryLang}"]:not(.wb-poly-hidden)`) || chEl.querySelector('.wb-poly-content') || chEl;
          if (col) {
            if (lvl === '2' && hIdx !== null) targetEl = col.querySelectorAll('h2')[parseInt(hIdx, 10)] || null;
            else if (lvl === '3' && sIdx !== null) targetEl = col.querySelectorAll('h3')[parseInt(sIdx, 10)] || null;
            if (!targetEl) targetEl = chEl;
          }
        }
      }
      if (!targetEl) { const href = link.getAttribute('href') || ''; if (href.startsWith('#')) targetEl = document.getElementById(href.slice(1)); }
      if (targetEl) {
        const topPos = window.pageYOffset + targetEl.getBoundingClientRect().top - 72;
        window.scrollTo({ top: Math.max(0, topPos), behavior: 'smooth' });
        allLinks.forEach(l => l.classList.remove('active', 'active-ch'));
        link.classList.add('active');
        const grp = link.closest('.wb-toc-group');
        if (grp) { grp.classList.remove('collapsed'); const chLink = grp.querySelector('.wb-toc-chapter'); if (chLink && chLink !== link) chLink.classList.add('active-ch'); }
      }
    });
  });

  // 9. 代码复制与表格容器
  document.querySelectorAll('.wb-chapter-body pre').forEach(pre => {
    if (pre.closest('.wb-code-wrapper')) return;
    const wrap = document.createElement('div'); wrap.className = 'wb-code-wrapper';
    pre.parentNode.insertBefore(wrap, pre); wrap.appendChild(pre);
    const cbtn = document.createElement('button'); cbtn.className = 'wb-copy-btn'; cbtn.type = 'button'; cbtn.innerHTML = '📋 复制';
    cbtn.onclick = async () => {
      const c = pre.querySelector('code') || pre, txt = c.innerText || c.textContent || '';
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) { await navigator.clipboard.writeText(txt); }
        else { const t = document.createElement('textarea'); t.value = txt; document.body.appendChild(t); t.select(); document.execCommand('copy'); t.remove(); }
        cbtn.innerHTML = '✓ 已复制'; cbtn.classList.add('copied');
        setTimeout(() => { cbtn.innerHTML = '📋 复制'; cbtn.classList.remove('copied'); }, 2000);
      } catch(e) { cbtn.innerHTML = '复制失败'; }
    };
    wrap.appendChild(cbtn);
  });
  document.querySelectorAll('.wb-chapter-body table').forEach(tbl => {
    if (tbl.closest('.wb-table-wrapper')) return;
    const wrap = document.createElement('div'); wrap.className = 'wb-table-wrapper';
    tbl.parentNode.insertBefore(wrap, tbl); wrap.appendChild(tbl);
  });

  // 10. 多语言对照矩阵
  const primaryBtns = document.querySelectorAll('.wb-primary-item'), compareChipsBox = document.getElementById('wb-compare-chips');
  const allLangs = compareChipsBox ? (compareChipsBox.getAttribute('data-all-langs') || 'zh,en,ja').split(',') : ['zh', 'en', 'ja'];
  const langNames = { zh: '🇨🇳 中文', en: '🇬🇧 英语', ja: '🇯🇵 日语', fr: '🇫🇷 法语', de: '🇩🇪 德语', es: '🇪🇸 西语', ru: '🇷🇺 俄语', ko: '🇰🇷 韩语' };
  let primaryLang = 'zh'; const initialActive = document.querySelector('.wb-primary-item.active');
  if (initialActive) primaryLang = initialActive.getAttribute('data-lang');
  try {
    const savedPri = localStorage.getItem('wb_primary_lang');
    if (savedPri && allLangs.includes(savedPri)) {
      primaryLang = savedPri;
      primaryBtns.forEach(b => b.classList.toggle('active', b.getAttribute('data-lang') === primaryLang));
    }
  } catch(e){}
  const compareLangs = new Set(); let hasSavedCompare = false;
  try {
    const savedCmp = localStorage.getItem('wb_compare_langs');
    if (savedCmp !== null) {
      hasSavedCompare = true;
      savedCmp.split(',').filter(l => l && l !== primaryLang && allLangs.includes(l)).forEach(l => compareLangs.add(l));
    }
  } catch(e){}
  if (!hasSavedCompare) {
    const defaultCompare = allLangs.find(l => l !== primaryLang);
    if (defaultCompare) compareLangs.add(defaultCompare);
  }
  function saveLangPrefs() {
    try {
      localStorage.setItem('wb_primary_lang', primaryLang);
      localStorage.setItem('wb_compare_langs', Array.from(compareLangs).join(','));
    } catch(e){}
  }
  function renderCompareChips() {
    if (!compareChipsBox) return;
    compareChipsBox.innerHTML = '';
    allLangs.filter(l => l !== primaryLang).forEach(l => {
      const btn = document.createElement('button'); btn.type = 'button';
      btn.className = 'wb-compare-chip' + (compareLangs.has(l) ? ' active' : '');
      btn.innerHTML = (compareLangs.has(l) ? '☑ ' : '☐ ') + (langNames[l] || l.toUpperCase());
      btn.onclick = () => {
        if (compareLangs.has(l)) { compareLangs.delete(l); } else { compareLangs.add(l); }
        saveLangPrefs(); renderCompareChips(); applyLanguageLayout();
      };
      compareChipsBox.appendChild(btn);
    });
  }
  function applyLanguageLayout() {
    document.querySelectorAll('[data-title-' + primaryLang + ']').forEach(el => {
      const val = el.getAttribute('data-title-' + primaryLang); if (val) el.textContent = val;
    });
    const isCompare = compareLangs.size > 0;
    document.body.classList.toggle('wb-concordance', isCompare);
    const layout = document.querySelector('.wb-layout');
    if (layout) layout.classList.toggle('wb-layout-wide', isCompare);
    const activeOrderedLangs = [primaryLang, ...Array.from(compareLangs)];
    document.querySelectorAll('.wb-polyglot-block').forEach(block => {
      block.querySelectorAll('.wb-poly-item').forEach(item => {
        const l = item.getAttribute('data-lang'), pos = activeOrderedLangs.indexOf(l);
        if (pos >= 0) {
          item.classList.remove('wb-poly-hidden'); item.style.order = String(pos + 1);
          const badge = item.querySelector('.wb-lang-badge');
          if (badge) badge.textContent = l === primaryLang ? `${l.toUpperCase()} 主语言` : `${l.toUpperCase()} 对照栏`;
        } else { item.classList.add('wb-poly-hidden'); }
      });
    });
    document.querySelectorAll('.wb-colophon-card').forEach(c => {
      const l = c.getAttribute('data-lang'); c.classList.toggle('wb-poly-hidden', l !== primaryLang && !compareLangs.has(l));
    });
  }
  primaryBtns.forEach(btn => {
    btn.onclick = () => {
      const l = btn.getAttribute('data-lang');
      if (l === primaryLang) return;
      primaryLang = l; compareLangs.delete(l);
      primaryBtns.forEach(b => b.classList.toggle('active', b.getAttribute('data-lang') === primaryLang));
      saveLangPrefs(); renderCompareChips(); applyLanguageLayout();
    };
  });
  renderCompareChips(); applyLanguageLayout();
})();"""
