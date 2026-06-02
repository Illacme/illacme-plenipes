/**
 * 🚀 Illacme Plenipes 3D Galaxy Engine - 3D Core & Controls Module
 * 职责：ForceGraph3D 链式配置、三维飞跃聚焦、OrbitControls太空滑行阻尼重载与Kinetic自呼吸。
 * 符合 SOP-02 模块拆分协议，行数严格控制在 300 行内。
 */

// 🪐 3D 节点飞入聚焦算法 (Camera Fly-To Focus)
function focusNodeIn3D(node) {
    if (!window.galaxyGraph || node.x === undefined) return;
    const distance = 120; // 黄金聚焦视距
    const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
    const targetPos = (node.x === 0 && node.y === 0 && node.z === 0)
        ? { x: 0, y: 0, z: distance }
        : { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio };
    
    window.galaxyGraph.cameraPosition(targetPos, node, 1200); // 1.2 秒柔和过渡
}

// 🪐 初始化 3D 力学星系图核心配置
window.setupGalaxyEngine = (elem) => {
    let lastClickTime = 0, clickTimeout = null;
    window._hoveredNode = null;

    // 🚀 [V86.8] 色彩治理适配：从 CSS 变量读取 RGB 原始通道值以兼容 WebGL / Three.js 渲染器，杜绝 HSL/var 导致的黑屏故障
    const style = getComputedStyle(document.documentElement);
    const purpleRgb = (style.getPropertyValue('--accent-primary-rgb') || '163, 76, 255').trim();
    const cyanRgb = (style.getPropertyValue('--neon-cyan-rgb') || '0, 242, 255').trim();

    const neonPurple = `rgb(${purpleRgb})`;
    const neonCyan = `rgb(${cyanRgb})`;

    const graph = ForceGraph3D()(elem)
        .width(elem.clientWidth || window.innerWidth || 1200)
        .height(elem.clientHeight || window.innerHeight || 800)
        .backgroundColor('rgba(0,0,0,0)')
        .nodeColor(node => node.group === 'imprint' ? neonPurple : neonCyan)
        .nodeResolution(24)
        .nodeRelSize(5)
        .nodeVal(node => window._hoveredNode && node.id === window._hoveredNode.id ? 2.2 : 1.0)
        .linkColor(link => {
            const isWikilink = link.type === 'wikilink';
            const src = link.source?.id || link.source;
            const tgt = link.target?.id || link.target;
            if (!window._hoveredNode) {
                // 静默状态：物理连线亮青色，语义连线暗紫色，拉开主次感
                return isWikilink ? `rgba(${cyanRgb}, 0.35)` : `rgba(${purpleRgb}, 0.12)`;
            }
            const isConnected = src === window._hoveredNode.id || tgt === window._hoveredNode.id;
            if (isConnected) {
                // 激活状态下：物理连线极亮，语义连线亮紫以呈现高维交织感
                return isWikilink ? `rgba(${cyanRgb}, 0.95)` : `rgba(${purpleRgb}, 0.75)`;
            }
            // 未激活连线：物理和语义均降为极弱半透明，聚焦当前节点网络
            return isWikilink ? `rgba(${cyanRgb}, 0.02)` : `rgba(${purpleRgb}, 0.01)`;
        })
        .linkWidth(link => {
            const isWikilink = link.type === 'wikilink';
            const src = link.source?.id || link.source, tgt = link.target?.id || link.target;
            const scale = window._galaxyScaleMode || 'small';
            let baseWidth = isWikilink ? 1.0 : 0.5;
            if (scale === 'huge') baseWidth *= 0.3;
            else if (scale === 'large') baseWidth *= 0.5;
            else if (scale === 'medium') baseWidth *= 0.8;
            if (!window._hoveredNode) return baseWidth;
            const isConnected = src === window._hoveredNode.id || tgt === window._hoveredNode.id;
            return isConnected ? (isWikilink ? 2.4 : 1.2) : (baseWidth * 0.3);
        })
        .showNavInfo(false)
        .linkDirectionalParticles(link => {
            const isWikilink = link.type === 'wikilink';
            const src = link.source?.id || link.source, tgt = link.target?.id || link.target;
            const scale = window._galaxyScaleMode || 'small';
            if (scale === 'huge' || scale === 'large') return 0; // 超大或大规模时，强制关闭粒子以防卡顿
            if (!window._hoveredNode) {
                // 静默时：物理连线带 2 颗粒子做慢速输运，语义连线带 1 颗幽微的粒子保持默认流动
                return isWikilink ? 2 : 1;
            }
            const isConnected = src === window._hoveredNode.id || tgt === window._hoveredNode.id;
            return isConnected ? (isWikilink ? 6 : 3) : 0;
        })
        .linkDirectionalParticleWidth(link => {
            const isWikilink = link.type === 'wikilink';
            const src = link.source?.id || link.source, tgt = link.target?.id || link.target;
            if (!window._hoveredNode) {
                // 静默时：物理连线粒子宽度 1.2，语义连线微弱粒子宽度 0.8
                return isWikilink ? 1.2 : 0.8;
            }
            const isConnected = src === window._hoveredNode.id || tgt === window._hoveredNode.id;
            return isConnected ? (isWikilink ? 2.0 : 1.2) : 0;
        })
        .linkDirectionalParticleSpeed(link => {
            const isWikilink = link.type === 'wikilink';
            const src = link.source?.id || link.source, tgt = link.target?.id || link.target;
            if (!window._hoveredNode) {
                // 静默时：物理连线速度 0.008，语义连线慢流速 0.003
                return isWikilink ? 0.008 : 0.003;
            }
            const isConnected = src === window._hoveredNode.id || tgt === window._hoveredNode.id;
            return isConnected ? (isWikilink ? 0.02 : 0.008) : 0.002;
        })
        .onNodeHover(node => {
            // 🧠 [V86.7] 记录全局 hovered 节点，激活 3D 神经网络高亮并放大 Hit Box
            window._hoveredNode = node;
            elem.style.cursor = node ? 'pointer' : null;
            // 触发 3D 渲染器对节点和连线高亮/脉冲属性的快速增量更新评估，保证 WebGL 极速响应
            if (window.galaxyGraph) {
                window.galaxyGraph
                    .nodeVal(window.galaxyGraph.nodeVal())
                    .linkColor(window.galaxyGraph.linkColor())
                    .linkWidth(window.galaxyGraph.linkWidth())
                    .linkDirectionalParticles(window.galaxyGraph.linkDirectionalParticles())
                    .linkDirectionalParticleWidth(window.galaxyGraph.linkDirectionalParticleWidth())
                    .linkDirectionalParticleSpeed(window.galaxyGraph.linkDirectionalParticleSpeed());
            }
            // 🏷️ 瞬间触发标签同步，让“雷达显影特赦标签”能够以 0 毫秒延迟显影
            if (typeof window.syncGalaxyLabels === 'function') {
                window.syncGalaxyLabels();
            }
        })
        .onNodeClick(node => {
            const currentTime = Date.now();
            const timeDiff = currentTime - lastClickTime;
            if (timeDiff < 250) {
                // 🚀 [双击]：星跃聚焦并立刻打开编辑器
                if (clickTimeout) {
                    clearTimeout(clickTimeout);
                    clickTimeout = null;
                }
                if (node.x !== undefined) focusNodeIn3D(node);
                if (node.id && typeof openEditor === 'function') {
                    // node.id 已经是后端的相对路径，不需要错误替换 'doc_' 导致带有 doc_ 的文件名被损坏
                    openEditor(node.id);
                }
            } else {
                // 🪐 [单击]：纯视觉星跃聚焦，不打扰 3D 视野，不拉编辑器
                clickTimeout = setTimeout(() => {
                    if (node.x !== undefined) focusNodeIn3D(node);
                    clickTimeout = null;
                }, 250);
            }
            lastClickTime = currentTime;
        })
        .onBackgroundClick(() => {
            // 🌌 点击背景空白：宇宙视角复位，将旋转中心重置为全局中心 (0,0,0)
            if (window.galaxyGraph) {
                window.galaxyGraph.cameraPosition(
                    { x: 0, y: 0, z: 280 }, // 初始 bird view 高度
                    { x: 0, y: 0, z: 0 },  // 重置旋转中心为原点
                    1200                   // 1.2 秒柔和退回
                );
            }
        })
        .onEngineTick(() => {
            // 🏷️ [Phase 3] 节流同步标签 — 避免每帧都触发 DOM 回流
            if (typeof window._throttledSyncLabels === 'function') {
                window._throttledSyncLabels();
            }
        });

    // 🏷️ 动态重建被 ForceGraph3D 劫持抹除的标签图层
    let layer = document.getElementById('galaxy-labels-layer');
    if (!layer) {
        layer = document.createElement('div');
        layer.id = 'galaxy-labels-layer';
        elem.appendChild(layer);
        console.log("🌌 [LOD] 动态重建标签图层已挂载至 #galaxy-3d");
    }

    // 🌌 配置 d3 排斥力与连线力，确保节点充分散开
    const chargeForce = graph.d3Force('charge');
    if (chargeForce) chargeForce.strength(-120);
    const linkForce = graph.d3Force('link');
    if (linkForce) linkForce.distance(80).strength(0.4);

    return graph;
};

