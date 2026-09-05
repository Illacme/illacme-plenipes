/**
 * TopologyCanvas — Docusaurus sidebar graph component
 * Fetches /graph.json at runtime and renders using shared topology-core.js
 *
 * Uses BrowserOnly to prevent SSR issues with topology-core's window/document usage.
 */
import React, { useEffect, useRef, useState } from 'react';
import { useLocation } from '@docusaurus/router';
import { useColorMode } from '@docusaurus/theme-common';
import BrowserOnly from '@docusaurus/BrowserOnly';

function TopologyCanvasInner({ height = 250 }) {
  const containerRef = useRef(null);
  const graphRef     = useRef(null);
  const location     = useLocation();
  const { colorMode } = useColorMode();
  const [loaded, setLoaded] = useState(false);

  // Extract locale from path with dynamic prefix matching
  const getLocale = (path) => {
    if (path.startsWith('/en/') || path === '/en') return 'en';
    if (path.startsWith('/ja/') || path === '/ja') return 'ja';
    if (path.startsWith('/zh-Hans/') || path === '/zh-Hans') return 'zh-Hans';
    const m = path.match(/^\/([a-z]{2}(-[A-Za-z]+)?)\//);
    if (m && !['docs', 'blog', 'showcase', 'auto'].includes(m[1])) {
      return m[1];
    }
    return 'root';
  };

  const currentLocale = getLocale(location.pathname);

  // Dynamic language filtering aligned with Starlight & Universal
  const matchUrl = (url) => {
    if (currentLocale === 'root') {
      return !url.startsWith('/en/') && !url.startsWith('/ja/') && !url.startsWith('/zh-Hans/') && !url.startsWith('/auto/');
    }
    return url.startsWith(`/${currentLocale}/`) || url === `/${currentLocale}`;
  };

  const getGraphTitle = (locale) => {
    switch (locale) {
      case 'en': return '🌌 Knowledge Graph';
      case 'ja': return '🌌 ナレッジグラフ';
      case 'ko': return '🌌 지식 그래프';
      default:   return '🌌 关系图谱';
    }
  };

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const { ensureD3, fetchGraphData, renderTopologyGraph } =
          await import('@site/src/lib/topology-core');

        const data = await fetchGraphData('/graph.json', matchUrl);
        if (cancelled) return;

        const hasBacklinks = data?.backlinks && Object.keys(data.backlinks).length > 0;
        const hasNodes = data?.all_nodes && Object.keys(data.all_nodes).length > 0;
        
        if (!hasBacklinks && !hasNodes) {
           setLoaded(true);
           return;
        }

        await ensureD3();
        if (cancelled) return;

        if (graphRef.current) graphRef.current.destroy();

        const result = renderTopologyGraph(containerRef.current, data, {
          height,
          darkMode: colorMode === 'dark',
          activeUrl: location.pathname,
        });

        graphRef.current = result;
        setLoaded(true);
      } catch (e) {
        console.warn('[TopologyCanvas] Failed to load graph:', e);
      }
    })();

    return () => {
      cancelled = true;
      if (graphRef.current) {
        graphRef.current.destroy();
        graphRef.current = null;
      }
    };
  }, [location.pathname, colorMode]);

  return (
    <div className="topology-canvas-wrapper" style={{
      margin: '0 0 1rem 0',
      padding: '0.75rem',
      borderRadius: '0.5rem',
      background: 'var(--ifm-background-surface-color, var(--ifm-color-emphasis-100))',
      border: '1px solid var(--ifm-toc-border-color, var(--ifm-color-emphasis-200))',
      minHeight: '100px'
    }}>
      <div style={{
        fontSize: '0.75rem',
        fontWeight: 600,
        marginBottom: '0.5rem',
        color: 'var(--ifm-color-emphasis-700)',
      }}>
        {getGraphTitle(currentLocale)}
      </div>
      <div
        ref={containerRef}
        style={{
          width: '100%',
          height: `${height}px`,
          overflow: 'hidden',
          opacity: loaded ? 1 : 0.5,
          transition: 'opacity 0.5s'
        }}
      />
    </div>
  );
}




export default function TopologyCanvas(props) {
  return (
    <BrowserOnly fallback={<div style={{ height: props.height || 250 }} />}>
      {() => <TopologyCanvasInner {...props} />}
    </BrowserOnly>
  );
}
