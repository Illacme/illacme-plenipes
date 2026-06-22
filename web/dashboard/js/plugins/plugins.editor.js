/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins Configuration Drawer
 * 职责：能力配置抽屉加载、SSG/S3/WordPress/Medium/Ghost/Hashnode 参数模板构建与多节点子渠道编辑。
 */
var renderSettingsItem = window.renderSettingsItem || (() => "");

// 🚀 集中归档平台/通道表单结构参数与描述模版
// 5. 插件配置抽屉
window.openPluginConfig = async (id, category = null) => {
    try {
        const drawer = document.getElementById('plugin-drawer');
        const body = document.getElementById('p-drawer-body');
        const title = document.getElementById('p-drawer-title');

        if (!drawer || !body) return;

        if (!window.allPlugins) window.allPlugins = [];
        const p = window.allPlugins.find(x => x.id === id && (!category || x.category === category));
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
            if (p && (p.category === 'publisher' || p.category === 'hosting' || p.category === 'image_hosting') && id !== 'github_pages') {
                dryRunBtn.style.display = 'block';
                dryRunBtn.setAttribute('onclick', `triggerPluginDryRun('${id}')`);
            } else {
                dryRunBtn.style.display = 'none';
            }
        }

        let html = '';

        if (p.is_manageable) {
            html += `
                <div class="settings-grid" style="margin-bottom: 1.5rem; padding-bottom: 1.2rem; border-bottom: 1px dashed var(--glass-border);">
                    <div class="setting-row level-local">
                        <div class="setting-info">
                            <div class="setting-label">🔌 全局物理驱动装载 (Global Driver) <span class="tier-tag tier-local">物理本地</span></div>
                            <div class="setting-desc">控制底层物理驱动是否装载。如果关闭，该功能将在全系统和所有品牌下被禁用且不加载其驱动代码（已被激活品牌绑定时会自动锁定）。</div>
                        </div>
                        <div class="setting-control">
                            <label class="p-switch">
                                <input type="checkbox" id="drawer-global-driver-toggle" ${p.is_enabled ? 'checked' : ''} onchange="window.handleGlobalDriverToggle('${p.id}', this, '${p.category}')" ${p.is_in_use ? 'disabled' : ''}>
                                <span class="p-slider round"></span>
                            </label>
                        </div>
                    </div>
                </div>
            `;
        }

        html += window.buildPluginConfigFormHtml(p);

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

        if (p && (p.category === 'publisher' || p.category === 'hosting' || p.category === 'image_hosting') && id !== 'github_pages') {
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
        
        // 🚀 [V89.0] 局部级联逻辑已被物理拆除，允许在全局驱动关闭状态下填写参数进行连通性探测自检

        // 🚀 [V89.0] 脏数据失效逻辑：一旦用户在配置抽屉中修改了任何物理参数，重置其自检通过状态，强制要求重新点击 📡 自检/🔌 测试连接 才能再次开启全局驱动
        const formInputs = body.querySelectorAll('input, select, textarea');
        formInputs.forEach(input => {
            if (input.id !== 'drawer-global-driver-toggle') {
                input.addEventListener('change', () => {
                    window.probePassState = window.probePassState || {};
                    window.probePassState[id] = false;
                    if (typeof addAudit === 'function') {
                        addAudit(`⚠️ [${id}] 配置参数已被修改，原物理连通性自检结论已失效。重新载入驱动前需再次完成 📡 自检/🧪 演练。`, 'warning');
                    }
                });
            }
        });
        
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

window.handleGlobalDriverToggle = async (id, el, category) => {
    const checked = el.checked;
    const p = window.allPlugins ? window.allPlugins.find(x => x.id === id && (!category || x.category === category)) : null;
    
    if (checked) {
        const needsProbe = ['protocol', 'publisher', 'hosting', 'image_hosting'].includes(category) && id !== 'github_pages';
        const isPassed = window.probePassState && window.probePassState[id] === true;
        
        if (needsProbe && !isPassed) {
            el.checked = false;
            
            // 级联置灰已物理移除，允许在全局驱动关闭时编辑参数进行探测自检
            
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '🔒 连通性未校验',
                    text: '请先在下方填写参数，并点击「📡 自检」或「🔌 测试连接」连通成功后，方可装载物理驱动。',
                    icon: 'warning',
                    background: 'var(--card-bg)',
                    color: 'var(--text-bright)',
                    confirmButtonText: '确定'
                });
            } else {
                alert('🔒 连通性未校验: 请先在下方填写参数，并点击「📡 自检/演练」连通成功后，方可装载物理驱动。');
            }
            return;
        }
    } else {
        if (p && p.is_in_use) {
            el.checked = true;
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '⚠️ 物理锁定',
                    text: '当前品牌已激活并正在使用此功能，禁止关闭全局物理驱动！如需停用，请先关闭当前品牌的“品牌激活使用”开关。',
                    icon: 'warning',
                    background: 'var(--card-bg)',
                    color: 'var(--text-bright)',
                    confirmButtonText: '确定'
                });
            } else {
                alert('⚠️ 物理锁定: 当前品牌已激活并正在使用此功能，禁止关闭全局物理驱动！如需停用，请先关闭当前品牌的“品牌激活使用”开关。');
            }
            return;
        }
    }
    
    await window.togglePlugin(id, checked, category);
};

