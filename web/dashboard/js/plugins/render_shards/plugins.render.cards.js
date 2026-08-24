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
        window.renderPlugins();
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
            if (window.currentView === 'plugins') {
                window.renderPlugins();
            }
        }).catch(() => {});
    }

    const categories = [
        { id: 'ingress', name: '📥 内容接入' },
        { id: 'transformer', name: '🛠️ 文稿加工' },
        { id: 'masker', name: '🛡️ 安全防护' },
        { id: 'protocol', name: '🧠 AI 协议' },
        { id: 'theme', name: '🎨 视觉装帧' },
        { id: 'image_hosting', name: '📷 图床存储' },
        { id: 'hosting', name: '🌐 全站托管' },
        { id: 'publisher', name: '📢 社媒分发' },
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
            window.renderPlugins();
            const containerEl = document.querySelector('.view-panel.active .tab-content-area');
            if (containerEl) containerEl.scrollTop = 0;
        };
    });

    window.renderPlugins();

    if (container) {
        container.scrollTop = scrollPos;
    }
};

window.isPluginConfigurable = (p) => {
    if (!p) return false;
    if (p.has_config === false || p.is_configurable === false) return false;
    if (p.is_manageable === false) return false;

    const configurableCategories = ['hosting', 'image_hosting', 'notification', 'publisher', 'theme', 'protocol', 'masker', 'ingress_source'];
    if (configurableCategories.includes(p.category)) {
        return true;
    }
    return false;
};

window.checkPluginConfiguredStatus = (p) => {
    if (!p) return { label: '未激活', class: 'blocked', style: 'color: var(--text-dim); margin-right: 0 !important;' };
    const canConfig = window.isPluginConfigurable ? window.isPluginConfigurable(p) : false;
    if (!canConfig) {
        return { label: '⚡ 免配置', class: 'info', style: 'background: rgba(255, 255, 255, 0.05); color: var(--text-dim); border: 1px solid rgba(255, 255, 255, 0.15); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
    }

    if (!p.is_enabled) {
        return { label: '🚫 全局禁用', class: 'warning', style: 'background: rgba(255, 77, 77, 0.08); color: #ff4d4d; border: 1px solid rgba(255, 77, 77, 0.2); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
    }

    // 🎨 装帧主题状态呈现：统一严格 4 字符对齐（当前选用 / 本地就绪 / 云端母本）
    if (p.category === 'theme') {
        if (p.is_in_use) {
            return { label: '🟢 当前选用', class: 'info', style: 'background: rgba(0, 255, 136, 0.08); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important; white-space: nowrap;' };
        }
        const loc = p.location || 'native';
        if (loc === 'local' || loc === 'global') {
            return { label: '📦 本地就绪', class: 'info', style: 'background: rgba(0, 242, 254, 0.08); color: var(--accent-secondary); border: 1px solid rgba(0, 242, 254, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important; white-space: nowrap;' };
        }
        return { label: '☁️ 云端母本', class: 'warning', style: 'background: rgba(245, 158, 11, 0.08); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important; white-space: nowrap;' };
    }

    const cfgData = window.settingsData || {};
    let settings = {};
    if (p.category === 'hosting') {
        settings = cfgData.publish_control?.direct_upload?.[p.id] || {};
    } else if (p.category === 'image_hosting') {
        settings = cfgData.image_hosting?.[p.id] || {};
    } else if (p.category === 'notification') {
        settings = cfgData.publish_control?.webhook_endpoints?.[p.id] || {};
    } else {
        settings = cfgData.syndication?.[p.id] || {};
    }

    // 📭 [V80.2] 「从未配置」与「配置不完整」语义分离
    // 如果整个配置节完全为空（只有 enabled 等非凭据字段，或全为占位模板值），属于"从未触碰"状态
    // 不应显示 ⚠️ 警告（会造成新用户焦虑），显示中性占位徽章即可
    const SKIP_FIELDS = new Set(['enabled', 'proxy', 'force_push', 'git_user_name', 'git_user_email', 'branch', 'is_primary']);
    // 与 isPluginCredentialReady 保持一致的占位模板值检测（YOUR_*、REPLACE_*、<...> 等）
    const _isPlaceholder = (v) => {
        if (!v || typeof v !== 'string') return true;
        const t = v.trim();
        if (!t) return true;
        return /^YOUR[_\-]/i.test(t) || /^REPLACE/i.test(t) || /^TOKEN_HERE$/i.test(t) ||
               /^<.+>$/.test(t) || /^\{.+\}$/.test(t) || /^EXAMPLE[_\-]/i.test(t) || /^PLACEHOLDER/i.test(t);
    };
    const hasAnyUserInput = Object.entries(settings).some(([k, v]) => {
        if (SKIP_FIELDS.has(k)) return false;
        const s = String(v ?? '').trim();
        return s.length > 0 && !_isPlaceholder(s);
    });

    if (!hasAnyUserInput) {
        // 完全未配置（或全为模板占位值）→ 中性占位，不显示警告
        return { label: '─ 待配置', class: 'info', style: 'color: var(--text-dim); opacity: 0.55; font-weight: 500; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.03);' };
    }

    if (window.isPluginCredentialReady) {
        const cred = window.isPluginCredentialReady(p.id, p.category, settings);
        if (cred.ready) {
            return { label: `🟢 ${cred.label || '配置齐全'}`, class: 'info', style: 'background: rgba(0, 255, 136, 0.08); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
        } else {
            return { label: `⚠️ ${cred.label || '待填凭据'}`, class: 'warning', style: 'background: rgba(245, 158, 11, 0.08); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
        }
    }

    // 兜底：有用户输入 → 判断是否完整（同样排除占位值）
    const hasKeys = Object.entries(settings).some(([k, v]) => {
        if (SKIP_FIELDS.has(k)) return false;
        const s = String(v ?? '').trim();
        return s.length > 0 && !_isPlaceholder(s);
    });

    if (hasKeys) {
        return { label: '🟢 配置齐全', class: 'info', style: 'background: rgba(0, 255, 136, 0.08); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
    } else {
        return { label: '⚠️ 待填凭据', class: 'warning', style: 'background: rgba(245, 158, 11, 0.08); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.25); font-weight: 700; font-size: 0.68rem; padding: 2px 8px; border-radius: 6px; margin-right: 0 !important;' };
    }

};


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
        'protocol': '🧠 AI 协议',
        'theme': '🎨 视觉装帧',
        'image_hosting': '📷 图床存储',
        'hosting': '🌐 全站托管',
        'publisher': '📢 社媒分发',
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
        'hosting': '将编译好的静态网站推送到 GitHub Pages、Vercel、Netlify、Cloudflare Pages 等平台。支持指定一个「主站」作为 canonical 权威域名（集中 SEO 权重），其余平台作为镜像备用站运行，实现容灾与加速。',
        'image_hosting': '集成 AWS S3, 七牛云, 又拍云, Lsky Pro 等公共与自建图床上传与外链转换。',
        'notification': '聚合飞书, 钉钉, 企业微信, Telegram 与通用 Webhook，负责出版生命周期事件广播与失败告警 Hook。',
        'publisher': '支持 Dev.to, Medium, WordPress, Ghost, Hashnode, LinkedIn 等第三方社交媒体渠道的内容分发与多平台推流。',
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

    const categoryOrder = ['ingress_source', 'ingress_dialect', 'transformer', 'masker', 'protocol', 'theme', 'hosting', 'image_hosting', 'publisher', 'notification', 'editorial'];

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
