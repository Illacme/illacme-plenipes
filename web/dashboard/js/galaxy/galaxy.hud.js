/**
 * 🚀 [V100.0] Illacme Plenipes 3D Galaxy Engine - HUD & Interactive Control Module
 * 职责：物理注入 HUD 控制区（右上角搜索与星球控制仪、左上角精简指标与动力学折叠面板）。
 * 符合 SOP-02 模块拆分协议，行数严格控制在 300 行内。
 */

// 1. 初始化交互状态与默认参数
window._showWikilinks = true;
window._showSemanticLinks = true;
window._galaxyConnectionSourceNode = null;
window._currentNode = null;

// 🪐 动态绑定 HUD 知识关联指标
window.updateGalaxyHUD = (nodes, links) => {
    // 注入控制 DOM 结构
    injectGalaxyInteractiveDOM();
    if (typeof window.injectGalaxyDirectorDOM === 'function') {
        window.injectGalaxyDirectorDOM();
    }

    const densityEl = document.getElementById('density-val');
    const connEl = document.getElementById('conn-count');
    if (densityEl) {
        const N = nodes ? nodes.length : 0;
        const L = links ? links.length : 0;
        const density = N > 1 ? (2 * L) / (N * (N - 1)) : 0;
        densityEl.innerText = density.toFixed(2);
    }
    if (connEl) {
        connEl.innerText = links ? links.length : 0;
    }
};

// ⚡ 隔离孤立节点交互逻辑
window._filterConnectedOnly = false;
window.toggleConnectedNodesOnly = () => {
    if (!window.galaxyGraph || !window._lastGalaxyData) return;
    window._filterConnectedOnly = !window._filterConnectedOnly;
    const label = document.getElementById('focus-btn-label');
    const card = document.getElementById('btn-focus-connected');
    
    if (window._filterConnectedOnly) {
        const connIds = new Set();
        window._lastGalaxyData.links.forEach(l => {
            const src = l.source?.id || l.source;
            const tgt = l.target?.id || l.target;
            if (src !== undefined && tgt !== undefined) {
                connIds.add(src); connIds.add(tgt);
            }
        });
        const filteredNodes = window._lastGalaxyData.nodes.filter(n => connIds.has(n.id));
        window.galaxyGraph.graphData({ nodes: filteredNodes, links: window._lastGalaxyData.links });
        if (label) { label.innerText = '🪐 显示全部'; label.style.color = 'var(--neon-amber)'; }
        if (card) { card.style.background = 'var(--accent-orange-05)'; card.style.borderColor = 'var(--accent-orange-30)'; }
        setTimeout(() => window.galaxyGraph.zoomToFit(1000, 80), 150);
    } else {
        window.galaxyGraph.graphData(window._lastGalaxyData);
        if (label) { label.innerText = '⚡ 隔离星球'; label.style.color = 'var(--neon-cyan)'; }
        if (card) { card.style.background = 'var(--neon-cyan-05)'; card.style.borderColor = 'var(--neon-cyan-20)'; }
        setTimeout(() => window.galaxyGraph.zoomToFit(1000, 80), 150);
    }
};

