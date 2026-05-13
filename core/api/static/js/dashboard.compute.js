/**
 * 🧠 [V74.83] Illacme Compute Center - Orchestration Hub
 * 职责：作为算力中心的流量枢纽，分发指令至原子分片 (API/UI/Handlers)。
 * 降阶声明：本文件已完成 SOP-04 物理重构，所有核心逻辑已平移至 js/compute/ 分片目录。
 */

// 全局状态管理
window._activeNodeIds = [];

/**
 * 🚀 算力中心主入口
 */
window.loadComputeCenter = async function() {
    const root = document.getElementById('compute-center-root');
    if (!root) return;

    console.log('🚀 [算力枢纽] 启动全域感应与分片对正...');

    try {
        const data = await apiFetch('/api/system/config');
        window.settingsData = data;
        const compute = data.translation;

        // 1. 注入搜索工具栏 (Handlers)
        window.ComputeUI.injectSearchHeader();

        // 2. 渲染基础架构卡片 (UI)
        window.ComputeUI.renderInfrastructureTab(
            compute.compute_nodes, 
            compute.primary_node, 
            compute.fallback_node
        );

        // 3. 同步状态勋章 (UI)
        window.ComputeUI.syncStrategyBadge();

        // 4. 自动触发全域脉冲感应 (API)
        window.ComputeAPI.probeAllNodes();

    } catch (err) {
        console.error('Compute Hub initialization failed:', err);
        root.innerHTML = `<div class="alert alert-danger">算力中枢链路断开: ${err.message}</div>`;
    }
};

/**
 * 🛰️ 全局事件桥接器 (Event Bridges)
 * 职责：保持 HTML inline 事件绑定的向后兼容性。
 */
window.updateStrategy = function() {
    window.ComputeUI.syncStrategyBadge();
};

window.saveComputeStrategy = function() {
    const strategy = document.getElementById('compute-strategy-select')?.value;
    const primary = document.getElementById('primary-node-select')?.value;
    const fallback = document.getElementById('fallback-node-select')?.value;
    window.ComputeAPI.saveComputeStrategy(strategy, primary, fallback);
};

window.applyModelToNode = function(id, model) {
    apiFetch('/api/config/update', {
        method: 'POST',
        body: JSON.stringify({ [`translation.compute_nodes.${id}.model`]: model })
    }).then(() => {
        Swal.fire({ icon: 'success', title: '模型已锚定', toast: true, position: 'top-end', timer: 1000 });
        window.loadComputeCenter();
    });
};

// 桥接旧版函数名以确保平滑过渡
window.selectProvider = (id) => window.ComputeHandlers.selectProvider(id);
window.editNode = (id) => window.ComputeUI.showNodeModal(id);

// 监听 Tab 切换事件
document.addEventListener('tab-switch', (e) => {
    if (e.detail.tab === 'compute') {
        window.ComputeHandlers.switchComputeTab(e.detail.subtab || 'infrastructure');
    }
});
