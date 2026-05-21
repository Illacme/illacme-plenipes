/**
 * 🚀 Illacme Plenipes 3D Galaxy Engine - Scale & Performance Module
 * 职责：定义全局 LOD/性能阈值常数，并实现大规模自适应品质降级器。
 * 符合 SOP-02 模块拆分协议，行数严格控制在 300 行内。
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

// 暴露全局变量以供其他物理分片访问
window.GALAXY_PERF = GALAXY_PERF;

// ═══════════════════════════════════════════════════
// 🎛️ [Phase 3] 大规模自适应渲染降级器
// ═══════════════════════════════════════════════════
window.applyScaleAdaptation = (nodeCount) => {
    if (!window.galaxyGraph) return;

    const chargeForce = window.galaxyGraph.d3Force('charge');
    const linkForce = window.galaxyGraph.d3Force('link');

    let scaleMode = 'small';
    const perf = window.GALAXY_PERF || GALAXY_PERF;

    if (nodeCount > perf.SCALE_THRESHOLD_HUGE) {
        scaleMode = 'huge';
        window.galaxyGraph.nodeResolution(6);
        window.galaxyGraph.nodeRelSize(2.5);
        if (chargeForce) chargeForce.strength(-60);
        if (linkForce) linkForce.distance(40).strength(0.5);
        console.log(`🎛️ [LOD] 超大规模降级: ${nodeCount} 节点 → 极简引力收敛模式`);
    } else if (nodeCount > perf.SCALE_THRESHOLD_LARGE) {
        scaleMode = 'large';
        window.galaxyGraph.nodeResolution(8);
        window.galaxyGraph.nodeRelSize(3.5);
        if (chargeForce) chargeForce.strength(-80);
        if (linkForce) linkForce.distance(50).strength(0.45);
        console.log(`🎛️ [LOD] 大规模降级: ${nodeCount} 节点 → 无粒子引力收敛模式`);
    } else if (nodeCount > perf.SCALE_THRESHOLD_MED) {
        scaleMode = 'medium';
        window.galaxyGraph.nodeResolution(12);
        window.galaxyGraph.nodeRelSize(4);
        if (chargeForce) chargeForce.strength(-100);
        if (linkForce) linkForce.distance(65).strength(0.4);
        console.log(`🎛️ [LOD] 中等规模降级: ${nodeCount} 节点 → 低精度引力收敛模式`);
    } else {
        scaleMode = 'small';
        window.galaxyGraph.nodeResolution(24);
        window.galaxyGraph.nodeRelSize(5);
        if (chargeForce) chargeForce.strength(-120);
        if (linkForce) linkForce.distance(80).strength(0.4);
        console.log(`🎛️ [LOD] 小规模高品质模式激活: ${nodeCount} 节点`);
    }

    window._galaxyScaleMode = scaleMode;

    // 🚀 [V100.0] 触发 3D 渲染器快速重绘所有链路样式回调，以应用 scaleMode 所致的变化
    window.galaxyGraph
        .linkColor(window.galaxyGraph.linkColor())
        .linkWidth(window.galaxyGraph.linkWidth())
        .linkDirectionalParticles(window.galaxyGraph.linkDirectionalParticles())
        .linkDirectionalParticleWidth(window.galaxyGraph.linkDirectionalParticleWidth())
        .linkDirectionalParticleSpeed(window.galaxyGraph.linkDirectionalParticleSpeed());
};
