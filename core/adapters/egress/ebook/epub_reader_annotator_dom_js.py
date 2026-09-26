# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Annotator DOM & Rehydration Engine
模块职责：提供正文 DOM 划线安全包裹、离线划线持久化重现还原（Rehydration）与就地悬浮操作气泡。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_annotator_dom_js() -> str:
    """获取正文划线 DOM 包裹、自动还原与就地气泡管理 JavaScript 引擎"""
    return """(function() {
  'use strict';

  // 1. 安全包裹选区 Range 为 <mark>
  function wrapRangeWithHighlight(range, item) {
    if (!range || !item) return null;
    const mark = document.createElement('mark');
    mark.className = `er-hl er-hl-${item.color || 'yellow'}`;
    mark.setAttribute('data-hl-id', item.id);
    if (item.comment) mark.setAttribute('data-has-comment', 'true');
    try {
      range.surroundContents(mark);
      return mark;
    } catch(e) {
      try {
        const frag = range.extractContents();
        mark.appendChild(frag);
        range.insertNode(mark);
        return mark;
      } catch(err) {
        return null;
      }
    }
  }
  window.wrapRangeWithHighlight = wrapRangeWithHighlight;

  // 2. 文本节点安全检索与高亮重现还原 (Rehydration)
  function rehydrateSingleAnnotation(item) {
    if (!item || !item.id || !item.text) return;
    if (document.querySelector(`mark[data-hl-id="${item.id}"]`)) return;
    const searchRoot = (item.chapterId ? document.getElementById(item.chapterId) : null) || document.getElementById('er-book-content');
    if (!searchRoot) return;

    const target = item.text.trim();
    if (target.length < 2) return;

    const walker = document.createTreeWalker(searchRoot, NodeFilter.SHOW_TEXT, null, false);
    let node;
    while ((node = walker.nextNode())) {
      if (node.parentElement && node.parentElement.closest('mark.er-hl, pre, code, script, style')) continue;
      const idx = node.textContent.indexOf(target);
      if (idx !== -1) {
        try {
          const rng = document.createRange();
          rng.setStart(node, idx);
          rng.setEnd(node, idx + target.length);
          wrapRangeWithHighlight(rng, item);
          break;
        } catch(e) {}
      }
    }
  }

  function rehydrateAnnotations(annotations) {
    if (!Array.isArray(annotations) || !annotations.length) return;
    annotations.forEach(item => rehydrateSingleAnnotation(item));
  }
  window.rehydrateAnnotations = rehydrateAnnotations;

  // 3. 正文划线解包与移除
  function removeHighlightMark(hlId) {
    const marks = document.querySelectorAll(`mark[data-hl-id="${hlId}"]`);
    marks.forEach(m => {
      const p = m.parentNode;
      while (m.firstChild) m.parentNode.insertBefore(m.firstChild, m);
      m.remove();
      if (p) p.normalize();
    });
  }
  window.removeHighlightMark = removeHighlightMark;

  // 4. 正文划线就地交互气泡 (In-place Popover)
  const pop = document.getElementById('er-mark-popover');
  let activeHlId = null;

  function closeMarkPopover() {
    if (pop) pop.classList.remove('open');
    activeHlId = null;
  }
  window.closeMarkPopover = closeMarkPopover;

  function showMarkPopover(markEl) {
    if (!pop || !markEl) return;
    const hlId = markEl.getAttribute('data-hl-id');
    if (!hlId) return;
    activeHlId = hlId;

    const item = (window.getAnnotationById ? window.getAnnotationById(hlId) : null) || {
      id: hlId,
      text: markEl.textContent.trim(),
      color: markEl.classList.contains('er-hl-emerald') ? 'emerald' : (markEl.classList.contains('er-hl-pink') ? 'pink' : 'yellow'),
      comment: ''
    };

    // 填充 popover 数据
    const commBox = pop.querySelector('.er-pop-comment');
    const commInput = pop.querySelector('.er-pop-input');
    if (commBox && commInput) {
      if (item.comment) {
        commBox.textContent = '💭 ' + item.comment;
        commBox.style.display = 'block';
        commInput.value = item.comment;
      } else {
        commBox.style.display = 'none';
        commInput.value = '';
      }
    }

    // 点亮当前颜色按钮
    pop.querySelectorAll('.er-pop-color').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-color') === (item.color || 'yellow'));
    });

    // 定位在 mark 正上方中央
    const r = markEl.getBoundingClientRect();
    const popW = 280;
    const left = Math.max(16, Math.min(window.innerWidth - popW - 16, r.left + r.width / 2 - popW / 2));
    const top = Math.max(56, r.top - 10);
    pop.style.left = left + 'px';
    pop.style.top = top + 'px';
    pop.classList.add('open');
  }

  // 监听正文划线点击
  document.addEventListener('click', function(e) {
    const mark = e.target.closest('mark.er-hl');
    if (mark) {
      e.stopPropagation();
      showMarkPopover(mark);
      return;
    }
    if (pop && pop.classList.contains('open') && !pop.contains(e.target)) {
      closeMarkPopover();
    }
  });

  // 绑定 Popover 内部操作
  if (pop) {
    pop.addEventListener('click', e => e.stopPropagation());

    // 换色
    pop.querySelectorAll('.er-pop-color').forEach(btn => {
      btn.onclick = () => {
        if (!activeHlId) return;
        const color = btn.getAttribute('data-color');
        const mark = document.querySelector(`mark[data-hl-id="${activeHlId}"]`);
        if (mark) {
          mark.className = `er-hl er-hl-${color}`;
        }
        if (typeof window.updateAnnotationColor === 'function') {
          window.updateAnnotationColor(activeHlId, color);
        }
        pop.querySelectorAll('.er-pop-color').forEach(b => b.classList.toggle('active', b === btn));
      };
    });

    // 保存批注
    const saveNoteBtn = pop.querySelector('.er-pop-save-note');
    if (saveNoteBtn) {
      saveNoteBtn.onclick = () => {
        if (!activeHlId) return;
        const commInput = pop.querySelector('.er-pop-input');
        const val = commInput ? commInput.value.trim() : '';
        if (typeof window.updateAnnotationComment === 'function') {
          window.updateAnnotationComment(activeHlId, val);
        }
        const mark = document.querySelector(`mark[data-hl-id="${activeHlId}"]`);
        if (mark) {
          if (val) mark.setAttribute('data-has-comment', 'true');
          else mark.removeAttribute('data-has-comment');
        }
        closeMarkPopover();
      };
    }

    // 删除划线
    const delBtn = pop.querySelector('.er-pop-del');
    if (delBtn) {
      delBtn.onclick = () => {
        if (!activeHlId) return;
        if (typeof window.deleteAnnotationById === 'function') {
          window.deleteAnnotationById(activeHlId);
        }
        removeHighlightMark(activeHlId);
        closeMarkPopover();
      };
    }

    // 复制划线文本
    const copyBtn = pop.querySelector('.er-pop-copy');
    if (copyBtn) {
      copyBtn.onclick = () => {
        if (!activeHlId) return;
        const mark = document.querySelector(`mark[data-hl-id="${activeHlId}"]`);
        if (mark && mark.textContent) {
          navigator.clipboard.writeText(mark.textContent.trim()).catch(()=>{});
          copyBtn.textContent = '✅ 已复制';
          setTimeout(() => { copyBtn.textContent = '📋 复制'; }, 1200);
        }
      };
    }

    // 金句卡片
    const cardBtn = pop.querySelector('.er-pop-card');
    if (cardBtn) {
      cardBtn.onclick = () => {
        if (!activeHlId) return;
        const mark = document.querySelector(`mark[data-hl-id="${activeHlId}"]`);
        if (!mark) return;
        closeMarkPopover();
        const text = mark.textContent.trim();
        const cCard = document.getElementById('er-card-modal');
        const cText = document.getElementById('er-card-text');
        const cBook = document.getElementById('er-card-book');
        const cChap = document.getElementById('er-card-chap');
        if (cText) cText.textContent = text;
        if (cBook) cBook.textContent = '《' + (document.title.split(' - ')[0] || '典籍') + '》';
        const parentCard = mark.closest('.er-chapter-card');
        if (cChap) cChap.textContent = (parentCard ? parentCard.querySelector('h1, h2, h3')?.textContent : '') || '经典摘录';
        if (cCard) cCard.classList.add('open');
      };
    }
  }
})();
"""
