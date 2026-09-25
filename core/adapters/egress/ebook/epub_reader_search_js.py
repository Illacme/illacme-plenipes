# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Search Engine JS
模块职责：提供全书即时全文检索、上下文 Snippet 提取、按章分组统计与正文穿透聚焦脉冲动画。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_search_js() -> str:
    """获取 EPUB 全书全文检索与高亮穿透 JavaScript 引擎"""
    return """(function() {
  'use strict';
  const searchInput = document.getElementById('er-search-input');
  const searchMeta = document.getElementById('er-search-meta');
  const searchResults = document.getElementById('er-search-results');
  const searchCountBadge = document.getElementById('er-search-count');
  const bookContainer = document.getElementById('er-book-content');

  let chaptersCache = null;
  let debounceTimer = null;
  let activeFocusMark = null;

  // 1. 初始化纯文本索引缓存
  function buildIndex() {
    if (!bookContainer) return [];
    const cards = bookContainer.querySelectorAll('.er-chapter-card');
    const index = [];
    cards.forEach(card => {
      const titleEl = card.querySelector('h1, h2, h3');
      const title = (titleEl ? titleEl.textContent : '典籍章节').trim();
      const text = card.textContent || '';
      index.push({
        id: card.id,
        title: title,
        element: card,
        text: text
      });
    });
    return index;
  }

  // 2. 搜索执行与 Snippet 提取
  function executeSearch(query) {
    if (!chaptersCache) chaptersCache = buildIndex();
    if (!searchResults) return;

    query = (query || '').trim();
    if (!query) {
      if (searchMeta) searchMeta.textContent = '输入关键词检索全书典籍';
      if (searchCountBadge) searchCountBadge.textContent = '0';
      searchResults.innerHTML = '<div class="er-search-empty">输入关键词，即可秒级全文检索所有章节与段落。</div>';
      return;
    }

    const lowerQuery = query.toLowerCase();
    const matches = [];

    chaptersCache.forEach(ch => {
      const fullText = ch.text;
      const lowerText = fullText.toLowerCase();
      let pos = 0;
      let count = 0;

      while ((pos = lowerText.indexOf(lowerQuery, pos)) !== -1 && count < 20) {
        const start = Math.max(0, pos - 30);
        const end = Math.min(fullText.length, pos + query.length + 35);
        let snippet = fullText.slice(start, end).replace(/\\s+/g, ' ');

        const matchIdx = snippet.toLowerCase().indexOf(lowerQuery);
        if (matchIdx !== -1) {
          const before = snippet.slice(0, matchIdx);
          const matched = snippet.slice(matchIdx, matchIdx + query.length);
          const after = snippet.slice(matchIdx + query.length);
          snippet = (start > 0 ? '...' : '') + before + '<mark class="er-search-match">' + matched + '</mark>' + after + (end < fullText.length ? '...' : '');
        }

        matches.push({
          chapterId: ch.id,
          chapterTitle: ch.title,
          snippetHtml: snippet,
          rawQuery: query
        });

        pos += query.length;
        count++;
      }
    });

    if (searchCountBadge) searchCountBadge.textContent = matches.length;
    if (searchMeta) searchMeta.textContent = `共在全书中找到 ${matches.length} 处匹配`;

    if (!matches.length) {
      searchResults.innerHTML = '<div class="er-search-empty">未找到与“' + query + '”匹配的内容。</div>';
      return;
    }

    searchResults.innerHTML = matches.map(m => `
      <div class="er-search-item" data-chap="${m.chapterId}">
        <div class="er-search-item-chap">📖 ${m.chapterTitle}</div>
        <div class="er-search-item-snippet">${m.snippetHtml}</div>
      </div>
    `).join('');

    searchResults.querySelectorAll('.er-search-item').forEach(item => {
      item.onclick = () => {
        const chapId = item.getAttribute('data-chap');
        jumpAndHighlight(chapId, query);
      };
    });
  }

  // 3. 目标章节跳转与聚焦脉冲动画
  function jumpAndHighlight(chapId, query) {
    if (window.navigateToTarget) {
      window.navigateToTarget('#' + chapId);
    }
    const card = document.getElementById(chapId);
    if (!card) return;

    if (activeFocusMark && activeFocusMark.parentNode) {
      const parent = activeFocusMark.parentNode;
      parent.replaceChild(document.createTextNode(activeFocusMark.textContent), activeFocusMark);
      parent.normalize();
      activeFocusMark = null;
    }

    // 在目标章节内查找第一个匹配文本节点并包裹焦点 mark
    const walker = document.createTreeWalker(card, NodeFilter.SHOW_TEXT, null, false);
    let node;
    const lowerQuery = query.toLowerCase();

    while ((node = walker.nextNode())) {
      const idx = node.nodeValue.toLowerCase().indexOf(lowerQuery);
      if (idx !== -1) {
        const span = document.createElement('mark');
        span.className = 'er-search-focus';
        span.textContent = node.nodeValue.substr(idx, query.length);

        const afterText = node.splitText(idx);
        afterText.nodeValue = afterText.nodeValue.substr(query.length);
        node.parentNode.insertBefore(span, afterText);

        activeFocusMark = span;

        // 如果是卷轴模式，顺畅滚动到聚焦元素中心
        if (document.documentElement.getAttribute('data-read-mode') === 'scroll') {
          setTimeout(() => {
            span.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }, 80);
        }

        setTimeout(() => {
          if (span && span.parentNode) {
            const p = span.parentNode;
            p.replaceChild(document.createTextNode(span.textContent), span);
            p.normalize();
            if (activeFocusMark === span) activeFocusMark = null;
          }
        }, 3800);
        break;
      }
    }
  }

  // 4. 输入监听与键盘快捷键 (⌘K / Ctrl+K)
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => executeSearch(searchInput.value), 180);
    });
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        searchInput.value = '';
        executeSearch('');
        searchInput.blur();
      }
    });
  }

  window.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      const sTab = document.getElementById('er-stab-search');
      if (sTab) sTab.click();
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
      }
    }
  });

  // 全局快捷方法
  window.openEpubSearch = function() {
    const sTab = document.getElementById('er-stab-search');
    if (sTab) sTab.click();
    if (searchInput) searchInput.focus();
  };
})();
"""
