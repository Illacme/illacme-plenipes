/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Sensing & Credential Judger Shard
 * 职责：Omni-Sensing Hub 全局环境与免密凭据感应中枢、快捷代理预设及多因子就绪判决算子。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

window.applyProxyPreset = (val, btn) => {
    let proxyInput = null;
    if (btn) {
        const row = btn.closest('.setting-row');
        if (row) proxyInput = row.querySelector('.setting-control input') || row.querySelector('input');
        if (!proxyInput) {
            const container = btn.closest('.setting-control');
            if (container) proxyInput = container.querySelector('input');
        }
    }
    if (!proxyInput) {
        const drawer = document.getElementById('plugin-drawer');
        if (drawer && (drawer.classList.contains('active') || drawer.style.display !== 'none')) {
            proxyInput = drawer.querySelector('input[data-path*="proxy"], input[name*="proxy"]');
        }
    }
    if (!proxyInput) {
        const settingsView = document.getElementById('view-settings');
        if (settingsView && !settingsView.classList.contains('hidden')) {
            proxyInput = settingsView.querySelector('input[data-path="global_proxy"], input[id*="global_proxy"]');
        }
    }
    if (proxyInput) {
        proxyInput.value = val;
        // 触发 input 与 change 事件驱动系统落盘及表单响应
        proxyInput.dispatchEvent(new Event('input', { bubbles: true }));
        proxyInput.dispatchEvent(new Event('change', { bubbles: true }));

        // 动态更新同组预设按钮高亮
        const chipsContainer = btn ? btn.closest('.proxy-preset-chips') : (proxyInput.closest('.setting-row') || proxyInput.closest('.setting-control'))?.querySelector('.proxy-preset-chips');
        if (chipsContainer) {
            chipsContainer.querySelectorAll('.proxy-chip-btn').forEach(b => {
                b.classList.remove('active-preset');
                b.style.boxShadow = 'none';
                b.style.transform = 'none';
            });
            if (btn && val !== '') {
                btn.classList.add('active-preset');
                btn.style.boxShadow = '0 0 10px rgba(0, 242, 255, 0.45)';
                btn.style.transform = 'translateY(-1px)';
            }
        }

        const toastMsg = val === '' ? '已清空代理地址' : (val === 'direct' ? '已设为强制物理直连 (direct)' : `已快捷填入代理: ${val}`);
        if (window.showToast) window.showToast(toastMsg, 'success');
    }
};

