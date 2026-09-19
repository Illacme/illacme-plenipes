/**
 * 🚀 [V122.0] Illacme Plenipes - Dispatch Center View Templates
 * 职责：定义全屏发布任务大盘与成果账本 HTML 拓扑骨架。
 * 🛡️ [SOP-02 模块拆分] 单文件严格保持在 300 行以内。
 */

if (!window.viewTemplates) {
    window.viewTemplates = {};
}

window.viewTemplates.tasks = `
<div id="view-tasks" class="view-panel">
    <!-- 1. 顶部 Header 与即时刷新动作 -->
    <div class="view-header dispatch-view-header">
        <div>
            <h2>
                <span>🚀 全域发布任务大厅</span>
                <span class="version-tag tiny dispatch-hub-tag">DISPATCH HUB</span>
            </h2>
            <p class="dispatch-view-desc">
                监控全站稿件发布流水线、各托管与社媒渠道健康矩阵、分发成果物权账本与死信自愈。
            </p>
        </div>
        <div class="dispatch-header-actions">
            <button class="secondary-btn glow-btn" onclick="if(typeof window.loadDispatchCenter==='function') window.loadDispatchCenter();">
                <span>🔄 刷新大盘</span>
            </button>
            <button class="primary-btn glow-btn" onclick="if(typeof window.triggerPublish==='function') window.triggerPublish(false);">
                <span>🚀 触发全域发布</span>
            </button>
        </div>
    </div>

    <!-- 2. 四大核心指标卡片 -->
    <div class="dispatch-metric-grid" id="dispatch-metric-container">
        <div class="dispatch-metric-card">
            <span class="metric-label">已成功分发成果</span>
            <span class="metric-val" id="metric-total-syndicated">--</span>
            <span class="metric-sub" id="metric-success-rate">成功率 --%</span>
        </div>
        <div class="dispatch-metric-card">
            <span class="metric-label">当前活跃作业</span>
            <span class="metric-val" id="metric-active-count">--</span>
            <span class="metric-sub" id="metric-active-sub">空闲中</span>
        </div>
        <div class="dispatch-metric-card">
            <span class="metric-label">异常待自愈任务</span>
            <span class="metric-val text-danger-val" id="metric-total-failed">--</span>
            <span class="metric-sub text-danger-val" id="metric-failed-sub">死信队列就绪</span>
        </div>
        <div class="dispatch-metric-card">
            <span class="metric-label">全渠道健康度</span>
            <span class="metric-val" id="metric-channels-count">--</span>
            <span class="metric-sub" id="metric-channels-sub">已连接渠道</span>
        </div>
    </div>

    <!-- 3. 全渠道连通性健康矩阵 -->
    <div class="dispatch-channel-strip glass-panel">
        <div class="channel-strip-header">
            <div class="channel-strip-title">
                <span>🌐 全渠道连通性健康矩阵</span>
                <span class="channel-strip-subtitle">(托管平台与社交渠道实时探针)</span>
            </div>
            <a href="#/plugins" onclick="if(typeof window.showView==='function') window.showView('plugins', 'hosting');" class="dispatch-text-link">
                管理渠道凭证 ↗
            </a>
        </div>
        <div class="channel-matrix-grid" id="dispatch-channel-matrix">
            <div style="color: var(--text-muted, #9ca3af); font-size: 0.8rem;">正在探测渠道健康矩阵...</div>
        </div>
    </div>

    <!-- 4. 活跃流水线作业专区 (按需显示) -->
    <div id="dispatch-active-pipeline-zone" style="display: none;"></div>

    <!-- 5. 成果账本与死信自愈选项卡导航 -->
    <div class="dispatch-tabs-bar">
        <div class="dispatch-tab-btn-group">
            <button class="dispatch-tab-btn active" id="tab-btn-ledger" onclick="window.switchDispatchSubTab('ledger')">
                <span>📋 全域分发成果账本</span>
                <span class="badge-pill" id="tab-badge-ledger">0</span>
            </button>
            <button class="dispatch-tab-btn" id="tab-btn-deadletter" onclick="window.switchDispatchSubTab('deadletter')">
                <span>⚠️ 异常死信与自愈站</span>
                <span class="badge-pill badge-danger-pill" id="tab-badge-deadletter">0</span>
            </button>
        </div>
        <!-- 检索与快捷工具 -->
        <div class="dispatch-tabs-tools">
            <input type="text" id="dispatch-search-input" placeholder="搜索原稿或渠道..." 
                oninput="if(typeof window.filterDispatchLedger==='function') window.filterDispatchLedger();" />
            <button class="secondary-btn" id="btn-batch-retry-all" onclick="if(typeof window.retryAllFailedTasks==='function') window.retryAllFailedTasks();" style="display: none;">
                <span>🔄 一键重试所有失败</span>
            </button>
        </div>
    </div>

    <!-- 6. 选项卡主体渲染区 -->
    <div id="dispatch-subtab-content" style="min-height: 260px;">
        <div class="ledger-table-wrapper" id="dispatch-ledger-container">
            <div style="padding: 30px; text-align: center; color: var(--text-muted, #9ca3af); font-size: 0.86rem;">
                正在调取分发成果账本...
            </div>
        </div>
        <div id="dispatch-deadletter-container" style="display: none; flex-direction: column; gap: 12px;"></div>
    </div>
</div>
`;
