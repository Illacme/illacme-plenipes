/**
 * ⚙️ [V1.0] Illacme Plenipes Plugins - Pod Matrix Loader & Category Shard
 * 职责：能力矩阵数据异步拉取 (loadPlugins)、SWR 缓存加速、骨架屏渲染与左侧 .side-tabs 分类计数器构建。
 * 对应重构拆分协议：SOP-01/SOP-02 模板一合规物理平移。
 */

(function () {
    'use strict';

    // 能力矩阵加载与 Tab 构建器
    window.loadPlugins = async (silent = false, targetCat = null) => {
        const gridEl = document.getElementById('plugins-grid');
        const tabsEl = document.querySelector('.side-tabs');
        if (!gridEl || !tabsEl) return;

        if (targetCat) {
            window.activePluginCategory = targetCat;
        } else if (window.pendingSubView) {
            window.activePluginCategory = window.pendingSubView;
            window.pendingSubView = null;
        } else if (!window.activePluginCategory) {
            window.activePluginCategory = 'all';
        }

        const container = document.querySelector('.view-panel.active .tab-content-area') || document.querySelector('.tab-content-area');
        const scrollPos = container ? container.scrollTop : 0;

        // ⚡ [SWR 极速瞬开] 若内存中已存在插件列表，0 毫秒先绘制页面，后台静默拉取更新，彻底消除首屏白屏与骨架跳动
        if (window.allPlugins && window.allPlugins.length > 0) {
            if (typeof window.renderPlugins === 'function') window.renderPlugins();
            silent = true;
        } else if (!silent) {
            gridEl.innerHTML = `
                <div class="card-gallery" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; width: 100%;">
                    ${Array(6).fill('<div class="plugin-card skeleton" style="height: 180px; border-radius: 12px; background: rgba(255, 255, 255, 0.03); border: 1px dashed rgba(255, 255, 255, 0.08);"></div>').join('')}
                </div>
            `;
        }

        const fetchFunc = window.apiFetch || (async (url, init) => {
            const r = await fetch(url, init);
            return r.json();
        });

        // 🚀 [毫秒级瞬开] 仅拉取轻量的插件元数据列表，绝不阻塞等待网络探针
        let data = null;
        try {
            data = await fetchFunc('/api/plugins/list');
        } catch (_) {}

        if (!data || !data.plugins) {
            if (!window.allPlugins || window.allPlugins.length === 0) {
                gridEl.innerHTML = '<div class="empty-state">⚠️ 无法感应全球能力矩阵，请检查核心链路。</div>';
            }
            return;
        }

        window.allPlugins = data.plugins;

        // 📡 触发后台静默环境探针嗅探，完成后静默更新状态，零阻塞主 UI
        if (typeof window.ensureEnvSensing === 'function') {
            window.ensureEnvSensing().then(() => {
                if (window.currentView === 'plugins' && typeof window.renderPlugins === 'function') {
                    window.renderPlugins();
                }
            }).catch(() => {});
        }

        const categories = [
            { id: 'ingress', name: '📥 内容接入' },
            { id: 'transformer', name: '🛠️ 文稿加工' },
            { id: 'masker', name: '🛡️ 安全防护' },
            { id: 'protocol', name: '🧠 算力渠道' },
            { id: 'theme', name: '🎨 视觉装帧' },
            { id: 'image_hosting', name: '📷 图床存储' },
            { id: 'hosting', name: '🌐 全站托管' },
            { id: 'publisher', name: '📢 社媒分发' },
            { id: 'ebook', name: '📚 数字装订' },
            { id: 'notification', name: '🔔 消息通知' },
            { id: 'editorial', name: '🧬 流程审计' }
        ];

        const catCountMap = {};
        window.allPlugins.forEach(p => {
            if (p.category === 'imprint') return;
            let catKey = p.category;
            if (catKey === 'ingress_source' || catKey === 'ingress_dialect') catKey = 'ingress';
            catCountMap[catKey] = (catCountMap[catKey] || 0) + 1;
        });
        const totalCount = window.allPlugins.filter(p => p.category !== 'imprint').length;

        let tabsHtml = `<div class="tab-item cap-tab ${window.activePluginCategory === 'all' ? 'active' : ''}" data-cat="all"><span class="tab-icon">🌈</span> 全部能力 <span class="tab-badge" style="font-size: 0.68rem; opacity: 0.75; margin-left: 4px;">(${totalCount})</span></div>`;

        categories.forEach(cat => {
            const icon = cat.name.substring(0, 2);
            const name = cat.name.substring(3);
            const count = catCountMap[cat.id] || 0;
            tabsHtml += `
                <div class="tab-item cap-tab ${window.activePluginCategory === cat.id ? 'active' : ''}" data-cat="${cat.id}">
                    <span class="tab-icon">${icon}</span> ${name} <span class="tab-badge" style="font-size: 0.68rem; opacity: 0.75; margin-left: 4px;">(${count})</span>
                </div>
            `;
        });
        tabsEl.innerHTML = tabsHtml;

        document.querySelectorAll('.cap-tab').forEach(tab => {
            tab.onclick = () => {
                document.querySelectorAll('.cap-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                window.activePluginCategory = tab.dataset.cat;
                if (typeof window.renderPlugins === 'function') window.renderPlugins();
                const containerEl = document.querySelector('.view-panel.active .tab-content-area');
                if (containerEl) containerEl.scrollTop = 0;
            };
        });

        if (typeof window.renderPlugins === 'function') {
            window.renderPlugins();
        }

        if (container) {
            container.scrollTop = scrollPos;
        }
    };
})();