window.renderProxyPresetsHtml = (currentVal = '') => {
    const rawVal = (currentVal || '').trim();
    const presets = [
        { label: 'Clash (7890)', value: 'http://127.0.0.1:7890', title: 'Clash / Mihomo / Clash Verge 常用 HTTP 混合代理端口', color: 'rgba(0, 242, 255, 0.08)', border: 'rgba(0, 242, 255, 0.3)', text: '#00f2fe' },
        { label: 'v2rayN (10809)', value: 'http://127.0.0.1:10809', title: 'v2rayN / Xray 官方默认本地 HTTP 代理端口', color: 'rgba(163, 76, 255, 0.08)', border: 'rgba(163, 76, 255, 0.3)', text: '#c084fc' },
        { label: 'v2rayN SOCKS (10808)', value: 'socks5://127.0.0.1:10808', title: 'v2rayN / Xray 默认本地 SOCKS5 代理端口', color: 'rgba(192, 132, 252, 0.06)', border: 'rgba(192, 132, 252, 0.25)', text: '#d8b4fe' },
        { label: 'Surge (6152)', value: 'http://127.0.0.1:6152', title: 'Surge for Mac 默认本地 HTTP 代理端口', color: 'rgba(56, 189, 248, 0.08)', border: 'rgba(56, 189, 248, 0.3)', text: '#38bdf8' },
        { label: 'Sing-box (2080)', value: 'http://127.0.0.1:2080', title: 'Sing-box / GUI.for.SingBox 默认 Mixed 代理端口', color: 'rgba(244, 114, 182, 0.08)', border: 'rgba(244, 114, 182, 0.3)', text: '#f472b6' },
        { label: 'SS / SSR (1080)', value: 'http://127.0.0.1:1080', title: 'Shadowsocks / SSR 经典默认代理端口', color: 'rgba(251, 191, 36, 0.08)', border: 'rgba(251, 191, 36, 0.3)', text: '#fbbf24' },
        { label: 'Charles (8888)', value: 'http://127.0.0.1:8888', title: 'Charles / Fiddler 抓包与调试代理端口', color: 'rgba(45, 212, 191, 0.08)', border: 'rgba(45, 212, 191, 0.3)', text: '#2dd4bf' },
        { label: '🌐 直连 (direct)', value: 'direct', title: '强制直连，跳过任何网络代理', color: 'rgba(74, 222, 128, 0.08)', border: 'rgba(74, 222, 128, 0.3)', text: '#4ade80' },
        { label: '🧹 清空', value: '', title: '清空代理设置（遵循上层默认或直连）', color: 'rgba(255, 255, 255, 0.05)', border: 'rgba(255, 255, 255, 0.18)', text: '#94a3b8' }
    ];

    const buttonsHtml = presets.map(p => {
        const isActive = rawVal === p.value;
        const activeStyle = isActive ? `box-shadow: 0 0 10px ${p.text}88; border-color: ${p.text}; font-weight: 600;` : '';
        const activeClass = isActive ? 'active-preset' : '';
        return `<button type="button" class="proxy-chip-btn ${activeClass}" onclick="window.applyProxyPreset('${p.value}', this)" title="${p.title}" style="font-size: 0.68rem; background: ${p.color}; border: 1px solid ${p.border}; color: ${p.text}; padding: 3px 8px; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1); white-space: nowrap; ${activeStyle}" onmouseover="this.style.background='${p.color.replace('0.08', '0.22').replace('0.06', '0.18').replace('0.05', '0.15')}'; this.style.transform='translateY(-1px)';" onmouseout="if(!this.classList.contains('active-preset')){ this.style.background='${p.color}'; this.style.transform='none'; }">${p.label}</button>`;
    }).join('\n');

    return `
        <div class="proxy-preset-chips" style="width: 100%; flex-basis: 100%; margin-top: 2px; padding-top: 6px; border-top: 1px dashed rgba(255, 255, 255, 0.08); display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
            <span style="font-size: 0.7rem; color: var(--text-dim, #94a3b8); font-weight: 600; display: inline-flex; align-items: center; gap: 4px; flex-shrink: 0;">⚡ 快捷代理预设:</span>
            ${buttonsHtml}
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
        return /^YOUR[_\-]/i.test(t) || /^your[_\-]/i.test(t) || /^REPLACE/i.test(t) || /^TOKEN_HERE$/i.test(t) ||
               /^<.+>$/.test(t) || /^\{.+\}$/.test(t) || /^EXAMPLE[_\-]/i.test(t) || /^PLACEHOLDER/i.test(t);
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

    // 0. 网络穿透驱动 (Tunnel: Pinggy / Localhost.run / Serveo / Cloudflare / cpolar / FRP / ngrok / Tailscale)
    if (category === 'tunnel' || pluginId === 'pinggy') {
        if (['pinggy', 'localhost_run', 'serveo', 'tailscale'].includes(pluginId)) return { ready: true, mode: 'zero_config', label: '免配即用' };
        if (pluginId === 'cloudflare') return (pCfg.tunnel_token && !isPlaceholderValue(pCfg.tunnel_token)) ? { ready: true, mode: 'token', label: '专属通道就绪' } : { ready: true, mode: 'quick', label: '免配即用' };
        if (pluginId === 'cpolar') return (pCfg.authtoken && !isPlaceholderValue(pCfg.authtoken)) ? { ready: true, mode: 'token', label: 'Token 就绪' } : { ready: true, mode: 'quick', label: '免配即用' };
        if (pluginId === 'ngrok') return (pCfg.authtoken && !isPlaceholderValue(pCfg.authtoken)) ? { ready: true, mode: 'token', label: 'Token 就绪' } : { ready: false, mode: 'missing', label: '待填 Token' };
        if (pluginId === 'frp') return (pCfg.server_addr && !isPlaceholderValue(pCfg.server_addr)) ? { ready: true, mode: 'config', label: '自建节点就绪' } : { ready: false, mode: 'missing', label: '待配服务器' };
        return { ready: true, mode: 'ready', label: '就绪' };
    }

    // 4. Vercel / Netlify / Cloudflare Pages (CLI / OAuth 免密)
    if (['vercel', 'netlify', 'cloudflare_pages'].includes(pluginId) || (pluginId === 'cloudflare' && category !== 'tunnel')) {
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

    // 6. 稀土掘金 (Juejin)
    if (pluginId === 'juejin') {
        const hasJuejin = [pCfg.cookie, pCfg.api_token, pCfg.token].some(v => v && !isPlaceholderValue(v));
        return { ready: hasJuejin, mode: hasJuejin ? 'credential' : 'missing', label: hasJuejin ? '凭据就绪' : '待填 Cookie/Token' };
    }

    // 7. Bilibili (B站)
    if (pluginId === 'bilibili') {
        const hasBili = Boolean(pCfg.sessdata && !isPlaceholderValue(pCfg.sessdata));
        return { ready: hasBili, mode: hasBili ? 'sessdata' : 'missing', label: hasBili ? 'SESSDATA 就绪' : '待填 SESSDATA' };
    }

    // 8. Substack
    if (pluginId === 'substack') {
        const hasSubstack = [pCfg.cookie, pCfg.api_key, pCfg.token].some(v => v && !isPlaceholderValue(v));
        return { ready: hasSubstack, mode: hasSubstack ? 'credential' : 'missing', label: hasSubstack ? '凭据就绪' : '待填 Cookie/Key' };
    }

    // 9. 小红书 / 今日头条 / CSDN / 思否 (二选一社媒矩阵)
    if (['xiaohongshu', 'red', 'toutiao', 'csdn', 'segmentfault'].includes(pluginId)) {
        const hasCred = [pCfg.cookie, pCfg.token, pCfg.access_token].some(v => v && !isPlaceholderValue(v));
        return { ready: hasCred, mode: hasCred ? 'credential' : 'missing', label: hasCred ? '凭据就绪' : '待填 Cookie/Token' };
    }

    // 10. Telegram 频道广播
    if (pluginId === 'telegram') {
        const hasBot = Boolean(pCfg.bot_token && !isPlaceholderValue(pCfg.bot_token));
        return { ready: hasBot, mode: hasBot ? 'bot_token' : 'missing', label: hasBot ? 'Bot Token 就绪' : '待填 Bot Token' };
    }

    // 10. 免配即用插件 (Catbox 等匿名上传服务)
    if (pluginId === 'catbox') return { ready: true, mode: 'anonymous', label: '免配即用' };

    // 10.1 Telegraph 自建图床 (强制校验自建端点)
    if (pluginId === 'telegraph') {
        const ep = (pCfg.endpoint || '').trim();
        const hasCustomNode = Boolean(ep && !ep.includes('telegra.ph'));
        return { ready: hasCustomNode, mode: hasCustomNode ? 'custom_endpoint' : 'missing', label: hasCustomNode ? '自建节点就绪' : '待填自建节点' };
    }

    // 11. 通用社媒、图床、通知与算力渠道凭据全模态感应
    const hasSecret = Boolean(
        [
            pCfg.token, pCfg.api_token, pCfg.api_key, pCfg.access_token, pCfg.secret_key,
            pCfg.cookie, pCfg.sessdata, pCfg.bot_token, pCfg.auth_token, pCfg.admin_api_key,
            pCfg.application_password, pCfg.url, pCfg.webhook, pCfg.webhook_url,
            pCfg.access_key_id, pCfg.access_key_secret, pCfg.secret_id, pCfg.operator,
            pCfg.password, pCfg.client_id, pCfg.access_key, pCfg.smtp_pass, pCfg.device_key,
            pCfg.app_secret, pCfg.bearer_token, pCfg.sendkey, pCfg.base_url
        ].find(v => v && !isPlaceholderValue(v))
    );
    return { ready: hasSecret, mode: hasSecret ? 'secret' : 'missing', label: hasSecret ? '凭据就绪' : '待填凭据' };
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
