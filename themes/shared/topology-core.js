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
      s.src = 'https://d3js.org/d3.v7.min.js';
      s.onload = () => resolve();
      s.onerror = () => reject(new Error('Failed to load D3 from CDN'));
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
    node: '#818cf8', nodeDim: '#3730a3', nodeHov: '#a5b4fc',
    link: '#6366f1', linkHov: '#a5b4fc',
    label: '#c7d2fe', labelDim: '#4338ca',
    linkOpacity: 0.40, linkOpacityHov: 0.95, linkOpacityDim: 0.06,
  },
  light: {
    node: '#7c3aed', nodeDim: '#a78bfa', nodeHov: '#6d28d9',
    link: '#7c3aed', linkHov: '#5b21b6',
    label: '#4c1d95', labelDim: '#8b5cf6',
    linkOpacity: 0.55, linkOpacityHov: 0.95, linkOpacityDim: 0.10,
  },
};

/**
 * Returns the appropriate color palette.
 * @param {boolean|'auto'} darkMode
 * @returns {object}
 */
export function getColors(darkMode = 'auto') {
  const isDark = darkMode === 'auto'
    ? (document.documentElement.getAttribute('data-theme') === 'dark')
    : Boolean(darkMode);
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
 * @property {number}           [nodeRadius=5]      - Default node radius
 * @property {number}           [nodeRadiusHover=9] - Hovered node radius
 * @property {number}           [labelTruncate=10]  - Max title chars before truncation
 * @property {number}           [linkDistance=55]   - Force link distance
 * @property {number}           [chargeStrength=-120] - Repulsion strength
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
    nodeRadius    = 5,
    nodeRadiusHov = 9,
    labelTruncate = 10,
    linkDistance  = 55,
    chargeStrength = -120,
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

  container.innerHTML = '';

  // SVG
  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .style('overflow', 'visible')
    .call(
      d3.zoom()
        .scaleExtent([0.4, 5])
        .on('zoom', (ev) => g.attr('transform', ev.transform))
    )
    .on('dblclick.zoom', null);

  const g = svg.append('g');

  // Force simulation
  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id((d) => d.id).distance(linkDistance))
    .force('charge', d3.forceManyBody().strength(chargeStrength))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(nodeRadius + 18));

  // Links
  const linkSel = g.append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .style('stroke', C.link)
    .style('stroke-opacity', C.linkOpacity)
    .style('stroke-width', 1.5);

  // Drag
  const drag = d3.drag()
    .on('start', (ev, d) => {
      if (!ev.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x; d.fy = d.y;
    })
    .on('drag',  (ev, d) => { d.fx = ev.x; d.fy = ev.y; })
    .on('end',   (ev, d) => {
      if (!ev.active) simulation.alphaTarget(0);
      d.fx = null; d.fy = null;
    });

  // Node groups (circle + label)
  const nodeGroup = g.append('g')
    .selectAll('g')
    .data(nodes)
    .join('g')
    .style('cursor', 'pointer')
    .call(drag)
    .on('mouseover', (_ev, d) => {
      const neighbors = neighborSet(links, d.id);
      nodeGroup.select('circle')
        .attr('r', (n) => n.id === d.id ? nodeRadiusHov : nodeRadius)
        .style('fill', (n) =>
          n.id === d.id ? C.nodeHov :
          neighbors.has(n.id) ? C.node : C.nodeDim)
        .style('filter', (n) =>
          n.id === d.id ? `drop-shadow(0 0 5px ${C.nodeHov})` : 'none');
      nodeGroup.select('text')
        .style('fill', (n) =>
          n.id === d.id || neighbors.has(n.id) ? C.label : C.labelDim)
        .style('font-weight', (n) => n.id === d.id ? '700' : '400')
        .style('opacity', (n) =>
          n.id === d.id || neighbors.has(n.id) ? '1' : '0.3');
      linkSel
        .style('stroke', (l) => isConnectedLink(l, d.id) ? C.linkHov : C.link)
        .style('stroke-opacity', (l) =>
          isConnectedLink(l, d.id) ? C.linkOpacityHov : C.linkOpacityDim)
        .style('stroke-width', (l) => isConnectedLink(l, d.id) ? 2.5 : 1);
    })
    .on('mouseout', () => {
      nodeGroup.select('circle')
        .attr('r', nodeRadius)
        .style('fill', C.node)
        .style('filter', 'none');
      nodeGroup.select('text')
        .style('fill', C.label)
        .style('font-weight', '400')
        .style('opacity', '1');
      linkSel
        .style('stroke', C.link)
        .style('stroke-opacity', C.linkOpacity)
        .style('stroke-width', 1.5);
    })
    .on('click', (_ev, d) => onNavigate(d.url));

  // Circle
  nodeGroup.append('circle')
    .attr('r', nodeRadius)
    .style('fill', C.node)
    .style('stroke', 'none');

  // Label
  const truncate = (s) =>
    s.length > labelTruncate ? s.slice(0, labelTruncate) + '…' : s;

  nodeGroup.append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', `${nodeRadius + 11}px`)
    .style('font-size', '9px')
    .style('fill', C.label)
    .style('pointer-events', 'none')
    .style('user-select', 'none')
    .text((d) => truncate(d.title || ''));

  // Tick
  simulation.on('tick', () => {
    const r = nodeRadius;
    nodes.forEach((d) => {
      d.x = Math.max(r + 20, Math.min(width  - r - 20, d.x));
      d.y = Math.max(r + 14, Math.min(height - r - 14, d.y));
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
      container.innerHTML = '';
    },
  };
}

// ─── UMD Global Export (for vanilla <script src> usage) ───────────────────────
if (typeof window !== 'undefined' && !window.PlenipesTopology) {
  window.PlenipesTopology = { ensureD3, buildGraphData, getColors, renderTopologyGraph };
}
