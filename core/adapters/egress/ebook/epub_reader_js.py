# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Runtime JavaScript
模块职责：提供 EPUB 浏览器流式阅读器的目录折叠、进度监听、主题切换与触控交互。
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

  // 1. 三模主题切换
  const themeBtns = document.querySelectorAll('.er-theme-btn');
  const applyTheme = (th) => {
    document.documentElement.setAttribute('data-theme', th);
    themeBtns.forEach(x => x.classList.toggle('active', x.getAttribute('data-theme') === th));
    try { localStorage.setItem('er_theme', th); } catch(e){}
  };
  themeBtns.forEach(b => { b.onclick = () => applyTheme(b.getAttribute('data-theme')); });
  try { const savedTh = localStorage.getItem('er_theme'); if (savedTh) applyTheme(savedTh); } catch(e){}

  // 2. 字号缩放
  let fs = 16;
  const inc = document.getElementById('er-font-inc'), dec = document.getElementById('er-font-dec');
  const setFs = (val) => { fs = val; document.documentElement.style.setProperty('--font-size', fs + 'px'); try { localStorage.setItem('er_fs', fs); } catch(e){} };
  try { const sfs = parseInt(localStorage.getItem('er_fs'), 10); if (sfs >= 13 && sfs <= 24) setFs(sfs); } catch(e){}
  if (inc) inc.onclick = () => setFs(Math.min(24, fs + 1));
  if (dec) dec.onclick = () => setFs(Math.max(13, fs - 1));

  // 3. 阅读进度条与当前章节目录高亮
  const pBar = document.getElementById('er-progress-bar');
  const chapters = document.querySelectorAll('.er-chapter-card');
  const tocItems = document.querySelectorAll('.er-toc-item');
  
  window.addEventListener('scroll', () => {
    const h = document.documentElement.scrollHeight - window.innerHeight;
    if (pBar && h > 0) pBar.style.width = Math.min(100, Math.max(0, (window.scrollY / h) * 100)) + '%';
    let currentId = '';
    chapters.forEach(c => {
      const rect = c.getBoundingClientRect();
      if (rect.top <= 120 && rect.bottom >= 120) currentId = c.id;
    });
    if (currentId) {
      tocItems.forEach(item => {
        const a = item.querySelector('a');
        if (a && a.getAttribute('href') === '#' + currentId) item.classList.add('active');
        else item.classList.remove('active');
      });
    }
  }, { passive: true });

  // 4. 目录项平滑滚动与手机侧栏自动收拢
  tocItems.forEach(item => {
    const a = item.querySelector('a');
    if (a) {
      a.onclick = (e) => {
        const href = a.getAttribute('href');
        if (href && href.startsWith('#')) {
          e.preventDefault();
          const target = document.querySelector(href);
          if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            if (window.innerWidth <= 900) closeSidebar();
          }
        }
      };
    }
  });

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
