/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins Configuration Drawer
 * 职责：能力配置抽屉加载、SSG/S3/WordPress/Medium/Ghost/Hashnode 参数模板构建与多节点子渠道编辑。
 */
const renderSettingsItem = window.renderSettingsItem || (() => "");

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
    try {
        const drawer = document.getElementById('plugin-drawer');
        const body = document.getElementById('p-drawer-body');
        const title = document.getElementById('p-drawer-title');

        if (!drawer || !body) return;

        if (!window.allPlugins) window.allPlugins = [];
        const p = window.allPlugins.find(x => x.id === id);
        if (!p) {
            throw new Error(`在全域能力矩阵 (window.allPlugins) 中未探测到 ID 为 '${id}' 的能力。`);
        }

        // 🔒 纵深防卫：防止非本地版图主题配置被强行调起
        if (p.category === 'theme' && p.location !== 'local') {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '🔒 暂不可配置',
                    text: '只有已被部署且启用为“当前版图库”的装帧主题才可以进行配置自定义。请先返回主题画廊同步并部署此主题！',
                    icon: 'warning',
                    background: 'var(--card-bg)',
                    color: 'var(--text-bright)',
                    confirmButtonText: '确定'
                });
            } else {
                alert('🔒 暂不可配置: 只有已被部署且启用为“当前版图库”的装帧主题才可以进行配置自定义。');
            }
            return;
        }

        title.innerText = `⚙️ 配置能力: ${p.name || id}`;
        body.innerHTML = '<div class="loading">正在提取插件治理元数据...</div>';
        drawer.style.display = 'flex';

        if (!window.settingsData || Object.keys(window.settingsData).length === 0 || !window.governanceRules || Object.keys(window.governanceRules).length === 0) {
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
                    ${renderSettingsItem('主站点 URL', 'site_url', window.settingsData?.site_url)}
                    ${renderSettingsItem('导航深度', 'theme_config.nav_depth', window.settingsData?.theme_config?.nav_depth || 2, 'number')}
                    ${renderSettingsItem('强制暗色模式', 'theme_config.force_dark', window.settingsData?.theme_config?.force_dark, 'checkbox')}
                    <div class="full-width" style="margin-top: 1rem; border-top: 1px solid var(--glass-border); padding-top: 1rem;">
                        <label style="font-size: 0.75rem; color: var(--text-dim);">当前激活引擎</label>
                        <code style="display: block; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 8px; margin-top: 0.5rem;">${window.settingsData?.system?.ssg_engine || 'default'}</code>
                    </div>
                </div>
            `;
        } else if (p.category === 'publisher' || p.category === 'hosting') {
            const platform = p.platform || id;
            if (platform === 'github_pages') {
                html = `<div class="settings-grid">${renderSettingsItem('启用 GitHub Pages 同步', 'github_enabled', window.settingsData?.github_enabled, 'checkbox')}</div>`;
            } else if (platform === 's3') {
                html = `<div class="settings-grid">${renderSettingsItem('启用 S3 镜像存储', 's3_enabled', window.settingsData?.s3_enabled, 'checkbox')}</div>`;
            } else {
                const cfg = window.settingsData?.syndication?.[id] || {};
                html = `<div class="settings-grid">${window.renderPlatformConfig ? window.renderPlatformConfig(id, cfg, p.category) : renderPlatformConfig(id, cfg, p.category)}</div>`;
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
            
            html = '<div style="display: flex; flex-direction: column; gap: 1.2rem;">';
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

        if (p.type !== 'container' && p.category !== 'theme') {
            html += `
                <div class="settings-grid" style="margin-top: 1.5rem;">
                    ${renderSettingsItem('分发延迟补偿 (ms)', 'sync_delay', window.settingsData?.sync_delay, 'number')}
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
        
        // 🚀 [V74.96] 离线预检自愈与出厂设置绑定
        const restoreBtn = document.getElementById('btn-restore-plugin-defaults');
        if (restoreBtn) {
            if (p.category === 'theme') {
                restoreBtn.style.display = 'block';
                restoreBtn.setAttribute('onclick', `window.restoreThemeDefaults('${id}')`);
            } else {
                restoreBtn.style.display = 'none';
            }
        }
        
        // 🚀 [V74.96] 脏检查激活
        if (typeof window.initDrawerDirtySensing === 'function') {
            window.initDrawerDirtySensing();
        }
        
        // 🚀 [V89.0] 视觉渐进式暴露联动：如果存在自定义样式控制开关，默认隐藏繁冗的视觉参数，只有勾选启用时才温和渐显，大幅提纯人机交互的专注度
        if (p.category === 'theme') {
            setTimeout(() => {
                const customStyleSwitch = body.querySelector('[data-path$="enable_custom_style"]') || body.querySelector('[name$="enable_custom_style"]');
                const styleBlock = document.getElementById('theme-config-style-group-block');
                if (customStyleSwitch && styleBlock) {
                    const checkToggle = () => {
                        if (customStyleSwitch.checked) {
                            styleBlock.style.display = 'block';
                            setTimeout(() => {
                                styleBlock.style.opacity = '1';
                            }, 20);
                        } else {
                            styleBlock.style.opacity = '0';
                            styleBlock.style.display = 'none';
                        }
                    };
                    // 初始化状态校准
                    checkToggle();
                    // 绑定 change 事件
                    customStyleSwitch.addEventListener('change', checkToggle);
                }
            }, 50);
        }
    } catch (e) {
        console.error("🛑 提取插件治理元数据时遭遇系统中断:", e);
        Swal.fire({
            title: '🚨 治理中枢异常',
            text: `无法提取此项能力的配置元数据: ${e.message}`,
            icon: 'error',
            background: 'rgba(10, 15, 25, 0.98)',
            color: 'var(--text-bright)',
            confirmButtonText: '确定'
        });
    }
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

