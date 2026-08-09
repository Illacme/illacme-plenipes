window.SAME_PROVIDER_MAP = {
    'github': ['github_pages', 'github'],
    'github_pages': ['github', 'github_pages'],
    'gitee': ['gitee_pages', 'gitee'],
    'gitee_pages': ['gitee', 'gitee_pages'],
    's3': ['s3', 'aliyun_oss', 'tencent_cos'],
    'aliyun_oss': ['s3', 'aliyun_oss'],
    'tencent_cos': ['s3', 'tencent_cos']
};

window.renderCrossPluginReuseGuide = (id, category) => {
    const cfgData = window.settingsData || {};

    // 🎯 校验当前插件自身是否已经填有有效 Token
    let selfCfg = {};
    if (['github_pages', 'gitee_pages', 's3'].includes(id)) {
        selfCfg = cfgData.publish_control?.direct_upload?.[id] || {};
    } else if (['github', 'gitee', 'smms', 'aliyun_oss', 'tencent_cos'].includes(id)) {
        selfCfg = cfgData.image_hosting?.[id] || {};
    } else {
        selfCfg = cfgData.syndication?.[id] || {};
    }

    const selfToken = selfCfg.token || selfCfg.access_token || selfCfg.api_token || selfCfg.api_key || selfCfg.secret_key || selfCfg.password || '';

    // 如果当前插件自身已经配置过 Token，物理 0 渲染，不展示同源复用提示
    let reuseHtml = '';
    if (!selfToken) {
        const peers = window.SAME_PROVIDER_MAP ? window.SAME_PROVIDER_MAP[id] : null;
        if (peers) {
            const otherId = peers.find(x => x !== id);
            if (otherId) {
                let otherCfg = {};
                if (['github_pages', 'gitee_pages', 's3'].includes(otherId)) {
                    otherCfg = cfgData.publish_control?.direct_upload?.[otherId] || {};
                } else if (['github', 'gitee', 'smms', 'aliyun_oss', 'tencent_cos'].includes(otherId)) {
                    otherCfg = cfgData.image_hosting?.[otherId] || {};
                } else {
                    otherCfg = cfgData.syndication?.[otherId] || {};
                }

                const tokenVal = otherCfg.token || otherCfg.access_token || otherCfg.api_token || otherCfg.api_key || otherCfg.secret_key || otherCfg.password || '';
                if (tokenVal) {
                    reuseHtml = `
                        <div class="api-token-helper reuse-helper-card" style="margin-bottom: 12px; padding: 6px 12px; border-radius: 6px; border: 1px solid rgba(0, 242, 255, 0.25); background: rgba(0, 242, 254, 0.04); display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                            <div style="font-size: 0.78rem; color: var(--text-bright, #fff);">
                                <span style="color: var(--neon-cyan, #00f2fe); font-weight: 600;">💡 可同源复用:</span> 检测到 <b>${otherId.toUpperCase()}</b> 已有凭据
                            </div>
                            <button type="button" class="helper-btn" onclick="window.applyCrossPluginCredentials('${otherId}', '${id}', '${category}', this)" style="background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.35); color: var(--neon-cyan, #00f2fe); padding: 2px 8px; border-radius: 4px; cursor: pointer; font-size: 0.72rem; font-weight: 600;">📋 一键复用</button>
                        </div>
                    `;
                }
            }
        }
    }

    // 🚀 [5-Star Dynamic UX] 剪贴板动态挂载容器，初始物理 0 空间占用
    const clipContainerHtml = `<div id="drawer-clip-token-banner-wrapper"></div>`;
    return reuseHtml + clipContainerHtml;
};

// 🚀 [V105.0] 校验剪贴板文本是否符合特定插件 ID 的 Token 格式规则
window.isTokenMatchingPluginRules = (id, text) => {
    if (!text || typeof text !== 'string') return false;
    const clean = text.trim();
    if (clean.length < 8 || clean.length > 150 || clean.includes('\n') || clean.includes(' ')) return false;

    // 针对不同插件 ID 的专属特征规则判断
    if (['github', 'github_pages'].includes(id)) {
        return clean.startsWith('ghp_') || clean.startsWith('github_pat_') || /^[a-f0-9]{40}$/i.test(clean);
    }
    if (['gitlab', 'gitlab_pages'].includes(id)) {
        return clean.startsWith('glpat-');
    }
    if (['cloudflare_pages'].includes(id)) {
        return clean.startsWith('wrangler_') || /^[a-f0-9]{32,40}$/i.test(clean);
    }
    if (['devto'].includes(id)) {
        return clean.startsWith('devto_') || /^[a-zA-Z0-9_\-]{20,64}$/.test(clean);
    }
    if (['medium'].includes(id)) {
        return /^[a-f0-9]{60,68}$/i.test(clean) || /^[a-zA-Z0-9_\-]{30,80}$/.test(clean);
    }
    if (['lsky_pro'].includes(id)) {
        return clean.startsWith('Bearer ') || /^[0-9]+\|[a-zA-Z0-9]{40,}$/.test(clean);
    }

    // 通用预设规则（其他未列出插件）：无空格、非英文自然句子、长度 12 位以上的 Key/Token 字符串
    return /^[a-zA-Z0-9_\-\.\:\=\/]{12,128}$/.test(clean);
};

