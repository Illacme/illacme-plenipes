/**
 * TopologyCanvas — Docusaurus sidebar & fullscreen immersive graph component
 * Fetches /graph.json at runtime and renders using shared topology-core.js
 * Uses BrowserOnly to prevent SSR issues with topology-core's window/document usage.
 */
import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useLocation, useHistory } from '@docusaurus/router';
import { useColorMode } from '@docusaurus/theme-common';
import BrowserOnly from '@docusaurus/BrowserOnly';

const I18N = {
  en: {
    title: '🌌 Local Graph',
    modalTitle: '🌌 Celestial Knowledge Galaxy',
    btn: 'Fullscreen',
    hint: '💡 Hint: Scroll to Zoom / Drag to Pan / Click Node to Teleport / Press ESC or Click Top-Right to Exit',
    close: '✕ Exit Fullscreen [ESC]'
  },
  ja: {
    title: '🌌 局所グラフ',
    modalTitle: '🌌 全域星系ナレッジグラフ',
    btn: '全画面',
    hint: '💡 ヒント: スクロールで拡大縮小 / ドラッグで移動 / クリックで移動 / ESCキーまたは右上で安全終了',
    close: '✕ 全画面終了 [ESC]'
  },
  ko: {
    title: '🌌 로컬 그래프',
    modalTitle: '🌌 전역 지식 은하망',
    btn: '전체 화면',
    hint: '💡 팁: 스크롤로 확대축소 / 드래그로 이동 / 클릭하여 이동 / ESC 키 또는 오른쪽 위로 안전 종료',
    close: '✕ 전체 화면 종료 [ESC]'
  },
  zh: {
    title: '🌌 局部关系图谱',
    modalTitle: '🌌 全域星系知识网络',
    btn: '全屏探索',
    hint: '💡 提示: 滚轮缩放 / 拖拽漫游 / 点击节点穿梭 / 点击右上角或按 ESC 键安全退出',
    close: '✕ 退出全屏 [ESC]'
  }
};

