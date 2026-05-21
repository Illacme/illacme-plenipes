/**
 * 🚀 Illacme Plenipes 3D Galaxy Engine - LOD Labels Module
 * 职责：LOD 智能标签池管理、相机背面/视锥裁剪与高频节流同步渲染引擎。
 * 符合 SOP-02 模块拆分协议，行数严格控制在 300 行内。
 */

// 🏷️ 标签 DOM 缓存池 (避免万级节点时全量创建 DOM)
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

// 🔭 [Phase 3] LOD 视锥裁剪 + 深度分层标签同步引擎
window.syncGalaxyLabels = () => {
    const container = document.getElementById('galaxy-labels-layer');
    const graph = window.galaxyGraph;
    if (!container || !graph) return;

    const nodes = graph.graphData().nodes;
    const totalNodes = nodes.length;
    if (totalNodes === 0) return;

    const perf = window.GALAXY_PERF || {
        LOD_NEAR: 300,
        LOD_MID: 600,
        LOD_FAR: 1000,
        FRUSTUM_MARGIN: 80,
        MAX_VISIBLE_LABELS: 200,
        SCALE_THRESHOLD_HUGE: 5000
    };

    // 🎛️ 超大规模时跳过全部标签渲染
    if (totalNodes > perf.SCALE_THRESHOLD_HUGE) {
        container.style.display = 'none';
        return;
    } else {
        container.style.display = '';
    }

    const camera = graph.camera();
    if (camera) {
        // 🛡️ [V86.5] 强制在投影计算前更新相机世界矩阵，杜绝交互拖拽时投影坐标滞后漂移
        camera.updateMatrixWorld();
    }
    const camPos = camera.position;

    // 🛡️ 提取相机前向向量 (Forward Vector) 用于背面裁剪
    const matrix = camera.matrixWorld.elements;
    const camDirX = -matrix[8], camDirY = -matrix[9], camDirZ = -matrix[10];

    // 📐 屏幕边界 (含容差)
    const W = window._galaxyWidth || 800;
    const H = window._galaxyHeight || 600;
    const margin = perf.FRUSTUM_MARGIN;

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

        // 🧠 [V86.7] 特赦判定：被 Hover 的节点即使再远，也强行豁免 LOD 远景裁剪，确保雷达显影
        const isHovered = window._hoveredNode && node.id === window._hoveredNode.id;

        // 3) LOD 远景裁剪
        if (!isHovered && dist > perf.LOD_FAR) continue;

        // 4) 屏幕坐标投影
        const pos = graph.graph2ScreenCoords(node.x, node.y, node.z);
        if (!pos) continue;

        const relativeX = pos.x;
        const relativeY = pos.y;

        // 5) 视锥裁剪：只剔除完全在容器局部画布外的标签
        if (relativeX < -margin || relativeX > W + margin || relativeY < -margin || relativeY > H + margin) continue;

        scored.push({ node, dist, relativeX, relativeY, isHovered });
    }

    // 🏎️ 按距离排序，只取最近的 MAX_VISIBLE_LABELS 个，保障超大规模下 DOM 性能守恒
    scored.sort((a, b) => a.dist - b.dist);
    const visibleSet = new Set();
    const maxLabels = Math.min(scored.length, perf.MAX_VISIBLE_LABELS);

    // 🏎️ 第二遍：仅对通过筛选的胜出节点执行 DOM 操作
    for (let i = 0; i < maxLabels; i++) {
        const { node, dist, relativeX, relativeY, isHovered } = scored[i];
        visibleSet.add(node.id);

        const el = _getOrCreateLabel(node.id, container);
        if (!el) continue;

        // LOD 分层字号与不透明度计算，实现 Obsidian 式极客呼吸渐变
        let fontSize, opacity;
        if (isHovered) {
            // 🧠 [V86.7] 临时显影的 Hover 节点，强行重载为高清饱满的字号 and 100% 不透明度
            fontSize = 14;
            opacity = 1;
        } else if (dist < perf.LOD_NEAR) {
            fontSize = Math.max(10, 16 - dist / 100);
            opacity = 1;
        } else if (dist < perf.LOD_MID) {
            const t = (dist - perf.LOD_NEAR) / (perf.LOD_MID - perf.LOD_NEAR);
            fontSize = Math.max(8, 14 - t * 6);
            opacity = Math.max(0.4, 1 - t * 0.6);
        } else {
            const t = (dist - perf.LOD_MID) / (perf.LOD_FAR - perf.LOD_MID);
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

// 🎛️ [Phase 3] 构建节流标签同步器
window._lastSyncTime = 0;
window._throttledSyncLabels = () => {
    const now = performance.now();
    const perf = window.GALAXY_PERF || { SYNC_THROTTLE_MS: 33 };
    if (now - window._lastSyncTime < perf.SYNC_THROTTLE_MS) return;
    window._lastSyncTime = now;
    if (typeof window.syncGalaxyLabels === 'function') {
        window.syncGalaxyLabels();
    }
};
