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

  const isEn = location.pathname.startsWith('/en/');
  const matchUrl = (url) => isEn ? url.startsWith('/en/') : !url.startsWith('/en/');

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        // Dynamic import only runs in browser context
        const { ensureD3, fetchGraphData, renderTopologyGraph } =
          await import('@site/src/lib/topology-core');

        const data = await fetchGraphData('/graph.json', matchUrl);
        if (cancelled) return;

        const hasBacklinks = data?.backlinks && Object.keys(data.backlinks).length > 0;
        const hasNodes = data?.all_nodes && Object.keys(data.all_nodes).length > 0;
        if (!hasBacklinks && !hasNodes) return;

        await ensureD3();
        if (cancelled) return;

        if (graphRef.current) graphRef.current.destroy();

        const result = renderTopologyGraph(containerRef.current, data, {
          height,
          darkMode: colorMode === 'dark',
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
    }}>
      <div style={{
        fontSize: '0.75rem',
        fontWeight: 600,
        marginBottom: '0.5rem',
        color: 'var(--ifm-color-emphasis-700)',
      }}>
        🌌 {isEn ? 'Graph View' : '关系图谱'}
      </div>
      <div
        ref={containerRef}
        style={{
          width: '100%',
          height: `${height}px`,
          overflow: 'hidden',
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
