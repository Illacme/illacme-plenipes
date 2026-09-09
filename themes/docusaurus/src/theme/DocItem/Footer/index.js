/**
 * Swizzled DocItem/Footer — adds backlinks panel below each doc page.
 */
import React, { useEffect, useState } from 'react';
import Footer from '@theme-original/DocItem/Footer';
import { useLocation } from '@docusaurus/router';
import BrowserOnly from '@docusaurus/BrowserOnly';

const I18N = {
  en: { title: '🔗 Linked Mentions', subtitle: 'Documents referencing this page' },
  ja: { title: '🔗 双方向リンクと参照', subtitle: 'このページを参照している文書' },
  ko: { title: '🔗 양방향 링크 및 참조', subtitle: '이 문서를 참조하는 문서' },
  zh: { title: '🔗 双向链接与引用回响', subtitle: '提及本篇的手稿' }
};

const cleanDocUrl = (u) => !u ? '/' : String(u).replace(/\/engineering\/engineering\//g, '/engineering/');

function BacklinksPanel() {
  const location = useLocation();
  const [backlinks, setBacklinks] = useState([]);

  const getLocale = (path) => {
    if (path.startsWith('/en/') || path === '/en') return 'en';
    if (path.startsWith('/ja/') || path === '/ja') return 'ja';
    if (path.startsWith('/ko/') || path === '/ko') return 'ko';
    return 'zh';
  };

  const currentLocale = getLocale(location.pathname);
  const t = I18N[currentLocale] || I18N.zh;

  useEffect(() => {
    let cancelled = false;
    try {
      import('@site/static/article-telemetry-core.js').then((m) => {
        if (m && m.mountArticleTelemetry) m.mountArticleTelemetry();
      }).catch(() => {});
    } catch {}
    (async () => {
      try {
        const res = await fetch('/graph.json');
        if (!res.ok) return;
        const data = await res.json();
        if (cancelled) return;
        const allBacklinks = data.backlinks || {};

        const currentPath = (location.pathname || '').split('?')[0].split('#')[0];
        const clean = (u) => (u ? u.split('?')[0].split('#')[0].replace(/\/$/, '') || '/' : '');
        const targetClean = clean(currentPath);

        const allTargetUrls = Object.keys(allBacklinks);
        let matchedKey = allTargetUrls.find(u => clean(u) === targetClean);
        if (!matchedKey && targetClean !== '/') {
          matchedKey = allTargetUrls.find(u => {
            const c = clean(u);
            return c !== '/' && (c.endsWith(targetClean) || targetClean.endsWith(c));
          });
        }

        if (matchedKey && allBacklinks[matchedKey]) {
          setBacklinks(allBacklinks[matchedKey] || []);
        } else {
          setBacklinks([]);
        }
      } catch {
        setBacklinks([]);
      }
    })();

    return () => { cancelled = true; };
  }, [location.pathname]);

  if (!backlinks || backlinks.length === 0) return null;

  return (
    <section
      className="linked-mentions-container"
      style={{
        marginTop: '2.5rem',
        marginBottom: '2rem',
        padding: '1.25rem 1.5rem',
        borderRadius: '0.75rem',
        background: 'var(--ifm-background-surface-color, var(--ifm-color-emphasis-100))',
        border: '1px solid var(--ifm-toc-border-color, var(--ifm-color-emphasis-200))',
        boxShadow: '0 2px 8px rgba(0,0,0,0.03)',
        boxSizing: 'border-box',
      }}
    >
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '1rem',
        borderBottom: '1px solid var(--ifm-color-emphasis-200)',
        paddingBottom: '0.65rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--ifm-color-emphasis-900)' }}>
            {t.title}
          </span>
          <span style={{
            fontSize: '0.75rem',
            fontWeight: 700,
            padding: '2px 8px',
            borderRadius: '9999px',
            background: 'var(--ifm-color-primary-lightest)',
            color: 'var(--ifm-color-primary)',
          }}>
            {backlinks.length}
          </span>
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--ifm-color-emphasis-600)' }}>
          {t.subtitle}
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
        gap: '10px',
      }}>
        {backlinks.map((bl, i) => (
          <a
            key={i}
            href={cleanDocUrl(bl.url)}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '10px 14px',
              borderRadius: '8px',
              background: 'var(--ifm-card-background-color, #ffffff)',
              border: '1px solid var(--ifm-color-emphasis-200)',
              color: 'var(--ifm-color-emphasis-800)',
              textDecoration: 'none',
              fontSize: '0.85rem',
              fontWeight: 600,
              transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
              boxShadow: '0 1px 2px rgba(0, 0, 0, 0.03)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.borderColor = 'var(--ifm-color-primary)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.08)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.borderColor = 'var(--ifm-color-emphasis-200)';
              e.currentTarget.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.03)';
            }}
          >
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginRight: '8px' }}>
              📄 {bl.title || bl.url}
            </span>
            <span style={{ fontSize: '0.8rem', opacity: 0.5, flexShrink: 0 }}>↗</span>
          </a>
        ))}
      </div>
    </section>
  );
}

export default function FooterWrapper(props) {
  return (
    <>
      <Footer {...props} />
      <BrowserOnly>{() => <BacklinksPanel />}</BrowserOnly>
    </>
  );
}
