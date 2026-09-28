# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Reader Pager & Quick Jump Controls JS
模块职责：提供 EPUB 阅读器底部翻页控制器、首页/尾页快捷按钮、输入跳转与键盘快捷键交互。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_pager_js() -> str:
    """获取底部页码导航与快捷跳转交互 JavaScript 脚本"""
    return r"""
(function() {
  'use strict';

  function initPagerControls() {
    const btnFirst = document.getElementById('er-nav-first');
    const btnLast = document.getElementById('er-nav-last');
    const btnPrev = document.getElementById('er-nav-prev-footer');
    const btnNext = document.getElementById('er-nav-next-footer');
    const pageBox = document.getElementById('er-footer-page-box');
    const pageText = document.getElementById('er-footer-page');
    const jumpWrap = document.getElementById('er-footer-page-jump');
    const jumpInput = document.getElementById('er-page-jump-input');
    const jumpTotal = document.getElementById('er-page-jump-total');

    if (!pageBox || !pageText || !jumpInput) return;

    if (btnFirst) {
      btnFirst.onclick = (e) => {
        e.stopPropagation();
        if (typeof window.goToFirstPage === 'function') window.goToFirstPage();
      };
    }
    if (btnLast) {
      btnLast.onclick = (e) => {
        e.stopPropagation();
        if (typeof window.goToLastPage === 'function') window.goToLastPage();
      };
    }
    if (btnPrev) {
      btnPrev.onclick = (e) => {
        e.stopPropagation();
        if (typeof window.prevPage === 'function') window.prevPage();
      };
    }
    if (btnNext) {
      btnNext.onclick = (e) => {
        e.stopPropagation();
        if (typeof window.nextPage === 'function') window.nextPage();
      };
    }

    function parsePageInfo() {
      const txt = (pageText.textContent || '').trim();
      const isPoly = document.body && document.body.classList.contains('wb-concordance');
      if (isPoly) {
        const curM = txt.match(/第\s*(\d+)\s*卷/), totM = txt.match(/共\s*(\d+)\s*卷/);
        const totCards = document.querySelectorAll('.er-chapter-card').length || 1;
        const curIdx = (typeof window.getReaderCurPage === 'function') ? (window.getReaderCurPage() + 1) : 1;
        return { cur: curM ? parseInt(curM[1], 10) : curIdx, total: totM ? parseInt(totM[1], 10) : totCards, unit: totM ? '卷' : '' };
      }
      const match = txt.match(/(\d+)(?:-(\d+))?\s*\/\s*(\d+)/);
      if (match) return { cur: parseInt(match[1], 10) || 1, total: parseInt(match[3], 10) || 1, unit: '' };
      const cur = (typeof window.getReaderCurPage === 'function') ? (window.getReaderCurPage() + 1) : 1;
      const tot = (typeof window.getReaderTotalPages === 'function') ? window.getReaderTotalPages() : (document.querySelectorAll('.er-chapter-card').length || 1);
      return { cur, total: Math.max(1, tot), unit: '' };
    }

    function activateJumpInput() {
      const info = parsePageInfo();
      pageText.style.display = 'none';
      jumpWrap.style.display = 'inline-flex';
      jumpInput.max = String(info.total);
      jumpInput.value = String(info.cur);
      jumpInput.placeholder = info.unit || '页';
      if (jumpTotal) jumpTotal.textContent = info.unit ? `/ ${info.total} ${info.unit}` : `/ ${info.total}`;
      setTimeout(() => {
        jumpInput.focus();
        jumpInput.select();
      }, 20);
    }

    function commitJump() {
      if (jumpWrap.style.display === 'none') return;
      const info = parsePageInfo();
      const val = parseInt(jumpInput.value, 10);
      jumpWrap.style.display = 'none';
      pageText.style.display = '';
      if (!isNaN(val) && val >= 1) {
        const target = Math.min(val, info.total);
        if (typeof window.goToPage === 'function') {
          window.goToPage(target);
        }
      }
    }

    function cancelJump() {
      jumpWrap.style.display = 'none';
      pageText.style.display = '';
    }

    pageBox.onclick = () => {
      if (jumpWrap.style.display === 'none' || !jumpWrap.style.display) {
        activateJumpInput();
      }
    };

    jumpInput.onkeydown = (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        commitJump();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        cancelJump();
      }
    };

    jumpInput.onblur = () => {
      commitJump();
    };

    window.addEventListener('keydown', (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (document.documentElement.getAttribute('data-read-mode') !== 'paginated') return;
      if (e.key === 'g' || e.key === 'G') {
        e.preventDefault();
        activateJumpInput();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => setTimeout(initPagerControls, 100));
  } else {
    setTimeout(initPagerControls, 100);
  }
})();
"""
