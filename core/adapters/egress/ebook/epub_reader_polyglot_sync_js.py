# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Polyglot Sync & Highlight Controller
模块职责：提供多语对照模式下的段落级视觉对齐、高亮微光联动与窄屏自适应对焦。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_reader_polyglot_sync_js() -> str:
    """获取多语对照段落联动与微光对齐 JavaScript 脚本"""
    return """(function() {
  'use strict';

  let highlightTimer = null;

  function clearActiveHighlight() {
    if (highlightTimer) { clearTimeout(highlightTimer); highlightTimer = null; }
    document.querySelectorAll('.wb-para-active').forEach(el => el.classList.remove('wb-para-active'));
  }

  function indexBlockParagraphs(block) {
    if (!block || block._indexed) return;
    const cols = block.querySelectorAll('.wb-poly-content');
    if (!cols || cols.length < 2) return;
    cols.forEach(col => {
      const paras = Array.from(col.children).filter(el => {
        const tn = el.tagName ? el.tagName.toLowerCase() : '';
        return /^(p|blockquote|li|pre|table|h1|h2|h3|h4|h5|h6|div)$/.test(tn);
      });
      paras.forEach((p, idx) => {
        if (!p.hasAttribute('data-para-idx')) {
          p.setAttribute('data-para-idx', String(idx));
          p.classList.add('wb-para-target');
        }
      });
    });
    block._indexed = true;
  }

  function setupParagraphClickDelegation() {
    if (document._hasPolyParaClick) return;
    document._hasPolyParaClick = true;

    document.addEventListener('click', (e) => {
      if (!document.body || !document.body.classList.contains('wb-concordance')) return;
      const targetPara = e.target.closest('.wb-para-target');
      if (!targetPara) {
        if (!e.target.closest('.wb-polyglot-bar, .wb-poly-header')) clearActiveHighlight();
        return;
      }
      const block = targetPara.closest('.wb-polyglot-block');
      if (!block) return;
      const idx = targetPara.getAttribute('data-para-idx');
      if (idx === null) return;

      clearActiveHighlight();

      const matched = block.querySelectorAll(`.wb-para-target[data-para-idx="${idx}"]`);
      matched.forEach(p => p.classList.add('wb-para-active'));

      const isScroll = document.documentElement.getAttribute('data-read-mode') === 'scroll';
      if (isScroll && window.innerWidth <= 800) {
        matched.forEach(p => {
          if (p !== targetPara && typeof p.scrollIntoView === 'function') {
            const rect = p.getBoundingClientRect();
            if (rect.top < 0 || rect.bottom > window.innerHeight) {
              p.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
          }
        });
      }

      highlightTimer = setTimeout(clearActiveHighlight, 4500);
    });
  }

  window.initPolyglotParaSync = function() {
    if (!document.body || !document.body.classList.contains('wb-concordance')) return;
    document.querySelectorAll('.wb-polyglot-block').forEach(b => {
      b._indexed = false;
      indexBlockParagraphs(b);
    });
  };

  setupParagraphClickDelegation();

  const initSync = () => setTimeout(window.initPolyglotParaSync, 200);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSync);
  } else {
    initSync();
  }
})();
"""
