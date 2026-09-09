/**
 * article-telemetry-core.js — 文章正文顶部「出版级全息装帧元数据栏」通用引擎
 * 跨 Nextra / Docusaurus / Starlight / Sovereign 等主题共享
 */

const LANG_LABELS = {
  zh: '中文', 'zh-Hans': '中文', 'zh-Hant': '繁体',
  en: 'English', ja: '日本語', ko: '한국어',
  fr: 'Français', de: 'Deutsch', es: 'Español'
};

let graphCache = null;

function injectTelemetryStyles() {
  if (document.getElementById('article-telemetry-styles')) return;
  const style = document.createElement('style');
  style.id = 'article-telemetry-styles';
  style.textContent = `
    .nextra-breadcrumb {
      display: none !important;
    }
    .article-telemetry-bar {
      display: inline-flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px 14px;
      margin: 14px 0 24px 0;
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 0.78rem;
      line-height: 1.4;
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      box-sizing: border-box;
      transition: all 0.2s ease;
    }
    :root[data-theme="dark"] .article-telemetry-bar, html.dark .article-telemetry-bar {
      background: rgba(30, 41, 59, 0.45);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: #94a3b8;
    }
    :root[data-theme="light"] .article-telemetry-bar, html:not(.dark) .article-telemetry-bar {
      background: rgba(248, 250, 252, 0.85);
      border: 1px solid rgba(226, 232, 240, 0.9);
      color: #475569;
    }
    .telemetry-item {
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .telemetry-icon {
      font-size: 0.85em;
      opacity: 0.85;
    }
    .telemetry-divider {
      width: 1px;
      height: 12px;
      background: rgba(148, 163, 184, 0.3);
    }
    .telemetry-i18n-group {
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .telemetry-i18n-pill {
      display: inline-flex;
      align-items: center;
      padding: 1px 7px;
      border-radius: 9999px;
      font-size: 0.72rem;
      font-weight: 600;
      text-decoration: none !important;
      transition: all 0.2s ease;
    }
    .telemetry-i18n-pill.active {
      background: rgba(56, 189, 248, 0.15);
      color: #0284c7;
      border: 1px solid rgba(2, 132, 199, 0.3);
    }
    :root[data-theme="dark"] .telemetry-i18n-pill.active, html.dark .telemetry-i18n-pill.active {
      background: rgba(56, 189, 248, 0.2);
      color: #38bdf8;
      border-color: rgba(56, 189, 248, 0.35);
    }
    .telemetry-i18n-pill.link {
      background: rgba(148, 163, 184, 0.1);
      color: inherit;
      border: 1px solid transparent;
    }
    .telemetry-i18n-pill.link:hover {
      background: rgba(56, 189, 248, 0.15);
      color: #0284c7;
      border-color: rgba(2, 132, 199, 0.25);
    }
  `;
  document.head.appendChild(style);
}

function calculateReadingStats(text) {
  if (!text) return { minutes: 1, words: 0 };
  const cjk = (text.match(/[\u4e00-\u9fa5\u3040-\u30ff]/g) || []).length;
  const words = (text.replace(/[\u4e00-\u9fa5\u3040-\u30ff]/g, ' ').match(/[a-zA-Z0-9_-]+/g) || []).length;
  const total = cjk + words;
  const minutes = Math.max(1, Math.ceil(cjk / 350 + words / 200));
  return { minutes, words: total };
}

async function getGraph() {
  if (graphCache) return graphCache;
  try {
    const res = await fetch('/graph.json');
    if (!res.ok) return null;
    graphCache = await res.json();
    return graphCache;
  } catch {
    return null;
  }
}

function detectCurrentLang(path) {
  if (path.startsWith('/en/') || path === '/en') return 'en';
  if (path.startsWith('/ja/') || path === '/ja') return 'ja';
  if (path.startsWith('/ko/') || path === '/ko') return 'ko';
  return 'zh';
}

