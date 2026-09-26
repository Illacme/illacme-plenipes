# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EPUB Embedded Reader Client-Side JS Engine
模块职责：纯客户端内存解包与解析引擎，基于本地化 JSZip 与原生 DOMParser 提取目录与章节，彻底摆脱 Python 服务端依赖。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""


def get_epub_client_loader_css() -> str:
    """获取纯客户端加载与拖拽区域的视觉样式"""
    return """
.er-client-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 480px;
  padding: 40px 20px;
  text-align: center;
  color: var(--text-main);
}
.er-loader-spinner {
  font-size: 2.8rem;
  margin-bottom: 16px;
  animation: er-spin 2s linear infinite;
}
@keyframes er-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.er-loader-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 0.05em;
}
.er-loader-desc {
  font-size: 0.88rem;
  color: var(--text-dim);
  max-width: 420px;
  line-height: 1.6;
  margin-bottom: 20px;
}
.er-drop-zone {
  border: 2px dashed var(--border-focus);
  border-radius: 12px;
  padding: 32px 24px;
  background: var(--bg-card);
  cursor: pointer;
  transition: all 0.2s ease;
  max-width: 480px;
  width: 100%;
}
.er-drop-zone:hover, .er-drop-zone.dragover {
  border-color: var(--accent);
  background: rgba(16, 185, 129, 0.08);
}
"""


