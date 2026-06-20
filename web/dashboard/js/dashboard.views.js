/**
 * 🌌 [V57.0] Illacme Plenipes View Orchestrator
 * 职责：动态渲染顶级视图面板，实现 index.html 的物理瘦身。
 */

// Templates have been extracted to dashboard.templates.js to comply with SOP-02.

/**
 * 初始化所有视图容器
 */
window.initViewContainers = () => {
    const viewport = document.getElementById('main-viewport');
    if (!viewport) return;
    viewport.innerHTML = Object.values(window.viewTemplates).join('');
};

// ==========================================
// 🚀 [V74.15] 核心视图导航与物理 Hash 路由逻辑
// ==========================================
// ==========================================
// 🛡️ [V87.0] 物理 UI 切换（仅执行 DOM 样式操作，不触发慢速 API 请求）
// ==========================================
window.switchViewDOM = (viewId) => {
    // 🛡️ P0 修复：离开 overview 时立即暂停星系 WebGL 渲染，减轻 GPU 负载
    if (viewId !== 'overview' && typeof window.pauseGalaxy === 'function') {
        window.pauseGalaxy();
    }

    window.currentView = viewId;
    if (window.location.hash !== `#/${viewId}`) {
        window.location.hash = `#/${viewId}`;
    }
    const panels = document.querySelectorAll('.view-panel');
    const navItems = document.querySelectorAll('.nav-item');
    panels.forEach(p => p.classList.remove('active'));
    navItems.forEach(n => n.classList.remove('active'));
    
    const activePanel = document.getElementById(`view-${viewId}`);
    const activeNav = document.getElementById(`nav-${viewId}`);
    if (activePanel) activePanel.classList.add('active');
    if (activeNav) activeNav.classList.add('active');
    
    if (typeof window.addAudit === 'function') {
        window.addAudit(`📡 导航: ${viewId.toUpperCase()}`);
    }
};

// ==========================================
// 🛡️ [V87.0] 数据加载（与 UI 切换动画解耦，在动画结束后异步执行）
// ==========================================
window.loadViewData = (viewId, subId) => {
    console.log(`📥 [Views] 开始为视图 ${viewId} 加载数据...`);
    if (viewId === 'vault' && typeof loadVault === 'function') loadVault();
    if (viewId === 'compute' && typeof loadComputeCenter === 'function') loadComputeCenter(subId);
    if (viewId === 'plugins' && typeof loadPlugins === 'function') loadPlugins();
    if (viewId === 'settings' && typeof loadSettings === 'function') {
        const target = subId || 'general';
        console.log(`🛰️ [导航对正] 定位设置子页: ${target}`);
        loadSettings(target);
        if (typeof loadPlugins === 'function') loadPlugins();
    }
    if (viewId === 'overview') {
        // 🛡️ P0 修复：进入 overview 时恢复星系 WebGL 渲染
        if (typeof window.resumeGalaxy === 'function') {
            window.resumeGalaxy();
        }
        if (typeof refreshGalaxy === 'function') {
            refreshGalaxy();
        }
    }
    if (viewId === 'tower' && typeof loadTowerCenter === 'function') loadTowerCenter();
    if (viewId === 'analytics' && typeof loadAnalyticsCenter === 'function') loadAnalyticsCenter();
};

// ==========================================
// 🚀 [V87.0] 统一视图切换入口（使用 View Transitions 解耦数据加载）
// ==========================================
window.showView = (id, subId) => {
    if (subId) window.pendingSubView = subId;
    else window.pendingSubView = null; // Fix for stale subId bleeding
    const container = document.querySelector('main');
    
    const executeDOMChange = () => {
        window.switchViewDOM(id);
    };

    const executeDataLoad = () => {
        window.loadViewData(id, subId);
    };

    if (document.startViewTransition) {
        if (typeof window.triggerSystemPulse === 'function') window.triggerSystemPulse();
        const transition = document.startViewTransition(() => {
            executeDOMChange();
        });
        // 🛡️ P1 修复：在 View Transition 动画彻底结束（finished）后再触发慢速 API 数据加载
        transition.finished.then(() => {
            executeDataLoad();
        }).catch((err) => {
            console.warn("⚠️ View transition transition.finished rejected or cancelled, load data fallback:", err);
            executeDataLoad();
        });
    } else {
        // 兜底降级：对于不支持的浏览器，继续走老的 setTimeout 动画
        if (container) {
            container.classList.add('switching-view');
            if (typeof window.triggerSystemPulse === 'function') window.triggerSystemPulse();
            setTimeout(() => {
                executeDOMChange();
                container.classList.remove('switching-view');
                executeDataLoad();
            }, 300);
        } else {
            executeDOMChange();
            executeDataLoad();
        }
    }
};

window.handleRouting = () => {
    const hash = window.location.hash.replace('#/', '');
    const validViews = ['overview', 'vault', 'compute', 'plugins', 'settings', 'tower', 'analytics'];
    if (hash && validViews.includes(hash)) {
        if (window.currentView === hash) return; // Prevent duplicate execution from programmatic hash changes
        const subId = window.pendingSubView;
        window.pendingSubView = null;
        window.showView(hash, subId);
        if (hash === 'overview' && typeof window.toggleHub === 'function') window.toggleHub('show');
    } else {
        window.showView('overview');
        if (typeof window.toggleHub === 'function') window.toggleHub('show');
    }
};
window.addEventListener('hashchange', window.handleRouting);