function TopologyCanvasInner({ height = 260 }) {
  const containerRef           = useRef(null);
  const graphRef               = useRef(null);
  const fullscreenContainerRef = useRef(null);
  const fullscreenGraphRef     = useRef(null);

  const location      = useLocation();
  const history       = useHistory();
  const { colorMode } = useColorMode();

  const [loaded, setLoaded]           = useState(false);
  const [graphData, setGraphData]     = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const getLocale = (path) => {
    if (path.startsWith('/en/') || path === '/en') return 'en';
    if (path.startsWith('/ja/') || path === '/ja') return 'ja';
    if (path.startsWith('/ko/') || path === '/ko') return 'ko';
    if (path.startsWith('/zh-Hans/') || path === '/zh-Hans') return 'zh';
    return 'zh';
  };

  const currentLocale = getLocale(location.pathname);
  const t = I18N[currentLocale] || I18N.zh;

  const matchUrl = (url) => {
    if (currentLocale === 'zh') {
      return !url.startsWith('/en/') && !url.startsWith('/ja/') && !url.startsWith('/ko/') && !url.startsWith('/auto/');
    }
    return url.startsWith(`/${currentLocale}/`) || url === `/${currentLocale}`;
  };

  // 1. 小图局部图谱渲染
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const { ensureD3, fetchGraphData, renderTopologyGraph } = await import('../lib/topology-core');
        const data = await fetchGraphData('/graph.json', matchUrl);
        if (cancelled) return;
        if (!data?.backlinks && !data?.all_nodes) { setLoaded(true); return; }

        setGraphData(data);
        await ensureD3();
        if (cancelled || !containerRef.current) return;

        if (graphRef.current) graphRef.current.destroy();
        const cardW = Math.max(containerRef.current.clientWidth || 0, 260);
        graphRef.current = renderTopologyGraph(containerRef.current, data, {
          width: cardW,
          height,
          darkMode: colorMode === 'dark',
          activeUrl: location.pathname,
          isLocal: true,
          localDepth: 1,
          onNavigate: (url) => {
            if (history?.push) history.push(url);
            else window.location.href = url;
          }
        });
        setLoaded(true);
      } catch (e) {
        console.warn('[Docusaurus:TopologyCanvas] Failed to load graph:', e);
      }
    })();

    return () => {
      cancelled = true;
      if (graphRef.current) { graphRef.current.destroy(); graphRef.current = null; }
    };
  }, [location.pathname, colorMode, height]);

  // 2. ESC 退出全屏与滚动条锁定
  useEffect(() => {
    if (!isModalOpen) return;
    const handleKeyDown = (e) => { if (e.key === 'Escape') setIsModalOpen(false); };
    window.addEventListener('keydown', handleKeyDown);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = prevOverflow;
    };
  }, [isModalOpen]);

  // 3. 全屏星系展开
  useEffect(() => {
    if (!isModalOpen || !graphData || !fullscreenContainerRef.current) return;
    let destroyed = false;

    (async () => {
      try {
        const { ensureD3, renderTopologyGraph } = await import('../lib/topology-core');
        await ensureD3();
        if (destroyed || !fullscreenContainerRef.current) return;
        if (fullscreenGraphRef.current) fullscreenGraphRef.current.destroy();

        const rect = fullscreenContainerRef.current.getBoundingClientRect();
        fullscreenGraphRef.current = renderTopologyGraph(fullscreenContainerRef.current, graphData, {
          width: Math.floor(rect.width || window.innerWidth * 0.96),
          height: Math.floor(rect.height || window.innerHeight * 0.86),
          nodeRadius: 5.5,
          nodeRadiusHov: 11,
          labelTruncate: 24,
          isExpanded: true,
          darkMode: colorMode === 'dark',
          activeUrl: location.pathname,
          onNavigate: (url) => {
            setIsModalOpen(false);
            if (history?.push) history.push(url);
            else window.location.href = url;
          }
        });
      } catch (e) {
        console.warn('[Docusaurus:TopologyCanvas] Fullscreen graph failed:', e);
      }
    })();

    return () => {
      destroyed = true;
      if (fullscreenGraphRef.current) {
        fullscreenGraphRef.current.destroy();
        fullscreenGraphRef.current = null;
      }
    };
  }, [isModalOpen, graphData, colorMode, location.pathname]);

  const isDark = colorMode === 'dark';

  const modalContent = isModalOpen && typeof document !== 'undefined' ? (
    <div
      className="topology-fullscreen-modal"
      style={{
        position: 'fixed',
        inset: 0,
        width: '100vw',
        height: '100vh',
        zIndex: 999999,
        background: isDark ? 'rgba(15, 23, 42, 0.96)' : 'rgba(255, 255, 255, 0.98)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        display: 'flex',
        flexDirection: 'column',
        boxSizing: 'border-box',
        padding: '1.25rem 1.5rem',
      }}
    >
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: isDark ? '1px solid rgba(255, 255, 255, 0.12)' : '1px solid rgba(226, 232, 240, 0.9)',
        paddingBottom: '0.85rem',
        marginBottom: '0.75rem',
      }}>
        <div>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--ifm-heading-color)' }}>{t.modalTitle}</div>
          <div style={{ fontSize: '0.78rem', color: isDark ? '#38bdf8' : '#0284c7', marginTop: '4px', fontWeight: 500 }}>{t.hint}</div>
        </div>
        <button
          type="button"
          onClick={() => setIsModalOpen(false)}
          style={{
            background: isDark ? 'rgba(239, 68, 68, 0.15)' : 'rgba(239, 68, 68, 0.1)',
            border: isDark ? '1px solid rgba(239, 68, 68, 0.35)' : '1px solid rgba(239, 68, 68, 0.25)',
            borderRadius: '8px',
            padding: '7px 16px',
            fontSize: '0.85rem',
            fontWeight: 700,
            cursor: 'pointer',
            color: isDark ? '#fca5a5' : '#dc2626',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
          }}
          title="点击退出全屏 (ESC)"
        >
          {t.close}
        </button>
      </div>

      <div
        ref={fullscreenContainerRef}
        style={{ flex: 1, width: '100%', height: '100%', overflow: 'hidden', borderRadius: '10px', position: 'relative' }}
      />
    </div>
  ) : null;

  return (
    <div
      className="topology-canvas-wrapper"
      style={{
        margin: '0 0 1rem 0',
        padding: '0.85rem',
        borderRadius: '0.65rem',
        background: isDark ? 'rgba(30, 41, 59, 0.55)' : '#f8fafc',
        border: '1px solid var(--ifm-toc-border-color, rgba(226, 232, 240, 0.9))',
        width: '100%',
        maxWidth: '100%',
        boxSizing: 'border-box',
        boxShadow: isDark ? '0 4px 12px rgba(0,0,0,0.25)' : '0 2px 6px rgba(0,0,0,0.03)'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--ifm-color-emphasis-700)' }}>{t.title}</div>
        <button
          type="button"
          onClick={() => setIsModalOpen(true)}
          style={{
            background: 'var(--ifm-color-emphasis-200)',
            border: 'none',
            borderRadius: '5px',
            padding: '3px 8px',
            fontSize: '0.72rem',
            fontWeight: 600,
            cursor: 'pointer',
            color: 'var(--ifm-color-emphasis-800)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            transition: 'all 0.2s ease',
          }}
          title={t.btn}
        >
          ⛶ {t.btn}
        </button>
      </div>

      <div
        ref={containerRef}
        style={{ width: '100%', height: `${height}px`, overflow: 'hidden', opacity: loaded ? 1 : 0.5, transition: 'opacity 0.5s' }}
      />

      {modalContent && createPortal(modalContent, document.body)}
    </div>
  );
}

export default function TopologyCanvas(props) {
  return (
    <BrowserOnly fallback={<div style={{ height: props.height || 260 }} />}>
      {() => <TopologyCanvasInner {...props} />}
    </BrowserOnly>
  );
}