// 🚀 [V105.0] 动态静默探测剪贴板凭据合规性（只有输入框完全无值 且 满足当前插件Token规则 时才提示）
window.asyncCheckClipboardForDrawerToken = async (id) => {
    try {
        if (!navigator.clipboard || !navigator.clipboard.readText) return;
        const drawer = document.getElementById('plugin-drawer');
        if (!drawer) return;

        // 🎯 规则一：强制要求当前抽屉的 Token 输入框【完全无值/为空】！
        const tokenInput = drawer.querySelector('input[data-path*="token"], input[data-path*="api_key"], input[data-path*="secret_key"], input[type="password"]');
        if (!tokenInput || tokenInput.value.trim() !== '') return; // 已有任何内容直接物理 0 渲染退出！

        const text = (await navigator.clipboard.readText() || '').trim();

        // 🎯 规则二：强制要求剪贴板里的 Token 符合当前插件 id 的特定规则！
        if (!window.isTokenMatchingPluginRules(id, text)) return;

        const wrapper = document.getElementById('drawer-clip-token-banner-wrapper');
        if (!wrapper) return;

        wrapper.innerHTML = `
            <div class="api-token-helper clip-sense-card" style="margin-bottom: 12px; padding: 6px 12px; border-radius: 6px; border: 1px solid rgba(0, 255, 136, 0.3); background: rgba(0, 255, 136, 0.04); display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                <div style="font-size: 0.78rem; color: var(--text-bright, #fff);">
                    <span style="color: #00ff88; font-weight: 600;">📋 剪贴板捕获:</span> 发现符合 ${id.toUpperCase()} 规则的凭据 <code style="background: rgba(0,0,0,0.3); color: #00ff88; padding: 1px 5px; border-radius: 3px;">${text.slice(0, 10)}...</code>
                </div>
                <button type="button" class="helper-btn" onclick="window.injectClipboardTextToDrawerToken('${text}', this)" style="background: rgba(0, 255, 136, 0.18); border: 1px solid rgba(0, 255, 136, 0.4); color: #00ff88; padding: 2px 8px; border-radius: 4px; cursor: pointer; font-size: 0.72rem; font-weight: 600;">📋 智能填入</button>
            </div>
        `;
    } catch (e) { }
};

// 🚀 [V105.0] 剪贴板 Token 精准直投回填算子
window.injectClipboardTextToDrawerToken = (tokenText, btn = null) => {
    const drawer = document.getElementById('plugin-drawer') || document;
    const tokenInput = drawer.querySelector('input[data-path*="token"], input[data-path*="api_key"], input[data-path*="secret_key"], input[data-path*="password"], input[name*="token"], input[type="password"]');
    if (tokenInput && tokenText) {
        tokenInput.value = tokenText;
        tokenInput.dispatchEvent(new Event('input', { bubbles: true }));
        tokenInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        tokenInput.focus();
        tokenInput.style.transition = 'all 0.3s';
        tokenInput.style.outline = '2px solid #00ff88';
        tokenInput.style.boxShadow = '0 0 15px rgba(0, 255, 136, 0.6)';
        setTimeout(() => {
            tokenInput.style.outline = '';
            tokenInput.style.boxShadow = '';
        }, 1500);

        if (btn) {
            btn.innerText = '✅ 已成功填入！';
            btn.style.background = 'rgba(0, 255, 136, 0.35)';
            setTimeout(() => {
                const card = btn.closest('.clip-sense-card');
                if (card) card.remove();
            }, 1000);
        }

        if (window.showToast) {
            window.showToast("🟢 已成功将剪贴板 Token 智能填入！", "success");
        }
    } else {
        if (window.showToast) {
            window.showToast("⚠️ 未在当前抽屉定位到 Token 输入框", "warning");
        }
    }
};

