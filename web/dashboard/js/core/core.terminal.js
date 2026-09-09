/**
 * 🛰️ [V55.9] Illacme Plenipes Dashboard Core - API & Log Terminal Component
 * 职责：核心 Axios 代理通讯网关、全链路遥测审计日志输出、实时 CLI 安装管线处理与彩色 ANSI 着色器。
 */

window.apiFetch = async (url, options = {}) => {
    try {
        if (!options.headers) {
            options.headers = {};
        }
        if (options.method && options.method !== 'GET' && !options.headers['Content-Type']) {
            options.headers['Content-Type'] = 'application/json';
        }
        
        // 🚀 [V74.9] 安全中枢：自动从 localStorage 或 URL 挂载主权 X-Token 授权凭证
        let token = localStorage.getItem('api_token');
        if (!token) {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                token = urlParams.get('token') || urlParams.get('api_token');
                if (token) {
                    localStorage.setItem('api_token', token);
                }
            } catch (paramErr) {}
        }
        if (token) {
            options.headers['X-Token'] = token;
        }

        const response = await fetch(url, options);
        if (response.status === 401) {
            console.warn("⚠️ [AUTH] 检测到 401 未授权信号，已拦截自动跳转以防止刷新循环。");
            if (typeof addAudit === 'function') addAudit("🚨 身份凭证失效，请尝试手动重新登录。", "error");
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error(`🛑 [API ERROR] ${url}:`, error);
        return null;
    }
};

window.addAudit = (message, type = 'info') => {
    const feed = document.getElementById('audit-feed');
    
    const defaultIconMap = {
        'info': '⚡',
        'success': '✅',
        'error': '🚨',
        'warning': '⚠️'
    };

    const typeLabelMap = {
        'info': 'INFO',
        'success': 'SUCCESS',
        'error': 'ERROR',
        'warning': 'WARN'
    };

    // 🚀 [V76.6] 全局主权规范化：统一标定 4 大核心状态图标 (✅/🚨/⚠️/⚡)，物理剥离所有杂乱的散落 Emoji
    const displayIcon = defaultIconMap[type] || '⚡';
    const typeLabel = typeLabelMap[type] || String(type).toUpperCase();
    let cleanMessage = message || '';

    if (typeof cleanMessage === 'string') {
        const emojiRegex = /^([\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F000}-\u{1F02F}\u{1F0A0}-\u{1F0DF}\u{1F100}-\u{1F6FF}\u{1F900}-\u{1F9FF}\u{E000}-\u{F8FF}\u{2B50}\u{2B55}\u{231A}-\u{231B}\u{23E9}-\u{23EC}\u{23F0}\u{23F3}]|[\uD800-\uDBFF][\uDC00-\uDFFF])\s*/u;
        while (emojiRegex.test(cleanMessage)) {
            cleanMessage = cleanMessage.replace(emojiRegex, '');
        }
    }

    // 🌟 物理自愈防线：即便 feed 容器被主权裁撤，也安全绕过 DOM 注入，确保向下执行状态栏刷新
    if (feed) {
        const item = document.createElement('div');
        item.className = `audit-entry ${type}`;
        const now = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        
        item.innerHTML = `
            <div class="audit-header">
                <div class="audit-meta-left">
                    <span class="audit-icon">${displayIcon}</span>
                    <span class="audit-badge ${type}">${typeLabel}</span>
                </div>
                <span class="audit-time">${now}</span>
            </div>
            <div class="audit-msg">${cleanMessage}</div>
        `;
        
        feed.prepend(item);
        if (feed.children.length > 50) feed.removeChild(feed.lastChild);
    }

    const summaryText = document.getElementById('audit-summary-text');
    if (summaryText) {
        summaryText.className = `audit-summary-mini audit-status-${type}`;
        summaryText.innerText = message;
    }
};

