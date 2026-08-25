/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Sensing & Credential Judger Shard
 * 职责：Omni-Sensing Hub 全局环境与免密凭据感应中枢、快捷代理预设及多因子就绪判决算子。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

window.applyProxyPreset = (val, btn) => {
    let proxyInput = null;
    if (btn) {
        const container = btn.closest('.setting-control') || btn.closest('.setting-row');
        if (container) proxyInput = container.querySelector('input');
    }
    if (!proxyInput) {
        const drawer = document.getElementById('plugin-drawer');
        if (drawer) {
            proxyInput = drawer.querySelector('input[data-path*="proxy"], input[name*="proxy"]');
        }
    }
    if (proxyInput) {
        proxyInput.value = val;
        proxyInput.dispatchEvent(new Event('input', { bubbles: true }));
        if (window.showToast) window.showToast(`已快捷回填代理设置: ${val}`, 'success');
    }
};

window.renderProxyPresetsHtml = () => {
    return `
        <div class="proxy-preset-chips" style="width: 100%; margin-top: 8px; padding-top: 6px; border-top: 1px dashed rgba(255, 255, 255, 0.1); display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span style="font-size: 0.7rem; color: var(--text-dim); font-weight: 600;">⚡ 快捷代理预设:</span>
            <button type="button" onclick="window.applyProxyPreset('http://127.0.0.1:7890', this)" style="font-size: 0.68rem; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.25); color: var(--neon-cyan); padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.2s;" onmouseover="this.style.background='rgba(0, 242, 255, 0.2)'" onmouseout="this.style.background='rgba(0, 242, 255, 0.08)'">Clash (7890)</button>
            <button type="button" onclick="window.applyProxyPreset('http://127.0.0.1:10808', this)" style="font-size: 0.68rem; background: rgba(163, 76, 255, 0.08); border: 1px solid rgba(163, 76, 255, 0.25); color: var(--accent-primary); padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.2s;" onmouseover="this.style.background='rgba(163, 76, 255, 0.2)'" onmouseout="this.style.background='rgba(163, 76, 255, 0.08)'">V2RayN (10808)</button>
            <button type="button" onclick="window.applyProxyPreset('direct', this)" style="font-size: 0.68rem; background: rgba(0, 255, 136, 0.08); border: 1px solid rgba(0, 255, 136, 0.25); color: #00ff88; padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.2s;" onmouseover="this.style.background='rgba(0, 255, 136, 0.2)'" onmouseout="this.style.background='rgba(0, 255, 136, 0.08)'">🌐 物理直连 (direct)</button>
        </div>
    `;
};

// 📡 [Omni-Sensing Hub] 全局环境与免密凭据感应中枢 (带 SessionStorage 极速预热)
(() => {
    let cachedEnv = null;
    try {
        const raw = sessionStorage.getItem('illacme_env_sensing');
        cachedEnv = raw ? JSON.parse(raw) : null;
    } catch (_) { cachedEnv = null; }

    window.envSensing = cachedEnv || {
        github_ssh: null,
        aws: null,
        docker: null,
        git: null,
        loading: false
    };
})();

window.ensureEnvSensing = async (force = false) => {
    if (window.envSensing.loading) return window.envSensing;
    if (!force && window.envSensing.github_ssh !== null) return window.envSensing;

    window.envSensing.loading = true;
    const fetchFunc = window.apiFetch || (async (url, init) => {
        try {
            const r = await fetch(url, init);
            return await r.json();
        } catch (_) { return null; }
    });

    try {
        const [sshRes, awsRes, gitRes] = await Promise.allSettled([
            fetchFunc('/api/plugins/github/ssh-status'),
            fetchFunc('/api/plugins/aws/credentials-status'),
            fetchFunc('/api/system/sensing/git', { method: 'POST' })
        ]);

        if (sshRes.status === 'fulfilled' && sshRes.value) window.envSensing.github_ssh = sshRes.value;
        if (awsRes.status === 'fulfilled' && awsRes.value) window.envSensing.aws = awsRes.value;
        if (gitRes.status === 'fulfilled' && gitRes.value) window.envSensing.git = gitRes.value;

        // 缓存到 sessionStorage 供刷新页面时 0 毫秒秒开
        try {
            sessionStorage.setItem('illacme_env_sensing', JSON.stringify({
                github_ssh: window.envSensing.github_ssh,
                aws: window.envSensing.aws,
                git: window.envSensing.git,
                docker: window.envSensing.docker
            }));
        } catch (_) {}
    } catch (_) {}
    finally {
        window.envSensing.loading = false;
    }
    return window.envSensing;
};

