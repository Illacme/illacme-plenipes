window.currentDispatchMode = window.currentDispatchMode || 'hosting';
window.currentDispatchSubTab = 'ledger';
const _isHostingTarget = (t) => {
    if (!t) return false;
    if (t.target_type === 'hosting' || t.type === 'hosting') return true;
    const tid = String(t.target_id || t.id || '').trim().toLowerCase();
    return ['github_pages', 'cloudflare_pages', 'vercel', 'netlify', 'sftp', 'render', 'railway', 'zeabur', 'supabase', 'aws_s3', 'oss', 'cos', 'upyun_uss', 'gitee_pages', 'gitlab_pages', 'coding_pages', 'firebase'].includes(tid);
};
window._dispatchLedgerPollingTimer = null;
window._dispatchActiveRunningSet = window._dispatchActiveRunningSet || new Set();
window._dispatchRecentlyCompletedSet = window._dispatchRecentlyCompletedSet || new Set();
window._dispatchTaskStartTimes = window._dispatchTaskStartTimes || new Map();

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
            const recordsMap = new Map((res.recent_records || []).map(s => [`${s.rel_path}::${s.target_id}`, s]));
            const now = Date.now();

            if (window._dispatchActiveRunningSet.size > 0) {
                for (const key of Array.from(window._dispatchActiveRunningSet)) {
                    const r = recordsMap.get(key);
                    const startTime = window._dispatchTaskStartTimes.get(key) || 0;
                    const elapsed = now - startTime;

                    if (deadLetterKeys.has(key)) {
                        window._dispatchActiveRunningSet.delete(key);
                        window._dispatchTaskStartTimes.delete(key);
                        const parts = key.split('::');
                        if (window.DispatchCooldownManager && parts.length === 2) {
                            window.DispatchCooldownManager.clearCooldown(parts[0], parts[1]);
                        }
                    } else if (r) {
                        const isFailed = (r.status === 'failed' || Boolean(r.error || r.last_error));
                        const isSyncing = (r.status === 'syncing');

                        if (isSyncing) {
                            // 任务仍在后台编译、上传或请求中，保持轮询
                            continue;
                        } else if (isFailed) {
                            window._dispatchActiveRunningSet.delete(key);
                            window._dispatchTaskStartTimes.delete(key);
                            if (window.DispatchCooldownManager) {
                                window.DispatchCooldownManager.clearCooldown(r.rel_path, r.target_id);
                            }
                            if (typeof showToast === 'function') {
                                const errMsg = (r.diagnostic && r.diagnostic.friendly_message) || r.error || '推流未成功，请查看诊断';
                                showToast(`⚠️ [${(r.target_id || '').toUpperCase()}] 分发失败: ${errMsg}`, 'error');
                            }
                        } else if (r.status === 'success' && !r.is_stale) {
                            window._dispatchActiveRunningSet.delete(key);
                            window._dispatchTaskStartTimes.delete(key);
                            window._dispatchRecentlyCompletedSet.add(key);
                            setTimeout(() => {
                                if (window._dispatchRecentlyCompletedSet) {
                                    window._dispatchRecentlyCompletedSet.delete(key);
                                }
                            }, 4000);
                            if (typeof showToast === 'function') {
                                showToast(`✅ [${(r.target_id || '').toUpperCase()}] 广播推流完成，账本已同步！`, 'success');
                            }
                        } else if (elapsed > 40000) {
                            // 超时 40 秒安全保底解冻
                            window._dispatchActiveRunningSet.delete(key);
                            window._dispatchTaskStartTimes.delete(key);
                        }
                    } else if (elapsed > 40000) {
                        window._dispatchActiveRunningSet.delete(key);
                        window._dispatchTaskStartTimes.delete(key);
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
    }, 2000);
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

            // 更新社媒徽章数字 (严格仅统计社媒物权分发任务总数)
            const badgeSocial = document.getElementById('badge-social-tasks');
            if (badgeSocial) {
                const sTotal = (res.recent_records || []).filter(r => !_isHostingTarget(r)).length + (res.dead_letter_tasks || []).filter(d => !_isHostingTarget(d)).length;
                badgeSocial.innerText = `${sTotal}`;
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

    const viewH = document.getElementById('dispatch-hosting-view'), viewS = document.getElementById('dispatch-social-view');
    if (viewH) viewH.style.display = isHosting ? 'block' : 'none';
    if (viewS) viewS.style.display = !isHosting ? 'block' : 'none';

    const metricGrid = document.getElementById('dispatch-metric-container');
    if (metricGrid) metricGrid.style.display = isHosting ? 'none' : 'grid';

    const dock = document.getElementById('dispatch-pagination-dock');
    if (dock) dock.style.display = (!isHosting && window._dispatchPagination && window._dispatchPagination.total > 0) ? 'flex' : 'none';

    const btnAct = document.getElementById('btn-dispatch-primary-action');
    if (btnAct) btnAct.innerHTML = isHosting ? '<span class="btn-icon">🚀</span> 部署当前整站' : '<span class="btn-icon">🚀</span> 触发全域发布';

    if (isHosting) {
        if (reloadHosting && typeof window.loadHostingDeployCenter === 'function') window.loadHostingDeployCenter();
    } else {
        const unified = window.buildUnifiedDispatchTasks(window._lastDispatchOverview);
        if (typeof window.renderDispatchLedger === 'function') window.renderDispatchLedger(unified);
    }
};

window.refreshCurrentDispatchView = function () {
    if (window.currentDispatchMode === 'hosting' && typeof window.loadHostingDeployCenter === 'function') window.loadHostingDeployCenter();
    window.loadDispatchCenter();
};

window.onDispatchPrimaryAction = function () {
    if (window.currentDispatchMode === 'hosting') {
        if (typeof window.triggerFullHostingDeploy === 'function') window.triggerFullHostingDeploy();
    } else if (typeof window.triggerPublish === 'function') {
        window.triggerPublish(false);
    }
};

window.buildUnifiedDispatchTasks = function (overview) {
    const rawSuccess = (overview && Array.isArray(overview.recent_records)) ? overview.recent_records : [];
    const rawDead = (overview && Array.isArray(overview.dead_letter_tasks)) ? overview.dead_letter_tasks : [];
    const successList = rawSuccess.filter(s => !_isHostingTarget(s));
    const deadList = rawDead.filter(d => !_isHostingTarget(d));
    const unified = [
        ...deadList.map(d => ({ ...d, status: 'failed', time_sort: d.failed_at || d.updated_at || '', display_time: d.failed_at || d.updated_at || '' })),
        ...successList.map(s => ({ ...s, status: s.status || (s.error ? 'failed' : 'success'), time_sort: s.updated_at || '', display_time: s.updated_at || '' }))
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
    const rawSuccess = (data && Array.isArray(data.recent_records)) ? data.recent_records : [];
    const rawDead = (data && Array.isArray(data.dead_letter_tasks)) ? data.dead_letter_tasks : [];
    const sRecords = rawSuccess.filter(r => !_isHostingTarget(r)), sDeads = rawDead.filter(d => !_isHostingTarget(d));
    const totalSyndicated = sRecords.length, totalFailed = sDeads.length;
    const successRate = (totalSyndicated + totalFailed > 0) ? `${((totalSyndicated / (totalSyndicated + totalFailed)) * 100).toFixed(1)}%` : '100.0%';
    const socialChannels = ((data && data.channel_health) || []).filter(c => !_isHostingTarget(c)), enabledChannels = socialChannels.filter(c => c.enabled);

    const setTxt = (id, txt) => { const el = document.getElementById(id); if (el) el.innerText = txt; };
    setTxt('metric-total-syndicated', totalSyndicated);
    setTxt('metric-success-rate', `分发成功率 ${successRate}`);
    setTxt('metric-active-count', (data && data.is_publishing) ? 1 : 0);
    setTxt('metric-total-failed', totalFailed);
    setTxt('metric-channels-count', `${enabledChannels.length} / ${socialChannels.length}`);
    setTxt('metric-channels-sub', `已激活 ${enabledChannels.length} 个渠道 · 点击配置 ↗`);

    const elActiveSub = document.getElementById('metric-active-sub');
    if (elActiveSub) {
        elActiveSub.innerText = data.is_publishing ? '正在并发分发中' : '管线就绪待命';
        elActiveSub.style.color = data.is_publishing ? 'var(--neon-cyan)' : 'var(--text-muted)';
    }
    const elFailedSub = document.getElementById('metric-failed-sub');
    if (elFailedSub) {
        elFailedSub.innerText = (totalFailed > 0) ? '需前往自愈修复' : '0 待修死信';
        elFailedSub.style.color = (totalFailed > 0) ? 'var(--text-danger)' : 'var(--neon-green)';
    }
    const liveBadge = document.getElementById('dispatch-live-badge');
    if (liveBadge) {
        liveBadge.innerText = data.is_publishing ? '⏳ 发布中...' : '● 系统就绪';
        liveBadge.className = data.is_publishing ? 'dispatch-mode-badge badge is-publishing' : 'dispatch-mode-badge badge active';
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
                <button class="secondary-btn danger" onclick="if(typeof window.abortSync==='function') window.abortSync();" style="padding: 5px 14px; font-size: 0.8rem;">🛑 紧急中止当前发布</button>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 8px;">
                <div style="background: rgba(0, 240, 255, 0.12); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 6px; padding: 8px 10px; font-size: 0.76rem; color: var(--text-main);">✅ 1. 原稿排版与清洗</div>
                <div style="background: rgba(0, 240, 255, 0.12); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 6px; padding: 8px 10px; font-size: 0.76rem; color: var(--text-main);">✅ 2. AI 译文与词库对齐</div>
                <div style="background: rgba(0, 240, 255, 0.12); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 6px; padding: 8px 10px; font-size: 0.76rem; color: var(--text-main);">✅ 3. 静态装帧主题构建</div>
                <div style="background: rgba(0, 240, 255, 0.22); border: 1px solid var(--neon-cyan); border-radius: 6px; padding: 8px 10px; font-size: 0.76rem; color: var(--neon-cyan); font-weight: 700; animation: dispatchPulse 2s infinite;">⏳ 4. 全渠道并发推送中...</div>
            </div>
        </div>`;
};

window.switchDispatchSubTab = function (tabName) {
    window.currentDispatchSubTab = tabName;
    if (tabName === 'deadletter') window.quickFilterDispatchStatus('failed');
    else if (tabName === 'ledger') window.quickFilterDispatchStatus('success');
    else window.quickFilterDispatchStatus('');
};
