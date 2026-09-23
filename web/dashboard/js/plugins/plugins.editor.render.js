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
    } else if (p.category === 'tunnel') {
        const tunnelCfg = window.settingsData?.tunnel?.[id] || {};
        if (id === 'cloudflare') {
            html += `
                <div class="channel-console-header api-token-helper" style="margin-bottom: 1.2rem; background: rgba(0, 242, 255, 0.04); border: 1px solid rgba(0, 242, 255, 0.18); border-radius: 10px; padding: 14px 16px;">
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; flex-wrap: wrap;">
                        <div>
                            <h4 style="margin: 0 0 6px 0; color: var(--accent-secondary); font-size: 0.92rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                <span>⚡ Cloudflare Argo 双模加速通道</span>
                            </h4>
                            <p style="margin: 0; font-size: 0.78rem; color: var(--text-dim); line-height: 1.5;">
                                💡 <b>双模通道模式</b>：若下方 Token <b>留空</b>，系统全自动唤醒 <b>Quick Tunnel</b> 临时免密公网通道；若填入 <b>Tunnel Token</b>，即可绑定专属自定义域名并享受全球 Anycast 边缘加速。
                            </p>
                        </div>
                        <div style="display: inline-flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                            <button type="button" class="action-btn glow-btn" onclick="window.installPluginDependencies('${id}')" style="font-size: 0.72rem; padding: 4px 10px; white-space: nowrap; border-color: rgba(16, 185, 129, 0.4); color: #10b981; background: rgba(16, 185, 129, 0.08); display: inline-flex; align-items: center; gap: 4px; cursor: pointer;">
                                <span>⚡ 一键安装 cloudflared</span>
                            </button>
                            <a href="https://one.dash.cloudflare.com/" target="_blank" rel="noopener noreferrer" class="action-btn" style="text-decoration: none; font-size: 0.72rem; padding: 4px 10px; white-space: nowrap; border-color: rgba(0, 242, 255, 0.4); color: var(--accent-secondary); display: inline-flex; align-items: center; gap: 4px;">
                                <span>☁️ 控制台 ↗</span>
                            </a>
                        </div>
                    </div>
                </div>
                <div class="settings-grid">
                    ${renderSettingsItem('Tunnel Token 隧道运行令牌', `tunnel.${id}.tunnel_token`, tunnelCfg.tunnel_token || '', 'password', {
                        description: 'Cloudflare Zero Trust 控制台生成的 Tunnel Token (eyJh...)。留空则自动降级为 Quick 临时免密通道。',
                        placeholder: '留空使用 Quick 临时通道，或粘贴专属 Token...',
                        optional: true
                    })}
                    ${renderSettingsItem('专属公网域名 (Hostname)', `tunnel.${id}.hostname`, tunnelCfg.hostname || '', 'text', {
                        description: '在 Cloudflare Tunnel Public Hostname 绑定的自定义完整域名（留空使用 trycloudflare.com 临时域名）。',
                        placeholder: '例如: press.yourdomain.com',
                        optional: true
                    })}
                </div>
            `;
        } else {
            html += `
                <div class="channel-console-header" style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 10px; padding: 16px; margin-bottom: 1.2rem;">
                    <h4 style="margin: 0 0 8px 0; color: #10b981; font-size: 0.92rem; font-weight: 700;">
                        <span>⚡ 原生 OpenSSH 零配置极速穿透</span>
                    </h4>
                    <p style="margin: 0; font-size: 0.8rem; color: var(--text-dim); line-height: 1.6;">
                        Pinggy 依托系统底层原生 OpenSSH 客户端与端口反向转发通道，<b>无需任何账号凭证、API Key 或 Token</b>。启动时系统会自动分配安全临时公网 URL，开箱即用。
                    </p>
                </div>
                <div style="text-align: center; padding: 20px 0;">
                    <button class="action-btn glow-btn" onclick="window.fastTestPluginConnectivity('${id}', '${p.category}', this)" style="padding: 8px 20px; font-size: 0.85rem;">
                        ⚡ 立即发起通道自检探针
                    </button>
                </div>
            `;
        }
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
            
            // 🚀 [V114.0 零假数据架构] 全局真实出版基线映射：优先使用真实全站数据，杜绝 schema 僵尸假数据
            const globalRealDefaults = {
                site_name: window.settingsData?.site_name || window.settingsData?.imprint_name || '',
                site_description: window.settingsData?.site_description || window.settingsData?.imprint_description || '',
                logo_path: window.settingsData?.logo_path || '',
                favicon_path: window.settingsData?.favicon_path || '',
                footer_copyright: window.settingsData?.frontmatter_defaults?.copyright || window.settingsData?.publishing_compliance?.copyright || '',
                license: window.settingsData?.frontmatter_defaults?.license || '',
                author: window.settingsData?.frontmatter_defaults?.author || '',
            };

            for (const { key, prop } of items) {
                const label = prop.title || key;
                const isColor = key.includes('color') || prop.format === 'color';
                const propType = prop.type === 'boolean' ? 'checkbox' : (prop.type === 'number' || prop.type === 'integer' ? 'number' : (isColor ? 'color' : 'text'));

                
                let currentVal = undefined;
                if (window.settingsData?.theme_options?.[id]?.options && key in window.settingsData.theme_options[id].options) {
                    currentVal = window.settingsData.theme_options[id].options[key];
                }
                
                // 仅当用户未专属定制时回退：优先继承全局真实出版基线；若非全局基线字段才使用 prop.default
                if (currentVal === undefined) {
                    if (key in globalRealDefaults && globalRealDefaults[key]) {
                        currentVal = globalRealDefaults[key];
                    } else if (key === 'hero_subtitle' || key === 'hero_title') {
                        // 首页 Hero 不硬编码第三方 SSG 的开源假宣传语，默认置空
                        currentVal = '';
                    } else {
                        currentVal = prop.default;
                    }
                }
                
                let placeholderText = '';
                if (key in globalRealDefaults && globalRealDefaults[key]) {
                    placeholderText = `继承全站基线: ${globalRealDefaults[key]}`;
                } else if (prop.default !== undefined) {
                    placeholderText = String(prop.default);
                }
                
                html += renderSettingsItem(label, `theme_options.${id}.options.${key}`, currentVal, propType, {
                    description: prop.description,
                    placeholder: placeholderText
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
