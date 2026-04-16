/**
 * Swizzled DocItem/Footer — adds backlinks panel below each doc page.
 */
import React, { useEffect, useState } from 'react';
import Footer from '@theme-original/DocItem/Footer';
import { useLocation } from '@docusaurus/router';
import BrowserOnly from '@docusaurus/BrowserOnly';

function BacklinksPanel() {
  const location = useLocation();
  const [backlinks, setBacklinks] = useState([]);
  const isEn = location.pathname.startsWith('/en/');

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch('/graph.json');
        if (!res.ok) return;
        const data = await res.json();
        const allBacklinks = data.backlinks || {};

        // Normalize path (strip trailing slash)
        const normalize = (p) => {
          const r = p.replace(/\/$/, '');
          return r === '' ? '/' : r;
        };
        const currentNorm = normalize(location.pathname);

        const found = [];
        for (const [targetUrl, sources] of Object.entries(allBacklinks)) {
          if (normalize(targetUrl) === currentNorm) {
            found.push(...sources);
          }
        }
        setBacklinks(found);
      } catch {
        // graph.json not available — silently skip
      }
    })();
  }, [location.pathname]);

  if (backlinks.length === 0) return null;

  return (
    <div style={{
      marginTop: '2rem',
      padding: '1rem 1.25rem',
      borderRadius: '0.5rem',
      background: 'var(--ifm-background-surface-color, var(--ifm-color-emphasis-100))',
      border: '1px solid var(--ifm-toc-border-color, var(--ifm-color-emphasis-200))',
    }}>
      <h3 style={{
        margin: '0 0 0.75rem 0',
        fontSize: '0.85rem',
        fontWeight: 600,
        color: 'var(--ifm-color-emphasis-700)',
      }}>
        🌱 {isEn ? 'Backlinks' : '漫游关联'}
        <span style={{
          marginLeft: '0.5rem',
          fontSize: '0.75rem',
          opacity: 0.6,
        }}>({backlinks.length})</span>
      </h3>
      <ul style={{
        listStyle: 'none',
        padding: 0,
        margin: 0,
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0.5rem',
      }}>
        {backlinks.map((bl, i) => (
          <li key={i}>
            <a
              href={bl.url}
              style={{
                display: 'inline-block',
                padding: '0.25rem 0.75rem',
                borderRadius: '1rem',
                fontSize: '0.8rem',
                background: 'var(--ifm-color-emphasis-200)',
                color: 'var(--ifm-color-emphasis-800)',
                textDecoration: 'none',
                transition: 'background 0.2s',
              }}
              onMouseOver={(e) => e.target.style.background = 'var(--ifm-color-primary-lightest)'}
              onMouseOut={(e) => e.target.style.background = 'var(--ifm-color-emphasis-200)'}
            >
              {bl.title || bl.url}
            </a>
          </li>
        ))}
      </ul>
    </div>
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
