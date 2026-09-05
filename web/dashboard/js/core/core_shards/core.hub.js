/**
 * 🚀 Illacme Plenipes Dashboard Core - Hub & Overlay Shard
 * 职责：核心指挥覆盖层切换、品牌上下文下拉绑定与关闭按钮事件委派。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

// 1. 核心指挥中枢控制 (全局单例)
window.toggleHub = (forceState) => {
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

    // 🚀 [V80.0] 每次展开出版工作台时刷新智能内容
    if (willShow && typeof window.initLaunchpad === 'function') {
        window.initLaunchpad();
    }
};

window.toggleImprintDropdown = (e) => {
    if (e) e.stopPropagation();
    const dropdown = document.getElementById('imprint-dropdown');
    if (!dropdown) return;
    const isHidden = dropdown.style.display === 'none';
    dropdown.style.display = isHidden ? 'block' : 'none';
    if (isHidden && typeof renderImprintDropdown === 'function') renderImprintDropdown();
};

// 🛰️ [V55.1] 核级事件委派：确保指挥中心关闭按钮在任何层级冲突下都能被捕获
document.addEventListener('click', (e) => {
    // 寻找最近的关闭按钮，且必须在指挥中心覆盖层内
    const closeBtn = e.target.closest('.overview-overlay .close-btn');
    if (closeBtn) {
        e.preventDefault();
        e.stopPropagation();
        window.toggleHub('hide');
    }
});

// 🚀 [V121.0] 出版工作台自动展开偏好持久化与广播控制
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

