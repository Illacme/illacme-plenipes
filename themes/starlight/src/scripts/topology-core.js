/**
 * @file topology-core.js
 * @description Framework-agnostic D3 force-directed graph renderer for plenipes.
 *   Consumes the standard graph.json format (node_titles, all_nodes, backlinks)
 *   and renders an Obsidian-style knowledge graph into any DOM container.
 *
 * @canonical themes/shared/topology-core.js
 * @version 1.0.0
 *
 * Usage (any framework):
 *   import { renderTopologyGraph } from './topology-core.js';
 *   await renderTopologyGraph(containerEl, graphData, options);
 *
 * Usage (vanilla HTML, runtime load):
 *   <script src="/topology-core.js"></script>
 *   <script>
 *     PlenipesTopology.renderTopologyGraph(el, data, opts);
 *   </script>
 */

// ─── D3 Lazy Loader ──────────────────────────────────────────────────────────

let _d3LoadPromise = null;

/**
 * Ensures D3 v7 is available on window.d3.
 * Safe to call multiple times — only loads once.
 * @returns {Promise<void>}
 */
export function ensureD3() {
  if (typeof window !== 'undefined' && window.d3) return Promise.resolve();
  if (!_d3LoadPromise) {
    _d3LoadPromise = new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = '/d3.v7.min.js';
      s.onload = () => resolve();
      s.onerror = () => {
        // Fallback to CDN if local fails
        const fallback = document.createElement('script');
        fallback.src = 'https://d3js.org/d3.v7.min.js';
        fallback.onload = () => resolve();
        fallback.onerror = () => reject(new Error('Failed to load D3 from local or CDN'));
        document.head.appendChild(fallback);
      };
      document.head.appendChild(s);
    });
  }
  return _d3LoadPromise;
}

// ─── Graph Data Builder ───────────────────────────────────────────────────────

/**
 * Builds a normalized { nodes, links } structure from plenipes graph.json data.
 * @param {object} data - Parsed graph.json content
 * @returns {{ nodes: Array, links: Array }}
 */
export function buildGraphData(data) {
  const nodeTitles  = data.node_titles || {};
  const allNodesList = data.all_nodes  || {};
  const backlinks   = data.backlinks   || {};

  const getTitle = (url, fallback) =>
    nodeTitles[url] ||
    allNodesList[url] ||
    fallback ||
    (url.split('/').filter(Boolean).pop() || '').replace(/-/g, ' ') ||
    url;

  const nodesMap = new Map();
  const links    = [];

  // Connected nodes first (from backlinks)
  for (const [targetUrl, sources] of Object.entries(backlinks)) {
    if (!nodesMap.has(targetUrl))
      nodesMap.set(targetUrl, { id: targetUrl, title: getTitle(targetUrl), url: targetUrl });
    for (const src of sources) {
      if (!nodesMap.has(src.url))
        nodesMap.set(src.url, { id: src.url, title: getTitle(src.url, src.title), url: src.url });
      links.push({ source: src.url, target: targetUrl });
    }
  }

  // Isolated nodes (no connections)
  for (const [url, title] of Object.entries(allNodesList)) {
    if (!nodesMap.has(url))
      nodesMap.set(url, { id: url, title, url });
  }

  return { nodes: Array.from(nodesMap.values()), links };
}

// ─── Runtime Data Loader ──────────────────────────────────────────────────────

/**
 * Filters graph.json data to a single language.
 * @param {object} rawData  - Full parsed graph.json
 * @param {function} matchUrl - fn(url: string) => boolean — true if URL belongs to target language
 * @returns {object} - Filtered graph data (same shape as input)
 */
export function filterGraphData(rawData, matchUrl) {
  const filtered = {
    version: rawData.version,
    node_titles: {},
    all_nodes: {},
    backlinks: {},
  };

  // Filter node_titles
  for (const [url, title] of Object.entries(rawData.node_titles || {})) {
    if (matchUrl(url)) filtered.node_titles[url] = title;
  }

  // Filter all_nodes
  for (const [url, title] of Object.entries(rawData.all_nodes || {})) {
    if (matchUrl(url)) filtered.all_nodes[url] = title;
  }

  // Filter backlinks (target + all sources must match lang)
  for (const [targetUrl, sources] of Object.entries(rawData.backlinks || {})) {
    if (!matchUrl(targetUrl)) continue;
    const filteredSources = sources.filter(s => matchUrl(s.url));
    if (filteredSources.length > 0) filtered.backlinks[targetUrl] = filteredSources;
  }

  return filtered;
}