function resolveCleanRoute(rawUrl) {
  if (!rawUrl) return '/';
  let u = String(rawUrl).trim().split('?')[0].split('#')[0];
  u = u.replace(/\/engineering\/engineering\//g, '/engineering/');
  u = u.replace(/^(\/(?:[a-zA-Z]{2,3}(?:-[A-Za-z0-9]+)?\/)?)docs\//, '$1');
  return u || '/';
}

function findI18nVariants(pathname, allNodes) {
  const currentClean = pathname.split('?')[0].split('#')[0].replace(/\/$/, '') || '/';
  const segs = currentClean.split('/').filter(Boolean);
  const currentSlug = segs.length > 0 ? segs[segs.length - 1] : '';
  if (!currentSlug || !allNodes) return [];

  const currentLang = detectCurrentLang(currentClean);
  const variants = [{ lang: currentLang, url: currentClean, active: true }];

  Object.keys(allNodes).forEach((rawUrl) => {
    const cleanUrl = resolveCleanRoute(rawUrl).replace(/\/$/, '') || '/';
    const otherSegs = cleanUrl.split('/').filter(Boolean);
    const otherSlug = otherSegs.length > 0 ? otherSegs[otherSegs.length - 1] : '';
    if (otherSlug === currentSlug) {
      const otherLang = detectCurrentLang(cleanUrl);
      if (!variants.some(v => v.lang === otherLang)) {
        variants.push({ lang: otherLang, url: cleanUrl, active: false });
      }
    }
  });

  return variants;
}

export async function mountArticleTelemetry() {
  if (typeof window === 'undefined' || typeof document === 'undefined') return;

  const h1 = document.querySelector('article h1, main h1, .nextra-content h1, .theme-doc-markdown h1, .sl-markdown-content h1');
  if (!h1) return;

  // 避免在已有元数据栏或正在挂载时重复执行（防止异步竞态）
  if (h1.dataset.telemetryMounted === 'true' || h1.dataset.telemetryMounting === 'true') return;
  h1.dataset.telemetryMounting = 'true';

  const articleContainer = h1.closest('article, main, .nextra-content, .theme-doc-markdown, .sl-markdown-content') || h1.parentElement;
  if (!articleContainer) {
    delete h1.dataset.telemetryMounting;
    return;
  }

  injectTelemetryStyles();

  // 1. 测算字数与预计阅读时间
  const fullText = articleContainer.innerText || '';
  const { minutes, words } = calculateReadingStats(fullText);

  // 2. 尝试提取文章修订日期
  const timeEl = document.querySelector('time, [itemprop="dateModified"], [itemprop="datePublished"], .theme-last-updated');
  let dateText = timeEl ? (timeEl.getAttribute('datetime') || timeEl.textContent || '').trim() : '';
  if (!dateText) {
    const today = new Date();
    dateText = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
  } else {
    const match = dateText.match(/\d{4}[-/.]\d{1,2}[-/.]\d{1,2}/);
    if (match) dateText = match[0].replace(/\./g, '-').replace(/\//g, '-');
  }

  // 3. 构建多语言穿梭胶囊
  const graphData = await getGraph();
  const allNodes = graphData?.all_nodes || {};
  const currentPath = window.location.pathname;
  const variants = findI18nVariants(currentPath, allNodes);

  // 4. 创建 DOM
  const bar = document.createElement('div');
  bar.className = 'article-telemetry-bar';

  let i18nHtml = '';
  if (variants.length > 1) {
    const pills = variants.map(v => {
      const label = LANG_LABELS[v.lang] || v.lang.toUpperCase();
      if (v.active) return `<span class="telemetry-i18n-pill active">${label}</span>`;
      return `<a href="${v.url}" class="telemetry-i18n-pill link" title="切换为 ${label} 版本">${label}</a>`;
    }).join('');
    i18nHtml = `
      <span class="telemetry-divider"></span>
      <div class="telemetry-item telemetry-i18n-group">
        <span class="telemetry-icon">🌐</span>
        ${pills}
      </div>
    `;
  }

  bar.innerHTML = `
    <div class="telemetry-item">
      <span class="telemetry-icon">⏱️</span>
      <span>约 ${minutes} 分钟 (${words.toLocaleString()} 字)</span>
    </div>
    <span class="telemetry-divider"></span>
    <div class="telemetry-item">
      <span class="telemetry-icon">📅</span>
      <span>${dateText}</span>
    </div>
    ${i18nHtml}
  `;

  // 插入前清理旧条目并保证绝对单例
  const oldBars = articleContainer.querySelectorAll('.article-telemetry-bar');
  oldBars.forEach(b => b.remove());

  // 插入到 H1 正下方
  h1.insertAdjacentElement('afterend', bar);
  delete h1.dataset.telemetryMounting;
  h1.dataset.telemetryMounted = 'true';

  // 🛡️ 防 React 水合 / SPA 异步重洗牌二次校准（保证绝对物理锚定于 H1 正下方）
  const ensureBelowH1 = () => {
    const curH1 = document.querySelector('article h1, main h1, .nextra-content h1, .theme-doc-markdown h1, .sl-markdown-content h1');
    if (curH1 && bar && bar.isConnected && bar.previousElementSibling !== curH1) {
      curH1.insertAdjacentElement('afterend', bar);
    }
  };
  setTimeout(ensureBelowH1, 60);
  setTimeout(ensureBelowH1, 250);
}
