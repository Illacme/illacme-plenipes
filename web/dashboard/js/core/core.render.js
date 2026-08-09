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
        'local': '<span class="tier-tag tier-local">本地</span>',
        'imprint': '<span class="tier-tag tier-imprint">品牌</span>',
        'global': '<span class="tier-tag tier-global">全局</span>'
    };

    let inputHtml = '';
    const id = `cfg-${path.replace(/\./g, '-')}`;
    const description = options.description || `配置主权链路中的 ${label} 参数。`;

    const safeValue = (value === undefined || value === null) ? '' : value;
    const requiredAttr = options.required ? 'required data-required="true"' : '';
    const reqStar = options.required ? '<span style="color: #ff4d4f; font-weight: bold; margin-left: 2px;">*</span>' : '';

    if (type === 'select') {
        const onchange = options.onchange || `updateConfigField('${path}', this.value)`;
        const disabledAttr = options.disabled ? 'disabled' : '';
        inputHtml = `<select id="${id}" data-path="${path}" data-label="${label}" class="setting-input" onchange="${onchange}" ${disabledAttr} ${requiredAttr}>
            ${(options.items || []).map(item => `<option value="${item.value}" ${item.value === safeValue ? 'selected' : ''} title="${item.title || item.text || ''}">${item.text}</option>`).join('')}
        </select>`;
    } else if (type === 'checkbox') {
        const onchange = options.onchange || `updateConfigField('${path}', this.checked)`;
        const disabledAttr = options.disabled ? 'disabled' : '';
        inputHtml = `<label class="p-switch"><input type="checkbox" id="${id}" data-path="${path}" data-label="${label}" ${safeValue ? 'checked' : ''} onchange="${onchange}" ${disabledAttr}><span class="p-slider"></span></label>`;
    } else if (type === 'password') {
        const onchange = options.onchange || `updateConfigField('${path}', this.value)`;
        inputHtml = `
            <div class="pwd-input-wrapper" style="position: relative; display: flex; align-items: center; width: 100%;">
                <input type="password" id="${id}" data-path="${path}" data-label="${label}" class="setting-input" value="${safeValue}" onchange="${onchange}" placeholder="${options.placeholder || ''}" ${requiredAttr} style="padding-right: 36px; width: 100%;">
                <button type="button" class="pwd-toggle-btn" onclick="window.togglePasswordVisibility(this)" title="切换明文/密文" style="position: absolute; right: 8px; background: transparent; border: none; cursor: pointer; font-size: 0.85rem; opacity: 0.7; transition: opacity 0.2s; padding: 2px 4px; color: var(--neon-cyan, #00f2fe);">👁️</button>
            </div>
        `;
    } else if (type === 'number') {
        const onchange = options.onchange || `updateConfigField('${path}', parseFloat(this.value))`;
        inputHtml = `<input type="number" id="${id}" data-path="${path}" data-label="${label}" class="setting-input" value="${safeValue}" onchange="${onchange}" placeholder="${options.placeholder || ''}" ${requiredAttr}>`;
    } else if (type === 'static') {
        inputHtml = `<div id="${id}" class="setting-static-value" style="padding: 10px 12px; background: rgba(0,0,0,0.15); border-radius: 6px; border: 1px dashed var(--border-color); color: var(--text-dim); font-family: monospace; word-break: break-all;">${safeValue}</div>`;
    } else {
        const onchange = options.onchange || `updateConfigField('${path}', this.value)`;
        inputHtml = `<input type="text" id="${id}" data-path="${path}" data-label="${label}" class="setting-input" value="${safeValue}" onchange="${onchange}" placeholder="${options.placeholder || ''}" ${options.readonly ? 'readonly' : ''} ${requiredAttr}>`;
    }

    if (path && path.toLowerCase().includes('proxy')) {
        const presetsHtml = typeof window.renderProxyPresetsHtml === 'function' ? window.renderProxyPresetsHtml() : '';
        inputHtml += presetsHtml;
    }

    const alignStyle = (type === 'checkbox' || type === 'select') ? 'align-items: flex-end;' : 'align-items: stretch;';
    return `
        <div class="setting-row level-${tier}">
            <div class="setting-info">
                <div class="setting-label">${label} ${reqStar} ${badgeMap[tier] || ''}</div>
                <div class="setting-desc">${description}</div>
            </div>
            <div class="setting-control" style="display: flex; flex-direction: column; ${alignStyle} flex: 1.2; max-width: 65%; min-width: 220px;">
                ${inputHtml}
            </div>
        </div>
    `;
};

window.togglePasswordVisibility = (btn) => {
    if (!btn) return;
    const wrapper = btn.closest('.pwd-input-wrapper') || btn.parentElement;
    if (!wrapper) return;
    const input = wrapper.querySelector('input');
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        btn.innerText = '🙈';
        btn.title = '切换为密文隐藏';
        btn.style.opacity = '1';
    } else {
        input.type = 'password';
        btn.innerText = '👁️';
        btn.title = '切换为明文显示';
        btn.style.opacity = '0.7';
    }
};
