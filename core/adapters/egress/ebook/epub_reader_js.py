# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Runtime JavaScript
模块职责：提供 EPUB 浏览器流式阅读器的全局相对链接拦截、平滑定位、目录联动与主题字号控制。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_reader_js() -> str:
    """获取整卷 EPUB 阅读器客户端交互 JavaScript 脚本"""
    return """(function() {
  'use strict';
  const sb = document.getElementById('er-sidebar'), btn = document.getElementById('er-toggle-sidebar'), bDrop = document.getElementById('er-backdrop');
  function closeSidebar() {
    if (sb) { sb.classList.remove('open'); sb.classList.add('collapsed'); }
    if (bDrop) bDrop.style.display = 'none';
  }
  function openSidebar() {
    if (sb) { sb.classList.add('open'); sb.classList.remove('collapsed'); }
    if (bDrop) bDrop.style.display = 'block';
  }
  function toggleSidebar() {
    const isMob = window.innerWidth <= 900;
    if (isMob) { if (sb && sb.classList.contains('open')) closeSidebar(); else openSidebar(); }
    else if (sb) { sb.classList.toggle('collapsed'); try { localStorage.setItem('er_sb_collapsed', sb.classList.contains('collapsed') ? '1' : '0'); } catch(e){} }
  }
  if (btn) btn.onclick = toggleSidebar;
  if (bDrop) bDrop.onclick = closeSidebar;
  try { if (localStorage.getItem('er_sb_collapsed') === '1' && window.innerWidth > 900 && sb) sb.classList.add('collapsed'); } catch(e){}

  // 1. 全局内部链接无缝拦截器 (彻底拦截 404 Not Found)
  function navigateToTarget(rawTarget) {
    if (!rawTarget) return;
    let targetEl = null;
    let anchor = rawTarget;
    if (anchor.includes('#')) {
      const parts = anchor.split('#');
      const hashId = parts[1];
      targetEl = document.getElementById(hashId) || document.querySelector(`[id="${CSS.escape(hashId)}"]`);
      if (!targetEl && parts[0]) {
        const base = parts[0].split('/').pop().replace(/[^a-zA-Z0-9_-]/g, '_');
        targetEl = document.getElementById('er-doc-' + base);
      }
    } else {
      const base = anchor.split('/').pop().replace(/[^a-zA-Z0-9_-]/g, '_');
      targetEl = document.getElementById('er-doc-' + base);
    }

    if (targetEl) {
      const topOffset = targetEl.getBoundingClientRect().top + window.scrollY - 65;
      window.scrollTo({ top: Math.max(0, topOffset), behavior: 'smooth' });
      if (window.innerWidth <= 900) closeSidebar();
    }
  }

  document.addEventListener('click', function(e) {
    const a = e.target.closest('a');
    if (!a) return;
    const href = a.getAttribute('href');
    if (!href) return;
    if (href.startsWith('http://') || href.startsWith('https://') || href.startsWith('mailto:') || href.startsWith('data:')) {
      a.setAttribute('target', '_blank');
      a.setAttribute('rel', 'noopener noreferrer');
      return;
    }
    
    // 拦截所有内部相对链接或锚点
    e.preventDefault();
    navigateToTarget(href);
  });

  // 2. 三模主题切换
  const themeBtns = document.querySelectorAll('.er-theme-btn');
  const applyTheme = (th) => {
    document.documentElement.setAttribute('data-theme', th);
    themeBtns.forEach(x => x.classList.toggle('active', x.getAttribute('data-theme') === th));
    try { localStorage.setItem('er_theme', th); } catch(e){}
  };
  themeBtns.forEach(b => { b.onclick = () => applyTheme(b.getAttribute('data-theme')); });
  try { const savedTh = localStorage.getItem('er_theme'); if (savedTh) applyTheme(savedTh); } catch(e){}

  // 3. 字号缩放
  let fs = 16;
  const inc = document.getElementById('er-font-inc'), dec = document.getElementById('er-font-dec');
  const setFs = (val) => { fs = val; document.documentElement.style.setProperty('--font-size', fs + 'px'); try { localStorage.setItem('er_fs', fs); } catch(e){} };
  try { const sfs = parseInt(localStorage.getItem('er_fs'), 10); if (sfs >= 13 && sfs <= 24) setFs(sfs); } catch(e){}
  if (inc) inc.onclick = () => setFs(Math.min(24, fs + 1));
  if (dec) dec.onclick = () => setFs(Math.max(13, fs - 1));

  // 4. 阅读进度条与目录高亮联动
  const pBar = document.getElementById('er-progress-bar');
  const chapters = document.querySelectorAll('.er-chapter-card');
  const tocLinks = document.querySelectorAll('.er-sidebar a');
  
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        const h = document.documentElement.scrollHeight - window.innerHeight;
        if (pBar && h > 0) pBar.style.width = Math.min(100, Math.max(0, (window.scrollY / h) * 100)) + '%';
        let currentCardId = '';
        chapters.forEach(c => {
          const rect = c.getBoundingClientRect();
          if (rect.top <= 140 && rect.bottom >= 140) currentCardId = c.id;
        });
        if (currentCardId) {
          tocLinks.forEach(link => {
            const h = link.getAttribute('href') || '';
            const isActive = h === '#' + currentCardId || h.endsWith(currentCardId);
            link.classList.toggle('active', isActive);
          });
        }
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  // 5. 键盘快捷翻页
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'ArrowRight' || e.key === 'PageDown') {
      window.scrollBy({ top: window.innerHeight * 0.85, behavior: 'smooth' });
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      window.scrollBy({ top: -window.innerHeight * 0.85, behavior: 'smooth' });
    }
  });
})();
"""
