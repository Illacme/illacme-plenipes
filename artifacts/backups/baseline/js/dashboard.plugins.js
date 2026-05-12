/**
 * 🧩 [V55.0] Illacme Plenipes Plugins & Capability Module
 * 职责：能力矩阵渲染、插件状态管控与分发通道治理。
 */

// 1. 状态矩阵
window.activePluginCategory = 'all';
window.allPlugins = [];

// 2. 插件开关控制
window.togglePlugin = async (id, enable) => {
    try {
        const response = await fetch('/api/plugins/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, enable })
        });
        const result = await response.json();
        if (result.status === 'success') {
            addAudit(`🛡️ 能力治理：已${enable ? '激活' : '封锁'}插件 [${id}]`);
            // 重新加载以更新 UI 状态和排序
            await loadPlugins();
        } else {
            alert(`操作失败: ${result.error}`);
        }
    } catch (e) {
        console.error("Toggle error:", e);
    }
};

// 3. 物理链路探测
window.probePlugin = async (id) => {
    addAudit(`🛰️ 正在物理探测 [${id}] 链路状态...`);
    const res = await apiFetch('/api/plugins/probe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    });

    if (res && res.success) {
        const dot = document.getElementById(`dot-${id}`);
        if (res.healthy) {
            addAudit(`✅ [${id}] 物理链路畅通。`);
            if (dot) {
                dot.classList.remove('blocked');
                dot.classList.add('healthy');
            }
        } else {
            addAudit(`❌ [${id}] 链路阻塞：物理连接失败或凭据无效。`, "error");
            if (dot) {
                dot.classList.remove('healthy');
                dot.classList.add('blocked');
            }
        }
    } else {
        addAudit(`⚠️ [${id}] 探测失败: ${res.error || '组件不支持物理自检'}`, "warning");
    }
};

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
        { id: 'ingress', name: '📥 输入感应' },
        { id: 'transformer', name: '🛠️ 资产加工' },
        { id: 'masker', name: '🛡️ 安全防护' },
        { id: 'theme', name: '🎨 视觉装帧' },
        { id: 'hosting', name: '🌐 全站托管' },
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
            const container = document.querySelector('.tab-content-area');
            if (container) container.scrollTop = 0;
        };
    });

    renderPlugins();
};

