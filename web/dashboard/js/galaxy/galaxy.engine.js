/**
 * 🚀 Illacme Plenipes 3D Galaxy Engine - 3D Core & Controls Module
 * 职责：ForceGraph3D 链式配置、三维飞跃聚焦、OrbitControls太空滑行阻尼重载与Kinetic自呼吸。
 * 符合 SOP-02 模块拆分协议，行数严格控制在 300 行内。
 */

// 🛡️ [V87.0] WebGL 生命周期守卫：追踪星系视图的物理可见状态
// 只有 overview 视图激活时此标志才为 true，防止 GPU 在后台空转导致 CONTEXT_LOST
window._galaxyVisible = false;


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
    const getColors = () => {
        const style = getComputedStyle(document.documentElement);
        return {
            purpleRgb: (style.getPropertyValue('--accent-primary-rgb') || '163, 76, 255').trim(),
            cyanRgb: (style.getPropertyValue('--neon-cyan-rgb') || '0, 242, 255').trim()
        };
    };
    
    let { purpleRgb, cyanRgb } = getColors();
    let neonPurple = `rgb(${purpleRgb})`;
    let neonCyan = `rgb(${cyanRgb})`;

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
            if (isWikilink && window._showWikilinks === false) return 'rgba(0,0,0,0)';
            if (!isWikilink && window._showSemanticLinks === false) return 'rgba(0,0,0,0)';
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
            if (isWikilink && window._showWikilinks === false) return 0;
            if (!isWikilink && window._showSemanticLinks === false) return 0;
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
            if (isWikilink && window._showWikilinks === false) return 0;
            if (!isWikilink && window._showSemanticLinks === false) return 0;
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
                    openEditor(node.id);
                }
            } else {
                // 🪐 [单击]：纯视觉星跃聚焦，并在连接模式或普通模式下做处理
                clickTimeout = setTimeout(() => {
                    if (node.x !== undefined) focusNodeIn3D(node);
                    if (window._galaxyConnectionSourceNode) {
                        if (typeof window.confirmManualConnection === 'function') {
                            window.confirmManualConnection(node);
                        }
                    } else {
                        if (typeof window.showNodeDirector === 'function') {
                            window.showNodeDirector(node);
                        }
                    }
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

    // 🌗 [Theme] 昼夜模式深度联动：实时响应光影切换
    window.addEventListener('themeModeChanged', () => {
        const newColors = getColors();
        purpleRgb = newColors.purpleRgb;
        cyanRgb = newColors.cyanRgb;
        neonPurple = `rgb(${purpleRgb})`;
        neonCyan = `rgb(${cyanRgb})`;
        
        // 强制引擎基于新闭包变量重绘色彩
        graph.nodeColor(graph.nodeColor());
        graph.linkColor(graph.linkColor());
    });

    return graph;
};
