/**
 * Illacme-plenipes Sovereign Theme - Orchestrator & Sidebar Engine
 * 职责：负责前端各微模块的自愈初始化（Orchestrator），以及驱动侧边栏折叠状态的跨物理页面持久化记忆。
 * 🛡️ [AEL-Iter-v11.8]：全局主控模块，彻底攻克静态页面“物理跳转瞬时失忆”难题，100% 遵守 300 行工程门禁。
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. 激活外部微模块
    if (typeof window.initTheme === 'function') window.initTheme();
    if (typeof window.initSearch === 'function') window.initSearch();
    if (typeof window.initReadingProgress === 'function') window.initReadingProgress();
    if (typeof window.initDynamicTOC === 'function') window.initDynamicTOC();

    // 2. 自举初始化侧边栏引擎
    initSidebar();
});

/**
 * 🌲 驱动侧边栏导航状态持久化与移动端响应式面板
 */
function initSidebar() {
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const sidebar = document.querySelector('.sidebar-pioneer');
    
    // 1. 移动端响应式折叠菜单交互
    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('active');
            mobileToggle.classList.toggle('active');
            const icon = mobileToggle.querySelector('.btn-icon');
            if (icon) {
                icon.textContent = sidebar.classList.contains('active') ? '✕' : '☰';
            }
        });

        // 点击侧边栏外围区域自动闭合面板
        document.addEventListener('click', (e) => {
            if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target) && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
                mobileToggle.classList.remove('active');
                const icon = mobileToggle.querySelector('.btn-icon');
                if (icon) icon.textContent = '☰';
            }
        });
    }

    // 2. 侧边栏折叠状态物理持久化与记忆自愈引擎
    const storageKey = 'sovereign_sidebar_collapsed_groups';

    /**
     * 沿着 DOM 树向上追溯，生成该目录组在整棵树中的唯一相对路径 Key
     * @param {HTMLElement} groupEl 目录分组的 <li> 容器
     * @returns {string} 唯一路径特征 Key (如: docs/guide)
     */
    function getGroupPath(groupEl) {
        const parts = [];
        let current = groupEl;
        while (current) {
            if (current.classList.contains('nav-group')) {
                const titleSpan = current.querySelector('.group-title span');
                if (titleSpan) {
                    parts.unshift(titleSpan.textContent.trim());
                }
            }
            current = current.parentElement;
        }
        return parts.join('/');
    }

    /**
     * 物理持久化当前的折叠状态
     */
    function saveCollapsedState(path, isCollapsed) {
        let collapsed = [];
        try {
            collapsed = JSON.parse(localStorage.getItem(storageKey)) || [];
        } catch (e) {}
        if (isCollapsed) {
            if (!collapsed.includes(path)) {
                collapsed.push(path);
            }
        } else {
            collapsed = collapsed.filter(p => p !== path);
        }
        localStorage.setItem(storageKey, JSON.stringify(collapsed));
    }

    /**
     * 获取历史固化的所有折叠目录相对路径
     */
    function getCollapsedGroups() {
        try {
            return JSON.parse(localStorage.getItem(storageKey)) || [];
        } catch (e) {
            return [];
        }
    }

    const collapsedGroups = getCollapsedGroups();
    const groups = document.querySelectorAll('.nav-group');

    groups.forEach(group => {
        const path = getGroupPath(group);
        const title = group.querySelector('.group-title');
        const toggle = title ? title.querySelector('.group-toggle') : null;

        if (!title) return;

        // 🚀 自愈恢复：从缓存中拉取上一页面的折叠记忆并物理对准
        if (collapsedGroups.includes(path)) {
            group.classList.add('collapsed');
            if (toggle) toggle.textContent = '▶';
        } else {
            group.classList.remove('collapsed');
            if (toggle) toggle.textContent = '▼';
        }

        // 监听用户的点击动作并持久化录入缓存
        title.addEventListener('click', (e) => {
            e.stopPropagation();
            const isCollapsed = group.classList.toggle('collapsed');
            if (toggle) {
                toggle.textContent = isCollapsed ? '▶' : '▼';
            }
            saveCollapsedState(path, isCollapsed);
        });
    });
}