window.handleTerminalData = (payload) => {
    if (!payload) return;

    // 📊 [V90.0] 处理全域分发汇总与站点直达报告
    if (payload.type === 'DEPLOY_SUMMARY' && payload.data) {
        if (typeof window.renderDeploymentSummaryCard === 'function') {
            window.renderDeploymentSummaryCard(payload.data);
        }
        return;
    }

    const msg = typeof payload === 'string' ? payload : (payload.data || payload.message || '');
    if (typeof appendTerminalLog === 'function') {
        appendTerminalLog(msg);
    }
    
    const statusEl = document.getElementById('terminal-status');
    if (statusEl && msg) {
        const raw = String(msg).toLowerCase();
        const currentStatus = statusEl.innerText.toUpperCase();

        if (raw.includes('ready in') || raw.includes('local: http') || raw.includes('website is running at') || raw.includes('compiled successfully') || raw.includes('http://localhost:')) {
            statusEl.innerText = 'ONLINE';
            statusEl.className = 'online';
        } else if (raw.includes('error') || raw.includes('failed')) {
            const isCritical = raw.includes('[error]') || raw.includes('fatal:');
            const isFalsePositive = raw.includes('0 error') || raw.includes('0 failed');
            
            if ((isCritical || !isFalsePositive) && currentStatus !== 'ONLINE') {
                if (!currentStatus.includes('INSTALLING')) {
                    statusEl.innerText = 'ERROR';
                    statusEl.className = 'error';
                }
            }
        }
    }

    // 🚀 [端口动态捕获与对正] 自动嗅探子进程实际绑定的服务端口 (如 Astro/Vite 冲突避让至 43214)
    if (msg) {
        const portMatch = String(msg).match(/https?:\/\/(?:localhost|127\.0\.0\.1):(\d+)/i);
        if (portMatch) {
            const detectedPort = parseInt(portMatch[1], 10);
            window._actualPreviewPort = detectedPort;
            window._actualPreviewUrl = `http://localhost:${detectedPort}/`;
            
            // 实时刷新弹窗中的直达超链接与端口展示
            const linkEl = document.getElementById('preview-site-link');
            if (linkEl) {
                linkEl.href = window._actualPreviewUrl;
                linkEl.innerText = window._actualPreviewUrl;
            }
            const portEl = document.getElementById('preview-site-port');
            if (portEl) {
                portEl.innerText = detectedPort;
            }
        }
    }

    if (payload.type === 'INSTALL_SUCCESS' || payload.type === 'INSTALL_ERROR') {
        if (statusEl) {
            statusEl.innerText = payload.type === 'INSTALL_SUCCESS' ? 'COMPLETED' : 'FAILED';
            statusEl.className = payload.type === 'INSTALL_SUCCESS' ? 'online' : 'error';
        }
        const okBtn = document.getElementById('btn-terminal-ok');
        if (okBtn) okBtn.style.display = 'block';
    }
};

window.appendTerminalLog = (msg, color = null) => {
    const out = document.getElementById('terminal-output');
    if (!out) return;

    // 🛡️ 限制 DOM 节点总数不超过 150 行，防止长日志造成页面卡顿
    while (out.children.length > 150) {
        out.removeChild(out.firstChild);
    }

    const div = document.createElement('div');
    div.className = 'term-line';
    div.style.cssText = 'line-height: 1.5; word-break: break-word; font-size: 0.82rem;';
    let cleanMsg = typeof msg === 'string' ? msg : JSON.stringify(msg);

    const ansiMap = { '31': '#ff4d4d', '32': '#00ff88', '33': '#ffaa00', '34': '#4da6ff', '35': '#a34cff', '36': '#00ffff', '37': 'var(--text-bright)' };
    cleanMsg = cleanMsg.replace(/\x1b\[(\d+)m/g, (match, code) => {
        const colorHex = ansiMap[code];
        return colorHex ? `</span><span style="color:${colorHex}">` : '</span><span>';
    });
    
    // 🌐 [V90.0] URL 自动识别并转换为安全可直接点击的高亮超链接
    cleanMsg = cleanMsg.replace(/(https?:\/\/[^\s<>"']+)/g, (fullMatch) => {
        // 🛡️ 剥离末尾的闭合标点（如括号、逗号、句号等），防止链接错位
        let trailingPunct = '';
        const punctMatch = fullMatch.match(/[),.;!?:\]]+$/);
        let url = fullMatch;
        if (punctMatch) {
            trailingPunct = punctMatch[0];
            url = fullMatch.slice(0, -trailingPunct.length);
        }
        return `<a href="${url}" target="_blank" rel="noopener noreferrer" style="color:var(--neon-cyan, #00f0ff); text-decoration:underline; font-weight:600; cursor:pointer;" onclick="event.stopPropagation();">${url} ↗</a>${trailingPunct}`;
    });

    div.innerHTML = `<span>${cleanMsg}</span>`;
    if (color) {
        div.style.color = (color === '#ffffff' || color === '#fff') ? 'var(--text-bright)' : color;
    }
    out.appendChild(div);
    
    // 🚀 使用 requestAnimationFrame 平滑贴底滚动，杜绝高频日志掉帧卡顿
    if (!window._termScrollPending) {
        window._termScrollPending = true;
        requestAnimationFrame(() => {
            out.scrollTop = out.scrollHeight;
            window._termScrollPending = false;
        });
    }
};

