/**
 * 🛰️ [V55.9] Illacme Plenipes Dashboard Core - Render Component
 * 职责：治理层级智能匹配决议、通用表单配置项拼接渲染与特权边界指示器加载。
 */

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
    } else if (type === 'static') {
        inputHtml = `<div id="${id}" class="setting-static-value" style="padding: 10px 12px; background: rgba(0,0,0,0.15); border-radius: 6px; border: 1px dashed var(--border-color); color: var(--text-dim); font-family: monospace; word-break: break-all;">${safeValue}</div>`;
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
