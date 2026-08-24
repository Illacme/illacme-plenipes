/**
 * 🛰️ [V105.0] Illacme Plenipes Plugin Editor - Cross-Plugin Reuse & Clipboard Sensing Shard
 * 职责：同源凭据智能复用、剪贴板格式静默校验、Token 直投填入与表单清空重置。
 */

(function () {
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
})();
