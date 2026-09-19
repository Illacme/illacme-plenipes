/**
 * 🚀 [V122.0] Illacme Plenipes - Dispatch Full Workbench Component
 * 职责：全域发布任务大厅全屏工作台数据调度、指标卡片与全渠道健康矩阵渲染。
 * 🛡️ [SOP-02 模块拆分] 单文件严格保持在 300 行以内。
 */

window.currentDispatchSubTab = 'ledger';

/**
 * 核心加载入口：供 window.loadViewData('tasks') 调用
 */
window.loadDispatchCenter = async function (subTab) {
    if (subTab) window.currentDispatchSubTab = subTab;
    const container = document.getElementById('view-tasks');
    if (!container) return;

    try {
        if (typeof apiFetch !== 'function') return;
        const res = await apiFetch('/api/dispatch/overview');
        if (res && res.status === 'success') {
            window._lastDispatchOverview = res;
            window.renderDispatchMetrics(res);
            window.renderChannelHealthMatrix(res.channel_health || []);
            window.renderActivePipelineZone(res);
            
            // 联动更新指示器
            if (typeof window.updateDispatchIndicator === 'function') {
                window.updateDispatchIndicator(res);
            }

            // 渲染默认或指定的子 Tab
            window.switchDispatchSubTab(window.currentDispatchSubTab, false);
        }
    } catch (err) {
        console.error("🛑 加载全域发布大厅失败:", err);
    }
};

/**
 * 渲染四大核心态势指标卡片
 */
window.renderDispatchMetrics = function (data) {
    const summary = (data && data.summary) || {};
    const channelHealth = (data && data.channel_health) || [];
    const enabledChannels = channelHealth.filter(c => c.enabled);

    const elSyndicated = document.getElementById('metric-total-syndicated');
    const elRate = document.getElementById('metric-success-rate');
    const elActive = document.getElementById('metric-active-count');
    const elActiveSub = document.getElementById('metric-active-sub');
    const elFailed = document.getElementById('metric-total-failed');
    const elFailedSub = document.getElementById('metric-failed-sub');
    const elChannels = document.getElementById('metric-channels-count');
    const elChannelsSub = document.getElementById('metric-channels-sub');

    if (elSyndicated) elSyndicated.innerText = summary.total_syndicated ?? 0;
    if (elRate) elRate.innerText = `分发成功率 ${summary.success_rate || '100%'}`;

    if (elActive) elActive.innerText = summary.active_count ?? 0;
    if (elActiveSub) {
        elActiveSub.innerText = data.is_publishing ? '正在并发分发中' : '管线就绪待命';
        elActiveSub.style.color = data.is_publishing ? '#00f0ff' : 'var(--text-muted, #9ca3af)';
    }

    if (elFailed) elFailed.innerText = summary.total_failed ?? 0;
    if (elFailedSub) {
        elFailedSub.innerText = (summary.total_failed > 0) ? '需前往自愈修复' : '0 待修死信';
        elFailedSub.style.color = (summary.total_failed > 0) ? '#ff6b6b' : '#00ff88';
    }

    if (elChannels) elChannels.innerText = `${enabledChannels.length} / ${channelHealth.length}`;
    if (elChannelsSub) elChannelsSub.innerText = `已激活 ${enabledChannels.length} 个渠道`;
};

/**
 * 渲染全渠道连通性健康矩阵卡片组
 */
window.renderChannelHealthMatrix = function (channels) {
    const matrix = document.getElementById('dispatch-channel-matrix');
    if (!matrix) return;

    if (!channels || channels.length === 0) {
        matrix.innerHTML = '<div style="color: var(--text-muted); font-size: 0.8rem;">未探测到已挂载的分发驱动</div>';
        return;
    }

    matrix.innerHTML = channels.map(ch => {
        const dotClass = ch.status || 'disabled';
        return `
            <div class="channel-health-card" title="${ch.status_msg || ''}">
                <span class="ch-icon">${ch.icon || '🌐'}</span>
                <div class="ch-info">
                    <span class="ch-name">${window.escapeHtml ? window.escapeHtml(ch.name) : ch.name}</span>
                    <span class="ch-status">
                        <span class="ch-dot ${dotClass}"></span>
                        <span style="color: var(--text-muted, #9ca3af); font-size: 0.72rem;">${ch.status_msg}</span>
                    </span>
                </div>
            </div>
        `;
    }).join('');
};