window.triggerThemeInstall = async () => {
    if (typeof addAudit === 'function') addAudit("🏗️ 发现当前品牌主题依赖缺失，正在尝试物理安装...", "warning");
    const res = await window.apiFetch('/api/system/theme/install', { method: 'POST' });
    if (res && res.status === 'started') {
        const modal = document.getElementById('terminal-modal');
        if (modal) modal.style.display = 'flex';
        if (typeof addAudit === 'function') addAudit("🛰️ 物理安装管线已开启，正在重定向实时终端数据。", "success");
    }
};

window.resetTerminalModalFooter = () => {
    const forceBar = document.getElementById('preview-force-sync-bar');
    if (forceBar) forceBar.style.display = 'none';
    const startBtn = document.getElementById('btn-terminal-start-preview');
    if (startBtn) startBtn.style.display = 'none';
    const openBtn = document.getElementById('btn-terminal-open-preview');
    if (openBtn) openBtn.style.display = 'none';
    const visitSiteBtn = document.getElementById('btn-terminal-visit-site');
    if (visitSiteBtn) visitSiteBtn.style.display = 'none';
    const okBtn = document.getElementById('btn-terminal-ok');
    if (okBtn) okBtn.style.display = 'none';
    const republishBtn = document.getElementById('btn-terminal-republish');
    if (republishBtn) republishBtn.style.display = 'none';
    const abortBtn = document.getElementById('btn-terminal-abort');
    if (abortBtn) abortBtn.style.display = 'none';
    const closeBtn = document.getElementById('btn-terminal-close');
    if (closeBtn) closeBtn.style.display = 'none';
};

window.closeTerminalModal = () => {
    const modal = document.getElementById('terminal-modal');
    if (modal) {
        modal.style.display = 'none';
        window.resetTerminalModalFooter();
    }
};

window._latestPrimaryLiveUrl = "";

window.openPrimaryLiveSite = () => {
    if (window._latestPrimaryLiveUrl) {
        window.open(window._latestPrimaryLiveUrl, '_blank', 'noopener,noreferrer');
    } else {
        if (typeof window.showToast === 'function') {
            window.showToast('未检测到有效的主站线上访问地址', 'warning');
        }
    }
};

window.copyAllLiveUrls = async (urls) => {
    try {
        const text = urls.join('\n');
        await navigator.clipboard.writeText(text);
        if (typeof window.showToast === 'function') {
            window.showToast('已复制全网访问地址至剪贴板 📋', 'success');
        }
    } catch(e) {
        prompt('请手动复制以下网站链接：', urls.join('\n'));
    }
};

