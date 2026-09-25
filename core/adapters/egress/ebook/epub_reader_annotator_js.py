# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Annotator & Quote Card JS Engine
模块职责：提供划词高亮、随笔批注管理、Markdown 笔记导出及金句卡片生成前端 JavaScript 引擎。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_annotator_js() -> str:
    """获取划词高亮、批注记录与金句卡片核心前端引擎 JavaScript"""
    return """(function() {
  'use strict';
  const fBar = document.getElementById('er-floating-bar');
  const cardModal = document.getElementById('er-card-modal');
  const noteModal = document.getElementById('er-note-modal');
  const noteInput = document.getElementById('er-note-input');
  const noteTargetText = document.getElementById('er-note-target-text');
  const notesList = document.getElementById('er-notes-list');
  const notesCountBadge = document.getElementById('er-notes-count');

  const bookId = 'er_notes_' + (document.title.split(' - ')[0] || 'book').replace(/[^a-zA-Z0-9_\u4e00-\u9fa5]/g, '_');
  let annotations = [];
  try { annotations = JSON.parse(localStorage.getItem(bookId) || '[]'); } catch(e){}

  let currentSelection = { text: '', range: null, chapterId: '', chapterTitle: '' };

  // 1. 划选监听与浮动菜单定位
  function handleSelection() {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) {
      if (fBar) fBar.style.display = 'none';
      return;
    }
    const text = sel.toString().trim();
    if (text.length < 2) {
      if (fBar) fBar.style.display = 'none';
      return;
    }
    const range = sel.getRangeAt(0);
    const container = range.commonAncestorContainer;
    const parentCard = (container.nodeType === 1 ? container : container.parentElement).closest('.er-chapter-card');
    if (!parentCard) {
      if (fBar) fBar.style.display = 'none';
      return;
    }

    const rect = range.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return;

    currentSelection = {
      text: text,
      range: range.cloneRange(),
      chapterId: parentCard.id,
      chapterTitle: (parentCard.querySelector('h1, h2, h3') || {}).textContent || '典籍正文'
    };

    if (fBar) {
      fBar.style.left = Math.max(120, Math.min(window.innerWidth - 120, rect.left + rect.width / 2)) + 'px';
      fBar.style.top = Math.max(60, rect.top) + 'px';
      fBar.style.display = 'flex';
    }
  }

  document.addEventListener('mouseup', () => setTimeout(handleSelection, 20));
  document.addEventListener('touchend', () => setTimeout(handleSelection, 50));
  document.addEventListener('mousedown', (e) => {
    if (fBar && !fBar.contains(e.target) && !e.target.closest('mark.er-hl')) {
      fBar.style.display = 'none';
    }
  });

  // 2. 荧光划线
  function addHighlight(color, comment = '') {
    if (!currentSelection.text) return;
    const item = {
      id: 'hl_' + Date.now(),
      text: currentSelection.text,
      chapterId: currentSelection.chapterId,
      chapterTitle: currentSelection.chapterTitle.trim(),
      color: color || 'yellow',
      comment: comment,
      time: new Date().toLocaleDateString()
    };
    annotations.unshift(item);
    saveAnnotations();
    renderNotesList();
    if (fBar) fBar.style.display = 'none';
    window.getSelection().removeAllRanges();
  }

  document.querySelectorAll('.er-fbtn[data-color]').forEach(btn => {
    btn.onclick = () => addHighlight(btn.getAttribute('data-color'));
  });

  // 3. 随手批注
  const noteBtn = document.getElementById('er-fbtn-note');
  if (noteBtn) {
    noteBtn.onclick = () => {
      if (!currentSelection.text) return;
      if (fBar) fBar.style.display = 'none';
      if (noteTargetText) noteTargetText.textContent = '“' + currentSelection.text.slice(0, 100) + '...”';
      if (noteInput) noteInput.value = '';
      if (noteModal) noteModal.classList.add('open');
      setTimeout(() => { if (noteInput) noteInput.focus(); }, 100);
    };
  }

  const noteCancel = document.getElementById('er-note-cancel-btn');
  const noteSave = document.getElementById('er-note-save-btn');
  if (noteCancel) noteCancel.onclick = () => { if (noteModal) noteModal.classList.remove('open'); };
  if (noteSave) {
    noteSave.onclick = () => {
      const val = (noteInput ? noteInput.value : '').trim();
      addHighlight('emerald', val);
      if (noteModal) noteModal.classList.remove('open');
    };
  }

  // 4. 复制文本
  const copyBtn = document.getElementById('er-fbtn-copy');
  if (copyBtn) {
    copyBtn.onclick = () => {
      if (currentSelection.text) {
        navigator.clipboard.writeText(currentSelection.text).catch(()=>{});
        if (fBar) fBar.style.display = 'none';
      }
    };
  }

  // 5. 金句分享卡片生成
  const cardBtn = document.getElementById('er-fbtn-card');
  if (cardBtn) {
    cardBtn.onclick = () => {
      if (!currentSelection.text) return;
      if (fBar) fBar.style.display = 'none';
      const cText = document.getElementById('er-card-text');
      const cBook = document.getElementById('er-card-book');
      const cChap = document.getElementById('er-card-chap');
      if (cText) cText.textContent = currentSelection.text;
      if (cBook) cBook.textContent = '《' + (document.title.split(' - ')[0] || '典籍') + '》';
      if (cChap) cChap.textContent = currentSelection.chapterTitle || '经典章回';
      if (cardModal) cardModal.classList.add('open');
    };
  }

  const cardClose = document.getElementById('er-card-close-btn');
  const cardCopy = document.getElementById('er-card-copy-btn');
  const cardSave = document.getElementById('er-card-save-btn');
  if (cardClose) cardClose.onclick = () => { if (cardModal) cardModal.classList.remove('open'); };
  if (cardCopy) {
    cardCopy.onclick = () => {
      const t = document.getElementById('er-card-text');
      const b = document.getElementById('er-card-book');
      if (t && b) {
        navigator.clipboard.writeText(`“${t.textContent}”\\n—— 摘自 ${b.textContent}`).catch(()=>{});
        cardCopy.textContent = '✅ 已复制金句';
        setTimeout(() => { cardCopy.textContent = '📋 复制金句文本'; }, 1500);
      }
    };
  }
  if (cardSave) {
    cardSave.onclick = () => {
      const t = document.getElementById('er-card-text');
      const b = document.getElementById('er-card-book');
      const c = document.getElementById('er-card-chap');
      const text = t ? t.textContent.trim() : '';
      const book = b ? b.textContent.replace(/[《》]/g, '').trim() : '';
      const chap = c ? c.textContent.trim() : '';
      if (typeof window.generateQuotePoster === 'function') {
        window.generateQuotePoster(text, book, chap);
      } else {
        const textToShare = `═════════════════════════\\n  ${book} · 经典摘录\\n═════════════════════════\\n\\n“${text}”\\n\\n── 出自 Illacme Plenipes 数字典籍`;
        navigator.clipboard.writeText(textToShare).catch(()=>{});
        cardSave.textContent = '✅ 海报文本已复制';
        setTimeout(() => { cardSave.textContent = '🖼️ 保存卡片海报'; }, 1500);
      }
    };
  }

  // 6. 存储与侧边栏渲染
  function saveAnnotations() {
    try { localStorage.setItem(bookId, JSON.stringify(annotations)); } catch(e){}
  }

  function renderNotesList() {
    if (notesCountBadge) notesCountBadge.textContent = annotations.length;
    if (!notesList) return;
    if (!annotations.length) {
      notesList.innerHTML = '<div class="er-empty-notes">暂无划线与笔记。<br/>划选正文文字即可划线或生成金句卡片。</div>';
      return;
    }
    notesList.innerHTML = annotations.map(item => `
      <div class="er-note-item" data-chap="${item.chapterId}">
        <div class="er-note-quote" style="border-left-color: ${item.color === 'pink' ? '#ec4899' : (item.color === 'emerald' ? '#10b981' : '#f59e0b')}">
          ${item.text}
        </div>
        ${item.comment ? `<div class="er-note-comment">💭 ${item.comment}</div>` : ''}
        <div class="er-note-footer">
          <span>${item.chapterTitle || '正文'} · ${item.time}</span>
          <button type="button" class="er-note-del" data-id="${item.id}">删除</button>
        </div>
      </div>
    `).join('');

    notesList.querySelectorAll('.er-note-item').forEach(el => {
      el.onclick = (e) => {
        if (e.target.classList.contains('er-note-del')) return;
        const chapId = el.getAttribute('data-chap');
        if (chapId && window.navigateToTarget) window.navigateToTarget('#' + chapId);
      };
    });

    notesList.querySelectorAll('.er-note-del').forEach(btn => {
      btn.onclick = (e) => {
        e.stopPropagation();
        const id = btn.getAttribute('data-id');
        annotations = annotations.filter(x => x.id !== id);
        saveAnnotations();
        renderNotesList();
      };
    });
  }

  // 7. 导出 Markdown
  const exportBtn = document.getElementById('er-export-notes-btn');
  if (exportBtn) {
    exportBtn.onclick = () => {
      if (!annotations.length) return alert('当前没有划线笔记可导出');
      const bookName = document.title.split(' - ')[0] || '典籍';
      let md = `# 《${bookName}》读书笔记与高亮摘录\\n\\n`;
      md += `> 导出时间：${new Date().toLocaleString()} · 共 ${annotations.length} 条划线\\n\\n---\\n\\n`;
      annotations.forEach((a, idx) => {
        md += `### ${idx + 1}. [${a.chapterTitle}]\\n\\n`;
        md += `> ${a.text}\\n\\n`;
        if (a.comment) md += `**批注**：${a.comment}\\n\\n`;
        md += `*记录于 ${a.time}*\\n\\n---\\n\\n`;
      });
      navigator.clipboard.writeText(md).then(() => {
        alert('🎉 已将整书 Markdown 格式笔记复制到剪贴板，可直接粘贴入 Obsidian 或文库！');
      }).catch(()=>{});
    };
  }

  const clearBtn = document.getElementById('er-clear-notes-btn');
  if (clearBtn) {
    clearBtn.onclick = () => {
      if (confirm('确定要清空全书的所有划线与批注吗？')) {
        annotations = [];
        saveAnnotations();
        renderNotesList();
      }
    };
  }

  // 8. 侧边栏通用 Tab 切换
  document.querySelectorAll('.er-stab-btn').forEach(btn => {
    btn.onclick = () => {
      const targetPaneId = btn.getAttribute('data-tab');
      document.querySelectorAll('.er-stab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.er-sidebar-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const pane = document.getElementById(targetPaneId);
      if (pane) pane.classList.add('active');
      if (targetPaneId === 'er-pane-notes') renderNotesList();
      if (targetPaneId === 'er-pane-search') {
        const sin = document.getElementById('er-search-input');
        if (sin) setTimeout(() => { sin.focus(); sin.select(); }, 60);
      }
    };
  });

  renderNotesList();
})();
"""
