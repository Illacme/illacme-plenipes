/**
 * Illacme-plenipes Sovereign Theme - Offline Search Hub
 * 职责：负责全离线静态索引的高精度匹配与键盘无障碍交互（A11y）。
 * 🛡️ [AEL-Iter-v11.8]：高内聚 Search 模块，利用 IIFE 物理屏蔽私有索引状态，防范内存污染。
 */

(function (window) {
    'use strict';

    let searchIndex = null;

    /**
     * 渲染搜索匹配结果列表
     * @param {Array} matches 匹配到的文档数组
     * @param {HTMLElement} container 下拉结果容器
     */
    function renderResults(matches, container) {
        if (matches.length === 0) {
            container.innerHTML = '<div class="search-no-results">未发现相关文档...</div>';
        } else {
            container.innerHTML = matches.map(m => `
                <a href="${m.url}" class="search-item">
                    <div class="search-item-title">${m.title}</div>
                    <div class="search-item-desc">${m.description || '无详细描述'}</div>
                </a>
            `).join('');
        }
        container.classList.add('active');
    }

    /**
     * 初始化离线搜索系统
     */
    async function initSearch() {
        const searchInput = document.getElementById('search-input');
        const resultsContainer = document.getElementById('search-results');
        if (!searchInput || !resultsContainer) return;

        // 🚀 [V15.0] 静态相对路径深度自适应回归
        const pathParts = window.location.pathname.split('/').filter(p => p);
        const depth = pathParts.length;
        const rootPrefix = depth > 1 ? '../'.repeat(depth - 1) : './';
        const indexPath = `${rootPrefix}static/search_index.json`;

        // 聚焦即触发异步惰性加载
        searchInput.addEventListener('focus', async () => {
            if (!searchIndex) {
                try {
                    const resp = await fetch(indexPath);
                    searchIndex = await resp.json();
                    console.log('📡 搜索索引已加载:', searchIndex.length);
                } catch (e) {
                    console.error('🛑 搜索索引加载失败:', e);
                }
            }
        });

        // 全文标题及关键词检索过滤
        searchInput.addEventListener('input', (e) => {
            if (!searchIndex) return;
            const query = e.target.value.toLowerCase().trim();
            if (query.length < 2) {
                resultsContainer.classList.remove('active');
                return;
            }

            const matches = searchIndex.filter(item => 
                item.title.toLowerCase().includes(query) || 
                (item.description && item.description.toLowerCase().includes(query)) ||
                (item.keywords && item.keywords.some(k => k.toLowerCase().includes(query)))
            ).slice(0, 10);

            renderResults(matches, resultsContainer);
        });

        // 点击空白处关闭下拉结果
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
                resultsContainer.classList.remove('active');
            }
        });

        // 🚀 [V15.5] 搜索列表键盘交互增强 (ArrowUp / ArrowDown / Enter / Escape)
        let selectedIndex = -1;

        searchInput.addEventListener('keydown', (e) => {
            const items = resultsContainer.querySelectorAll('.search-item');
            if (!resultsContainer.classList.contains('active') || items.length === 0) return;

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedIndex = (selectedIndex + 1) % items.length;
                updateSelection(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedIndex = (selectedIndex - 1 + items.length) % items.length;
                updateSelection(items);
            } else if (e.key === 'Enter') {
                if (selectedIndex >= 0) {
                    e.preventDefault();
                    items[selectedIndex].click();
                }
            } else if (e.key === 'Escape') {
                resultsContainer.classList.remove('active');
                searchInput.blur();
            }
        });

        function updateSelection(items) {
            items.forEach((item, index) => {
                if (index === selectedIndex) {
                    item.classList.add('selected');
                    item.scrollIntoView({ block: 'nearest' });
                } else {
                    item.classList.remove('selected');
                }
            });
        }

        // 🚀 [V15.5] 移动端搜索框聚焦时自适应拉伸
        const searchHub = document.querySelector('.search-hub');
        searchInput.addEventListener('focus', () => {
            if (window.innerWidth <= 768 && searchHub) {
                searchHub.classList.add('expanded');
            }
        });

        document.addEventListener('click', (e) => {
            if (searchHub && !searchHub.contains(e.target) && searchHub.classList.contains('expanded')) {
                searchHub.classList.remove('expanded');
            }
        });
    }

    // 挂载至全局 window 状态总线
    window.initSearch = initSearch;

})(window);