window.runHealthRadar = async (overrideUrls) => {
    const badges = document.querySelectorAll('.deploy-summary-card .health-radar-badge');
    if (!badges || badges.length === 0) return;

    let urls = overrideUrls || [];
    if (!urls || urls.length === 0) {
        badges.forEach(b => {
            const u = b.dataset.url;
            if (u && !urls.includes(u)) urls.push(u);
        });
    }
    if (urls.length === 0) return;

    // 置为探测中动画状态
    badges.forEach(b => {
        b.innerHTML = '<span style="color:#38bdf8;">🛰️ 正在探测连通性...</span>';
        b.style.borderColor = 'rgba(56,189,248,0.3)';
        b.style.background = 'rgba(56,189,248,0.08)';
    });

    try {
        const res = await window.apiFetch('/api/governance/health-radar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ urls: urls })
        });

        if (res && res.status === 'success' && Array.isArray(res.results)) {
            res.results.forEach(item => {
                const targetBadges = document.querySelectorAll(`.deploy-summary-card .health-radar-badge[data-url="${item.url}"]`);
                targetBadges.forEach(b => {
                    if (item.is_healthy) {
                        const isFast = item.latency_ms < 150;
                        const latencyColor = isFast ? '#10b981' : '#38bdf8';
                        const bgLight = isFast ? 'rgba(16,185,129,0.12)' : 'rgba(56,189,248,0.12)';
                        const borderLight = isFast ? 'rgba(16,185,129,0.35)' : 'rgba(56,189,248,0.35)';
                        b.innerHTML = `<span style="color:${latencyColor};font-weight:700;">⚡ ${item.latency_ms}ms</span> <span style="color:#94a3b8;">·</span> <span style="color:${latencyColor};">HTTP ${item.status_code}</span> <span style="color:#64748b;">(${item.server || 'Edge'})</span>`;
                        b.style.borderColor = borderLight;
                        b.style.background = bgLight;
                        b.title = `边缘节点: ${item.server} | 往返时延: ${item.latency_ms}ms | 状态: 正常连通`;
                    } else if (item.status_code === 404) {
                        b.innerHTML = `<span style="color:#f59e0b;font-weight:600;">⏳ 边缘广播中 (404)</span>`;
                        b.style.borderColor = 'rgba(245,158,11,0.35)';
                        b.style.background = 'rgba(245,158,11,0.1)';
                        b.title = `最新产物已推送到云端，边缘 CDN 节点正在进行全局 DNS/缓存广播，数秒后即可正常访问`;
                    } else {
                        b.innerHTML = `<span style="color:#ef4444;font-weight:600;">⚠️ ${item.message || '网络波动'}</span>`;
                        b.style.borderColor = 'rgba(239,68,68,0.35)';
                        b.style.background = 'rgba(239,68,68,0.1)';
                        b.title = `探测信息: ${item.message}`;
                    }
                });
            });
        }
    } catch (e) {
        console.warn('⚠️ [HealthRadar] 探测接口请求失败:', e);
        badges.forEach(b => {
            b.innerHTML = '<span style="color:#94a3b8;">雷达暂不可用</span>';
        });
    }
};

