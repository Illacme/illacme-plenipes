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
        { id: 'ingress', name: '📥 内容接入' },
        { id: 'transformer', name: '🛠️ 文稿加工' },
        { id: 'masker', name: '🛡️ 安全防护' },
        { id: 'protocol', name: '🧠 AI 协议' },
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
    const categoryOrder = ['ingress_source', 'ingress_dialect', 'transformer', 'masker', 'protocol', 'theme', 'hosting', 'publisher', 'editorial'];

    categoryOrder.forEach(catId => {
        const cat = categories[catId];
        if (cat && cat.items.length > 0) {
            html += `
                <div class="plugins-category-section">
                    <div class="plugins-category-header"><h3>${cat.name}</h3></div>
                    <div class="shield-matrix">
                    ${cat.items.map(p => {
                        const needsProbe = ['protocol', 'publisher', 'hosting'].includes(p.category);
                        return `
                        <div class="shield-pod plugin-pod ${p.is_in_use ? 'active-duty' : ''}">
                            <div class="shield-status">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span class="status-dot-mini ${p.is_enabled ? 'healthy' : 'blocked'}" id="dot-${p.id}"></span>
                                    <span class="shield-id">RELEASE ${p.version.split(' ')[0]}</span>
                                </div>
                                ${p.is_manageable
                                    ? (p.is_in_use 
                                        ? `<div class="log-tag success" style="background: rgba(0, 255, 136, 0.08); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.2); font-weight: 700; font-size: 0.65rem; padding: 2px 8px; border-radius: 6px;">🟢 品牌激活</div>` 
                                        : (p.is_enabled 
                                            ? `<div class="log-tag info" style="background: rgba(0, 242, 255, 0.08); color: var(--accent-secondary); border: 1px solid rgba(0, 242, 255, 0.2); font-weight: 700; font-size: 0.65rem; padding: 2px 8px; border-radius: 6px;">🔘 驱动就绪</div>` 
                                            : `<div class="log-tag warning" style="background: rgba(255, 77, 77, 0.08); color: #ff4d4d; border: 1px solid rgba(255, 77, 77, 0.2); font-weight: 700; font-size: 0.65rem; padding: 2px 8px; border-radius: 6px;">🚫 全局禁用</div>`))
                                    : `<div class="log-tag info">${p.status.toUpperCase()}</div>`
                                }
                            </div>
                            
                            <div class="shield-body" style="flex:1; display:flex; flex-direction:column;">
                                <h4 style="font-size:1.1rem; color:#fff; margin-bottom:5px;">${p.name || p.id}</h4>
                                <p style="margin-bottom:15px; flex:1; font-size:0.75rem; color:var(--text-dim);">${p.description || 'Capability syncing...'}</p>
                                
                                <div class="pod-telemetry" style="margin-bottom:15px; padding:8px 12px; display:flex; align-items:center;">
                                    <span class="tiny-label" style="color:var(--accent-primary);">${p.origin === 'core' ? '🛡️ CORE ASSET' : '🧩 EXTENSION'}</span>
                                    ${p.is_in_use ? '<span class="tiny-label" style="margin-left:auto; color:#00ff88; display:flex; align-items:center; gap:6px;"><span class="heartbeat-indicator pulsing" style="background:#00ff88; width:6px; height:6px;"></span>品牌已绑定</span>' : ''}
                                </div>

                                <div class="p-control-group" style="display:grid; grid-template-columns: ${needsProbe ? '1fr 1fr' : '1fr'}; gap:8px;">
                                    <button class="action-btn" onclick="openPluginConfig('${p.id}')" ${!p.is_enabled ? 'disabled' : ''}>⚙️ CONFIG</button>
                                    ${needsProbe ? `<button class="action-btn" onclick="probePlugin('${p.id}')">📡 PROBE</button>` : ''}
                                </div>
                                
                                ${p.is_manageable ? `
                                 <div style="margin-top:15px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center;">
                                     <span class="tiny-label" style="opacity: 0.85; display: inline-flex; align-items: center; gap: 4px;" title="控制该功能的全局开关状态。如果当前已被激活的品牌绑定使用，滑块将自动锁定以确保发布链路安全。">🔌 全局功能开关 (Global Switch)</span>
                                     <label class="p-switch">
                                         <input type="checkbox" ${p.is_enabled ? 'checked' : ''} onchange="togglePlugin('${p.id}', this.checked)" ${p.is_in_use ? 'disabled' : ''}>
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

    if (Object.keys(window.settingsData).length === 0 || !window.governanceRules || Object.keys(window.governanceRules).length === 0) {
        const res = await apiFetch('/api/system/config');
        if (res) {
            window.settingsData = res.config || res;
            window.governanceRules = res.governance_rules || res._governance_rules || {};
        }
    }

    // 🚀 控制底部“🧪 沙盘演练”按钮的显示与绑定
    const dryRunBtn = document.getElementById('btn-dry-run-plugin');
    if (dryRunBtn) {
        if (p && (p.category === 'publisher' || p.category === 'hosting') && id !== 'github_pages') {
            dryRunBtn.style.display = 'block';
            dryRunBtn.setAttribute('onclick', `triggerPluginDryRun('${id}')`);
        } else {
            dryRunBtn.style.display = 'none';
        }
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
            
            // 🚀 1. WordPress 卡片主配置定制与保姆级参数指导
            if (id === 'wordpress') {
                html = `
                    <div class="settings-grid">
                        ${renderSettingsItem('通道激活', `syndication.wordpress.enabled`, cfg.enabled, 'checkbox', {description: '激活后，文章出版发布时将自动分发并同步更新至您的 WordPress。'})}
                        ${renderSettingsItem('平台 REST API 地址', `syndication.wordpress.api_url`, cfg.api_url || cfg.url, 'text', {placeholder: "例如: https://yourdomain.com/wp-json/wp/v2", description: "【如何获取】输入您的 WordPress 站点 API 端点，通常为您的网站地址加上 '/wp-json/wp/v2'"})}
                        ${renderSettingsItem('管理员用户名', `syndication.wordpress.username`, cfg.username, 'text', {placeholder: "例如: admin", description: "【如何获取】您在 WordPress 中登录后台所使用的用户名"})}
                        ${renderSettingsItem('应用密码 (Application Password)', `syndication.wordpress.application_password`, cfg.application_password || cfg.api_key, 'password', {placeholder: "请在此输入 24 位的应用密码", description: "【如何获取】在 WordPress 后台 -> 用户 -> 个人资料 -> 应用密码中生成（注意：此处切勿输入您的 WordPress 登录密码！）"})}
                        ${renderSettingsItem('文章默认发布状态', `syndication.wordpress.default_status`, cfg.default_status || 'publish', 'select', {
                            items: [
                                {value: 'publish', text: '🟢 直接公开发布 (publish)'},
                                {value: 'draft', text: '🟡 存为本地草稿 (draft)'},
                                {value: 'pending', text: '🟠 等待人工审核 (pending)'}
                            ],
                            description: '同步到 WordPress 后的文章默认状态'
                        })}
                    </div>
                `;
            }
            // 🚀 2. Medium 卡片主配置定制与保姆级参数指导
            else if (id === 'medium') {
                html = `
                    <div class="settings-grid">
                        ${renderSettingsItem('通道激活', `syndication.medium.enabled`, cfg.enabled, 'checkbox', {description: '激活后，文章出版发布时将同步分发到 Medium。'})}
                        ${renderSettingsItem('访问凭据 (Integration Token)', `syndication.medium.integration_token`, cfg.integration_token || cfg.api_key, 'password', {placeholder: "请输入您的 Medium Integration Token", description: "【如何获取】登录 Medium 网页端，点击头像 -> Settings -> Security & Apps -> Integration Tokens 中申请生成"})}
                    </div>
                `;
            }
            // 🚀 3. Ghost 卡片主配置定制与保姆级参数指导
            else if (id === 'ghost') {
                html = `
                    <div class="settings-grid">
                        ${renderSettingsItem('通道激活', `syndication.ghost.enabled`, cfg.enabled, 'checkbox', {description: '激活后，文章出版发布时将同步分发到 Ghost 博客。'})}
                        ${renderSettingsItem('Ghost 平台 URL', `syndication.ghost.url`, cfg.url, 'text', {placeholder: "例如: https://myblog.ghost.io", description: "【如何获取】您 Ghost 站点的基本访问地址"})}
                        ${renderSettingsItem('Admin API Key', `syndication.ghost.api_key`, cfg.api_key, 'password', {placeholder: "请输入 Admin API Key", description: "【如何获取】登录 Ghost 后台 -> Settings -> Integrations -> 添加 Custom Integration，复制其中的 Admin API Key"})}
                    </div>
                `;
            }
            // 🚀 4. Hashnode 卡片主配置定制与保姆级参数指导
            else if (id === 'hashnode') {
                html = `
                    <div class="settings-grid">
                        ${renderSettingsItem('通道激活', `syndication.hashnode.enabled`, cfg.enabled, 'checkbox', {description: '激活后，文章出版发布时将同步分发到 Hashnode。'})}
                        ${renderSettingsItem('GraphQL API Token', `syndication.hashnode.api_key`, cfg.api_key, 'password', {placeholder: "请输入 Hashnode GraphQL Token", description: "【如何获取】登录 Hashnode 网页端 -> 点击头像 -> Account Settings -> Developer Settings 中生成个人 Token"})}
                    </div>
                `;
            }
            // 🚀 5. 通用兜底
            else {
                html = `
                    <div class="settings-grid">
                        ${renderSettingsItem('通道激活', p.category === 'hosting' ? `publish_control.direct_upload.${id}.enabled` : `syndication.${id}.enabled`, cfg.enabled, 'checkbox', {description: '开启后，当前激活的品牌将在执行出版发布任务时向该端点进行物理分发。'})}
                        ${renderSettingsItem('凭据/密钥 (Key/Token)', p.category === 'hosting' ? `publish_control.direct_upload.${id}.api_key` : `syndication.${id}.api_key`, cfg.api_key || cfg.app_password, 'password', {placeholder: "请输入访问令牌/API密钥"})}
                        ${renderSettingsItem('发布目标 (URL/Bucket)', p.category === 'hosting' ? `publish_control.direct_upload.${id}.url` : `syndication.${id}.url`, cfg.url, 'text', {placeholder: "请输入目标 URL 或存储桶名称"})}
                        ${renderSettingsItem('账号/ID', p.category === 'hosting' ? `publish_control.direct_upload.${id}.username` : `syndication.${id}.username`, cfg.username, 'text', {placeholder: "请输入账号名"})}
                    </div>
                `;
            }
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

    // 🚀 在 openPluginConfig 底部追加物理沙盒终端 HTML 占位区
    if (p && (p.category === 'publisher' || p.category === 'hosting') && id !== 'github_pages') {
        html += `
            <div id="sandbox-console-wrapper" style="display: none; margin-top: 25px; border-top: 1px solid var(--glass-border); padding-top: 15px;">
                <label class="tiny-label" style="color: var(--accent-secondary); margin-bottom: 8px; display: block; font-weight: 700; font-size: 0.7rem;">🧪 物理沙盒仿真演练终端 (Sandbox Emulation Terminal)</label>
                <div id="sandbox-console-terminal" style="background: rgba(0,0,0,0.55); border: 1px solid var(--glass-border); border-radius: 8px; padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00ff88; max-height: 180px; overflow-y: auto; line-height: 1.5; box-shadow: inset 0 0 10px rgba(0,0,0,0.7); scrollbar-width: thin;">
                    <!-- 滚动日志 -->
                </div>
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

    // 🚀 控制底部“🧪 沙盘演练”按钮的显示与绑定
    const dryRunBtn = document.getElementById('btn-dry-run-plugin');
    if (dryRunBtn) {
        dryRunBtn.style.display = 'block';
        dryRunBtn.setAttribute('onclick', `triggerPluginDryRun('${subId}', '${parentId}')`);
    }

    let subHtml = `
        <div class="sub-editor-header" style="margin-bottom: 1.5rem;">
            <button class="p-action-btn secondary" style="padding: 4px 10px; font-size: 0.75rem;" onclick="openPluginConfig('${parentId}')">⬅️ 返回通道列表</button>
            <h4 style="margin-top: 1rem; color: var(--accent-primary);">⚙️ 节点管理: ${subId.toUpperCase()}</h4>
        </div>
        <div class="settings-grid">
    `;

    if (parentId === 'webhook_gateway') {
        const endpoint = window.settingsData.publish_control?.webhook_endpoints?.[subId] || {};
        
        // 🚀 根据子渠道类型做描述与占位符优化
        let urlPlaceholder = "例如: https://hooks.slack.com/services/...";
        let desc = "开启后，当前激活的品牌将在执行出版发布任务时向该 Webhook 端点推送数据。";
        let hasSecret = true;

        if (subId === 'feishu') {
            urlPlaceholder = "例如: https://open.feishu.cn/open-apis/bot/v2/hook/...";
        } else if (subId === 'dingtalk') {
            urlPlaceholder = "例如: https://oapi.dingtalk.com/robot/send?access_token=...";
            hasSecret = false; // 钉钉使用签名称或自定义关键词，无需 secret
        } else if (subId === 'private_api') {
            urlPlaceholder = "例如: https://api.yourdomain.com/v1/publish-notify";
        }

        subHtml += `
            ${renderSettingsItem('通道激活', `publish_control.webhook_endpoints.${subId}.enabled`, endpoint.enabled, 'checkbox', {description: desc})}
            ${renderSettingsItem('物理端点 (URL)', `publish_control.webhook_endpoints.${subId}.url`, endpoint.url, 'text', {placeholder: urlPlaceholder})}
        `;
        if (hasSecret) {
            subHtml += `
                ${renderSettingsItem('主权密钥 (Secret / Sign Key)', `publish_control.webhook_endpoints.${subId}.secret`, endpoint.secret, 'password', {placeholder: "签名验证 Key (可选，防重放)"})}
            `;
        }
    } else {
        const cfg = window.settingsData.syndication?.[subId] || {};
        
        // 🚀 1. Medium 专有极简表单（完全剔除无关的 URL 与用户名，对准 integration_token）
        if (subId === 'medium') {
            subHtml += `
                ${renderSettingsItem('通道激活', `syndication.medium.enabled`, cfg.enabled, 'checkbox', {description: '开启后，文章出版发布时将自动分发至 Medium 平台。'})}
                ${renderSettingsItem('访问凭据 (Integration Token)', `syndication.medium.integration_token`, cfg.integration_token || cfg.api_key, 'password', {placeholder: "请输入在 Medium -> Settings -> Integration Tokens 申请的 Token"})}
            `;
        }
        // 🚀 2. WordPress 专业多字段表单（对准 api_url, username, application_password 与默认状态）
        else if (subId === 'wordpress') {
            subHtml += `
                ${renderSettingsItem('通道激活', `syndication.wordpress.enabled`, cfg.enabled, 'checkbox', {description: '开启后，文章出版发布时将自动同步并原地更新至您的自建 WordPress 网站。'})}
                ${renderSettingsItem('平台 REST API 地址', `syndication.wordpress.api_url`, cfg.api_url || cfg.url, 'text', {placeholder: "例如: https://yourdomain.com/wp-json/wp/v2"})}
                ${renderSettingsItem('管理员用户名', `syndication.wordpress.username`, cfg.username, 'text', {placeholder: "输入您在 WordPress 中的登录用户名，例如 admin"})}
                ${renderSettingsItem('应用密码 (Application Password)', `syndication.wordpress.application_password`, cfg.application_password || cfg.api_key, 'password', {placeholder: "请在 WordPress 用户资料页面生成 24 位应用密码（切勿输入登录密码）"})}
                ${renderSettingsItem('文章默认发布状态', `syndication.wordpress.default_status`, cfg.default_status || 'publish', 'select', {
                    items: [
                        {value: 'publish', text: '🟢 直接公开发布 (publish)'},
                        {value: 'draft', text: '🟡 存为本地草稿 (draft)'},
                        {value: 'pending', text: '🟠 等待人工审核 (pending)'}
                    ],
                    description: '同步到 WordPress 后的文章默认状态'
                })}
            `;
        }
        // 🚀 3. Ghost 专有表单
        else if (subId === 'ghost') {
            subHtml += `
                ${renderSettingsItem('通道激活', `syndication.ghost.enabled`, cfg.enabled, 'checkbox', {description: '开启后，文章出版发布时将自动同步至 Ghost 博客。'})}
                ${renderSettingsItem('Ghost 平台 URL', `syndication.ghost.url`, cfg.url, 'text', {placeholder: "例如: https://myblog.ghost.io"})}
                ${renderSettingsItem('Admin API Key', `syndication.ghost.api_key`, cfg.api_key, 'password', {placeholder: "请在 Ghost -> Integrations 中创建自定义集成并获取"})}
            `;
        }
        // 🚀 4. Hashnode 专有表单
        else if (subId === 'hashnode') {
            subHtml += `
                ${renderSettingsItem('通道激活', `syndication.hashnode.enabled`, cfg.enabled, 'checkbox', {description: '开启后，文章出版发布时将自动同步至 Hashnode 平台。'})}
                ${renderSettingsItem('GraphQL API Token', `syndication.hashnode.api_key`, cfg.api_key, 'password', {placeholder: "请在 Hashnode -> Account Settings -> Developer Settings 中生成 Token"})}
            `;
        }
        // 🚀 5. 其他通道通用兜底
        else {
            subHtml += `
                ${renderSettingsItem('通道激活', `syndication.${subId}.enabled`, cfg.enabled, 'checkbox', {description: '开启后，当前激活的品牌将在执行出版发布任务时向该分发端点推送数据。'})}
                ${renderSettingsItem('平台 URL (可选)', `syndication.${subId}.url`, cfg.url, 'text', {placeholder: "请输入端点 URL"})}
                ${renderSettingsItem('账号名/用户名', `syndication.${subId}.username`, cfg.username, 'text', {placeholder: "请输入账号名"})}
                ${renderSettingsItem('访问凭据 (Token/Key)', `syndication.${subId}.api_key`, cfg.api_key || cfg.app_password, 'password', {placeholder: "请输入访问令牌"})}
            `;
        }
    }

    subHtml += `
        </div>
        
        <!-- 🚀 追加子项编辑中的仿真终端组件 -->
        <div id="sandbox-console-wrapper" style="display: none; margin-top: 25px; border-top: 1px solid var(--glass-border); padding-top: 15px;">
            <label class="tiny-label" style="color: var(--accent-secondary); margin-bottom: 8px; display: block; font-weight: 700; font-size: 0.7rem;">🧪 物理沙盒仿真演练终端 (Sandbox Emulation Terminal)</label>
            <div id="sandbox-console-terminal" style="background: rgba(0,0,0,0.55); border: 1px solid var(--glass-border); border-radius: 8px; padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00ff88; max-height: 180px; overflow-y: auto; line-height: 1.5; box-shadow: inset 0 0 10px rgba(0,0,0,0.7); scrollbar-width: thin;">
                <!-- 滚动日志 -->
            </div>
        </div>

        <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--glass-border); display: flex; flex-direction: column; gap: 1rem;">
            <button class="primary-btn glow-btn" onclick="savePluginSettingsAndClose()">💾 保存节点配置</button>
            <p style="font-size: 0.7rem; color: var(--text-dim);">⚠️ 注意：修改将直接同步至物理配置文件，保存后请重启系统生效。</p>
        </div>
    `;

    body.innerHTML = subHtml;
};

// 🚀 物理沙盒干跑前端控制台交互算子（高保真流式淡入动画效果）
window.triggerPluginDryRun = async (id, parentId = null) => {
    const terminalWrapper = document.getElementById('sandbox-console-wrapper');
    const terminal = document.getElementById('sandbox-console-terminal');
    if (!terminalWrapper || !terminal) return;

    // 展现透明终端，启动脉冲动画
    terminalWrapper.style.display = 'block';
    terminal.innerHTML = '<div style="color: var(--accent-secondary); opacity: 0.8; font-style: italic; animation: pulse 1.5s infinite;">📡 物理演练通道点火中，正在抓取并对齐当前表单临时参数...</div>';
    
    // 自动滑动定位到演练面板
    terminalWrapper.scrollIntoView({ behavior: 'smooth' });

    // 抓取当前已修改但未保存的配置（与 updateConfigField 无缝联动）
    let settings = {};
    if (parentId === 'webhook_gateway') {
        settings = window.settingsData.publish_control?.webhook_endpoints?.[id] || {};
    } else if (parentId) {
        settings = window.settingsData.syndication?.[id] || {};
    } else {
        settings = window.settingsData.syndication?.[id] || window.settingsData.publish_control?.direct_upload?.[id] || {};
    }

    try {
        const res = await apiFetch('/api/plugins/dry-run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, parentId, settings })
        });

        if (!res || !res.logs) {
            terminal.innerHTML = '<div style="color: #ff4d4d; font-weight: bold;">❌ 物理沙箱干跑路由通信超时，未获得遥测回吐。</div>';
            return;
        }

        // 流式高科技模拟淡入，逐行打点
        terminal.innerHTML = '';
        let i = 0;
        const streamInterval = setInterval(() => {
            if (i >= res.logs.length) {
                clearInterval(streamInterval);
                return;
            }
            const log = res.logs[i];
            let color = '#d1d1d1'; // INFO
            if (log.level === 'WARN') color = '#ffaa00';
            else if (log.level === 'ERROR') color = '#ff4d4d';
            else if (log.level === 'SUCCESS') color = '#00ff88';

            const line = document.createElement('div');
            line.style.color = color;
            line.style.opacity = '0';
            line.style.transition = 'opacity 0.25s ease-out';
            line.style.marginBottom = '4px';
            line.innerText = `[${log.time}] [${log.level}] ${log.message}`;
            
            terminal.appendChild(line);
            
            // 触发微淡入并保持终端触底滚动
            setTimeout(() => { line.style.opacity = '1'; }, 10);
            terminal.scrollTop = terminal.scrollHeight;
            
            i++;
        }, 280); // 精雕细琢的 280ms 节奏，极其逼真的发布沙盘动态推演反馈

    } catch (e) {
        terminal.innerHTML = `<div style="color: #ff4d4d;">❌ 沙盘物理通信报错: ${e}</div>`;
    }
};

// 🚀 [V75.5] 100% 物理自愈：专门针对插件/通道抽屉配置设计的“强力同步保存并关闭”算子
window.savePluginSettingsAndClose = async () => {
    if (typeof addAudit === 'function') addAudit("💾 开始抓取当前面板临时参数并准备固化...");

    // 1. 强力抓取抽屉内所有 input 的当前最新状态，写入 window.settingsData
    const drawerBody = document.getElementById('p-drawer-body');
    if (drawerBody) {
        const inputs = drawerBody.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            const path = input.getAttribute('data-path');
            if (path) {
                let val;
                if (input.type === 'checkbox') {
                    val = input.checked;
                } else if (input.type === 'number') {
                    val = parseFloat(input.value);
                } else {
                    val = input.value;
                }
                
                // 写入 window.settingsData
                const keys = path.split('.');
                let current = window.settingsData;
                for (let i = 0; i < keys.length - 1; i++) {
                    if (!current[keys[i]]) current[keys[i]] = {};
                    current = current[keys[i]];
                }
                current[keys[keys.length - 1]] = val;
            }
        });
    }

    // 2. 调用后台保存接口落盘
    const fullConfig = typeof window.flattenObject === 'function' ? window.flattenObject(window.settingsData) : window.settingsData;
    const payload = {};
    
    Object.keys(fullConfig).forEach(key => {
        if (!key.split('.').some(part => part.startsWith('_'))) {
            payload[key] = fullConfig[key];
        }
    });

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit("✅ 插件配置已成功固化至物理磁盘。", 'success');
        if (res.active_config) {
            window.settingsData = { ...window.settingsData, ...res.active_config };
        }

        // 3. 弹出高保真玻璃磨砂通知，给用户强烈的物理确认视觉反馈！
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '💾 保存成功',
                text: '插件能力配置已成功固化并写入物理磁盘 config.yaml / config.local.yaml！',
                icon: 'success',
                confirmButtonText: '确定',
                background: 'var(--card-bg)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--accent-primary)'
            });
        }

        // 4. 自动关闭抽屉
        if (typeof closePluginDrawer === 'function') {
            closePluginDrawer();
        }

        // 5. 重新渲染插件矩阵列表，以刷新状态
        if (typeof renderPlugins === 'function') {
            renderPlugins();
        }
        
        // 6. 即时更新左侧身份及状态面板
        if (typeof refreshGovernanceContext === 'function') {
            await refreshGovernanceContext();
        }
    } else {
        const errMsg = res ? res.error : '物理链路异常';
        if (typeof addAudit === 'function') addAudit(`❌ 插件配置保存失败: ${errMsg}`, 'error');
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '❌ 保存失败',
                text: errMsg,
                icon: 'error',
                confirmButtonText: '了解',
                background: 'var(--card-bg)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--accent-primary)'
            });
        }
    }
};
