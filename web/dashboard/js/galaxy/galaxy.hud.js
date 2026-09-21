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
    injectGalaxyInteractiveDOM();
    if (typeof window.injectGalaxyDirectorDOM === 'function') window.injectGalaxyDirectorDOM();

    const densityEl = document.getElementById('density-val'), nodeEl = document.getElementById('node-count'), connEl = document.getElementById('conn-count');
    const N = nodes ? nodes.length : 0, L = links ? links.length : 0;
    if (densityEl) densityEl.innerText = (N > 1 ? (2 * L) / (N * (N - 1)) : 0).toFixed(2);
    if (nodeEl) nodeEl.innerText = N;
    if (connEl) connEl.innerText = L;
};

// ⚡ 隔离孤立节点交互逻辑
window._filterConnectedOnly = false;
window.toggleConnectedNodesOnly = () => {
    if (!window.galaxyGraph || !window._lastGalaxyData) return;
    window._filterConnectedOnly = !window._filterConnectedOnly;
    const label = document.getElementById('focus-btn-label'), card = document.getElementById('btn-focus-connected');
    const newTitle = window._filterConnectedOnly
        ? '一键恢复显示所有星球，包含无任何连线的孤立知识点。'
        : '一键过滤并隐藏所有无连线的孤立星球，聚焦展示有关联的知识网络。';

    if (card) card.hasAttribute('data-tooltip') ? card.setAttribute('data-tooltip', newTitle) : card.setAttribute('title', newTitle);
    const activeTooltip = document.querySelector('.custom-glass-tooltip');
    if (activeTooltip) activeTooltip.innerText = newTitle;
    
    if (window._filterConnectedOnly) {
        const connIds = new Set();
        window._lastGalaxyData.links.forEach(l => {
            const src = l.source?.id || l.source, tgt = l.target?.id || l.target;
            if (src !== undefined && tgt !== undefined) { connIds.add(src); connIds.add(tgt); }
        });
        const filteredNodes = window._lastGalaxyData.nodes.filter(n => connIds.has(n.id));
        window.galaxyGraph.graphData({ nodes: filteredNodes, links: window._lastGalaxyData.links });
        if (label) { label.innerText = '🪐 显示全部'; label.style.color = ''; }
        if (card) { card.classList.add('active-isolated'); card.style.background = ''; card.style.borderColor = ''; }
    } else {
        window.galaxyGraph.graphData(window._lastGalaxyData);
        if (label) { label.innerText = '⚡ 隔离星球'; label.style.color = ''; }
        if (card) { card.classList.remove('active-isolated'); card.style.background = ''; card.style.borderColor = ''; }
    }
    setTimeout(() => window.galaxyGraph.zoomToFit(1000, 80), 150);
};

