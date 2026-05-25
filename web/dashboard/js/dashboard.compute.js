/**
 * 🧠 [V74.24] Illacme Compute Center - Orchestration Hub (GENOME RESTORED)
 * 职责：作为算力中心的流量枢纽，分发指令至原子分片 (API/UI/Handlers)。
 * 还原声明：本文件内容严格对正 83b7900 基准版本，负责物理槽位的初始化注入。
 */

// 全局状态管理
window._activeNodeIds = [];

/**
 * 🚀 算力中心主入口 (像素级还原注入逻辑)
 */
window.loadComputeCenter = async function(targetTab) {
    const topActions = document.getElementById('compute-header-actions-top');
    const navTabsSlot = document.getElementById('compute-nav-tabs-slot');
    const navActionsSlot = document.getElementById('compute-nav-actions-slot');
    const contentRoot = document.getElementById('compute-center-root');

    if (!topActions || !navTabsSlot || !navActionsSlot || !contentRoot) return;

    // 🛡️ [V74.10] 物理负载监控已迁移至全局底部状态栏 (footer-center)
    // 头部仅保留搜索框（由 switchComputeTab 按需注入）
    topActions.innerHTML = `
        <div class="search-box" style="margin-left: auto;">
            <input type="text" id="compute-search" placeholder="搜索单元、提供商或模型..." oninput="window.ComputeHandlers.filterNodes(this.value)">
        </div>
    `;

    // 2. 注入导航标签与策略勋章 (原始结构)
    navTabsSlot.innerHTML = `
        <div style="display: flex; align-items: center; gap: 24px;">
            <nav class="tactical-tabs">
                <button class="t-tab active" data-tab="infrastructure" onclick="window.ComputeHandlers.switchComputeTab('infrastructure')">
                    <span class="t-icon">🧱</span> 算力单元
                </button>
                <button class="t-tab" data-tab="strategy" onclick="window.ComputeHandlers.switchComputeTab('strategy')">
                    <span class="t-icon">⚖️</span> 调度策略
                </button>
            </nav>
            <div id="compute-strategy-badge-slot">
                <div class="strategy-mode-badge badge active" style="font-size: 0.65rem; padding: 4px 12px;">LOADING...</div>
            </div>
        </div>
    `;

    // 3. 注入操作动作 (原始按钮组)
    navActionsSlot.innerHTML = `
        <div class="tactical-actions" style="display: flex; gap: 12px; align-items: center;">
            <button id="btn-add-node" class="mini-btn glow-btn" onclick="window.ComputeHandlers.showAddNodeModal()">+ 新增算力单元</button>
            <button id="btn-probe-nodes" class="mini-btn" onclick="window.ComputeHandlers.probeAllNodes()">📡 全域脉冲</button>
            <button id="btn-save-compute-strategy" class="mini-btn glow-btn" disabled style="display:none; padding: 6px 20px;" onclick="window.ComputeHandlers.saveComputeStrategy(event)">
                💾 保存配置
            </button>
            <button id="id-btn-reset-compute-strategy" class="mini-btn" style="display:none;" onclick="window.ComputeHandlers.resetComputeStrategy()">🔄 恢复默认</button>
            <button id="btn-refresh-compute" class="mini-btn" onclick="window.loadComputeCenter()">🔄 刷新</button>
        </div>
    `;

    // 🚀 [V74.24] 预加载全局配置并同步勋章
    try {
        const res = await apiFetch('/api/system/config');
        const config = res.config || res;
        window.settingsData = window.settingsData || {};
        window.settingsData.translation = config.translation || {};
        window.ComputeHandlers.syncStrategyBadge();
    } catch (e) {
        console.error("Failed to pre-sync strategy badge:", e);
    }

    // 4. 准备加载视口
    contentRoot.innerHTML = `
        <div id="compute-tab-viewport" class="compute-viewport" style="margin-top: 0 !important; padding-top: 5px;">
            <div class="loading-scanner">
                <div class="scan-line"></div>
                <p>正在同步物理全域频率...</p>
            </div>
        </div>
    `;

    // 默认启动指定子选项卡视图，兜底使用基础架构视图
    const activeTab = targetTab || 'infrastructure';
    await window.ComputeHandlers.switchComputeTab(activeTab);
};
