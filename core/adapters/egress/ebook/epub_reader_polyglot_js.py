# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Polyglot Controller
模块职责：为 EPUB 在线阅读器提供多语言平行分栏对照中枢、顶部控制条与多语种联动。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_reader_polyglot_js() -> str:
    """获取多语对照交互与分栏控制 JavaScript 脚本"""
    return """(function() {
  'use strict';

  const LANG_NAMES = { 'zh': '🇨🇳 中', 'en': '🇬🇧 EN', 'ja': '🇯🇵 日', 'fr': '🇫🇷 法', 'de': '🇩🇪 德', 'es': '🇪🇸 西', 'ru': '🇷🇺 俄' };
  const FULL_LANG_NAMES = { 'zh': '简体中文', 'en': 'English', 'ja': '日本語', 'fr': 'Français', 'de': 'Deutsch', 'es': 'Español', 'ru': 'Русский' };
  let primaryLang = 'zh', compareLangs = new Set(), savedCompare = null;
  try {
    if (typeof localStorage !== 'undefined') {
      primaryLang = localStorage.getItem('er_poly_primary') || 'zh';
      savedCompare = localStorage.getItem('er_poly_compare');
      if (savedCompare !== null) savedCompare.split(',').filter(Boolean).forEach(l => compareLangs.add(l));
    }
  } catch(e) {}

  function detectAllLanguages() {
    const langs = new Set();
    document.querySelectorAll('.wb-poly-item[data-lang], .wb-poly-column[data-lang]').forEach(el => {
      const l = el.getAttribute('data-lang'); if (l) langs.add(l.toLowerCase());
    });
    return Array.from(langs);
  }

  function savePrefs() {
    try {
      localStorage.setItem('er_poly_primary', primaryLang);
      localStorage.setItem('er_poly_compare', Array.from(compareLangs).join(','));
    } catch (e) {}
  }

  function renderPolyglotBar(allLangs) {
    let slot = document.getElementById('er-topbar-polyglot');
    if (!slot) {
      const topbar = document.querySelector('.er-topbar');
      const controls = document.querySelector('.er-controls');
      if (topbar && controls) {
        slot = document.createElement('div');
        slot.id = 'er-topbar-polyglot';
        slot.className = 'er-topbar-polyglot';
        controls.before(slot);
      }
    }
    if (!slot) return;

    let bar = document.getElementById('er-polyglot-bar');
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'er-polyglot-bar';
      bar.className = 'er-polyglot-bar';
      slot.appendChild(bar);
    }

    if (!allLangs || allLangs.length < 2) {
      bar.style.display = 'none'; document.body.classList.remove('wb-concordance'); return;
    }
    bar.style.display = 'inline-flex';
    if (!allLangs.includes(primaryLang)) primaryLang = allLangs[0];
    if (savedCompare === null && compareLangs.size === 0) {
      allLangs.filter(l => l !== primaryLang).forEach(l => compareLangs.add(l));
    }
    let primaryBtnsHtml = allLangs.map(l => {
      const act = l === primaryLang ? ' active' : '', fn = FULL_LANG_NAMES[l] || l.toUpperCase();
      return `<button type="button" class="er-poly-pitem${act}" data-lang="${l}" title="切换主语言为 ${fn}">${LANG_NAMES[l] || l.toUpperCase()}</button>`;
    }).join('');
    let compareChipsHtml = allLangs.filter(l => l !== primaryLang).map(l => {
      const act = compareLangs.has(l) ? ' active' : '', icon = compareLangs.has(l) ? '☑ ' : '☐ ', fn = FULL_LANG_NAMES[l] || l.toUpperCase();
      return `<button type="button" class="er-poly-cchip${act}" data-lang="${l}" title="切换 ${fn} 对照栏">${icon}${LANG_NAMES[l] || l.toUpperCase()}</button>`;
    }).join('');
    bar.innerHTML = `<div class="er-poly-group er-poly-primary-group"><span class="er-poly-label">主语:</span><div class="er-poly-capsule">${primaryBtnsHtml}</div></div><span class="er-poly-sep">|</span><div class="er-poly-group er-poly-compare-group"><span class="er-poly-label">对照:</span><div class="er-poly-chips">${compareChipsHtml}</div></div>`;
    bar.querySelectorAll('.er-poly-pitem').forEach(btn => {
      btn.onclick = () => {
        const l = btn.getAttribute('data-lang'); if (l === primaryLang) return;
        const oldP = primaryLang; primaryLang = l; compareLangs.delete(l);
        if (allLangs.includes(oldP)) compareLangs.add(oldP);
        savePrefs(); renderPolyglotBar(allLangs); applyLanguageLayout();
      };
    });
    bar.querySelectorAll('.er-poly-cchip').forEach(btn => {
      btn.onclick = () => {
        const l = btn.getAttribute('data-lang');
        if (compareLangs.has(l)) compareLangs.delete(l); else compareLangs.add(l);
        savePrefs(); renderPolyglotBar(allLangs); applyLanguageLayout();
      };
    });
  }

  function applyLanguageLayout() {
    const isCompare = compareLangs.size > 0;
    document.body.classList.toggle('wb-concordance', isCompare);
    const activeOrdered = isCompare ? [primaryLang, ...Array.from(compareLangs)] : [primaryLang];
    document.querySelectorAll('.wb-polyglot-block').forEach(block => {
      block.querySelectorAll('.wb-poly-item, .wb-poly-column').forEach(item => {
        const l = (item.getAttribute('data-lang') || '').toLowerCase(), pos = activeOrdered.indexOf(l);
        if (pos >= 0) {
          item.classList.remove('wb-poly-hidden'); item.style.display = ''; item.style.order = String(pos + 1);
          const badge = item.querySelector('.wb-lang-badge');
          if (badge) badge.textContent = l === primaryLang ? `${l.toUpperCase()} 主语言` : `${l.toUpperCase()} 对照栏`;
        } else { item.classList.add('wb-poly-hidden'); item.style.display = 'none'; }
      });
    });
    setupPolyglotWheelSync();
    if (typeof window.updatePagination === 'function') window.updatePagination();
    if (typeof window.onPolyglotRenderPage === 'function') {
      const p = typeof window.getReaderCurPage === 'function' ? window.getReaderCurPage() : 0;
      window.onPolyglotRenderPage(p, 1);
    }
    if (typeof window.initPolyglotParaSync === 'function') window.initPolyglotParaSync();
  }

  let isSyncingScroll = false;
  function setupPolyglotWheelSync() {
    document.querySelectorAll('.wb-polyglot-block').forEach(block => {
      const contents = block.querySelectorAll('.wb-poly-content');
      if (contents.length < 2) return;
      contents.forEach(col => {
        if (col._hasPolySync) return;
        col._hasPolySync = true;
        col.addEventListener('scroll', () => {
          if (isSyncingScroll) return;
          isSyncingScroll = true;
          const sMax = col.scrollHeight - col.clientHeight, ratio = sMax > 0 ? col.scrollTop / sMax : 0;
          contents.forEach(other => { if (other !== col) { const oMax = other.scrollHeight - other.clientHeight; if (oMax > 0) other.scrollTop = ratio * oMax; } });
          requestAnimationFrame(() => { isSyncingScroll = false; });
        }, { passive: true });
      });
    });
  }

  function getCardMeta(card, allCards) {
    if (!card) return { type: 'chapter', chapterNum: 1, totalChapters: 1 };
    const cid = (card.id || '').toLowerCase();
    const hasClass = (cls) => !!(card.classList && typeof card.classList.contains === 'function' && card.classList.contains(cls));
    const hasSel = (sel) => !!(typeof card.querySelector === 'function' && card.querySelector(sel));
    if (hasClass('er-cover-card') || cid.includes('cover') || hasSel('.wb-cover-card, .er-cover-wrapper')) return { type: 'cover' };
    if (cid.includes('nav') || hasSel('.er-toc-tree') || (hasSel('h1, h2, h3') && /^(目录|table of contents)/i.test((card.querySelector('h1, h2, h3')?.textContent || '').trim()))) return { type: 'nav' };
    if (cid.includes('colophon') || cid.includes('copyright') || hasSel('.colophon-card, .colophon-page, .colophon-header')) return { type: 'colophon' };
    let chNum = 0, totCh = 0;
    (allCards || []).forEach(c => {
      const id = (c.id || '').toLowerCase();
      const isAux = (c.classList && typeof c.classList.contains === 'function' && c.classList.contains('er-cover-card')) || id.includes('cover') || id.includes('nav') || id.includes('colophon') || id.includes('copyright') || (typeof c.querySelector === 'function' && (c.querySelector('.wb-cover-card') || c.querySelector('.er-toc-tree') || c.querySelector('.colophon-card')));
      if (!isAux) { totCh++; if (c === card) chNum = totCh; }
    });
    return { type: 'chapter', chapterNum: chNum || 1, totalChapters: totCh || 1 };
  }

  function getPrimaryCol(cols, card) {
    if (!cols || !cols.length) return null;
    if (card && typeof card.querySelector === 'function') {
      const p = card.querySelector(`.wb-poly-column[data-lang="${primaryLang}"] .wb-poly-content`);
      if (p && !p.closest('.wb-poly-hidden')) return p;
    }
    return cols[0];
  }

  function getPolyglotTargets(cols, card) {
    if (!cols || !cols.length) return [0];
    const pCol = getPrimaryCol(cols, card) || cols[0], vh = pCol.clientHeight || 600, maxScroll = Math.max(0, pCol.scrollHeight - vh);
    if (maxScroll <= 20) return [0];
    const targets = [0]; let pos = 0;
    while (pos + vh < maxScroll) {
      let nextPos = pos + vh;
      if (pCol && typeof pCol.querySelectorAll === 'function') {
        const items = pCol.querySelectorAll('p, li, h1, h2, h3, h4, pre, blockquote, tr'), cTop = pCol.offsetTop || 0;
        for (let i = 0; i < items.length; i++) {
          const top = items[i].offsetTop - cTop, bottom = top + items[i].offsetHeight;
          if (top < nextPos && bottom > nextPos && (nextPos - top < 72) && top > pos + 100) { nextPos = top; break; }
        }
      }
      pos = nextPos; targets.push(pos);
    }
    if (maxScroll - pos >= 40) targets.push(maxScroll);
    else if (targets.length > 1) targets[targets.length - 1] = maxScroll;
    else targets.push(maxScroll);
    return targets;
  }

  function applyPolyglotScroll(cols, card, curSub, totSub, targets) {
    const pCol = getPrimaryCol(cols, card) || cols[0], pTarget = targets[curSub - 1] || 0, ratio = totSub > 1 ? (curSub - 1) / (totSub - 1) : 0;
    cols.forEach(c => {
      if (c === pCol) c.scrollTop = pTarget;
      else { const cMax = Math.max(0, c.scrollHeight - c.clientHeight); c.scrollTop = Math.round(ratio * cMax); }
    });
  }

  function updateFooterPage(curIdx, totalCards, curSub, totSub) {
    const fPage = document.getElementById('er-footer-page'), pBar = document.getElementById('er-progress-bar');
    const cards = Array.from(document.querySelectorAll('.er-chapter-card')), meta = getCardMeta(cards[curIdx], cards);
    if (fPage) {
      if (meta.type === 'cover') fPage.textContent = '📕 典籍封面与扉页';
      else if (meta.type === 'nav') fPage.textContent = totSub > 1 ? `📑 全书目录索引 (第 ${curSub}/${totSub} 页)` : '📑 全书目录索引';
      else if (meta.type === 'colophon') fPage.textContent = totSub > 1 ? `📜 出版版权与版记 (第 ${curSub}/${totSub} 页)` : '📜 出版版权与版记';
      else fPage.textContent = totSub > 1 ? `第 ${meta.chapterNum} 卷 (第 ${curSub}/${totSub} 页) · 共 ${meta.totalChapters} 卷` : `第 ${meta.chapterNum} 卷 · 共 ${meta.totalChapters} 卷`;
    }
    if (pBar) {
      const ratio = ((curIdx + (curSub - 1) / Math.max(1, totSub)) / Math.max(1, totalCards)) * 100;
      pBar.style.width = Math.min(100, Math.max(0, ratio)) + '%';
    }
  }

  let isFlipping = false, pendingFlip = null;
  function flipSubPage(curCard, isNext, curSub, totSub, curIdx, totalCards, cols, targets) {
    if (isFlipping) { pendingFlip = isNext; return; }
    isFlipping = true;
    const outClass = isNext ? 'wb-flip-slide-out-left' : 'wb-flip-slide-out-right', inClass = isNext ? 'wb-flip-slide-in-right' : 'wb-flip-slide-in-left';
    curCard.classList.remove('wb-flip-slide-out-left', 'wb-flip-slide-out-right', 'wb-flip-slide-in-right', 'wb-flip-slide-in-left');
    curCard.classList.add(outClass); applyPolyglotScroll(cols, curCard, curSub, totSub, targets); updateFooterPage(curIdx, totalCards, curSub, totSub);
    setTimeout(() => {
      curCard.classList.remove(outClass); curCard.classList.add(inClass);
      setTimeout(() => {
        curCard.classList.remove(inClass); isFlipping = false;
        if (pendingFlip !== null) {
          const nextDir = pendingFlip; pendingFlip = null;
          if (!window.handlePolyglotPaging(nextDir)) {
            if (nextDir && typeof window.nextPage === 'function') window.nextPage();
            else if (!nextDir && typeof window.prevPage === 'function') window.prevPage();
          }
        }
      }, 140);
    }, 110);
  }

  let lastWheelTime = 0;
  if (typeof window !== 'undefined' && typeof window.addEventListener === 'function') {
    window.addEventListener('wheel', (e) => {
      if (!document.body || !document.body.classList.contains('wb-concordance') || document.documentElement.getAttribute('data-read-mode') !== 'paginated') return;
      if (Math.abs(e.deltaY) < 18) return;
      const now = Date.now();
      if (now - lastWheelTime < 320) { if (isFlipping) pendingFlip = e.deltaY > 0; e.preventDefault(); return; }
      lastWheelTime = now; e.preventDefault();
      const isNext = e.deltaY > 0;
      if (!window.handlePolyglotPaging(isNext)) {
        if (isNext && typeof window.nextPage === 'function') window.nextPage();
        else if (!isNext && typeof window.prevPage === 'function') window.prevPage();
      }
    }, { passive: false });
  }

  window.handlePolyglotPaging = function(isNext) {
    if (!document.body || !document.body.classList.contains('wb-concordance') || document.documentElement.getAttribute('data-read-mode') !== 'paginated') return false;
    const curIdx = (typeof window.getReaderCurPage === 'function') ? window.getReaderCurPage() : 0;
    const cards = document.querySelectorAll('.er-chapter-card'), curCard = cards[curIdx]; if (!curCard) return false;
    const cols = Array.from(curCard.querySelectorAll('.wb-poly-column:not(.wb-poly-hidden) .wb-poly-content')); if (!cols.length) return false;
    const targets = getPolyglotTargets(cols, curCard), totSub = targets.length; if (totSub <= 1) return false;
    let curSub = curCard._subPage || 1; if (curSub > totSub) curSub = totSub;
    if (isNext && curSub >= totSub) return false;
    if (!isNext && curSub <= 1) return false;
    if (isFlipping) { pendingFlip = isNext; return true; }
    if (isNext && curSub < totSub) {
      curSub++; curCard._subPage = curSub; flipSubPage(curCard, true, curSub, totSub, curIdx, cards.length, cols, targets); return true;
    } else if (!isNext && curSub > 1) {
      curSub--; curCard._subPage = curSub; flipSubPage(curCard, false, curSub, totSub, curIdx, cards.length, cols, targets); return true;
    }
    return false;
  };

  window.handlePolyglotGoToPage = function(targetPage, maxPages) {
    if (!document.body || !document.body.classList.contains('wb-concordance') || document.documentElement.getAttribute('data-read-mode') !== 'paginated') return false;
    const cards = Array.from(document.querySelectorAll('.er-chapter-card')); if (!cards.length) return false;
    if (targetPage <= 1) {
      cards[0]._subPage = 1; if (typeof window.selectChapterByIndex === 'function') window.selectChapterByIndex(0); return true;
    }
    let targetIdx = -1;
    cards.forEach((c, idx) => { const meta = getCardMeta(c, cards); if (meta.type === 'chapter' && meta.chapterNum === targetPage) targetIdx = idx; });
    if (targetIdx < 0) targetIdx = targetPage >= maxPages ? (cards.length - 1) : Math.max(0, Math.min(cards.length - 1, targetPage - 1));
    const cols = Array.from(cards[targetIdx].querySelectorAll('.wb-poly-column:not(.wb-poly-hidden) .wb-poly-content'));
    cards[targetIdx]._subPage = targetPage >= maxPages ? Math.max(1, getPolyglotTargets(cols, cards[targetIdx]).length) : 1;
    if (typeof window.selectChapterByIndex === 'function') window.selectChapterByIndex(targetIdx);
    return true;
  };

  window.onPolyglotRenderPage = function(curIdx, totalCards) {
    if (!document.body || !document.body.classList.contains('wb-concordance') || document.documentElement.getAttribute('data-read-mode') !== 'paginated') return;
    const cards = document.querySelectorAll('.er-chapter-card'), card = cards[curIdx]; if (!card) return;
    const cols = Array.from(card.querySelectorAll('.wb-poly-column:not(.wb-poly-hidden) .wb-poly-content')); if (!cols.length) return;
    const targets = getPolyglotTargets(cols, card), totSub = targets.length;
    if (!card._subPage || card._subPage > totSub) card._subPage = 1;
    applyPolyglotScroll(cols, card, card._subPage, totSub, targets);
    updateFooterPage(curIdx, totalCards, card._subPage, totSub);
  };

  window.initPolyglotBar = function() {
    const allLangs = detectAllLanguages();
    if (allLangs && allLangs.length >= 2) { renderPolyglotBar(allLangs); applyLanguageLayout(); }
  };
  const initFn = () => setTimeout(window.initPolyglotBar, 150);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initFn); else initFn();
})();
"""
