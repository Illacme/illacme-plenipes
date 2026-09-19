/**
 * 🚀 Illacme Plenipes 3D Galaxy Engine - LOD Labels Module
 * 职责：LOD 智能标签池管理、相机背面/视锥裁剪与高频节流同步渲染引擎。
 * 符合 SOP-02 模块拆分协议，行数严格控制在 300 行内。
 */

// 🏷️ 标签 DOM 缓存池与迟滞缓冲记忆
window._labelPool = new Map(); // id -> DOM element
window._labelDataMap = new Map(); // id -> { title }
window._visibleLabelsSet = new Set(); // 上一帧可见标签集合 (用于迟滞排序与粘滞优先级)
window._labelMissMap = new Map(); // id -> 连续未命中帧数 (用于平滑淡出退场)

window.updateGalaxyLabelElements = (nodes) => {
    // 📝 先填充数据映射表 (不依赖 DOM 容器是否就绪)
    const newIds = new Set();
    nodes.forEach(node => {
        const cleanTitle = (node.title && String(node.title).trim())
            ? String(node.title).trim()
            : (node.id ? String(node.id).split('/').pop().replace(/\.[^/.]+$/, '') : '');
        window._labelDataMap.set(node.id, { title: cleanTitle });
        newIds.add(node.id);
    });

    // 清理已移除节点的 DOM 和数据
    for (const [id, el] of window._labelPool) {
        if (!newIds.has(id)) {
            el.remove();
            window._labelPool.delete(id);
            window._labelDataMap.delete(id);
            window._visibleLabelsSet.delete(id);
            window._labelMissMap.delete(id);
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
        el.style.transition = 'opacity 0.18s ease-out'; // 🌟 平滑过渡，杜绝突兀硬闪
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

        const holdFrames = window._labelHoldMap ? (window._labelHoldMap.get(node.id) || 0) : 0;
        scored.push({ node, dist, relativeX, relativeY, isHovered, holdFrames });
    }

    // 🏎️ 重新排序：被 Hover 节点与 Imprint 根节点拥有最高显示权；
    // 🛡️ [Hysteresis] 防闪烁迟滞缓冲：上一帧处于可见状态的标签享有 30px 稳态偏置 (Sticky Bias)，
    // 彻底杜绝相机自转时相邻节点因微米级距离交替翻转而产生的乒乓互斥闪烁！
    scored.sort((a, b) => {
        if (a.isHovered !== b.isHovered) return a.isHovered ? -1 : 1;
        const aIsImprint = a.node.group === 'imprint';
        const bIsImprint = b.node.group === 'imprint';
        if (aIsImprint !== bIsImprint) return aIsImprint ? -1 : 1;
        const aEffectiveDist = a.dist - (a.holdFrames > 0 ? 30 : 0);
        const bEffectiveDist = b.dist - (b.holdFrames > 0 ? 30 : 0);
        return aEffectiveDist - bEffectiveDist;
    });

    const renderedBoxes = [];
    const visibleSet = new Set();

    // 🏎️ 第二遍：仅对胜出且没有碰撞重叠的节点执行 DOM 操作与 GPU 定位
    for (let i = 0; i < scored.length; i++) {
        // 达到最大可见标签上限则中止，保障超大规模下 DOM 性能守恒
        if (visibleSet.size >= perf.MAX_VISIBLE_LABELS) break;

        const { node, dist, relativeX, relativeY, isHovered } = scored[i];
        const isImprint = node.group === 'imprint';

        // 📝 预估当前标题的包围盒尺寸
        const labelData = window._labelDataMap.get(node.id);
        const titleText = labelData ? labelData.title : (node.title || node.id);
        const charCount = titleText.length;

        // 计算该节点在当前距离下的 LOD 缩放字号（整数像素量化，杜绝浮点字体抖动）
        let fontSize;
        if (isHovered) {
            fontSize = 14;
        } else if (isImprint) {
            fontSize = 13;
        } else if (dist < perf.LOD_NEAR) {
            fontSize = Math.round(Math.max(10, 16 - dist / 100));
        } else if (dist < perf.LOD_MID) {
            const t = (dist - perf.LOD_NEAR) / (perf.LOD_MID - perf.LOD_NEAR);
            fontSize = Math.round(Math.max(8, 14 - t * 6));
        } else {
            const t = (dist - perf.LOD_MID) / (perf.LOD_FAR - perf.LOD_MID);
            fontSize = Math.round(Math.max(6, 8 - t * 2));
        }

        // 预估 2D 像素盒子大小 (单字符均宽约 0.65 * fontSize，并加入 16px 的左右间距容差)
        const boxWidth = charCount * fontSize * 0.65 + 16;
        const boxHeight = fontSize + 10;

        // 由于使用 translate(-50%, 15px) 居中与偏移定位，计算屏幕包围盒
        const currentBox = {
            x1: relativeX - boxWidth / 2,
            x2: relativeX + boxWidth / 2,
            y1: relativeY + 15,
            y2: relativeY + 15 + boxHeight
        };

        // 📐 碰撞规避测试：普通节点必须避让已渲染的高优先级盒子，而被 Hover 的节点强行豁免
        let hasCollision = false;
        if (!isHovered) {
            for (let j = 0; j < renderedBoxes.length; j++) {
                const rBox = renderedBoxes[j];
                const overlap = !(currentBox.x2 < rBox.x1 || currentBox.x1 > rBox.x2 || currentBox.y2 < rBox.y1 || currentBox.y1 > rBox.y2);
                if (overlap) {
                    hasCollision = true;
                    break;
                }
            }
        }

        if (hasCollision) continue; // 碰撞则自动抽稀隐藏

        renderedBoxes.push(currentBox);
        visibleSet.add(node.id);

        const el = _getOrCreateLabel(node.id, container);
        if (!el) continue;

        // LOD 呼吸不透明度计算
        let opacity;
        if (isHovered) {
            opacity = 1;
        } else if (isImprint) {
            opacity = 0.95;
        } else if (dist < perf.LOD_NEAR) {
            opacity = 1;
        } else if (dist < perf.LOD_MID) {
            const t = (dist - perf.LOD_NEAR) / (perf.LOD_MID - perf.LOD_NEAR);
            opacity = Math.max(0.4, 1 - t * 0.6);
        } else {
            const t = (dist - perf.LOD_MID) / (perf.LOD_FAR - perf.LOD_MID);
            opacity = Math.max(0.15, 0.4 - t * 0.25);
        }

        el.style.display = 'block';
        el.style.left = '0';
        el.style.top = '0';
        el.style.transform = `translate3d(${relativeX}px, ${relativeY}px, 0) translate(-50%, 15px)`;
        el.style.fontSize = `${fontSize}px`;
        el.style.opacity = opacity;
    }

    // 🧹 [Hysteresis 退场] 对不可见标签执行平滑阶梯衰减，连续 4 帧未命中才彻底隐藏
    for (const [id, el] of window._labelPool) {
        if (visibleSet.has(id)) {
            window._labelMissMap.delete(id);
        } else {
            const misses = (window._labelMissMap.get(id) || 0) + 1;
            window._labelMissMap.set(id, misses);
            if (misses >= 4) {
                el.style.display = 'none';
                el.style.opacity = '0';
            } else {
                const curOp = parseFloat(el.style.opacity) || 0.8;
                el.style.opacity = (curOp * 0.7).toFixed(2);
            }
        }
    }

    // 记忆连续可见帧数与可见集合，供下一帧做迟滞稳态决策
    window._labelHoldMap = window._labelHoldMap || new Map();
    for (const id of visibleSet) {
        window._labelHoldMap.set(id, (window._labelHoldMap.get(id) || 0) + 1);
    }
    for (const [id] of window._labelPool) {
        if (!visibleSet.has(id)) window._labelHoldMap.delete(id);
    }
    window._visibleLabelsSet = visibleSet;
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
