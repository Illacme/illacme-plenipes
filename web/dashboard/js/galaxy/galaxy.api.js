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
        label.style.color = 'var(--neon-cyan, #00f2ff)';
    }
    if (card) {
        card.style.background = 'hsla(183, 100%, 50%, 0.05)';
        card.style.borderColor = 'hsla(183, 100%, 50%, 0.2)';
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
        if (skeleton.nodes.length === 1) {
            // 🌟 创世星球 (Genesis Star) 特写视域：平滑飞向 (0, 0, 180) 居中观察
            skeleton.nodes[0].x = 0;
            skeleton.nodes[0].y = 0;
            skeleton.nodes[0].z = 0;
            if (typeof window.galaxyGraph.cameraPosition === 'function') {
                window.galaxyGraph.cameraPosition({ x: 0, y: 0, z: 180 }, { x: 0, y: 0, z: 0 }, 1200);
            }
        } else {
            window.galaxyGraph.zoomToFit(1200, 60);
        }

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
    } else {
        // 🌌 0 节点空态处理：清空旧数据并同步 HUD 指标
        window.galaxyGraph.graphData({ nodes: [], links: [] });
        window._lastGalaxyData = { nodes: [], links: [] };
        if (typeof window.updateGalaxyHUD === 'function') {
            window.updateGalaxyHUD([], []);
        }
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

        // 合并新节点 (保持原有对象的物理引用，防止坐标重置)
        const mergedNodesMap = {};
        currentData.nodes.forEach(n => { mergedNodesMap[n.id] = n; });
        const spread = Math.max(100, full.nodes.length * 10);
        full.nodes.forEach(n => {
            if (!mergedNodesMap[n.id]) {
                hasNewData = true;
                // 给新节点赋初值，防止它们全部在原点 (0,0,0) 发生“超新星爆炸”导致视觉上的“二次拉近”
                n.x = (Math.random() - 0.5) * spread;
                n.y = (Math.random() - 0.5) * spread;
                n.z = (Math.random() - 0.5) * spread;
                mergedNodesMap[n.id] = n; // 新节点
            } else {
                if (mergedNodesMap[n.id].title !== n.title) {
                    hasNewData = true;
                }
                // 直接向现有对象注入新属性，绝不破坏现有的 x, y, z 等物理引擎状态
                Object.assign(mergedNodesMap[n.id], n);
            }
        });

        // 合并新连线
        const mergedLinksMap = {};
        currentData.links.forEach(l => {
            const src = l.source?.id || l.source;
            const tgt = l.target?.id || l.target;
            const key = [src, tgt].sort().join('⇄');
            mergedLinksMap[key] = l; // 保持原有引用
        });
        full.links.forEach(l => {
            const src = l.source?.id || l.source;
            const tgt = l.target?.id || l.target;
            const key = [src, tgt].sort().join('⇄');
            if (!mergedLinksMap[key]) {
                hasNewData = true;
                mergedLinksMap[key] = l; // 新连线
            } else {
                // 向现有连线对象注入新属性，务必排除 source 和 target！
                // 因为 ForceGraph 已经在内部将 source/target 从字符串 ID 转换成了真正的节点对象引用
                // 如果用后端的字符串强行覆盖，会导致引擎报错 "Cannot create property 'vx' on string"
                const { source, target, ...rest } = l;
                Object.assign(mergedLinksMap[key], rest);
            }
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

            // 🌌 增量加载完成后，仅给引力引擎注入极低的“微热量”（0.1）
            // 让新连线像橡皮筋一样“轻柔地”将节点拉入最终位置，避免已经静止的第一阶段节点再次剧烈抖动
            if (typeof window.galaxyGraph.d3Alpha === 'function') {
                window.galaxyGraph.d3Alpha(0.1);
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
