/**
 * 🚀 Illacme Plenipes Dashboard 3D Galaxy Engine - Hub Orchestrator
 * 职责：作为 3D 星系引擎主总控与协调枢纽，挂载 window.initGalaxy 入口。
 * 符合 SOP-02 模块拆分协议，实现主巨石文件的彻底降维。
 */

window.initGalaxy = () => {
    const elem = document.getElementById('galaxy-3d');
    if (!elem || typeof ForceGraph3D === 'undefined') return;

    if (window.galaxyGraph) return;

    console.log("🌌 [Hub] 启动 3D 星系图总装配流程...");

    // 🪐 1. 调用 3D 核心分片进行底座配置
    if (typeof window.setupGalaxyEngine === 'function') {
        const graph = window.setupGalaxyEngine(elem);
        window.galaxyGraph = graph;

        // 🪐 2. 调用手势 controls 及太空阻尼重载
        if (typeof window.setupGalaxyEngineControls === 'function') {
            window.setupGalaxyEngineControls(graph);
        }
    } else {
        console.error("❌ [Hub] 3D 星系引擎核心 setupGalaxyEngine 未装载！");
        return;
    }

    // 🪐 3. 激活双阶段渐进数据网络网关
    if (typeof window.refreshGalaxy === 'function') {
        window.refreshGalaxy();
    } else {
        console.warn("⚠️ [Hub] 渐进式刷新网关 refreshGalaxy 未装载！");
    }
};
