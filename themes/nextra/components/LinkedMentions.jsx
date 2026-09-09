import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { initWikiPreview } from '../lib/wiki-preview-core';
import { mountArticleTelemetry } from '../lib/article-telemetry-core';

const I18N = {
  en: { title: '🔗 Linked Mentions', subtitle: 'Documents referencing this page', empty: 'No backlinks yet' },
  ja: { title: '🔗 双方向リンクと参照', subtitle: 'このページを参照している文書', empty: '参照文書はありません' },
  ko: { title: '🔗 양방향 링크 및 참조', subtitle: '이 문서를 참조하는 문서', empty: '참조 문서가 없습니다' },
  zh: { title: '🔗 双向链接与引用回响', subtitle: '提及本篇的手稿', empty: '暂无双向引用' }
};

function resolveNextraUrl(rawUrl) {
  if (!rawUrl) return '/';
  let u = String(rawUrl).trim();
  const [pathPart, hashPart] = u.split('#');
  let [route, queryPart] = pathPart.split('?');
  route = route.replace(/\/engineering\/engineering\//g, '/engineering/');
  route = route.replace(/^(\/(?:[a-zA-Z]{2,3}(?:-[A-Za-z0-9]+)?\/)?)docs\//, '$1');
  let finalUrl = route || '/';
  if (queryPart) finalUrl += `?${queryPart}`;
  if (hashPart) finalUrl += `#${hashPart}`;
  return finalUrl;
}

export default function LinkedMentions() {
  const router = useRouter();
  const [mentions, setMentions] = useState([]);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    initWikiPreview();
    mountArticleTelemetry();
    if (typeof document === 'undefined') return;
    const checkDark = () => {
      const el = document.documentElement;
      setIsDark(el.classList.contains('dark') || el.getAttribute('data-theme') === 'dark');
    };
    checkDark();
    const observer = new MutationObserver(checkDark);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] });
    return () => observer.disconnect();
  }, []);

  const currentLocale = (router?.locale && I18N[router.locale]) ? router.locale : 'zh';
  const t = I18N[currentLocale] || I18N.zh;

  useEffect(() => {
    let cancelled = false;
    mountArticleTelemetry();
    (async () => {
      try {
        const res = await fetch('/graph.json');
        if (!res.ok) return;
        const data = await res.json();
        if (cancelled) return;

        const backlinks = data.backlinks || {};
        const currentPath = (router.asPath || router.pathname || '').split('?')[0].split('#')[0];
        const clean = (u) => (u ? u.split('?')[0].split('#')[0].replace(/\/$/, '') || '/' : '');
        const targetClean = clean(currentPath);

        const allTargetUrls = Object.keys(backlinks);
        let matchedKey = allTargetUrls.find(u => clean(u) === targetClean);
        if (!matchedKey && targetClean !== '/') {
          matchedKey = allTargetUrls.find(u => {
            const c = clean(u);
            return c !== '/' && (c.endsWith(targetClean) || targetClean.endsWith(c));
          });
        }

        if (matchedKey && backlinks[matchedKey]) {
          setMentions(backlinks[matchedKey] || []);
        } else {
          setMentions([]);
        }
      } catch (e) {
        setMentions([]);
      }
    })();

    return () => { cancelled = true; };
  }, [router.asPath, router.locale]);

  if (!mentions || mentions.length === 0) return null;

  return (
    <section
      className="linked-mentions-container"
      style={{
        marginTop: '3rem',
        marginBottom: '2rem',
        padding: '1.25rem 1.5rem',
        borderRadius: '0.75rem',
        background: isDark ? 'rgba(30, 41, 59, 0.45)' : '#f8fafc',
        border: isDark ? '1px solid rgba(255, 255, 255, 0.08)' : '1px solid rgba(226, 232, 240, 0.95)',
        boxShadow: isDark ? '0 4px 16px rgba(0,0,0,0.2)' : '0 2px 8px rgba(0,0,0,0.02)',
        backdropFilter: 'blur(12px)',
        boxSizing: 'border-box',
        transition: 'background 0.3s ease, border-color 0.3s ease',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: isDark ? '1px solid rgba(255,255,255,0.06)' : '1px solid rgba(226,232,240,0.8)', paddingBottom: '0.65rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.95rem', fontWeight: 700, color: isDark ? '#f1f5f9' : '#0f172a' }}>
            {t.title}
          </span>
          <span style={{
            fontSize: '0.75rem',
            fontWeight: 700,
            padding: '2px 8px',
            borderRadius: '9999px',
            background: isDark ? 'rgba(56, 189, 248, 0.15)' : 'rgba(2, 132, 199, 0.1)',
            color: isDark ? '#38bdf8' : '#0284c7',
          }}>
            {mentions.length}
          </span>
        </div>
        <span style={{ fontSize: '0.75rem', color: isDark ? '#64748b' : '#94a3b8' }}>
          {t.subtitle}
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
        gap: '10px',
      }}>
        {mentions.map((item, idx) => {
          const targetUrl = resolveNextraUrl(item.url);
          return (
            <a
              key={idx}
              href={targetUrl}
              onClick={(e) => {
                if (router?.push) {
                  e.preventDefault();
                  router.push(targetUrl);
                }
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: '8px',
                background: isDark ? 'rgba(15, 23, 42, 0.5)' : '#ffffff',
                border: isDark ? '1px solid rgba(255, 255, 255, 0.08)' : '1px solid rgba(226, 232, 240, 0.9)',
                color: isDark ? '#e2e8f0' : '#1e293b',
                textDecoration: 'none',
                fontSize: '0.85rem',
                fontWeight: 600,
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                boxShadow: '0 1px 2px rgba(0, 0, 0, 0.03)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.borderColor = isDark ? '#38bdf8' : '#0284c7';
                e.currentTarget.style.boxShadow = isDark ? '0 4px 12px rgba(56, 189, 248, 0.15)' : '0 4px 12px rgba(2, 132, 199, 0.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.borderColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(226, 232, 240, 0.9)';
                e.currentTarget.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.03)';
              }}
            >
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginRight: '8px' }}>
                📄 {item.title || item.url}
              </span>
              <span style={{ fontSize: '0.8rem', opacity: 0.5, flexShrink: 0 }}>↗</span>
            </a>
          );
        })}
      </div>
    </section>
  );
}
