# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Client-Side JS Engine
模块职责：纯客户端内存解包与解析引擎，基于本地化 JSZip 与原生 DOMParser 提取目录与章节，彻底摆脱 Python 服务端依赖。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_client_loader_css() -> str:
    """获取纯客户端加载与拖拽区域的视觉样式"""
    return """
.er-client-loader { display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:480px; padding:40px 20px; text-align:center; color:var(--text-main); }
.er-loader-spinner { font-size:2.8rem; margin-bottom:16px; animation:er-spin 2s linear infinite; }
@keyframes er-spin { 0% { transform:rotate(0deg); } 100% { transform:rotate(360deg); } }
.er-loader-title { font-size:1.25rem; font-weight:700; margin-bottom:8px; letter-spacing:0.05em; }
.er-loader-desc { font-size:0.88rem; color:var(--text-dim); max-width:420px; line-height:1.6; margin-bottom:20px; }
.er-drop-zone { border:2px dashed var(--border-focus); border-radius:12px; padding:32px 24px; background:var(--bg-card); cursor:pointer; transition:all 0.2s ease; max-width:480px; width:100%; }
.er-drop-zone:hover, .er-drop-zone.dragover { border-color:var(--accent); background:rgba(16, 185, 129, 0.08); }
"""


def get_epub_client_engine_js() -> str:
    """获取纯客户端浏览器端 EPUB 解析驱动脚本"""
    return """(function() {
  'use strict';

  function parseXML(xmlStr) { return new DOMParser().parseFromString(xmlStr, 'application/xml'); }

  function resolvePath(baseDir, relativePath) {
    if (!relativePath) return '';
    const parts = (baseDir ? baseDir + '/' + relativePath : relativePath).split('/');
    const stack = [];
    for (const p of parts) {
      if (!p || p === '.') continue;
      if (p === '..') { if (stack.length > 0) stack.pop(); } else stack.push(p);
    }
    return stack.join('/');
  }

  const toCardId = (href) => 'er-doc-' + (href.split('#')[0].split('/').pop() || '').replace(/[^a-zA-Z0-9_-]/g, '_');
  const toTarget = (href) => {
    if (!href) return '#';
    const parts = href.split('#'), baseId = toCardId(parts[0]);
    return (parts.length > 1 && parts[1]) ? `#${baseId}#${parts[1]}` : ('#' + baseId);
  };

  async function parseClientToc(zip, manifest, spineItems) {
    const navItem = Object.values(manifest).find(v => (v.properties || '').includes('nav') || v.href.endsWith('nav.xhtml') || v.href.endsWith('nav.html'));
    if (navItem && zip.file(navItem.href)) {
      try {
        const xml = await zip.file(navItem.href).async('text');
        const doc = parseXML(xml);
        const navEl = doc.querySelector('nav[*|type="toc"], nav#toc, nav');
        if (navEl) {
          navEl.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => h.remove());
          navEl.querySelectorAll('a').forEach(a => {
            const raw = a.getAttribute('href') || '';
            a.setAttribute('href', toTarget(raw));
            a.setAttribute('data-epub-href', raw);
            a.className = 'er-toc-link';
          });
          const list = navEl.querySelector('ol, ul');
          if (list) { list.className = 'er-toc-tree'; return list.outerHTML; }
        }
      } catch (e) { console.warn('nav.xhtml parse error:', e); }
    }
    const ncxItem = Object.values(manifest).find(v => (v.mediaType || '').includes('dtbncx') || v.href.endsWith('.ncx'));
    if (ncxItem && zip.file(ncxItem.href)) {
      try {
        const xml = await zip.file(ncxItem.href).async('text');
        const doc = parseXML(xml);
        const navMap = doc.querySelector('navMap');
        if (navMap) {
          const walkPoints = (parent) => {
            const pts = Array.from(parent.children).filter(el => (el.localName || el.tagName || '').toLowerCase().endsWith('navpoint'));
            if (!pts.length) return '';
            return '<ol>' + pts.map(pt => {
              const lblEl = pt.querySelector(':scope > navLabel > text, navLabel text');
              const lbl = (lblEl && lblEl.textContent) ? lblEl.textContent.trim() : '章节';
              const srcEl = pt.querySelector(':scope > content, content');
              const src = srcEl ? (srcEl.getAttribute('src') || '') : '';
              return `<li><a href="${toTarget(src)}" class="er-toc-link" data-epub-href="${src}">${lbl}</a>${walkPoints(pt)}</li>`;
            }).join('') + '</ol>';
          };
          const tree = walkPoints(navMap);
          if (tree) return tree.replace('<ol>', '<ol class="er-toc-tree">');
        }
      } catch (e) { console.warn('toc.ncx parse error:', e); }
    }
    let chCount = 0;
    return '<ol class="er-toc-tree">' + spineItems.map((item, idx) => {
      const cid = toCardId(item.href), href = (item.href || '').toLowerCase();
      if (href.includes('cover')) return `<li><a href="#${cid}" class="er-toc-link">📕 典籍封面与扉页</a></li>`;
      if (href.includes('nav')) return `<li><a href="#${cid}" class="er-toc-link">📑 全书目录索引</a></li>`;
      if (href.includes('colophon')) return `<li><a href="#${cid}" class="er-toc-link">📜 出版版权与版记</a></li>`;
      chCount++;
      return `<li><a href="#${cid}" class="er-toc-link">📖 第 ${chCount} 卷</a></li>`;
    }).join('') + '</ol>';
  }

  window.initClientEpubReader = async function(fileSource) {
    const bookContent = document.getElementById('er-book-content');
    const tocTree = document.getElementById('er-toc-tree');
    const titleEl = document.querySelector('.er-top-title');

    if (!window.JSZip) {
      if (bookContent) bookContent.innerHTML = '<div class="er-client-loader" style="color:#ef4444;">⚠️ 未检测到本地 JSZip 解压驱动。</div>';
      return;
    }

    try {
      let arrayBuffer;
      if (fileSource instanceof ArrayBuffer) arrayBuffer = fileSource;
      else if (fileSource instanceof Blob) arrayBuffer = await fileSource.arrayBuffer();
      else if (typeof fileSource === 'string' && fileSource) {
        const res = await fetch(fileSource);
        if (!res.ok) throw new Error('拉取 EPUB 文件失败 (' + res.status + ')');
        arrayBuffer = await res.arrayBuffer();
      } else { renderDropZone(); return; }

      const zip = await JSZip.loadAsync(arrayBuffer);
      const containerFile = zip.file('META-INF/container.xml');
      if (!containerFile) throw new Error('非法的 EPUB: 缺少 META-INF/container.xml');
      const containerXml = await containerFile.async('text');
      const rootfileEl = parseXML(containerXml).querySelector('rootfile');
      if (!rootfileEl || !rootfileEl.getAttribute('full-path')) throw new Error('未找到 OPF rootfile 指针');

      const opfPath = rootfileEl.getAttribute('full-path');
      const opfDir = opfPath.includes('/') ? opfPath.substring(0, opfPath.lastIndexOf('/')) : '';
      const opfFile = zip.file(opfPath);
      if (!opfFile) throw new Error('未找到 OPF 清单文件: ' + opfPath);
      const opfDoc = parseXML(await opfFile.async('text'));

      const dcTitle = opfDoc.querySelector('title');
      const bookTitle = (dcTitle && dcTitle.textContent) ? dcTitle.textContent.trim() : '电子典籍';
      if (titleEl) titleEl.textContent = bookTitle;
      document.title = bookTitle + ' - 纯 JS 离线翻阅';

      const manifest = {};
      opfDoc.querySelectorAll('manifest > item').forEach(el => {
        const id = el.getAttribute('id'), href = el.getAttribute('href'), mtype = el.getAttribute('media-type') || '', props = el.getAttribute('properties') || '';
        if (id && href) manifest[id] = { href: resolvePath(opfDir, href), mediaType: mtype, properties: props };
      });

      const blobUrlMap = {};
      for (const id in manifest) {
        const item = manifest[id];
        if (item.mediaType.startsWith('image/')) {
          const zf = zip.file(item.href);
          if (zf) {
            const ab = await zf.async('arraybuffer');
            const b = new Blob([ab], { type: item.mediaType || 'image/png' });
            blobUrlMap[item.href] = URL.createObjectURL(b);
          }
        }
      }

      const spineItems = [];
      opfDoc.querySelectorAll('spine > itemref').forEach(el => {
        const idref = el.getAttribute('idref');
        if (manifest[idref]) spineItems.push(manifest[idref]);
      });

      const chapterCards = [];
      for (let idx = 0; idx < spineItems.length; idx++) {
        const sItem = spineItems[idx];
        const cFile = zip.file(sItem.href);
        if (!cFile) continue;
        const rawHtml = await cFile.async('text');
        const doc = new DOMParser().parseFromString(rawHtml, 'text/html');
        const hEl = doc.querySelector('h1, h2, h3, title');
        const sHref = (sItem.href || '').toLowerCase();
        const isCover = sHref.includes('cover') || (sItem.properties || '').includes('cover');
        const isNav = sHref.includes('nav');
        const isColophon = sHref.includes('colophon') || sHref.includes('copyright');
        const fallbackTitle = isCover ? '典籍封面与扉页' : (isNav ? '全书目录索引' : (isColophon ? '出版版权与版记' : ('第 ' + (idx + 1) + ' 章')));
        const cTitle = (hEl && hEl.textContent) ? hEl.textContent.trim() : fallbackTitle;
        const chapterId = toCardId(sItem.href);
        const chapDir = sItem.href.includes('/') ? sItem.href.substring(0, sItem.href.lastIndexOf('/')) : '';

        doc.querySelectorAll('img, image').forEach(img => {
          const origSrc = img.getAttribute('src') || img.getAttribute('xlink:href');
          if (origSrc) {
            const absImgPath = resolvePath(chapDir, origSrc);
            if (blobUrlMap[absImgPath]) { img.setAttribute('src', blobUrlMap[absImgPath]); img.removeAttribute('xlink:href'); }
          }
        });

        const cardClass = isCover ? 'er-chapter-card er-cover-card' : (isNav ? 'er-chapter-card er-nav-card' : (isColophon ? 'er-chapter-card er-colophon-card' : 'er-chapter-card'));
        const bodyContent = doc.body ? doc.body.innerHTML : rawHtml;
        chapterCards.push(
          '<article class="' + cardClass + '" id="' + chapterId + '" data-chapter-index="' + idx + '" data-chapter-title="' + cTitle.replace(/"/g, '&quot;') + '">' +
          '<div class="er-chapter-inner">' + bodyContent + '</div>' +
          '</article>'
        );
      }

      if (bookContent) bookContent.innerHTML = chapterCards.join('\\n');

      let tocHtml = await parseClientToc(zip, manifest, spineItems);
      const coverItem = spineItems.find(s => s.href.toLowerCase().includes('cover'));
      if (coverItem && !tocHtml.includes(toCardId(coverItem.href))) {
        const coverNav = '<li><a href="#' + toCardId(coverItem.href) + '" class="er-toc-link">📕 典籍封面与扉页</a></li>';
        tocHtml = tocHtml.replace('<ol class="er-toc-tree">', '<ol class="er-toc-tree">' + coverNav);
      }
      if (tocTree) tocTree.innerHTML = tocHtml;

      // 触发周边生态初始化
      if (typeof window.initPolyglotBar === 'function') window.initPolyglotBar();
      if (typeof window.updatePagination === 'function') window.updatePagination();
      if (typeof window.initPagination === 'function') window.initPagination();
      if (typeof window.rebuildSearchIndex === 'function') window.rebuildSearchIndex();
      if (typeof window.refreshAnnotationHighlights === 'function') window.refreshAnnotationHighlights();

    } catch (err) {
      console.error('Client EPUB Parse Error:', err);
      if (bookContent) {
        bookContent.innerHTML = '<div class="er-client-loader" style="color:#ef4444;">' +
          '<div style="font-size:2rem; margin-bottom:12px;">⚠️</div>' +
          '<div class="er-loader-title">客户端解析失败</div>' +
          '<div class="er-loader-desc">' + String(err.message || err) + '</div>' +
          '</div>';
      }
    }
  };

  function renderDropZone() {
    const bookContent = document.getElementById('er-book-content');
    if (!bookContent) return;
    bookContent.innerHTML = '<div class="er-client-loader">' +
      '<div class="er-loader-spinner">📖</div>' +
      '<div class="er-loader-title">纯 JS 离线典籍翻阅</div>' +
      '<div class="er-loader-desc">当前运行在 100% 纯前端模式下。请拖拽任意 .epub 电子书至下方，或由页面自动拉取。</div>' +
      '<div class="er-drop-zone" id="er-drop-zone">' +
      '<div style="font-size:1.8rem; margin-bottom:8px;">📂</div>' +
      '<div style="font-weight:600;">点击选择或拖放本地 EPUB 文件</div>' +
      '<div style="font-size:0.75rem; color:var(--text-dim); margin-top:4px;">零服务器开销 · 纯前端内存极速解析</div>' +
      '<input type="file" id="er-file-input" accept=".epub" style="display:none;" />' +
      '</div>' +
      '</div>';

    const dz = document.getElementById('er-drop-zone'), fi = document.getElementById('er-file-input');
    if (dz && fi) {
      dz.onclick = () => fi.click();
      fi.onchange = (e) => { if (e.target.files && e.target.files[0]) window.initClientEpubReader(e.target.files[0]); };
      dz.ondragover = (e) => { e.preventDefault(); dz.classList.add('dragover'); };
      dz.ondragleave = () => { dz.classList.remove('dragover'); };
      dz.ondrop = (e) => {
        e.preventDefault(); dz.classList.remove('dragover');
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) window.initClientEpubReader(e.dataTransfer.files[0]);
      };
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const appEl = document.getElementById('er-app');
    const sourceUrl = appEl ? appEl.getAttribute('data-source-url') : '';
    if (sourceUrl) window.initClientEpubReader(sourceUrl);
    else renderDropZone();
  });
})();
"""
