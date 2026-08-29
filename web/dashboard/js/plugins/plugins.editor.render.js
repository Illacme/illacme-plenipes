/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins Configuration Drawer Renderers
 * 职责：渲染各种插件分类（container/ssg/publisher/hosting/image_hosting/theme）的表单/组件 HTML。
 */
var renderSettingsItem = window.renderSettingsItem || (() => "");

window.buildPluginConfigFormHtml = (p) => {
    let html = '';
    const id = p.id;

    if (p.type === 'container') {
        html += `
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
        html += `
            <div class="settings-grid">
                ${renderSettingsItem('主站点 URL', 'site_url', window.settingsData?.site_url)}
                ${renderSettingsItem('导航深度', 'theme_config.nav_depth', window.settingsData?.theme_config?.nav_depth || 2, 'number')}
                ${renderSettingsItem('强制暗色模式', 'theme_config.force_dark', window.settingsData?.theme_config?.force_dark, 'checkbox')}
                <div class="full-width" style="margin-top: 1rem; border-top: 1px solid var(--glass-border); padding-top: 1rem;">
                    <label style="font-size: 0.75rem; color: var(--text-dim);">当前激活引擎</label>
                    <code style="display: block; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 8px; margin-top: 0.5rem;">${window.settingsData?.system?.ssg_engine || 'default'}</code>
                </div>
            </div>
        `;
    } else if (p.category === 'publisher' || p.category === 'hosting' || p.category === 'notification') {
        const cfg = p.category === 'hosting'
            ? (window.settingsData?.publish_control?.direct_upload?.[id] || {})
            : (p.category === 'notification'
                ? (window.settingsData?.publish_control?.webhook_endpoints?.[id] || {})
                : (window.settingsData?.syndication?.[id] || {}));
        html += `<div class="settings-grid">${window.renderPlatformConfig ? window.renderPlatformConfig(id, cfg, p.category) : renderPlatformConfig(id, cfg, p.category)}</div>`;
    } else if (p.category === 'image_hosting') {
        const cfg = window.settingsData?.image_hosting?.[id] || {};
        html += `<div class="settings-grid">${window.renderImageHostingConfig ? window.renderImageHostingConfig(id, cfg) : renderImageHostingConfig(id, cfg)}</div>`;
    } else if (p.category === 'protocol') {
        html += `<div class="settings-grid">${window.renderAIProtocolConfig ? window.renderAIProtocolConfig(id, p) : rawRenderAIProtocolConfig(id, p)}</div>`;
    } else if (p.category === 'theme') {
        const schema = p.schema || {};
        const properties = schema.properties || {};
        
        // 🚀 [V88.0] 高级主题选项按 group 进行物理分类并按 order 排序
        const groups = {};
        for (const [key, prop] of Object.entries(properties)) {
            const groupName = prop.group || '常规设置';
            if (!groups[groupName]) groups[groupName] = [];
            groups[groupName].push({ key, prop });
        }
        
        // 按自定义排序对组内的 properties 进行升序排列
        for (const g in groups) {
            groups[g].sort((a, b) => (a.prop.order || 99) - (b.prop.order || 99));
        }
        
        // 定义组本身的呈现顺序
        const groupPriority = ["基础设置", "视觉样式", "首页 Hero", "外部链接", "常规设置"];
        const sortedGroupNames = Object.keys(groups).sort((a, b) => {
            let idxA = groupPriority.indexOf(a);
            let idxB = groupPriority.indexOf(b);
            if (idxA === -1) idxA = 99;
            if (idxB === -1) idxB = 99;
            return idxA - idxB;
        });
        
        html += '<div style="display: flex; flex-direction: column; gap: 1.2rem;">';
        for (const gName of sortedGroupNames) {
            const items = groups[gName];
            const groupIconMap = { '基础设置': '⚙️', '视觉样式': '🎨', '首页 Hero': '🏠', '外部链接': '🔗', '常规设置': '🧩' };
            const icon = groupIconMap[gName] || '🧩';
            
            const isStyleBlock = gName === '视觉样式';
            const styleBlockAttr = isStyleBlock ? 'id="theme-config-style-group-block"' : '';
            let extraStyle = '';
            if (isStyleBlock) {
                extraStyle = 'display: none; opacity: 0; transition: opacity 0.25s ease;';
            }
            
            html += `
                <div class="theme-config-group-block" ${styleBlockAttr} style="border: 1px solid var(--glass-border); border-radius: 8px; padding: 1.2rem; background: rgba(255, 255, 255, 0.02); backdrop-filter: blur(10px); ${extraStyle}">
                    <h5 style="color: var(--accent-secondary); margin: 0 0 1rem 0; font-size: 0.85rem; font-weight: 700; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 0.5rem;">
                        <span>${icon} ${gName}</span>
                    </h5>
                    <div class="settings-grid">
            `;
            
            for (const { key, prop } of items) {
                const label = prop.title || key;
                const propType = prop.type === 'boolean' ? 'checkbox' : (prop.type === 'number' || prop.type === 'integer' ? 'number' : 'text');
                
                let currentVal = undefined;
                if (window.settingsData && window.settingsData.theme_options && window.settingsData.theme_options[id] && window.settingsData.theme_options[id].options) {
                    currentVal = window.settingsData.theme_options[id].options[key];
                }
                if (currentVal === undefined) {
                    currentVal = prop.default;
                }
                
                html += renderSettingsItem(label, `theme_options.${id}.options.${key}`, currentVal, propType, {
                    description: prop.description,
                    placeholder: prop.default !== undefined ? String(prop.default) : ''
                });
            }
            
            html += `
                    </div>
                </div>
            `;
        }
        html += '</div>';
    }

    return html;
};
