/**
 * 🚀 Illacme Plenipes 3D Galaxy Engine - OrbitControls & Animation Lifecycle Module
 * 职责：OrbitControls 阻尼滑行重载、Kinetic自呼吸、Neural Pulse 节流呼吸和 WebGL 渲染生命周期管理。
 * 符合 SOP-02 模块拆分协议，行数严格控制在 300 行内。
 */

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
    // 🛡️ [V87.0] 加入 _galaxyVisible 守卫：不可见时跳过所有 GPU 操作，防止后台空转
    let angle = 0;
    setInterval(() => {
        if (!window._galaxyVisible) return; // 🛡️ 守卫：视图不可见时立刻跳出，零 GPU 消耗
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

// ==========================================
// 🛡️ [V87.0] WebGL 生命周期管理 — 星系动画暂停/恢复接口
// 由 dashboard.views.js 在视图切换时调用，防止后台 GPU 空转
// ==========================================

/**
 * 暂停星系渲染循环（离开 overview 视图时调用）
 * 同时停止 OrbitControls 自动旋转，最小化 GPU 负载
 */
window.pauseGalaxy = () => {
    window._galaxyVisible = false;
    if (window.galaxyGraph) {
        window.galaxyGraph.pauseAnimation(); // 停止 Three.js requestAnimationFrame 循环
        const controls = window.galaxyGraph.controls();
        if (controls) controls.autoRotate = false; // 停止自动旋转
    }
    console.log('⏸️ [Galaxy] 渲染循环已暂停（视图离开）');
};

/**
 * 恢复星系渲染循环（回到 overview 视图时调用）
 * 恢复自动旋转并触发一次数据刷新
 */
window.resumeGalaxy = () => {
    window._galaxyVisible = true;
    if (window.galaxyGraph) {
        window.galaxyGraph.resumeAnimation(); // 恢复 Three.js requestAnimationFrame 循环
        const controls = window.galaxyGraph.controls();
        if (controls) controls.autoRotate = true; // 恢复自动旋转
    }
    console.log('▶️ [Galaxy] 渲染循环已恢复（视图激活）');
};
