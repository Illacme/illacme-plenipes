/**
 * 🚀 [V125.0] Illacme Plenipes - Dispatch Full Workbench Component
 * 职责：全域发布任务大厅双模式（全站托管/社媒分发）数据调度、指标卡片与流式轮询。
 * 🛡️ [SOP-02 模块拆分] 单文件严格保持在 300 行以内。
 */

window.currentDispatchMode = window.currentDispatchMode || 'hosting';
window.currentDispatchSubTab = 'ledger';

// ==========================================
// 🌊 流式呼吸感知与自动无感轮询中枢
// ==========================================
window._dispatchLedgerPollingTimer = null;
window._dispatchActiveRunningSet = window._dispatchActiveRunningSet || new Set();
window._dispatchRecentlyCompletedSet = window._dispatchRecentlyCompletedSet || new Set();

window.startDispatchLedgerPolling = function () {
    if (window._dispatchLedgerPollingTimer) return;

    window._dispatchLedgerPollingTimer = setInterval(async () => {
        const viewTasks = document.getElementById('view-tasks');
        const isTasksActive = viewTasks && (viewTasks.classList.contains('active') || viewTasks.style.display !== 'none');
        if (!isTasksActive) {
            window.stopDispatchLedgerPolling();
            return;
        }

        try {
            if (typeof apiFetch !== 'function') return;
            const res = await apiFetch('/api/dispatch/overview');
            if (!res || res.status !== 'success') return;

            const isPublishing = Boolean(res.is_publishing);
            const deadLetterKeys = new Set((res.dead_letter_tasks || []).map(t => `${t.rel_path}::${t.target_id}`));
            const successKeys = new Set((res.recent_records || []).map(s => `${s.rel_path}::${s.target_id}`));

            if (window._dispatchActiveRunningSet.size > 0) {
                for (const key of window._dispatchActiveRunningSet) {
                    if (successKeys.has(key)) {
                        window._dispatchActiveRunningSet.delete(key);
                        window._dispatchRecentlyCompletedSet.add(key);
                        setTimeout(() => window._dispatchRecentlyCompletedSet.delete(key), 4000);
                    } else if (deadLetterKeys.has(key)) {
                        window._dispatchActiveRunningSet.delete(key);
                    }
                }
            }

            window._lastDispatchOverview = res;
            window.renderDispatchMetrics(res);
            window.renderActivePipelineZone(res);
            if (typeof window.updateDispatchIndicator === 'function') window.updateDispatchIndicator(res);

            if (window.currentDispatchMode === 'hosting') {
                if (typeof window.loadHostingDeployCenter === 'function') window.loadHostingDeployCenter();
            } else {
                const unified = window.buildUnifiedDispatchTasks(res);
                if (typeof window.renderDispatchLedger === 'function') window.renderDispatchLedger(unified);
            }

            if (!isPublishing && window._dispatchActiveRunningSet.size === 0) {
                window.stopDispatchLedgerPolling();
            }
        } catch (e) {
            console.warn('[Dispatch Polling] Skipped:', e);
        }
    }, 3000);
};

window.stopDispatchLedgerPolling = function () {
    if (window._dispatchLedgerPollingTimer) {
        clearInterval(window._dispatchLedgerPollingTimer);
        window._dispatchLedgerPollingTimer = null;
    }
};

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
            window.renderActivePipelineZone(res);
            if (typeof window.updateDispatchIndicator === 'function') window.updateDispatchIndicator(res);

            // 更新社媒徽章数字
            const badgeSocial = document.getElementById('badge-social-tasks');
            if (badgeSocial) {
                const totalSocial = ((res.recent_records || []).length) + ((res.dead_letter_tasks || []).length);
                badgeSocial.innerText = `${totalSocial}`;
            }

            // 保持当前模式渲染（确保初次进入托管模式能自动加载全站部署中心数据）
            const targetMode = window.currentDispatchMode || 'hosting';
            window.switchDispatchMode(targetMode, targetMode === 'hosting');

            if (res.is_publishing || window._dispatchActiveRunningSet.size > 0) {
                window.startDispatchLedgerPolling();
            } else {
                window.stopDispatchLedgerPolling();
            }
        }
    } catch (err) {
        console.error("🛑 加载全域发布大厅失败:", err);
    }
};

/**
 * 切换全站托管部署 / 社交媒体分发双模式
 */
window.switchDispatchMode = function (mode, reloadHosting = true) {
    window.currentDispatchMode = mode || 'hosting';
    const isHosting = (window.currentDispatchMode === 'hosting');

    const tabH = document.getElementById('tab-dispatch-hosting') || document.getElementById('pill-dispatch-hosting');
    const tabS = document.getElementById('tab-dispatch-social') || document.getElementById('pill-dispatch-social');
    if (tabH) tabH.classList.toggle('active', isHosting);
    if (tabS) tabS.classList.toggle('active', !isHosting);

    const viewH = document.getElementById('dispatch-hosting-view');
    const viewS = document.getElementById('dispatch-social-view');
    if (viewH) viewH.style.display = isHosting ? 'block' : 'none';
    if (viewS) viewS.style.display = !isHosting ? 'block' : 'none';

    const metricGrid = document.getElementById('dispatch-metric-container');
    if (metricGrid) metricGrid.style.display = isHosting ? 'none' : 'grid';

    const dock = document.getElementById('dispatch-pagination-dock');
    if (dock) dock.style.display = (!isHosting && window._dispatchPagination && window._dispatchPagination.total > 0) ? 'flex' : 'none';

    const btnAct = document.getElementById('btn-dispatch-primary-action');
    if (btnAct) {
        btnAct.innerHTML = isHosting
            ? '<span class="btn-icon">🚀</span> 部署当前整站'
            : '<span class="btn-icon">🚀</span> 触发全域发布';
    }

    if (isHosting) {
        if (reloadHosting && typeof window.loadHostingDeployCenter === 'function') {
            window.loadHostingDeployCenter();
        }
    } else {
        const unified = window.buildUnifiedDispatchTasks(window._lastDispatchOverview);
        if (typeof window.renderDispatchLedger === 'function') {
            window.renderDispatchLedger(unified);
        }
    }
};

