/**
 * 🚀 Illacme Plenipes Dashboard 3D Galaxy Engine
 * 职责：初始化 ForceGraph3D、定时刷新物理图谱网络，Obsidian 标签洗白及相机 2D 坐标轴深度映射。
 * 🪐 [Phase 3] LOD 视锥裁剪 + 万级节点性能优化
 */

// ═══════════════════════════════════════════════════
// 🎛️ [Phase 3] 全局性能调控参数 (Performance Tuning)
// ═══════════════════════════════════════════════════
const GALAXY_PERF = {
    // LOD 分层阈值 (相机到节点的距离)
    LOD_NEAR: 300,           // 近景：显示完整标签 + 高精度球体
    LOD_MID: 600,            // 中景：显示缩小标签
    LOD_FAR: 1000,           // 远景：隐藏标签，仅保留光点
    // 视锥裁剪边界 (屏幕坐标超出此像素范围则剪裁)
    FRUSTUM_MARGIN: 80,      // 屏幕外 80px 容差 (防止边缘闪烁)
    // 节流控制
    SYNC_THROTTLE_MS: 33,    // 标签同步节流间隔 (~30fps)
    // 大规模自适应
    SCALE_THRESHOLD_MED: 500,   // 中等规模：降低球体精度
    SCALE_THRESHOLD_LARGE: 2000, // 大规模：关闭粒子特效
    SCALE_THRESHOLD_HUGE: 5000,  // 超大规模：关闭标签、极简渲染
    // 标签虚拟化
    MAX_VISIBLE_LABELS: 200, // 同一时刻最多渲染的标签 DOM 数量
};

// 1. 3D 宇宙引擎 (Sovereign Refinement)
window.initGalaxy = () => {
    const elem = document.getElementById('galaxy-3d');
    if (!elem || typeof ForceGraph3D === 'undefined') return;

    if (window.galaxyGraph) return;

    window.galaxyGraph = ForceGraph3D()(elem)
        .width(elem.clientWidth)
        .height(elem.clientHeight)
        .backgroundColor('rgba(0,0,0,0)')
        .nodeColor(node => node.group === 'imprint' ? '#a34cff' : '#00f2ff')
        .nodeResolution(24)
        .nodeRelSize(5)
        .linkColor(() => 'rgba(0, 242, 255, 0.15)')
        .linkWidth(0.8)
        .showNavInfo(false)
        .linkDirectionalParticles(2)
        .linkDirectionalParticleWidth(1.2)
        .linkDirectionalParticleSpeed(0.006)
        .onNodeClick(node => {
            if (node.id && typeof openEditor === 'function') {
                const cleanId = node.id.replace('doc_', '');
                openEditor(cleanId);
            }
        })
        .onEngineTick(() => {
            // 🏷️ [Phase 3] 节流同步标签 — 避免每帧都触发 DOM 回流
            if (typeof window._throttledSyncLabels === 'function') {
                window._throttledSyncLabels();
            }
        });

    // 🌌 配置 d3 排斥力与连线力，确保节点充分散开
    const chargeForce = window.galaxyGraph.d3Force('charge');
    if (chargeForce) chargeForce.strength(-120);
    const linkForce = window.galaxyGraph.d3Force('link');
    if (linkForce) linkForce.distance(80).strength(0.4);

    // 🌪️ [V86.0] Kinetic Upgrade: Native Auto-Rotate
    window.galaxyGraph.controls().autoRotate = true;
    window.galaxyGraph.controls().autoRotateSpeed = 0.5;

    // 🔗 [Phase 3] 相机控制器的 change 事件 → 使用节流同步
    window.galaxyGraph.controls().addEventListener('change', () => {
        if (typeof window._throttledSyncLabels === 'function') {
            window._throttledSyncLabels();
        }
    });

    // 🧪 [Phase 3] Neural Pulse: 大规模时自动降频呼吸 + 标签持续同步
    let angle = 0;
    setInterval(() => {
        if (window.galaxyGraph) {
            const nodeCount = window.galaxyGraph.graphData().nodes.length;
            // 超大规模时禁用呼吸效应，避免反复触发 WebGL 重绘
            if (nodeCount > GALAXY_PERF.SCALE_THRESHOLD_HUGE) return;
            angle += 0.05;
            const pulse = 4.5 + Math.sin(angle) * 0.8;
            window.galaxyGraph.nodeRelSize(pulse);
            // 🏷️ 持续同步标签位置 (兜底机制，确保力学引擎停止后标签仍更新)
            if (typeof window.syncGalaxyLabels === 'function') {
                window.syncGalaxyLabels();
            }
        }
    }, 100);

    if (typeof window.refreshGalaxy === 'function') {
        window.refreshGalaxy();
    }

    // 📏 [Phase 3] 响应式监听 + 容器尺寸缓存
    window._galaxyWidth = elem.clientWidth;
    window._galaxyHeight = elem.clientHeight;
    const resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
            if (window.galaxyGraph) {
                const { width, height } = entry.contentRect;
                window._galaxyWidth = width;
                window._galaxyHeight = height;
                window.galaxyGraph.width(width);
                window.galaxyGraph.height(height);
            }
        }
    });
    resizeObserver.observe(elem);

    // 🎛️ [Phase 3] 构建节流标签同步器
    window._lastSyncTime = 0;
    window._throttledSyncLabels = () => {
        const now = performance.now();
        if (now - window._lastSyncTime < GALAXY_PERF.SYNC_THROTTLE_MS) return;
        window._lastSyncTime = now;
        if (typeof window.syncGalaxyLabels === 'function') {
            window.syncGalaxyLabels();
        }
    };
};

