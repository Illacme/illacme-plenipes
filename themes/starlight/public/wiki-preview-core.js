/**
 * wiki-preview-core.js — 纯原生零依赖通用悬浮预览卡片引擎
 * 跨 Nextra / Docusaurus / Starlight 主题共享
 */

let overlayEl = null;
let graphDataCache = null;
let excerptFetchCache = {};
let hoverTimer = null;
let hideTimer = null;
let currentAnchor = null;
let isInitialized = false;

// 1. 样式注入
function injectStyles() {
  if (document.getElementById('wiki-preview-styles')) return;
  const style = document.createElement('style');
  style.id = 'wiki-preview-styles';
  style.textContent = `
    .wiki-hover-card {
      position: fixed;
      z-index: 99999;
      width: 320px;
      max-width: calc(100vw - 32px);
      padding: 14px 16px;
      border-radius: 12px;
      pointer-events: auto;
      opacity: 0;
      transform: translateY(6px) scale(0.98);
      transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1), transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      box-sizing: border-box;
      font-family: inherit;
      line-height: 1.5;
      display: none;
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
    }
    .wiki-hover-card.wiki-visible {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    .wiki-hover-card.dark, :root[data-theme="dark"] .wiki-hover-card, html.dark .wiki-hover-card {
      background: rgba(15, 23, 42, 0.88);
      border: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45), 0 2px 6px rgba(0, 0, 0, 0.3);
      color: #f1f5f9;
    }
    .wiki-hover-card.light, :root[data-theme="light"] .wiki-hover-card, html:not(.dark) .wiki-hover-card {
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid rgba(226, 232, 240, 0.95);
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12), 0 2px 8px rgba(15, 23, 42, 0.04);
      color: #1e293b;
    }
    .wiki-card-header {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 6px;
    }
    .wiki-card-title {
      font-size: 0.92rem;
      font-weight: 700;
      margin: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
      color: inherit;
    }
    .wiki-card-excerpt {
      font-size: 0.8rem;
      margin: 0 0 10px 0;
      opacity: 0.85;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
      line-height: 1.45;
    }
    .wiki-card-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.72rem;
      opacity: 0.65;
      border-top: 1px dashed rgba(148, 163, 184, 0.3);
      padding-top: 6px;
    }
    .wiki-card-hint {
      display: inline-flex;
      align-items: center;
      gap: 3px;
    }
  `;
  document.head.appendChild(style);
}