def get_epub_client_engine_js() -> str:
    """获取纯客户端浏览器端 EPUB 解析驱动脚本"""
    return """(function() {
  'use strict';

  // 纯客户端原生 XML 提取工具
  function parseXML(xmlStr) {
    return new DOMParser().parseFromString(xmlStr, 'application/xml');
  }

  // 路径规范化 (处理相对路径 ../ 与 ./)
  function resolvePath(baseDir, relativePath) {
    if (!relativePath) return '';
    const parts = (baseDir ? baseDir + '/' + relativePath : relativePath).split('/');
    const stack = [];
    for (const p of parts) {
      if (!p || p === '.') continue;
      if (p === '..') {
        if (stack.length > 0) stack.pop();
      } else {
        stack.push(p);
      }
    }
    return stack.join('/');
  }

  // 核心纯前端 EPUB 解析与渲染总控
  window.initClientEpubReader = async function(fileSource) {
    const bookContent = document.getElementById('er-book-content');
    const tocTree = document.getElementById('er-toc-tree');
    const appEl = document.getElementById('er-app');
    const titleEl = document.querySelector('.er-top-title');

    if (!window.JSZip) {
      if (bookContent) bookContent.innerHTML = '<div class="er-client-loader" style="color:#ef4444;">⚠️ 未检测到本地 JSZip 解压驱动，请确保 vendor/jszip.min.js 正常加载。</div>';
      return;
    }

    try {
      let arrayBuffer;
      if (fileSource instanceof ArrayBuffer) {
        arrayBuffer = fileSource;
      } else if (fileSource instanceof Blob) {
        arrayBuffer = await fileSource.arrayBuffer();
      } else if (typeof fileSource === 'string' && fileSource) {
        const res = await fetch(fileSource);
        if (!res.ok) throw new Error('拉取 EPUB 文件失败 (' + res.status + ')');
        arrayBuffer = await res.arrayBuffer();
      } else {
        renderDropZone();
        return;
      }

      // 1. 解压 ZIP 容器
      const zip = await JSZip.loadAsync(arrayBuffer);

      // 2. 解析 META-INF/container.xml 查找 OPF 路径
      const containerFile = zip.file('META-INF/container.xml');
      if (!containerFile) throw new Error('非法的 EPUB: 缺少 META-INF/container.xml');
      const containerXml = await containerFile.async('text');
      const cDoc = parseXML(containerXml);
      const rootfileEl = cDoc.querySelector('rootfile');
      if (!rootfileEl || !rootfileEl.getAttribute('full-path')) throw new Error('未找到 OPF rootfile 指针');

      const opfPath = rootfileEl.getAttribute('full-path');
      const opfDir = opfPath.includes('/') ? opfPath.substring(0, opfPath.lastIndexOf('/')) : '';

      // 3. 解析 content.opf
      const opfFile = zip.file(opfPath);
      if (!opfFile) throw new Error('未找到 OPF 清单文件: ' + opfPath);
      const opfXml = await opfFile.async('text');
      const opfDoc = parseXML(opfXml);

      // 提取书名
      const dcTitle = opfDoc.querySelector('title');
      const bookTitle = (dcTitle && dcTitle.textContent) ? dcTitle.textContent.trim() : '电子典籍';
      if (titleEl) titleEl.textContent = bookTitle;
      document.title = bookTitle + ' - 纯 JS 离线翻阅';

      // 提取 manifest
      const manifest = {};
      opfDoc.querySelectorAll('manifest > item').forEach(el => {
        const id = el.getAttribute('id');
        const href = el.getAttribute('href');
        const mtype = el.getAttribute('media-type') || '';
        if (id && href) {
          manifest[id] = { href: resolvePath(opfDir, href), mediaType: mtype };
        }
      });

      // 4. 将所有图片转为内存 Blob URL
      const blobUrlMap = {};
      for (const id in manifest) {
        const item = manifest[id];
        if (item.mediaType.startsWith('image/')) {
          const zf = zip.file(item.href);
          if (zf) {
            const blob = await zf.async('blob');
            blobUrlMap[item.href] = URL.createObjectURL(blob);
          }
        }
      }

      // 5. 提取 spine 章节顺序
      const spineItems = [];
      opfDoc.querySelectorAll('spine > itemref').forEach(el => {
        const idref = el.getAttribute('idref');
        if (manifest[idref]) spineItems.push(manifest[idref]);
      });

      // 6. 提取与渲染各章节 HTML
      const chapterCards = [];
      const tocItems = [];

      for (let idx = 0; idx < spineItems.length; idx++) {
        const sItem = spineItems[idx];
        const cFile = zip.file(sItem.href);
        if (!cFile) continue;
        const rawHtml = await cFile.async('text');
        const parser = new DOMParser();
        const doc = parser.parseFromString(rawHtml, 'text/html');

        // 提取章节标题
        const hEl = doc.querySelector('h1, h2, h3, title');
        const cTitle = (hEl && hEl.textContent) ? hEl.textContent.trim() : ('第 ' + (idx + 1) + ' 章');
        const chapterId = 'er-doc-ch' + idx;

        // 替换正文中的图片 src 为内存 Blob URL
        const chapDir = sItem.href.includes('/') ? sItem.href.substring(0, sItem.href.lastIndexOf('/')) : '';
        doc.querySelectorAll('img, image').forEach(img => {
          const origSrc = img.getAttribute('src') || img.getAttribute('xlink:href');
          if (origSrc) {
            const absImgPath = resolvePath(chapDir, origSrc);
            if (blobUrlMap[absImgPath]) {
              img.setAttribute('src', blobUrlMap[absImgPath]);
              img.removeAttribute('xlink:href');
            }
          }
        });

        const bodyContent = doc.body ? doc.body.innerHTML : rawHtml;
        chapterCards.push(
          '<article class="er-chapter-card" id="' + chapterId + '" data-chapter-index="' + idx + '" data-chapter-title="' + cTitle.replace(/"/g, '&quot;') + '">' +
          '<div class="er-chapter-inner">' + bodyContent + '</div>' +
          '</article>'
        );
        tocItems.push({ id: chapterId, title: cTitle, index: idx });
      }

      // 7. 注入章节内容与目录树
      if (bookContent) bookContent.innerHTML = chapterCards.join('\\n');

      if (tocTree) {
        tocTree.innerHTML = tocItems.map(item =>
          '<div class="er-toc-item' + (item.index === 0 ? ' active' : '') + '" data-target="' + item.id + '" title="' + item.title.replace(/"/g, '&quot;') + '">' +
          '<span class="er-toc-icon">📄</span><span class="er-toc-label">' + item.title + '</span>' +
          '</div>'
        ).join('');
      }

      // 8. 触发周边生态初始化 (排版、分页、标注、检索)
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

    const dz = document.getElementById('er-drop-zone');
    const fi = document.getElementById('er-file-input');
    if (dz && fi) {
      dz.onclick = () => fi.click();
      fi.onchange = (e) => {
        if (e.target.files && e.target.files[0]) window.initClientEpubReader(e.target.files[0]);
      };
      dz.ondragover = (e) => { e.preventDefault(); dz.classList.add('dragover'); };
      dz.ondragleave = () => { dz.classList.remove('dragover'); };
      dz.ondrop = (e) => {
        e.preventDefault();
        dz.classList.remove('dragover');
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
          window.initClientEpubReader(e.dataTransfer.files[0]);
        }
      };
    }
  }

  // 页面加载完成后自动探测数据源
  document.addEventListener('DOMContentLoaded', () => {
    const appEl = document.getElementById('er-app');
    const sourceUrl = appEl ? appEl.getAttribute('data-source-url') : '';
    if (sourceUrl) {
      window.initClientEpubReader(sourceUrl);
    } else {
      renderDropZone();
    }
  });
})();
"""
