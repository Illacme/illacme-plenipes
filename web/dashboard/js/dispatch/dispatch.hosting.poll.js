/**
 * 🔄 [V125.3] Illacme Plenipes - Hosting Deploy Auto-Polling Shard
 * 职责：负责全站托管发布期间的状态自动侦测与高频自愈轮询，无需用户手动刷新页面。
 * 🛡️ [SOP-02 模块规范] 单文件严格保持在 300 行以内。
 */

window._hostingDeployPollingTimer = null;
window._hostingDeployPollingCount = 0;

/**
 * 启动全站托管专属高频轮询（每 2.5 秒侦测一次）
 */
window.startHostingDeployPolling = function () {
    if (window._hostingDeployPollingTimer) return;
    window._hostingDeployPollingCount = 0;

    window._hostingDeployPollingTimer = setInterval(async () => {
        window._hostingDeployPollingCount++;
        const container = document.getElementById('hosting-batch-container');
        const viewTasks = document.getElementById('view-tasks');
        const isTasksVisible = viewTasks && (viewTasks.classList.contains('active') || viewTasks.style.display !== 'none');

        // 若不在发布工作台或全站托管视图，暂停轮询避免无谓开销
        if (!container || !isTasksVisible) {
            window.stopHostingDeployPolling();
            return;
        }

        // 超时保底保护：最多连续轮询 60 次（约 150 秒）自动熔断
        if (window._hostingDeployPollingCount > 60) {
            window.stopHostingDeployPolling();
            return;
        }

        try {
            if (typeof apiFetch !== 'function') return;
            const res = await apiFetch('/api/dispatch/hosting/overview');
            if (!res || res.status !== 'success') return;

            window._lastHostingOverview = res;

            // 动态更新舰队网格与流水大表
            if (typeof window.renderHostingFleetGrid === 'function') {
                window.renderHostingFleetGrid(res.fleet || []);
            }
            if (typeof window.renderHostingBatchLedger === 'function') {
                window.renderHostingBatchLedger(res.batches || []);
            }

            // 若所有批次均已脱离 RUNNING/PENDING 态，自动闭环停止轮询
            const hasActiveDeploy = (res.batches || []).some(
                b => b && (b.overall_status === 'RUNNING' || b.overall_status === 'PENDING')
            );
            if (!hasActiveDeploy) {
                window.stopHostingDeployPolling();
            }
        } catch (e) {
            console.warn('[Hosting Poll] Skipped due to error:', e);
        }
    }, 2500);
};

/**
 * 停止全站托管轮询
 */
window.stopHostingDeployPolling = function () {
    if (window._hostingDeployPollingTimer) {
        clearInterval(window._hostingDeployPollingTimer);
        window._hostingDeployPollingTimer = null;
        window._hostingDeployPollingCount = 0;
    }
};
