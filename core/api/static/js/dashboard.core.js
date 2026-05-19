/**
 * 🛰️ [V55.9] Illacme Plenipes Dashboard Core
 * 职责：全局状态管理、API 核心封装与通用组件渲染器。
 */

// 1. 全局状态矩阵
window.settingsData = window.settingsData || {};
window.discoveredModels = {};
window.discoveryErrors = {};
window.activeImprint = null;
window.governanceRules = {};
window.currentView = 'overview';
window.galaxyGraph = null;

// 2. 核心通讯总线
window.apiFetch = async (url, options = {}) => {
    try {
        if (options.method && options.method !== 'GET' && !options.headers) {
            options.headers = { 'Content-Type': 'application/json' };
        }
        const response = await fetch(url, options);
        if (response.status === 401) {
            console.warn("⚠️ [AUTH] 检测到 401 未授权信号，已拦截自动跳转以防止刷新循环。");
            if (typeof addAudit === 'function') addAudit("🚨 身份凭证失效，请尝试手动重新登录。", "error");
            // window.location.href = '/login';
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
    if (!feed) return;
    
    const iconMap = {
        'info': '⚡',
        'success': '✅',
        'error': '🚨',
        'warning': '⚠️'
    };

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

    const summaryText = document.getElementById('audit-summary-text');
    if (summaryText) {
        summaryText.className = `audit-summary-mini audit-status-${type}`;
        summaryText.innerText = message;
    }
};

// 3. 治理分层解析器
window.resolveFieldLevel = (key) => {
    if (!window.governanceRules) return 'imprint';
    try {
        for (const [level, patterns] of Object.entries(window.governanceRules)) {
            if (!Array.isArray(patterns)) continue;
            for (const pattern of patterns) {
                const regex = new RegExp(pattern);
                if (regex.test(key)) return level;
            }
        }
    } catch(e) {}
    return 'imprint';
};

// 4. 通用配置渲染算子 - 商业级 Refined 版
window.renderSettingsItem = (label, path, value, type = 'text', options = {}, tierOverride = null) => {
    const tier = tierOverride || window.resolveFieldLevel(path);
    const badgeMap = {
        'local': '<span class="tier-tag tier-local">物理本地</span>',
        'imprint': '<span class="tier-tag tier-imprint">品牌主权</span>',
        'global': '<span class="tier-tag tier-global">系统宪法</span>'
    };

    let inputHtml = '';
    const id = `cfg-${path.replace(/\./g, '-')}`;
    const description = options.description || `配置主权链路中的 ${label} 参数。`;

    // 🚀 [V57.2] 降级防呆：若值为 undefined 或 null，自动归一化为空字符串，消除前端文本框中的 "undefined" 字符
    const safeValue = (value === undefined || value === null) ? '' : value;

    if (type === 'select') {
        const onchange = options.onchange || `updateConfigField('${path}', this.value)`;
        inputHtml = `<select id="${id}" data-path="${path}" class="setting-input" onchange="${onchange}">
            ${(options.items || []).map(item => `<option value="${item.value}" ${item.value === safeValue ? 'selected' : ''} title="${item.title || item.text || ''}">${item.text}</option>`).join('')}
        </select>`;
    } else if (type === 'checkbox') {
        const onchange = options.onchange || `updateConfigField('${path}', this.checked)`;
        inputHtml = `<label class="p-switch"><input type="checkbox" id="${id}" data-path="${path}" ${safeValue ? 'checked' : ''} onchange="${onchange}"><span class="p-slider"></span></label>`;
    } else if (type === 'password') {
        const onchange = options.onchange || `updateConfigField('${path}', this.value)`;
        inputHtml = `<input type="password" id="${id}" data-path="${path}" class="setting-input" value="${safeValue}" onchange="${onchange}" placeholder="${options.placeholder || ''}">`;
    } else if (type === 'number') {
        const onchange = options.onchange || `updateConfigField('${path}', parseFloat(this.value))`;
        inputHtml = `<input type="number" id="${id}" data-path="${path}" class="setting-input" value="${safeValue}" onchange="${onchange}" placeholder="${options.placeholder || ''}">`;
    } else {
        const onchange = options.onchange || `updateConfigField('${path}', this.value)`;
        inputHtml = `<input type="text" id="${id}" data-path="${path}" class="setting-input" value="${safeValue}" onchange="${onchange}" placeholder="${options.placeholder || ''}" ${options.readonly ? 'readonly' : ''}>`;
    }

    return `
        <div class="setting-row level-${tier}">
            <div class="setting-info">
                <div class="setting-label">${label} ${badgeMap[tier] || ''}</div>
                <div class="setting-desc">${description}</div>
            </div>
            <div class="setting-control">
                ${inputHtml}
            </div>
        </div>
    `;
};

window.updateConfigField = (path, value) => {
    const keys = path.split('.');
    let current = window.settingsData;
    for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {};
        current = current[keys[i]];
    }
    current[keys[keys.length - 1]] = value;
    if (typeof addAudit === 'function') addAudit(`📝 配置变更: ${path} = ${value}`);
    
    // 🚀 [V57.1] 脏检查：联动更新保存按钮状态
    if (typeof window.checkSettingsDirty === 'function') {
        window.checkSettingsDirty();
    }
};

window.getCleanConfig = (obj) => {
    const flat = window.flattenObject(obj);
    const clean = {};
    Object.keys(flat).sort().forEach(key => {
        if (!key.split('.').some(part => part.startsWith('_'))) {
            clean[key] = flat[key];
        }
    });
    return JSON.stringify(clean);
};

window.checkSettingsDirty = () => {
    const saveBtn = document.getElementById('btn-save-settings');
    if (!saveBtn) return;
    
    if (!window.initialSettingsState) {
        saveBtn.disabled = true;
        saveBtn.style.opacity = '0.5';
        return;
    }

    const currentState = window.getCleanConfig(window.settingsData);
    const isDirty = currentState !== window.initialSettingsState;
    
    saveBtn.disabled = !isDirty;
    saveBtn.style.opacity = isDirty ? '1' : '0.5';
    if (isDirty) {
        saveBtn.classList.add('glow-btn');
    } else {
        saveBtn.classList.remove('glow-btn');
    }
};

/**
 * 🛰️ [终端数据处理器] - 物理对正增强版
 */
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

        // 🚀 [V55.9] 物理对正增强版：防止敏感误报
        if (raw.includes('ready in') || raw.includes('local: http')) {
            statusEl.innerText = 'ONLINE';
            statusEl.className = 'online';
        } else if (raw.includes('error') || raw.includes('failed')) {
            // 如果已经是 ONLINE，除非是非常严重的崩溃信号，否则不降级
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

/**
 * 🚀 [V55.1] 触发主题依赖安装 (补全逻辑)
 */
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

window.flattenObject = (obj, prefix = '') => {
    let result = {};
    for (let key in obj) {
        if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
            Object.assign(result, window.flattenObject(obj[key], prefix + key + '.'));
        } else {
            result[prefix + key] = obj[key];
        }
    }
    return result;
};
