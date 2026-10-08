/**
 * 🚀 [V125.0] Illacme Plenipes - Dispatch Center View Templates
 * 职责：定义全屏发布任务大盘双模式（全站托管部署 / 社交媒体分发）HTML 拓扑骨架。
 * 🛡️ [SOP-02 模块拆分] 单文件严格保持在 300 行以内。
 */

if (!window.viewTemplates) {
    window.viewTemplates = {};
}

window.viewTemplates.tasks = `
<div id="view-tasks" class="view-panel">
    <!-- 1. 顶部 Header 与即时刷新动作 (1:1 像素级物理对齐数据统计 Analytics Hub 视觉范式) -->
    <div class="view-header" style="margin-bottom: 0; padding-bottom: 15px; border-bottom: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;">
        <h2>🚀 发布中心 (Publishing Hub)</h2>
        <div class="header-actions">
            <button class="primary-btn glow-btn" id="btn-refresh-dispatch" onclick="if(typeof window.refreshCurrentDispatchView==='function') window.refreshCurrentDispatchView();" style="padding: 5px 12px; font-size: 0.75rem; height: 28px; line-height: 14px;">🔄 刷新状态</button>
        </div>
    </div>

    <!-- 2. 下层矩阵: 导航切换与即时态势勋章 (对齐算力中心 Tactical Tabs) -->
    <div class="header-nav-row" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 10px; border-bottom: 1px solid var(--glass-border); margin-top: 0; width: 100%; box-sizing: border-box; flex-shrink: 0;">
            <div style="display: flex; align-items: center; gap: 20px;">
                <nav class="tactical-tabs dispatch-tactical-tabs">
                    <button class="t-tab active" id="tab-dispatch-hosting" onclick="if(typeof window.switchDispatchMode==='function') window.switchDispatchMode('hosting');">
                        <span class="t-icon">🌐</span> 网站托管发布
                        <span class="tab-badge" id="badge-hosting-ready">--</span>
                    </button>
                    <button class="t-tab" id="tab-dispatch-social" onclick="if(typeof window.switchDispatchMode==='function') window.switchDispatchMode('social');">
                        <span class="t-icon">📡</span> 社交媒体分发
                        <span class="tab-badge" id="badge-social-tasks">--</span>
                    </button>
                </nav>
                <div id="dispatch-pipeline-status-badge-slot">
                    <div class="dispatch-mode-badge badge active" id="dispatch-live-badge">● 系统就绪</div>
                </div>
            </div>
            <div class="header-nav-actions" style="display: flex; gap: 10px; align-items: center;">
                <button class="secondary-btn btn-sm" onclick="if(typeof window.showView==='function') window.showView('plugins', 'hosting');" style="padding: 4px 10px; font-size: 0.74rem;">
                    <span>⚙️ 平台账号配置 ↗</span>
                </button>
                <button class="secondary-btn btn-sm" onclick="if(typeof window.showView==='function') window.showView('settings', 'themes');" style="padding: 4px 10px; font-size: 0.74rem;">
                    <span>🎨 装帧主题 ↗</span>
                </button>
            </div>
        </div>

    <!-- 2. 独立内容滚动视区 (Header 物理固定，仅内容区向下平滑滚动) -->
    <div class="view-content scroll-container dispatch-content-scroll" id="dispatch-scroll-viewport">
        <!-- ========================================== -->
        <!-- 模式一：🌐 网站托管发布专区 (Site Hosting) -->
        <!-- ========================================== -->
        <div id="dispatch-hosting-view" class="dispatch-subview-panel">
            <!-- 战区一：整站编译态势与并发调度总控台 -->
            <div class="hosting-control-console" id="hosting-control-console">
                <div style="padding: 24px; text-align: center; color: var(--text-muted); font-size: 0.86rem;">
                    正在探测整站发布产物态势...
                </div>
            </div>

            <!-- 战区二：网站托管平台卡片列表 -->
            <div class="hosting-fleet-section">
                <div class="hosting-section-header">
                    <div class="section-title">
                        <span class="title-icon">🌐</span> 网站托管平台 (Website Hosting)
                        <span class="section-sub-tag" id="hosting-fleet-subtag">主流平台原生支持</span>
                    </div>
                    <div class="section-actions">
                        <button class="secondary-btn" onclick="if(typeof window.showView==='function') window.showView('plugins', 'hosting');" style="padding: 4px 10px; font-size: 0.75rem;">
                            <span>⚙️ 管理托管平台 ↗</span>
                        </button>
                    </div>
                </div>
                <div class="hosting-fleet-grid" id="hosting-fleet-container">
                    <div style="padding: 20px; text-align: center; color: var(--text-muted); font-size: 0.84rem;">
                        正在检索托管平台连通性...
                    </div>
                </div>
            </div>

            <!-- 战区三：网站发布历史记录 -->
            <div class="hosting-ledger-section">
                <div class="hosting-section-header">
                    <div class="section-title">
                        <span class="title-icon">📜</span> 网站发布历史记录 (Publishing History)
                    </div>
                    <div class="section-tools">
                        <button class="secondary-btn" onclick="if(typeof window.loadHostingDeployCenter==='function') window.loadHostingDeployCenter();" style="padding: 4px 10px; font-size: 0.75rem;">
                            <span>🔄 刷新记录</span>
                        </button>
                    </div>
                </div>
                <div class="ledger-table-wrapper" id="hosting-batch-container">
                    <div style="padding: 24px; text-align: center; color: var(--text-muted); font-size: 0.84rem;">
                        暂无网站发布历史记录
                    </div>
                </div>
            </div>
        </div>

        <!-- ========================================== -->
        <!-- 模式二：📡 社交媒体分发专区 (Social Syndication) -->
        <!-- ========================================== -->
        <div id="dispatch-social-view" class="dispatch-subview-panel" style="display: none;">
            <!-- 四大核心指标卡片 (社媒分发专属态势感知，支持点击一键状态过滤) -->
            <div class="dispatch-metric-grid" id="dispatch-metric-container">
                <div class="dispatch-metric-card interactive" onclick="if(typeof window.quickFilterDispatchStatus==='function') { window.switchDispatchMode('social'); window.quickFilterDispatchStatus('success'); }" title="点击仅看成功分发成果">
                    <span class="metric-label">已成功分发成果</span>
                    <span class="metric-val" id="metric-total-syndicated">--</span>
                    <span class="metric-sub" id="metric-success-rate">成功率 --%</span>
                </div>
                <div class="dispatch-metric-card">
                    <span class="metric-label">当前活跃作业</span>
                    <span class="metric-val" id="metric-active-count">--</span>
                    <span class="metric-sub" id="metric-active-sub">空闲中</span>
                </div>
                <div class="dispatch-metric-card interactive" onclick="if(typeof window.quickFilterDispatchStatus==='function') { window.switchDispatchMode('social'); window.quickFilterDispatchStatus('failed'); }" title="点击仅看异常待自愈任务">
                    <span class="metric-label">异常待自愈任务</span>
                    <span class="metric-val text-danger-val" id="metric-total-failed">--</span>
                    <span class="metric-sub text-danger-val" id="metric-failed-sub">死信队列就绪</span>
                </div>
                <div class="dispatch-metric-card interactive" id="metric-channels-card" onclick="if(typeof window.showView==='function') window.showView('plugins', 'hosting');" title="点击直达渠道凭证与驱动配置" style="cursor: pointer;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="metric-label">全渠道健康度</span>
                        <span style="font-size: 0.72rem; color: var(--neon-cyan); opacity: 0.85;">管理 ↗</span>
                    </div>
                    <span class="metric-val" id="metric-channels-count">--</span>
                    <span class="metric-sub" id="metric-channels-sub">已连接渠道 · 点击配置 ↗</span>
                </div>
            </div>

            <!-- 活跃流水线作业专区 (按需显示) -->
            <div id="dispatch-active-pipeline-zone" style="display: none;"></div>

            <!-- 全域分发总账流水平行控制栏 (左侧多维组合筛选，右侧搜索与批量操作) -->
            <div class="dispatch-tabs-bar">
                <div class="dispatch-filter-group" id="dispatch-filter-group">
                    <div class="dispatch-filter-wrapper">
                        <select id="dispatch-filter-lang" class="dispatch-filter-select" onchange="if(typeof window.filterDispatchLedger==='function') window.filterDispatchLedger();" title="按发布语种筛选">
                            <option value="">🌐 全部语种</option>
                        </select>
                    </div>
                    <div class="dispatch-filter-wrapper">
                        <select id="dispatch-filter-channel" class="dispatch-filter-select" onchange="if(typeof window.filterDispatchLedger==='function') window.filterDispatchLedger();" title="按目标分发渠道筛选">
                            <option value="">🏷️ 全部渠道</option>
                        </select>
                    </div>
                    <div class="dispatch-filter-wrapper">
                        <select id="dispatch-filter-status" class="dispatch-filter-select" onchange="if(typeof window.filterDispatchLedger==='function') window.filterDispatchLedger();" title="按发布状态筛选">
                            <option value="">📊 全部状态</option>
                            <option value="success">✅ 仅看成功</option>
                            <option value="failed">⚠️ 仅看异常待自愈</option>
                        </select>
                    </div>
                </div>

                <div class="dispatch-tabs-tools">
                    <input type="text" id="dispatch-search-input" placeholder="搜索原稿或渠道..." 
                        oninput="if(typeof window.filterDispatchLedger==='function') window.filterDispatchLedger();" />
                    <button class="secondary-btn" id="btn-batch-retry-all" onclick="if(typeof window.retryAllFailedTasks==='function') window.retryAllFailedTasks();" style="display: none;">
                        <span>🔄 一键重试所有失败</span>
                    </button>
                </div>
            </div>

            <!-- 社媒成果总账主体渲染区 -->
            <div id="dispatch-subtab-content" style="min-height: 260px;">
                <div class="ledger-table-wrapper" id="dispatch-ledger-container">
                    <div style="padding: 30px; text-align: center; color: var(--text-muted); font-size: 0.86rem;">
                        正在调取分发成果记录...
                    </div>
                </div>
                <div id="dispatch-deadletter-container" style="display: none; flex-direction: column; gap: 12px;"></div>
            </div>
        </div>
    </div>

    <!-- 3. 底部专属固定分页栏 (仅在社媒视图激活且有数据时显示) -->
    <div class="dispatch-ledger-pagination-dock" id="dispatch-pagination-dock" style="display: none;"></div>
</div>
`;
