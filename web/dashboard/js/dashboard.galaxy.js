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
        try {
            elem.innerHTML = ''; // 清空可能干扰 ForceGraph 的子元素
            const graph = window.setupGalaxyEngine(elem);
            window.galaxyGraph = graph;

            // 🛡️ [V87.0] 初始化完成后立即暂停渲染循环
            // 星系只在 overview 视图显示时才应运行，resumeGalaxy() 由 showView('overview') 触发
            graph.pauseAnimation();
            console.log("⏸️ [Hub] 星系引擎初始化完毕，进入休眠态（等待 overview 视图激活）");

            // 🪐 2. 调用手势 controls 及太空阻尼重载
            if (typeof window.setupGalaxyEngineControls === 'function') {
                window.setupGalaxyEngineControls(graph);
            }
        } catch (error) {
            console.error("❌ [Hub] 3D 星系引擎核心崩溃，已触发降级保护:", error);
            if (typeof window.addAudit === 'function') {
                window.addAudit(`⛔ [SYS FALLBACK] 3D 星系引擎崩溃: ${error.message}`);
            }
            // 优雅降级 UI
            elem.innerHTML = `
                <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--text-dim); background: radial-gradient(circle, rgba(20,10,20,0.8) 0%, transparent 100%);">
                    <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;">🛰️</div>
                    <h3 style="color: var(--accent-secondary); margin-bottom: 0.5rem;">3D 引擎初始化受阻</h3>
                    <p style="font-family: var(--font-mono); font-size: 0.8rem; max-width: 400px; text-align: center; opacity: 0.7; margin-bottom: 1.5rem;">
                        检测到底层 WebGL 或数据链路解析发生严重错误，已切断渲染以保护主线程。<br/>
                        <span style="color: #ff4c4c; display: block; margin-top: 5px;">${error.message}</span>
                    </p>
                    <button class="action-btn" onclick="window.galaxyGraph=null; window.initGalaxy();" style="border: 1px solid var(--glass-border); background: var(--white-05); padding: 8px 20px; border-radius: 6px; cursor: pointer; color: var(--text-bright); transition: all 0.3s;">
                        尝试重新唤醒引擎
                    </button>
                </div>
            `;
            return; // 终止后续操作
        }
    } else {
        console.error("❌ [Hub] 3D 星系引擎核心 setupGalaxyEngine 未装载！");
        return;
    }

    // 🪐 3. 激活双阶段渐进数据网络网关
    // 注意：refreshGalaxy 在此处只拉取数据并缓存，不强制渲染（引擎处于暂停态）
    if (typeof window.refreshGalaxy === 'function') {
        window.refreshGalaxy();
    } else {
        console.warn("⚠️ [Hub] 渐进式刷新网关 refreshGalaxy 未装载！");
    }
};

