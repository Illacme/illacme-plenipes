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
