/**
 * 🚀 Illacme Plenipes Dashboard Core - Hub & Overlay Shard
 * 职责：核心指挥覆盖层切换、品牌上下文下拉绑定与关闭按钮事件委派。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

// 辅助检测导览是否真正处于激活态 (严格双重物理校验：内存标志 + DOM 遮罩层)
const _isTourRealActive = () => {
    if (typeof window.isTourActive === 'function') return window.isTourActive();
    return !!(window._isTourActive && document.querySelector('.dashboard-tour-overlay'));
};

// 1. 核心指挥中枢控制 (全局单例)
window.toggleHub = (forceState) => {
    // 🛡️ 导览进行中守护：若处于导览态且非显式隐藏指令，重定向为唤起品牌下拉菜单，防止误唤起领航仪打断导览
    if (_isTourRealActive() && forceState !== 'hide') {
        if (typeof window.toggleImprintDropdown === 'function') {
            window.toggleImprintDropdown();
        }
        return;
    }

    const hub = document.getElementById('command-hub-overlay');
    if (!hub) return;

    // 强制状态或切换
    let willShow = false;
    if (forceState === 'show') {
        hub.style.display = 'flex';
        willShow = true;
    } else if (forceState === 'hide') {
        hub.style.display = 'none';
    } else {
        const isHidden = window.getComputedStyle(hub).display === 'none';
        hub.style.display = isHidden ? 'flex' : 'none';
        willShow = isHidden;
    }

    // 🚀 [V80.0] 每次展开出版领航仪时刷新智能内容
    if (willShow && typeof window.initLaunchpad === 'function') {
        window.initLaunchpad();
    }
};

window.toggleImprintDropdown = (e) => {
    if (e) e.stopPropagation();

    const isTourActive = _isTourRealActive();

    // 🛡️ [退出导览自愈守护] 若导览未激活，确保清理任何遗留的锁定态与流光样式，绝对不阻碍用户操作
    if (!isTourActive) {
        const triggerEl = document.getElementById('imprint-selector-trigger');
        if (triggerEl && (triggerEl.classList.contains('tour-brand-locked') || triggerEl.classList.contains('tour-shimmer-capsule'))) {
            triggerEl.classList.remove('tour-brand-locked', 'tour-shimmer-capsule', 'tour-target-beacon');
            triggerEl.removeAttribute('title');
        }
    } else if (typeof window._isDefaultBrandActive === 'function' && window._isDefaultBrandActive()) {
        // 🔒 仅当导览真实物理处于激活态且已对正默认品牌时，才锁定拦截并提示
        if (typeof window.showToast === 'function') {
            window.showToast('🧭 导览全流程需基于官方示范品牌「创作者指南」进行，导览期间已锁定当前品牌', 'info');
        } else if (typeof window.addAudit === 'function') {
            window.addAudit('ℹ️ 导览进行中，已锁定出版品牌为「创作者指南」。', 'info');
        }
        return;
    }

    const dropdown = document.getElementById('imprint-dropdown');
    if (!dropdown) return;
    const isHidden = dropdown.style.display === 'none';
    dropdown.style.display = isHidden ? 'block' : 'none';
    if (isHidden && typeof renderImprintDropdown === 'function') renderImprintDropdown();
};

// 🛰️ [V55.1] 核级事件委派：确保出版领航仪 (Navigator) 覆盖层关闭按钮在任何层级冲突下都能被捕获
document.addEventListener('click', (e) => {
    // 寻找最近的关闭按钮，且必须在出版领航仪覆盖层内
    const closeBtn = e.target.closest('.overview-overlay .close-btn');
    if (closeBtn) {
        e.preventDefault();
        e.stopPropagation();
        window.toggleHub('hide');
    }
});

// 🚀 [V121.0] 出版领航仪自动展开偏好持久化与广播控制
window.shouldAutoOpenLaunchpad = function () {
    try {
        if (typeof localStorage === 'undefined') return true;
        return localStorage.getItem('illacme_launchpad_auto_open') !== 'false';
    } catch (e) {
        return true; // 异常时安全降级为默认开启，绝不中断主流程
    }
};

window.setLaunchpadAutoOpenPreference = function (checked) {
    try {
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('illacme_launchpad_auto_open', checked ? 'true' : 'false');
        }
    } catch (e) {
        console.warn('[Launchpad] 偏好持久化受限:', e);
    }
    // 广播同步当前 DOM 树中所有对应的复选框节点 (包括弹窗底部与治理中心开关)
    const toggles = document.querySelectorAll('.chk-auto-open-launchpad');
    toggles.forEach(chk => { chk.checked = checked; });
    const cfgToggle = document.getElementById('cfg-ui-launchpad_auto_open');
    if (cfgToggle) cfgToggle.checked = checked;
};

