/**
 * 🧪 [V87.0] Illacme Plenipes Plugins Sandbox & Config Saver
 * 职责：物理沙盒干跑仿真、280ms 流式淡入终端日志渲染、以及 config.yaml 配置强力捕获与固化落盘。
 */

// 🚀 物理沙盒干跑前端控制台交互算子（高保真流式淡入动画效果）
window.triggerPluginDryRun = async (id, parentId = null) => {
    const terminalWrapper = document.getElementById('sandbox-console-wrapper');
    const terminal = document.getElementById('sandbox-console-terminal');
    if (!terminalWrapper || !terminal) return;

    // 展现透明终端，启动脉冲动画
    terminalWrapper.style.display = 'block';
    terminal.innerHTML = '<div style="color: #38bdf8; font-weight: 600; opacity: 0.95; font-style: italic; animation: pulse 1.5s infinite;">📡 物理通道连接测试中，正在抓取并对齐当前表单临时参数...</div>';
    
    // 自动滑动定位到测试终端 (仅在抽屉 body 容器内部滚动，防止外层 window 或整个抽屉浮层发生位移溢出)
    const drawerBody = document.getElementById('p-drawer-body');
    if (drawerBody) {
        drawerBody.scrollTo({
            top: drawerBody.scrollHeight,
            behavior: 'smooth'
        });
    }

    // 🚀 [Sovereign 实时抓取] 提取已落盘配置 + 强力合并抽屉当前 DOM 输入框的最新实时值
    let settings = {};
    if (window.settingsData) {
        settings = {
            ...(window.settingsData.image_hosting?.[id] || {}),
            ...(window.settingsData.publish_control?.direct_upload?.[id] || {}),
            ...(window.settingsData.syndication?.[id] || {})
        };
    }

    if (drawerBody) {
        drawerBody.querySelectorAll('input, select, textarea').forEach(input => {
            const path = input.getAttribute('data-path') || input.name;
            if (path && input.value !== undefined) {
                const parts = path.split('.');
                const key = parts[parts.length - 1];
                let val = input.value;
                if (input.type === 'checkbox') val = input.checked;
                else if (input.type === 'number') val = parseFloat(input.value) || 0;
                settings[key] = val;
            }
        });
    }

    try {
        const res = await apiFetch('/api/plugins/dry-run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, parentId, settings })
        });

        window.probePassState = window.probePassState || {};
        if (res && res.success) {
            window.probePassState[id] = true;
        } else {
            window.probePassState[id] = false;
        }

        if (!res || !res.logs) {
            terminal.innerHTML = '<div style="color: #ff4d4d; font-weight: bold;">❌ 物理通道连接测试超时，未获得连接反馈。</div>';
            return;
        }

        // 流式高科技模拟淡入，逐行打点
        terminal.innerHTML = '';
        let i = 0;
        const streamInterval = setInterval(() => {
            if (i >= res.logs.length) {
                clearInterval(streamInterval);

                // 🚀 [V106.0] 物理连通关卡标志同步
                window.probePassState = window.probePassState || {};
                if (res.success) {
                    window.probePassState[id] = true;
                } else {
                    window.probePassState[id] = false;
                }
                
                // 🔍 检查是否有依赖缺失的 Warn 级日志
                const hasDepWarning = res.logs.some(log => log.message.includes('install') || log.message.includes('安装') || log.message.includes('依赖库'));
                const oldContainer = document.getElementById('dep-install-container');
                if (oldContainer) oldContainer.remove();

                if (hasDepWarning) {
                    const installBox = document.createElement('div');
                    installBox.id = 'dep-install-container';
                    installBox.style.marginTop = '10px';
                    installBox.style.display = 'flex';
                    installBox.style.justifyContent = 'space-between';
                    installBox.style.alignItems = 'center';
                    installBox.style.padding = '8px 12px';
                    installBox.style.background = 'rgba(255, 170, 0, 0.1)';
                    installBox.style.border = '1px solid rgba(255, 170, 0, 0.3)';
                    installBox.style.borderRadius = '6px';
                    installBox.style.transition = 'opacity 0.3s ease-out';
                    
                    installBox.innerHTML = `
                        <span style="font-size: 0.72rem; color: #ffaa00;">检测到本地环境缺少该驱动所需的 Python 依赖包。</span>
                        <button id="btn-install-dep" class="p-btn" style="padding: 4px 10px; font-size: 0.7rem; background: var(--accent-primary); border-radius: 4px; color: var(--text-bright); border: none; cursor: pointer;" onclick="window.installPluginDependencies('${id}')">🔌 一键安装依赖</button>
                    `;
                    terminal.parentNode.appendChild(installBox);
                    
                    if (drawerBody) {
                        drawerBody.scrollTo({
                            top: drawerBody.scrollHeight,
                            behavior: 'smooth'
                        });
                    }
                }
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
        terminal.innerHTML = `<div style="color: #ff4d4d;">❌ 连接测试物理通信报错: ${e}</div>`;
    }
};

window.installPluginDependencies = async (id) => {
    const btn = document.getElementById('btn-install-dep');
    const container = document.getElementById('dep-install-container');
    const terminal = document.getElementById('sandbox-console-terminal');
    if (!btn || !terminal) return;

    btn.disabled = true;
    btn.innerText = '⏳ 正在安装中...';
    
    const addLogLine = (msg, level = 'INFO') => {
        const line = document.createElement('div');
        let color = '#d1d1d1';
        if (level === 'ERROR') color = '#ff4d4d';
        else if (level === 'SUCCESS') color = '#00ff88';
        line.style.color = color;
        line.style.marginBottom = '4px';
        const now = new Date().toTimeString().split(' ')[0];
        line.innerText = `[${now}] [${level}] ${msg}`;
        terminal.appendChild(line);
        terminal.scrollTop = terminal.scrollHeight;
    };

    addLogLine('🔑 物理触发一键依赖自愈管线，自动连接远端镜像源...', 'INFO');

    try {
        const res = await apiFetch('/api/plugins/install-deps', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        });

        if (res && res.success) {
            if (res.logs) {
                res.logs.forEach(l => {
                    addLogLine(l.message, l.level);
                });
            }
            addLogLine('🟢 物理依赖自动装载完成！将在 1.5 秒后自动为您重启「测试连接」...', 'SUCCESS');
            if (container) {
                setTimeout(() => {
                    container.style.opacity = '0';
                    setTimeout(() => container.remove(), 300);
                }, 1000);
            }
            setTimeout(() => {
                window.triggerPluginDryRun(id);
            }, 1500);
        } else {
            const errMsg = res ? (res.error || '依赖包部分安装失败') : '安装超时';
            if (res && res.logs) {
                res.logs.forEach(l => {
                    addLogLine(l.message, l.level);
                });
            }
            addLogLine(`❌ 依赖自动安装中止: ${errMsg}`, 'ERROR');
            btn.disabled = false;
            btn.innerText = '重新一键安装';
        }
    } catch (e) {
        addLogLine(`❌ 物理通信中断: ${e}`, 'ERROR');
        btn.disabled = false;
        btn.innerText = '重新一键安装';
    }
};

// 🚀 [必填字段校验拦截机制]
window.validatePluginDrawerForm = (drawerBody, activePluginId) => {
    if (!drawerBody) return { valid: true };

    const inputs = drawerBody.querySelectorAll('input, select, textarea');
    for (const input of inputs) {
        // 排除隐藏的、禁用的、checkbox/button/submit 等非文本录入框
        if (input.disabled || input.type === 'checkbox' || input.type === 'button' || input.type === 'submit') continue;
        if (input.classList.contains('console-search') || input.closest('.console-search')) continue;
        
        const path = (input.getAttribute('data-path') || input.name || '').toLowerCase();
        if (!path) continue;

        // 获取字段友好名称
        let label = input.getAttribute('data-label');
        if (!label) {
            const row = input.closest('.setting-row');
            if (row) {
                const labelEl = row.querySelector('.setting-label');
                if (labelEl) {
                    label = labelEl.innerText.replace(/[*\s]+$/, '').replace(/(本地|品牌|全局)/g, '').trim();
                }
            }
        }
        if (!label) {
            const lastPart = path.split('.').pop();
            label = lastPart.replace(/_/g, ' ').toUpperCase();
        }

        // 1. 显式标记了 required 或 data-required
        const isExplicitRequired = input.hasAttribute('required') || input.getAttribute('data-required') === 'true';

        // 2. 属于核心必要凭据字段（如 token, api_token, access_token, secret_key, application_password, admin_api_key 等）
        // 排除明确可选的字段（如 proxy, cname, prefix, acl, public_url, endpoint_url 等）
        const isOptionalField = path.includes('proxy') || path.includes('cname') || path.includes('prefix') || path.includes('acl') || path.includes('public_url') || path.includes('endpoint_url') || path.includes('git_user_name') || path.includes('git_user_email') || path.includes('description');
        
        const isCoreCredential = !isOptionalField && (
            path.includes('token') || path.includes('api_key') || path.includes('secret_key') ||
            path.includes('application_password') || path.includes('admin_api_key') ||
            (input.type === 'password' && !path.includes('proxy'))
        );

        // 3. 核心平台关键定位字段
        const isCorePlatformField = !isOptionalField && (
            (path.includes('.s3.bucket') || path.includes('.s3.access_key') || path.includes('.s3.secret_key')) ||
            (path.includes('.wordpress.api_url') || path.includes('.wordpress.username') || path.includes('.wordpress.application_password')) ||
            (path.includes('.ghost.url') || path.includes('.ghost.admin_api_key')) ||
            (path.includes('.aliyun_oss.bucket') || path.includes('.aliyun_oss.access_key_id') || path.includes('.aliyun_oss.access_key_secret') || path.includes('.aliyun_oss.endpoint')) ||
            (path.includes('.tencent_cos.bucket') || path.includes('.tencent_cos.secret_id') || path.includes('.tencent_cos.secret_key') || path.includes('.tencent_cos.region')) ||
            (path.includes('.cloudflare_pages.account_id') || path.includes('.cloudflare_pages.api_token') || path.includes('.cloudflare_pages.project_name')) ||
            (path.includes('.netlify.auth_token') || path.includes('.netlify.site_id')) ||
            (path.includes('.vercel.token') || path.includes('.vercel.project_id')) ||
            (path.includes('.hashnode.publication_id') || path.includes('.hashnode.access_token') || path.includes('.hashnode.token')) ||
            (path.includes('.linkedin.author_urn') || path.includes('.linkedin.access_token') || path.includes('.linkedin.token')) ||
            (path.includes('.lsky_pro.api_url') || path.includes('.lsky_pro.token') || path.includes('.lsky_pro.api_token'))
        );

        // 特殊豁免：github_pages / gitee_pages / gitlab_pages 使用 SSH 探测免密时，token 允许为空
        if ((path.includes('github_pages') || path.includes('gitee_pages') || path.includes('gitlab_pages')) && path.includes('token')) {
            if (window.githubSSHPassState === true || window.giteeSSHPassState === true || window.gitlabSSHPassState === true) {
                continue;
            }
        }

        const isRequired = isExplicitRequired || isCoreCredential || isCorePlatformField;

        if (isRequired) {
            const val = (input.value || '').trim();
            if (val === '') {
                return {
                    valid: false,
                    input: input,
                    label: label,
                    path: path
                };
            }
        }
    }

    return { valid: true };
};

// 🚀 [V75.5] 100% 物理自愈：专门针对插件/通道抽屉配置设计的“强力同步保存并关闭”算子
window.savePluginSettingsAndClose = async () => {
    const drawerBody = document.getElementById('p-drawer-body');

    // 获取当前正在编辑的插件定义对象
    const drawerTitle = document.getElementById('p-drawer-title');
    let activePluginId = null;
    if (drawerTitle && drawerTitle.innerText) {
        const match = drawerTitle.innerText.match(/⚙️ 配置(?:能力|节点|插件):?\s*(.*)/);
        if (match) activePluginId = match[1].toLowerCase().replace(/^[^\w]+/, '');
    }
    const pluginObj = (window.allPlugins && activePluginId) ? window.allPlugins.find(p => p.id === activePluginId || (p.name && p.name.toLowerCase() === activePluginId)) : null;

    // 🛡️ 必填字段校验拦截：无值时禁止保存并高亮提示
    const check = window.validatePluginDrawerForm(drawerBody, activePluginId);
    if (!check.valid && check.input) {
        // 自动展开对应的 Step 区域
        const path = check.path || '';
        if (typeof window.handleWizardStepClick === 'function' && pluginObj) {
            if (path.includes('token') || path.includes('key') || check.input.type === 'password') {
                window.handleWizardStepClick(0, activePluginId, pluginObj.category);
            } else {
                window.handleWizardStepClick(1, activePluginId, pluginObj.category);
            }
        }

        // 高亮错误输入框与发光边框
        check.input.style.border = '1px solid #ff4d4f';
        check.input.style.boxShadow = '0 0 10px rgba(255, 77, 79, 0.5)';
        check.input.style.background = 'rgba(255, 77, 79, 0.08)';
        check.input.focus();
        if (typeof check.input.scrollIntoView === 'function') {
            check.input.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        check.input.addEventListener('input', () => {
            check.input.style.border = '';
            check.input.style.boxShadow = '';
            check.input.style.background = '';
        }, { once: true });

        if (typeof window.showToast === 'function') {
            window.showToast(`⚠️ 请先填写必填字段 [${check.label}]`, 'warning');
        }
        return;
    }

    if (typeof addAudit === 'function') addAudit("💾 开始同步当前面板参数并准备保存...");

    // 🔍 1. 探测当前抽屉中是否将核心 Token 擦除了
    let tokenWasCleared = false;
    if (drawerBody) {
        const tokenInput = drawerBody.querySelector('input[name*="token"], input[name*="api_key"], input[name*="access_token"], input[name*="secret_key"], input[name*="integration_token"], input[name*="password"], input[data-path*="token"], input[data-path*="api_key"], input[data-path*="secret_key"]');
        if (tokenInput && tokenInput.value.trim() === '') {
            tokenWasCleared = true;
        }
    }

    if (tokenWasCleared && pluginObj) {
        if (pluginObj.is_in_use) {
            if (typeof Swal !== 'undefined') {
                Swal.fire({ title: '⚠️ 物理锁定拦截', text: `当前品牌正在激活使用 [${pluginObj.name || activePluginId.toUpperCase()}]，禁止清空鉴权 Token！如需清空，请先关闭品牌绑定。`, icon: 'warning', background: 'var(--card-bg)', color: 'var(--text-bright)', confirmButtonColor: 'var(--accent-primary)' });
            } else { alert(`⚠️ 物理锁定拦截: 当前品牌正在使用 [${pluginObj.name || activePluginId.toUpperCase()}]，禁止擦除 Token！`); }
            return;
        }
        if (pluginObj.is_enabled) {
            pluginObj.is_enabled = false;
            window.probePassState = window.probePassState || {};
            window.probePassState[pluginObj.id] = false;
            const masterToggle = drawerBody ? drawerBody.querySelector('#drawer-global-driver-toggle') : null;
            if (masterToggle) masterToggle.checked = false;
            if (typeof window.togglePlugin === 'function') await window.togglePlugin(pluginObj.id, false, pluginObj.category);
            if (typeof addAudit === 'function') addAudit(`⚠️ [${pluginObj.id}] 因 Token 被擦除，系统已全自动安全关闭物理总开关。`, 'warning');
        }
    }

    // 🚀 [V113.0] 物理强锁：防范全局总开关状态被抽屉局域收集遗漏，导致 enabled 被脏覆盖
    const globalMasterToggle = document.getElementById('drawer-global-driver-toggle');
    if (globalMasterToggle && activePluginId && pluginObj) {
        const isMasterEnabled = globalMasterToggle.checked;
        const catKey = pluginObj.category === 'publisher' ? 'syndication' : (pluginObj.category === 'hosting' ? 'publish_control.direct_upload' : pluginObj.category);
        if (catKey && window.settingsData) {
            const keys = catKey.split('.');
            let curr = window.settingsData;
            for (const k of keys) {
                if (!curr[k]) curr[k] = {};
                curr = curr[k];
            }
            if (!curr[activePluginId]) curr[activePluginId] = {};
            curr[activePluginId]['enabled'] = isMasterEnabled;
        }
    }

    if (drawerBody) {
        drawerBody.querySelectorAll('input, select, textarea').forEach(input => {
            const path = input.getAttribute('data-path');
            if (path) {
                let val = input.type === 'checkbox' ? input.checked : (input.type === 'number' ? (parseFloat(input.value) || 0) : input.value);
                const keys = path.split('.');
                let current = window.settingsData;
                for (let i = 0; i < keys.length - 1; i++) {
                    if (!current[keys[i]]) current[keys[i]] = {};
                    current = current[keys[i]];
                }
                const fieldName = keys[keys.length - 1];
                current[fieldName] = val;
                if (val === '') {
                    if (fieldName === 'token') { current['api_token'] = ''; current['access_token'] = ''; }
                    else if (fieldName === 'api_token' || fieldName === 'access_token') { current['token'] = ''; }
                }
            }
        });
    }

    const fullConfig = typeof window.flattenObject === 'function' ? window.flattenObject(window.settingsData) : window.settingsData;
    const payload = {};
    Object.keys(fullConfig).forEach(key => {
        if (!key.split('.').some(part => part.startsWith('_'))) payload[key] = fullConfig[key];
    });

    const res = await apiFetch('/api/config/update', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit("✅ 插件能力配置已成功保存并生效。", 'success');
        if (res.active_config) {
            window.settingsData = { ...window.settingsData, ...res.active_config };
            if (drawerBody) {
                drawerBody.querySelectorAll('input').forEach(input => {
                    const path = input.getAttribute('data-path');
                    if (path && input.value === '') {
                        const keys = path.split('.');
                        let cur = window.settingsData;
                        for (let i = 0; i < keys.length - 1; i++) { if (cur) cur = cur[keys[i]]; }
                        if (cur) cur[keys[keys.length - 1]] = '';
                    }
                });
            }
        }
        const ctx = window._syndicateReturnContext;
        if (ctx && typeof window.returnToSyndicateDrawer === 'function') {
            if (typeof window.showToast === 'function') {
                window.showToast('💾 插件配置已保存，已自动返回社媒渠道分发', 'success');
            }
            await window.returnToSyndicateDrawer();
        } else if (window._vaultReturnContext && typeof window.returnToVaultDrawer === 'function') {
            if (typeof window.showToast === 'function') {
                window.showToast('💾 插件配置已保存，已自动返回网页托管发布', 'success');
            }
            await window.returnToVaultDrawer();
        } else {
            if (typeof Swal !== 'undefined') {
                Swal.fire({ title: '💾 保存成功', text: '插件能力配置已成功保存，系统配置已即刻更新生效！', icon: 'success', confirmButtonText: '确定', background: 'var(--card-bg)', color: 'var(--text-bright)', confirmButtonColor: 'var(--accent-primary)' });
            }
            if (typeof closePluginDrawer === 'function') closePluginDrawer();
        }
        if (typeof loadPlugins === 'function') await loadPlugins(true);
        else if (typeof renderPlugins === 'function') renderPlugins();
        if (typeof refreshGovernanceContext === 'function') await refreshGovernanceContext();
    } else {
        const errMsg = res ? res.error : '物理链路异常';
        if (typeof addAudit === 'function') addAudit(`❌ 插件配置保存失败: ${errMsg}`, 'error');
        if (typeof Swal !== 'undefined') Swal.fire({ title: '❌ 保存失败', text: errMsg, icon: 'error', confirmButtonText: '了解', background: 'var(--card-bg)', color: 'var(--text-bright)', confirmButtonColor: 'var(--accent-primary)' });
    }
};