/**
 * Fetches graph.json from a URL and optionally filters by language.
 * @param {string}   url       - URL to fetch (e.g. '/graph.json')
 * @param {function} [matchUrl] - Optional lang filter fn(url: string) => boolean
 * @returns {Promise<object>}  - Filtered (or raw) graph data
 */
export async function fetchGraphData(url = '/graph.json', matchUrl = null) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch graph data: ${res.status} ${url}`);
  const raw = await res.json();
  return matchUrl ? filterGraphData(raw, matchUrl) : raw;
}

// ─── Color Theme ─────────────────────────────────────────────────────────────

const PALETTE = {
  dark: {
    node: '#818cf8', nodeDim: '#312e81', nodeHov: '#38bdf8',
    link: '#6366f1', linkHov: '#38bdf8',
    label: '#f8fafc', labelDim: '#94a3b8',
    labelStroke: '#090d16',
    linkOpacity: 0.35, linkOpacityHov: 0.85, linkOpacityDim: 0.08,
  },
  light: {
    node: '#4f46e5', nodeDim: '#c7d2fe', nodeHov: '#4338ca',
    link: '#818cf8', linkHov: '#4338ca',
    label: '#0f172a', labelDim: '#475569',
    labelStroke: '#ffffff',
    linkOpacity: 0.35, linkOpacityHov: 0.85, linkOpacityDim: 0.08,
  },
};

/**
 * Returns the appropriate color palette.
 * @param {boolean|'auto'} darkMode
 * @returns {object}
 */
export function getColors(darkMode = 'auto') {
  let isDark = false;
  if (darkMode === 'auto') {
    if (typeof document !== 'undefined') {
      const theme = document.documentElement.getAttribute('data-theme');
      if (theme) {
        isDark = (theme === 'dark');
      } else {
        isDark = document.documentElement.classList.contains('dark') ||
                 (typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
      }
    }
  } else {
    isDark = Boolean(darkMode);
  }
  return isDark ? PALETTE.dark : PALETTE.light;
}

// ─── Adjacency Helpers ────────────────────────────────────────────────────────

function neighborSet(links, nodeId) {
  const s = new Set();
  for (const l of links) {
    const src = typeof l.source === 'object' ? l.source.id : l.source;
    const tgt = typeof l.target === 'object' ? l.target.id : l.target;
    if (src === nodeId) s.add(tgt);
    if (tgt === nodeId) s.add(src);
  }
  return s;
}

function isConnectedLink(l, nodeId) {
  const src = typeof l.source === 'object' ? l.source.id : l.source;
  const tgt = typeof l.target === 'object' ? l.target.id : l.target;
  return src === nodeId || tgt === nodeId;
}

// ─── Main Renderer ────────────────────────────────────────────────────────────

/**
 * @typedef {object} TopologyOptions
 * @property {number}           [height=250]        - Canvas height in px
 * @property {number|null}      [width=null]        - Canvas width (null = auto from container)
 * @property {boolean|'auto'}   [darkMode='auto']   - Color scheme
 * @property {number}           [nodeRadius=4]      - Base node radius
 * @property {number}           [nodeRadiusHover=8] - Hovered node radius
 * @property {number}           [labelTruncate=11]  - Max title chars before truncation
 * @property {string|null}      [activeUrl=null]    - URL of the currently active document
 * @property {function}         [widthDetector]     - Optional fn() => number for custom width detection
 * @property {function}         [onNavigate]        - fn(url: string) — default: window.location.href = url
 */

/**
 * Renders the plenipes topology graph into `container`.
 * Expects D3 to already be loaded (call ensureD3() first).
 *
 * @param {HTMLElement}    container - The DOM element to render into (will be cleared)
 * @param {object}         data      - Parsed graph.json content
 * @param {TopologyOptions} [options={}]
 * @returns {object} - { simulation, destroy } — call destroy() to stop and clean up
 */
export function renderTopologyGraph(container, data, options = {}) {
  const d3 = window.d3;
  if (!d3) throw new Error('D3 is not loaded. Call ensureD3() first.');

  const {
    darkMode      = 'auto',
    nodeRadius    = 4,
    nodeRadiusHov = 8,
    labelTruncate = 11,
    activeUrl     = null,
    onNavigate    = (url) => { window.location.href = url; },
    widthDetector = null,
  } = options;

  // Dimensions
  const containerRect = container.getBoundingClientRect();
  let width = options.width ?? (
    widthDetector ? widthDetector() :
    (containerRect.width > 0 ? Math.floor(containerRect.width) : 250)
  );
  const height = options.height ?? (container.clientHeight || 250);
  width = Math.max(100, width);

  // Colors
  const C = getColors(darkMode);

  // Build graph
  const { nodes, links } = buildGraphData(data);
  if (nodes.length === 0) return null;

  // Calculate degree (connection count) for celestial sizing & label hierarchy
  const degMap = new Map();
  nodes.forEach(n => degMap.set(n.id, 0));
  links.forEach(l => {
    const s = typeof l.source === 'object' ? l.source.id : l.source;
    const t = typeof l.target === 'object' ? l.target.id : l.target;
    degMap.set(s, (degMap.get(s) || 0) + 1);
    degMap.set(t, (degMap.get(t) || 0) + 1);
  });

  // Current active doc path matching
  const currentPath = (activeUrl || (typeof window !== 'undefined' ? window.location.pathname : ''))
    .replace(/\/$/, '') || '/';

  nodes.forEach((n, idx) => {
    n.degree = degMap.get(n.id) || 0;
    // Celestial radius: leaf nodes 3.5px, major hubs up to 7px
    n.r = Math.min(7.5, Math.max(3.5, 3.5 + Math.sqrt(n.degree) * 1.3));
    
    // Check if active node
    const nClean = n.url.replace(/\/$/, '') || '/';
    n.isActive = (nClean === currentPath) || (currentPath !== '/' && nClean.endsWith(currentPath));

    // Natural cosmic spiral distribution to eliminate grid-like rows
    const angle = (idx / nodes.length) * 2 * Math.PI + ((idx % 3) * 0.4);
    const dist = 20 + Math.sqrt((idx + 1) / nodes.length) * (Math.min(width, height) * 0.36);
    n.x = width / 2 + Math.cos(angle) * dist;
    n.y = height / 2 + Math.sin(angle) * dist;
  });

  // Determine Hub nodes for default label visibility (strictly max 2-3 to guarantee 0 collision)
  // Only the active node and top 2 connected hubs show labels by default in compact cards.
  const sortedByDegree = [...nodes].filter(n => n.degree > 0).sort((a, b) => b.degree - a.degree);
  const topHubIds = new Set(sortedByDegree.slice(0, 2).map(n => n.id));
  
  nodes.forEach(n => {
    n.isHub = n.isActive || topHubIds.has(n.id);
  });

  container.innerHTML = '';
  container.style.position = 'relative';

  // Floating Micro-Tooltip for full title inspection
  const tooltip = document.createElement('div');
  tooltip.className = 'plenipes-topology-tooltip';
  Object.assign(tooltip.style, {
    position: 'absolute',
    display: 'none',
    pointerEvents: 'none',
    zIndex: '100',
    padding: '5px 10px',
    fontSize: '11px',
    lineHeight: '1.4',
    borderRadius: '6px',
    color: C.label,
    background: darkMode === true || (darkMode === 'auto' && getColors('auto') === PALETTE.dark) 
      ? 'rgba(15, 23, 42, 0.94)' : 'rgba(255, 255, 255, 0.96)',
    boxShadow: '0 6px 16px rgba(0,0,0,0.22)',
    border: `1px solid ${C.link}`,
    backdropFilter: 'blur(8px)',
    maxWidth: '220px',
    wordBreak: 'break-word',
    transition: 'opacity 0.15s ease',
  });
  container.appendChild(tooltip);

  // SVG
  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .style('overflow', 'hidden')
    .style('border-radius', '8px')
    .call(
      d3.zoom()
        .scaleExtent([0.4, 5])
        .on('zoom', (ev) => g.attr('transform', ev.transform))
    )
    .on('dblclick.zoom', null);

  const g = svg.append('g');

  // Galaxy Force simulation with organic spacing & celestial gravity
  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links)
      .id((d) => d.id)
      .distance((d) => 50 + Math.max(0, 25 - (d.source.degree + d.target.degree) * 2))
      .strength(0.6)
    )
    // Connected hubs have strong repulsion to stretch clusters; isolated nodes have tiny repulsion to float naturally
    .force('charge', d3.forceManyBody()
      .strength((d) => d.degree > 0 ? (-120 - Math.min(d.degree * 30, 220)) : -25)
      .distanceMax(Math.min(width, height) * 0.85)
    )
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('x', d3.forceX(width / 2).strength((d) => d.degree > 0 ? 0.06 : 0.12))
    .force('y', d3.forceY(height / 2).strength((d) => d.degree > 0 ? 0.06 : 0.12))
    // Generous collision buffer for hub nodes with text labels to completely eliminate collisions
    .force('collision', d3.forceCollide().radius((d) => d.isHub ? (d.r + 26) : (d.r + 10)).iterations(3));

  // Links
  const linkSel = g.append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .style('stroke', C.link)
    .style('stroke-opacity', C.linkOpacity)
    .style('stroke-width', 1.2);

  // Drag
  const drag = d3.drag()
    .on('start', (ev, d) => {
      if (!ev.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x; d.fy = d.y;
    })
    .on('drag', (ev, d) => { d.fx = ev.x; d.fy = ev.y; })
    .on('end', (ev, d) => {
      if (!ev.active) simulation.alphaTarget(0);
      d.fx = null; d.fy = null;
    });

  // Node groups (circle + label)
  const nodeGroup = g.append('g')
    .selectAll('g')
    .data(nodes)
    .join('g')
    .style('cursor', 'pointer')
    .call(drag);

  // Active halo ring for current reading page
  nodeGroup.filter((d) => d.isActive)
    .append('circle')
    .attr('class', 'active-halo')
    .attr('r', (d) => d.r + 5)
    .style('fill', 'none')
    .style('stroke', C.nodeHov)
    .style('stroke-width', 1.8)
    .style('stroke-dasharray', '3 2')
    .style('opacity', 0.9);

  // Core Circle
  nodeGroup.append('circle')
    .attr('class', 'node-circle')
    .attr('r', (d) => d.r)
    .style('fill', (d) => d.isActive ? C.nodeHov : (d.degree > 0 ? C.node : C.nodeDim))
    .style('stroke', (d) => d.isActive ? '#fff' : 'none')
    .style('stroke-width', (d) => d.isActive ? '1.5px' : '0');

  // Label Formatter
  const truncate = (s) =>
    s.length > labelTruncate ? s.slice(0, labelTruncate) + '…' : s;

  // Text Elements (Hierarchical & Anti-Collision)
  const textSel = nodeGroup.append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', (d) => `${d.r + 12}px`)
    .style('font-size', '10px')
    .style('font-weight', (d) => d.isHub || d.isActive ? '700' : '500')
    .style('fill', C.label)
    .style('stroke', C.labelStroke)
    .style('stroke-width', '2.5px')
    .style('stroke-linejoin', 'round')
    .style('paint-order', 'stroke fill')
    .style('pointer-events', 'none')
    .style('user-select', 'none')
    .style('transition', 'opacity 0.2s ease, font-size 0.2s ease')
    // Only top hubs/active nodes are visible by default
    .style('opacity', (d) => d.isHub ? '0.95' : '0')
    .text((d) => truncate(d.title || ''));

  // Interactive Hover and Click Handlers
  nodeGroup
    .on('mouseenter', function(ev, d) {
      // 🚀 核心抗遮挡：调用 raise() 将当前节点及其文字提升至最顶层渲染
      d3.select(this).raise();

      const neighbors = neighborSet(links, d.id);

      // 1. Update Nodes: Focus active and neighbors, dim the rest
      nodeGroup.select('.node-circle')
        .attr('r', (n) => n.id === d.id ? Math.max(n.r + 3, nodeRadiusHov) : n.r)
        .style('fill', (n) =>
          n.id === d.id ? C.nodeHov :
          neighbors.has(n.id) ? C.node : C.nodeDim
        )
        .style('filter', (n) =>
          n.id === d.id ? `drop-shadow(0 0 6px ${C.nodeHov})` : 'none'
        );

      // 2. Update Labels: Hovered node becomes 11.5px bold, neighbors appear, others dim
      nodeGroup.select('text')
        .style('opacity', (n) => {
          if (n.id === d.id) return '1';
          if (neighbors.has(n.id)) return '0.88';
          if (n.isHub) return '0.18';
          return '0';
        })
        .style('font-size', (n) => n.id === d.id ? '11.5px' : '10px')
        .style('font-weight', (n) => n.id === d.id ? '800' : (n.isHub ? '700' : '500'))
        .style('fill', (n) =>
          n.id === d.id ? C.nodeHov :
          neighbors.has(n.id) ? C.label : C.labelDim
        );

      // 3. Update Links
      linkSel
        .style('stroke', (l) => isConnectedLink(l, d.id) ? C.linkHov : C.link)
        .style('stroke-opacity', (l) =>
          isConnectedLink(l, d.id) ? C.linkOpacityHov : C.linkOpacityDim
        )
        .style('stroke-width', (l) => isConnectedLink(l, d.id) ? 2.5 : 1);

      // 4. Show Tooltip
      const rect = container.getBoundingClientRect();
      const x = ev.clientX - rect.left + 10;
      const y = ev.clientY - rect.top + 10;
      tooltip.innerHTML = `<strong>${d.title || d.id}</strong>` +
        (d.degree > 0 ? `<div style="font-size:10px;opacity:0.75;margin-top:2px;">🔗 ${d.degree} 处双链关联</div>` : '');
      tooltip.style.left = `${Math.min(x, width - 180)}px`;
      tooltip.style.top = `${Math.min(y, height - 50)}px`;
      tooltip.style.display = 'block';
    })
    .on('mousemove', function(ev) {
      const rect = container.getBoundingClientRect();
      const x = ev.clientX - rect.left + 10;
      const y = ev.clientY - rect.top + 10;
      tooltip.style.left = `${Math.min(x, width - 180)}px`;
      tooltip.style.top = `${Math.min(y, height - 50)}px`;
    })
    .on('mouseleave', function() {
      // Restore default galaxy breathing state
      nodeGroup.select('.node-circle')
        .attr('r', (d) => d.r)
        .style('fill', (d) => d.isActive ? C.nodeHov : (d.degree > 0 ? C.node : C.nodeDim))
        .style('filter', 'none');

      nodeGroup.select('text')
        .style('opacity', (d) => d.isHub ? '0.95' : '0')
        .style('font-size', '10px')
        .style('font-weight', (d) => d.isHub || d.isActive ? '700' : '500')
        .style('fill', C.label);

      linkSel
        .style('stroke', C.link)
        .style('stroke-opacity', C.linkOpacity)
        .style('stroke-width', 1.2);

      tooltip.style.display = 'none';
    })
    .on('click', (_ev, d) => onNavigate(d.url));

  // 🪐 Soft Elliptical Cosmic Boundary (smooth galaxy cloud, never square clamped)
  const rx = Math.max(40, (width / 2) - 22);
  const ry = Math.max(40, (height / 2) - 24);
  const cx = width / 2;
  const cy = height / 2;

  simulation.on('tick', () => {
    nodes.forEach((d) => {
      const dx = d.x - cx;
      const dy = d.y - cy;
      const distSq = (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry);
      if (distSq > 1) {
        const factor = 1 / Math.sqrt(distSq);
        d.x = cx + dx * factor;
        d.y = cy + dy * factor;
      }
    });
    linkSel
      .attr('x1', (d) => d.source.x).attr('y1', (d) => d.source.y)
      .attr('x2', (d) => d.target.x).attr('y2', (d) => d.target.y);
    nodeGroup.attr('transform', (d) => `translate(${d.x},${d.y})`);
  });

  return {
    simulation,
    /** Stop and remove the graph */
    destroy() {
      simulation.stop();
      if (tooltip && tooltip.parentNode) {
        tooltip.parentNode.removeChild(tooltip);
      }
      container.innerHTML = '';
    },
  };
}

// ─── UMD Global Export (for vanilla <script src> usage) ───────────────────────
if (typeof window !== 'undefined' && !window.PlenipesTopology) {
  window.PlenipesTopology = { ensureD3, buildGraphData, getColors, renderTopologyGraph };
}
