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
    const isPublishing = Boolean(overviewData && overviewData.is_publishing);
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
        label.innerText = '正在分发';
        pill.innerText = activeCount > 0 ? `${activeCount} 篇` : '进行中';
        pill.style.display = 'inline-block';
        btn.title = '全域发布正在执行中，点击查看实时流水线';
    } else if (failedCount > 0) {
        btn.classList.add('is-warning');
        label.innerText = '分发待自愈';
        pill.innerText = `${failedCount} 项`;
        pill.style.display = 'inline-block';
        btn.title = `探测到 ${failedCount} 项分发异常，点击进入自愈站`;
    } else {
        label.innerText = '任务大厅';
        pill.innerText = summary.total_syndicated ? String(summary.total_syndicated) : '0';
        pill.style.display = 'inline-block';
        btn.title = '点击展开出版任务即时监视器';
    }
};

/**
 * 异步从后端拉取轻量总览并刷新指示器
 */
window.refreshDispatchIndicator = async function () {
    try {
        if (typeof apiFetch !== 'function') return;
        const res = await apiFetch('/api/dispatch/overview');
        if (res && res.status === 'success') {
            window._lastDispatchOverview = res;
            window.updateDispatchIndicator(res);
            if (typeof window.renderPopoverContent === 'function' && window._isPopoverOpen) {
                window.renderPopoverContent(res);
            }
        }
    } catch (e) {
        console.warn("⚠️ 刷新分发指示器跳过:", e);
    }
};

/**
 * 初始化指示器轮询定时器
 */
window.initDispatchIndicator = function () {
    // 首次拉取
    window.refreshDispatchIndicator();

    // 避免重复启动定时器
    if (window._dispatchIndicatorTimer) {
        clearInterval(window._dispatchIndicatorTimer);
    }
    window._dispatchIndicatorTimer = setInterval(() => {
        window.refreshDispatchIndicator();
    }, 6000);
};

// 页面加载完成后挂载自启
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(window.initDispatchIndicator, 1000);
    });
}
