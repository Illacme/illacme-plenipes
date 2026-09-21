/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Pod Cards & Matrix Grid Render Shard
 * 职责：能力矩阵节点 Pod 卡片渲染、侧边 Tab 栏、搜索过滤、置顶管理与 3D 视差微动效。
 */

window.getPinnedPlugins = () => {
    try {
        return JSON.parse(localStorage.getItem('pinned_plugins') || '[]');
    } catch (e) {
        return [];
    }
};

window.togglePinPlugin = (id, event) => {
    if (event) event.stopPropagation();
    let pins = window.getPinnedPlugins();
    if (pins.includes(id)) {
        pins = pins.filter(x => x !== id);
        if (window.showToast) window.showToast(`已取消置顶 [${id.toUpperCase()}]`, 'info');
    } else {
        pins.push(id);
        if (window.showToast) window.showToast(`已成功将 [${id.toUpperCase()}] 置顶至常用能力`, 'success');
    }
    localStorage.setItem('pinned_plugins', JSON.stringify(pins));
    if (typeof window.renderPlugins === 'function') window.renderPlugins();
};

window.searchQuery = '';
window.filterPluginsBySearch = (query) => {
    window.searchQuery = (query || '').trim().toLowerCase();
    if (typeof window.renderPlugins === 'function') window.renderPlugins();
    const input = document.getElementById('plugin-search-input');
    if (input) {
        input.focus();
        const len = input.value.length;
        input.setSelectionRange(len, len);
    }
};

