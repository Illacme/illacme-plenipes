# -*- coding: utf-8 -*-
"""
Illacme Plenipes - WebBook Embedded Assets & Runtime Driver
模块职责：提供单文件离线网页书 (WebBook) 的高质感 CSS 样式、多语言全局无缝切换与对照研读运行时。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""
class WebBookAssets:
    """🎨 WebBook 离线内联资产构建器"""
    @staticmethod
    def get_embedded_css() -> str:
        return """:root { --bg-main: #0d1117; --bg-sidebar: #161b22; --bg-card: #1f242c; --text-main: #c9d1d9; --text-dim: #8b949e; --text-title: #f0f6fc; --accent: #10b981; --border: #30363d; --code-bg: #161b22; --font-size: 16px; }
[data-theme="light"] { --bg-main: #f8fafc; --bg-sidebar: #ffffff; --bg-card: #f1f5f9; --text-main: #1e293b; --text-dim: #64748b; --text-title: #0f172a; --accent: #059669; --border: #e2e8f0; --code-bg: #f8fafc; }
[data-theme="sepia"] { --bg-main: #fbf0d9; --bg-sidebar: #f4e3c1; --bg-card: #efe0bc; --text-main: #433422; --text-dim: #7f6e5d; --text-title: #2b1f14; --accent: #b45309; --border: #dfcaa7; --code-bg: #f5e7cd; }
* { box-sizing: border-box; margin: 0; padding: 0; } body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: var(--font-size); background: var(--bg-main); color: var(--text-main); line-height: 1.8; }
.wb-progress-bar { position: fixed; top: 0; left: 0; height: 3px; background: var(--accent); width: 0%; z-index: 1000; transition: width 0.1s; }
.wb-topbar { position: fixed; top: 0; left: 0; right: 0; height: 50px; background: var(--bg-sidebar); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; padding: 0 16px; z-index: 900; }
.wb-book-title { font-weight: 700; font-size: 0.88rem; color: var(--text-title); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 20vw; }
.wb-btn { background: var(--bg-card); border: 1px solid var(--border); color: var(--text-main); border-radius: 6px; padding: 4px 9px; cursor: pointer; font-size: 0.82rem; transition: all 0.2s; } .wb-btn:hover { border-color: var(--accent); color: var(--accent); }
.wb-controls { display: flex; gap: 6px; align-items: center; } .wb-theme-btn { background: none; border: 1px solid var(--border); border-radius: 5px; padding: 3px 7px; cursor: pointer; font-size: 0.85rem; } .wb-theme-btn.active { border-color: var(--accent); background: rgba(16,185,129,0.15); }
.wb-layout { display: flex; margin-top: 50px; min-height: calc(100vh - 50px); } .wb-sidebar { width: 290px; background: var(--bg-sidebar); border-right: 1px solid var(--border); position: fixed; top: 50px; bottom: 0; left: 0; display: flex; flex-direction: column; overflow: hidden; z-index: 800; transition: transform 0.3s; } .wb-sidebar.collapsed { transform: translateX(-100%); }
.wb-cover-box { text-align: center; padding: 14px 10px 4px; } .wb-cover-img { max-height: 135px; border-radius: 6px; box-shadow: 0 4px 14px rgba(0,0,0,0.25); border: 1px solid var(--border); }
.wb-search-box { padding: 10px 14px; } .wb-search-box input { width: 100%; padding: 6px 10px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; color: var(--text-main); font-size: 0.84rem; outline: none; } .wb-search-box input:focus { border-color: var(--accent); }
.wb-toc { flex: 1; overflow-y: auto; padding: 4px 8px; } .wb-toc-row { display: flex; align-items: center; justify-content: space-between; border-radius: 6px; margin-bottom: 2px; } .wb-toc-row:hover { background: rgba(16,185,129,0.08); }
.wb-toc-item { flex: 1; display: block; padding: 6px 8px; text-decoration: none; color: var(--text-main); font-size: 0.86rem; border-radius: 6px; transition: color 0.15s; } .wb-toc-item:hover { color: var(--accent); } .wb-toc-item.active { background: var(--accent); color: #fff; font-weight: 600; } .wb-toc-item.active-ch { color: var(--accent); font-weight: 600; }
.wb-toc-toggle { background: none; border: none; color: var(--text-dim); cursor: pointer; padding: 4px 6px; font-size: 0.78rem; transition: transform 0.2s; border-radius: 4px; } .wb-toc-group.collapsed .wb-toc-toggle { transform: rotate(-90deg); } .wb-toc-group.collapsed .wb-toc-sub { display: none; }
.wb-toc-sub { margin-left: 10px; padding-left: 8px; border-left: 1px solid var(--border); margin-top: 1px; margin-bottom: 3px; } .wb-toc-subitem { display: block; padding: 3px 6px; text-decoration: none; color: var(--text-dim); font-size: 0.81rem; border-radius: 4px; } .wb-toc-subitem:hover { color: var(--accent); background: rgba(16,185,129,0.06); } .wb-toc-subitem.active { color: var(--accent); font-weight: 600; background: rgba(16,185,129,0.12); }
.wb-toc-h3 { margin-left: 8px; font-size: 0.76rem; opacity: 0.88; } .wb-toc-bullet { opacity: 0.5; margin-right: 4px; font-size: 0.7rem; } .wb-toc-num { opacity: 0.65; margin-right: 4px; }
.wb-sidebar-footer { font-size: 0.72rem; color: var(--text-dim); text-align: center; padding: 8px; border-top: 1px solid var(--border); } .wb-main { flex: 1; margin-left: 290px; padding: 30px 40px 100px; transition: margin 0.3s; } .wb-sidebar.collapsed ~ .wb-main { margin-left: 0; }
.wb-content-wrapper { max-width: 860px; margin: 0 auto; transition: max-width 0.3s, opacity 0.18s ease-in-out; } .wb-crossfade { opacity: 0; transform: translateY(4px); } .wb-layout-wide .wb-content-wrapper { max-width: 1360px; }
.wb-chapter { margin-bottom: 70px; padding-bottom: 40px; border-bottom: 1px solid var(--border); scroll-margin-top: 95px; } .wb-chapter-badge { font-size: 0.75rem; text-transform: uppercase; color: var(--accent); font-weight: 700; letter-spacing: 0.05em; }
.wb-chapter-title { font-size: 1.85rem; font-weight: 800; color: var(--text-title); margin: 6px 0 20px; transition: color 0.2s; scroll-margin-top: 95px; }
.wb-chapter-body p { margin: 0.8em 0; } .wb-chapter-body h1, .wb-chapter-body h2, .wb-chapter-body h3, .wb-chapter-body h4 { color: var(--text-title); margin: 1.4em 0 0.6em; scroll-margin-top: 95px; }
.wb-chapter-body blockquote { border-left: 4px solid var(--accent); padding: 0.6em 1em; background: var(--bg-card); color: var(--text-dim); margin: 1.2em 0; border-radius: 0 6px 6px 0; }
.wb-chapter-body code { font-family: ui-monospace, Menlo, monospace; background: var(--code-bg); padding: 2px 5px; border-radius: 4px; font-size: 0.9em; }
.wb-chapter-body pre { background: var(--code-bg); padding: 14px; border-radius: 6px; overflow-x: auto; border: 1px solid var(--border); margin: 1.2em 0; }
.wb-chapter-body img { max-width: 100%; height: auto; display: block; margin: 1.5em auto; border-radius: 6px; border: 1px solid var(--border); } .wb-chapter-body a { color: var(--accent); text-decoration: none; }
.colophon-card { border: 1px solid var(--border); background: var(--bg-card); padding: 22px; border-radius: 8px; margin: 20px 0; } .colophon-grid { width: 100%; border-collapse: collapse; font-size: 0.88rem; } .colophon-grid td { padding: 6px 8px; border-bottom: 1px dashed var(--border); }
.wb-polyglot-bar { display: flex; align-items: center; gap: 8px; } .wb-poly-switcher-group { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.wb-primary-group, .wb-compare-group { display: flex; align-items: center; gap: 6px; } .wb-bar-label { font-size: 0.75rem; color: var(--text-dim); font-weight: 600; white-space: nowrap; } .wb-bar-sep { color: var(--border); font-size: 0.8rem; user-select: none; }
.wb-segmented-capsule { display: flex; background: var(--bg-card); padding: 2px; border-radius: 8px; border: 1px solid var(--border); } .wb-primary-item { background: none; border: none; color: var(--text-dim); font-size: 0.78rem; font-weight: 600; padding: 4px 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s; white-space: nowrap; } .wb-primary-item:hover { color: var(--text-title); } .wb-primary-item.active { background: var(--accent); color: #ffffff; box-shadow: 0 2px 6px rgba(16,185,129,0.3); }
.wb-compare-chips { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; } .wb-compare-chip { background: var(--bg-card); border: 1px solid var(--border); color: var(--text-dim); font-size: 0.74rem; font-weight: 600; padding: 3px 8px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 4px; transition: all 0.2s; user-select: none; } .wb-compare-chip:hover { border-color: var(--accent); color: var(--text-title); } .wb-compare-chip.active { background: rgba(16,185,129,0.15); border-color: var(--accent); color: var(--accent); font-weight: 700; box-shadow: 0 0 8px rgba(16,185,129,0.2); }
body:not(.wb-concordance) .wb-poly-header, body:not(.wb-concordance) .wb-poly-subtitles { display: none !important; } body:not(.wb-concordance) .wb-polyglot-block { margin: 0.6em 0; }
body:not(.wb-concordance) .wb-poly-item { width: 100%; border: none !important; background: transparent !important; padding: 0 !important; box-shadow: none !important; }
body.wb-concordance .wb-polyglot-block { display: flex !important; flex-direction: row !important; gap: 32px !important; align-items: stretch !important; margin: 1.2em 0 2.5em; padding: 0 !important; background: transparent !important; border: none !important; box-shadow: none !important; width: 100%; box-sizing: border-box; }
body.wb-concordance .wb-poly-item { flex: 1 1 0; min-width: 0 !important; display: flex; flex-direction: column; padding: 0; background: transparent !important; border: none !important; box-shadow: none !important; box-sizing: border-box; position: relative; }
body.wb-concordance .wb-poly-item:not(:last-child) { border-right: 1px dashed var(--border) !important; padding-right: 32px; }
body.wb-concordance .wb-poly-header { position: sticky; top: 48px; z-index: 15; display: flex; align-items: center; gap: 8px; padding: 8px 12px; margin-bottom: 18px; background: var(--bg-card); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid var(--border); border-radius: 8px; font-weight: 700; font-size: 0.82rem; color: var(--text-title); user-select: none; box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
body.wb-concordance .wb-lang-badge { display: inline-block; font-size: 0.68rem; font-weight: 700; color: var(--accent); background: rgba(16,185,129,0.14); padding: 2px 8px; border-radius: 4px; letter-spacing: 0.5px; }
body.wb-concordance .wb-poly-content { flex: 1; min-width: 0; word-break: break-word; line-height: 1.8; font-size: var(--font-size); color: var(--text-main); }
body.wb-concordance .wb-poly-content > *:first-child { margin-top: 0; }
body.wb-concordance .wb-poly-content p { margin: 1.1em 0; }
body.wb-concordance .wb-poly-content h1, body.wb-concordance .wb-poly-content h2, body.wb-concordance .wb-poly-content h3 { color: var(--text-title); margin: 1.4em 0 0.6em; }
.wb-poly-hidden { display: none !important; } @media (max-width: 900px) { .wb-sidebar { transform: translateX(-100%); } .wb-sidebar.open { transform: translateX(0); }
.wb-main { margin-left: 0; padding: 20px 16px; } body.wb-concordance .wb-polyglot-block { flex-direction: column !important; gap: 24px !important; }
body.wb-concordance .wb-poly-item:not(:last-child) { border-right: none !important; border-bottom: 1px dashed var(--border) !important; padding-right: 0; padding-bottom: 24px; }
}"""
    @staticmethod
    def get_embedded_js() -> str:
        return """(function() {
  const sb = document.getElementById('wb-sidebar'), btn = document.getElementById('wb-toggle-sidebar');
  if (btn && sb) {
    btn.onclick = () => {
      const isMob = window.innerWidth <= 900;
      if (isMob) { sb.classList.toggle('open'); } else { sb.classList.toggle('collapsed'); }
      try { localStorage.setItem('wb_sb_collapsed', sb.classList.contains('collapsed') ? '1' : '0'); } catch(e){}
    };
    try { if (localStorage.getItem('wb_sb_collapsed') === '1' && window.innerWidth > 900) sb.classList.add('collapsed'); } catch(e){}
  }
  document.querySelectorAll('.wb-theme-btn').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('.wb-theme-btn').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      const th = b.getAttribute('data-theme');
      document.documentElement.setAttribute('data-theme', th);
      try { localStorage.setItem('wb_theme', th); } catch(e){}
    };
  });
  try {
    const savedTh = localStorage.getItem('wb_theme');
    if (savedTh) {
      document.documentElement.setAttribute('data-theme', savedTh);
      document.querySelectorAll('.wb-theme-btn').forEach(x => x.classList.toggle('active', x.getAttribute('data-theme') === savedTh));
    }
  } catch(e){}
  let fs = 16;
  try {
    const savedFs = parseInt(localStorage.getItem('wb_fs'), 10);
    if (savedFs >= 13 && savedFs <= 24) { fs = savedFs; document.documentElement.style.setProperty('--font-size', fs + 'px'); }
  } catch(e){}
  const inc = document.getElementById('wb-font-inc'), dec = document.getElementById('wb-font-dec');
  const setFs = (val) => { fs = val; document.documentElement.style.setProperty('--font-size', fs + 'px'); try { localStorage.setItem('wb_fs', fs); } catch(e){} };
  if (inc) inc.onclick = () => setFs(Math.min(24, fs + 1));
  if (dec) dec.onclick = () => setFs(Math.max(13, fs - 1));
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'j' || e.key === 'k') {
      const chs = Array.from(document.querySelectorAll('.wb-chapter'));
      if (!chs.length) return;
      const cur = chs.findIndex(c => c.getBoundingClientRect().bottom > 130);
      const next = (e.key === 'ArrowLeft' || e.key === 'k') ? Math.max(0, cur - 1) : Math.min(chs.length - 1, cur + 1);
      if (next >= 0 && chs[next]) {
        const top = window.pageYOffset + chs[next].getBoundingClientRect().top - 80;
        window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
      }
    }
  });
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
  allLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
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
        const topPos = window.pageYOffset + targetEl.getBoundingClientRect().top - 92;
        window.scrollTo({ top: Math.max(0, topPos), behavior: 'smooth' });
        allLinks.forEach(l => l.classList.remove('active', 'active-ch'));
        link.classList.add('active');
        const grp = link.closest('.wb-toc-group');
        if (grp) { grp.classList.remove('collapsed'); const chLink = grp.querySelector('.wb-toc-chapter'); if (chLink && chLink !== link) chLink.classList.add('active-ch'); }
      }
    });
  });
  const primaryBtns = document.querySelectorAll('.wb-primary-item');
  const compareChipsBox = document.getElementById('wb-compare-chips');
  const allLangs = compareChipsBox ? (compareChipsBox.getAttribute('data-all-langs') || 'zh,en,ja').split(',') : ['zh', 'en', 'ja'];
  const langNames = { zh: '🇨🇳 中文', en: '🇬🇧 英语', ja: '🇯🇵 日语', fr: '🇫🇷 法语', de: '🇩🇪 德语', es: '🇪🇸 西语', ru: '🇷🇺 俄语', ko: '🇰🇷 韩语' };
  
  let primaryLang = 'zh';
  const initialActive = document.querySelector('.wb-primary-item.active');
  if (initialActive) primaryLang = initialActive.getAttribute('data-lang');
  try {
    const savedPri = localStorage.getItem('wb_primary_lang');
    if (savedPri && allLangs.includes(savedPri)) {
      primaryLang = savedPri;
      primaryBtns.forEach(b => b.classList.toggle('active', b.getAttribute('data-lang') === primaryLang));
    }
  } catch(e){}
  const compareLangs = new Set();
  let hasSavedCompare = false;
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
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'wb-compare-chip' + (compareLangs.has(l) ? ' active' : '');
      btn.innerHTML = (compareLangs.has(l) ? '☑ ' : '☐ ') + (langNames[l] || l.toUpperCase());
      btn.onclick = () => {
        if (compareLangs.has(l)) { compareLangs.delete(l); } else { compareLangs.add(l); }
        saveLangPrefs();
        renderCompareChips();
        applyLanguageLayout();
      };
      compareChipsBox.appendChild(btn);
    });
  }
  function applyLanguageLayout() {
    document.querySelectorAll('[data-title-' + primaryLang + ']').forEach(el => {
      const val = el.getAttribute('data-title-' + primaryLang);
      if (val) el.textContent = val;
    });
    const isCompare = compareLangs.size > 0;
    document.body.classList.toggle('wb-concordance', isCompare);
    const layout = document.querySelector('.wb-layout');
    if (layout) layout.classList.toggle('wb-layout-wide', isCompare);
    const activeOrderedLangs = [primaryLang, ...Array.from(compareLangs)];
    document.querySelectorAll('.wb-polyglot-block').forEach(block => {
      block.querySelectorAll('.wb-poly-item').forEach(item => {
        const l = item.getAttribute('data-lang');
        const pos = activeOrderedLangs.indexOf(l);
        if (pos >= 0) {
          item.classList.remove('wb-poly-hidden');
          item.style.order = String(pos + 1);
          const badge = item.querySelector('.wb-lang-badge');
          if (badge) badge.textContent = l === primaryLang ? `${l.toUpperCase()} 主语言` : `${l.toUpperCase()} 对照栏`;
        } else {
          item.classList.add('wb-poly-hidden');
        }
      });
    });
    document.querySelectorAll('.wb-colophon-card').forEach(c => {
      const l = c.getAttribute('data-lang');
      c.classList.toggle('wb-poly-hidden', l !== primaryLang && !compareLangs.has(l));
    });
  }
  primaryBtns.forEach(btn => {
    btn.onclick = () => {
      const l = btn.getAttribute('data-lang');
      if (l === primaryLang) return;
      primaryLang = l;
      compareLangs.delete(l);
      primaryBtns.forEach(b => b.classList.toggle('active', b.getAttribute('data-lang') === primaryLang));
      saveLangPrefs();
      renderCompareChips();
      applyLanguageLayout();
    };
  });
  renderCompareChips();
  applyLanguageLayout();
})();"""
