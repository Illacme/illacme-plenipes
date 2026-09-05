/**
 * 🚀 [V120.0] Illacme Plenipes - 出版工作台 (Launchpad) 智能飞行指挥中心 Hub
 * 架构职责：判断用户状态与会话偏好，动态调度渲染「首次引导向导」或「智能仪表盘」主 Hub 门面控制器 (SOP-02 物理拆分微步演进)
 * 核心原则：零新轮子——所有操作入口 100% 调用已有全局函数；绝对尊崇文库不可变绑定铁律。
 * 
 * 分片拓扑：
 * 1. launchpad.onboarding.js  - 首次启动双轨引导向导 (Onboarding) _renderOnboarding
 * 2. launchpad.skeleton.js    - 三栏合一顶栏 Trio Bar 骨架构建、公网独立站链接复制 _mountLaunchpadSkeleton / copySiteUrlSafe
 * 3. launchpad.pipeline.js    - 流水线六节点透视 _buildPipelineRow 与出版就绪诊断卡片 _buildSuggestions
 * 4. launchpad.dashboard.js   - 日常智能仪表盘 _renderDashboard、指标统计条 _buildStatsStrip 与核心快捷操作 _buildQuickActions
 */

var shardFiles = [
    "launchpad.onboarding.js",
    "launchpad.skeleton.js",
    "launchpad.pipeline.js",
    "launchpad.dashboard.js"
];

// 🛡️ Node.js 测试沙箱环境下的子分片自动装配 (防单测直接 eval launchpad.js 遗漏子函数)
if (typeof require === 'function' || typeof fs !== 'undefined') {
    try {
        var _fs = (typeof fs !== 'undefined') ? fs : require('fs');
        var _path = (typeof path !== 'undefined') ? path : (typeof require === 'function' ? require('path') : null);
        var dir = (typeof __dirname !== 'undefined') ? __dirname : 'web/dashboard/js/ui/launchpad_shards';
        shardFiles.forEach(function (s) {
            var target = _path ? _path.join(dir, s) : (dir + '/' + s);
            if (_fs.existsSync(target)) {
                eval(_fs.readFileSync(target, 'utf8'));
            }
        });
    } catch (e) {
        // 静默忽略非 Node/fs 环境
    }
}

// 作用域桥接（保证 new Function 沙箱中直接可寻址）
var _renderOnboarding = window._renderOnboarding;
var _mountLaunchpadSkeleton = window._mountLaunchpadSkeleton;
var _renderDashboard = window._renderDashboard;
var _updateSiteLinkContainer = window._updateSiteLinkContainer;
var _buildSiteLinkHtml = window._buildSiteLinkHtml;

/**
 * 模式切换总入口：支持在仪表盘与向导之间自由穿梭。
 */
window.switchLaunchpadMode = function (mode) {
    sessionStorage.setItem('_illacme_launchpad_mode', mode);
    var subview = document.getElementById('hub-mode-subview');
    var siteWrap = document.getElementById('hub-site-link-container');
    var capsuleBtns = document.querySelectorAll('.hub-capsule-btn');

    capsuleBtns.forEach(function (btn) {
        if (btn.dataset.mode === mode) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    if (mode === 'onboarding') {
        if (siteWrap) siteWrap.style.display = 'none';
        if (subview && typeof window._renderOnboarding === 'function') {
            window._renderOnboarding(subview, window.governanceContext);
        }
    } else {
        if (siteWrap) siteWrap.style.display = 'inline-flex';
        if (subview && typeof window._renderDashboard === 'function') {
            window._renderDashboard(subview, window.governanceContext);
        }
    }
};

/**
 * 弹窗顶栏品牌切换处理：彻底隔离数据并触发全域热更。
 */
window.handleLaunchpadImprintChange = async function (newImprintId) {
    if (!newImprintId) return;
    if (typeof window.switchImprint === 'function') {
        try {
            await window.switchImprint(newImprintId);
        } catch (e) {
            console.warn('[Launchpad] switchImprint 执行异常:', e);
        }
    }
    // 彻底清空旧品牌的 context 缓存，防跨品牌数据串门
    window.governanceContext = null;
    try {
        if (typeof apiFetch === 'function') {
            var freshCtx = await apiFetch('/api/system/context');
            window.governanceContext = freshCtx;
            var subview = document.getElementById('hub-mode-subview');
            if (subview && typeof window._renderDashboard === 'function') {
                window._renderDashboard(subview, freshCtx);
            }
            // 刷新外链
            if (typeof window._updateSiteLinkContainer === 'function') {
                window._updateSiteLinkContainer();
            }
        }
    } catch (err) {
        console.warn('[Launchpad] 切换品牌后刷新上下文失败:', err);
    }
};

/**
 * 每次打开出版工作台时调用，自动装配并判断模式。
 */
window.initLaunchpad = async function () {
    var area = document.getElementById('hub-dynamic-area');
    if (!area) return;

    // 先用缓存的 context 快速渲染首屏，避免白屏闪烁
    var ctx = window.governanceContext;

    if (!ctx && typeof apiFetch === 'function') {
        try {
            ctx = await apiFetch('/api/system/context');
            window.governanceContext = ctx;
        } catch (e) {
            console.warn('[Launchpad] context fetch failed, using dashboard fallback.', e);
        }
    }

    // 首屏数据就绪安全判定：检查品牌列表
    var imprints = (window.settingsData && window.settingsData._imprints) || (ctx && ctx.imprints) || [];
    var savedMode = sessionStorage.getItem('_illacme_launchpad_mode');
    var defaultMode = (imprints.length === 0 || (ctx && ctx.onboarding_required)) ? 'onboarding' : 'dashboard';
    var activeMode = savedMode || defaultMode;

    // 装配三栏合一顶栏结构与子视图挂载点
    if (typeof window._mountLaunchpadSkeleton === 'function') {
        window._mountLaunchpadSkeleton(area, activeMode);
    }

    var subview = document.getElementById('hub-mode-subview');
    if (subview) {
        if (activeMode === 'onboarding') {
            if (typeof window._renderOnboarding === 'function') {
                window._renderOnboarding(subview, ctx);
            }
        } else {
            if (typeof window._renderDashboard === 'function') {
                window._renderDashboard(subview, ctx);
            }
        }
    }

    // SWR 异步静默校准数据
    _refreshContextSilently();
};

/**
 * SWR 异步静默校准数据
 */
async function _refreshContextSilently() {
    if (typeof apiFetch !== 'function') return;
    try {
        var fresh = await apiFetch('/api/system/context');
        if (!fresh) return;
        window.governanceContext = fresh;
        var subview = document.getElementById('hub-mode-subview');
        var savedMode = sessionStorage.getItem('_illacme_launchpad_mode');
        if (subview && savedMode !== 'onboarding' && typeof window._renderDashboard === 'function') {
            window._renderDashboard(subview, fresh);
        }
    } catch (_) {}
    if (typeof window.refreshHealthMatrix === 'function') {
        window.refreshHealthMatrix();
    }
}

// 🌐 核心命名空间门面 (向后兼容与集中索引)
window.LaunchpadHub = {
    version: "120.0",
    shards: shardFiles,
    isLoaded: function () {
        return !!(
            window.switchLaunchpadMode &&
            window.initLaunchpad &&
            window._renderOnboarding &&
            window._mountLaunchpadSkeleton &&
            window._renderDashboard
        );
    }
};
