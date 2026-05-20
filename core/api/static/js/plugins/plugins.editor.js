/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins Configuration Drawer
 * 职责：能力配置抽屉加载、SSG/S3/WordPress/Medium/Ghost/Hashnode 参数模板构建与多节点子渠道编辑。
 */

// 🚀 集中归档平台/通道表单结构参数与描述模版
window.renderPlatformConfig = (id, cfg, category = 'publisher') => {
    if (id === 'wordpress') {
        return `
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
        `;
    } else if (id === 'medium') {
        return `
            ${renderSettingsItem('通道激活', `syndication.medium.enabled`, cfg.enabled, 'checkbox', {description: '激活后，文章出版发布时将同步分发到 Medium。'})}
            ${renderSettingsItem('访问凭据 (Integration Token)', `syndication.medium.integration_token`, cfg.integration_token || cfg.api_key, 'password', {placeholder: "请输入您的 Medium Integration Token", description: "【如何获取】登录 Medium 网页端，点击头像 -> Settings -> Security & Apps -> Integration Tokens 中申请生成"})}
        `;
    } else if (id === 'ghost') {
        return `
            ${renderSettingsItem('通道激活', `syndication.ghost.enabled`, cfg.enabled, 'checkbox', {description: '激活后，文章出版发布时将同步分发到 Ghost 博客。'})}
            ${renderSettingsItem('Ghost 平台 URL', `syndication.ghost.url`, cfg.url, 'text', {placeholder: "例如: https://myblog.ghost.io", description: "【如何获取】您 Ghost 站点的基本访问地址"})}
            ${renderSettingsItem('Admin API Key', `syndication.ghost.api_key`, cfg.api_key, 'password', {placeholder: "请输入 Admin API Key", description: "【如何获取】登录 Ghost 后台 -> Settings -> Integrations -> 添加 Custom Integration，复制其中的 Admin API Key"})}
        `;
    } else if (id === 'hashnode') {
        return `
            ${renderSettingsItem('通道激活', `syndication.hashnode.enabled`, cfg.enabled, 'checkbox', {description: '激活后，文章出版发布时将同步分发到 Hashnode。'})}
            ${renderSettingsItem('GraphQL API Token', `syndication.hashnode.api_key`, cfg.api_key, 'password', {placeholder: "请输入 Hashnode GraphQL Token", description: "【如何获取】登录 Hashnode 网页端 -> 点击头像 -> Account Settings -> Developer Settings 中生成个人 Token"})}
        `;
    } else {
        return `
            ${renderSettingsItem('通道激活', category === 'hosting' ? `publish_control.direct_upload.${id}.enabled` : `syndication.${id}.enabled`, cfg.enabled, 'checkbox', {description: '开启后，当前激活的品牌将在执行出版发布任务时向该端点进行物理分发。'})}
            ${renderSettingsItem('凭据/密钥 (Key/Token)', category === 'hosting' ? `publish_control.direct_upload.${id}.api_key` : `syndication.${id}.api_key`, cfg.api_key || cfg.app_password, 'password', {placeholder: "请输入访问令牌/API密钥"})}
            ${renderSettingsItem('发布目标 (URL/Bucket)', category === 'hosting' ? `publish_control.direct_upload.${id}.url` : `syndication.${id}.url`, cfg.url, 'text', {placeholder: "请输入目标 URL 或存储桶名称"})}
            ${renderSettingsItem('账号/ID', category === 'hosting' ? `publish_control.direct_upload.${id}.username` : `syndication.${id}.username`, cfg.username, 'text', {placeholder: "请输入账号名"})}
        `;
    }
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
            html = `<div class="settings-grid">${window.renderPlatformConfig(id, cfg, p.category)}</div>`;
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
        let urlPlaceholder = "例如: https://hooks.slack.com/services/...";
        let desc = "开启后，当前激活的品牌将在执行出版发布任务时向该 Webhook 端点推送数据。";
        let hasSecret = true;

        if (subId === 'feishu') {
            urlPlaceholder = "例如: https://open.feishu.cn/open-apis/bot/v2/hook/...";
        } else if (subId === 'dingtalk') {
            urlPlaceholder = "例如: https://oapi.dingtalk.com/robot/send?access_token=...";
            hasSecret = false;
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
        subHtml += window.renderPlatformConfig(subId, cfg, p.category);
    }

    subHtml += `
        </div>
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
