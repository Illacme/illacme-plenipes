/**
 * 🚀 Illacme Plenipes 3D Galaxy Engine - 3D Core & Controls Module
 * 职责：ForceGraph3D 链式配置、三维飞跃聚焦、OrbitControls太空滑行阻尼重载与Kinetic自呼吸。
 * 🌟 [V130.0] 星光辉芒升级：UnrealBloom 后处理 + 多色彩自发光材质 + 动态尺寸分级
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

// 🌟 [V130.0] 多色彩星球色系映射 — 基于节点连接度与类型分配 7 种渐变色
function _getStarColor(node, isLight) {
    if (node.group === 'imprint') return isLight ? '#c030aa' : '#ff44cc'; // 品牌节点：洋红
    const links = node._linkCount || 0;
    if (links >= 10) return isLight ? '#7ab800' : '#a3ff00'; // 超级枢纽：明亮黄绿
    if (links >= 6)  return isLight ? '#00b860' : '#00ff88'; // 高连接：翠绿
    if (links >= 3)  return isLight ? '#0098b0' : '#00f2ff'; // 中等连接：青色
    if (links >= 1)  return isLight ? '#6858d8' : '#7b68ee'; // 低连接：蓝紫
    return isLight ? '#b88830' : '#ffaa33'; // 孤立节点：琥珀橙
}

// 🪐 初始化 3D 力学星系图核心配置
window.setupGalaxyEngine = (elem) => {
    let lastClickTime = 0, clickTimeout = null;
    window._hoveredNode = null;

    // 🚀 [V86.8] 色彩治理适配：从 CSS 变量读取 RGB 原始通道值以兼容 WebGL / Three.js 渲染器，杜绝 HSL/var 导致的黑屏故障
    const getColors = () => {
        const style = getComputedStyle(document.documentElement);
        const isLight = document.documentElement.getAttribute('data-theme') === 'light';
        return {
            // 亮色调模式：物理骨干使用高对比深湛青蓝 (3, 105, 161)，语义连线使用优雅紫罗兰 (147, 51, 234)
            // 暗黑宇宙模式：物理骨干采用极光青 (0, 242, 255)，语义连线采用荧光霓虹紫 (163, 76, 255)
            wikiRgb: isLight ? '3, 105, 161' : (style.getPropertyValue('--neon-cyan-rgb') || '0, 242, 255').trim(),
            semanticRgb: isLight ? '147, 51, 234' : (style.getPropertyValue('--neon-purple-rgb') || style.getPropertyValue('--accent-primary-rgb') || '163, 76, 255').trim(),
            isLight
        };
    };
    
    let { wikiRgb, semanticRgb, isLight } = getColors();

    const graph = ForceGraph3D()(elem)
        .width(elem.clientWidth || window.innerWidth || 1200)
        .height(elem.clientHeight || window.innerHeight || 800)
        .backgroundColor('rgba(0,0,0,0)')
        // 🌟 [V130.0] 多色彩星球：基于连接度与节点类型分配 7 种渐变色系
        .nodeColor(node => _getStarColor(node, isLight))
        .nodeResolution(24)
        .nodeRelSize(5)
        .nodeVal(node => {
            const links = node._linkCount || 0;
            const isHovered = window._hoveredNode && node.id === window._hoveredNode.id;
            return isHovered ? Math.max(1.5, Math.sqrt(links + 1) * 1.6) : Math.max(0.5, Math.sqrt(links + 1) * 0.8);
        })
        .linkColor(link => {
            const isWikilink = link.type === 'wikilink';
            if (isWikilink && window._showWikilinks === false) return 'rgba(0,0,0,0)';
            if (!isWikilink && window._showSemanticLinks === false) return 'rgba(0,0,0,0)';
            const src = link.source?.id || link.source;
            const tgt = link.target?.id || link.target;
            const colorRgb = isWikilink ? wikiRgb : semanticRgb;
            if (!window._hoveredNode) {
                // 静默状态：物理双链高对比深青骨架（白底 0.70 / 黑底 0.40），语义连线空灵淡雅紫烟（白底 0.16 / 黑底 0.12）
                const alpha = isWikilink ? (isLight ? 0.70 : 0.40) : (isLight ? 0.16 : 0.12);
                return `rgba(${colorRgb}, ${alpha})`;
            }
            const isConnected = src === window._hoveredNode.id || tgt === window._hoveredNode.id;
            if (isConnected) {
                // 激活状态下：物理连线极度饱满深青（0.95），语义连线高维亮紫（0.85）
                const activeAlpha = isWikilink ? 0.95 : 0.85;
                return `rgba(${colorRgb}, ${activeAlpha})`;
            }
            // 未激活连线：大幅淡化
            const dimAlpha = isWikilink ? (isLight ? 0.05 : 0.02) : (isLight ? 0.02 : 0.01);
            return `rgba(${colorRgb}, ${dimAlpha})`;
        })
        // 🌟 [几何形态区分]：物理双链笔直刚劲直线 (0)，AI 语义关联赋予 0.18 柔性引力微弧
        .linkCurvature(link => (link.type === 'wikilink' ? 0 : 0.18))
        .linkWidth(link => {
            const isWikilink = link.type === 'wikilink';
            if (isWikilink && window._showWikilinks === false) return 0;
            if (!isWikilink && window._showSemanticLinks === false) return 0;
            const src = link.source?.id || link.source, tgt = link.target?.id || link.target;
            const scale = window._galaxyScaleMode || 'small';
            // 物理双链 1.0px，语义连线 0.5px
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
            if (scale === 'huge' || scale === 'large') return 0;
            if (!window._hoveredNode) {
                // 静默时：物理连线 2 颗能量光子，语义连线 1 颗幽微粒子
                return isWikilink ? 2 : 1;
            }
            const isConnected = src === window._hoveredNode.id || tgt === window._hoveredNode.id;
            return isConnected ? (isWikilink ? 6 : 3) : 0;
        })
        .linkDirectionalParticleWidth(link => {
            const isWikilink = link.type === 'wikilink';
            const src = link.source?.id || link.source, tgt = link.target?.id || link.target;
            if (!window._hoveredNode) {
                return isWikilink ? (isLight ? 1.6 : 1.2) : 0.7;
            }
            const isConnected = src === window._hoveredNode.id || tgt === window._hoveredNode.id;
            return isConnected ? (isWikilink ? 2.4 : 1.2) : 0;
        })
        .linkDirectionalParticleSpeed(link => {
            const isWikilink = link.type === 'wikilink';
            const src = link.source?.id || link.source, tgt = link.target?.id || link.target;
            if (!window._hoveredNode) {
                return isWikilink ? 0.008 : 0.003;
            }
            const isConnected = src === window._hoveredNode.id || tgt === window._hoveredNode.id;
            return isConnected ? (isWikilink ? 0.02 : 0.008) : 0.002;
        })
        .linkDirectionalParticleColor(link => (link.type === 'wikilink' ? `rgb(${wikiRgb})` : `rgb(${semanticRgb})`))
        .onNodeHover(node => {
            // 🧠 [V86.7] 记录全局 hovered 节点，激活 3D 神经网络高亮并放大 Hit Box
            window._hoveredNode = node;
            elem.style.cursor = node ? 'pointer' : null;
            // 触发 3D 渲染器对节点和连线高亮/脉冲属性的快速增量更新评估，保证 WebGL 极速响应
            if (window.galaxyGraph) {
                window.galaxyGraph
                    .nodeColor(window.galaxyGraph.nodeColor())
                    .nodeVal(window.galaxyGraph.nodeVal())
                    .linkColor(window.galaxyGraph.linkColor())
                    .linkWidth(window.galaxyGraph.linkWidth())
                    .linkDirectionalParticles(window.galaxyGraph.linkDirectionalParticles())
                    .linkDirectionalParticleWidth(window.galaxyGraph.linkDirectionalParticleWidth())
                    .linkDirectionalParticleSpeed(window.galaxyGraph.linkDirectionalParticleSpeed());
            }
            // 🏷️ 瞬间触发标签同步，让"雷达显影特赦标签"能够以 0 毫秒延迟显影
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
            if (typeof window.closeNodeDirector === 'function') {
                window.closeNodeDirector();
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

    // 🌌 [力学主权解耦] 配置 d3 排斥力与连线力，彻底消除语义弹力超载导致的塌缩成团
    const chargeForce = graph.d3Force('charge');
    if (chargeForce) chargeForce.strength(-240);
    const linkForce = graph.d3Force('link');
    if (linkForce) {
        linkForce
            .distance(link => (link.type === 'wikilink' ? 80 : 150))
            .strength(link => (link.type === 'wikilink' ? 0.35 : 0.04));
    }

    // 🌟 [V130.0] 注入 UnrealBloom 辉光后处理管线
    if (window.THREE && window.THREE.UnrealBloomPass) {
        try {
            const bloomPass = new window.THREE.UnrealBloomPass(
                new window.THREE.Vector2(elem.clientWidth || 1200, elem.clientHeight || 800),
                isLight ? 0.6 : 1.5,   // strength: 亮色模式降低辉光强度
                0.8,                   // radius: 辉光扩散半径
                isLight ? 0.4 : 0.1    // threshold: 亮色模式提高阈值，避免画面过曝
            );
            graph.postProcessingComposer().addPass(bloomPass);
            window._galaxyBloomPass = bloomPass;
            console.log('🌟 [Bloom] UnrealBloomPass 辉光后处理已注入', isLight ? '(亮色模式)' : '(暗色模式)');
        } catch (e) {
            console.warn('🌟 [Bloom] 辉光后处理注入失败，降级为无辉光模式:', e.message);
        }
    } else {
        console.warn('🌟 [Bloom] UnrealBloomPass 未加载，使用默认渲染');
    }

    // 🌗 [Theme] 昼夜模式深度联动：实时响应光影切换
    window.addEventListener('themeModeChanged', () => {
        const newColors = getColors();
        wikiRgb = newColors.wikiRgb;
        semanticRgb = newColors.semanticRgb;
        isLight = newColors.isLight;
        
        // 🌟 [V130.0] 动态调整 Bloom 参数适配昼夜模式
        if (window._galaxyBloomPass) {
            window._galaxyBloomPass.strength = isLight ? 0.6 : 1.5;
            window._galaxyBloomPass.threshold = isLight ? 0.4 : 0.1;
        }

        // 强制引擎基于新闭包变量重绘色彩、线宽、粒子与节点
        graph.nodeColor(graph.nodeColor());
        graph.linkColor(graph.linkColor());
        graph.linkWidth(graph.linkWidth());
        graph.linkDirectionalParticleColor(graph.linkDirectionalParticleColor());
        graph.linkDirectionalParticleWidth(graph.linkDirectionalParticleWidth());
    });

    return graph;
};
