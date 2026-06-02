/**
 * Illacme-plenipes Sovereign Theme - Theme Management
 * 职责：负责全站深色/浅色模式切换与持久化状态回填。
 * 🛡️ [AEL-Iter-v11.8]：高内聚主题微模块，对齐全局主权状态总线。
 */

(function (window) {
    'use strict';

    /**
     * 更新切换按钮的 UI 文本与图标
     * @param {string} theme 当前主题模式
     */
    function updateToggleUI(theme) {
        const btn = document.getElementById('theme-toggle');
        if (!btn) return;
        const icon = btn.querySelector('.btn-icon');
        const label = btn.querySelector('.btn-label');
        if (theme === 'dark') {
            if (icon) icon.textContent = '☀️';
            if (label) label.textContent = 'Light';
        } else {
            if (icon) icon.textContent = '🌙';
            if (label) label.textContent = 'Dark';
        }
    }

    /**
     * 初始化主题管理系统
     */
    function initTheme() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (!toggleBtn) return;

        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateToggleUI(savedTheme);

        toggleBtn.addEventListener('click', () => {
            const theme = document.documentElement.getAttribute('data-theme');
            const targetTheme = theme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', targetTheme);
            localStorage.setItem('theme', targetTheme);
            updateToggleUI(targetTheme);
        });
    }

    // 挂载至全局 window 状态总线
    window.initTheme = initTheme;
    window.updateToggleUI = updateToggleUI;

})(window);