window.renderPlugins = () => {
    const gridEl = document.getElementById('plugins-grid');
    const filtered = window.activePluginCategory === 'all'
        ? window.allPlugins.filter(p => p.category !== 'imprint')
        : window.allPlugins.filter(p => p.category === window.activePluginCategory && p.category !== 'imprint');

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
    const categoryOrder = ['ingress', 'transformer', 'masker', 'theme', 'hosting', 'publisher', 'editorial'];

    categoryOrder.forEach(catId => {
        const cat = categories[catId];
        if (cat && cat.items.length > 0) {
            html += `
                <div class="plugins-category-section">
                    <div class="plugins-category-header"><h3>${cat.name}</h3></div>
                    <div class="shield-matrix">
                    ${cat.items.map(p => `
                        <div class="shield-pod plugin-pod ${p.is_in_use ? 'active-duty' : ''}">
                            <div class="shield-status">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span class="status-dot-mini ${p.is_enabled ? 'healthy' : 'blocked'}" id="dot-${p.id}"></span>
                                    <span class="shield-id">RELEASE ${p.version.split(' ')[0]}</span>
                                </div>
                                <div class="log-tag info">${p.status.toUpperCase()}</div>
                            </div>
                            
                            <div class="shield-body" style="flex:1; display:flex; flex-direction:column;">
                                <h4 style="font-size:1.1rem; color:#fff; margin-bottom:5px;">${(p.name || p.id).toUpperCase()}</h4>
                                <p style="margin-bottom:15px; flex:1; font-size:0.75rem; color:var(--text-dim);">${p.description || 'Capability syncing...'}</p>
                                
                                <div class="pod-telemetry" style="margin-bottom:15px; padding:8px 12px; display:flex; align-items:center;">
                                    <span class="tiny-label" style="color:var(--accent-primary);">${p.origin === 'core' ? '🛡️ CORE ASSET' : '🧩 EXTENSION'}</span>
                                    ${p.is_in_use ? '<span class="tiny-label" style="margin-left:auto; color:#00ff88;">● ACTIVE DUTY</span>' : ''}
                                </div>

                                <div class="p-control-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
                                    <button class="action-btn" onclick="openPluginConfig('${p.id}')" ${!p.is_enabled ? 'disabled' : ''}>⚙️ CONFIG</button>
                                    <button class="action-btn" onclick="probePlugin('${p.id}')">📡 PROBE</button>
                                </div>
                                
                                <div style="margin-top:15px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center;">
                                    <span class="tiny-label">POWER STATE</span>
                                    <label class="p-switch">
                                        <input type="checkbox" ${p.is_enabled ? 'checked' : ''} onchange="togglePlugin('${p.id}', this.checked)" ${p.is_in_use ? 'disabled' : ''}>
                                        <span class="p-slider round"></span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    `).join('')}
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
        'ingress': '📥',
        'transformer': '🛠️',
        'masker': '🛡️',
        'editorial': '🧬'
    };
    return map[cat] || '🔌';
};

// 5. 插件配置抽屉
window.openPluginConfig = async (id) => {
    const drawer = document.getElementById('plugin-drawer');
    const body = document.getElementById('p-drawer-body');
    const title = document.getElementById('p-drawer-title');

    if (!drawer || !body) return;

    const p = window.allPlugins.find(x => x.id === id);
    title.innerText = `⚙️ 配置能力: ${p?.name || id}`;
    body.innerHTML = '<div class="loading">正在提取插件治理元数据...</div>';
    drawer.style.display = 'flex';

    if (Object.keys(window.settingsData).length === 0) {
        const res = await apiFetch('/api/system/config');
        if (res && res.config) window.settingsData = res.config;
    }

    let html = '';
    // p is already defined at the top of the function

    if (p.type === 'container') {
        html = `
            <div class="channel-console-header">
                <p style="color: var(--text-dim); font-size: 0.85rem;">${p.description}</p>
                <div class="console-search">
                    <input type="text" placeholder="🔍 在 ${p.sub_items.length} 个节点中快速检索..." onkeyup="filterConsoleTable(this)">
                </div>
            </div>
            <div class="console-table-wrapper">
                <table class="modern-table">
                    <thead>
                        <tr>
                            <th>节点名称</th>
                            <th>物理目标</th>
                            <th>状态</th>
                            <th style="text-align: right;">管控</th>
                        </tr>
                    </thead>
                    <tbody id="console-table-body">
                        ${p.sub_items.map(sub => `
                            <tr class="console-tr" data-search="${sub.name.toLowerCase()} ${sub.target.toLowerCase()}">
                                <td>
                                    <div style="display: flex; flex-direction: column;">
                                        <span style="font-weight: 600;">${sub.name}</span>
                                        <span style="font-size: 0.65rem; opacity: 0.4;">ID: ${sub.id}</span>
                                    </div>
                                </td>
                                <td><code class="path-tag" title="${sub.target}">${sub.target.length > 30 ? sub.target.substring(0, 27) + '...' : sub.target}</code></td>
                                <td><span class="sub-status-pill ${sub.status.toLowerCase()}">${sub.status}</span></td>
                                <td style="text-align: right;">
                                    <div style="display: inline-flex; gap: 8px;">
                                        <button class="mini-action-btn" onclick="editSubItem('${p.id}', '${sub.id}')">⚙️</button>
                                        <button class="mini-action-btn" onclick="addAudit('📡 正在对端点发起主权 Ping...')">📡</button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } else if (p.category === 'ssg') {
        html = `
            <div class="settings-grid">
                ${renderSettingsItem('主站点 URL', 'site_url', window.settingsData.site_url)}
                ${renderSettingsItem('导航深度', 'theme_config.nav_depth', window.settingsData.theme_config?.nav_depth || 2, 'number')}
                ${renderSettingsItem('强制暗色模式', 'theme_config.force_dark', window.settingsData.theme_config?.force_dark, 'checkbox')}
                <div class="full-width" style="margin-top: 1rem; border-top: 1px solid var(--glass-border); padding-top: 1rem;">
                    <label style="font-size: 0.75rem; color: var(--text-dim);">当前激活引擎</label>
                    <code style="display: block; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 8px; margin-top: 0.5rem;">${window.settingsData.system?.ssg_engine || 'default'}</code>
                </div>
            </div>
        `;
    } else if (p.category === 'publisher' || p.category === 'hosting') {
        const platform = p.platform || id;
        if (platform === 'github_pages') {
            html = `<div class="settings-grid">${renderSettingsItem('启用 GitHub Pages 同步', 'github_enabled', window.settingsData.github_enabled, 'checkbox')}</div>`;
        } else if (platform === 's3') {
            html = `<div class="settings-grid">${renderSettingsItem('启用 S3 镜像存储', 's3_enabled', window.settingsData.s3_enabled, 'checkbox')}</div>`;
        } else {
            const cfg = window.settingsData.syndication?.[id] || {};
            html = `
                <div class="settings-grid">
                    ${renderSettingsItem('启用该节点', p.category === 'hosting' ? `publish_control.direct_upload.${id}.enabled` : `syndication.${id}.enabled`, cfg.enabled, 'checkbox')}
                    ${renderSettingsItem('凭据/密钥 (Key/Token)', p.category === 'hosting' ? `publish_control.direct_upload.${id}.api_key` : `syndication.${id}.api_key`, cfg.api_key || cfg.app_password, 'password')}
                    ${renderSettingsItem('发布目标 (URL/Bucket)', p.category === 'hosting' ? `publish_control.direct_upload.${id}.url` : `syndication.${id}.url`, cfg.url)}
                    ${renderSettingsItem('账号/ID', p.category === 'hosting' ? `publish_control.direct_upload.${id}.username` : `syndication.${id}.username`, cfg.username)}
                </div>
            `;
        }
    }

    if (p.type !== 'container') {
        html += `
            <div class="settings-grid" style="margin-top: 1.5rem;">
                ${renderSettingsItem('分发延迟补偿 (ms)', 'sync_delay', window.settingsData.sync_delay, 'number')}
            </div>
        `;
    }

    if (!html) {
        html = `
            <div class="empty-state">
                <p>该能力目前遵循系统全息配置，暂无独立调节参数。</p>
                <code style="font-size: 0.7rem; opacity: 0.5;">ID: ${id} | Origin: ${p.origin}</code>
            </div>
        `;
    }

    body.innerHTML = html;
};

window.closePluginDrawer = () => {
    const drawer = document.getElementById('plugin-drawer');
    if (drawer) drawer.style.display = 'none';
};

window.filterSubItems = (input) => {
    const term = input.value.toLowerCase();
    const card = input.closest('.plugin-card');
    const rows = card.querySelectorAll('.sub-item-row');
    rows.forEach(row => {
        const name = row.getAttribute('data-sub-name');
        const target = row.getAttribute('data-sub-target');
        row.style.display = (name.includes(term) || target.includes(term)) ? 'flex' : 'none';
    });
};

window.filterConsoleTable = (input) => {
    const term = input.value.toLowerCase();
    const rows = document.querySelectorAll('.console-tr');
    rows.forEach(row => {
        const searchData = row.getAttribute('data-search');
        row.style.display = searchData.includes(term) ? '' : 'none';
    });
};

window.editSubItem = async (parentId, subId) => {
    const body = document.getElementById('p-drawer-body');
    const p = window.allPlugins.find(x => x.id === parentId);
    if (!p) return;

    let subHtml = `
        <div class="sub-editor-header" style="margin-bottom: 1.5rem;">
            <button class="p-action-btn secondary" style="padding: 4px 10px; font-size: 0.75rem;" onclick="openPluginConfig('${parentId}')">⬅️ 返回通道列表</button>
            <h4 style="margin-top: 1rem; color: var(--accent-primary);">⚙️ 节点管理: ${subId.toUpperCase()}</h4>
        </div>
        <div class="settings-grid">
    `;

    if (parentId === 'webhook_gateway') {
        const endpoint = window.settingsData.publish_control?.webhook_endpoints?.[subId] || {};
        subHtml += `
            ${renderSettingsItem('通道开关', `publish_control.webhook_endpoints.${subId}.enabled`, endpoint.enabled, 'checkbox')}
            ${renderSettingsItem('物理端点 (URL)', `publish_control.webhook_endpoints.${subId}.url`, endpoint.url)}
            ${renderSettingsItem('主权密钥 (Secret)', `publish_control.webhook_endpoints.${subId}.secret`, endpoint.secret, 'password')}
        `;
    } else {
        const cfg = window.settingsData.syndication?.[subId] || {};
        subHtml += `
            ${renderSettingsItem('节点开关', `syndication.${subId}.enabled`, cfg.enabled, 'checkbox')}
            ${renderSettingsItem('平台 URL (可选)', `syndication.${subId}.url`, cfg.url)}
            ${renderSettingsItem('账号名/用户名', `syndication.${subId}.username`, cfg.username)}
            ${renderSettingsItem('访问凭据 (Token/Key)', `syndication.${subId}.api_key`, cfg.api_key || cfg.app_password, 'password')}
        `;
    }

    subHtml += `
        </div>
        <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--glass-border); display: flex; flex-direction: column; gap: 1rem;">
            <button class="primary-btn glow-btn" onclick="saveAllSettings()">💾 保存节点配置</button>
            <p style="font-size: 0.7rem; color: var(--text-dim);">⚠️ 注意：修改将直接同步至物理配置文件，保存后请重启系统生效。</p>
        </div>
    `;

    body.innerHTML = subHtml;
};