function injectGalaxyInteractiveDOM() {
    const leftColumn = document.getElementById('galaxy-hud-column');
    const rightColumn = document.getElementById('galaxy-right-column');
    if (!leftColumn || !rightColumn) return;

    // 1. 注入检索框至右侧控制列
    if (!document.getElementById('galaxy-search-container')) {
        const searchDiv = document.createElement('div');
        searchDiv.id = 'galaxy-search-container';
        searchDiv.style.cssText = 'display: flex; flex-direction: column; width: 100%; padding: 6px 10px; box-sizing: border-box; flex-shrink: 0; pointer-events: auto;';
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

    // 3. 注入数据指标组 (Stats Unified Card，内嵌横向扩展物理参数) 至左侧列
    if (!document.getElementById('galaxy-telemetry-container')) {
        const telDiv = document.createElement('div');
        telDiv.id = 'galaxy-telemetry-container';
        telDiv.className = 'hud-item glass-panel';
        telDiv.style.cssText = 'padding: 10px 14px; width: auto; border-radius: 12px; display: flex; flex-direction: row; min-width: 0; box-sizing: border-box; animation: none; margin-top: 0;';
        telDiv.innerHTML = `
            <!-- 指标主区域 -->
            <div id="telemetry-main-section" style="display: flex; flex-direction: column; justify-content: space-between; height: 99px; min-height: 99px; width: 180px; flex-shrink: 0; box-sizing: border-box;">
                <div id="telemetry-title-bar" style="display: flex; justify-content: space-between; align-items: center; user-select: none;">
                    <span style="font-size: 0.52rem; font-weight: 800; color: var(--text-dim); letter-spacing: 0.5px;">📊 实时指标</span>
                    <span id="telemetry-expand-btn" style="font-size: 0.65rem; color: var(--text-dim); transition: transform 0.3s ease; cursor: pointer; margin-right: -2px;" title="动力学参数调节">⚙️</span>
                </div>
                <div style="display: flex; flex-direction: column; justify-content: space-between; flex: 1; margin-top: 6px;">
                    <div style="display: flex; gap: 4px; align-items: center; justify-content: space-between; margin-top: 2px;">
                        <div style="flex: 1; text-align: center; cursor: help;" title="当前星图中所包含的活跃知识星球（已加载的笔记节点）总数。">
                            <div class="hud-label" style="font-size: 0.45rem; margin-bottom: 2px; letter-spacing: 0.5px;">神经元</div>
                            <div class="hud-value" id="node-count" style="font-size: 0.85rem; line-height: 1;">0</div>
                        </div>
                        <div style="flex: 1; text-align: center; border-left: 1px solid var(--glass-border); padding-left: 4px; cursor: help;" title="当前星图中所有星球之间的有效物理连线与 AI 语义引力链总数。">
                            <div class="hud-label" style="font-size: 0.45rem; margin-bottom: 2px; letter-spacing: 0.5px;">引力链</div>
                            <div class="hud-value" id="conn-count" style="font-size: 0.85rem; line-height: 1;">0</div>
                        </div>
                        <div style="flex: 1; text-align: center; border-left: 1px solid var(--glass-border); padding-left: 4px; cursor: help;" title="星图内星球之间连线的密集程度。数值越高，说明文献之间的交叉关联越紧密。">
                            <div class="hud-label" style="font-size: 0.45rem; margin-bottom: 2px; letter-spacing: 0.5px;">关联密度</div>
                            <div class="hud-value" id="density-val" style="font-size: 0.85rem; line-height: 1;">0.00</div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 6px; width: 100%;">
                        <button class="galaxy-hud-btn" id="btn-focus-connected" onclick="window.toggleConnectedNodesOnly()" title="一键过滤并隐藏所有无连线的孤立星球，聚焦展示有关联的知识网络。">
                            <span id="focus-btn-label">⚡ 隔离星球</span>
                        </button>
                        <button class="galaxy-hud-btn" id="btn-toggle-rotate" onclick="window.toggleGalaxyAutoRotate()" title="一键开启或暂停知识星系平滑轨道自转">
                            <span id="rotate-btn-label">🪐 开启自转</span>
                        </button>
                    </div>
                </div>
            </div>
            <!-- 物理调节子区域 (内嵌于同一个卡片中) -->
            <div id="galaxy-physics-controls" class="horizontal-collapsed">
                <div style="display: flex; flex-direction: column; gap: 5px; font-size: 0.6rem; color: var(--text-dim); width: 100%; box-sizing: border-box;">
                    <div style="display: flex; align-items: center; gap: 8px; width: 100%; cursor: help;" title="调节星球间连线的默认物理长度。数值越大，星球间距越宽；数值越小，星图越紧凑。">
                        <span style="flex-shrink: 0; min-width: 28px;">引力:</span>
                        <input type="range" id="gravity-distance-slider" min="30" max="200" value="80" style="flex: 1; min-width: 0; height: 2px; accent-color: var(--accent-secondary); cursor: pointer;" />
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; width: 100%; cursor: help;" title="调节星球之间的排斥力强度。排斥力越强，星团越发散，便于看清密集区域；越弱则越聚拢。">
                        <span style="flex-shrink: 0; min-width: 28px;">排斥:</span>
                        <input type="range" id="charge-strength-slider" min="-300" max="-20" value="-120" style="flex: 1; min-width: 0; height: 2px; accent-color: var(--accent-secondary); cursor: pointer;" />
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; width: 100%; cursor: help;" title="调节知识星谱平滑自转的角速度倍率 (0.2x ~ 3.0x)">
                        <span style="flex-shrink: 0; min-width: 28px;">转速:</span>
                        <input type="range" id="rotate-speed-slider" min="0.2" max="3.0" step="0.1" value="1.0" style="flex: 1; min-width: 0; height: 2px; accent-color: var(--accent-secondary); cursor: pointer;" />
                        <span id="rotate-speed-val" style="min-width: 24px; text-align: right; font-family: monospace; font-size: 0.52rem; color: var(--accent-secondary);">1.0x</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; width: 100%; cursor: help;" title="调节自转轨道的鸟瞰俯仰倾角 (0° ~ 60°，20° 为立体俯瞰视角)">
                        <span style="flex-shrink: 0; min-width: 28px;">倾角:</span>
                        <input type="range" id="rotate-incline-slider" min="0" max="60" step="1" value="20" style="flex: 1; min-width: 0; height: 2px; accent-color: var(--accent-secondary); cursor: pointer;" />
                        <span id="rotate-incline-val" style="min-width: 24px; text-align: right; font-family: monospace; font-size: 0.52rem; color: var(--accent-secondary);">20°</span>
                    </div>
                    <div style="display: flex; gap: 6px; margin-top: 2px; font-size: 0.5rem; justify-content: space-between; width: 100%; white-space: nowrap;">
                        <label style="display: flex; align-items: center; gap: 3px; cursor: help; white-space: nowrap;" title="显示或隐藏原稿笔记中手动书写的直接双向链接（[[WikiLinks]]，深青直线）">
                            <input type="checkbox" id="toggle-wikilinks" checked style="accent-color: var(--accent-secondary); cursor: pointer;" />
                            <span style="display: inline-block; width: 8px; height: 2px; background: var(--accent-secondary); border-radius: 1px; vertical-align: middle;"></span> 文档双链
                        </label>
                        <label style="display: flex; align-items: center; gap: 3px; cursor: help; white-space: nowrap;" title="显示或隐藏系统根据 AI 语义分析自动推荐的概念关联连线（柔性微弧线）">
                            <input type="checkbox" id="toggle-semantic-links" checked style="accent-color: var(--neon-purple); cursor: pointer;" />
                            <span style="display: inline-block; width: 8px; height: 2px; background: var(--neon-purple); border-radius: 50%; vertical-align: middle;"></span> 智能关联
                        </label>
                        <label style="display: flex; align-items: center; gap: 2px; cursor: help; white-space: nowrap;" title="开启后自转呈现太空滑行与周期回拉动效；关闭后呈现纯匀速平滑轨道巡航">
                            <input type="checkbox" id="toggle-rotation-damping" checked style="accent-color: var(--accent-secondary); cursor: pointer;" /> 旋转阻尼
                        </label>
                    </div>
                </div>
            </div>
        `;
        leftColumn.appendChild(telDiv);
        if (typeof window.updateGalaxyRotateUIState === 'function') {
            window.updateGalaxyRotateUIState(typeof window.isGalaxyAutoRotating === 'function' && window.isGalaxyAutoRotating());
        }

        // 绑定齿轮点击展开右侧物理面板
        const expandBtn = document.getElementById('telemetry-expand-btn');
        if (expandBtn) {
            expandBtn.onclick = (e) => {
                e.stopPropagation();
                const physCtrl = document.getElementById('galaxy-physics-controls');
                if (physCtrl) {
                    const isCollapsed = physCtrl.classList.contains('horizontal-collapsed');
                    physCtrl.classList.toggle('horizontal-collapsed', !isCollapsed);
                    physCtrl.classList.toggle('horizontal-expanded', isCollapsed);
                    expandBtn.style.transform = isCollapsed ? 'rotate(90deg)' : 'rotate(0deg)';
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
        suggs.innerHTML = matches.map(n => `<div class="galaxy-suggestion-item" data-id="${n.id}">🪐 ${n.title || n.id.split('/').pop()}</div>`).join('');
        suggs.style.display = 'flex';

        suggs.querySelectorAll('.galaxy-suggestion-item').forEach(el => {
            el.addEventListener('click', () => {
                const nodeId = el.getAttribute('data-id');
                const node = nodes.find(n => n.id === nodeId);
                if (node && typeof focusNodeIn3D === 'function') {
                    focusNodeIn3D(node);
                    if (typeof window.showNodeDirector === 'function') window.showNodeDirector(node);
                }
                input.value = '';
                suggs.style.display = 'none';
            });
        });
    });

    document.addEventListener('click', (e) => {
        const container = document.getElementById('galaxy-search-container');
        if (container && !container.contains(e.target)) suggs.style.display = 'none';
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

    const speedSlider = document.getElementById('rotate-speed-slider');
    const speedVal = document.getElementById('rotate-speed-val');
    if (speedSlider) {
        const curSpeed = typeof window.getGalaxyRotateSpeed === 'function' ? window.getGalaxyRotateSpeed() : 1.0;
        speedSlider.value = curSpeed.toFixed(1);
        if (speedVal) speedVal.innerText = `${curSpeed.toFixed(1)}x`;
        speedSlider.addEventListener('input', () => {
            const val = parseFloat(speedSlider.value) || 1.0;
            if (speedVal) speedVal.innerText = `${val.toFixed(1)}x`;
            if (typeof window.setGalaxyRotateSpeed === 'function') window.setGalaxyRotateSpeed(val);
        });
    }

    const inclineSlider = document.getElementById('rotate-incline-slider');
    const inclineVal = document.getElementById('rotate-incline-val');
    if (inclineSlider) {
        const curIncline = typeof window.getGalaxyOrbitIncline === 'function' ? window.getGalaxyOrbitIncline() : 20;
        inclineSlider.value = curIncline;
        if (inclineVal) inclineVal.innerText = `${curIncline}°`;
        inclineSlider.addEventListener('input', () => {
            const val = parseInt(inclineSlider.value) || 0;
            if (inclineVal) inclineVal.innerText = `${val}°`;
            if (typeof window.setGalaxyOrbitIncline === 'function') window.setGalaxyOrbitIncline(val);
        });
    }

    const dampingChk = document.getElementById('toggle-rotation-damping') || document.getElementById('toggle-anti-flip');
    if (dampingChk) {
        const curDamping = typeof window.getGalaxyRotationDamping === 'function' ? window.getGalaxyRotationDamping() : true;
        dampingChk.checked = curDamping;
        dampingChk.addEventListener('change', () => {
            if (typeof window.setGalaxyRotationDamping === 'function') window.setGalaxyRotationDamping(dampingChk.checked);
        });
    }
}