// 🚀 全局分类切换算子
window.filterPluginCategory = (catId) => {
    window.activePluginCategory = catId || 'all';
    document.querySelectorAll('.cap-tab').forEach(tab => {
        if (tab.dataset.cat === window.activePluginCategory) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    if (typeof window.renderPlugins === 'function') {
        window.renderPlugins();
    }
    const containerEl = document.querySelector('.view-panel.active .tab-content-area') || document.querySelector('#view-plugins .tab-content-area');
    if (containerEl) containerEl.scrollTop = 0;
};

// ⚡ [SOP-02 模块拆分] 
// 1. 能力矩阵加载器与侧边 Tab 构建器 -> plugins.render.loader.js
// 2. 插件可配置性与凭据齐全度判定算子 -> plugins.render.status.js



window.renderPlugins = () => {
    const gridEl = document.getElementById('plugins-grid');
    if (!gridEl) return;
    const pinnedIds = window.getPinnedPlugins();
    const query = window.searchQuery || '';
    const allPlugins = window.allPlugins || [];

    let filtered = window.activePluginCategory === 'all'
        ? allPlugins.filter(p => p.category !== 'imprint')
        : allPlugins.filter(p => {
            if (window.activePluginCategory === 'ingress') {
                return p.category === 'ingress_source' || p.category === 'ingress_dialect';
            }
            return p.category === window.activePluginCategory && p.category !== 'imprint';
        });

    if (query) {
        filtered = filtered.filter(p => {
            const nameMatch = (p.name || '').toLowerCase().includes(query);
            const idMatch = (p.id || '').toLowerCase().includes(query);
            const catMatch = (p.category_name || p.category || '').toLowerCase().includes(query);
            const descMatch = (p.description || '').toLowerCase().includes(query);
            return nameMatch || idMatch || catMatch || descMatch;
        });
    }

    const catNameMap = {
        'all': '🌈 全部能力矩阵',
        'ingress': '📥 内容接入',
        'transformer': '🛠️ 文稿加工',
        'masker': '🛡️ 安全防护',
        'protocol': '🧠 算力渠道',
        'theme': '🎨 视觉装帧',
        'image_hosting': '📷 图床存储',
        'hosting': '🌐 全站托管',
        'publisher': '📢 社媒分发',
        'ebook': '📚 数字装订',
        'notification': '🔔 消息通知',
        'editorial': '🧬 流程审计'
    };

    const catDescMap = {
        'all': '全站全球能力中心，支持全自动一键授权、独立网络代理与物理通道探针自检。',
        'ingress': '感知本地 Markdown/HTML 稿件与物理文件变动，自动逆向生成语法树与解析元素。',
        'transformer': '负责 Markdown 逆向渲染加工、排版指纹识别与段落结构装帧引擎。',
        'masker': '内置敏感词过滤、EXIF 地理指纹脱敏与图像安全隐私掩码保护屏障。',
        'protocol': '连接底座大语言模型，提供语义润色、智能提炼与多语言翻译中枢协议。',
        'theme': '定制全站出版物装帧主题、CSS 样式排版与视觉渲染模版引擎。',
        'hosting': '将编译好的静态网站发布至 GitHub Pages、Vercel 等多平台。支持指定一个「首选主站」作为官方主要网址，其余平台作为备用镜像同步容灾，确保全网随时随地流畅访问。',
        'image_hosting': '集成 AWS S3, 七牛云, 又拍云, Lsky Pro 等公共与自建图床上传与外链转换。',
        'publisher': '支持 Dev.to, Medium, WordPress, Ghost, Hashnode, LinkedIn 等第三方社交媒体渠道的内容分发与多平台推流。',
        'ebook': '提供符合国际出版标准的数字排版与书册装订驱动（如 EPUB 3.0、印刷级 PDF），支持整卷文稿一键合订导出。',
        'notification': '聚合飞书, 钉钉, 企业微信, Telegram 与通用 Webhook，负责出版生命周期事件广播与失败告警 Hook。',
        'editorial': '记录全站稿件版本演化指纹、发布履历与全生命周期审计追溯日志。'
    };

    const activeCatTitle = catNameMap[window.activePluginCategory] || '🌈 全部能力矩阵';
    const activeCatDesc = catDescMap[window.activePluginCategory] || '支持全自动一键授权、独立网络代理与物理通道探针自检。';

    const toolbarHtml = `
        <div class="plugin-matrix-toolbar" style="width: 100%; box-sizing: border-box; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.12)); display: flex; flex-direction: column; gap: 6px;">
            <div class="matrix-title-group" style="display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;">
                <h2 style="margin: 0; font-size: 1.35rem; color: var(--text-bright, #ffffff); font-weight: 700; display: flex; align-items: center; gap: 10px;">
                    ${activeCatTitle}
                    <span style="font-size: 0.72rem; color: var(--neon-cyan, #00f2fe); background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 254, 0.2); padding: 2px 8px; border-radius: 12px; font-weight: 600;">${filtered.length} 个节点</span>
                </h2>
            </div>
            <div class="matrix-cat-description" style="font-size: 0.82rem; color: var(--text-dim, rgba(255, 255, 255, 0.65)); line-height: 1.5; margin-top: 2px;">
                ${activeCatDesc}
            </div>
        </div>
    `;

    const categories = {};
    const pinnedItems = [];

    filtered.forEach(p => {
        if (pinnedIds.includes(p.id)) {
            pinnedItems.push(p);
        }
        if (!categories[p.category]) {
            categories[p.category] = {
                name: p.category_name || p.category,
                items: []
            };
        }
        categories[p.category].items.push(p);
    });

    let html = toolbarHtml;

    if (typeof window.runCrossPluginDiagnostics === 'function') {
        html += window.runCrossPluginDiagnostics();
    }
    if (pinnedItems.length > 0) {
        html += `
            <div class="plugins-category-section pinned-category-section" style="margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px dashed var(--glass-border);">
                <div class="plugins-category-header"><h3 style="color: #ffb700;">⭐ 常用置顶能力 (${pinnedItems.length})</h3></div>
                <div class="shield-matrix">
                ${pinnedItems.map(p => window.buildPluginPodHtml(p, true)).join('')}
                </div>
            </div>
        `;
    }

    const categoryOrder = ['ingress_source', 'ingress_dialect', 'transformer', 'masker', 'protocol', 'theme', 'hosting', 'image_hosting', 'publisher', 'ebook', 'notification', 'editorial'];

    const activeSections = categoryOrder.filter(catId => categories[catId] && categories[catId].items.length > 0);
    const hideSectionHeader = window.activePluginCategory !== 'all' && activeSections.length <= 1;

    categoryOrder.forEach(catId => {
        const cat = categories[catId];
        if (cat && cat.items.length > 0) {
            html += `
                <div class="plugins-category-section" style="${hideSectionHeader ? 'margin-top: 5px;' : ''}">
                    ${hideSectionHeader ? '' : `
                    <div class="plugins-category-header">
                        <h3 style="display: flex; align-items: center; gap: 10px;">
                            ${cat.name}
                            <span style="font-size: 0.72rem; color: var(--neon-cyan); background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.2); padding: 1px 8px; border-radius: 12px; font-weight: 600;">${cat.items.length} 个节点</span>
                        </h3>
                    </div>
                    `}
                    <div class="shield-matrix">
                    ${cat.items.map(p => window.buildPluginPodHtml(p, pinnedIds.includes(p.id))).join('')}
                    </div>
                </div>
            `;
        }
    });

    gridEl.innerHTML = html || `<div class="empty-state">${query ? `🔍 未搜索到包含 "${query}" 的相关能力。` : '⚠️ 未在该能级发现任何活跃组件。'}</div>`;
    if (typeof window.init3DHoverPhysics === 'function') {
        setTimeout(window.init3DHoverPhysics, 50);
    }
};
