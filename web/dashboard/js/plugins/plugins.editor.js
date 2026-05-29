/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins Configuration Drawer
 * 职责：能力配置抽屉加载、SSG/S3/WordPress/Medium/Ghost/Hashnode 参数模板构建与多节点子渠道编辑。
 */
var renderSettingsItem = window.renderSettingsItem || (() => "");

// 🚀 集中归档平台/通道表单结构参数与描述模版
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