window.applyCrossPluginCredentials = (sourceId, targetId, category, btn = null) => {
    const cfgData = window.settingsData || {};
    let srcCfg = {};
    if (['github_pages', 'gitee_pages', 's3'].includes(sourceId)) {
        srcCfg = cfgData.publish_control?.direct_upload?.[sourceId] || {};
    } else if (['github', 'gitee', 'smms', 'aliyun_oss', 'tencent_cos'].includes(sourceId)) {
        srcCfg = cfgData.image_hosting?.[sourceId] || {};
    } else {
        srcCfg = cfgData.syndication?.[sourceId] || {};
    }

    const tokenVal = srcCfg.token || srcCfg.access_token || srcCfg.api_token || srcCfg.api_key || srcCfg.secret_key || srcCfg.password || '';
    const userVal = srcCfg.git_user_name || srcCfg.username || srcCfg.user || '';
    const emailVal = srcCfg.git_user_email || srcCfg.email || '';
    const rawRepoUrl = srcCfg.repo_url || srcCfg.repo || '';

    // 🚀 [Sovereign 智能清洗] 从 git@github.com:owner/repo.git 或 https://github.com/owner/repo.git 洗出 owner/repo 格式
    let cleanRepo = '';
    if (rawRepoUrl) {
        const match = rawRepoUrl.match(/(?:github|gitee)\.com[:/]([^/]+\/[^/]+?)(?:\.git)?$/i);
        if (match) cleanRepo = match[1];
        else if (rawRepoUrl.includes('/') && !rawRepoUrl.includes(':')) cleanRepo = rawRepoUrl;
    }

    let filledCount = 0;
    const drawer = document.getElementById('plugin-drawer') || document;

    const tokenInput = drawer.querySelector('input[data-path*="token"], input[data-path*="secret_key"], input[data-path*="api_key"], input[data-path*="password"], input[name*="token"], input[name*="access_token"], input[type="password"]');
    if (tokenInput && tokenVal) {
        tokenInput.value = tokenVal;
        tokenInput.dispatchEvent(new Event('input', { bubbles: true }));
        tokenInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        tokenInput.focus();
        tokenInput.style.transition = 'all 0.3s';
        tokenInput.style.outline = '2px solid #00ff88';
        tokenInput.style.boxShadow = '0 0 15px rgba(0, 255, 136, 0.6)';
        setTimeout(() => {
            tokenInput.style.outline = '';
            tokenInput.style.boxShadow = '';
        }, 1500);
        filledCount++;
    }

    const repoInput = drawer.querySelector('input[data-path*="repo"]');
    if (repoInput && cleanRepo) {
        repoInput.value = cleanRepo;
        repoInput.dispatchEvent(new Event('input', { bubbles: true }));
        filledCount++;
    }

    const userInput = drawer.querySelector('input[data-path*="username"], input[name*="git_user_name"], input[name*="username"]');
    if (userInput && userVal) {
        userInput.value = userVal;
        userInput.dispatchEvent(new Event('input', { bubbles: true }));
        filledCount++;
    }

    const emailInput = drawer.querySelector('input[data-path*="email"], input[name*="git_user_email"]');
    if (emailInput && emailVal) {
        emailInput.value = emailVal;
        emailInput.dispatchEvent(new Event('input', { bubbles: true }));
        filledCount++;
    }

    if (btn) {
        const origText = btn.innerText;
        btn.innerText = '✅ 已成功一键同源复用！';
        btn.style.background = 'rgba(0, 255, 136, 0.35)';
        btn.style.borderColor = '#00ff88';
        setTimeout(() => {
            btn.innerText = origText;
            btn.style.background = 'rgba(0, 255, 136, 0.18)';
            btn.style.borderColor = 'rgba(0, 255, 136, 0.4)';
        }, 1500);
    }

    if (window.showToast) {
        window.showToast(`🟢 成功复用 [${sourceId.toUpperCase()}] 凭据并自动清洗填入 ${filledCount} 项！`, 'success');
    }
};

