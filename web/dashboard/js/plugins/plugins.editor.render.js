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
                <div class="channel-console-header api-token-helper" style="margin-bottom:1.2rem; background:rgba(0,242,255,0.04); border:1px solid rgba(0,242,255,0.18); border-radius:10px; padding:12px 14px; display:flex; justify-content:space-between; align-items:center;">
                    <div><h4 style="margin:0 0 4px; color:var(--accent-secondary); font-size:0.9rem; font-weight:700;">⚡ Cloudflare Argo 双模通道</h4><p style="margin:0; font-size:0.76rem; color:var(--text-dim);">Token 留空自动降级为 Quick 免密通道；填入 Token 享受专属域名加速。</p></div>
                    <a href="https://one.dash.cloudflare.com/" target="_blank" rel="noopener noreferrer" class="action-btn" style="text-decoration:none; font-size:0.72rem; padding:4px 10px; color:var(--accent-secondary); border-color:rgba(0,242,255,0.4);">控制台 ↗</a>
                </div>
                <div class="settings-grid">
                    ${renderSettingsItem('Tunnel Token 运行令牌', `tunnel.${id}.tunnel_token`, tunnelCfg.tunnel_token || '', 'password', { description: 'Cloudflare Zero Trust Token。留空自动使用 Quick 免密通道。', placeholder: '留空使用 Quick 临时通道，或粘贴专属 Token...', optional: true })}
                    ${renderSettingsItem('专属公网域名 (Hostname)', `tunnel.${id}.hostname`, tunnelCfg.hostname || '', 'text', { description: '绑定的自定义完整域名（留空使用临时域名）。', placeholder: '例如: press.yourdomain.com', optional: true })}
                </div>`;
        } else if (id === 'frp') {
            html += `
                <div class="channel-console-header" style="margin-bottom:1.2rem; background:rgba(59,130,246,0.05); border:1px solid rgba(59,130,246,0.2); border-radius:10px; padding:12px 14px;"><h4 style="margin:0 0 4px; color:#60a5fa; font-size:0.9rem; font-weight:700;">🛡️ FRP 自建高性能反向代理</h4><p style="margin:0; font-size:0.76rem; color:var(--text-dim);">支持国内 VPS 自建服务端，独享物理带宽与自定义域名。</p></div>
                <div class="settings-grid">
                    ${renderSettingsItem('FRP 服务端地址 (server_addr)', `tunnel.${id}.server_addr`, tunnelCfg.server_addr || '', 'text', { description: '自建 FRP 服务器的公网 IP 或域名。', placeholder: '例如: frp.yourdomain.com 或 123.45.67.89', required: true })}
                    ${renderSettingsItem('服务端通信端口 (server_port)', `tunnel.${id}.server_port`, tunnelCfg.server_port || 7000, 'number', { description: 'FRP 服务端 bind_port 端口，默认 7000。', placeholder: '7000', required: true })}
                    ${renderSettingsItem('鉴权令牌 (Token)', `tunnel.${id}.token`, tunnelCfg.token || '', 'password', { description: 'FRP 服务端通信安全凭证 (auth.token)。', placeholder: '留空或填入密码...', optional: true })}
                    ${renderSettingsItem('自定义访问域名 (custom_domain)', `tunnel.${id}.custom_domain`, tunnelCfg.custom_domain || '', 'text', { description: 'HTTP 穿透绑定的独立域名。', placeholder: '例如: press.yourdomain.com', optional: true })}
                </div>`;
        } else if (id === 'cpolar') {
            html += `
                <div class="channel-console-header" style="margin-bottom:1.2rem; background:rgba(245,158,11,0.05); border:1px solid rgba(245,158,11,0.2); border-radius:10px; padding:12px 14px; display:flex; justify-content:space-between; align-items:center;">
                    <div><h4 style="margin:0 0 4px; color:#fbbf24; font-size:0.9rem; font-weight:700;">🚀 cpolar 极点云国内极速穿透</h4><p style="margin:0; font-size:0.76rem; color:var(--text-dim);">针对国内多线网络优化，支持免费临时隧道或绑定专属二级域名。</p></div>
                    <a href="https://dashboard.cpolar.com/" target="_blank" rel="noopener noreferrer" class="action-btn" style="text-decoration:none; font-size:0.72rem; padding:4px 10px; color:#fbbf24; border-color:rgba(245,158,11,0.4);">控制台 ↗</a>
                </div>
                <div class="settings-grid">
                    ${renderSettingsItem('Authtoken 认证令牌', `tunnel.${id}.authtoken`, tunnelCfg.authtoken || '', 'password', { description: 'cpolar 仪表盘分配的 Authtoken。留空使用免密通道。', placeholder: '粘贴 cpolar Authtoken...', optional: true })}
                    ${renderSettingsItem('专属二级子域名 (Subdomain)', `tunnel.${id}.subdomain`, tunnelCfg.subdomain || '', 'text', { description: '保留的专属二级子域（仅限高级/专业版生效）。', placeholder: '例如: mypress', optional: true })}
                </div>`;
        } else if (id === 'ngrok') {
            html += `
                <div class="channel-console-header" style="margin-bottom:1.2rem; background:rgba(99,102,241,0.05); border:1px solid rgba(99,102,241,0.2); border-radius:10px; padding:12px 14px; display:flex; justify-content:space-between; align-items:center;">
                    <div><h4 style="margin:0 0 4px; color:#818cf8; font-size:0.9rem; font-weight:700;">🌍 ngrok 全球开发者隧道</h4><p style="margin:0; font-size:0.76rem; color:var(--text-dim);">国际标准反代平台，全球多边缘接入节点，需配置个人 Authtoken。</p></div>
                    <a href="https://dashboard.ngrok.com/get-started/your-authtoken" target="_blank" rel="noopener noreferrer" class="action-btn" style="text-decoration:none; font-size:0.72rem; padding:4px 10px; color:#818cf8; border-color:rgba(99,102,241,0.4);">获取 Token ↗</a>
                </div>
                <div class="settings-grid">
                    ${renderSettingsItem('ngrok Authtoken', `tunnel.${id}.authtoken`, tunnelCfg.authtoken || '', 'password', { description: 'ngrok 控制台分配的个人 Authtoken (必填)。', placeholder: '粘贴 ngrok Authtoken...', required: true })}
                    ${renderSettingsItem('静态公网域名 (Domain)', `tunnel.${id}.domain`, tunnelCfg.domain || '', 'text', { description: '在 ngrok 控制台绑定的免费静态域名或自定义域名。', placeholder: '例如: myapp.ngrok-free.app', optional: true })}
                </div>`;
        } else if (id === 'serveo') {
            html += `
                <div class="channel-console-header" style="background:rgba(16,185,129,0.05); border:1px solid rgba(16,185,129,0.2); border-radius:10px; padding:12px 14px; margin-bottom:1.2rem;"><h4 style="margin:0 0 4px; color:#10b981; font-size:0.9rem; font-weight:700;">🔗 Serveo SSH 端口转发穿透</h4><p style="margin:0; font-size:0.76rem; color:var(--text-dim);">依托系统原生 OpenSSH，零安装免客户端，可选用指定个性化子域名。</p></div>
                <div class="settings-grid">${renderSettingsItem('自定义子域名 (Subdomain)', `tunnel.${id}.subdomain`, tunnelCfg.subdomain || '', 'text', { description: '向 Serveo 请求的自定义前缀。', placeholder: '留空自动分配随机域...', optional: true })}</div>`;
        } else if (id === 'tailscale') {
            html += `
                <div class="channel-console-header" style="background:rgba(139,92,246,0.05); border:1px solid rgba(139,92,246,0.2); border-radius:10px; padding:12px 14px; margin-bottom:1.2rem;"><h4 style="margin:0 0 4px; color:#a78bfa; font-size:0.9rem; font-weight:700;">🔒 Tailscale Funnel / Serve 安全网格端点</h4><p style="margin:0; font-size:0.76rem; color:var(--text-dim);">依托本地 Tailscale 客户端与节点证书，支持公网 Funnel 或 Tailnet 设备间直连。</p></div>
                <div class="settings-grid">${renderSettingsItem('发布模式 (Funnel / Serve)', `tunnel.${id}.funnel_mode`, tunnelCfg.funnel_mode || 'funnel', 'select', { description: 'funnel 模式可供公网手机扫码访问；serve 模式仅限已加入您 Tailnet 的设备访问。', options: [{ value: 'funnel', label: '🌐 公网 Funnel (全网移动端扫码秒开)' }, { value: 'serve', label: '🔒 私网 Serve (仅限 Tailnet 网格内设备)' }] })}</div>`;
        } else {
            const driverTitle = id === 'localhost_run' ? 'Localhost.run SSH 免密穿透' : 'Pinggy SSH 极速穿透';
            html += `
                <div class="channel-console-header" style="background:rgba(16,185,129,0.05); border:1px solid rgba(16,185,129,0.2); border-radius:10px; padding:14px; margin-bottom:1.2rem;">
                    <h4 style="margin:0 0 6px; color:#10b981; font-size:0.9rem; font-weight:700;"><span>⚡ ${driverTitle}</span></h4>
                    <p style="margin:0; font-size:0.78rem; color:var(--text-dim); line-height:1.5;">依托系统底层原生 OpenSSH 客户端与端口反向转发通道，<b>无需任何账号凭证或 Token</b>，开箱即用。</p>
                </div>
                <div style="text-align:center; padding:16px 0;"><button class="action-btn glow-btn" onclick="window.fastTestPluginConnectivity('${id}', '${p.category}', this)" style="padding:8px 20px; font-size:0.85rem;">⚡ 立即发起通道自检探针</button></div>`;
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
