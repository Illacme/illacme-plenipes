/**
 * 🛰️ [V105.0] Illacme Plenipes Plugin Editor - Drawer Shell & Lifecycle Shard
 * 职责：插件配置抽屉主入口、数据提取、DOM 装配与抽屉关闭生命周期。
 */

(function () {
    window.closePluginDrawer = () => {
        const drawer = document.getElementById('plugin-drawer');
        if (drawer) drawer.style.display = 'none';
        window._syndicateReturnContext = null;
        window._vaultReturnContext = null;
        if (typeof window.updateDrawerReturnButtons === 'function') {
            window.updateDrawerReturnButtons();
        }
    };

    window.openPluginConfig = async (id, category = null, fromDrawer = null) => {
        try {
            const drawer = document.getElementById('plugin-drawer');
            const body = document.getElementById('p-drawer-body');
            const title = document.getElementById('p-drawer-title');

            if (!drawer || !body) return;

            // 🚀 [V104.0] 多抽屉压栈治理：强行提升配置抽屉的 z-index 为 10005，确保覆盖在其他抽屉 (如单篇广播 9999) 上方
            drawer.style.zIndex = '10005';

            // 🎯 严格隔离返回上下文：仅当显式声明从跨抽屉跳转入口打开时才保留对应上下文，否则彻底清空以防污染常规插件中心
            if (fromDrawer === 'syndicate') {
                window._vaultReturnContext = null;
            } else if (fromDrawer === 'vault') {
                window._syndicateReturnContext = null;
            } else {
                window._syndicateReturnContext = null;
                window._vaultReturnContext = null;
            }
            if (typeof window.updateDrawerReturnButtons === 'function') {
                window.updateDrawerReturnButtons();
            }

            if (!window.allPlugins || window.allPlugins.length === 0) {
                const fetchFunc = window.apiFetch || (async (url) => (await fetch(url)).json());
                try {
                    const res = await fetchFunc('/api/plugins/list');
                    if (res && res.plugins) window.allPlugins = res.plugins;
                } catch (e) {
                    console.warn("[Plugin Editor] Unable to auto-fetch plugin list:", e);
                }
            }
            if (!window.allPlugins) window.allPlugins = [];

            let p = window.allPlugins.find(x => x.id === id && (!category || x.category === category));
            if (!p) {
                p = window.allPlugins.find(x => x.id === id || x.id.replace(/_/g, '') === id.replace(/_/g, ''));
            }

            if (!p) {
                throw new Error(`在全域能力矩阵 (window.allPlugins) 中未探测到 ID 为 '${id}' 的能力。`);
            }

            // 🔒 纵深防卫：防止非本地品牌主题配置被强行调起
            if (p.category === 'theme' && p.location !== 'local') {
                if (typeof Swal !== 'undefined') {
                    Swal.fire({
                        title: '🔒 暂不可配置',
                        text: '只有已被部署且启用为“当前品牌库”的装帧主题才可以进行配置自定义。请先返回主题画廊同步并部署此主题！',
                        icon: 'warning',
                        background: 'var(--card-bg)',
                        color: 'var(--text-bright)',
                        confirmButtonText: '确定'
                    });
                } else {
                    alert('🔒 暂不可配置: 只有已被部署且启用为“当前品牌库”的装帧主题才可以进行配置自定义。');
                }
                return;
            }

            const brand = typeof window.getPlatformBrandBadge === 'function'
                ? window.getPlatformBrandBadge(p.id, p.category)
                : { icon: '⚙️', bg: 'rgba(0, 242, 254, 0.12)', border: 'rgba(0, 242, 254, 0.3)' };

            title.innerHTML = `
                <div style="display:inline-flex; align-items:center; gap:8px;">
                    <span class="p-title-badge" style="width:24px; height:24px; min-width:24px; border-radius:6px; display:inline-flex; align-items:center; justify-content:center; font-size:0.95rem; background:${brand.bg}; border:1px solid ${brand.border}; box-shadow: 0 1px 4px rgba(0,0,0,0.25);">${brand.icon}</span>
                    <span>${p.name || id}</span>
                </div>
            `;
            body.innerHTML = '<div class="loading">正在提取插件治理元数据...</div>';
            drawer.style.display = 'flex';

            if (!window.settingsData || Object.keys(window.settingsData).length === 0 || !window.governanceRules || Object.keys(window.governanceRules).length === 0) {
                const fetchFunc = window.apiFetch || (async (url) => (await fetch(url)).json());
                const res = await fetchFunc('/api/system/config');
                if (res) {
                    window.settingsData = res.config || res;
                    window.governanceRules = res.governance_rules || res._governance_rules || {};
                }
            }

            // 🚀 控制底部“🧪 沙盘演练 (测试连接)”按钮的显示与绑定
            const dryRunBtn = document.getElementById('btn-dry-run-plugin');
            if (dryRunBtn) {
                if (p && (p.category === 'publisher' || p.category === 'hosting' || p.category === 'image_hosting' || p.category === 'notification')) {
                    dryRunBtn.style.display = 'block';
                    dryRunBtn.setAttribute('onclick', `triggerPluginDryRun('${id}')`);
                } else {
                    dryRunBtn.style.display = 'none';
                }
            }

            let html = typeof window.renderCrossPluginReuseGuide === 'function' ? window.renderCrossPluginReuseGuide(id, p.category) : '';

            // 🛡️ 情境自适应：仅当从治理中心 (governance) 打开主题配置时隐藏全局驱动开关；在插件中心保留全局驱动启停开关
            const hideMasterSwitch = (fromDrawer === 'governance' && p.category === 'theme');
            if (p.is_manageable && !hideMasterSwitch) {
                const headerSwitch = document.getElementById('drawer-global-driver-toggle');
                const headerSwitchWrapper = document.getElementById('header-master-switch-wrapper');
                const headerStatusLabel = document.getElementById('header-toggle-status-label');

                window.probePassState = window.probePassState || {};

                if (headerSwitch) {
                    if (headerSwitchWrapper) headerSwitchWrapper.style.display = 'inline-flex';

                    const isCurrentlyEnabled = !!p.is_enabled;
                    headerSwitch.checked = isCurrentlyEnabled;

                    if (headerStatusLabel) {
                        headerStatusLabel.textContent = isCurrentlyEnabled ? '🟢 全局已启用' : '⚪ 全局已暂停';
                        headerStatusLabel.style.color = isCurrentlyEnabled ? 'var(--neon-cyan)' : 'var(--text-dim)';
                    }

                    headerSwitch.onchange = function (e) {
                        if (e && typeof e.stopPropagation === 'function') e.stopPropagation();
                        if (typeof window.handleGlobalDriverToggle === 'function') {
                            window.handleGlobalDriverToggle(p.id, this, p.category);
                        }
                    };
                }
            } else {
                const headerSwitchWrapper = document.getElementById('header-master-switch-wrapper');
                if (headerSwitchWrapper) headerSwitchWrapper.style.display = 'none';
            }

            // 🚀 [V105.0] 恢复三步极简向导 Tab Header
            if (['hosting', 'image_hosting', 'publisher', 'notification'].includes(p.category) && p.is_manageable) {
                if (typeof window.renderPluginStepWizardHeader === 'function') {
                    html += window.renderPluginStepWizardHeader(id, p.category);
                }
            }
            if (typeof window.buildPluginConfigFormHtml === 'function') {
                html += window.buildPluginConfigFormHtml(p);
            }

            if (!html) {
                html = `
                    <div class="empty-state">
                        <p>该能力目前遵循系统全息配置，暂无独立调节参数。</p>
                        <code style="font-size: 0.7rem; opacity: 0.5;">ID: ${id} | Origin: ${p.origin}</code>
                    </div>
                `;
            }

            if (p && (p.category === 'publisher' || p.category === 'hosting' || p.category === 'image_hosting' || p.category === 'notification')) {
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
            body.setAttribute('data-plugin-id', id);
            body.setAttribute('data-plugin-category', p.category || '');

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

            // 🚀 [V105.0] 物理结构重构：针对具有多步骤向导的插件 (托管, 图床, 出版) 恢复 Step 1 与 Step 2 发光卡片外框
            if (p.category !== 'notification' && typeof window.groupDrawerFormIntoStepCards === 'function') {
                window.groupDrawerFormIntoStepCards(body);
            }

            // 🚀 [V89.0] 脏数据失效逻辑
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

                    // 🚀 [V105.0] 输入框 Focus 智能反向联动 Step Wizard
                    input.addEventListener('focus', () => {
                        const path = input.getAttribute('data-path') || input.name || '';
                        if (path.includes('token') || path.includes('key') || input.type === 'password') {
                            if (typeof window.handleWizardStepClick === 'function') {
                                window.handleWizardStepClick(0, id, p.category);
                            }
                        } else if (path.includes('repo') || path.includes('bucket') || path.includes('domain') || path.includes('branch') || path.includes('path') || path.includes('url')) {
                            if (typeof window.handleWizardStepClick === 'function') {
                                window.handleWizardStepClick(1, id, p.category);
                            }
                        }
                    });
                }
            });

            // 🚀 默认全量激活 Step 0 卡片状态
            setTimeout(() => {
                if (typeof window.handleWizardStepClick === 'function') {
                    window.handleWizardStepClick(0, id, p.category);
                }
            }, 50);

            // 🚀 [V89.0] 视觉渐进式暴露联动
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
                        checkToggle();
                        customStyleSwitch.addEventListener('change', checkToggle);
                    }
                }, 50);
            }

            // 🚀 [V105.0] 动态静默探测剪贴板凭据合规性
            if (typeof window.asyncCheckClipboardForDrawerToken === 'function') {
                setTimeout(() => {
                    window.asyncCheckClipboardForDrawerToken(id);
                }, 150);
            }
        } catch (e) {
            console.error("🛑 提取插件治理元数据时遭遇系统中断:", e);
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '🚨 治理中枢异常',
                    text: `无法提取此项能力的配置元数据: ${e.message}`,
                    icon: 'error',
                    background: 'rgba(10, 15, 25, 0.98)',
                    color: 'var(--text-bright)',
                    confirmButtonText: '确定'
                });
            }
        }
    };
})();