/**
 * 渲染活跃流水线专区（仅在任务运行中时展示）
 */
window.renderActivePipelineZone = function (data) {
    const zone = document.getElementById('dispatch-active-pipeline-zone');
    if (!zone) return;

    if (!data || !data.is_publishing) {
        zone.style.display = 'none';
        zone.innerHTML = '';
        return;
    }

    zone.style.display = 'block';
    zone.innerHTML = `
        <div class="active-pipeline-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.1rem; animation: dispatchPulse 1.5s infinite;">⚡</span>
                    <div>
                        <span style="font-weight: 800; font-size: 0.95rem; color: #00f0ff;">全域发布流水线正在执行</span>
                        <span style="font-size: 0.76rem; color: var(--text-muted, #9ca3af); margin-left: 8px;">(四阶并发管线已全量点火)</span>
                    </div>
                </div>
                <button class="secondary-btn danger" onclick="if(typeof window.abortSync==='function') window.abortSync();" style="padding: 5px 14px; font-size: 0.8rem;">
                    🛑 紧急中止当前发布
                </button>
            </div>
            <!-- 四阶进度阶梯指示 -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 4px;">
                <div style="background: rgba(0, 240, 255, 0.15); border: 1px solid rgba(0, 240, 255, 0.4); border-radius: 6px; padding: 8px 10px; font-size: 0.76rem; color: #ffffff;">
                    ✅ 1. 原稿排版与清洗
                </div>
                <div style="background: rgba(0, 240, 255, 0.15); border: 1px solid rgba(0, 240, 255, 0.4); border-radius: 6px; padding: 8px 10px; font-size: 0.76rem; color: #ffffff;">
                    ✅ 2. AI 译文与词库对齐
                </div>
                <div style="background: rgba(0, 240, 255, 0.15); border: 1px solid rgba(0, 240, 255, 0.4); border-radius: 6px; padding: 8px 10px; font-size: 0.76rem; color: #ffffff;">
                    ✅ 3. 静态装帧主题构建
                </div>
                <div style="background: rgba(0, 240, 255, 0.25); border: 1px solid #00f0ff; border-radius: 6px; padding: 8px 10px; font-size: 0.76rem; color: #00f0ff; font-weight: 700; animation: dispatchPulse 2s infinite;">
                    ⏳ 4. 全渠道并发推送中...
                </div>
            </div>
        </div>
    `;
};

/**
 * 切换分发账本与异常死信 Sub-Tab
 */
window.switchDispatchSubTab = function (tabName, shouldScroll = false) {
    window.currentDispatchSubTab = tabName;

    const btnLedger = document.getElementById('tab-btn-ledger');
    const btnDead = document.getElementById('tab-btn-deadletter');
    const boxLedger = document.getElementById('dispatch-ledger-container');
    const boxDead = document.getElementById('dispatch-deadletter-container');
    const btnBatchRetry = document.getElementById('btn-batch-retry-all');

    if (btnLedger) btnLedger.classList.toggle('active', tabName === 'ledger');
    if (btnDead) btnDead.classList.toggle('active', tabName === 'deadletter');

    if (boxLedger) boxLedger.style.display = (tabName === 'ledger') ? 'block' : 'none';
    if (boxDead) boxDead.style.display = (tabName === 'deadletter') ? 'flex' : 'none';

    if (btnBatchRetry) {
        btnBatchRetry.style.display = (tabName === 'deadletter') ? 'inline-flex' : 'none';
    }

    const data = window._lastDispatchOverview || {};
    if (tabName === 'ledger') {
        if (typeof window.renderDispatchLedger === 'function') {
            window.renderDispatchLedger(data.recent_records || []);
        }
    } else if (tabName === 'deadletter') {
        if (typeof window.renderDispatchDeadLetters === 'function') {
            window.renderDispatchDeadLetters(data.dead_letter_tasks || []);
        }
    }
};