// 🚀 [V74.96] 脏状态感应机制
window.initDrawerDirtySensing = () => {
    const body = document.getElementById('p-drawer-body');
    if (!body) return;
    
    window.isDrawerDirty = false;
    const indicator = document.getElementById('drawer-dirty-indicator');
    if (indicator) indicator.style.display = 'none';
    
    const saveBtn = document.getElementById('btn-save-plugin-cfg');
    if (saveBtn) saveBtn.classList.remove('glow-active');

    const serializeState = () => {
        const obj = {};
        body.querySelectorAll('input, select, textarea').forEach(el => {
            if (el.name) {
                obj[el.name] = el.type === 'checkbox' ? el.checked : el.value;
            }
        });
        return JSON.stringify(obj);
    };

    window.initialDrawerState = serializeState();

    body.querySelectorAll('input, select, textarea').forEach(el => {
        const handler = () => {
            const currentState = serializeState();
            if (currentState !== window.initialDrawerState) {
                if (saveBtn) saveBtn.classList.add('glow-active');
                if (indicator) indicator.style.display = 'inline-flex';
                window.isDrawerDirty = true;
            } else {
                if (saveBtn) saveBtn.classList.remove('glow-active');
                if (indicator) indicator.style.display = 'none';
                window.isDrawerDirty = false;
            }
        };
        el.addEventListener('input', handler);
        el.addEventListener('change', handler);
    });
};

// 🚀 [V74.96] 一键恢复出厂默认值 (Restore Defaults)
window.restoreThemeDefaults = async (themeId) => {
    const result = await Swal.fire({
        title: '🧹 恢复出厂设置？',
        text: '这将会把当前主题的所有配置选项抹除，并还原为官方定义的原始默认值！',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '确定还原',
        cancelButtonText: '取消',
        background: 'rgba(10, 15, 25, 0.98)',
        color: 'var(--text-bright)'
    });
    
    if (result.isConfirmed) {
        const plugins = window.allPlugins || [];
        const theme = plugins.find(p => p.id === themeId);
        if (!theme || !theme.schema) {
             Swal.fire('🛑 错误', '未找到该主题的自描述定义，无法定位默认值！', 'error');
             return;
        }
        
        const props = theme.schema.properties || {};
        const payload = {};
        
        Object.keys(props).forEach(key => {
             if ('default' in props[key]) {
                 const defaultVal = props[key].default;
                 payload[`theme_options.${themeId}.options.${key}`] = defaultVal;
                 
                 const inputEl = document.querySelector(`[name="theme_options.${themeId}.options.${key}"]`);
                 if (inputEl) {
                     if (inputEl.type === 'checkbox') {
                         inputEl.checked = defaultVal;
                     } else {
                         inputEl.value = defaultVal;
                     }
                 }
             }
        });
        
        const res = await apiFetch('/api/config/update', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        if (res && res.status === 'success') {
            window.settingsData = { ...window.settingsData, ...res.active_config };
            window.isDrawerDirty = false;
            Swal.fire('✅ 已恢复', '主题已成功恢复出厂默认配置！', 'success');
            
            window.closePluginDrawer();
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('themes');
        } else {
            Swal.fire('🛑 恢复失败', res ? res.error : '网络链路阻塞', 'error');
        }
    }
};
