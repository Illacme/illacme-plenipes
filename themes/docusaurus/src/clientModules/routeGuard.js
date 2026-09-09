import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

/**
 * 🛡️ [Docusaurus 客户端路由自愈守卫]
 * 1. 实时拦截并清洗任何因相对导航意外造成的多语言前缀嵌套 (例如 /en/ja/docs -> /ja/docs)
 * 2. 实时规范化单页应用的末尾斜杠 (例如 /ja/showcase/ -> /ja/showcase)，防止 React Router 404
 */
export function onRouteUpdate({ location }) {
  if (!ExecutionEnvironment.canUseDOM) return;
  const pathname = (location && location.pathname) || window.location.pathname || '';
  
  // 1. 自愈多语言前缀意外嵌套
  const nestedPattern = /^\/([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_-]+)(\/.*)?$/;
  const match = pathname.match(nestedPattern);
  if (match) {
    const knownLocales = ['en', 'ja', 'zh-hans', 'zh-hant', 'es', 'fr', 'de', 'ru', 'ko', 'pt', 'it', 'ar'];
    const first = match[1].toLowerCase();
    const second = match[2].toLowerCase();
    if (knownLocales.includes(first) && knownLocales.includes(second)) {
      const rest = match[3] || '/';
      const cleanPath = `/${match[2]}${rest}`;
      if (cleanPath !== pathname) {
        window.location.replace(cleanPath);
        return;
      }
    }
  }

  // 2. 自愈独立页面末尾意外的斜杠 (例如 /showcase/ 或 /ja/showcase/)
  if (pathname.length > 1 && pathname.endsWith('/') && !pathname.endsWith('/docs/')) {
    const cleanNoSlash = pathname.replace(/\/+$/, '');
    if (cleanNoSlash && cleanNoSlash !== pathname) {
      window.location.replace(cleanNoSlash);
      return;
    }
  }

  // 3. 🛡️ 自愈脱落 /showcase 前缀的特性子页面 (例如 /block-cache-shadow-translation -> /showcase/block-cache-shadow-translation)
  const SHOWCASE_SLUGS = [
    'block-cache-shadow-translation',
    'multi-imprint-sovereignty',
    'privacy-security-pipeline',
    'galaxy-knowledge-graph',
    'intelligent-slug-seo',
    'ast-dialect-bridge',
    'multi-channel-syndication',
    'hybrid-compute-ai',
    'omni-channel-notifications',
    'janitor-gc-self-healing',
    'preflight-dry-run-probes',
    'process-lock-resilience-gateway',
    'themes-matrix'
  ];
  const singleSlugPattern = /^(?:\/([a-zA-Z0-9_-]+))?\/([a-zA-Z0-9_-]+)\/?$/;
  const slugMatch = pathname.match(singleSlugPattern);
  if (slugMatch) {
    const p1 = (slugMatch[1] || '').toLowerCase();
    const p2 = (slugMatch[2] || '').toLowerCase();
    const knownLocales = ['en', 'ja', 'zh-hans', 'zh-hant', 'es', 'fr', 'de', 'ru', 'ko', 'pt', 'it', 'ar'];
    if (!p1 && SHOWCASE_SLUGS.includes(p2)) {
      window.location.replace(`/showcase/${p2}`);
      return;
    }
    if (knownLocales.includes(p1) && SHOWCASE_SLUGS.includes(p2) && p2 !== 'showcase') {
      window.location.replace(`/${p1}/showcase/${p2}`);
      return;
    }
  }

  // 4. 激活全局内联双链悬浮预览卡片
  try {
    import('../../static/wiki-preview-core.js').then((m) => {
      if (m && m.initWikiPreview) m.initWikiPreview();
    }).catch(() => {});
  } catch {}

  // 5. 激活文章正文顶部出版级全息装帧元数据栏
  try {
    import('../../static/article-telemetry-core.js').then((m) => {
      if (m && m.mountArticleTelemetry) m.mountArticleTelemetry();
    }).catch(() => {});
  } catch {}
}

