/**
 * 🚀 Illacme Plenipes 3D Galaxy Engine - HUD & Node Isolator Module
 * 职责：计算动态拓扑密度 HUD，并提供孤立星球网络物理过滤与隔离控制。
 * 符合 SOP-02 模块拆分协议，行数严格控制 in 300 行内。
 */

// 🌌 动态绑定 HUD 知识关联指标
window.updateGalaxyHUD = (nodes, links) => {
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

// ⚡ 隔离孤立节点交互逻辑 (Isolate Isolated Planets)
window._filterConnectedOnly = false;
window.toggleConnectedNodesOnly = () => {
    if (!window.galaxyGraph || !window._lastGalaxyData) {
        console.warn("🌌 [LOD] 图谱数据尚未完全就绪，无法执行隔离");
        return;
    }
    window._filterConnectedOnly = !window._filterConnectedOnly;
    
    const label = document.getElementById('focus-btn-label');
    const card = document.getElementById('btn-focus-connected');
    
    if (window._filterConnectedOnly) {
        // Find connected node IDs
        const connectedNodeIds = new Set();
        window._lastGalaxyData.links.forEach(l => {
            const src = l.source?.id || l.source;
            const tgt = l.target?.id || l.target;
            if (src !== undefined && tgt !== undefined) {
                connectedNodeIds.add(src);
                connectedNodeIds.add(tgt);
            }
        });
        
        const filteredNodes = window._lastGalaxyData.nodes.filter(n => connectedNodeIds.has(n.id));
        const filteredLinks = window._lastGalaxyData.links;
        
        window.galaxyGraph.graphData({
            nodes: filteredNodes,
            links: filteredLinks
        });
        
        if (label) {
            label.innerText = '🪐 显示全部星球';
            label.style.color = '#ff9f43';
        }
        if (card) {
            card.style.background = 'rgba(255, 159, 67, 0.08)';
            card.style.borderColor = 'rgba(255, 159, 67, 0.3)';
        }
        
        // Let it scatter, then frame it nicely
        setTimeout(() => {
            if (window.galaxyGraph) {
                window.galaxyGraph.zoomToFit(1000, 80);
            }
        }, 150);
        
        if (typeof window.updateGalaxyLabelElements === 'function') {
            window.updateGalaxyLabelElements(filteredNodes);
        }
        console.log(`⚡ [HUD] 隔离孤立星球完成，保留 ${filteredNodes.length} / ${window._lastGalaxyData.nodes.length} 个有连接节点`);
    } else {
        // Restore full data
        window.galaxyGraph.graphData(window._lastGalaxyData);
        
        if (label) {
            label.innerText = '⚡ 隔离孤立星球';
            label.style.color = '#00f2ff';
        }
        if (card) {
            card.style.background = 'rgba(0, 242, 255, 0.05)';
            card.style.borderColor = 'rgba(0, 242, 255, 0.2)';
        }
        
        setTimeout(() => {
            if (window.galaxyGraph) {
                window.galaxyGraph.zoomToFit(1000, 80);
            }
        }, 150);
        
        if (typeof window.updateGalaxyLabelElements === 'function') {
            window.updateGalaxyLabelElements(window._lastGalaxyData.nodes);
        }
        console.log(`🪐 [HUD] 还原全量星球，展现 ${window._lastGalaxyData.nodes.length} 个星球`);
    }
};