function injectGalaxyInteractiveDOM() {
    const leftColumn = document.getElementById('galaxy-hud-column');
    const rightColumn = document.getElementById('galaxy-right-column');
    if (!leftColumn || !rightColumn) return;

    // 1. 注入检索框至右侧控制列
    if (!document.getElementById('galaxy-search-container')) {
        const searchDiv = document.createElement('div');
        searchDiv.id = 'galaxy-search-container';
        searchDiv.style.cssText = 'display: flex; flex-direction: column; width: 100%; padding: 6px 10px; box-sizing: border-box;';
        searchDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 0.9rem;">🔍</span>
                <input type="text" id="galaxy-search-input" placeholder="检索星空节点..." style="background: transparent; border: none; color: var(--text-bright); outline: none; width: 100%; font-size: 0.75rem;" autocomplete="off" />
            </div>
            <div id="galaxy-search-suggestions" class="scroll-container" style="display: none; max-height: 180px; overflow-y: auto; margin-top: 8px; border-top: 1px solid var(--glass-border); padding-top: 8px; flex-direction: column; gap: 4px;"></div>
        `;
        rightColumn.appendChild(searchDiv);
        setupSearchListeners();
    }

    // 3. 注入数据指标组 (Stats Unified Card) 至左侧列，支持折叠
    if (!document.getElementById('galaxy-telemetry-container')) {
        const telDiv = document.createElement('div');
        telDiv.id = 'galaxy-telemetry-container';
        telDiv.className = 'hud-item glass-panel';
        telDiv.style.cssText = 'padding: 10px 14px; width: 100%; border-radius: 12px; display: flex; flex-direction: column; gap: 8px; min-width: 0; box-sizing: border-box; animation: none; margin-top: 0;';
        telDiv.innerHTML = `
            <div id="telemetry-title-bar" style="display: flex; justify-content: space-between; align-items: center; cursor: pointer; user-select: none;">
                <span style="font-size: 0.52rem; font-weight: 800; color: var(--text-dim); letter-spacing: 0.5px;">📊 实时指标</span>
                <span id="telemetry-collapse-arrow" style="font-size: 0.52rem; color: var(--text-dim); transition: transform 0.2s;">▼</span>
            </div>
            <div id="telemetry-controls-body" class="hud-collapsible-body expanded" style="display: flex; flex-direction: column; gap: 8px;">
                <div style="display: flex; gap: 6px; align-items: center; justify-content: space-between; margin-top: 2px;">
                    <div style="flex: 1; text-align: center;">
                        <div class="hud-label" style="font-size: 0.45rem; margin-bottom: 2px; letter-spacing: 0.5px;">关联密度</div>
                        <div class="hud-value" id="density-val" style="font-size: 0.85rem; line-height: 1;">0.00</div>
                    </div>
                    <div style="flex: 1; text-align: center; border-left: 1px solid var(--glass-border); padding-left: 6px;">
                        <div class="hud-label" style="font-size: 0.45rem; margin-bottom: 2px; letter-spacing: 0.5px;">神经元</div>
                        <div class="hud-value" id="conn-count" style="font-size: 0.85rem; line-height: 1;">0</div>
                    </div>
                </div>
                <button class="primary-btn glow-btn" id="btn-focus-connected" onclick="window.toggleConnectedNodesOnly()" style="width: 100%; height: 22px; line-height: 12px; font-size: 0.55rem; cursor: pointer; border-radius: 4px; background: var(--neon-cyan-05); border: 1px solid var(--neon-cyan-20); transition: all 0.3s; padding: 0;">
                    <span id="focus-btn-label" style="color: var(--neon-cyan); letter-spacing: 0.5px; font-size: 0.55rem;">⚡ 隔离星球</span>
                </button>
            </div>
        `;
        leftColumn.appendChild(telDiv);

        // 绑定折叠点击 (默认展开)
        const tTitle = document.getElementById('telemetry-title-bar');
        const tBody = document.getElementById('telemetry-controls-body');
        const tArrow = document.getElementById('telemetry-collapse-arrow');
        if (tTitle && tBody && tArrow) {
            tTitle.onclick = () => {
                const isCollapsed = tBody.classList.contains('collapsed');
                if (isCollapsed) {
                    tBody.classList.remove('collapsed');
                    tBody.classList.add('expanded');
                    tArrow.style.transform = 'rotate(0deg)';
                } else {
                    tBody.classList.remove('expanded');
                    tBody.classList.add('collapsed');
                    tArrow.style.transform = 'rotate(-90deg)';
                }
            };
        }
    }

    // 4. 注入动力学调节器至左侧列 (支持折叠)
    if (!document.getElementById('galaxy-physics-controls')) {
        const ctrlDiv = document.createElement('div');
        ctrlDiv.id = 'galaxy-physics-controls';
        ctrlDiv.className = 'hud-item glass-panel';
        ctrlDiv.style.cssText = 'padding: 10px 14px; width: 100%; border-radius: 12px; display: flex; flex-direction: column; gap: 8px; min-width: 0; box-sizing: border-box; animation: none; margin-top: 0;';
        ctrlDiv.innerHTML = `
            <div id="physics-title-bar" style="display: flex; justify-content: space-between; align-items: center; cursor: pointer; user-select: none;">
                <span style="font-size: 0.52rem; font-weight: 800; color: var(--text-dim); letter-spacing: 0.5px;">📐 物理控制</span>
                <span id="physics-collapse-arrow" style="font-size: 0.52rem; color: var(--text-dim); transition: transform 0.2s;">▼</span>
            </div>
            <div id="physics-controls-body" class="hud-collapsible-body collapsed" style="display: flex; flex-direction: column; gap: 6px; font-size: 0.6rem; color: var(--text-dim);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                    <span>引力:</span>
                    <input type="range" id="gravity-distance-slider" min="30" max="200" value="80" style="width: 75px; height: 2px; accent-color: var(--accent-secondary);" />
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>排斥:</span>
                    <input type="range" id="charge-strength-slider" min="-300" max="-20" value="-120" style="width: 75px; height: 2px; accent-color: var(--accent-secondary);" />
                </div>
                <div style="display: flex; gap: 8px; margin-top: 4px; justify-content: space-between; font-size: 0.55rem;">
                    <label style="display: flex; align-items: center; gap: 3px; cursor: pointer;">
                        <input type="checkbox" id="toggle-wikilinks" checked style="accent-color: var(--accent-secondary);" /> 物理
                    </label>
                    <label style="display: flex; align-items: center; gap: 3px; cursor: pointer;">
                        <input type="checkbox" id="toggle-semantic-links" checked style="accent-color: var(--accent-secondary);" /> 语义
                    </label>
                </div>
            </div>
        `;
        leftColumn.appendChild(ctrlDiv);

        // 绑定折叠点击 (默认折叠)
        const pTitle = document.getElementById('physics-title-bar');
        const pBody = document.getElementById('physics-controls-body');
        const pArrow = document.getElementById('physics-collapse-arrow');
        if (pTitle && pBody && pArrow) {
            pArrow.style.transform = 'rotate(-90deg)';
            pTitle.onclick = () => {
                const isCollapsed = pBody.classList.contains('collapsed');
                if (isCollapsed) {
                    pBody.classList.remove('collapsed');
                    pBody.classList.add('expanded');
                    pArrow.style.transform = 'rotate(0deg)';
                } else {
                    pBody.classList.remove('expanded');
                    pBody.classList.add('collapsed');
                    pArrow.style.transform = 'rotate(-90deg)';
                }
            };
        }
        setupPhysicsListeners();
    }
}

function setupSearchListeners() {
    const input = document.getElementById('galaxy-search-input');
    const suggs = document.getElementById('galaxy-search-suggestions');
    if (!input || !suggs) return;

    input.addEventListener('input', () => {
        const query = input.value.trim().toLowerCase();
        if (!query || !window.galaxyGraph) {
            suggs.style.display = 'none';
            return;
        }
        const nodes = window.galaxyGraph.graphData().nodes;
        const matches = nodes.filter(n => (n.title || '').toLowerCase().includes(query) || n.id.toLowerCase().includes(query)).slice(0, 8);
        if (matches.length === 0) {
            suggs.style.display = 'none';
            return;
        }
        suggs.innerHTML = matches.map(n => `
            <div class="galaxy-suggestion-item" data-id="${n.id}">
                🪐 ${n.title || n.id.split('/').pop()}
            </div>
        `).join('');
        suggs.style.display = 'flex';

        suggs.querySelectorAll('.galaxy-suggestion-item').forEach(el => {
            el.addEventListener('click', () => {
                const nodeId = el.getAttribute('data-id');
                const node = nodes.find(n => n.id === nodeId);
                if (node && typeof focusNodeIn3D === 'function') {
                    focusNodeIn3D(node);
                    if (typeof window.showNodeDirector === 'function') {
                        window.showNodeDirector(node);
                    }
                }
                input.value = '';
                suggs.style.display = 'none';
            });
        });
    });

    document.addEventListener('click', (e) => {
        const container = document.getElementById('galaxy-search-container');
        if (container && !container.contains(e.target)) {
            suggs.style.display = 'none';
        }
    });
}

function setupPhysicsListeners() {
    const distSlider = document.getElementById('gravity-distance-slider');
    const strengthSlider = document.getElementById('charge-strength-slider');
    const wikiCheck = document.getElementById('toggle-wikilinks');
    const semanticCheck = document.getElementById('toggle-semantic-links');

    const updatePhysics = () => {
        if (!window.galaxyGraph) return;
        const dist = parseInt(distSlider.value);
        const strength = parseInt(strengthSlider.value);
        const chargeForce = window.galaxyGraph.d3Force('charge');
        if (chargeForce) chargeForce.strength(strength);
        const linkForce = window.galaxyGraph.d3Force('link');
        if (linkForce) linkForce.distance(dist);
        
        window._showWikilinks = wikiCheck.checked;
        window._showSemanticLinks = semanticCheck.checked;

        if (window.galaxyGraph.d3Alpha) window.galaxyGraph.d3Alpha(0.2);
        window.galaxyGraph.nodeRelSize(window.galaxyGraph.nodeRelSize());
        window.galaxyGraph.linkColor(window.galaxyGraph.linkColor());
    };

    if (distSlider) distSlider.addEventListener('input', updatePhysics);
    if (strengthSlider) strengthSlider.addEventListener('input', updatePhysics);
    if (wikiCheck) wikiCheck.addEventListener('change', updatePhysics);
    if (semanticCheck) semanticCheck.addEventListener('change', updatePhysics);
}
