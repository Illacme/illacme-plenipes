/**
 * 🎨 [V87.0] Illacme Plenipes Plugins Category Cards Renderer
 * 职责：能力矩阵能级 Tabs 渲染、分类过滤卡片 HSL 配色拼接与全局开关 Slider 展示。
 */

// 4. 能力矩阵渲染器
window.loadPlugins = async () => {
    const gridEl = document.getElementById('plugins-grid');
    const tabsEl = document.querySelector('.side-tabs'); // 🚀 适配统一类名
    if (!gridEl || !tabsEl) return;

    gridEl.innerHTML = `
        <div class="skeleton-grid">
            ${Array(6).fill('<div class="plugin-card skeleton" style="height: 180px;"></div>').join('')}
        </div>
    `;

    const data = await apiFetch('/api/plugins/list');
    if (!data || !data.plugins) {
        gridEl.innerHTML = '<div class="empty-state">⚠️ 无法感应全球能力矩阵，请检查核心链路。</div>';
        return;
    }

    window.allPlugins = data.plugins;

    const categories = [
        { id: 'ingress', name: '📥 内容接入' },
        { id: 'transformer', name: '🛠️ 文稿加工' },
        { id: 'masker', name: '🛡️ 安全防护' },
        { id: 'protocol', name: '🧠 AI 协议' },
        { id: 'theme', name: '🎨 视觉装帧' },
        { id: 'hosting', name: '🌐 全站托管' },
        { id: 'image_hosting', name: '📷 图床服务' },
        { id: 'publisher', name: '🚀 分发渠道' },
        { id: 'editorial', name: '🧬 流程审计' }
    ];

    let tabsHtml = `<div class="tab-item cap-tab ${window.activePluginCategory === 'all' ? 'active' : ''}" data-cat="all"><span class="tab-icon">🌈</span> 全部能力</div>`;

    categories.forEach(cat => {
        const icon = cat.name.substring(0, 2);
        const name = cat.name.substring(3);
        tabsHtml += `
            <div class="tab-item cap-tab ${window.activePluginCategory === cat.id ? 'active' : ''}" data-cat="${cat.id}">
                <span class="tab-icon">${icon}</span> ${name}
            </div>
        `;
    });
    tabsEl.innerHTML = tabsHtml;

    document.querySelectorAll('.cap-tab').forEach(tab => {
        tab.onclick = () => {
            document.querySelectorAll('.cap-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            window.activePluginCategory = tab.dataset.cat;
            renderPlugins();
            const container = document.querySelector('.view-panel.active .tab-content-area');
            if (container) container.scrollTop = 0;
        };
    });

    renderPlugins();
};

window.renderPlugins = () => {
    const gridEl = document.getElementById('plugins-grid');
    const filtered = window.activePluginCategory === 'all'
        ? window.allPlugins.filter(p => p.category !== 'imprint')
        : window.allPlugins.filter(p => {
            if (window.activePluginCategory === 'ingress') {
                return p.category === 'ingress_source' || p.category === 'ingress_dialect';
            }
            return p.category === window.activePluginCategory && p.category !== 'imprint';
        });

    const categories = {};
    filtered.forEach(p => {
        if (!categories[p.category]) {
            categories[p.category] = {
                name: p.category_name || p.category,
                items: []
            };
        }
        categories[p.category].items.push(p);
    });

    let html = '';
    const categoryOrder = ['ingress_source', 'ingress_dialect', 'transformer', 'masker', 'protocol', 'theme', 'hosting', 'image_hosting', 'publisher', 'editorial'];

    categoryOrder.forEach(catId => {
        const cat = categories[catId];
        if (cat && cat.items.length > 0) {
            html += `
                <div class="plugins-category-section">
                    <div class="plugins-category-header"><h3>${cat.name}</h3></div>
                    <div class="shield-matrix">
                    ${cat.items.map(p => {
                        return `
                        <div class="shield-pod plugin-pod ${p.is_in_use ? 'active-duty' : ''}">
                            <div class="shield-status">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span class="status-dot-mini ${p.is_enabled ? 'healthy' : 'blocked'}" id="dot-${p.category}-${p.id}"></span>
                                    <span class="shield-id">RELEASE ${p.version.split(' ')[0]}</span>
                                </div>
                                ${p.is_manageable
                                    ? (p.is_enabled 
                                        ? `<div class="log-tag info" style="background: rgba(0, 242, 255, 0.08); color: var(--accent-secondary); border: 1px solid rgba(0, 242, 255, 0.2); font-weight: 700; font-size: 0.65rem; padding: 2px 8px; border-radius: 6px;">🔘 驱动就绪</div>` 
                                        : `<div class="log-tag warning" style="background: rgba(255, 77, 77, 0.08); color: #ff4d4d; border: 1px solid rgba(255, 77, 77, 0.2); font-weight: 700; font-size: 0.65rem; padding: 2px 8px; border-radius: 6px;">🚫 全局禁用</div>`)
                                    : `<div class="log-tag info">${p.status.toUpperCase()}</div>`
                                }
                            </div>
                            
                            <div class="shield-body" style="flex:1; display:flex; flex-direction:column;">
                                <h4 style="font-size:1.1rem; color:#fff; margin-bottom:5px;">${p.name || p.id}</h4>
                                <p style="margin-bottom:15px; flex:1; font-size:0.75rem; color:var(--text-dim);">${p.description || 'Capability syncing...'}</p>
                                
                                <div class="pod-telemetry" style="margin-bottom:15px; padding:8px 12px; display:flex; align-items:center;">
                                    <span class="tiny-label" style="color:var(--accent-primary);">${p.origin === 'core' ? '⚙️ 系统内置' : '🔌 外部扩展'}</span>
                                    ${p.is_in_use ? '<span class="tiny-label" style="margin-left:auto; color:#00ff88; display:flex; align-items:center; gap:6px;"><span class="heartbeat-indicator pulsing" style="background:#00ff88; width:6px; height:6px;"></span>品牌已绑定</span>' : ''}
                                </div>

                                <div class="p-control-group" style="display:grid; grid-template-columns: 1fr; gap:8px;">
                                    <button class="action-btn" onclick="openPluginConfig('${p.id}', '${p.category}')">⚙️ CONFIG</button>
                                </div>
                                
                                ${p.is_manageable ? `
                                  <div style="margin-top:15px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center;">
                                      <span class="tiny-label" style="opacity: 0.85; display: inline-flex; align-items: center; gap: 4px;" title="控制当前选中的品牌是否激活并使用此能力/渠道。如果关闭，当前品牌发布时将忽略该端点。">🟢 当前品牌启用</span>
                                      <label class="p-switch">
                                          <input type="checkbox" ${p.is_in_use ? 'checked' : ''} onchange="toggleBrandActivation('${p.id}', this.checked, '${p.category}')" ${!p.is_enabled ? 'disabled' : ''}>
                                          <span class="p-slider round"></span>
                                      </label>
                                  </div>
                                  ` : ''}
                            </div>
                        </div>
                    `;}).join('')}
                    </div>
                </div>
            `;
        }
    });
    gridEl.innerHTML = html || '<div class="empty-state">⚠️ 未在该能级发现任何活跃组件。</div>';
};

window.getPluginEmoji = (cat) => {
    const map = {
        'imprint': '🏗️',
        'theme': '🎨',
        'hosting': '🌐',
        'publisher': '🚀',
        'processor': '🧠',
        'ingress_source': '📥',
        'ingress_dialect': '🌀',
        'transformer': '🛠️',
        'masker': '🛡️',
        'editorial': '🧬'
    };
    return map[cat] || '🔌';
};