// 🪐 配置 OrbitControls、自转、阻尼滑行与 Kinetic 呼吸
window.setupGalaxyEngineControls = (graph) => {
    if (!graph) return;

    // 🌪️ [V86.0] Kinetic Upgrade: Native Auto-Rotate
    graph.controls().autoRotate = true;
    graph.controls().autoRotateSpeed = 0.5;

    // 🏷️ [V86.5] 满帧（60fps）零延时标签同步状态机，解决交互时便签不守星球与画面撕裂感
    let isDraggingGalaxy = false, dragFrameId = null;

    const startContinuousSync = () => {
        if (isDraggingGalaxy) return;
        isDraggingGalaxy = true;
        const syncLoop = () => {
            if (!isDraggingGalaxy) return;
            if (typeof window.syncGalaxyLabels === 'function') window.syncGalaxyLabels();
            dragFrameId = requestAnimationFrame(syncLoop);
        };
        dragFrameId = requestAnimationFrame(syncLoop);
    };

    const stopContinuousSync = () => {
        isDraggingGalaxy = false;
        if (dragFrameId) {
            cancelAnimationFrame(dragFrameId);
            dragFrameId = null;
        }
        if (typeof window.syncGalaxyLabels === 'function') window.syncGalaxyLabels();
    };

    const controls = graph.controls();
    if (controls) {
        // 🪐 [V86.6] 重载 OrbitControls 底层参数，解锁极限拉近与阻尼惯性，解禁平移
        controls.minDistance = 15;        // 极限贴脸距离
        controls.maxDistance = 2000;      // 极限拉远距离
        controls.enablePan = true;        // 允许通过右键平移相机旋转中心
        controls.enableDamping = true;    // 启用旋转/缩放/平移的太空滑行阻尼感
        controls.dampingFactor = 0.05;    // 阻尼强度

        controls.addEventListener('start', startContinuousSync);
        controls.addEventListener('change', () => {
            // 在拖拽状态下，让 requestAnimationFrame 循环全速刷新
            // 如果是非拖拽状态下的变化（例如自动旋转或程序性位置变更），则直接单次对齐更新
            if (!isDraggingGalaxy && typeof window.syncGalaxyLabels === 'function') {
                window.syncGalaxyLabels();
            }
        });
        controls.addEventListener('end', stopContinuousSync);
    }

    // 🧪 [Phase 3] Neural Pulse: 大规模时自动降频呼吸 + 标签持续同步
    let angle = 0;
    setInterval(() => {
        if (window.galaxyGraph) {
            const nodeCount = window.galaxyGraph.graphData().nodes.length;
            const perf = window.GALAXY_PERF || { SCALE_THRESHOLD_HUGE: 5000 };
            if (nodeCount > perf.SCALE_THRESHOLD_HUGE) return; // 超大规模时禁用呼吸效应
            angle += 0.05;
            const pulse = 4.5 + Math.sin(angle) * 0.8;
            window.galaxyGraph.nodeRelSize(pulse);
            // 🏷️ 持续同步标签位置 (兜底机制，确保力学引擎停止后标签仍更新)
            if (typeof window.syncGalaxyLabels === 'function') window.syncGalaxyLabels();
        }
    }, 100);

    // 📏 [Phase 3] 响应式监听 + 容器尺寸缓存
    const elem = document.getElementById('galaxy-3d');
    if (elem) {
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
    }
};