// 2. 🪐 [混合渐进式] 数据动态刷新 (两阶段渐进加载)
window.refreshGalaxy = async () => {
    if (!window.galaxyGraph || typeof apiFetch !== 'function') return;

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
        window.galaxyGraph.d3Reheat();

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
            window.galaxyGraph.cooldownTicks(60);
            window.galaxyGraph.d3Reheat();
            window.applyScaleAdaptation(mergedData.nodes.length);
            if (typeof window.updateGalaxyLabelElements === 'function') {
                window.updateGalaxyLabelElements(mergedData.nodes);
            }
            console.log(`🚀 [Phase 2] 全量增量合并完成: ${mergedData.nodes.length} 节点, ${mergedData.links.length} 连线`);
        } else {
            console.log('✅ [Phase 2] 全量图谱与骨架一致，无需增量合并');
        }
    }, 2000);
};

// ═══════════════════════════════════════════════════
// 3. 🏷️ [Phase 3] LOD 智能标签引擎 (虚拟化 + 视锥裁剪)
// ═══════════════════════════════════════════════════

// 🎛️ 标签 DOM 缓存池 (避免万级节点时全量创建 DOM)
window._labelPool = new Map(); // id -> DOM element
window._labelDataMap = new Map(); // id -> { title }

window.updateGalaxyLabelElements = (nodes) => {
    // 📝 先填充数据映射表 (不依赖 DOM 容器是否就绪)
    const newIds = new Set();
    nodes.forEach(node => {
        const rawTitle = node.title || node.id;
        const cleanTitle = rawTitle.split('/').pop().replace(/\.[^/.]+$/, '');
        window._labelDataMap.set(node.id, { title: cleanTitle });
        newIds.add(node.id);
    });

    // 清理已移除节点的 DOM 和数据
    for (const [id, el] of window._labelPool) {
        if (!newIds.has(id)) {
            el.remove();
            window._labelPool.delete(id);
            window._labelDataMap.delete(id);
        }
    }
};

// 🏷️ 按需获取或创建标签 DOM (虚拟化核心)
function _getOrCreateLabel(id, container) {
    let el = window._labelPool.get(id);
    if (!el) {
        const data = window._labelDataMap.get(id);
        if (!data) return null;
        el = document.createElement('div');
        el.className = 'tactical-node-label';
        el.id = `label-${id}`;
        el.innerText = data.title;
        el.style.position = 'absolute';
        el.style.transform = 'translate(-50%, 15px)';
        el.style.pointerEvents = 'none';
        el.style.willChange = 'transform, opacity'; // GPU 层提升
        container.appendChild(el);
        window._labelPool.set(id, el);
    }
    return el;
}

