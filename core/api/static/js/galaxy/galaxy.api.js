/**
 * 🚀 Illacme Plenipes 3D Galaxy Engine - Network & API Merge Module
 * 职责：实现双阶段渐进刷新（骨架秒亮 + 延迟语义增量温和合并）。
 * 符合 SOP-02 模块拆分协议，行数严格控制在 300 行内。
 */

// 🌌 共享的全局星系数据备份 (用于隔离星球模式与全量模式切换)
window._lastGalaxyData = null;

// 🪐 [混合渐进式] 数据动态刷新 (两阶段渐进加载)
window.refreshGalaxy = async () => {
    if (!window.galaxyGraph || typeof apiFetch !== 'function') return;

    window._filterConnectedOnly = false;
    const label = document.getElementById('focus-btn-label');
    const card = document.getElementById('btn-focus-connected');
    if (label) {
        label.innerText = '⚡ 隔离孤立星球';
        label.style.color = '#00f2ff';
    }
    if (card) {
        card.style.background = 'rgba(0, 242, 255, 0.05)';
        card.style.borderColor = 'rgba(0, 242, 255, 0.2)';
    }

    // ──── Phase 1: 骨架秒亮 (Skeleton Instant Render) ────
    // 先拉取轻量物理 WikiLinks 骨架，预分配随机坐标后让力学引擎散射
    const skeleton = await apiFetch('/api/galaxy/graph?mode=skeleton');
    if (skeleton && skeleton.nodes && skeleton.nodes.length > 0) {
        // 🛡️ 过滤幽灵链路：移除指向不存在节点的连线
        // ForceGraph3D 会为不存在的 target 创建隐形幽灵节点在原点 (0,0,0)，
        // 导致连线力把所有真实节点拉向原点，造成全部堆叠为一颗星球
        const nodeIds = new Set(skeleton.nodes.map(n => n.id));
        skeleton.links = (skeleton.links || []).filter(l => {
            const src = l.source?.id || l.source;
            const tgt = l.target?.id || l.target;
            return nodeIds.has(src) && nodeIds.has(tgt);
        });

        // 🌌 预分配随机初始位置，防止所有节点堆叠在原点
        const spread = Math.max(100, skeleton.nodes.length * 10);
        skeleton.nodes.forEach(n => {
            if (n.x === undefined) n.x = (Math.random() - 0.5) * spread;
            if (n.y === undefined) n.y = (Math.random() - 0.5) * spread;
            if (n.z === undefined) n.z = (Math.random() - 0.5) * spread;
        });

        // 允许力学引擎运行足够的模拟周期来散开节点
        window.galaxyGraph.cooldownTicks(150);
        window.galaxyGraph.graphData(skeleton);
        window._lastGalaxyData = skeleton;
        
        // 动态更新 HUD 指标
        if (typeof window.updateGalaxyHUD === 'function') {
            window.updateGalaxyHUD(skeleton.nodes, skeleton.links);
        }
        
        // 🌌 自动计算视域，将骨架星群以 1.2s 缓动完美框进屏幕
        window.galaxyGraph.zoomToFit(1200, 60);

        if (typeof window.galaxyGraph.d3Reheat === 'function') {
            window.galaxyGraph.d3Reheat();
        } else if (typeof window.galaxyGraph.d3ReheatLayout === 'function') {
            window.galaxyGraph.d3ReheatLayout();
        } else if (typeof window.galaxyGraph.refresh === 'function') {
            window.galaxyGraph.refresh();
        }

        // 初始化标签 DOM
        if (typeof window.updateGalaxyLabelElements === 'function') {
            window.updateGalaxyLabelElements(skeleton.nodes);
        }
        console.log(`🌌 [Phase 1] 骨架渲染完成: ${skeleton.nodes.length} 节点, ${skeleton.links.length} 有效连线, 力学引擎运行中`);
    }

    // ──── Phase 2: 全量增量合并 (Full Incremental Merge) ────
    // 异步拉取包含 AI 语义连线的完整图谱，增量合并后温和弹射
    setTimeout(async () => {
        const full = await apiFetch('/api/galaxy/graph?mode=full');
        if (!full || !full.nodes) return;

        // 检测是否有增量（新节点或新连线）
        if (!window.galaxyGraph) return;
        const currentData = window.galaxyGraph.graphData();
        const currentNodeIds = new Set(currentData.nodes.map(n => n.id));
        const currentLinkIds = new Set(currentData.links.map(l =>
            [l.source?.id || l.source, l.target?.id || l.target].sort().join('⇄')
        ));

        let hasNewData = false;

        // 合并新节点
        const mergedNodesMap = {};
        currentData.nodes.forEach(n => { mergedNodesMap[n.id] = { ...n }; });
        full.nodes.forEach(n => {
            if (!mergedNodesMap[n.id]) {
                hasNewData = true;
            } else if (mergedNodesMap[n.id].title !== n.title) {
                // 🚀 [V100.0] 标题增量侦测：如果节点名称被修改，强行将其视为有增量更新以刷新标签 DOM 缓存
                hasNewData = true;
            }
            mergedNodesMap[n.id] = { ...mergedNodesMap[n.id], ...n };
        });

        // 合并新连线
        const mergedLinksMap = {};
        currentData.links.forEach(l => {
            const src = l.source?.id || l.source;
            const tgt = l.target?.id || l.target;
            const key = [src, tgt].sort().join('⇄');
            mergedLinksMap[key] = { source: src, target: tgt, ...l };
        });
        full.links.forEach(l => {
            const src = l.source?.id || l.source;
            const tgt = l.target?.id || l.target;
            const key = [src, tgt].sort().join('⇄');
            if (!mergedLinksMap[key]) {
                hasNewData = true;
            }
            mergedLinksMap[key] = { source: src, target: tgt, ...l };
        });

        if (hasNewData) {
            // 🛡️ 过滤幽灵链路 (同 Phase 1 逻辑)
            const allNodeIds = new Set(Object.keys(mergedNodesMap));
            const validLinks = Object.values(mergedLinksMap).filter(l => {
                const src = l.source?.id || l.source;
                const tgt = l.target?.id || l.target;
                return allNodeIds.has(src) && allNodeIds.has(tgt);
            });

            const mergedData = {
                nodes: Object.values(mergedNodesMap),
                links: validLinks
            };
            window.galaxyGraph.graphData(mergedData);
            window._lastGalaxyData = mergedData;
            
            // 动态更新 HUD 指标
            if (typeof window.updateGalaxyHUD === 'function') {
                window.updateGalaxyHUD(mergedData.nodes, mergedData.links);
            }
            
            // 🌌 增量加载完成后，全量自适应视场对齐
            window.galaxyGraph.zoomToFit(1500, 80);

            window.galaxyGraph.cooldownTicks(60);
            if (typeof window.galaxyGraph.d3Reheat === 'function') {
                window.galaxyGraph.d3Reheat();
            } else if (typeof window.galaxyGraph.d3ReheatLayout === 'function') {
                window.galaxyGraph.d3ReheatLayout();
            } else if (typeof window.galaxyGraph.refresh === 'function') {
                window.galaxyGraph.refresh();
            }
            
            if (typeof window.applyScaleAdaptation === 'function') {
                window.applyScaleAdaptation(mergedData.nodes.length);
            }
            if (typeof window.updateGalaxyLabelElements === 'function') {
                window.updateGalaxyLabelElements(mergedData.nodes);
            }
            console.log(`🚀 [Phase 2] 全量增量合并完成: ${mergedData.nodes.length} 节点, ${mergedData.links.length} 连线`);
        } else {
            console.log('✅ [Phase 2] 全量图谱与骨架一致，无需增量合并');
            window._lastGalaxyData = {
                nodes: currentData.nodes,
                links: currentData.links
            };
        }
    }, 2000);
};