// 2. 路由路径归一化（复用成熟的跨引擎映射）
function normalizeUrl(raw) {
  if (!raw) return '/';
  let u = String(raw).trim().split('?')[0].split('#')[0];
  u = u.replace(/\/engineering\/engineering\//g, '/engineering/');
  return u.replace(/\/$/, '') || '/';
}

// 3. 异步获取 graph.json
async function loadGraphData() {
  if (graphDataCache) return graphDataCache;
  try {
    const res = await fetch('/graph.json');
    if (!res.ok) return null;
    graphDataCache = await res.json();
    return graphDataCache;
  } catch {
    return null;
  }
}

// 4. 创建或获取浮层 DOM
function getOverlay() {
  if (overlayEl) return overlayEl;
  injectStyles();
  overlayEl = document.createElement('div');
  overlayEl.id = 'wiki-hover-card';
  overlayEl.className = 'wiki-hover-card';
  overlayEl.innerHTML = `
    <div class="wiki-card-header">
      <span>📄</span>
      <h4 class="wiki-card-title"></h4>
    </div>
    <p class="wiki-card-excerpt"></p>
    <div class="wiki-card-footer">
      <span class="wiki-card-badge">手稿预览</span>
      <span class="wiki-card-hint">点击直达 ↗</span>
    </div>
  `;
  // 鼠标移入浮层自身时不关闭
  overlayEl.addEventListener('mouseenter', () => clearTimeout(hideTimer));
  overlayEl.addEventListener('mouseleave', () => scheduleHide());
  document.body.appendChild(overlayEl);
  return overlayEl;
}

// 5. 显示浮层并计算防碰撞坐标
function showOverlay(targetA, title, excerpt) {
  const overlay = getOverlay();
  const titleEl = overlay.querySelector('.wiki-card-title');
  const excerptEl = overlay.querySelector('.wiki-card-excerpt');
  if (titleEl) titleEl.textContent = title;
  if (excerptEl) excerptEl.textContent = excerpt || '点击可深入阅读该手稿的完整图文内容与知识脉络。';

  overlay.style.display = 'block';

  // 坐标计算与视口防碰撞
  const rect = targetA.getBoundingClientRect();
  const cardW = 320;
  const cardH = overlay.offsetHeight || 130;
  const pad = 12;

  let left = rect.left + rect.width / 2 - cardW / 2;
  left = Math.max(pad, Math.min(left, window.innerWidth - cardW - pad));

  // 默认显示在下方；若下方空间不足则翻转到上方
  let top = rect.bottom + 8;
  if (top + cardH > window.innerHeight - pad && rect.top - cardH - 8 > pad) {
    top = rect.top - cardH - 8;
  }

  overlay.style.left = `${left}px`;
  overlay.style.top = `${top}px`;

  requestAnimationFrame(() => {
    overlay.classList.add('wiki-visible');
  });
}

function scheduleHide() {
  clearTimeout(hoverTimer);
  clearTimeout(hideTimer);
  hideTimer = setTimeout(() => {
    if (overlayEl) {
      overlayEl.classList.remove('wiki-visible');
      setTimeout(() => {
        if (!overlayEl.classList.contains('wiki-visible')) overlayEl.style.display = 'none';
      }, 200);
    }
    currentAnchor = null;
  }, 200);
}

// 6. 查找目标链接对应的信息
async function resolveLinkData(href) {
  const norm = normalizeUrl(href);
  const data = await loadGraphData();
  let title = '';
  let excerpt = '';

  if (data) {
    const titles = data.node_titles || data.all_nodes || {};
    const excerpts = data.node_excerpts || {};
    const allKeys = Object.keys(titles);

    let matchedKey = allKeys.find(k => normalizeUrl(k) === norm);
    if (!matchedKey && norm !== '/') {
      matchedKey = allKeys.find(k => {
        const c = normalizeUrl(k);
        return c !== '/' && (c.endsWith(norm) || norm.endsWith(c));
      });
    }

    if (matchedKey) {
      title = titles[matchedKey] || '';
      excerpt = excerpts[matchedKey] || '';
    }
  }

  // 若无 excerpt，尝试通过缓存或 fetch meta description 兜底
  if (!excerpt && norm && norm !== '/') {
    if (excerptFetchCache[norm]) {
      excerpt = excerptFetchCache[norm];
    } else {
      try {
        const res = await fetch(href);
        if (res.ok) {
          const html = await res.text();
          const match = html.match(/<meta\s+name=["']description["']\s+content=["'](.*?)["']/i);
          if (match && match[1]) {
            excerpt = match[1].trim();
            excerptFetchCache[norm] = excerpt;
          }
        }
      } catch {}
    }
  }

  if (!title) {
    const segs = norm.split('/').filter(Boolean);
    title = segs.length > 0 ? segs[segs.length - 1].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : '手稿引言';
  }

  return { title, excerpt };
}

// 7. 全局事件代理初始化
export function initWikiPreview(rootSelector = 'main, article, .nextra-content, .theme-doc-markdown, .sl-markdown-content') {
  if (typeof window === 'undefined' || typeof document === 'undefined') return;
  if (isInitialized) return;
  isInitialized = true;

  // 预热拉取 graph.json
  loadGraphData();

  document.addEventListener('mouseover', (e) => {
    const a = e.target.closest('a');
    if (!a) return;

    // 仅针对正文容器内的站内链接
    const container = a.closest(rootSelector);
    if (!container) return;

    const href = a.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:')) return;
    if (href.startsWith('http://') || href.startsWith('https://') || href.startsWith('//')) {
      // 若是外部链接，忽略
      try {
        const u = new URL(href, window.location.origin);
        if (u.origin !== window.location.origin) return;
      } catch { return; }
    }

    currentAnchor = a;
    clearTimeout(hideTimer);
    clearTimeout(hoverTimer);

    hoverTimer = setTimeout(async () => {
      if (currentAnchor !== a) return;
      const { title, excerpt } = await resolveLinkData(href);
      if (currentAnchor === a) {
        showOverlay(a, title, excerpt);
      }
    }, 220);
  });

  document.addEventListener('mouseout', (e) => {
    const a = e.target.closest('a');
    if (a && a === currentAnchor) {
      scheduleHide();
    }
  });

  // 滚动或按 ESC 时自动隐去
  window.addEventListener('scroll', () => scheduleHide(), { passive: true });
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') scheduleHide(); });
}