// ═══════════════════════════════════════════════════
// 4. 🔭 [Phase 3] LOD 视锥裁剪 + 深度分层标签同步引擎
// ═══════════════════════════════════════════════════
window.syncGalaxyLabels = () => {
    const container = document.getElementById('galaxy-labels-layer');
    const graph = window.galaxyGraph;
    if (!container || !graph) return;

    const nodes = graph.graphData().nodes;
    const totalNodes = nodes.length;
    if (totalNodes === 0) return;

    // 🎛️ 超大规模时跳过全部标签渲染
    if (totalNodes > GALAXY_PERF.SCALE_THRESHOLD_HUGE) {
        container.style.display = 'none';
        return;
    } else {
        container.style.display = '';
    }

    const camera = graph.camera();
    const camPos = camera.position;

    // 🛡️ 提取相机前向向量 (Forward Vector) 用于背面裁剪
    const matrix = camera.matrixWorld.elements;
    const camDirX = -matrix[8], camDirY = -matrix[9], camDirZ = -matrix[10];

    // 📐 获取标签容器相对于视口的物理偏移，用于精细校准局部坐标
    const containerRect = container.getBoundingClientRect();

    // 📐 屏幕边界 (含容差)
    const W = window._galaxyWidth || 800;
    const H = window._galaxyHeight || 600;
    const margin = GALAXY_PERF.FRUSTUM_MARGIN;

    // 🏎️ 第一遍：快速计算每个节点的距离与可见性 (纯数学，零 DOM 操作)
    const scored = [];
    for (let i = 0; i < totalNodes; i++) {
        const node = nodes[i];
        if (node.x === undefined) continue;

        const dx = node.x - camPos.x;
        const dy = node.y - camPos.y;
        const dz = node.z - camPos.z;

        // 1) 后方裁剪 (Back-face Culling)，防止背面节点标签穿透
        const dot = dx * camDirX + dy * camDirY + dz * camDirZ;
        if (dot <= 0) continue;

        // 2) 距离计算
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

        // 3) LOD 远景裁剪
        if (dist > GALAXY_PERF.LOD_FAR) continue;

        // 4) 屏幕坐标投影
        const pos = graph.graph2ScreenCoords(node.x, node.y, node.z);
        if (!pos) continue;

        // 📐 计算相对于局部容器的精准坐标
        const relativeX = pos.x - containerRect.left;
        const relativeY = pos.y - containerRect.top;

        // 5) 视锥裁剪：只剔除完全在容器局部画布外的标签
        if (relativeX < -margin || relativeX > W + margin || relativeY < -margin || relativeY > H + margin) continue;

        scored.push({ node, dist, relativeX, relativeY });
    }

    // 🏎️ 按距离排序，只取最近的 MAX_VISIBLE_LABELS 个，保障超大规模下 DOM 性能守恒
    scored.sort((a, b) => a.dist - b.dist);
    const visibleSet = new Set();
    const maxLabels = Math.min(scored.length, GALAXY_PERF.MAX_VISIBLE_LABELS);

    // 🏎️ 第二遍：仅对通过筛选的胜出节点执行 DOM 操作
    for (let i = 0; i < maxLabels; i++) {
        const { node, dist, relativeX, relativeY } = scored[i];
        visibleSet.add(node.id);

        const el = _getOrCreateLabel(node.id, container);
        if (!el) continue;

        // LOD 分层字号与不透明度计算，实现 Obsidian 式极客呼吸渐变
        let fontSize, opacity;
        if (dist < GALAXY_PERF.LOD_NEAR) {
            fontSize = Math.max(10, 16 - dist / 100);
            opacity = 1;
        } else if (dist < GALAXY_PERF.LOD_MID) {
            const t = (dist - GALAXY_PERF.LOD_NEAR) / (GALAXY_PERF.LOD_MID - GALAXY_PERF.LOD_NEAR);
            fontSize = Math.max(8, 14 - t * 6);
            opacity = Math.max(0.4, 1 - t * 0.6);
        } else {
            const t = (dist - GALAXY_PERF.LOD_MID) / (GALAXY_PERF.LOD_FAR - GALAXY_PERF.LOD_MID);
            fontSize = Math.max(6, 8 - t * 2);
            opacity = Math.max(0.15, 0.4 - t * 0.25);
        }

        el.style.display = 'block';
        el.style.left = `${relativeX}px`;
        el.style.top = `${relativeY}px`;
        el.style.fontSize = `${fontSize}px`;
        el.style.opacity = opacity;
    }

    // 🧹 隐藏不可见的标签
    for (const [id, el] of window._labelPool) {
        if (!visibleSet.has(id)) {
            el.style.display = 'none';
        }
    }
};

// ═══════════════════════════════════════════════════
// 5. 🎛️ [Phase 3] 大规模自适应渲染降级器
// ═══════════════════════════════════════════════════
window.applyScaleAdaptation = (nodeCount) => {
    if (!window.galaxyGraph) return;
    if (nodeCount > GALAXY_PERF.SCALE_THRESHOLD_HUGE) {
        // 超大规模 (>5000)：极简模式
        window.galaxyGraph.nodeResolution(6);
        window.galaxyGraph.linkDirectionalParticles(0);
        window.galaxyGraph.linkWidth(0.3);
        window.galaxyGraph.nodeRelSize(2.5);
        console.log(`🎛️ [LOD] 超大规模降级: ${nodeCount} 节点 → 极简模式`);
    } else if (nodeCount > GALAXY_PERF.SCALE_THRESHOLD_LARGE) {
        // 大规模 (>2000)：关闭粒子
        window.galaxyGraph.nodeResolution(8);
        window.galaxyGraph.linkDirectionalParticles(0);
        window.galaxyGraph.linkWidth(0.5);
        window.galaxyGraph.nodeRelSize(3.5);
        console.log(`🎛️ [LOD] 大规模降级: ${nodeCount} 节点 → 无粒子模式`);
    } else if (nodeCount > GALAXY_PERF.SCALE_THRESHOLD_MED) {
        // 中等规模 (>500)：降低球体精度
        window.galaxyGraph.nodeResolution(12);
        window.galaxyGraph.linkDirectionalParticles(1);
        window.galaxyGraph.linkWidth(0.6);
        window.galaxyGraph.nodeRelSize(4);
        console.log(`🎛️ [LOD] 中等规模降级: ${nodeCount} 节点 → 低精度模式`);
    } else {
        // 小规模：全品质
        window.galaxyGraph.nodeResolution(24);
        window.galaxyGraph.linkDirectionalParticles(2);
        window.galaxyGraph.linkWidth(0.8);
        window.galaxyGraph.nodeRelSize(5);
    }
};