window.refreshCurrentDispatchView = function () {
    if (window.currentDispatchMode === 'hosting' && typeof window.loadHostingDeployCenter === 'function') {
        window.loadHostingDeployCenter();
    }
    window.loadDispatchCenter();
};

window.onDispatchPrimaryAction = function () {
    if (window.currentDispatchMode === 'hosting') {
        if (typeof window.triggerFullHostingDeploy === 'function') {
            window.triggerFullHostingDeploy();
        }
    } else {
        if (typeof window.triggerPublish === 'function') {
            window.triggerPublish(false);
        }
    }
};

window.buildUnifiedDispatchTasks = function (overview) {
    const successList = (overview && Array.isArray(overview.recent_records)) ? overview.recent_records : [];
    const deadList = (overview && Array.isArray(overview.dead_letter_tasks)) ? overview.dead_letter_tasks : [];
    const unified = [
        ...deadList.map(d => ({ ...d, status: 'failed', time_sort: d.failed_at || d.updated_at || '', display_time: d.failed_at || d.updated_at || '' })),
        ...successList.map(s => ({ ...s, status: 'success', time_sort: s.updated_at || '', display_time: s.updated_at || '' }))
    ];
    unified.sort((a, b) => (b.time_sort || '').localeCompare(a.time_sort || ''));
    return unified;
};

window.quickFilterDispatchStatus = function (status) {
    const sel = document.getElementById('dispatch-filter-status');
    if (sel) {
        sel.value = status || '';
        if (typeof window.filterDispatchLedger === 'function') window.filterDispatchLedger();
    }
};

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
        elActiveSub.style.color = data.is_publishing ? 'var(--neon-cyan)' : 'var(--text-muted)';
    }
    if (elFailed) elFailed.innerText = summary.total_failed ?? 0;
    if (elFailedSub) {
        elFailedSub.innerText = (summary.total_failed > 0) ? '需前往自愈修复' : '0 待修死信';
        elFailedSub.style.color = (summary.total_failed > 0) ? 'var(--text-danger)' : 'var(--neon-green)';
    }
    if (elChannels) elChannels.innerText = `${enabledChannels.length} / ${channelHealth.length}`;
    if (elChannelsSub) elChannelsSub.innerText = `已激活 ${enabledChannels.length} 个渠道 · 点击配置 ↗`;

    // 动态同步更新算力中心风格的顶部态势勋章
    const liveBadge = document.getElementById('dispatch-live-badge');
    if (liveBadge) {
        if (data.is_publishing) {
            liveBadge.innerText = '⏳ 发布中...';
            liveBadge.className = 'dispatch-mode-badge badge is-publishing';
        } else {
            liveBadge.innerText = '● 系统就绪';
            liveBadge.className = 'dispatch-mode-badge badge active';
        }
    }
};

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
                        <span style="font-weight: 800; font-size: 0.95rem; color: var(--neon-cyan);">发布任务正在执行中</span>
                        <span style="font-size: 0.76rem; color: var(--text-muted); margin-left: 8px;">(多渠道内容正在同步推送)</span>
                    </div>
                </div>
                <button class="secondary-btn danger" onclick="if(typeof window.abortSync==='function') window.abortSync();" style="padding: 5px 14px; font-size: 0.8rem;">
                    🛑 紧急中止当前发布
                </button>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 8px;">
                <div style="background: rgba(0, 240, 255, 0.12); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 6px; padding: 8px 10px; font-size: 0.76rem; color: var(--text-main);">✅ 1. 原稿排版与清洗</div>
                <div style="background: rgba(0, 240, 255, 0.12); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 6px; padding: 8px 10px; font-size: 0.76rem; color: var(--text-main);">✅ 2. AI 译文与词库对齐</div>
                <div style="background: rgba(0, 240, 255, 0.12); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 6px; padding: 8px 10px; font-size: 0.76rem; color: var(--text-main);">✅ 3. 静态装帧主题构建</div>
                <div style="background: rgba(0, 240, 255, 0.22); border: 1px solid var(--neon-cyan); border-radius: 6px; padding: 8px 10px; font-size: 0.76rem; color: var(--neon-cyan); font-weight: 700; animation: dispatchPulse 2s infinite;">⏳ 4. 全渠道并发推送中...</div>
            </div>
        </div>
    `;
};

window.switchDispatchSubTab = function (tabName) {
    window.currentDispatchSubTab = tabName;
    if (tabName === 'deadletter') {
        window.quickFilterDispatchStatus('failed');
    } else if (tabName === 'ledger') {
        window.quickFilterDispatchStatus('success');
    } else {
        window.quickFilterDispatchStatus('');
    }
};