window.renderDeploymentSummaryCard = (summary) => {
    if (!summary || !summary.channels || summary.channels.length === 0) return;
    const out = document.getElementById('terminal-output');
    if (!out) return;

    // 防重入：若已有最新汇总卡片，先移除旧的
    const existing = out.querySelector('.deploy-summary-card');
    if (existing) existing.remove();

    const card = document.createElement('div');
    card.className = 'deploy-summary-card';
    card.style.cssText = `
        margin: 16px 0 8px 0;
        padding: 16px 18px;
        background: rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(0, 240, 255, 0.4);
        border-radius: 12px;
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
        font-family: inherit;
        text-align: left;
    `;

    const total = summary.total_channels || summary.channels.length;
    const success = summary.success_count !== undefined ? summary.success_count : summary.channels.filter(c => c.status === 'success').length;
    const failed = summary.fail_count !== undefined ? summary.fail_count : summary.channels.filter(c => c.status !== 'success').length;

    // 寻找主站 URL
    const primaryCh = summary.channels.find(c => c.is_primary && c.url) || summary.channels.find(c => c.url && c.status === 'success');
    if (primaryCh && primaryCh.url) {
        window._latestPrimaryLiveUrl = primaryCh.url;
        const visitBtn = document.getElementById('btn-terminal-visit-site');
        if (visitBtn) {
            visitBtn.style.display = 'inline-flex';
            visitBtn.title = `立即在新标签页打开 ${primaryCh.name} (${primaryCh.url})`;
        }
    }

    const allSuccessUrls = summary.channels.filter(c => c.status === 'success' && c.url).map(c => `${c.name}: ${c.url}`);

    let channelsHtml = summary.channels.map(ch => {
        const isSuccess = ch.status === 'success';
        const roleBadge = ch.is_primary
            ? `<span style="background:rgba(5,150,105,0.22);color:#10b981;border:1px solid rgba(16,185,129,0.4);padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:700;white-space:nowrap;">🏠 官方主站</span>`
            : `<span style="background:rgba(56,189,248,0.18);color:#38bdf8;border:1px solid rgba(56,189,248,0.35);padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:600;white-space:nowrap;">🔄 备用镜像</span>`;
        
        const statusBadge = isSuccess
            ? `<span style="color:#10b981;font-size:0.75rem;font-weight:600;display:inline-flex;align-items:center;gap:4px;">🟢 部署成功</span>`
            : `<span style="color:#ef4444;font-size:0.75rem;font-weight:600;display:inline-flex;align-items:center;gap:4px;">❌ 投递失败</span>`;

        // 🛰️ [V90.0] 健康雷达动态徽章插槽
        const radarBadge = isSuccess && ch.url
            ? `<span class="health-radar-badge" data-url="${ch.url}" style="font-size:0.72rem;padding:2px 8px;border-radius:4px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:#94a3b8;display:inline-flex;align-items:center;gap:4px;transition:all 0.3s;white-space:nowrap;"><span style="display:inline-block;transform:scale(0.85);">🛰️</span> 探测中...</span>`
            : '';

        const linkAction = isSuccess && ch.url
            ? `<a href="${ch.url}" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:4px;padding:4px 12px;background:rgba(0,240,255,0.15);border:1px solid rgba(0,240,255,0.4);color:#00f0ff;border-radius:6px;font-size:0.75rem;font-weight:700;text-decoration:none;transition:all 0.15s;white-space:nowrap;" onmouseover="this.style.background='rgba(0,240,255,0.3)'" onmouseout="this.style.background='rgba(0,240,255,0.15)'">打开浏览 ↗</a>`
            : `<span style="font-size:0.72rem;color:#94a3b8;">${ch.error || '未生成线上地址'}</span>`;

        const urlDisplay = isSuccess && ch.url
            ? `<div style="margin-top:5px;font-size:0.75rem;color:#94a3b8;word-break:break-all;font-family:'JetBrains Mono',monospace;"><a href="${ch.url}" target="_blank" rel="noopener noreferrer" style="color:#38bdf8;text-decoration:underline;">${ch.url}</a></div>`
            : '';

        return `
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px 14px;margin-bottom:8px;">
                <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
                    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                        ${roleBadge}
                        <span style="font-weight:700;font-size:0.85rem;color:var(--text-bright, #fff);">${ch.name}</span>
                        ${statusBadge}
                        ${radarBadge}
                    </div>
                    <div>
                        ${linkAction}
                    </div>
                </div>
                ${urlDisplay}
            </div>
        `;
    }).join('');

    const copyBtnHtml = allSuccessUrls.length > 0
        ? `<button type="button" onclick='window.copyAllLiveUrls(${JSON.stringify(allSuccessUrls)})' style="background:none;border:1px solid rgba(255,255,255,0.15);color:#cbd5e1;border-radius:6px;padding:3px 10px;font-size:0.72rem;cursor:pointer;display:inline-flex;align-items:center;gap:4px;" onmouseover="this.style.borderColor='rgba(0,240,255,0.5)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.15)'">📋 复制全部链接</button>`
        : '';

    const refreshRadarBtnHtml = allSuccessUrls.length > 0
        ? `<button type="button" onclick="window.runHealthRadar()" style="background:none;border:1px solid rgba(0,240,255,0.3);color:#00f0ff;border-radius:6px;padding:3px 10px;font-size:0.72rem;cursor:pointer;display:inline-flex;align-items:center;gap:4px;" onmouseover="this.style.background='rgba(0,240,255,0.1)'" onmouseout="this.style.background='none'" title="重新发起全球 CDN 边缘测速与连通性探测">⚡ 刷新测速</button>`
        : '';

    card.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:10px;flex-wrap:wrap;gap:8px;">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:1.15rem;">🎉</span>
                <span style="font-weight:800;font-size:0.95rem;color:#00ff88;letter-spacing:0.3px;">全域发布圆满完成 · 站点已上线</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                <span style="font-size:0.75rem;color:#94a3b8;">已同步 ${total} 个渠道 (🟢 成功 ${success} / 🔴 失败 ${failed})</span>
                ${refreshRadarBtnHtml}
                ${copyBtnHtml}
            </div>
        </div>
        <div>
            ${channelsHtml}
        </div>
    `;

    out.appendChild(card);
    out.scrollTop = out.scrollHeight;

    // 🚀 [V90.0] 自动点火健康度雷达，异步探测全球 CDN 连通性
    setTimeout(() => {
        if (typeof window.runHealthRadar === 'function') {
            window.runHealthRadar();
        }
    }, 200);
};