// 🎯 全面多因子凭据智能判决算子 (支持 Token / SSH 免密 / 本地 CLI 授权 / 凭据助手)
window.isPluginCredentialReady = (pluginId, category, cfg) => {
    const pCfg = cfg || {};
    const env = window.envSensing || {};

    // 占位默认值检测：排除 YOUR_*、REPLACE_*、<...>、{...} 等模板占位符
    const isPlaceholderValue = (v) => {
        if (!v || typeof v !== 'string') return true;
        const t = v.trim();
        if (!t) return true;
        return (
            /^YOUR[_\-]/i.test(t) ||
            /^your[_\-]/i.test(t) ||
            /^REPLACE/i.test(t) ||
            /^TOKEN_HERE$/i.test(t) ||
            /^<.+>$/.test(t) ||
            /^\{.+\}$/.test(t) ||
            /^EXAMPLE[_\-]/i.test(t) ||
            /^PLACEHOLDER/i.test(t)
        );
    };

    // 提取可能的仓库地址/URL (兼容 repo_url, repo, repository, git_url, url)
    const _rawRepo = (pCfg.repo_url || pCfg.repo || pCfg.repository || pCfg.git_url || pCfg.url || '').trim();
    const _rawToken = (pCfg.token || pCfg.access_token || pCfg.api_token || pCfg.git_token || '').trim();
    const repoAddress = isPlaceholderValue(_rawRepo) ? '' : _rawRepo;
    const tokenVal = isPlaceholderValue(_rawToken) ? '' : _rawToken;

    // 1. GitHub Pages (全站托管) 与 GitHub (图床)
    if (pluginId === 'github_pages' || (pluginId === 'github' && category === 'image_hosting')) {
        if (tokenVal) return { ready: true, mode: 'token', label: 'Token 鉴权就绪' };
        if (repoAddress) {
            if (repoAddress.startsWith('git@') || repoAddress.includes('git@github.com')) {
                return { ready: true, mode: 'ssh_repo', label: 'SSH 仓库就绪' };
            }
            if (env.github_ssh?.ssh_ok) {
                return { ready: true, mode: 'ssh', label: `SSH 免密就绪 (${env.github_ssh.username || 'Git'})` };
            }
            if (env.git?.name || pCfg.git_user_name) {
                return { ready: true, mode: 'git_credential', label: 'Git 仓库已就绪' };
            }
            return { ready: true, mode: 'configured_repo', label: '目标仓库已就绪' };
        }
        if (env.github_ssh?.ssh_ok) {
            return { ready: false, mode: 'missing_repo', label: '待填目标仓库' };
        }
        return { ready: false, mode: 'missing', label: '待配置仓库' };
    }

    // 2. Gitee Pages
    if (pluginId === 'gitee_pages' || (pluginId === 'gitee' && category === 'image_hosting')) {
        if (tokenVal) return { ready: true, mode: 'token', label: 'Token 鉴权就绪' };
        if (repoAddress) {
            return { ready: true, mode: 'configured_repo', label: 'Gitee 仓库就绪' };
        }
        return { ready: false, mode: 'missing', label: '待配置仓库' };
    }

    // 3. AWS S3 (托管或图床)
    if (pluginId === 's3' || pluginId === 'aws_s3') {
        if (pCfg.access_key_id && pCfg.secret_access_key) return { ready: true, mode: 'key', label: '密钥就绪' };
        if (env.aws?.logged_in) return { ready: true, mode: 'local_aws', label: '本地 AWS 凭据就绪' };
        return { ready: false, mode: 'missing', label: '待填 Access Key' };
    }

    // 4. Vercel / Netlify / Cloudflare (CLI / OAuth 免密)
    if (['vercel', 'netlify', 'cloudflare_pages', 'cloudflare'].includes(pluginId)) {
        // 逐个检查，排除占位默认值
        const cfToken = [pCfg.token, pCfg.api_token, pCfg.api_key, pCfg.auth_token].find(v => v && !isPlaceholderValue(v));
        if (cfToken) return { ready: true, mode: 'token', label: 'Token 就绪' };
        const cfProject = [pCfg.project_name, pCfg.site_id, pCfg.account_id].find(v => v && !isPlaceholderValue(v));
        if (cfProject) return { ready: true, mode: 'cli_oauth', label: 'CLI 免密就绪' };
        return { ready: false, mode: 'missing', label: '待授权 / 待填项目名' };
    }

    // 5. SFTP / 本地服务
    if (pluginId === 'sftp' || pluginId === 'local_fs') {
        if (pCfg.host || pCfg.path || pluginId === 'local_fs') return { ready: true, mode: 'config', label: '配置就绪' };
        return { ready: false, mode: 'missing', label: '待配置主机' };
    }

    // 6. 通用社媒与通知插件 (Dev.to, Medium, Hashnode, 飞书, 钉钉等)
    const hasSecret = Boolean(pCfg.token || pCfg.api_key || pCfg.url || pCfg.webhook || pCfg.access_token || pCfg.secret_key);
    return { ready: hasSecret, mode: hasSecret ? 'secret' : 'missing', label: hasSecret ? '凭据就绪' : '待填 Token' };
};

window.focusErrorField = (fieldName) => {
    const drawer = document.getElementById('plugin-drawer');
    if (!drawer) return;
    let target = drawer.querySelector(`[name*="${fieldName}"]`) || drawer.querySelector(`[id*="${fieldName}"]`);
    if (!target) {
        const allInputs = Array.from(drawer.querySelectorAll('input, select, textarea'));
        target = allInputs.find(i => (i.name || i.id || '').toLowerCase().includes(fieldName.toLowerCase()));
    }
    if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        target.focus();
        target.style.transition = 'all 0.3s';
        target.style.outline = '2px solid #ff4d4d';
        target.style.boxShadow = '0 0 15px rgba(255, 77, 77, 0.6)';
        setTimeout(() => {
            target.style.outline = '';
            target.style.boxShadow = '';
        }, 2500);
        if (window.showToast) window.showToast(`已为您高亮闪烁定位至参数: ${fieldName}`, 'info');
    }
};
