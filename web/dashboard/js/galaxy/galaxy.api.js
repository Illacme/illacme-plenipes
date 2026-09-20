/**
 * 🚀 Illacme Plenipes 3D Galaxy Engine - Network & API Merge Module
 * 职责：实现双阶段渐进刷新（骨架秒亮 + 延迟语义增量温和合并）。
 * 符合 SOP-02 模块拆分协议，行数严格控制在 300 行内。
 */

// 🌌 共享的全局星系数据备份 (用于隔离星球模式与全量模式切换)
window._lastGalaxyData = null;

// 🪐 数据动态刷新与高维自然舒展加载
window.refreshGalaxy = async () => {
    if (!window.galaxyGraph || typeof apiFetch !== 'function') return;

    window._filterConnectedOnly = false;
    const label = document.getElementById('focus-btn-label');
    const card = document.getElementById('btn-focus-connected');
    if (label) {
        label.innerText = '⚡ 隔离星球';
        label.style.color = '';
    }
    if (card) {
        card.classList.remove('active-isolated');
        card.style.background = '';
        card.style.borderColor = '';
    }

    // 🌌 直接获取包含物理双链与语义关联的全量知识星谱，彻底消除两阶段跳变与突兀收缩
    const graphData = await apiFetch('/api/galaxy/graph?mode=full');
    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
        window.galaxyGraph.graphData({ nodes: [], links: [] });
        window._lastGalaxyData = { nodes: [], links: [] };
        if (typeof window.updateGalaxyHUD === 'function') {
            window.updateGalaxyHUD([], []);
        }
        return;
    }

    // 🛡️ 过滤幽灵链路：移除指向不存在节点的连线，防止将节点无脑拉向原点 (0,0,0)
    const nodeIds = new Set(graphData.nodes.map(n => n.id));
    graphData.links = (graphData.links || []).filter(l => {
        const src = l.source?.id || l.source;
        const tgt = l.target?.id || l.target;
        return nodeIds.has(src) && nodeIds.has(tgt);
    });

    // 🌟 [V130.0] 预计算节点连接度 — 用于多色彩映射与动态尺寸分级
    const linkCountMap = {};
    graphData.links.forEach(l => {
        const src = l.source?.id || l.source;
        const tgt = l.target?.id || l.target;
        linkCountMap[src] = (linkCountMap[src] || 0) + 1;
        linkCountMap[tgt] = (linkCountMap[tgt] || 0) + 1;
    });
    graphData.nodes.forEach(n => { n._linkCount = linkCountMap[n.id] || 0; });

    // 🌌 预分配球形三维温和散布坐标，使力学引擎如宇宙膨胀般自然绽放
    const spread = Math.max(140, Math.sqrt(graphData.nodes.length) * 48);
    graphData.nodes.forEach(n => {
        if (n.x === undefined) {
            const u = Math.random();
            const v = Math.random();
            const theta = u * 2.0 * Math.PI;
            const phi = Math.acos(2.0 * v - 1.0);
            const r = Math.cbrt(Math.random()) * spread;
            n.x = r * Math.sin(phi) * Math.cos(theta);
            n.y = r * Math.sin(phi) * Math.sin(theta);
            n.z = r * Math.cos(phi);
        }
    });

    // 🎛️ 自适应品质与解耦力学加载
    if (typeof window.applyScaleAdaptation === 'function') {
        window.applyScaleAdaptation(graphData.nodes.length);
    }

    // 注入充足模拟周期使星系优雅绽开定型
    window.galaxyGraph.cooldownTicks(200);
    window.galaxyGraph.graphData(graphData);
    window._lastGalaxyData = graphData;

    // 动态更新 HUD 指标
    if (typeof window.updateGalaxyHUD === 'function') {
        window.updateGalaxyHUD(graphData.nodes, graphData.links);
    }

    // 🌌 自动计算最佳观察视域
    if (graphData.nodes.length === 1) {
        graphData.nodes[0].x = 0; graphData.nodes[0].y = 0; graphData.nodes[0].z = 0;
        if (typeof window.galaxyGraph.cameraPosition === 'function') {
            window.galaxyGraph.cameraPosition({ x: 0, y: 0, z: 180 }, { x: 0, y: 0, z: 0 }, 1200);
        }
    } else {
        window.galaxyGraph.zoomToFit(1400, 70);
    }

    if (typeof window.galaxyGraph.d3Reheat === 'function') {
        window.galaxyGraph.d3Reheat();
    } else if (typeof window.galaxyGraph.d3ReheatLayout === 'function') {
        window.galaxyGraph.d3ReheatLayout();
    }

    // 同步标签图层与导向面板
    if (typeof window.updateGalaxyLabelElements === 'function') {
        window.updateGalaxyLabelElements(graphData.nodes);
    }
    if (typeof window.renderConnectionsList === 'function' && window._currentNode) {
        window.renderConnectionsList(window._currentNode);
    }
    console.log(`🌌 [Galaxy] 知识星谱全息图载入完成: ${graphData.nodes.length} 节点, ${graphData.links.length} 连线，力学引擎自然舒展中`);
};