window.resetDrawerConfig = (id) => {
    if (confirm(`确认擦除重置 [${id.toUpperCase()}] 渠道当前的所有文本配置？`)) {
        const drawer = document.getElementById('plugin-drawer');
        if (!drawer) return;
        drawer.querySelectorAll('input[type="text"], input[type="password"], textarea').forEach(input => {
            input.value = '';
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
        if (window.showToast) window.showToast("已清空擦除当前平台的草稿参数", "info");
    }
};

// 5. 插件配置抽屉
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

        title.innerText = `⚙️ ${p.name || id}`;
        body.innerHTML = '<div class="loading">正在提取插件治理元数据...</div>';
        drawer.style.display = 'flex';

        if (!window.settingsData || Object.keys(window.settingsData).length === 0 || !window.governanceRules || Object.keys(window.governanceRules).length === 0) {
            const res = await apiFetch('/api/system/config');
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

        let html = window.renderCrossPluginReuseGuide(id, p.category);

        if (p.is_manageable) {
            if (typeof window.renderPluginStepWizardHeader === 'function' && p.category !== 'notification') {
                html += window.renderPluginStepWizardHeader(p.id, p.category);
            }
        }

        // 🚀 [V106.0] 方案 1：Master Switch 移至抽屉 Header 标题右侧 + 强防线关卡
        const headerSwitch = document.getElementById('drawer-global-driver-toggle');
        const headerSwitchWrapper = document.getElementById('header-master-switch-wrapper');
        const headerStatusLabel = document.getElementById('header-toggle-status-label');

        window.probePassState = window.probePassState || {};

        if (headerSwitch) {
            if (p.is_manageable) {
                if (headerSwitchWrapper) headerSwitchWrapper.style.display = 'inline-flex';

                // 若插件本身在后端已经是 is_enabled 状态，默认视作已被证明的物理通过状态
                if (p.is_enabled) {
                    window.probePassState[p.id] = true;
                }

                const isCurrentlyEnabled = !!p.is_enabled;
                headerSwitch.checked = isCurrentlyEnabled;

                // 强制修正 Label 文字与 CSS 风格，彻底解决视觉与实际 Switch 错配问题
                if (headerStatusLabel) {
                    headerStatusLabel.textContent = isCurrentlyEnabled ? '🟢 全局已启用' : '⚪ 全局已暂停';
                    headerStatusLabel.style.color = isCurrentlyEnabled ? 'var(--neon-cyan)' : 'var(--text-dim)';
                }

                headerSwitch.onchange = function(e) {
                    const isAttemptingEnable = this.checked;
                    const isPassed = !!window.probePassState[p.id];

                    if (isAttemptingEnable) {
                        // 🛡️ 物理强制关卡：如果没有测试连接通过记录，强行拦截弹回关闭！
                        if (!isPassed) {
                            this.checked = false;
                            if (headerStatusLabel) {
                                headerStatusLabel.textContent = '⚪ 全局已暂停';
                                headerStatusLabel.style.color = 'var(--text-dim)';
                            }

                            if (typeof Swal !== 'undefined') {
                                Swal.fire({
                                    title: '🚨 无法开启全局驱动',
                                    html: `插件 [<b>${p.name || p.id}</b>] 尚未通过物理连通性校验。<br><br><span style="color:#00f2ff; font-size:0.85rem;">💡 请先点击抽屉底部的 <b>「🔌 测试连接」</b> 完成链路验证！</span>`,
                                    icon: 'warning',
                                    confirmButtonText: '⚡ 立即测试连通性',
                                    showCancelButton: true,
                                    cancelButtonText: '取消',
                                    background: 'var(--card-bg)',
                                    color: 'var(--text-bright)',
                                    confirmButtonColor: 'var(--accent-secondary)'
                                }).then((r) => {
                                    if (r.isConfirmed && typeof window.triggerPluginDryRun === 'function') {
                                        window.triggerPluginDryRun(p.id);
                                    }
                                });
                            } else if (window.showToast) {
                                window.showToast("🚨 请先点击「🔌 测试连接」完成链路验证", "error");
                            }
                            return;
                        }

                        // 通过验证，物理允许开启
                        if (headerStatusLabel) {
                            headerStatusLabel.textContent = '🟢 全局已启用';
                            headerStatusLabel.style.color = 'var(--neon-cyan)';
                        }
                        window.handleGlobalDriverToggle(p.id, this, p.category);
                    } else {
                        // 允许手动暂停
                        if (headerStatusLabel) {
                            headerStatusLabel.textContent = '⚪ 全局已暂停';
                            headerStatusLabel.style.color = 'var(--text-dim)';
                        }
                        window.handleGlobalDriverToggle(p.id, this, p.category);
                    }
                };
            } else {
                if (headerSwitchWrapper) headerSwitchWrapper.style.display = 'none';
            }
        }

        html += window.buildPluginConfigFormHtml(p);

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

                // 🚀 [V105.0] 输入框 Focus 智能反向联动 Step Wizard
                input.addEventListener('focus', () => {
                    const path = input.getAttribute('data-path') || input.name || '';
                    if (path.includes('token') || path.includes('key') || input.type === 'password') {
                        window.handleWizardStepClick(0, id, p.category);
                    } else if (path.includes('repo') || path.includes('bucket') || path.includes('domain') || path.includes('branch') || path.includes('path') || path.includes('url')) {
                        window.handleWizardStepClick(1, id, p.category);
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

        // 🚀 [V105.0] 动态静默探测剪贴板凭据合规性（只在存在有效 Token 且当前未填时精准静默滑出）
        if (typeof window.asyncCheckClipboardForDrawerToken === 'function') {
            setTimeout(() => {
                window.asyncCheckClipboardForDrawerToken(id);
            }, 150);
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
    window._syndicateReturnContext = null;
    window._vaultReturnContext = null;
    if (typeof window.updateDrawerReturnButtons === 'function') {
        window.updateDrawerReturnButtons();
    }
};

window.handleGlobalDriverToggle = async (id, el, category) => {
    const checked = el.checked;
    const p = window.allPlugins ? window.allPlugins.find(x => x.id === id && (!category || x.category === category)) : null;

    if (checked) {
        const needsProbe = ['protocol', 'publisher', 'hosting', 'image_hosting'].includes(category);
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

// 🚀 [V105.0] 复杂平台分类感知 3 步引导配置向导 Component
// 🚀 [V105.0] 复杂平台分类感知 3 步引导配置向导步骤名称映射提取器
window.getPluginWizardSteps = (pluginId, category = '') => {
    const specificStepsMap = {
        'devto': ['1. 个人 API Key 凭据', '2. 默认发布偏好模式', '3. 连通测试与保存'],
        'dev_to': ['1. 个人 API Key 凭据', '2. 默认发布偏好模式', '3. 连通测试与保存'],
        'wordpress': ['1. API 端点与应用密码', '2. 默认文章发布状态', '3. 连通测试与保存'],
        'medium': ['1. Integration Token 凭据', '2. 默认状态与发布偏好', '3. 连通测试与保存'],
        'hashnode': ['1. GraphQL API Token 凭据', '2. Publication 专栏绑定', '3. 连通测试与保存'],
        'ghost': ['1. Admin API Key & URL', '2. 模板与装帧偏好设置', '3. 连通测试与保存'],
        'wechat': ['1. 公众号 AppID/Secret 凭据', '2. 独立代理与图文设置', '3. 连通测试与保存'],
        'zhihu': ['1. 个人 Token / 专栏 ID', '2. 独立代理与发布偏好', '3. 连通测试与保存'],
        'telegram': ['1. Bot Token 机器人凭据', '2. 目标 Chat ID 频道参数', '3. 连通测试与保存'],
        'discord': ['1. Webhook 授权回调地址', '2. 提醒与独立代理参数', '3. 连通测试与保存'],
        'github_pages': ['1. 个人 Access Token 凭据', '2. 仓库 URL 与部署分支', '3. CNAME 与 Git 身份参数'],
        'gitee_pages': ['1. Gitee 私人 Access Token', '2. 仓库 URL 与部署分支', '3. 独立代理与 Git 身份'],
        'gitlab_pages': ['1. Personal Access Token', '2. 仓库 URL 与部署分支', '3. 独立代理与 Git 身份'],
        'sftp': ['1. 服务器主机与登录凭据', '2. 远程部署目录与域名', '3. 连通测试与保存'],
        'vercel': ['1. Vercel Access Token 凭据', '2. 项目名称与组织 ID 参数', '3. 生产部署与代理参数'],
        'netlify': ['1. Netlify Access Token 凭据', '2. Site ID 与部署分支参数', '3. 生产部署与代理参数'],
        'cloudflare_pages': ['1. Cloudflare API Token 凭据', '2. 项目名称与账号 ID 参数', '3. 部署分支与代理参数'],
        'firebase': ['1. Firebase CI Token 凭据', '2. 项目 ID 与 Site ID 参数', '3. 代理与部署测试'],
        'railway': ['1. Deploy Hook 触发地址', '2. 关联 Git 部署拓展参数', '3. 触发测试与保存'],
        'render': ['1. Deploy Hook 触发地址', '2. API Key 与代理拓展参数', '3. 触发测试与保存'],
        'zeabur': ['1. Deploy Hook 触发地址', '2. API Token 与代理拓展参数', '3. 触发测试与保存'],
        's3': ['1. AccessKey 身份凭据', '2. Bucket 存储桶与访问域名', '3. Endpoint 与 ACL 扩展参数'],
        'qiniu': ['1. 七牛云 AK/SK 密钥凭据', '2. 存储空间 Bucket 与访问域名', '3. 连通测试与保存'],
        'upyun': ['1. 操作员账号与授权密码', '2. 服务名称 Bucket 与访问域名', '3. 连通测试与保存']
    };

    const cat = (category || '').toLowerCase();
    const pid = (pluginId || '').toLowerCase();

    let steps = specificStepsMap[pid];
    if (!steps) {
        if (cat === 'hosting') {
            steps = ['1. 平台 API Token 凭据', '2. 仓库与域名扩展参数', '3. 测试连通与保存'];
        } else if (cat === 'image_hosting') {
            steps = ['1. 存储 Key/密钥凭据', '2. 存储桶 Bucket 与访问域名', '3. 测试连通与保存'];
        } else if (cat === 'notification') {
            steps = ['1. 消息端点/授权凭据', '2. 提醒与样式偏好参数', '3. 测试连通与保存'];
        } else if (cat === 'publisher') {
            steps = ['1. 访问 Token/密钥凭据', '2. 默认发布偏好参数', '3. 测试连通与保存'];
        } else if (cat === 'protocol' || pid.includes('ai') || pid.includes('llm')) {
            steps = ['1. API Key 与服务端点', '2. 采样与提示词策略', '3. 校验模型与保存'];
        } else if (cat === 'ssg' || cat === 'theme') {
            steps = ['1. 基础全局设置', '2. 视觉样式与装帧配置', '3. 预览生成与保存'];
        } else {
            steps = ['1. 账号与授权凭据', '2. 选项与存储参数', '3. 测试连通与保存'];
        }
    }
    return steps;
};

// 🚀 [V105.0] 复杂平台分类感知 3 步引导配置向导 Component
window.renderPluginStepWizardHeader = (pluginId, category = '') => {
    const steps = window.getPluginWizardSteps(pluginId, category);

    return `
        <div class="plugin-wizard-header" style="margin-bottom: 16px; padding: 12px 14px; background: rgba(0, 242, 255, 0.04); border: 1px solid rgba(0, 242, 255, 0.25); border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 0.82rem; font-weight: 700; color: var(--neon-cyan);">🧙 3 步极简向导 (Step Wizard)</span>
                <span style="font-size: 0.68rem; color: var(--neon-cyan); opacity: 0.8; font-weight: 600;">👉 点击步骤节点直达表单位置</span>
            </div>
            <div class="wizard-steps-container" style="display: flex; gap: 6px; font-size: 0.72rem; margin-bottom: 8px;">
                <div class="wiz-step active" data-step="0" onclick="window.handleWizardStepClick(0, '${pluginId}', '${category}', this)" style="flex: 1; padding: 6px; border-radius: 6px; background: rgba(0, 242, 255, 0.18); color: var(--neon-cyan); text-align: center; font-weight: 700; border: 1px solid var(--neon-cyan); cursor: pointer; transition: all 0.2s;">${steps[0]}</div>
                <div class="wiz-step" data-step="1" onclick="window.handleWizardStepClick(1, '${pluginId}', '${category}', this)" style="flex: 1; padding: 6px; border-radius: 6px; background: rgba(255, 255, 255, 0.04); color: var(--text-dim); text-align: center; font-weight: 500; border: 1px solid rgba(255, 255, 255, 0.1); cursor: pointer; transition: all 0.2s;">${steps[1]}</div>
                <div class="wiz-step" data-step="2" onclick="window.handleWizardStepClick(2, '${pluginId}', '${category}', this)" style="flex: 1; padding: 6px; border-radius: 6px; background: rgba(255, 255, 255, 0.04); color: var(--text-dim); text-align: center; font-weight: 500; border: 1px solid rgba(255, 255, 255, 0.1); cursor: pointer; transition: all 0.2s;">${steps[2]}</div>
            </div>
            <div id="wiz-mission-banner" style="font-size: 0.75rem; color: #00ff88; background: rgba(0, 255, 136, 0.06); border: 1px dashed rgba(0, 255, 136, 0.3); padding: 6px 10px; border-radius: 6px; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                <span>🎯 当前步骤 [1/3]：请在下方填写凭据 Token/Key 或使用一键复用</span>
            </div>
        </div>
    `;
};

// 🚀 [V105.0] 物理结构分组大卡片包装器 (全能力与授权向导全量无死角适配 + 严格 DOM 安全防环断言)
window.groupDrawerFormIntoStepCards = (drawerBody) => {
    if (!drawerBody || drawerBody.querySelector('.wiz-step-card')) return;

    const pluginId = drawerBody.getAttribute('data-plugin-id') || '';
    const category = drawerBody.getAttribute('data-plugin-category') || '';
    const steps = window.getPluginWizardSteps(pluginId, category);
    const step0Title = steps[0].replace(/^[0-9]+\.\s*/, '');
    const step1Title = steps[1].replace(/^[0-9]+\.\s*/, '');

    // 安全断言：判断一个 div 是否是合法的向导卡片（严禁包含主容器节点，避免循环嵌套崩溃）
    const isSafeGuideCard = (div) => {
        if (!div || div.nodeType !== 1) return false;
        if (div.classList.contains('settings-grid') || div.classList.contains('wiz-cards-wrapper') || div.classList.contains('plugin-wizard-header')) return false;
        if (div.id === 'plugin-drawer' || div.id === 'p-drawer-body' || div.id === 'sandbox-console-wrapper') return false;
        // 如果内部包含了全局总开关或包含了主配置网格，绝对不能当作向导卡片移动
        if (div.querySelector('#drawer-global-driver-toggle, .settings-grid, .wiz-cards-wrapper')) return false;
        // 如果不是专门的 api-token-helper，且内部包含了多个 setting-row，不能当成向导卡片
        if (!div.classList.contains('api-token-helper') && !div.classList.contains('cross-plugin-reuse-guide') && div.querySelectorAll('.setting-row, .setting-item').length > 0) return false;
        return true;
    };

    // 1. 搜集所有合法的授权向导卡片
    const guideCards = [];
    const helperCards = Array.from(drawerBody.querySelectorAll('.api-token-helper, .cross-plugin-reuse-guide, .clip-sense-card, .reuse-helper-card, [class*="api-token"]'));

    helperCards.forEach(div => {
        if (isSafeGuideCard(div) && !div.closest('.wiz-step-card') && !guideCards.includes(div)) {
            guideCards.push(div);
        }
    });

    // 2. 收集所有配置行节点
    const rows = Array.from(drawerBody.querySelectorAll('.setting-row, .setting-item, .setting-group'));
    if (rows.length === 0 && guideCards.length === 0) return;

    const step0Rows = [];
    const step1Rows = [];

    // 🚀 将全量寻找出来的授权向导卡片，首优先注入 Step 0 列表（Step 1 卡片内部头部）
    guideCards.forEach(card => {
        if (!step0Rows.includes(card)) {
            step0Rows.push(card);
        }
    });

    rows.forEach(row => {
        // 如果是全局总开关行或已经在卡片内的元素，跳过
        if (row.querySelector('#drawer-global-driver-toggle') || row.closest('.wiz-step-card')) return;
        // 如果是向导卡片本身，避免重复添加
        if (guideCards.includes(row)) return;

        const inputs = row.querySelectorAll('input, select, textarea');
        let isStep0 = false;

        inputs.forEach(inp => {
            const path = (inp.getAttribute('data-path') || inp.name || '').toLowerCase();
            if (path.includes('token') || path.includes('access_key') || path.includes('secret_key') || path.includes('api_key') || inp.type === 'password') {
                isStep0 = true;
            }
        });

        // 查找配置行内是否有带有 Token 申请 / 授权向导链接的元素
        if (row.querySelector('a[href*="token"], a[href*="api"], [class*="magic-link"], [class*="guide"]')) {
            isStep0 = true;
        }

        if (isStep0) {
            step0Rows.push(row);
        } else {
            step1Rows.push(row);
        }
    });

    if (step0Rows.length === 0 && step1Rows.length === 0) return;

    const firstRow = guideCards[0] || step0Rows[0] || step1Rows[0];
    if (!firstRow || !firstRow.parentElement) return;
    const parentContainer = firstRow.parentElement;

    // 在 firstRow 原物理位置插入一个占位 Marker，确保即使 firstRow 被移走，Marker 依然固定在 parentContainer 内
    const marker = document.createElement('span');
    marker.style.display = 'none';
    parentContainer.insertBefore(marker, firstRow);

    // 创建卡片组专属 Wrapper 容器，避免 Node.insertBefore 参照点脱离 DOM 树
    const cardsWrapper = document.createElement('div');
    cardsWrapper.className = 'wiz-cards-wrapper';

    // 1. 创建 Step 1 物理大卡片
    if (step0Rows.length > 0) {
        const card0 = document.createElement('div');
        card0.className = 'wiz-step-card wiz-card-step-0 active';
        card0.id = 'wiz-card-step-0';
        card0.style.cssText = `
            margin-bottom: 16px;
            padding: 14px;
            background: rgba(0, 242, 255, 0.04);
            border: 1.5px solid var(--neon-cyan);
            border-radius: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(0, 242, 255, 0.15);
        `;
        card0.innerHTML = `
            <div style="font-size: 0.78rem; font-weight: 700; color: var(--neon-cyan); margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                <span>🔑 步骤 1：${step0Title}</span>
                <span class="card-status-tag" style="font-size: 0.65rem; padding: 2px 8px; background: rgba(0, 242, 254, 0.2); color: var(--neon-cyan); border-radius: 4px; font-weight: 600;">聚焦配置中</span>
            </div>
            <div class="card-content"></div>
        `;
        const content = card0.querySelector('.card-content');
        step0Rows.forEach(r => {
            if (r !== card0 && !r.contains(card0) && !card0.contains(r)) {
                content.appendChild(r);
            }
        });
        cardsWrapper.appendChild(card0);
    }

    // 2. 创建 Step 2 物理大卡片
    if (step1Rows.length > 0) {
        const card1 = document.createElement('div');
        card1.className = 'wiz-step-card wiz-card-step-1';
        card1.id = 'wiz-card-step-1';
        card1.style.cssText = `
            margin-bottom: 16px;
            padding: 14px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px dashed rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            transition: all 0.3s ease;
        `;
        card1.innerHTML = `
            <div style="font-size: 0.78rem; font-weight: 700; color: var(--text-dim); margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                <span>⚙️ 步骤 2：${step1Title}</span>
                <span class="card-status-tag" style="font-size: 0.65rem; padding: 2px 8px; background: rgba(255, 255, 255, 0.05); color: var(--text-dim); border-radius: 4px; font-weight: 600; display: none;">聚焦配置中</span>
            </div>
            <div class="card-content"></div>
        `;
        const content = card1.querySelector('.card-content');
        step1Rows.forEach(r => {
            if (r !== card1 && !r.contains(card1) && !card1.contains(r)) {
                content.appendChild(r);
            }
        });
        cardsWrapper.appendChild(card1);
    }

    // 🚀 [V105.1] 物理清理：如果存在任何内部不含输入配置项的空高级参数折叠块，直接清理剔除以节省上下空间
    const emptyBlocks = drawerBody.querySelectorAll('.advanced-settings-block, details');
    emptyBlocks.forEach(b => {
        if (b.querySelectorAll('input, select, textarea').length === 0) {
            b.remove();
        }
    });

    // 将 cardsWrapper 完美插入在预先固定的 marker 位置，然后移除 marker
    parentContainer.insertBefore(cardsWrapper, marker);
    marker.remove();
};

// 🚀 [V105.0] 3 步向导点击联动与任务指引更新算子 (常驻大卡片焦点高亮)
window.handleWizardStepClick = (stepIdx, pluginId, category, clickedBtn = null) => {
    const drawer = document.getElementById('plugin-drawer') || document;
    const missionBanner = drawer.querySelector('#wiz-mission-banner');

    // 1. 切换视觉 Active 高光状态
    const steps = drawer.querySelectorAll('.wiz-step');
    steps.forEach((st, idx) => {
        if (idx === stepIdx) {
            st.classList.add('active');
            st.style.background = 'rgba(0, 242, 255, 0.18)';
            st.style.color = 'var(--neon-cyan)';
            st.style.border = '1px solid var(--neon-cyan)';
            st.style.fontWeight = '700';
        } else {
            st.classList.remove('active');
            st.style.background = 'rgba(255, 255, 255, 0.04)';
            st.style.color = 'var(--text-dim)';
            st.style.border = '1px solid rgba(255, 255, 255, 0.1)';
            st.style.fontWeight = '500';
        }
    });

    // 2. 获取大卡片节点
    const card0 = drawer.querySelector('#wiz-card-step-0');
    const card1 = drawer.querySelector('#wiz-card-step-1');
    const footerContainer = drawer.querySelector('#p-drawer-footer') || drawer.querySelector('.drawer-footer') || (drawer.querySelector('#btn-save-plugin-cfg')?.parentElement);

    // 重置所有大卡片样式为暗淡未聚焦状态
    if (card0) {
        card0.style.border = '1px dashed rgba(255, 255, 255, 0.15)';
        card0.style.background = 'rgba(255, 255, 255, 0.02)';
        card0.style.boxShadow = 'none';
        const tag = card0.querySelector('.card-status-tag');
        if (tag) tag.style.display = 'none';
        const title = card0.querySelector('span');
        if (title) title.style.color = 'var(--text-dim)';
    }
    if (card1) {
        card1.style.border = '1px dashed rgba(255, 255, 255, 0.15)';
        card1.style.background = 'rgba(255, 255, 255, 0.02)';
        card1.style.boxShadow = 'none';
        const tag = card1.querySelector('.card-status-tag');
        if (tag) tag.style.display = 'none';
        const title = card1.querySelector('span');
        if (title) title.style.color = 'var(--text-dim)';
    }
    if (footerContainer) {
        footerContainer.style.border = '';
        footerContainer.style.outline = '';
        footerContainer.style.boxShadow = '';
        footerContainer.style.background = '';
    }

    // 3. 辅助函数：物理精准滚动至目标大卡片的外框顶部（保留 14px 完美发光边距）
    const scrollToCardTop = (targetCard) => {
        if (!targetCard) return;
        const drawerBody = document.getElementById('p-drawer-body');
        if (drawerBody) {
            const cardRect = targetCard.getBoundingClientRect();
            const bodyRect = drawerBody.getBoundingClientRect();
            const relativeTop = cardRect.top - bodyRect.top;
            const targetScrollTop = drawerBody.scrollTop + relativeTop - 14;
            drawerBody.scrollTo({ top: Math.max(0, targetScrollTop), behavior: 'smooth' });
        } else {
            targetCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    if (stepIdx === 0) {
        if (missionBanner) {
            missionBanner.innerHTML = '<span>🎯 当前步骤 [1/3]：请在下方【步骤 1 专属卡片】中填写凭据或使用一键复用</span>';
            missionBanner.style.color = '#00ff88';
            missionBanner.style.borderColor = 'rgba(0, 255, 136, 0.3)';
            missionBanner.style.background = 'rgba(0, 255, 136, 0.06)';
        }
        if (card0) {
            scrollToCardTop(card0);
            card0.style.border = '1.5px solid var(--neon-cyan)';
            card0.style.background = 'rgba(0, 242, 255, 0.05)';
            card0.style.boxShadow = '0 0 25px rgba(0, 242, 255, 0.3)';
            const tag = card0.querySelector('.card-status-tag');
            if (tag) {
                tag.style.display = 'inline-block';
                tag.style.background = 'rgba(0, 242, 255, 0.2)';
                tag.style.color = 'var(--neon-cyan)';
            }
            const title = card0.querySelector('span');
            if (title) title.style.color = 'var(--neon-cyan)';
            const firstInput = card0.querySelector('input');
            if (firstInput) firstInput.focus();
        }
    } else if (stepIdx === 1) {
        if (missionBanner) {
            const step2Hint = (category || '').toLowerCase() === 'notification'
                ? '<span>🎯 当前步骤 [2/3]：请在下方配置消息渲染样式、@被提醒人或自定义扩展参数</span>'
                : '<span>🎯 当前步骤 [2/3]：请在下方【步骤 2 专属卡片】中配置仓库、Bucket或自定义域名等核心参数</span>';
            missionBanner.innerHTML = step2Hint;
            missionBanner.style.color = 'var(--neon-cyan)';
            missionBanner.style.borderColor = 'rgba(0, 242, 255, 0.3)';
            missionBanner.style.background = 'rgba(0, 242, 255, 0.06)';
        }
        if (card1) {
            scrollToCardTop(card1);
            card1.style.border = '1.5px solid #00ff88';
            card1.style.background = 'rgba(0, 255, 136, 0.05)';
            card1.style.boxShadow = '0 0 25px rgba(0, 255, 136, 0.3)';
            const tag = card1.querySelector('.card-status-tag');
            if (tag) {
                tag.style.display = 'inline-block';
                tag.style.background = 'rgba(0, 255, 136, 0.2)';
                tag.style.color = '#00ff88';
            }
            const title = card1.querySelector('span');
            if (title) title.style.color = '#00ff88';
            const firstInput = card1.querySelector('input');
            if (firstInput) firstInput.focus();
        }
    } else if (stepIdx === 2) {
        if (missionBanner) {
            missionBanner.innerHTML = '<span>🎯 当前步骤 [3/3]：请在底部点击【测试连接】验证物理链路，确认无误后点击【保存配置】</span>';
            missionBanner.style.color = '#ffb700';
            missionBanner.style.borderColor = 'rgba(255, 183, 0, 0.3)';
            missionBanner.style.background = 'rgba(255, 183, 0, 0.06)';
        }
        const drawerBody = document.getElementById('p-drawer-body');
        if (drawerBody) {
            drawerBody.scrollTo({ top: drawerBody.scrollHeight, behavior: 'smooth' });
        }
        if (footerContainer) {
            footerContainer.style.transition = 'all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            // 🚀 匹配抽屉最底部圆角 (16px)，呈现完美具有弧度的金黄极光外框
            footerContainer.style.borderRadius = '12px 12px 16px 16px';
            footerContainer.style.border = '1.5px solid #ffb700';
            footerContainer.style.outline = 'none';
            footerContainer.style.boxShadow = '0 0 25px rgba(255, 183, 0, 0.45), inset 0 0 15px rgba(255, 183, 0, 0.15)';
            footerContainer.style.background = 'rgba(255, 183, 0, 0.06)';
        }
    }
};

