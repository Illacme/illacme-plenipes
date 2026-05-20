/**
 * 🎭 [V57.0] Illacme Plenipes UI Component Hub
 * 职责：渲染全局 UI 组件（如弹窗、抽屉），维持 index.html 的极简状态。
 * 🛡️ [V75.2 Decoupled] 模块化重构：HTML 组件及 Tooltip 引擎已拆分为独立原子模块（drawers.js, modals.js, tooltip.js）。
 */

window.renderUIComponents = () => {
    const appContainer = document.getElementById('app-container');
    if (!appContainer) return;

    // 🚀 [V75.2] 动态整合原子化子组件的 HTML (Single Source of Truth)
    const componentsHTML = window.getUIDrawersHTML() + window.getUIModalsHTML();

    // 注入到 app-container 末尾
    appContainer.insertAdjacentHTML('beforeend', componentsHTML);
};
