/**
 * 🚀 [V122.0] Illacme Plenipes - Dispatch Indicator Component
 * 职责：顶部导航右上角发布任务指示徽章生命周期、轮询与状态更新。
 * 🛡️ [SOP-02 模块拆分] 单文件严格保持在 300 行以内。
 */

window._dispatchIndicatorState = {
    isPublishing: false,
    failedCount: 0,
    activeCount: 0,
    lastUpdate: 0
};

/**
 * 更新右上角指示徽章外观与文案
 */
window.updateDispatchIndicator = function (overviewData) {
    const btn = document.getElementById('btn-dispatch-center');
    const label = document.getElementById('dispatch-indicator-text');
    const pill = document.getElementById('dispatch-indicator-pill');
    if (!btn || !label || !pill) return;

    const summary = (overviewData && overviewData.summary) || {};
    const fullSiteState = window._fullSitePublishState || {};
    const isPublishing = Boolean(overviewData && overviewData.is_publishing) || Boolean(fullSiteState.isPublishing) || Boolean(window._isPublishPreviewActive);
    const failedCount = Number(summary.total_failed || 0);
    const activeCount = Number(summary.active_count || 0);

    window._dispatchIndicatorState = {
        isPublishing,
        failedCount,
        activeCount,
        lastUpdate: Date.now()
    };

    // 移除历史状态类
    btn.classList.remove('is-running', 'is-warning');

    if (isPublishing) {
        btn.classList.add('is-running');
        label.innerText = fullSiteState.isPublishing ? '全站发布中' : '正在分发';
        pill.className = 'indicator-pill';
        if (fullSiteState.isPublishing && fullSiteState.stage > 0 && fullSiteState.stage <= 4) {
            pill.innerText = `步骤 ${fullSiteState.stage}/4`;
        } else {
            pill.innerText = activeCount > 0 ? `${activeCount} 篇` : '进行中';
        }
        pill.style.display = 'inline-block';
        btn.title = '全站发布正在执行中，点击查看实时流水线与步骤进度';
    } else if (failedCount > 0) {
        btn.classList.add('is-warning');
        label.innerText = '分发待自愈';
        pill.className = 'indicator-pill';
        pill.innerText = `${failedCount} 项`;
        pill.style.display = 'inline-block';
        btn.title = `探测到 ${failedCount} 项分发异常，点击进入自愈站`;
    } else {
        label.innerText = '任务进度';
        pill.className = 'indicator-pill ready-dot';
        pill.innerText = '';
        pill.style.display = 'inline-block';
        const total = summary.total_syndicated ? Number(summary.total_syndicated) : 0;
        btn.title = `分发管线就绪，已累计交付 ${total} 项成果 (点击查看流水明细)`;
    }
};

/**
 * 异步从后端拉取轻量总览并刷新指示器
 */
window.refreshDispatchIndicator = async function () {
    try {
        if (typeof apiFetch !== 'function') return;
        const [res, syncRes] = await Promise.all([
            apiFetch('/api/dispatch/overview').catch(() => null),
            apiFetch('/api/system/sync/status').catch(() => null)
        ]);

        if (syncRes && syncRes.is_publishing) {
            if (!window._fullSitePublishState) window._fullSitePublishState = {};
            window._fullSitePublishState.isPublishing = true;
            if (!window._fullSitePublishState.stage || window._fullSitePublishState.stage === 0) {
                window._fullSitePublishState.stage = 2;
                window._fullSitePublishState.stageName = '正在编译';
            }
        } else if (syncRes && !syncRes.is_publishing && window._fullSitePublishState?.isPublishing) {
            window._fullSitePublishState.isPublishing = false;
            window._fullSitePublishState.stage = 5;
            window._fullSitePublishState.stageName = '发布完成';
        }

        if (res && res.status === 'success') {
            window._lastDispatchOverview = res;
            window.updateDispatchIndicator(res);
            if (typeof window.renderPopoverContent === 'function' && window._isPopoverOpen) {
                window.renderPopoverContent(res);
            }
        } else if (window._fullSitePublishState?.isPublishing) {
            window.updateDispatchIndicator({});
        }
    } catch (e) {
        console.warn("⚠️ 刷新分发指示器跳过:", e);
    }
};

/**
 * 启动指示器轮询定时器
 */
window.startDispatchIndicatorPolling = function () {
    if (window._dispatchIndicatorTimer) {
        clearInterval(window._dispatchIndicatorTimer);
    }
    window._dispatchIndicatorTimer = setInterval(() => {
        if (typeof document !== 'undefined' && document.hidden) {
            return;
        }
        window.refreshDispatchIndicator();
    }, 6000);
};

/**
 * 停止指示器轮询定时器
 */
window.stopDispatchIndicatorPolling = function () {
    if (window._dispatchIndicatorTimer) {
        clearInterval(window._dispatchIndicatorTimer);
        window._dispatchIndicatorTimer = null;
    }
};

/**
 * 初始化指示器轮询定时器与页面可见性感知
 */
window.initDispatchIndicator = function () {
    // 首次拉取
    window.refreshDispatchIndicator();

    // 启动定时轮询
    window.startDispatchIndicatorPolling();

    // 页面可见性挂起（节约后台能耗与网络流量）
    if (typeof document !== 'undefined' && !window._dispatchVisibilityBound) {
        window._dispatchVisibilityBound = true;
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                window.stopDispatchIndicatorPolling();
            } else {
                window.refreshDispatchIndicator();
                window.startDispatchIndicatorPolling();
            }
        });
    }
};

// 页面加载完成后挂载自启
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(window.initDispatchIndicator, 1000);
    });
}

