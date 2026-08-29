/**
 * 💾 [V87.0] Illacme Plenipes Plugins Sandbox Saver & Validator
 * 职责：抽屉表单必填字段智能校验拦截、Token 防擦除强锁、参数收集与配置强力持久化落盘。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10]
 */

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

        // 特殊豁免 1：本地 AI 协议与内网私有化算力节点（lmstudio, ollama, localai 或 localhost/127.0.0.1）允许 API Key 为空
        const isLocalAIProto = ['ollama', 'lmstudio', 'localai'].includes(activePluginId) || (
            drawerBody && (
                (drawerBody.querySelector('[data-path*="base_url"]')?.value || '').includes('localhost') ||
                (drawerBody.querySelector('[data-path*="base_url"]')?.value || '').includes('127.0.0.1')
            )
        );
        if (isLocalAIProto && path.includes('api_key')) {
            continue;
        }

        // 特殊豁免 2：github_pages / gitee_pages / gitlab_pages 使用 SSH 探测免密时，token 允许为空
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
    const isLocalAIProto = ['ollama', 'lmstudio', 'localai'].includes(activePluginId) || (
        drawerBody && (
            (drawerBody.querySelector('[data-path*="base_url"]')?.value || '').includes('localhost') ||
            (drawerBody.querySelector('[data-path*="base_url"]')?.value || '').includes('127.0.0.1')
        )
    );

    if (drawerBody && !isLocalAIProto) {
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
