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
    
    const iconMap = {
        'info': '⚡',
        'success': '✅',
        'error': '🚨',
        'warning': '⚠️'
    };

    // 🌟 物理自愈防线：即便 feed 容器被主权裁撤，也安全绕过 DOM 注入，确保向下执行状态栏刷新
    if (feed) {
        const item = document.createElement('div');
        item.className = `audit-entry ${type}`;
        const now = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        
        item.innerHTML = `
            <div class="audit-header">
                <span class="audit-icon">${iconMap[type] || '📡'}</span>
                <span class="audit-time">${now}</span>
            </div>
            <div class="audit-msg">${message}</div>
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

    const div = document.createElement('div');
    div.className = 'term-line';
    let cleanMsg = typeof msg === 'string' ? msg : JSON.stringify(msg);

    const ansiMap = { '31': '#ff4d4d', '32': '#00ff88', '33': '#ffaa00', '34': '#4da6ff', '35': '#a34cff', '36': '#00ffff', '37': '#ffffff' };
    cleanMsg = cleanMsg.replace(/\x1b\[(\d+)m/g, (match, code) => {
        const colorHex = ansiMap[code];
        return colorHex ? `</span><span style="color:${colorHex}">` : '</span><span>';
    });
    
    div.innerHTML = `<span>${cleanMsg}</span>`;
    if (color) div.style.color = color;
    out.appendChild(div);
    out.scrollTop = out.scrollHeight;
};

window.triggerThemeInstall = async () => {
    if (typeof addAudit === 'function') addAudit("🏗️ 发现当前版图主题依赖缺失，正在尝试物理安装...", "warning");
    const res = await window.apiFetch('/api/system/theme/install', { method: 'POST' });
    if (res && res.status === 'started') {
        const modal = document.getElementById('terminal-modal');
        if (modal) modal.style.display = 'flex';
        if (typeof addAudit === 'function') addAudit("🛰️ 物理安装管线已开启，正在重定向实时终端数据。", "success");
    }
};

window.closeTerminalModal = () => {
    const modal = document.getElementById('terminal-modal');
    if (modal) {
        modal.style.display = 'none';
        const okBtn = document.getElementById('btn-terminal-ok');
        if (okBtn) okBtn.style.display = 'none';
    }
};
